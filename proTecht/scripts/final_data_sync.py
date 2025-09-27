#!/usr/bin/env python3
"""
Final data sync solution - directly sync local AWS data to ECS database
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aws_collect import collect_all
from database import ProTechtDatabase

def sync_all_data():
    """Collect data locally and sync to ECS database"""
    
    print("🔄 Collecting AWS data locally...")
    
    # Collect data locally with your profile
    collected = collect_all(profile='tanmay_modi', regions=['us-east-1', 'us-west-2'])
    
    print(f"✅ Collected data for: {list(collected.keys())}")
    
    # Check IAM data specifically
    if 'iam' in collected:
        iam_data = collected['iam']
        print(f"📊 IAM Users: {len(iam_data.get('users', []))}")
        print(f"📊 IAM Roles: {len(iam_data.get('roles', []))}")
        print(f"📊 Password Policy: {iam_data.get('password_policy', {})}")
    
    # Convert datetime objects to strings for JSON serialization
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_datetime(item) for item in obj]
        else:
            return obj
    
    collected_serializable = convert_datetime(collected)
    
    # Upload to ECS API
    print("🚀 Uploading data to ECS API...")
    
    api_url = "http://protec-Publi-d6VUhLtO713D-2114058116.us-east-1.elb.amazonaws.com"
    
    try:
        # Use the ingest endpoint to upload the data
        response = requests.post(
            f"{api_url}/api/evidence/aws/ingest",
            headers={"Authorization": "Bearer test-token"},
            json=collected_serializable,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Data successfully uploaded to ECS API")
            result = response.json()
            print(f"📊 Response: {result}")
            
            # Wait a moment for data to be processed
            print("⏳ Waiting for data to be processed...")
            import time
            time.sleep(5)
            
            # Test the evidence services endpoint
            print("🧪 Testing evidence services endpoint...")
            test_response = requests.get(f"{api_url}/api/evidence/aws/services", timeout=30)
            
            if test_response.status_code == 200:
                test_data = test_response.json()
                iam_service = next((s for s in test_data.get('data', []) if s['id'] == 'iam-config'), None)
                if iam_service:
                    print(f"📊 IAM Service KPIs: {iam_service.get('kpis', {})}")
                    if iam_service.get('kpis', {}).get('Users', 0) > 0:
                        print("🎉 SUCCESS! Evidence page now shows real IAM data!")
                    else:
                        print("❌ Evidence page still shows zeros")
                else:
                    print("❌ IAM service not found in response")
            else:
                print(f"❌ Test failed: {test_response.status_code}")
                print(test_response.text)
            
        else:
            print(f"❌ Failed to upload data: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error uploading data: {e}")

if __name__ == "__main__":
    sync_all_data()
