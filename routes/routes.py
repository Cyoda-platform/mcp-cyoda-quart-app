from dataclasses import dataclass
from typing import Optional, List, Dict
from quart import Quart, request, jsonify
from quart_schema import QuartSchema, validate_request
import asyncio, datetime, uuid, ulid, logging
from app_init.app_init import BeanFactory
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

factory = BeanFactory(config={'CHAT_REPOSITORY': 'cyoda'})
entity_service = factory.get_services()['entity_service']
cyoda_auth_service = factory.get_services()["cyoda_auth_service"]

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

def now_iso():
    return datetime.datetime.utcnow().isoformat()+"Z"

def gen_id():
    return str(uuid.uuid4())

def gen_ulid():
    return str(ulid.new())

async def auto_mark_paid(payment_id: str):
    try:
        await asyncio.sleep(0.1)
        logger.info(f"Auto mark paid triggered for payment_id={payment_id}")
        # Insert real logic here, e.g., update related entities except payment itself
    except Exception as e:
        logger.error(f"auto_mark_paid failed for payment_id={payment_id}: {e}")

async def process_product(entity: dict):
    sku = entity.get('sku')
    if sku and isinstance(sku, str):
        entity['sku'] = sku.upper()
    return entity

async def process_cart(entity: dict):
    if not entity.get('status'):
        entity['status'] = 'new'
    return entity

async def process_user(entity: dict):
    if not entity.get('userId'):
        entity['userId'] = gen_id()
    return entity

async def process_payment(entity: dict):
    if not entity.get('paymentId'):
        entity['paymentId'] = gen_id()
    asyncio.create_task(auto_mark_paid(entity['paymentId']))
    return entity

async def process_order(entity: dict):
    if not entity.get('orderId'):
        entity['orderId'] = gen_id()
    return entity

async def process_shipment(entity: dict):
    return entity

async def process_pickledger(entity: dict):
    if not entity.get('pickId'):
        entity['pickId'] = gen_id()
    return entity

@app.route("/entity/Product", methods=["GET"])
async def product_list():
    try:
        items = await entity_service.get_items(
            token=cyoda_auth_service,
            entity_model="product",
            entity_version=ENTITY_VERSION,
        )
        return jsonify(items)
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to get products"}), 500

@app.route("/entity/Product", methods=["POST"])
@validate_request(ProductRequest)
async def product_create(data: ProductRequest):
    try:
        product = data.__dict__
        id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model="product",
            entity_version=ENTITY_VERSION,
            entity=product
        )
        return jsonify({"id": id}), 201
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to create product"}), 500

@app.route("/entity/Product/<string:sku>", methods=["PATCH"])
async def product_patch(sku):
    try:
        data = await request.get_json()
        existing = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model="product",
            entity_version=ENTITY_VERSION,
            technical_id=sku
        )
        if not existing:
            return jsonify({"error": "not found"}), 404
        existing.update(data)
        await entity_service.update_item(
            token=cyoda_auth_service,
            entity_model="product",
            entity_version=ENTITY_VERSION,
            entity=existing,
            technical_id=sku,
            meta={}
        )
        return jsonify(existing)
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to patch product"}), 500

@app.route("/entity/Cart", methods=["POST"])
@validate_request(CartRequest)
async def cart_create(data: CartRequest):
    try:
        cart = data.__dict__
        id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model="cart",
            entity_version=ENTITY_VERSION,
            entity=cart
        )
        return jsonify({"id": id}), 201
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to create cart"}), 500

@app.route("/entity/Cart/<string:cartId>", methods=["PATCH"])
@validate_request(CartPatchRequest)
async def cart_patch(data: CartPatchRequest, cartId):
    try:
        existing = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model="cart",
            entity_version=ENTITY_VERSION,
            technical_id=cartId
        )
        if not existing:
            return jsonify({"error": "not found"}), 404
        update_data = data.__dict__
        update_data = {k: v for k, v in update_data.items() if v is not None}
        existing.update(update_data)
        await entity_service.update_item(
            token=cyoda_auth_service,
            entity_model="cart",
            entity_version=ENTITY_VERSION,
            entity=existing,
            technical_id=cartId,
            meta={}
        )
        return jsonify(existing)
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to patch cart"}), 500

