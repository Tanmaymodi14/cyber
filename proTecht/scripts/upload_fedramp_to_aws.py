#!/usr/bin/env python3
"""
Upload FedRAMP template to deployed AWS database
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import ProTechtDatabase

def upload_fedramp_template():
    """Upload FedRAMP template to AWS database"""
    
    # Initialize local database
    db = ProTechtDatabase()
    
    # Get the template from local database
    template_data = db.get_fedramp_template("FedRAMP-SSP-Low-Baseline-Template-v1.1")
    if not template_data:
        print("❌ FedRAMP template not found in local database. Run store_fedramp_template.py first.")
        return False
    
    print(f"📄 Found FedRAMP template: {template_data['template_name']}")
    print(f"📊 File size: {template_data['file_size']:,} bytes")
    
    # Create temporary file for upload
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        tmp_file.write(template_data['file_content'])
        tmp_file_path = tmp_file.name
    
    try:
        # Upload to AWS API using file upload
        api_url = "http://protec-Publi-d6VUhLtO713D-2114058116.us-east-1.elb.amazonaws.com/api/fedramp-template/upload"
        
        print("🚀 Uploading FedRAMP template to AWS database...")
        with open(tmp_file_path, 'rb') as f:
            files = {'file': (template_data['template_name'] + '.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {'template_name': template_data['template_name']}
            response = requests.post(api_url, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ FedRAMP template uploaded successfully!")
            print(f"📋 Template ID: {result.get('template_id', 'N/A')}")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

if __name__ == "__main__":
    success = upload_fedramp_template()
    if success:
        print("\n🎯 FedRAMP template is now available in AWS database for policy analysis!")
    else:
        print("\n❌ Failed to upload FedRAMP template to AWS database")
        sys.exit(1)
