#!/usr/bin/env python3
"""
Store FedRAMP Template in Database
Stores the FedRAMP-SSP-Low-Baseline-Template-v1.1.docx file in the database
similar to how it's stored in OpenAI file search tool
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import ProTechtDatabase

def main():
    """Store the FedRAMP template in the database"""
    
    # Path to the FedRAMP template
    template_path = Path("docs/FedRAMP-SSP-Low-Baseline-Template-v1.1.docx")
    
    if not template_path.exists():
        print(f"❌ Error: FedRAMP template not found at {template_path}")
        print("Please ensure the file exists in the docs/ directory")
        sys.exit(1)
    
    print(f"📄 Found FedRAMP template: {template_path}")
    print(f"📊 File size: {template_path.stat().st_size:,} bytes")
    
    # Initialize database
    print("🗄️  Initializing database...")
    db = ProTechtDatabase()
    
    # Store the template
    print("💾 Storing FedRAMP template in database...")
    success = db.store_fedramp_template(
        template_name="FedRAMP-SSP-Low-Baseline-Template-v1.1",
        template_type="SSP-Low-Baseline",
        file_path=str(template_path)
    )
    
    if success:
        print("✅ FedRAMP template stored successfully!")
        
        # List stored templates
        print("\n📋 Stored FedRAMP templates:")
        templates = db.list_fedramp_templates()
        for template in templates:
            print(f"  - {template['template_name']} ({template['template_type']}) - {template['file_size']:,} bytes")
        
        print(f"\n🎯 Template is now available in the database for policy analysis!")
        print("   The AI policy analysis system can now use this template for validation.")
        
    else:
        print("❌ Failed to store FedRAMP template")
        sys.exit(1)

if __name__ == "__main__":
    main()
