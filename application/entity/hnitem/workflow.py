"""
HN Item workflow processors for managing Hacker News items lifecycle.
"""
import logging
from datetime import datetime
from typing import Dict, Any, List
import requests
import asyncio

logger = logging.getLogger(__name__)


async def validate_item_processor(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates HN item data structure and required fields.
    
    Args:
        entity: HN item entity data
        
    Returns:
        Updated entity with validation status
        
    Raises:
        ValueError: If validation fails
    """
    logger.info(f"Validating HN item: {entity.get('id')}")
    
    # Validate required fields
    if not entity.get('id') or not isinstance(entity.get('id'), int):
        raise ValueError("Invalid or missing ID - must be integer")
    
    item_type = entity.get('type')
    if item_type not in ['story', 'comment', 'job', 'poll', 'pollopt']:
        raise ValueError(f"Invalid type: {item_type}")
    
    # Type-specific validations
    if item_type == 'story' and not entity.get('title'):
        raise ValueError("Story items require a title")
    
    if item_type == 'comment' and not entity.get('text'):
        raise ValueError("Comment items require text content")
    
    if item_type == 'pollopt' and not entity.get('poll'):
        raise ValueError("Poll option items require a poll reference")
    
    # Validate time field if present
    if entity.get('time') and not isinstance(entity.get('time'), int):
        raise ValueError("Time field must be Unix timestamp integer")
    
    # Validate kids array if present
    if entity.get('kids') and not isinstance(entity.get('kids'), list):
        raise ValueError("Kids field must be an array")
    
    # Set validation status
    entity['validation_status'] = 'valid'
    logger.info(f"HN item {entity['id']} validated successfully")
    
    return entity


async def process_item_processor(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes validated HN item for storage and relationship management.
    
    Args:
        entity: Validated HN item entity
        
    Returns:
        Processed entity ready for storage
    """
    logger.info(f"Processing HN item: {entity.get('id')}")
    
    # Set processing timestamp
    entity['processed_time'] = int(datetime.now().timestamp())
    
    # Calculate children count from kids array
    if entity.get('kids'):
        entity['children_count'] = len(entity['kids'])
    else:
        entity['children_count'] = 0
    
    # Handle parent-child relationships
    if entity.get('parent'):
        logger.info(f"Item {entity['id']} has parent: {entity['parent']}")
        # Note: In a real implementation, you would update the parent's children count
        # This would require access to the entity service to fetch and update the parent
    
    # Handle poll relationships
    if entity.get('poll'):
        logger.info(f"Poll option {entity['id']} belongs to poll: {entity['poll']}")
    
    if entity.get('parts'):
        logger.info(f"Poll {entity['id']} has {len(entity['parts'])} options")
    
    # Set processing status
    entity['processing_status'] = 'complete'
    logger.info(f"HN item {entity['id']} processed successfully")
    
    return entity


async def firebase_sync_processor(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetches HN item data from Firebase HN API.
    
    Args:
        entity: Entity containing sync parameters
        
    Returns:
        Entity with Firebase data populated
    """
    logger.info("Starting Firebase HN API sync")
    
    base_url = "https://hacker-news.firebaseio.com/v0"
    
    try:
        # Get item ID from entity or fetch latest
        item_id = entity.get('firebase_item_id')
        
        if not item_id:
            # Fetch max item ID
            response = requests.get(f"{base_url}/maxitem.json", timeout=10)
            response.raise_for_status()
            item_id = response.json()
            logger.info(f"Fetched max item ID: {item_id}")
        
        # Fetch specific item
        response = requests.get(f"{base_url}/item/{item_id}.json", timeout=10)
        response.raise_for_status()
        firebase_data = response.json()
        
        if firebase_data:
            # Map Firebase data to entity
            entity.update({
                'id': firebase_data.get('id'),
                'type': firebase_data.get('type'),
                'by': firebase_data.get('by'),
                'time': firebase_data.get('time'),
                'text': firebase_data.get('text'),
                'url': firebase_data.get('url'),
                'score': firebase_data.get('score'),
                'title': firebase_data.get('title'),
                'kids': firebase_data.get('kids', []),
                'parent': firebase_data.get('parent'),
                'poll': firebase_data.get('poll'),
                'parts': firebase_data.get('parts', []),
                'descendants': firebase_data.get('descendants'),
                'deleted': firebase_data.get('deleted', False),
                'dead': firebase_data.get('dead', False)
            })
            
            logger.info(f"Successfully synced item {item_id} from Firebase")
        else:
            logger.warning(f"No data found for item {item_id}")
            
    except requests.RequestException as e:
        logger.error(f"Firebase API request failed: {e}")
        raise ValueError(f"Failed to fetch from Firebase API: {e}")
    
    return entity
