#!/usr/bin/env python3
"""
Test IAM collection in ECS environment
"""

import requests
import json

def test_iam_collection():
    """Test IAM collection via API"""
    
    api_url = "http://protec-Publi-d6VUhLtO713D-2114058116.us-east-1.elb.amazonaws.com"
    
    print("🔍 Testing IAM collection...")
    
    # Test the raw evidence endpoint
    try:
        response = requests.get(f"{api_url}/api/evidence/aws", timeout=30)
        if response.status_code == 200:
            data = response.json()
            iam_data = data.get('data', {}).get('iam', {})
            print(f"📊 IAM Users: {len(iam_data.get('users', []))}")
            print(f"📊 IAM Roles: {len(iam_data.get('roles', []))}")
            print(f"📊 Password Policy: {iam_data.get('password_policy', {})}")
            
            if iam_data.get('users'):
                print(f"✅ IAM data found: {iam_data['users'][0]}")
            else:
                print("❌ No IAM users found")
                
        else:
            print(f"❌ API error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_iam_collection()
