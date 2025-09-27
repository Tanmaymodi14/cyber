#!/usr/bin/env python3
"""
Quick CloudFront Deployment
Deploys the current working system to your CloudFront distribution
"""

import boto3
import json
import os
import sys
import subprocess
import time
from datetime import datetime

def get_cloudfront_info():
    """Get CloudFront distribution information"""
    print("🔍 Finding your CloudFront distribution...")
    
    try:
        # Try different AWS profiles
        profiles = ['default', 'tanmay_modi', 'protecht']
        
        for profile in profiles:
            try:
                session = boto3.Session(profile_name=profile)
                cloudfront = session.client('cloudfront')
                
                # List distributions
                response = cloudfront.list_distributions()
                distributions = response.get('DistributionList', {}).get('Items', [])
                
                print(f"   Checking profile: {profile}")
                
                for dist in distributions:
                    comment = dist.get('Comment', '').lower()
                    if 'protecht' in comment or 'protech' in comment:
                        print(f"✅ Found proTecht distribution in profile '{profile}':")
                        print(f"   ID: {dist['Id']}")
                        print(f"   Domain: {dist['DomainName']}")
                        print(f"   Status: {dist['Status']}")
                        return session, dist
                
            except Exception as e:
                print(f"   Profile {profile}: {e}")
                continue
        
        print("❌ No proTecht CloudFront distribution found")
        print("Available distributions:")
        for profile in profiles:
            try:
                session = boto3.Session(profile_name=profile)
                cloudfront = session.client('cloudfront')
                response = cloudfront.list_distributions()
                distributions = response.get('DistributionList', {}).get('Items', [])
                
                for dist in distributions:
                    print(f"   {profile}: {dist['Id']} - {dist['Comment']} ({dist['Status']})")
            except:
                continue
        
        return None, None
        
    except Exception as e:
        print(f"❌ Error finding CloudFront distribution: {e}")
        return None, None

def build_and_deploy_frontend(session, distribution):
    """Build and deploy frontend to S3"""
    print("🏗️ Building and deploying frontend...")
    
    try:
        # Get S3 bucket from CloudFront origin
        distribution_id = distribution['Id']
        cloudfront = session.client('cloudfront')
        
        # Get distribution config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        
        # Find S3 origin
        origins = config.get('Origins', {}).get('Items', [])
        s3_origin = None
        for origin in origins:
            if 's3' in origin.get('DomainName', '').lower():
                s3_origin = origin
                break
        
        if not s3_origin:
            print("❌ No S3 origin found in CloudFront distribution")
            return False
        
        bucket_name = s3_origin['DomainName'].replace('.s3.amazonaws.com', '')
        print(f"   S3 Bucket: {bucket_name}")
        
        # Build frontend
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'Frontend')
        os.chdir(frontend_dir)
        
        print("   Building frontend...")
        subprocess.run(['npm', 'install'], check=True)
        
        # Set API base to CloudFront domain
        env = os.environ.copy()
        env['VITE_API_BASE'] = f"https://{distribution['DomainName']}/api"
        
        subprocess.run(['npm', 'run', 'build'], check=True, env=env)
        
        # Deploy to S3
        print("   Deploying to S3...")
        s3 = session.client('s3')
        
        dist_dir = os.path.join(frontend_dir, 'dist')
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, dist_dir)
                s3_key = relative_path.replace('\\', '/')
                
                s3.upload_file(local_path, bucket_name, s3_key)
                print(f"     Uploaded: {s3_key}")
        
        print("✅ Frontend deployed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error deploying frontend: {e}")
        return False

def create_cache_invalidation(session, distribution_id):
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
                'CallerReference': f"protecht-update-{int(time.time())}"
            }
        )
        
        invalidation_id = response['Invalidation']['Id']
        print(f"✅ Cache invalidation created: {invalidation_id}")
        print("   Cache will be cleared in 5-10 minutes")
        return True
        
    except Exception as e:
        print(f"❌ Error creating invalidation: {e}")
        return False

def update_api_origin(session, distribution_id, new_api_url):
    """Update CloudFront to point to new API"""
    print("🔧 Updating API origin...")
    
    try:
        cloudfront = session.client('cloudfront')
        
        # Get current config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        # Update API origin
        origins = config.get('Origins', {}).get('Items', [])
        for origin in origins:
            if 'api' in origin.get('Id', '').lower():
                origin['DomainName'] = new_api_url
                print(f"   Updated API origin to: {new_api_url}")
                break
        
        # Update distribution
        update_response = cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print("✅ API origin updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating API origin: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Quick CloudFront Deployment")
    print("=" * 40)
    
    # Find CloudFront distribution
    session, distribution = get_cloudfront_info()
    if not session or not distribution:
        print("\n❌ Cannot proceed without CloudFront distribution")
        print("Please ensure you have a proTecht CloudFront distribution")
        return False
    
    distribution_id = distribution['Id']
    distribution_domain = distribution['DomainName']
    
    print(f"\n📋 Deployment Plan:")
    print(f"   Distribution: {distribution_id}")
    print(f"   Domain: {distribution_domain}")
    print(f"   Status: {distribution['Status']}")
    
    # Build and deploy frontend
    if not build_and_deploy_frontend(session, distribution):
        return False
    
    # Create cache invalidation
    if not create_cache_invalidation(session, distribution_id):
        return False
    
    # Ask about API update
    api_url = input("\nEnter new API URL (or press Enter to skip): ").strip()
    if api_url:
        if not update_api_origin(session, distribution_id, api_url):
            return False
    
    print(f"\n🎉 Deployment completed!")
    print(f"✅ Frontend: https://{distribution_domain}")
    print(f"✅ Cache invalidation created")
    print(f"✅ Updated system is now live!")
    
    print(f"\n📝 Next steps:")
    print(f"   1. Wait 5-10 minutes for cache to clear")
    print(f"   2. Visit: https://{distribution_domain}")
    print(f"   3. Test the reanalyze buttons")
    print(f"   4. Verify all functionality works")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
