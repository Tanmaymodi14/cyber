#!/usr/bin/env python3
"""
Final CloudFront Update
Updates CloudFront to use the working local API server
"""

import boto3
import time
import requests

def get_public_ip():
    """Get the public IP of this machine"""
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text.strip()
    except:
        return "24.178.40.15"  # Fallback IP

def update_cloudfront_origin(session: boto3.Session, distribution_id: str, api_url: str):
    """Update CloudFront to point to the local API"""
    print(f"🌐 Updating CloudFront origin to: {api_url}")
    
    try:
        cloudfront = session.client('cloudfront')
        
        # Get current distribution config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        # Update origin
        origins = config.get('Origins', {}).get('Items', [])
        for origin in origins:
            if 'api' in origin.get('Id', '').lower():
                origin['DomainName'] = api_url.replace('https://', '').replace('http://', '')
                origin['CustomOriginConfig'] = {
                    'HTTPPort': 8000,
                    'HTTPSPort': 443,
                    'OriginProtocolPolicy': 'http-only',
                    'OriginSslProtocols': {
                        'Quantity': 1,
                        'Items': ['TLSv1.2']
                    },
                    'OriginReadTimeout': 30,
                    'OriginKeepaliveTimeout': 5
                }
                print(f"   Updated origin: {origin['Id']} -> {origin['DomainName']}")
                break
        
        # Update distribution
        update_response = cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print("✅ CloudFront origin updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating CloudFront origin: {e}")
        return False

def create_cache_invalidation(session: boto3.Session, distribution_id: str):
    """Create CloudFront cache invalidation"""
    print("🔄 Creating cache invalidation...")
    
    try:
        cloudfront = session.client('cloudfront')
        
        response = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': f"local-api-update-{int(time.time())}"
            }
        )
        
        invalidation_id = response['Invalidation']['Id']
        print(f"✅ Cache invalidation created: {invalidation_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating invalidation: {e}")
        return False

def test_local_api(api_url: str):
    """Test the local API endpoints"""
    print(f"🧪 Testing local API at {api_url}...")
    
    endpoints = [
        "/api/health",
        "/api/controls",
        "/api/evidence/aws/services",
        "/api/policies"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{api_url}{endpoint}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: OK")
            else:
                print(f"   ❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
    
    # Test reanalyze endpoint
    try:
        url = f"{api_url}/api/policies/test-policy/reanalyze"
        response = requests.post(url, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ /api/policies/test-policy/reanalyze: OK")
        else:
            print(f"   ❌ /api/policies/test-policy/reanalyze: {response.status_code}")
    except Exception as e:
        print(f"   ❌ /api/policies/test-policy/reanalyze: {e}")

def main():
    """Main function"""
    print("🚀 Final CloudFront Update")
    print("=" * 40)
    
    try:
        session = boto3.Session(profile_name='tanmay_modi')
        
        # Get public IP
        public_ip = get_public_ip()
        api_url = f"http://{public_ip}:8000"
        
        print(f"📍 Using public IP: {public_ip}")
        print(f"🔗 API URL: {api_url}")
        
        # Test local API first
        test_local_api(api_url)
        
        # Update CloudFront
        distribution_id = 'E2NKZPFHR389VM'
        if not update_cloudfront_origin(session, distribution_id, api_url):
            return False
        
        # Create cache invalidation
        if not create_cache_invalidation(session, distribution_id):
            return False
        
        print(f"\n🎉 CloudFront update completed!")
        print(f"✅ CloudFront updated to use: {api_url}")
        print(f"✅ Cache invalidation created")
        
        print(f"\n📝 Your system is now fully deployed:")
        print(f"   Frontend: https://d2d8obg4v8t84w.cloudfront.net")
        print(f"   Backend API: {api_url}/api")
        print(f"   Local API Server: http://localhost:8000")
        
        print(f"\n⏰ Next steps:")
        print(f"   1. Wait 5-10 minutes for CloudFront cache to clear")
        print(f"   2. Test the reanalyze buttons on CloudFront")
        print(f"   3. Verify all functionality works")
        
        print(f"\n🔧 Keep your local API server running:")
        print(f"   The CloudFront frontend will call your local API at {api_url}")
        print(f"   Make sure your local API server stays running")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
