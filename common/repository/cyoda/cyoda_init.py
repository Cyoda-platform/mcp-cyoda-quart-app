import asyncio
import json
import logging
import os
from pathlib import Path

from common.auth.cyoda_auth import CyodaAuthService
from common.config.config import CYODA_API_URL, IMPORT_WORKFLOWS, CYODA_CLIENT_ID, CYODA_CLIENT_SECRET, CYODA_TOKEN_URL, \
    ENTITY_VERSION
from common.repository.cyoda.cyoda_repository import CyodaRepository
from common.utils.utils import send_cyoda_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

entity_dir = Path(__file__).resolve().parent.parent.parent.parent / 'entity'

API_V_WORKFLOWS_ = "api/v1/workflows"


class CyodaInitService:
    def __init__(self, cyoda_repository: CyodaRepository, cyoda_auth_service: CyodaAuthService):
        self.cyoda_repository = cyoda_repository
        self.entity_dir = Path(__file__).resolve().parent.parent.parent.parent / 'entity'
        self.API_V_WORKFLOWS_ = "api/v1/workflows"
        self.cyoda_auth_service = cyoda_auth_service

    async def initialize_service(self):
        await self.init_cyoda(token=self.cyoda_auth_service)

    async def init_cyoda(self, token: CyodaAuthService):
        await self.init_entities_schema(entity_dir=self.entity_dir, token=token)

    async def init_entities_schema(self, entity_dir, token: CyodaAuthService):
        if IMPORT_WORKFLOWS:
            for json_file in entity_dir.glob('*/**/*.json'):
                # Ensure the JSON file is in an immediate subdirectory
                if json_file.parent.parent.name != "entity" or json_file.name != 'workflow.json':
                    continue
                try:
                    entity_name = json_file.parent.name
                    await self.init_workflow(entity_dir=json_file.parent, token=token, entity_name=entity_name)
                except Exception as e:
                    print(f"Error reading {json_file}: {e}")
                    logger.exception(e)

    async def init_workflow(self, entity_dir, token: CyodaAuthService, entity_name):
        # Traverse the directory structure
        files_set = {Path('')}
        for root, dirs, files in os.walk(entity_dir):
            # Look for 'workflow.json' files
            if 'workflow.json' in files:
                file_path = Path(root) / 'workflow.json'
                if file_path not in files_set:
                    workflow_dto = json.loads(file_path.read_text())
                    dto = {"workflows": [workflow_dto]}

                    # Use the new endpoint format: model/{entity_name}/{ENTITY_VERSION}/workflow/import
                    import_path = f"model/{entity_name}/{ENTITY_VERSION}/workflow/import"
                    logger.debug("🔗 Using import endpoint: %s", import_path)

                    response = await send_cyoda_request(cyoda_auth_service=token, method="post", base_url=CYODA_API_URL,
                                                        path=import_path,
                                                        data=json.dumps(dto))

                    # Check response status and log accordingly
                    status_code = response.get('status', 0)
                    if 200 <= status_code < 300:
                        logger.info("✅ Successfully imported workflow for entity: %s", entity_name)
                    else:
                        error_body = response.get('json', {})
                        error_msg = f"Failed to import workflow for entity {entity_name}. Status code: {status_code}, body: {error_body}"
                        logger.error("❌ %s", error_msg)
                        raise RuntimeError(error_msg)

                    return response
        return None


def main():
    # Initialize required services and repository
    cyoda_auth_service = CyodaAuthService(
        client_id=CYODA_CLIENT_ID,
        client_secret=CYODA_CLIENT_SECRET,
        token_url=CYODA_TOKEN_URL
    )
    cyoda_repository = CyodaRepository(
        cyoda_auth_service=cyoda_auth_service)  # Make sure this can be instantiated or mocked appropriately

    # Create the CyodaInitService instance
    init_service = CyodaInitService(cyoda_repository, cyoda_auth_service)

    # Run the async start method using asyncio
    asyncio.run(init_service.initialize_service())


if __name__ == "__main__":
    main()
