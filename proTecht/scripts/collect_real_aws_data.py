#!/usr/bin/env python3
"""
Collect real AWS data for compliance analysis
This script collects actual data from AWS accounts and stores it in the database
"""

import sys
import os
import json
from datetime import datetime, timezone

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import ProTechtDatabase
from aws_collect import collect_all

def collect_real_aws_data(profile=None, regions=None):
    """Collect real AWS data and store in database"""
    
    print("🔍 Collecting real AWS data...")
    print(f"Profile: {profile or 'default'}")
    print(f"Regions: {regions or ['us-east-1']}")
    
    try:
        # Collect real AWS data
        print("\n📊 Collecting AWS infrastructure data...")
        aws_data = collect_all(profile=profile, regions=regions)
        
        print(f"✅ Collected data for {len(aws_data)} services:")
        for service, data in aws_data.items():
            if isinstance(data, dict):
                print(f"  - {service}: {len(data)} items")
            elif isinstance(data, list):
                print(f"  - {service}: {len(data)} items")
            else:
                print(f"  - {service}: {type(data).__name__}")
        
        # Store in database
        print("\n💾 Storing data in database...")
        db = ProTechtDatabase()
        db.load_aws_data(aws_data)
        
        print("✅ Real AWS data collected and stored successfully!")
        
        # Verify the data was stored
        print("\n🔍 Verifying stored data...")
        stored_data = db.load_aws_data_from_db()
        
        print(f"IAM Users: {len(stored_data.get('iam', {}).get('users', []))}")
        print(f"S3 Buckets: {len(stored_data.get('s3', {}).get('buckets', []))}")
        print(f"KMS Keys: {len(stored_data.get('kms', {}).get('keys', []))}")
        print(f"CloudTrail Trails: {len(stored_data.get('cloudtrail', {}).get('trails', []))}")
        print(f"WAF WebACLs: {len(stored_data.get('waf', {}).get('web_acls', []))}")
        print(f"CloudFront Distributions: {len(stored_data.get('cloudfront', {}).get('distributions', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error collecting AWS data: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect real AWS data for compliance analysis')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--regions', help='Comma-separated list of AWS regions', default='us-east-1')
    
    args = parser.parse_args()
    
    regions = [r.strip() for r in args.regions.split(',')] if args.regions else ['us-east-1']
    
    success = collect_real_aws_data(profile=args.profile, regions=regions)
    
    if success:
        print("\n🎉 Real AWS data collection completed successfully!")
        print("The dashboard will now show actual compliance data from your AWS account.")
    else:
        print("\n💥 Real AWS data collection failed!")
        print("Please check your AWS credentials and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
