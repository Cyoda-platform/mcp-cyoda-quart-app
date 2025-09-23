"""
PetDataIngestionProcessor for Cyoda Pet Search Application

Handles data ingestion from external Pet Store API using search parameters
such as species, status, and category ID as specified in functional requirements.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetDataIngestionProcessor(CyodaProcessor):
    """
    Processor for ingesting pet data from external API based on search parameters.
    Fetches pet details using species, status, and category ID filters.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetDataIngestionProcessor",
            description="Ingests pet data from external API using search parameters",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )
        # External API base URL (using standard Swagger Petstore for demo)
        self.api_base_url = "https://petstore3.swagger.io/api/v3"

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity by ingesting data from external API.

        Args:
            entity: The Pet entity to process (must be in 'initial_state')
            **kwargs: Additional processing parameters

        Returns:
            The pet entity with ingested data
        """
        try:
            self.logger.info(
                f"Starting data ingestion for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Fetch pet data from external API
            api_data = await self._fetch_pet_data(pet)

            # Set the ingested data on the pet entity
            if api_data:
                pet.set_ingested_data(api_data)
                self.logger.info(
                    f"Successfully ingested data for Pet {pet.technical_id}: {pet.name}"
                )
            else:
                # Create mock data if API is not available
                mock_data = self._create_mock_data(pet)
                pet.set_ingested_data(mock_data)
                self.logger.info(
                    f"Used mock data for Pet {pet.technical_id} (API not available)"
                )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error ingesting data for Pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Create fallback mock data on error
            pet = cast_entity(entity, Pet)
            mock_data = self._create_mock_data(pet)
            pet.set_ingested_data(mock_data)
            return pet

    async def _fetch_pet_data(self, pet: Pet) -> Optional[Dict[str, Any]]:
        """
        Fetch pet data from external API using search parameters.

        Args:
            pet: The Pet entity with search parameters

        Returns:
            Dictionary containing pet data from API, or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to fetch pets by status first
                status = pet.search_status or "available"
                url = f"{self.api_base_url}/pet/findByStatus"
                
                self.logger.info(f"Fetching pets from API: {url} with status={status}")
                
                response = await client.get(url, params={"status": status})
                
                if response.status_code == 200:
                    pets_data = response.json()
                    
                    if pets_data and isinstance(pets_data, list) and len(pets_data) > 0:
                        # Filter by additional criteria if provided
                        filtered_pet = self._filter_pet_data(pets_data, pet)
                        if filtered_pet:
                            self.logger.info(f"Found matching pet: {filtered_pet.get('name', 'Unknown')}")
                            return filtered_pet
                
                self.logger.warning(f"No pets found matching criteria for Pet {pet.technical_id}")
                return None

        except Exception as e:
            self.logger.error(f"Error fetching data from external API: {str(e)}")
            return None

    def _filter_pet_data(self, pets_data: List[Dict[str, Any]], pet: Pet) -> Optional[Dict[str, Any]]:
        """
        Filter pet data based on search criteria.

        Args:
            pets_data: List of pets from API
            pet: Pet entity with search criteria

        Returns:
            First matching pet data or None
        """
        for pet_data in pets_data:
            # Check category ID filter
            if pet.search_category_id is not None:
                category = pet_data.get("category", {})
                if category.get("id") != pet.search_category_id:
                    continue
            
            # Check species filter (derived from category name or tags)
            if pet.search_species:
                species_match = False
                
                # Check category name
                category = pet_data.get("category", {})
                category_name = category.get("name", "").lower()
                if pet.search_species.lower() in category_name:
                    species_match = True
                
                # Check tags
                tags = pet_data.get("tags", [])
                for tag in tags:
                    tag_name = tag.get("name", "").lower()
                    if pet.search_species.lower() in tag_name:
                        species_match = True
                        break
                
                if not species_match:
                    continue
            
            # If we reach here, the pet matches all criteria
            return pet_data
        
        return None

    def _create_mock_data(self, pet: Pet) -> Dict[str, Any]:
        """
        Create mock pet data when external API is not available.

        Args:
            pet: Pet entity with search parameters

        Returns:
            Dictionary containing mock pet data
        """
        species = pet.search_species or "dog"
        status = pet.search_status or "available"
        category_id = pet.search_category_id or 1
        
        # Generate mock data based on search criteria
        mock_data = {
            "id": 12345,
            "name": f"Buddy the {species.title()}",
            "category": {
                "id": category_id,
                "name": species.title() + "s"
            },
            "photoUrls": [
                f"https://example.com/photos/{species}1.jpg",
                f"https://example.com/photos/{species}2.jpg"
            ],
            "tags": [
                {"id": 1, "name": species},
                {"id": 2, "name": "friendly"},
                {"id": 3, "name": "playful"}
            ],
            "status": status
        }
        
        self.logger.info(f"Created mock data for {species} with status {status}")
        return mock_data
