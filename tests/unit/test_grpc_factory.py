"""
Unit tests for GrpcStreamingFacadeFactory.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from common.grpc_client.constants import (
    CALC_REQ_EVENT_TYPE,
    CALC_RESP_EVENT_TYPE,
    CRITERIA_CALC_REQ_EVENT_TYPE,
    CRITERIA_CALC_RESP_EVENT_TYPE,
    ERROR_EVENT_TYPE,
    EVENT_ACK_TYPE,
    GREET_EVENT_TYPE,
    JOIN_EVENT_TYPE,
    KEEP_ALIVE_EVENT_TYPE,
)
from common.grpc_client.facade import GrpcStreamingFacade
from common.grpc_client.factory import GrpcStreamingFacadeFactory


class TestGrpcStreamingFacadeFactory:
    """Test suite for GrpcStreamingFacadeFactory."""

    @pytest.fixture
    def mock_auth(self):
        """Create mock auth object."""
        return Mock()

    @pytest.fixture
    def mock_processor_loop(self):
        """Create mock processor loop."""
        return Mock()

    @pytest.fixture
    def mock_processor_manager(self):
        """Create mock processor manager."""
        return Mock()

    @pytest.fixture
    def mock_grpc_client(self):
        """Create mock gRPC client."""
        return Mock()

    @patch("services.services.get_processor_manager")
    @patch("common.grpc_client.factory.create_default_middleware_config")
    @patch("common.grpc_client.factory.MiddlewareChainBuilder")
    def test_create_facade(
        self,
        mock_builder_class,
        mock_config_func,
        mock_get_processor_manager,
        mock_auth,
        mock_processor_loop,
        mock_processor_manager,
    ):
        """Test creating a facade with all components."""
        # Setup mocks
        mock_get_processor_manager.return_value = mock_processor_manager
        mock_config = Mock()
        mock_config_func.return_value = mock_config
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_middleware = Mock()
        mock_builder.build_chain.return_value = mock_middleware

        # Create facade
        facade = GrpcStreamingFacadeFactory.create(
            auth=mock_auth, processor_loop=mock_processor_loop
        )

        # Verify facade was created
        assert isinstance(facade, GrpcStreamingFacade)
        assert facade.auth is mock_auth
        assert facade.first_middleware is mock_middleware

        # Verify processor manager was retrieved
        mock_get_processor_manager.assert_called_once()

        # Verify middleware config was created
        mock_config_func.assert_called_once()

        # Verify middleware chain was built
        mock_builder.build_chain.assert_called_once()

    @patch("services.services.get_processor_manager")
    @patch("common.grpc_client.factory.create_default_middleware_config")
    @patch("common.grpc_client.factory.MiddlewareChainBuilder")
    def test_create_facade_with_grpc_client(
        self,
        mock_builder_class,
        mock_config_func,
        mock_get_processor_manager,
        mock_auth,
        mock_processor_loop,
        mock_processor_manager,
        mock_grpc_client,
    ):
        """Test creating a facade with optional grpc_client."""
        # Setup mocks
        mock_get_processor_manager.return_value = mock_processor_manager
        mock_config = Mock()
        mock_config_func.return_value = mock_config
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_middleware = Mock()
        mock_builder.build_chain.return_value = mock_middleware

        # Create facade with grpc_client
        facade = GrpcStreamingFacadeFactory.create(
            auth=mock_auth,
            processor_loop=mock_processor_loop,
            grpc_client=mock_grpc_client,
        )

        # Verify facade was created with grpc_client
        assert isinstance(facade, GrpcStreamingFacade)
        assert facade.grpc_client is mock_grpc_client

    @patch("services.services.get_processor_manager")
    @patch("common.grpc_client.factory.create_default_middleware_config")
    @patch("common.grpc_client.factory.MiddlewareChainBuilder")
    def test_router_has_all_handlers(
        self,
        mock_builder_class,
        mock_config_func,
        mock_get_processor_manager,
        mock_auth,
        mock_processor_loop,
        mock_processor_manager,
    ):
        """Test that router is configured with all required handlers."""
        # Setup mocks
        mock_get_processor_manager.return_value = mock_processor_manager
        mock_config = Mock()
        mock_config_func.return_value = mock_config
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_middleware = Mock()
        mock_builder.build_chain.return_value = mock_middleware

        # Create facade
        facade = GrpcStreamingFacadeFactory.create(
            auth=mock_auth, processor_loop=mock_processor_loop
        )

        # Verify router has all required handlers
        router = facade.router
        assert router.route(Mock(type=KEEP_ALIVE_EVENT_TYPE)) is not None
        assert router.route(Mock(type=EVENT_ACK_TYPE)) is not None
        assert router.route(Mock(type=GREET_EVENT_TYPE)) is not None
        assert router.route(Mock(type=ERROR_EVENT_TYPE)) is not None
        assert router.route(Mock(type=CALC_REQ_EVENT_TYPE)) is not None
        assert router.route(Mock(type=CRITERIA_CALC_REQ_EVENT_TYPE)) is not None

    @patch("services.services.get_processor_manager")
    @patch("common.grpc_client.factory.create_default_middleware_config")
    @patch("common.grpc_client.factory.MiddlewareChainBuilder")
    def test_builders_has_all_response_types(
        self,
        mock_builder_class,
        mock_config_func,
        mock_get_processor_manager,
        mock_auth,
        mock_processor_loop,
        mock_processor_manager,
    ):
        """Test that builders registry has all required response builders."""
        # Setup mocks
        mock_get_processor_manager.return_value = mock_processor_manager
        mock_config = Mock()
        mock_config_func.return_value = mock_config
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_middleware = Mock()
        mock_builder.build_chain.return_value = mock_middleware

        # Create facade
        facade = GrpcStreamingFacadeFactory.create(
            auth=mock_auth, processor_loop=mock_processor_loop
        )

        # Verify builders has all required response types
        builders = facade.builders
        assert builders.get(JOIN_EVENT_TYPE) is not None
        assert builders.get(EVENT_ACK_TYPE) is not None
        assert builders.get(CALC_RESP_EVENT_TYPE) is not None
        assert builders.get(CRITERIA_CALC_RESP_EVENT_TYPE) is not None

    @patch("services.services.get_processor_manager")
    @patch("common.grpc_client.factory.create_default_middleware_config")
    @patch("common.grpc_client.factory.MiddlewareChainBuilder")
    def test_outbox_created(
        self,
        mock_builder_class,
        mock_config_func,
        mock_get_processor_manager,
        mock_auth,
        mock_processor_loop,
        mock_processor_manager,
    ):
        """Test that outbox is created."""
        # Setup mocks
        mock_get_processor_manager.return_value = mock_processor_manager
        mock_config = Mock()
        mock_config_func.return_value = mock_config
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_middleware = Mock()
        mock_builder.build_chain.return_value = mock_middleware

        # Create facade
        facade = GrpcStreamingFacadeFactory.create(
            auth=mock_auth, processor_loop=mock_processor_loop
        )

        # Verify outbox exists
        assert facade.outbox is not None

    @patch("services.services.get_processor_manager")
    @patch("common.grpc_client.factory.create_default_middleware_config")
    @patch("common.grpc_client.factory.MiddlewareChainBuilder")
    def test_middleware_chain_built_with_correct_params(
        self,
        mock_builder_class,
        mock_config_func,
        mock_get_processor_manager,
        mock_auth,
        mock_processor_loop,
        mock_processor_manager,
    ):
        """Test that middleware chain is built with correct parameters."""
        # Setup mocks
        mock_get_processor_manager.return_value = mock_processor_manager
        mock_config = Mock()
        mock_config_func.return_value = mock_config
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_middleware = Mock()
        mock_builder.build_chain.return_value = mock_middleware

        # Create facade
        facade = GrpcStreamingFacadeFactory.create(
            auth=mock_auth, processor_loop=mock_processor_loop
        )

        # Verify build_chain was called with correct parameters
        call_args = mock_builder.build_chain.call_args
        assert call_args.kwargs["config"] is mock_config
        assert call_args.kwargs["router"] is facade.router
        assert call_args.kwargs["builders"] is facade.builders
        assert call_args.kwargs["outbox"] is facade.outbox
        assert call_args.kwargs["services"] is not None

    @patch("services.services.get_processor_manager")
    @patch("common.grpc_client.factory.create_default_middleware_config")
    @patch("common.grpc_client.factory.MiddlewareChainBuilder")
    def test_services_object_created(
        self,
        mock_builder_class,
        mock_config_func,
        mock_get_processor_manager,
        mock_auth,
        mock_processor_loop,
        mock_processor_manager,
    ):
        """Test that services object is created with processor_loop and processor_manager."""
        # Setup mocks
        mock_get_processor_manager.return_value = mock_processor_manager
        mock_config = Mock()
        mock_config_func.return_value = mock_config
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_middleware = Mock()
        mock_builder.build_chain.return_value = mock_middleware

        # Create facade
        GrpcStreamingFacadeFactory.create(
            auth=mock_auth, processor_loop=mock_processor_loop
        )

        # Verify build_chain was called with services
        call_args = mock_builder.build_chain.call_args
        services = call_args.kwargs["services"]
        assert services.processor_loop is mock_processor_loop
        assert services.processor_manager is mock_processor_manager

    @patch("services.services.get_processor_manager")
    @patch("common.grpc_client.factory.create_default_middleware_config")
    @patch("common.grpc_client.factory.MiddlewareChainBuilder")
    def test_middleware_chain_failure_raises_error(
        self,
        mock_builder_class,
        mock_config_func,
        mock_get_processor_manager,
        mock_auth,
        mock_processor_loop,
        mock_processor_manager,
    ):
        """Test that failure to create middleware chain raises RuntimeError."""
        # Setup mocks
        mock_get_processor_manager.return_value = mock_processor_manager
        mock_config = Mock()
        mock_config_func.return_value = mock_config
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        # Return None to simulate failure
        mock_builder.build_chain.return_value = None

        # Verify RuntimeError is raised
        with pytest.raises(RuntimeError) as exc_info:
            GrpcStreamingFacadeFactory.create(
                auth=mock_auth, processor_loop=mock_processor_loop
            )

        assert "Failed to create middleware chain" in str(exc_info.value)
