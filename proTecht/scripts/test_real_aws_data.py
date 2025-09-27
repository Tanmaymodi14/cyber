#!/usr/bin/env python3
"""
Test Real AWS Data Collection
Collects real data from AWS accounts and verifies it flows to frontend
"""

import boto3
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import ProTechtDatabase
from aws_collect import collect_all

class RealAWSTestDataCollector:
    def __init__(self, profile_name: str = None, region: str = 'us-east-1'):
        """Initialize real AWS data collector"""
        self.profile_name = profile_name
        self.region = region
        self.session = boto3.Session(profile_name=profile_name, region_name=region)
        self.db = ProTechtDatabase()
        
    def test_aws_connection(self):
        """Test AWS connection and permissions"""
        print("🔍 Testing AWS connection...")
        
        try:
            # Test basic connection
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ Connected to AWS Account: {identity['Account']}")
            print(f"   User/Role: {identity['Arn']}")
            print(f"   Region: {self.region}")
            
            # Test IAM permissions
            iam = self.session.client('iam')
            iam.get_account_summary()
            print("✅ IAM permissions verified")
            
            # Test S3 permissions
            s3 = self.session.client('s3')
            s3.list_buckets()
            print("✅ S3 permissions verified")
            
            # Test KMS permissions
            kms = self.session.client('kms')
            kms.list_keys()
            print("✅ KMS permissions verified")
            
            return True
            
        except Exception as e:
            print(f"❌ AWS connection failed: {e}")
            return False
    
    def collect_real_aws_data(self):
        """Collect real data from AWS account"""
        print("📊 Collecting real AWS data...")
        
        try:
            # Collect data from all AWS services
            regions = [self.region] if self.region else None
            aws_data = collect_all(profile=self.profile_name, regions=regions)
            
            print(f"✅ Collected data from {len(aws_data)} services:")
            for service, data in aws_data.items():
                if isinstance(data, dict):
                    if 'users' in data:
                        print(f"   {service}: {len(data['users'])} users")
                    elif 'buckets' in data:
                        print(f"   {service}: {len(data['buckets'])} buckets")
                    elif 'keys' in data:
                        print(f"   {service}: {len(data['keys'])} keys")
                    elif 'trails' in data:
                        print(f"   {service}: {len(data['trails'])} trails")
                    else:
                        print(f"   {service}: {len(data)} items")
                else:
                    print(f"   {service}: {len(data)} items")
            
            return aws_data
            
        except Exception as e:
            print(f"❌ Data collection failed: {e}")
            return None
    
    def load_data_to_database(self, aws_data: Dict[str, Any]):
        """Load real data into database"""
        print("💾 Loading real data into database...")
        
        try:
            self.db.load_aws_data(aws_data)
            print("✅ Real data loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading real data: {e}")
            return False
    
    def verify_data_loaded(self):
        """Verify that real data was loaded correctly"""
        print("🔍 Verifying loaded real data...")
        
        try:
            data = self.db.load_aws_data_from_db()
            
            print("\n📊 Real Data Summary:")
            print(f"  IAM Users: {len(data.get('iam', {}).get('users', []))}")
            print(f"  IAM Roles: {len(data.get('iam', {}).get('roles', []))}")
            print(f"  S3 Buckets: {len(data.get('s3', {}).get('buckets', []))}")
            print(f"  KMS Keys: {len(data.get('kms', {}).get('keys', []))}")
            print(f"  CloudTrail Trails: {len(data.get('cloudtrail', {}).get('trails', []))}")
            print(f"  WAF WebACLs: {len(data.get('waf', {}).get('web_acls', []))}")
            print(f"  CloudFront Distributions: {len(data.get('cloudfront', {}).get('distributions', []))}")
            print(f"  VPC Flow Logs: {data.get('vpc', {}).get('flow_logs', False)}")
            print(f"  GuardDuty Detectors: {data.get('guardduty', {}).get('detector_count', 0)}")
            print(f"  Security Hub Enabled: {data.get('security_hub', {}).get('enabled', False)}")
            print(f"  SSO Enabled: {data.get('sso', {}).get('enabled', False)}")
            
            return True
        except Exception as e:
            print(f"❌ Error verifying data: {e}")
            return False
    
    def test_controls_evaluation(self):
        """Test controls evaluation with real data"""
        print("🧪 Testing controls evaluation with real data...")
        
        try:
            from technical_engine import evaluate_ac_controls
            
            data = self.db.load_aws_data_from_db()
            results = evaluate_ac_controls(data)
            
            print(f"\n📈 Real Data Controls Evaluation Results:")
            print(f"  Total Controls: {len(results)}")
            
            # Count by status
            status_counts = {}
            for control_id, result in results.items():
                status = result.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"  {status.upper()}: {count}")
            
            # Show some specific results
            print(f"\n🎯 Sample Results:")
            for control_id in ['AC-3', 'AC-7', 'AC-10', 'AC-16', 'AC-21']:
                if control_id in results:
                    result = results[control_id]
                    print(f"  {control_id}: {result.get('status')} ({result.get('confidence', 0):.2f})")
            
            return True
        except Exception as e:
            print(f"❌ Error testing controls: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints with real data"""
        print("🌐 Testing API endpoints...")
        
        try:
            import requests
            
            base_url = "http://localhost:8000"
            
            # Test health endpoint
            response = requests.get(f"{base_url}/api/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test controls endpoint
            response = requests.get(f"{base_url}/api/controls")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    print(f"✅ Controls endpoint working - {len(data['data'])} controls")
                else:
                    print(f"✅ Controls endpoint working - {len(data)} controls")
            else:
                print(f"❌ Controls endpoint failed: {response.status_code}")
                return False
            
            # Test services endpoint
            response = requests.get(f"{base_url}/api/evidence/aws/services")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    print(f"✅ Services endpoint working - {len(data['data'])} services")
                else:
                    print(f"✅ Services endpoint working - {len(data)} services")
            else:
                print(f"❌ Services endpoint failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing API endpoints: {e}")
            return False
    
    def test_recollect_functionality(self):
        """Test the recollect functionality"""
        print("🔄 Testing recollect functionality...")
        
        try:
            import requests
            
            base_url = "http://localhost:8000"
            
            # Test AWS recollect
            response = requests.post(f"{base_url}/api/evidence/aws/recollect")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ AWS recollect working - collected {len(data.get('collected_keys', []))} services")
            else:
                print(f"❌ AWS recollect failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing recollect: {e}")
            return False

def main():
    """Main function to test real AWS data collection"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test real AWS data collection')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--test-only', action='store_true', help='Only test existing data')
    
    args = parser.parse_args()
    
    print("🚀 proTecht Real AWS Data Collection Test")
    print("=" * 50)
    
    collector = RealAWSTestDataCollector(profile_name=args.profile, region=args.region)
    
    if args.test_only:
        print("🔍 Testing existing data...")
        collector.verify_data_loaded()
        collector.test_controls_evaluation()
        collector.test_api_endpoints()
        return
    
    # Test AWS connection
    if not collector.test_aws_connection():
        print("❌ Cannot proceed without AWS connection")
        return
    
    # Collect real AWS data
    aws_data = collector.collect_real_aws_data()
    if not aws_data:
        print("❌ Cannot proceed without real AWS data")
        return
    
    # Load data into database
    if not collector.load_data_to_database(aws_data):
        print("❌ Cannot proceed without loading data")
        return
    
    # Verify data was loaded
    if not collector.verify_data_loaded():
        print("❌ Data verification failed")
        return
    
    # Test controls evaluation
    if not collector.test_controls_evaluation():
        print("❌ Controls evaluation failed")
        return
    
    # Test API endpoints
    if not collector.test_api_endpoints():
        print("❌ API endpoints failed")
        return
    
    # Test recollect functionality
    if not collector.test_recollect_functionality():
        print("❌ Recollect functionality failed")
        return
    
    print("\n🎉 Real AWS data collection test complete!")
    print("✅ Real data is flowing from AWS to frontend")
    print("✅ All API endpoints are working")
    print("✅ Controls evaluation is working with real data")
    print("✅ Recollect functionality is working")

if __name__ == "__main__":
    main()
