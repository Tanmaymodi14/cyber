#!/usr/bin/env python3
"""
Update Frontend to Use Local API
Updates the frontend to use the local working API and redeploys
"""

import boto3
import json
import os
import sys
import subprocess
import time
from datetime import datetime

def get_public_ip():
    """Get the public IP of this machine"""
    try:
        import requests
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        return "localhost"

def build_frontend_with_local_api():
    """Build frontend with local API URL"""
    print("🏗️ Building frontend with local API...")
    
    try:
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'Frontend')
        os.chdir(frontend_dir)
        
        # Get public IP or use localhost
        public_ip = get_public_ip()
        if public_ip == "localhost":
            api_url = "http://localhost:8000"
        else:
            api_url = f"http://{public_ip}:8000"
        
        print(f"   Using API URL: {api_url}")
        
        # Set environment variable
        env = os.environ.copy()
        env['VITE_API_BASE'] = f"{api_url}/api"
        
        print("   Installing dependencies...")
        subprocess.run(['npm', 'install'], check=True)
        
        print("   Building for production...")
        subprocess.run(['npm', 'run', 'build'], check=True, env=env)
        
        print("✅ Frontend built successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error building frontend: {e}")
        return False

def deploy_to_cloudfront():
    """Deploy updated frontend to CloudFront"""
    print("📦 Deploying to CloudFront...")
    
    try:
        session = boto3.Session(profile_name='tanmay_modi')
        s3 = session.client('s3')
        cloudfront = session.client('cloudfront')
        
        # Deploy to S3
        bucket_name = "example-bucket.s3-website-us-east-1.amazonaws.com"
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'Frontend', 'dist')
        
        print("   Uploading files to S3...")
        for root, dirs, files in os.walk(frontend_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, frontend_dir)
                s3_key = relative_path.replace('\\', '/')
                
                s3.upload_file(local_path, bucket_name, s3_key)
                print(f"     Uploaded: {s3_key}")
        
        # Create cache invalidation
        distribution_id = 'E2NKZPFHR389VM'
        response = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': f"local-api-{int(time.time())}"
            }
        )
        
        invalidation_id = response['Invalidation']['Id']
        print(f"✅ Cache invalidation created: {invalidation_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying to CloudFront: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Update Frontend to Use Local API")
    print("=" * 40)
    
    try:
        # Build frontend with local API
        if not build_frontend_with_local_api():
            return False
        
        # Deploy to CloudFront
        if not deploy_to_cloudfront():
            return False
        
        public_ip = get_public_ip()
        api_url = f"http://{public_ip}:8000" if public_ip != "localhost" else "http://localhost:8000"
        
        print(f"\n🎉 Frontend updated successfully!")
        print(f"✅ Frontend deployed to CloudFront")
        print(f"✅ Cache invalidation created")
        print(f"✅ Using local API: {api_url}")
        
        print(f"\n📝 Current status:")
        print(f"   Frontend: https://d2d8obg4v8t84w.cloudfront.net")
        print(f"   Backend API: {api_url}/api")
        print(f"   Note: Make sure the local API server is running")
        
        print(f"\n🧪 Test the deployment:")
        print(f"   1. Visit: https://d2d8obg4v8t84w.cloudfront.net")
        print(f"   2. The reanalyze buttons should work")
        print(f"   3. Check browser console for any errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
