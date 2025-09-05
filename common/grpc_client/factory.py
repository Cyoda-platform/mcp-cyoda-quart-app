"""
Factory for creating GrpcStreamingFacade with all components properly wired.
This contains all the complex logic moved out of GrpcClient.
"""
import types
from typing import Optional

from common.grpc_client.facade import GrpcStreamingFacade
from common.grpc_client.outbox import Outbox
from common.grpc_client.router import EventRouter
from common.grpc_client.responses.builders import (
    ResponseBuilderRegistry, JoinResponseBuilder, AckResponseBuilder,
    CalcResponseBuilder, CriteriaCalcResponseBuilder,
)
from common.grpc_client.middleware.config import (
    MiddlewareChainBuilder, create_default_middleware_config
)
from common.grpc_client.handlers.keep_alive import KeepAliveHandler
from common.grpc_client.handlers.ack import AckHandler
from common.grpc_client.handlers.greet import GreetHandler
from common.grpc_client.handlers.error import ErrorHandler
from common.grpc_client.handlers.calc import CalcRequestHandler
from common.grpc_client.handlers.criteria_calc import CriteriaCalcRequestHandler
from common.grpc_client.constants import (
    JOIN_EVENT_TYPE, EVENT_ACK_TYPE, CALC_RESP_EVENT_TYPE, CRITERIA_CALC_RESP_EVENT_TYPE,
    KEEP_ALIVE_EVENT_TYPE, GREET_EVENT_TYPE, ERROR_EVENT_TYPE, CALC_REQ_EVENT_TYPE, CRITERIA_CALC_REQ_EVENT_TYPE,
)


class GrpcStreamingFacadeFactory:
    """Factory that creates and wires all components for the GrpcStreamingFacade."""
    
    @staticmethod
    def create( auth,  processor_loop, grpc_client=None) -> GrpcStreamingFacade:
        """Create a fully configured GrpcStreamingFacade with all components."""

        # Import here to avoid circular imports
        from service.services import get_processor_manager

        # Create services object for handlers with processor manager
        services = types.SimpleNamespace(
            processor_loop=processor_loop,
            processor_manager=get_processor_manager()
        )

        # Create and configure EventRouter with handlers
        router = EventRouter()
        router.register(KEEP_ALIVE_EVENT_TYPE, KeepAliveHandler())
        router.register(EVENT_ACK_TYPE, AckHandler())
        router.register(GREET_EVENT_TYPE, GreetHandler())
        router.register(ERROR_EVENT_TYPE, ErrorHandler())
        router.register(CALC_REQ_EVENT_TYPE, CalcRequestHandler())
        router.register(CRITERIA_CALC_REQ_EVENT_TYPE, CriteriaCalcRequestHandler())

        # Create and configure ResponseBuilderRegistry
        builders = ResponseBuilderRegistry()
        builders.register(JOIN_EVENT_TYPE, JoinResponseBuilder())
        builders.register(EVENT_ACK_TYPE, AckResponseBuilder())
        builders.register(CALC_RESP_EVENT_TYPE, CalcResponseBuilder())
        builders.register(CRITERIA_CALC_RESP_EVENT_TYPE, CriteriaCalcResponseBuilder())

        # Create Outbox
        outbox = Outbox()

        # Create middleware chain using configuration
        middleware_config = create_default_middleware_config()
        middleware_builder = MiddlewareChainBuilder()

        first_middleware = middleware_builder.build_chain(
            config=middleware_config,
            router=router,
            builders=builders,
            outbox=outbox,
            services=services
        )

        if not first_middleware:
            raise RuntimeError("Failed to create middleware chain")

        # Create and return facade
        return GrpcStreamingFacade(
            auth=auth,
            router=router,
            builders=builders,
            outbox=outbox,
            first_middleware=first_middleware,
            grpc_client=grpc_client
        )