@app.route("/entity/Cart/<string:cartId>", methods=["GET"])
async def cart_get(cartId):
    try:
        cart = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model="cart",
            entity_version=ENTITY_VERSION,
            technical_id=cartId
        )
        if not cart:
            return jsonify({}), 404
        return jsonify(cart)
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to get cart"}), 500

@app.route("/entity/User", methods=["POST"])
@validate_request(UserRequest)
async def user_upsert(data: UserRequest):
    try:
        user = data.__dict__
        id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model="user",
            entity_version=ENTITY_VERSION,
            entity=user
        )
        return jsonify({"id": id}), 201
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to upsert user"}), 500

@app.route("/entity/User/<string:userId>", methods=["PATCH"])
async def user_patch(userId):
    try:
        data = await request.get_json()
        existing = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model="user",
            entity_version=ENTITY_VERSION,
            technical_id=userId
        )
        if not existing:
            return jsonify({"error": "not found"}), 404
        existing.update(data)
        await entity_service.update_item(
            token=cyoda_auth_service,
            entity_model="user",
            entity_version=ENTITY_VERSION,
            entity=existing,
            technical_id=userId,
            meta={}
        )
        return jsonify(existing)
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to patch user"}), 500

@app.route("/entity/Payment", methods=["POST"])
@validate_request(PaymentRequest)
async def payment_create(data: PaymentRequest):
    try:
        payment = data.__dict__
        id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model="payment",
            entity_version=ENTITY_VERSION,
            entity=payment
        )
        return jsonify({"id": id}), 201
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to create payment"}), 500

@app.route("/entity/Order", methods=["POST"])
@validate_request(OrderRequest)
async def order_create(data: OrderRequest):
    try:
        order = data.__dict__
        id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model="order",
            entity_version=ENTITY_VERSION,
            entity=order
        )
        return jsonify({"id": id}), 201
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to create order"}), 500

@app.route("/entity/Order/<string:orderId>", methods=["PATCH","GET"])
async def order_patch_get(orderId):
    try:
        if request.method == "GET":
            order = await entity_service.get_item(
                token=cyoda_auth_service,
                entity_model="order",
                entity_version=ENTITY_VERSION,
                technical_id=orderId
            )
            if not order:
                return jsonify({}), 404
            return jsonify(order)
        data = await request.get_json()
        existing = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model="order",
            entity_version=ENTITY_VERSION,
            technical_id=orderId
        )
        if not existing:
            return jsonify({"error": "not found"}), 404
        existing.update(data)
        await entity_service.update_item(
            token=cyoda_auth_service,
            entity_model="order",
            entity_version=ENTITY_VERSION,
            entity=existing,
            technical_id=orderId,
            meta={}
        )
        return jsonify(existing)
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to process order"}), 500

@app.route("/entity/Shipment/<string:shipmentId>", methods=["PATCH","GET"])
async def shipment_patch_get(shipmentId):
    try:
        if request.method == "GET":
            shipment = await entity_service.get_item(
                token=cyoda_auth_service,
                entity_model="shipment",
                entity_version=ENTITY_VERSION,
                technical_id=shipmentId
            )
            if not shipment:
                return jsonify({}), 404
            return jsonify(shipment)
        data = await request.get_json()
        existing = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model="shipment",
            entity_version=ENTITY_VERSION,
            technical_id=shipmentId
        )
        if not existing:
            return jsonify({"error": "not found"}), 404
        existing.update(data)
        await entity_service.update_item(
            token=cyoda_auth_service,
            entity_model="shipment",
            entity_version=ENTITY_VERSION,
            entity=existing,
            technical_id=shipmentId,
            meta={}
        )
        return jsonify(existing)
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to process shipment"}), 500

@app.route("/entity/PickLedger", methods=["POST"])
@validate_request(PickLedgerRequest)
async def pickledger_create(data: PickLedgerRequest):
    try:
        pick = data.__dict__
        id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model="pickledger",
            entity_version=ENTITY_VERSION,
            entity=pick
        )
        return jsonify({"id": id}), 201
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "failed to create pickledger"}), 500

if __name__ == '__main__':
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)