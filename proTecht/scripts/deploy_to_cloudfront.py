#!/usr/bin/env python3
"""
Deploy proTecht to CloudFront
Deploys the updated system to your existing CloudFront distribution
"""

import boto3
import json
import os
import sys
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        session = boto3.Session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials configured")
        print(f"   Account: {identity['Account']}")
        print(f"   User/Role: {identity['Arn']}")
        return session
    except Exception as e:
        print(f"❌ AWS credentials not configured: {e}")
        print("Please run: aws configure")
        return None

def find_cloudfront_distribution(session: boto3.Session):
    """Find the proTecht CloudFront distribution"""
    try:
        cloudfront = session.client('cloudfront')
        
        # List all distributions
        response = cloudfront.list_distributions()
        distributions = response.get('DistributionList', {}).get('Items', [])
        
        # Look for proTecht distribution
        protecht_dist = None
        for dist in distributions:
            comment = dist.get('Comment', '')
            if 'protecht' in comment.lower() or 'protech' in comment.lower():
                protecht_dist = dist
                break
        
        if protecht_dist:
            print(f"✅ Found proTecht CloudFront distribution:")
            print(f"   ID: {protecht_dist['Id']}")
            print(f"   Domain: {protecht_dist['DomainName']}")
            print(f"   Status: {protecht_dist['Status']}")
            print(f"   Comment: {protecht_dist['Comment']}")
            return protecht_dist
        else:
            print("❌ No proTecht CloudFront distribution found")
            print("Available distributions:")
            for dist in distributions:
                print(f"   {dist['Id']}: {dist['Comment']} ({dist['Status']})")
            return None
            
    except Exception as e:
        print(f"❌ Error finding CloudFront distribution: {e}")
        return None

def build_frontend():
    """Build the frontend for production"""
    print("🏗️ Building frontend for production...")
    
    try:
        # Change to frontend directory
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'Frontend')
        os.chdir(frontend_dir)
        
        # Install dependencies
        print("   Installing dependencies...")
        subprocess.run(['npm', 'install'], check=True)
        
        # Build for production
        print("   Building for production...")
        env = os.environ.copy()
        # Set API base to the CloudFront distribution
        env['VITE_API_BASE'] = 'https://your-cloudfront-domain.cloudfront.net/api'
        
        subprocess.run(['npm', 'run', 'build'], check=True, env=env)
        
        print("✅ Frontend built successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error building frontend: {e}")
        return False

def deploy_to_s3(session: boto3.Session, bucket_name: str):
    """Deploy frontend to S3"""
    print(f"📦 Deploying frontend to S3 bucket: {bucket_name}")
    
    try:
        s3 = session.client('s3')
        
        # Check if bucket exists
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"✅ S3 bucket {bucket_name} exists")
        except:
            print(f"❌ S3 bucket {bucket_name} does not exist")
            return False
        
        # Upload files
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'Frontend', 'dist')
        
        if not os.path.exists(frontend_dir):
            print(f"❌ Frontend build directory not found: {frontend_dir}")
            return False
        
        print("   Uploading files to S3...")
        for root, dirs, files in os.walk(frontend_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, frontend_dir)
                s3_key = relative_path.replace('\\', '/')
                
                s3.upload_file(local_path, bucket_name, s3_key)
                print(f"     Uploaded: {s3_key}")
        
        print("✅ Frontend deployed to S3 successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error deploying to S3: {e}")
        return False

def update_cloudfront_distribution(session: boto3.Session, distribution_id: str):
    """Update CloudFront distribution to point to S3"""
    print(f"🌐 Updating CloudFront distribution: {distribution_id}")
    
    try:
        cloudfront = session.client('cloudfront')
        
        # Get current distribution config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        # Update origin to point to S3
        s3_domain = f"{bucket_name}.s3.amazonaws.com"
        config['Origins']['Items'][0]['DomainName'] = s3_domain
        config['Origins']['Items'][0]['S3OriginConfig'] = {
            'OriginAccessIdentity': ''
        }
        
        # Remove custom origin config
        if 'CustomOriginConfig' in config['Origins']['Items'][0]:
            del config['Origins']['Items'][0]['CustomOriginConfig']
        
        # Update distribution
        update_response = cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print("✅ CloudFront distribution updated")
        print(f"   New domain: {update_response['Distribution']['DomainName']}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating CloudFront: {e}")
        return False

def create_invalidation(session: boto3.Session, distribution_id: str):
    """Create CloudFront invalidation to clear cache"""
    print(f"🔄 Creating CloudFront invalidation...")
    
    try:
        cloudfront = session.client('cloudfront')
        
        # Create invalidation for all files
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
        print(f"✅ CloudFront invalidation created: {invalidation_id}")
        print("   Cache will be cleared in a few minutes")
        return True
        
    except Exception as e:
        print(f"❌ Error creating invalidation: {e}")
        return False

def deploy_backend_to_aws(session: boto3.Session):
    """Deploy backend to AWS (EC2, ECS, or Lambda)"""
    print("🚀 Deploying backend to AWS...")
    
    # This is a placeholder - you would implement your preferred deployment method
    # Options: EC2, ECS, Lambda, Elastic Beanstalk, etc.
    
    print("⚠️ Backend deployment not implemented yet")
    print("   Current system is running locally")
    print("   You can:")
    print("   1. Deploy to EC2 instance")
    print("   2. Deploy to ECS cluster")
    print("   3. Deploy to Lambda functions")
    print("   4. Deploy to Elastic Beanstalk")
    
    return True

def main():
    """Main deployment function"""
    print("🚀 proTecht CloudFront Deployment")
    print("=" * 50)
    
    # Check AWS credentials
    session = check_aws_credentials()
    if not session:
        return False
    
    # Find CloudFront distribution
    distribution = find_cloudfront_distribution(session)
    if not distribution:
        return False
    
    distribution_id = distribution['Id']
    distribution_domain = distribution['DomainName']
    
    # Get S3 bucket name (you'll need to provide this)
    bucket_name = input("Enter S3 bucket name for frontend hosting: ").strip()
    if not bucket_name:
        print("❌ S3 bucket name is required")
        return False
    
    # Build frontend
    if not build_frontend():
        return False
    
    # Deploy frontend to S3
    if not deploy_to_s3(session, bucket_name):
        return False
    
    # Update CloudFront distribution
    if not update_cloudfront_distribution(session, distribution_id):
        return False
    
    # Create invalidation
    if not create_invalidation(session, distribution_id):
        return False
    
    # Deploy backend (placeholder)
    deploy_backend_to_aws(session)
    
    print("\n🎉 Deployment completed!")
    print(f"✅ Frontend deployed to: https://{distribution_domain}")
    print("✅ CloudFront cache invalidation created")
    print("⚠️ Backend still running locally - needs separate deployment")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
