#!/usr/bin/env python3
"""
Debug the _services_from_aws function
"""

import sys
import os
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def debug_services_function():
    """Debug what's being passed to _services_from_aws"""
    
    api_url = "http://protec-Publi-d6VUhLtO713D-2114058116.us-east-1.elb.amazonaws.com"
    
    print("🔍 Getting raw AWS data...")
    
    try:
        response = requests.get(f"{api_url}/api/evidence/aws", timeout=30)
        if response.status_code == 200:
            data = response.json()
            aws_data = data.get('data', {})
            
            print(f"📊 AWS data type: {type(aws_data)}")
            print(f"📊 AWS data keys: {list(aws_data.keys())}")
            
            if 'iam' in aws_data:
                iam_data = aws_data['iam']
                print(f"📊 IAM data type: {type(iam_data)}")
                print(f"📊 IAM data keys: {list(iam_data.keys())}")
                print(f"📊 IAM users type: {type(iam_data.get('users', []))}")
                print(f"📊 IAM users count: {len(iam_data.get('users', []))}")
                
                if iam_data.get('users'):
                    print(f"📊 First user type: {type(iam_data['users'][0])}")
                    print(f"📊 First user: {iam_data['users'][0]}")
            
            # Test the function directly
            print("\n🧪 Testing _services_from_aws function...")
            from api_server import _services_from_aws
            
            try:
                services = _services_from_aws(aws_data)
                print(f"✅ Function succeeded! Generated {len(services)} services")
                
                if services:
                    iam_service = next((s for s in services if s['id'] == 'iam-config'), None)
                    if iam_service:
                        print(f"📊 IAM Service KPIs: {iam_service.get('kpis', {})}")
                    else:
                        print("❌ IAM service not found in results")
                        
            except Exception as e:
                print(f"❌ Function failed: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print(f"❌ API error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_services_function()
