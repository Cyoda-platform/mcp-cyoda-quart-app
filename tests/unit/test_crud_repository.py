"""
Unit tests for CRUD Repository interface and default implementations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.repository.crud_repository import CrudRepository


class MockEntity(dict):
    """Mock entity for testing that supports both attribute and dict access."""

    def __init__(self, technical_id: str, name: str, value: int, key: str = None):
        super().__init__()
        self.technical_id = technical_id
        self.name = name
        self.value = value
        self.key = key or technical_id
        # Also store as dict for compatibility
        self["technical_id"] = technical_id
        self["name"] = name
        self["value"] = value
        self["key"] = self.key

    def get(self, item, default=None):
        """Support dict.get() method."""
        return getattr(self, item, default)


class MockEntityOld:
    """Mock entity for testing."""

    def __init__(self, technical_id: str, name: str, value: int):
        self.technical_id = technical_id
        self.name = name
        self.value = value


class ConcreteCrudRepository(CrudRepository[MockEntity]):
    """Concrete implementation of CrudRepository for testing."""

    def __init__(self):
        self.storage: Dict[str, MockEntity] = {}
        self.find_by_id_called = False
        self.find_all_called = False
        self.find_all_by_criteria_called = False
        self.save_called = False
        self.save_all_called = False
        self.update_called = False
        self.delete_by_id_called = False
        self.count_called = False
        self.exists_by_key_called = False
        self.get_entity_count_called = False
        self.get_entity_changes_metadata_called = False

    async def find_by_id(
        self,
        meta: Dict[str, Any],
        entity_id: Any,
        point_in_time: Optional[datetime] = None,
    ) -> Optional[MockEntity]:
        self.find_by_id_called = True
        return self.storage.get(str(entity_id))

    async def find_all(self, meta: Dict[str, Any]) -> List[MockEntity]:
        self.find_all_called = True
        return list(self.storage.values())

    async def find_all_by_criteria(
        self,
        meta: Dict[str, Any],
        criteria: Any,
        point_in_time: Optional[datetime] = None,
    ) -> List[MockEntity]:
        self.find_all_by_criteria_called = True
        if isinstance(criteria, dict):
            results = []
            for entity in self.storage.values():
                match = True
                for field_name, field_value in criteria.items():
                    # Support both attribute and dict access
                    entity_val = None
                    if hasattr(entity, field_name):
                        entity_val = getattr(entity, field_name)
                    elif isinstance(entity, dict) and field_name in entity:
                        entity_val = entity[field_name]

                    if entity_val != field_value:
                        match = False
                        break
                if match:
                    results.append(entity)
            return results
        return list(self.storage.values())

    async def save(self, meta: Dict[str, Any], entity: MockEntity) -> Any:
        self.save_called = True
        entity_id = entity.technical_id
        self.storage[entity_id] = entity
        return entity_id

    async def save_all(self, meta: Dict[str, Any], entities: List[MockEntity]) -> Any:
        self.save_all_called = True
        for entity in entities:
            self.storage[entity.technical_id] = entity
        return "batch_id"

    async def update(
        self, meta: Dict[str, Any], entity_id: Any, entity: Optional[MockEntity] = None
    ) -> Any:
        self.update_called = True
        if entity:
            self.storage[str(entity_id)] = entity
        return entity_id

    async def delete_by_id(self, meta: Dict[str, Any], entity_id: Any) -> None:
        self.delete_by_id_called = True
        if str(entity_id) in self.storage:
            del self.storage[str(entity_id)]

    async def count(self, meta: Dict[str, Any]) -> int:
        self.count_called = True
        return len(self.storage)

    async def exists_by_key(self, meta: Dict[str, Any], key: Any) -> bool:
        self.exists_by_key_called = True
        return str(key) in self.storage

    async def get_entity_count(
        self, meta: Dict[str, Any], point_in_time: Optional[datetime] = None
    ) -> int:
        self.get_entity_count_called = True
        return len(self.storage)

    async def get_entity_changes_metadata(
        self, entity_id: Any, point_in_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        self.get_entity_changes_metadata_called = True
        return [{"entity_id": str(entity_id), "change_type": "created"}]


class TestCrudRepository:
    """Test suite for CrudRepository interface and default implementations."""

    @pytest.fixture
    def repository(self):
        """Create a concrete repository instance for testing."""
        return ConcreteCrudRepository()

    @pytest.fixture
    def meta(self):
        """Create metadata for repository operations."""
        return {
            "token": "test-token",
            "entity_model": "MockEntity",
            "entity_version": "1",
        }

    @pytest.fixture
    def sample_entity(self):
        """Create a sample entity for testing."""
        return MockEntity(technical_id="test-id-1", name="Test Entity", value=42)

    @pytest.mark.asyncio
    async def test_find_by_id_found(self, repository, meta, sample_entity):
        """Test finding entity by ID when it exists."""
        repository.storage["test-id-1"] = sample_entity

        result = await repository.find_by_id(meta, "test-id-1")

        assert result is not None
        assert result.technical_id == "test-id-1"
        assert result.name == "Test Entity"
        assert repository.find_by_id_called

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository, meta):
        """Test finding entity by ID when it doesn't exist."""
        result = await repository.find_by_id(meta, "non-existent-id")

        assert result is None
        assert repository.find_by_id_called

    @pytest.mark.asyncio
    async def test_find_all_empty(self, repository, meta):
        """Test finding all entities when repository is empty."""
        result = await repository.find_all(meta)

        assert result == []
        assert repository.find_all_called

    @pytest.mark.asyncio
    async def test_find_all_with_entities(self, repository, meta):
        """Test finding all entities when repository has data."""
        entity1 = MockEntity("id-1", "Entity 1", 10)
        entity2 = MockEntity("id-2", "Entity 2", 20)
        repository.storage = {"id-1": entity1, "id-2": entity2}

        result = await repository.find_all(meta)

        assert len(result) == 2
        assert repository.find_all_called

    @pytest.mark.asyncio
    async def test_find_all_by_criteria_matching(self, repository, meta):
        """Test finding entities by criteria with matches."""
        entity1 = MockEntity("id-1", "Test", 10)
        entity2 = MockEntity("id-2", "Test", 20)
        entity3 = MockEntity("id-3", "Other", 30)
        repository.storage = {"id-1": entity1, "id-2": entity2, "id-3": entity3}

        result = await repository.find_all_by_criteria(meta, {"name": "Test"})

        assert len(result) == 2
        assert all(e.name == "Test" for e in result)
        assert repository.find_all_by_criteria_called

    @pytest.mark.asyncio
    async def test_find_all_by_criteria_no_matches(self, repository, meta):
        """Test finding entities by criteria with no matches."""
        entity1 = MockEntity("id-1", "Test", 10)
        repository.storage = {"id-1": entity1}

        result = await repository.find_all_by_criteria(meta, {"name": "NonExistent"})

        assert len(result) == 0
        assert repository.find_all_by_criteria_called

    @pytest.mark.asyncio
    async def test_save_entity(self, repository, meta, sample_entity):
        """Test saving a new entity."""
        result = await repository.save(meta, sample_entity)

        assert result == "test-id-1"
        assert "test-id-1" in repository.storage
        assert repository.save_called

    @pytest.mark.asyncio
    async def test_save_all_entities(self, repository, meta):
        """Test saving multiple entities."""
        entities = [
            MockEntity("id-1", "Entity 1", 10),
            MockEntity("id-2", "Entity 2", 20),
        ]

        result = await repository.save_all(meta, entities)

        assert result == "batch_id"
        assert len(repository.storage) == 2
        assert repository.save_all_called

    @pytest.mark.asyncio
    async def test_update_entity(self, repository, meta):
        """Test updating an existing entity."""
        original = MockEntity("id-1", "Original", 10)
        repository.storage["id-1"] = original

        updated = MockEntity("id-1", "Updated", 20)
        result = await repository.update(meta, "id-1", updated)

        assert result == "id-1"
        assert repository.storage["id-1"].name == "Updated"
        assert repository.update_called

    @pytest.mark.asyncio
    async def test_delete_by_id_existing(self, repository, meta, sample_entity):
        """Test deleting an existing entity."""
        repository.storage["test-id-1"] = sample_entity

        await repository.delete_by_id(meta, "test-id-1")

        assert "test-id-1" not in repository.storage
        assert repository.delete_by_id_called

    @pytest.mark.asyncio
    async def test_delete_by_id_non_existing(self, repository, meta):
        """Test deleting a non-existing entity."""
        await repository.delete_by_id(meta, "non-existent")

        assert repository.delete_by_id_called

    @pytest.mark.asyncio
    async def test_count_entities(self, repository, meta):
        """Test counting entities."""
        repository.storage = {
            "id-1": MockEntity("id-1", "Entity 1", 10),
            "id-2": MockEntity("id-2", "Entity 2", 20),
        }

        result = await repository.count(meta)

        assert result == 2
        assert repository.count_called

    @pytest.mark.asyncio
    async def test_exists_by_key_true(self, repository, meta):
        """Test checking if entity exists by key when it does."""
        repository.storage["test-key"] = MockEntity("test-key", "Test", 10)

        result = await repository.exists_by_key(meta, "test-key")

        assert result is True
        assert repository.exists_by_key_called

    @pytest.mark.asyncio
    async def test_exists_by_key_false(self, repository, meta):
        """Test checking if entity exists by key when it doesn't."""
        result = await repository.exists_by_key(meta, "non-existent-key")

        assert result is False
        assert repository.exists_by_key_called

    @pytest.mark.asyncio
    async def test_get_entity_count(self, repository, meta):
        """Test getting entity count."""
        repository.storage = {
            "id-1": MockEntity("id-1", "Entity 1", 10),
            "id-2": MockEntity("id-2", "Entity 2", 20),
            "id-3": MockEntity("id-3", "Entity 3", 30),
        }

        result = await repository.get_entity_count(meta)

        assert result == 3
        assert repository.get_entity_count_called

    @pytest.mark.asyncio
    async def test_get_entity_count_with_point_in_time(self, repository, meta):
        """Test getting entity count at a specific point in time."""
        repository.storage = {"id-1": MockEntity("id-1", "Entity 1", 10)}
        point_in_time = datetime(2024, 1, 1, 12, 0, 0)

        result = await repository.get_entity_count(meta, point_in_time)

        assert result == 1
        assert repository.get_entity_count_called

    @pytest.mark.asyncio
    async def test_get_entity_changes_metadata(self, repository, meta):
        """Test getting entity change history metadata."""
        result = await repository.get_entity_changes_metadata("test-id-1")

        assert len(result) == 1
        assert result[0]["entity_id"] == "test-id-1"
        assert repository.get_entity_changes_metadata_called

    @pytest.mark.asyncio
    async def test_find_by_key_found(self, repository, meta):
        """Test finding entity by key when it exists."""
        entity = MockEntity("id-1", "Test", 10)
        repository.storage = {"id-1": entity}

        result = await repository.find_by_key(meta, "id-1")

        assert result is not None
        assert result.technical_id == "id-1"

    @pytest.mark.asyncio
    async def test_find_by_key_not_found(self, repository, meta):
        """Test finding entity by key when it doesn't exist."""
        result = await repository.find_by_key(meta, "non-existent")

        assert result is None

    @pytest.mark.asyncio
    async def test_find_all_by_key(self, repository, meta):
        """Test finding entities by multiple keys."""
        entity1 = MockEntity("id-1", "Entity 1", 10)
        entity2 = MockEntity("id-2", "Entity 2", 20)
        entity3 = MockEntity("id-3", "Entity 3", 30)
        repository.storage = {"id-1": entity1, "id-2": entity2, "id-3": entity3}

        result = await repository.find_all_by_key(
            meta, ["id-1", "id-3", "non-existent"]
        )

        assert len(result) == 2
        assert any(e.technical_id == "id-1" for e in result)
        assert any(e.technical_id == "id-3" for e in result)

    @pytest.mark.asyncio
    async def test_delete_all(self, repository, meta):
        """Test deleting all entities."""
        repository.storage = {
            "id-1": MockEntity("id-1", "Entity 1", 10),
            "id-2": MockEntity("id-2", "Entity 2", 20),
        }

        await repository.delete_all(meta)

        assert len(repository.storage) == 0

    @pytest.mark.asyncio
    async def test_delete_all_entities(self, repository, meta):
        """Test deleting specific entities."""
        entity1 = MockEntity("id-1", "Entity 1", 10)
        entity2 = MockEntity("id-2", "Entity 2", 20)
        entity3 = MockEntity("id-3", "Entity 3", 30)
        repository.storage = {"id-1": entity1, "id-2": entity2, "id-3": entity3}

        await repository.delete_all_entities(meta, [entity1, entity2])

        assert len(repository.storage) == 1
        assert "id-3" in repository.storage

    @pytest.mark.asyncio
    async def test_delete_all_by_key(self, repository, meta):
        """Test deleting entities by multiple keys."""
        repository.storage = {
            "id-1": MockEntity("id-1", "Entity 1", 10),
            "id-2": MockEntity("id-2", "Entity 2", 20),
            "id-3": MockEntity("id-3", "Entity 3", 30),
        }

        await repository.delete_all_by_key(meta, ["id-1", "id-3"])

        assert len(repository.storage) == 1
        assert "id-2" in repository.storage

    @pytest.mark.asyncio
    async def test_delete_by_key(self, repository, meta):
        """Test deleting entity by key."""
        repository.storage = {"test-key": MockEntity("test-key", "Test", 10)}

        await repository.delete_by_key(meta, "test-key")

        assert "test-key" not in repository.storage

    @pytest.mark.asyncio
    async def test_update_all(self, repository, meta):
        """Test updating multiple entities."""
        entity1 = MockEntity("id-1", "Original 1", 10)
        entity2 = MockEntity("id-2", "Original 2", 20)
        repository.storage = {"id-1": entity1, "id-2": entity2}

        updated1 = MockEntity("id-1", "Updated 1", 15)
        updated2 = MockEntity("id-2", "Updated 2", 25)

        result = await repository.update_all(meta, [updated1, updated2])

        assert len(result) == 2
        assert repository.storage["id-1"].name == "Updated 1"
        assert repository.storage["id-2"].name == "Updated 2"

    @pytest.mark.asyncio
    async def test_get_meta(self, repository):
        """Test getting metadata for repository operations."""
        result = await repository.get_meta("test-token", "TestEntity", "1.0")

        assert result["token"] == "test-token"
        assert result["entity_model"] == "TestEntity"
        assert result["entity_version"] == "1.0"

    @pytest.mark.asyncio
    async def test_delete_all_entities_with_dict_entities(self, repository, meta):
        """Test deleting entities when entities are dictionaries."""
        # Add entities to storage
        repository.storage = {
            "id-1": MockEntity("id-1", "Entity 1", 10),
            "id-2": MockEntity("id-2", "Entity 2", 20),
        }

        # Create dict-like entities
        dict_entities = [
            {"technical_id": "id-1"},
            {"technical_id": "id-2"},
        ]

        await repository.delete_all_entities(meta, dict_entities)

        # Both should be deleted
        assert len(repository.storage) == 0

    @pytest.mark.asyncio
    async def test_update_all_with_missing_technical_id(self, repository, meta):
        """Test updating entities when some don't have technical_id."""
        entity1 = MockEntity("id-1", "Entity 1", 10)
        repository.storage = {"id-1": entity1}

        # Create entity without technical_id attribute
        class EntityWithoutId:
            pass

        entity_without_id = EntityWithoutId()

        result = await repository.update_all(meta, [entity_without_id])

        # Should return empty list since entity has no technical_id
        assert len(result) == 0
