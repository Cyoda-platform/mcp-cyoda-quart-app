"""
PetDataTransformationProcessor for Cyoda Pet Search Application

Handles transformation of pet data into user-friendly format, including
renaming fields and incorporating additional attributes as specified
in functional requirements.
"""

import logging
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetDataTransformationProcessor(CyodaProcessor):
    """
    Processor for transforming pet data into user-friendly format.
    Converts raw API data to display-ready format with enhanced attributes.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetDataTransformationProcessor",
            description="Transforms pet data into user-friendly format with enhanced attributes",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity by transforming data to user-friendly format.

        Args:
            entity: The Pet entity to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The pet entity with transformed user-friendly data
        """
        try:
            self.logger.info(
                f"Starting data transformation for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Create transformation data
            transformation_data = self._create_transformation_data(pet)

            # Apply transformations to the pet entity
            pet.set_transformed_data(transformation_data)

            self.logger.info(
                f"Successfully transformed data for Pet {pet.technical_id}: {pet.display_name}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error transforming data for Pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_transformation_data(self, pet: Pet) -> Dict[str, Any]:
        """
        Create transformation data with user-friendly enhancements.

        Args:
            pet: The Pet entity with ingested data

        Returns:
            Dictionary containing transformation metadata and enhancements
        """
        transformation_data: Dict[str, Any] = {
            "transformation_type": "user_friendly_format",
            "original_name": pet.name,
            "enhancements_applied": [],
        }

        # Apply field renaming transformations
        enhancements = []

        # 1. Transform name to display name with emoji
        if pet.name:
            original_name = pet.name
            # Add appropriate emoji based on species or category
            emoji = self._get_species_emoji(pet)
            transformed_name = f"{emoji} {original_name}"
            enhancements.append(f"Added emoji to name: '{original_name}' -> '{transformed_name}'")

        # 2. Transform status to availability status
        if pet.status:
            original_status = pet.status
            status_mapping = {
                "available": "✅ Available for Adoption",
                "pending": "⏳ Adoption Pending", 
                "sold": "❤️ Already Adopted"
            }
            transformed_status = status_mapping.get(original_status, original_status)
            enhancements.append(f"Enhanced status: '{original_status}' -> '{transformed_status}'")

        # 3. Derive species information
        species = self._derive_species(pet)
        if species:
            enhancements.append(f"Derived species: '{species}' from category/tags")

        # 4. Generate descriptive text
        description = self._generate_description(pet, species)
        if description:
            enhancements.append(f"Generated description: '{description}'")

        # 5. Add additional user-friendly attributes
        additional_attributes = self._create_additional_attributes(pet, species)
        if additional_attributes:
            enhancements.append(f"Added {len(additional_attributes)} additional attributes")

        transformation_data["enhancements_applied"] = enhancements
        transformation_data["additional_attributes"] = additional_attributes

        return transformation_data

    def _get_species_emoji(self, pet: Pet) -> str:
        """Get appropriate emoji based on pet species/category."""
        species = self._derive_species(pet)
        
        emoji_mapping = {
            "dog": "🐕",
            "cat": "🐱", 
            "bird": "🐦",
            "fish": "🐠",
            "rabbit": "🐰",
            "hamster": "🐹",
        }
        
        return emoji_mapping.get(species, "🐾")

    def _derive_species(self, pet: Pet) -> str:
        """Derive species from category name or tags."""
        # Check category first
        if pet.category and "name" in pet.category:
            category_name = pet.category["name"].lower()
            if "dog" in category_name:
                return "dog"
            elif "cat" in category_name:
                return "cat"
            elif "bird" in category_name:
                return "bird"
            elif "fish" in category_name:
                return "fish"
            elif "rabbit" in category_name:
                return "rabbit"
            elif "hamster" in category_name:
                return "hamster"

        # Check tags
        if pet.tags:
            for tag in pet.tags:
                if isinstance(tag, dict) and "name" in tag:
                    tag_name = tag["name"].lower()
                    if any(species in tag_name for species in ["dog", "canine", "puppy"]):
                        return "dog"
                    elif any(species in tag_name for species in ["cat", "feline", "kitten"]):
                        return "cat"
                    elif any(species in tag_name for species in ["bird", "avian"]):
                        return "bird"
                    elif any(species in tag_name for species in ["fish", "aquatic"]):
                        return "fish"
                    elif "rabbit" in tag_name:
                        return "rabbit"
                    elif "hamster" in tag_name:
                        return "hamster"

        return "other"

    def _generate_description(self, pet: Pet, species: str) -> str:
        """Generate a user-friendly description for the pet."""
        name = pet.name or "this pet"
        
        # Get availability status
        status_text = "available"
        if pet.status == "pending":
            status_text = "pending adoption"
        elif pet.status == "sold":
            status_text = "already adopted"
        
        # Create personality traits based on tags
        personality_traits = []
        if pet.tags:
            for tag in pet.tags:
                if isinstance(tag, dict) and "name" in tag:
                    tag_name = tag["name"].lower()
                    if tag_name in ["friendly", "playful", "gentle", "energetic", "calm", "loving"]:
                        personality_traits.append(tag_name)
        
        # Build description
        description = f"Meet {name}, a lovely {species}"
        
        if personality_traits:
            if len(personality_traits) == 1:
                description += f" who is {personality_traits[0]}"
            elif len(personality_traits) == 2:
                description += f" who is {personality_traits[0]} and {personality_traits[1]}"
            else:
                description += f" who is {', '.join(personality_traits[:-1])}, and {personality_traits[-1]}"
        
        description += f". This pet is currently {status_text}."
        
        return description

    def _create_additional_attributes(self, pet: Pet, species: str) -> Dict[str, Any]:
        """Create additional user-friendly attributes."""
        attributes = {}
        
        # Add care level based on species
        care_levels = {
            "dog": "Medium - needs daily walks and attention",
            "cat": "Low - independent but needs regular feeding",
            "bird": "Medium - needs daily interaction and cage cleaning",
            "fish": "Low - needs regular feeding and tank maintenance",
            "rabbit": "Medium - needs daily exercise and fresh vegetables",
            "hamster": "Low - needs regular feeding and cage cleaning",
            "other": "Varies - please consult with our staff"
        }
        attributes["care_level"] = care_levels.get(species, care_levels["other"])
        
        # Add photo count
        photo_count = len(pet.photo_urls) if pet.photo_urls else 0
        attributes["photo_count"] = photo_count
        attributes["has_photos"] = photo_count > 0
        
        # Add tag count and summary
        tag_count = len(pet.tags) if pet.tags else 0
        attributes["tag_count"] = tag_count
        
        if pet.tags:
            tag_names = [tag.get("name", "") for tag in pet.tags if isinstance(tag, dict)]
            attributes["tag_summary"] = ", ".join(tag_names[:3])  # Show first 3 tags
        
        # Add adoption readiness score (simple calculation)
        readiness_score = 0
        if pet.status == "available":
            readiness_score += 40
        if photo_count > 0:
            readiness_score += 30
        if tag_count > 0:
            readiness_score += 20
        if pet.name and len(pet.name) > 0:
            readiness_score += 10
        
        attributes["adoption_readiness_score"] = min(readiness_score, 100)
        
        return attributes
