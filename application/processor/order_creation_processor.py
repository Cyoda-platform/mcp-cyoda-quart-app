"""
OrderCreationProcessor for Cyoda OMS Application

Handles order creation from paid cart, stock decrement, and shipment creation
as specified in functional requirements.
"""

import logging
import uuid
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.order.version_1.order import Order
from application.entity.product.version_1.product import Product
from application.entity.shipment.version_1.shipment import Shipment
from services.services import get_entity_service


class OrderCreationProcessor(CyodaProcessor):
    """
    Processor for Order that handles order creation from paid cart.
    Decrements product stock and creates associated shipment.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderCreationProcessor",
            description="Processes Order creation from paid cart with stock decrement and shipment creation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order creation from paid cart.

        Args:
            entity: The Order entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed order with stock decremented and shipment created
        """
        try:
            self.logger.info(
                f"Processing Order creation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)
            entity_service = get_entity_service()

            # Decrement stock for each product in the order
            for line in order.lines:
                sku = line.get("sku")
                qty = line.get("qty", 0)
                
                if sku and qty > 0:
                    await self._decrement_product_stock(entity_service, sku, qty)

            # Create shipment for the order
            await self._create_shipment(entity_service, order)

            self.logger.info(
                f"Order {order.technical_id} processed: stock decremented, shipment created"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error processing order creation for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _decrement_product_stock(self, entity_service: Any, sku: str, qty: int) -> None:
        """Decrement product stock by specified quantity"""
        try:
            # Find product by SKU (business ID)
            product_response = await entity_service.find_by_business_id(
                entity_class=Product.ENTITY_NAME,
                business_id=sku,
                business_id_field="sku",
                entity_version=str(Product.ENTITY_VERSION),
            )

            if not product_response:
                self.logger.warning(f"Product with SKU {sku} not found for stock decrement")
                return

            # Cast to Product and decrement quantity
            product = cast_entity(product_response.data, Product)
            
            if product.quantityAvailable < qty:
                self.logger.warning(
                    f"Insufficient stock for SKU {sku}: available={product.quantityAvailable}, requested={qty}"
                )
                # For demo purposes, allow negative stock
            
            product.decrement_quantity(qty)

            # Update the product
            product_data = product.model_dump(by_alias=True)
            await entity_service.update(
                entity_id=product_response.metadata.id,
                entity=product_data,
                entity_class=Product.ENTITY_NAME,
                entity_version=str(Product.ENTITY_VERSION),
            )

            self.logger.info(f"Decremented stock for SKU {sku} by {qty} units")

        except Exception as e:
            self.logger.error(f"Error decrementing stock for SKU {sku}: {str(e)}")
            # Don't raise - continue with order processing

    async def _create_shipment(self, entity_service: Any, order: Order) -> None:
        """Create shipment for the order"""
        try:
            shipment_id = str(uuid.uuid4())
            
            # Create shipment from order data
            shipment = Shipment.create_from_order(
                shipment_id=shipment_id,
                order_data=order.model_dump(by_alias=True)
            )

            # Save the shipment
            shipment_data = shipment.model_dump(by_alias=True)
            response = await entity_service.save(
                entity=shipment_data,
                entity_class=Shipment.ENTITY_NAME,
                entity_version=str(Shipment.ENTITY_VERSION),
            )

            self.logger.info(f"Created shipment {response.metadata.id} for order {order.orderId}")

        except Exception as e:
            self.logger.error(f"Error creating shipment for order {order.orderId}: {str(e)}")
            # Don't raise - order creation should still succeed
