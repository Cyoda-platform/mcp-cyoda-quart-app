import asyncio
import threading
from services.services import initialize_services, get_grpc_client, get_entity_service, get_processor_manager, shutdown_services
from services.config import get_service_config


def before_all(context):
    config = get_service_config()
    initialize_services(config)
    context.entity_service = get_entity_service()
    processor_manager = get_processor_manager()

    processors = getattr(processor_manager, 'processors').items()

    for n, p in processors:
        if n != 'test-processor-1':
            continue

        context.processor = p

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
    #context.processors.clear()
    print("  - Cleaning up entities...")
    cleanup_future = asyncio.run_coroutine_threadsafe(
        context.entity_service.delete_all("nobel-prize", "1"),
        context.loop
    )
    try:
        cleanup_future.result(timeout=10)
        print("  - Entity cleanup successful.")
    except Exception as e:
        print(f"  - WARNING: Cleanup failed with error: {e}")

    print("  - Cancelling background gRPC stream...")
    if hasattr(context, 'bg_task_future') and not context.bg_task_future.done():
        context.loop.call_soon_threadsafe(context.bg_task_future.cancel)
        try:
            context.bg_task_future.result(timeout=5)
        except asyncio.CancelledError:
            print("  - Background task successfully cancelled.")
        except Exception as e:
            print(f"  - An error occurred during task cancellation: {e}")
