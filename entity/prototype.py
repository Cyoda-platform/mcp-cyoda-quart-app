from dataclasses import dataclass
from typing import Optional, List, Dict
from quart import Quart, request, jsonify
from quart_schema import QuartSchema, validate_request, validate_querystring
import asyncio, datetime, uuid, ulid, logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# request schemas
@dataclass
class ProductRequest:
    sku: str
    name: str
    description: Optional[str]
    price: float
    quantityAvailable: int
    category: Optional[str]

@dataclass
class CartRequest:
    cartId: Optional[str]
    userId: Optional[str]
    status: str
    lines: List[Dict]

@dataclass
class CartPatchRequest:
    lines: Optional[List[Dict]]
    status: Optional[str]
    userId: Optional[str]

@dataclass
class UserRequest:
    userId: Optional[str]
    name: str
    email: str
    phone: Optional[str]
    addresses: Dict

@dataclass
class PaymentRequest:
    paymentId: Optional[str]
    cartId: str
    amount: float
    provider: str
    status: str

@dataclass
class OrderRequest:
    orderId: Optional[str]
    orderNumber: Optional[str]
    userId: str
    shippingAddress: Dict
    lines: List[Dict]
    totals: Dict
    status: Optional[str]

@dataclass
class PickLedgerRequest:
    pickId: Optional[str]
    orderId: str
    shipmentId: str
    sku: str
    delta: int
    at: Optional[str]
    actor: Optional[str]
    note: Optional[str]

cache = { "Product":{}, "Cart":{}, "User":{}, "Payment":{}, "Order":{}, "Shipment":{}, "Reservation":{}, "PickLedger":{} }
RESERVATION_TTL_SECONDS = 4*3600

def now_iso(): return datetime.datetime.utcnow().isoformat()+"Z"
def gen_id(): return str(uuid.uuid4())
def gen_ulid(): return str(ulid.new())

# PRODUCT
@app.route("/entity/Product", methods=["GET"])
async def product_list():
    return jsonify(list(cache["Product"].values()))

@app.route("/entity/Product", methods=["POST"])
@validate_request(ProductRequest)  # workaround: POST validation last due to quart-schema issue
async def product_create(data: ProductRequest):
    product = data.__dict__
    cache["Product"][product["sku"]] = product
    return jsonify(product), 201

@app.route("/entity/Product/<sku>", methods=["PATCH"])
async def product_patch(sku):
    data = await request.get_json()
    product = cache["Product"].get(sku)
    if not product: return jsonify({"error":"not found"}),404
    product.update(data)
    return jsonify(product)

# CART
@app.route("/entity/Cart", methods=["POST"])
@validate_request(CartRequest)  # workaround: POST validation last due to quart-schema issue
async def cart_create(data: CartRequest):
    # ... original logic using data.__dict__ ...
    cart = data.__dict__
    return jsonify(cart)

@app.route("/entity/Cart/<cartId>", methods=["PATCH"])
@validate_request(CartPatchRequest)  # workaround: POST validation last due to quart-schema issue
async def cart_patch(data: CartPatchRequest, cartId):
    # ... original logic using data.__dict__ ...
    return jsonify({})

@app.route("/entity/Cart/<cartId>", methods=["GET"])
async def cart_get(cartId):
    return jsonify(cache["Cart"].get(cartId, {}))

# USER
@app.route("/entity/User", methods=["POST"])
@validate_request(UserRequest)  # workaround: POST validation last due to quart-schema issue
async def user_upsert(data: UserRequest):
    user = data.__dict__
    userId = user.get("userId") or gen_id()
    user["userId"] = userId
    cache["User"][userId] = user
    return jsonify(user)

@app.route("/entity/User/<userId>", methods=["PATCH"])
async def user_patch(userId):
    data = await request.get_json()
    user = cache["User"].get(userId)
    if not user: return jsonify({"error":"not found"}),404
    user.update(data)
    return jsonify(user)

# PAYMENT
@app.route("/entity/Payment", methods=["POST"])
@validate_request(PaymentRequest)  # workaround: POST validation last due to quart-schema issue
async def payment_create(data: PaymentRequest):
    payment = data.__dict__
    payment["paymentId"] = payment.get("paymentId") or gen_id()
    cache["Payment"][payment["paymentId"]] = payment
    asyncio.create_task(auto_mark_paid(payment["paymentId"]))
    return jsonify(payment), 201

# ORDER
@app.route("/entity/Order", methods=["POST"])
@validate_request(OrderRequest)  # workaround: POST validation last due to quart-schema issue
async def order_create(data: OrderRequest):
    order = data.__dict__
    order["orderId"] = order.get("orderId") or gen_id()
    cache["Order"][order["orderId"]] = order
    return jsonify(order), 201

@app.route("/entity/Order/<orderId>", methods=["PATCH","GET"])
async def order_patch_get(orderId):
    if request.method=="GET":
        return jsonify(cache["Order"].get(orderId, {}))
    data = await request.get_json()
    cache["Order"][orderId].update(data)
    return jsonify(cache["Order"][orderId])

# SHIPMENT
@app.route("/entity/Shipment/<shipmentId>", methods=["PATCH","GET"])
async def shipment_patch_get(shipmentId):
    if request.method=="GET":
        return jsonify(cache["Shipment"].get(shipmentId, {}))
    data = await request.get_json()
    cache["Shipment"][shipmentId].update(data)
    return jsonify(cache["Shipment"][shipmentId])

# PICKLEDGER
@app.route("/entity/PickLedger", methods=["POST"])
@validate_request(PickLedgerRequest)  # workaround: POST validation last due to quart-schema issue
async def pickledger_create(data: PickLedgerRequest):
    pick = data.__dict__
    pick["pickId"] = pick.get("pickId") or gen_id()
    cache["PickLedger"][pick["pickId"]] = pick
    return jsonify(pick), 201

if __name__ == '__main__':
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)