#!/usr/bin/env python3
"""
Quick script to fix common route issues
"""

import re
import os

def fix_route_file(filepath):
    """Fix common issues in route files"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix get_all -> find_all
    content = re.sub(r'\.get_all\(', '.find_all(', content)
    
    # Fix delete -> delete_by_id
    content = re.sub(r'\.delete\(', '.delete_by_id(', content)
    
    # Fix entity_data -> entity
    content = re.sub(r'entity_data=', 'entity=', content)
    
    # Fix response.data -> response.data.model_dump()
    content = re.sub(r'Pet\(\*\*response\.data\)', 'Pet(**response.data.model_dump())', content)
    content = re.sub(r'Customer\(\*\*response\.data\)', 'Customer(**response.data.model_dump())', content)
    content = re.sub(r'AdoptionApplication\(\*\*response\.data\)', 'AdoptionApplication(**response.data.model_dump())', content)
    content = re.sub(r'PetCareRecord\(\*\*response\.data\)', 'PetCareRecord(**response.data.model_dump())', content)
    content = re.sub(r'Staff\(\*\*response\.data\)', 'Staff(**response.data.model_dump())', content)
    
    # Remove processor_kwargs
    content = re.sub(r',\s*processor_kwargs=[^,)]+', '', content)
    
    # Fix transition parameter in save calls
    content = re.sub(r'transition="[^"]+",\s*\)', ')', content)
    
    with open(filepath, 'w') as f:
        f.write(content)

# Fix all route files
route_files = [
    'application/routes/customers.py',
    'application/routes/adoption_applications.py', 
    'application/routes/pet_care_records.py',
    'application/routes/staff.py'
]

for route_file in route_files:
    if os.path.exists(route_file):
        print(f"Fixing {route_file}")
        fix_route_file(route_file)
        print(f"Fixed {route_file}")

print("All route files fixed!")
