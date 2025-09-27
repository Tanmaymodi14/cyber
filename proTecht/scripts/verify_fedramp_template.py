#!/usr/bin/env python3
"""
Verify FedRAMP Template in Database
Verifies that the FedRAMP template was stored correctly and can be retrieved
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import ProTechtDatabase

def main():
    """Verify the FedRAMP template in the database"""
    
    print("🔍 Verifying FedRAMP template in database...")
    
    # Initialize database
    db = ProTechtDatabase()
    
    # List all stored templates
    print("\n📋 Stored FedRAMP templates:")
    templates = db.list_fedramp_templates()
    
    if not templates:
        print("❌ No FedRAMP templates found in database")
        sys.exit(1)
    
    for template in templates:
        print(f"  - {template['template_name']} ({template['template_type']})")
        print(f"    Size: {template['file_size']:,} bytes")
        print(f"    Uploaded: {template['upload_date']}")
    
    # Retrieve the specific template
    template_name = "FedRAMP-SSP-Low-Baseline-Template-v1.1"
    print(f"\n🔍 Retrieving template: {template_name}")
    
    template_data = db.get_fedramp_template(template_name)
    
    if template_data:
        print("✅ Template retrieved successfully!")
        print(f"  - Name: {template_data['template_name']}")
        print(f"  - Type: {template_data['template_type']}")
        print(f"  - Size: {template_data['file_size']:,} bytes")
        print(f"  - Upload Date: {template_data['upload_date']}")
        print(f"  - Content Available: {'Yes' if template_data['file_content'] else 'No'}")
        
        # Verify content size matches
        if len(template_data['file_content']) == template_data['file_size']:
            print("✅ Content size verification passed")
        else:
            print("❌ Content size mismatch!")
            
        print(f"\n🎯 Template is ready for use in policy analysis!")
        
    else:
        print(f"❌ Template '{template_name}' not found in database")
        sys.exit(1)

if __name__ == "__main__":
    main()
