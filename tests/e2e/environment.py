import asyncio
import logging
import threading
from services.services import initialize_services, get_grpc_client, get_entity_service, get_processor_manager, shutdown_services
from services.config import get_service_config

logger = logging.getLogger(__name__)
test_processor_module = 'tests.e2e.processors'
test_criterion_module = 'tests.e2e.criterions'


def before_all(context):
    config = get_service_config()
    config['processor']['modules'].append(test_processor_module)
    logger.info(f'Config was ehanced. Added new processor module: {test_processor_module}')
    config['processor']['modules'].append(test_criterion_module)
    logger.info(f'Config was ehanced. Added new criterion module: {test_criterion_module}')
    initialize_services(config)
    context.entity_service = get_entity_service()
    processor_manager = get_processor_manager()

    for n, p in getattr(processor_manager, 'processors').items():
        if n != 'test-processor-1':
            continue

        context.processor = p
        break

    context.criterions = {}
    for n, c in getattr(processor_manager, 'criteria').items():
        if n != 'test-criterion-true' and n != 'test-criterion-false':
            continue

        context.criterions[n] = c

    context.grpc_client = get_grpc_client()

    context.loop = asyncio.new_event_loop()

    def run_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    context.loop_thread = threading.Thread(target=run_loop, args=(context.loop,), daemon=True)
    context.loop_thread.start()


def after_all(context):
    if context.loop and context.loop.is_running():
        context.loop.call_soon_threadsafe(context.loop.stop)
    context.loop_thread.join(timeout=5)
    context.loop.close()
    shutdown_services()


def before_scenario(context, scenario):
    grpc_stream_coro = context.grpc_client.grpc_stream()
    context.bg_task_future = asyncio.run_coroutine_threadsafe(
        grpc_stream_coro,
        context.loop
    )


def after_scenario(context, scenario):
    logger.info("  - Cleaning up entities...")
    if hasattr(context, 'entity_service'):
        cleanup_future = asyncio.run_coroutine_threadsafe(
            context.entity_service.delete_all("nobel-prize", "1"),
            context.loop
        )
        try:
            cleanup_future.result(timeout=10)
            logger.info("  - Entity cleanup successful.")
        except Exception as e:
            logger.warn(f"  - Cleanup failed with error: {e}")

    logger.info("  - Gracefully shutting down gRPC stream...")
    if hasattr(context, 'bg_task_future') and not context.bg_task_future.done():
        try:
            shutdown_coro = context.grpc_client.close()
            shutdown_future = asyncio.run_coroutine_threadsafe(shutdown_coro, context.loop)
            shutdown_future.result(timeout=5)

            context.bg_task_future.result(timeout=5)
            logger.info("  - Background gRPC task finished cleanly.")

        except Exception as e:
            logger.warn(f"  - An error occurred during gRPC shutdown: {e}")
            if not context.bg_task_future.done():
                context.loop.call_soon_threadsafe(context.bg_task_future.cancel)
