```python
import asyncio
import logging
import datetime
import uuid
import ulid
from quart import Quart, request, jsonify
from quart_schema import QuartSchema
import httpx

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# In-memory caches for entities
cache = {
    "Product": {},       # sku -> product dict
    "Cart": {},          # cartId -> cart dict
    "User": {},          # userId -> user dict
    "Payment": {},       # paymentId -> payment dict
    "Order": {},         # orderId -> order dict
    "Shipment": {},      # shipmentId -> shipment dict
    "Reservation": {},   # reservationId -> reservation dict
    "PickLedger": {},    # pickId -> pick entry dict
}

# TTL for reservations (in seconds)
RESERVATION_TTL_SECONDS = 4 * 3600

# Helpers

def now_iso():
    return datetime.datetime.utcnow().isoformat() + "Z"

def gen_id():
    return str(uuid.uuid4())

def gen_ulid():
    return str(ulid.new())

def snapshot_address(addresses):
    # Take snapshot of delivery address only per spec
    delivery = addresses.get("delivery")
    if not delivery:
        # fallback to default or billing if delivery missing
        delivery = addresses.get("default") or addresses.get("billing") or {}
    # copy relevant fields
    return {
        "line1": delivery.get("line1", ""),
        "city": delivery.get("city", ""),
        "postcode": delivery.get("postcode", ""),
        "country": delivery.get("country", ""),
    }

def recalc_cart_totals(cart):
    total_items = sum(line.get("qty", 0) for line in cart.get("lines", []))
    grand_total = sum(line.get("price", 0) * line.get("qty", 0) for line in cart.get("lines", []))
    cart["totalItems"] = total_items
    cart["grandTotal"] = grand_total

async def refresh_reservation_ttl(cartId):
    # Update all ACTIVE reservations for this cart to extend expiresAt
    now = datetime.datetime.utcnow()
    expires_at = now + datetime.timedelta(seconds=RESERVATION_TTL_SECONDS)
    for r in cache["Reservation"].values():
        if r["cartId"] == cartId and r["status"] == "ACTIVE":
            r["expiresAt"] = expires_at.isoformat() + "Z"

async def create_reservations_for_cart(cart):
    # For each line create or update ACTIVE reservation
    now = datetime.datetime.utcnow()
    expires_at = now + datetime.timedelta(seconds=RESERVATION_TTL_SECONDS)
    cartId = cart["cartId"]
    # First collect existing reservations for this cart by sku
    existing = {r["sku"]: r for r in cache["Reservation"].values() if r["cartId"] == cartId and r["status"] == "ACTIVE"}
    # New sku set
    new_skus = {line["sku"] for line in cart.get("lines", [])}
    # Add or update reservations for present skus
    for line in cart.get("lines", []):
        sku = line["sku"]
        qty = line["qty"]
        if sku in existing:
            existing[sku]["qty"] = qty
            existing[sku]["expiresAt"] = expires_at.isoformat() + "Z"
        else:
            reservationId = gen_id()
            reservationBatchId = cart.get("reservationBatchId") or gen_id()
            cart["reservationBatchId"] = reservationBatchId
            r = {
                "reservationId": reservationId,
                "reservationBatchId": reservationBatchId,
                "cartId": cartId,
                "sku": sku,
                "qty": qty,
                "expiresAt": expires_at.isoformat() + "Z",
                "status": "ACTIVE",
            }
            cache["Reservation"][reservationId] = r
    # Release any reservations for skus no longer in cart lines
    for sku, r in existing.items():
        if sku not in new_skus:
            r["status"] = "RELEASED"

async def release_reservations_for_cart(cartId):
    # Immediately release all ACTIVE reservations for cart
    for r in cache["Reservation"].values():
        if r["cartId"] == cartId and r["status"] == "ACTIVE":
            r["status"] = "RELEASED"

async def decrement_stock_for_order(order):
    # Decrement quantityAvailable in Product for each line qty
    for line in order["lines"]:
        sku = line["sku"]
        qty = line["qty"]
        product = cache["Product"].get(sku)
        if product:
            new_qty = max(product.get("quantityAvailable", 0) - qty, 0)
            product["quantityAvailable"] = new_qty

async def auto_split_shipments(order):
    # Split shipments by item quantities - simple 1 shipment per sku for prototype
    shipments = []
    for line in order["lines"]:
        shipmentId = gen_id()
        shipment = {
            "shipmentId": shipmentId,
            "orderId": order["orderId"],
            "status": "PICKING",
            "lines": [{
                "sku": line["sku"],
                "qtyOrdered": line["qty"],
                "qtyPicked": 0,
                "qtyShipped": 0,
            }],
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
        }
        cache["Shipment"][shipmentId] = shipment
        shipments.append(shipment)
    return shipments

async def aggregate_order_status(orderId):
    # Aggregate shipment statuses into order status
    shipments = [s for s in cache["Shipment"].values() if s["orderId"] == orderId]
    if not shipments:
        return
    statuses = {s["status"] for s in shipments}
    order = cache["Order"].get(orderId)
    if not order:
        return
    # Determine order status by priority of shipment statuses
    if "PICKING" in statuses:
        order["status"] = "PICKING"
    elif "WAITING_TO_SEND" in statuses:
        order["status"] = "WAITING_TO_SEND"
    elif "SENT" in statuses:
        order["status"] = "SENT"
    elif statuses == {"DELIVERED"}:
        order["status"] = "DELIVERED"
    else:
        order["status"] = "WAITING_TO_FULFILL"
    order["updatedAt"] = now_iso()

# Background task to auto-mark payment PAID after 3 seconds
async def auto_mark_paid(paymentId):
    await asyncio.sleep(3)
    payment = cache["Payment"].get(paymentId)
    if payment and payment["status"] == "INITIATED":
        payment["status"] = "PAID"
        payment["updatedAt"] = now_iso()
        logger.info(f"Payment {paymentId} auto-marked PAID")
        # Trigger order creation from payment
        asyncio.create_task(create_order_from_paid(payment))

async def create_order_from_paid(payment):
    # Find cart
    cart = cache["Cart"].get(payment["cartId"])
    if not cart or cart["status"] != "CHECKING_OUT":
        logger.warning(f"Cart not ready for order creation for payment {payment['paymentId']}")
        return
    # Guard: cart must not be empty
    if not cart.get("lines"):
        logger.warning(f"Cart {cart['cartId']} empty - abort order creation")
        return
    # Commit reservations (set status to COMMITTED)
    batch_id = cart.get("reservationBatchId")
    for r in cache["Reservation"].values():
        if r["reservationBatchId"] == batch_id and r["status"] == "ACTIVE":
            r["status"] = "COMMITTED"
    # Decrement stock
    await decrement_stock_for_order(cart)
    # Snapshot user address
    user = cache["User"].get(cart.get("userId"))
    shipping_address = snapshot_address(user.get("addresses", {}) if user else {})
    # Create order
    orderId = gen_id()
    orderNumber = gen_ulid()
    lines = []
    for line in cart["lines"]:
        lineTotal = line["price"] * line["qty"]
        lines.append({
            "sku": line["sku"],
            "name": line["name"],
            "unitPrice": line["price"],
            "qty": line["qty"],
            "lineTotal": lineTotal,
        })
    totals = {
        "items": sum(line["qty"] for line in lines),
        "grand": sum(line["lineTotal"] for line in lines),
    }
    order = {
        "orderId": orderId,
        "orderNumber": orderNumber,
        "userId": cart.get("userId"),
        "shippingAddress": shipping_address,
        "lines": lines,
        "totals": totals,
        "status": "WAITING_TO_FULFILL",
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    cache["Order"][orderId] = order
    # Auto-split shipments
    await auto_split_shipments(order)
    # Update cart status to CONVERTED
    cart["status"] = "CONVERTED"
    cart["updatedAt"] = now_iso()
    logger.info(f"Created order {orderNumber} from payment {payment['paymentId']}")


# Routes

@app.route("/entity/Product", methods=["GET", "POST"])
async def product_collection():
    if request.method == "GET":
        # Return all products
        return jsonify(list(cache["Product"].values()))
    else:
        data = await request.get_json()
        sku = data.get("sku")
        if not sku:
            return jsonify({"error": "sku is required"}), 400
        # Create product
        product = {
            "sku": sku,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "price": data.get("price", 0),
            "quantityAvailable": data.get("quantityAvailable", 0),
            "category": data.get("category", ""),
        }
        cache["Product"][sku] = product
        return jsonify(product), 201

@app.route("/entity/Product/<sku>", methods=["PATCH"])
async def product_patch(sku):
    data = await request.get_json()
    product = cache["Product"].get(sku)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    product.update(data)
    return jsonify(product)

@app.route("/entity/Cart", methods=["POST"])
async def cart_post():
    data = await request.get_json()
    cartId = data.get("cartId") or gen_id()
    cart = cache["Cart"].get(cartId)
    if not cart:
        # New cart
        cart = {
            "cartId": cartId,
            "userId": data.get("userId"),
            "status": data.get("status", "NEW"),
            "lines": data.get("lines", []),
            "totalItems": 0,
            "grandTotal": 0,
            "reservationBatchId": None,
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
        }
        cache["Cart"][cartId] = cart
    else:
        # Update existing cart lines/status if provided
        if "lines" in data:
            cart["lines"] = data["lines"]
        if "status" in data:
            cart["status"] = data["status"]
        cart["userId"] = data.get("userId") or cart.get("userId")
        cart["updatedAt"] = now_iso()
    # Business logic: refresh reservation TTL, create/update reservations, recalc totals
    await create_reservations_for_cart(cart)
    await refresh_reservation_ttl(cartId)
    recalc_cart_totals(cart)
    return jsonify(cart)

@app.route("/entity/Cart/<cartId>", methods=["PATCH", "GET"])
async def cart_patch_get(cartId):
    if cartId not in cache["Cart"]:
        return jsonify({"error": "Cart not found"}), 404
    cart = cache["Cart"][cartId]
    if request.method == "PATCH":
        data = await request.get_json()
        # Update fields
        for k in ["lines", "status", "userId"]:
            if k in data:
                cart[k] = data[k]
        cart["updatedAt"] = now_iso()
        # Business logic
        await create_reservations_for_cart(cart)
        await refresh_reservation_ttl(cartId)
        recalc_cart_totals(cart)
        return jsonify(cart)
    else:
        return jsonify(cart)

@app.route("/entity/User", methods=["POST"])
async def user_post():
    data = await request.get_json()
    # Upsert by userId or email
    userId = data.get("userId")
    email = data.get("email")
    # Find existing user by userId or email
    user = None
    if userId:
        user = cache["User"].get(userId)
    if not user and email:
        for u in cache["User"].values():
            if u.get("email") == email:
                user = u
                userId = user["userId"]
                break
    if not user:
        userId = userId or gen_id()
        user = {
            "userId": userId,
            "name": data.get("name", ""),
            "email": email,
            "phone": data.get("phone"),
            "addresses": data.get("addresses", {}),
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
        }
    else:
        # Update existing user fields
        for field in ["name", "email", "phone", "addresses"]:
            if field in data:
                user[field] = data[field]
        user["updatedAt"] = now_iso()
    cache["User"][userId] = user
    return jsonify(user)

@app.route("/entity/User/<userId>", methods=["PATCH"])
async def user_patch(userId):
    user = cache["User"].get(userId)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = await request.get_json()
    for field in ["name", "email", "phone", "addresses"]:
        if field in data:
            user[field] = data[field]
    user["updatedAt"] = now_iso()
    return jsonify(user)

@app.route("/entity/Payment", methods=["POST"])
async def payment_post():
    data = await request.get_json()
    paymentId = data.get("paymentId") or gen_id()
    cartId = data.get("cartId")
    amount = data.get("amount", 0)
    provider = data.get("provider", "DUMMY")
    status = data.get("status", "INITIATED")
    payment = {
        "paymentId": paymentId,
        "cartId": cartId,
        "amount": amount,
        "provider": provider,
        "status": status,
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    cache["Payment"][paymentId] = payment
    # Fire & forget auto mark paid in 3s
    asyncio.create_task(auto_mark_paid(paymentId))
    return jsonify(payment), 201

@app.route("/entity/Order", methods=["POST"])
async def order_post():
    data = await request.get_json()
    # For prototype: orders created only via payment auto flow
    # Accept order creation requests but just mock creation here
    orderId = data.get("orderId") or gen_id()
    orderNumber = data.get("orderNumber") or gen_ulid()
    order = {
        "orderId": orderId,
        "orderNumber": orderNumber,
        "userId": data.get("userId"),
        "shippingAddress": data.get("shippingAddress", {}),
        "lines": data.get("lines", []),
        "totals": data.get("totals", {}),
        "status": data.get("status", "WAITING_TO_FULFILL"),
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    cache["Order"][orderId] = order
    # TODO: in full implementation, commit reservations, decrement stock, split shipments
    return jsonify(order), 201

@app.route("/entity/Order/<orderId>", methods=["PATCH", "GET"])
async def order_patch_get(orderId):
    order = cache["Order"].get(orderId)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    if request.method == "PATCH":
        data = await request.get_json()
        for k in ["status", "lines", "shippingAddress", "totals"]:
            if k in data:
                order[k] = data[k]
        order["updatedAt"] = now_iso()
        return jsonify(order)
    else:
        return jsonify(order)

@app.route("/entity/Shipment/<shipmentId>", methods=["PATCH", "GET"])
async def shipment_patch_get(shipmentId):
    shipment = cache["Shipment"].get(shipmentId)
    if not shipment:
        return jsonify({"error": "Shipment not found"}), 404
    if request.method == "PATCH":
        data = await request.get_json()
        for k in ["status", "carrier", "trackingNumber", "lines"]:
            if k in data:
                shipment[k] = data[k]
        shipment["updatedAt"] = now_iso()
        # After shipment update, aggregate order status
        await aggregate_order_status(shipment["orderId"])
        return jsonify(shipment)
    else:
        return jsonify(shipment)

@app.route("/entity/PickLedger", methods=["POST"])
async def pickledger_post():
    data = await request.get_json()
    pickId = data.get("pickId") or gen_id()
    pick = {
        "pickId": pickId,
        "orderId": data.get("orderId"),
        "shipmentId": data.get("shipmentId"),
        "sku": data.get("sku"),
        "delta": data.get("delta"),
        "at": data.get("at") or now_iso(),
        "actor": data.get("actor"),
        "note": data.get("note"),
    }
    cache["PickLedger"][pickId] = pick
    # Update shipment lines qtyPicked accordingly
    shipment = cache["Shipment"].get(pick["shipmentId"])
    if shipment:
        for line in shipment["lines"]:
            if line["sku"] == pick["sku"]:
                line["qtyPicked"] = line.get("qtyPicked", 0) + pick["delta"]
                # Clamp qtyPicked max qtyOrdered
                if line["qtyPicked"] > line["qtyOrdered"]:
                    line["qtyPicked"] = line["qtyOrdered"]
        # Auto advance shipment status if fully picked
        all_picked = all(l["qtyPicked"] >= l["qtyOrdered"] for l in shipment["lines"])
        if all_picked and shipment["status"] == "PICKING":
            shipment["status"] = "WAITING_TO_SEND"
            shipment["updatedAt"] = now_iso()
            # Aggregate order status
            await aggregate_order_status(shipment["orderId"])
    return jsonify(pick), 201


if __name__ == '__main__':
    import sys, logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
```
