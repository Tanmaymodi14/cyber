#!/usr/bin/env python3
"""
Comprehensive AWS Test Environment Setup
Creates realistic AWS resources for testing proTecht compliance dashboard
"""

import boto3
import json
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import ProTechtDatabase

class AWSTestEnvironmentSetup:
    def __init__(self, profile_name: str = None, region: str = 'us-east-1'):
        """Initialize AWS test environment setup"""
        self.profile_name = profile_name
        self.region = region
        self.session = boto3.Session(profile_name=profile_name, region_name=region)
        self.db = ProTechtDatabase()
        
        # Track created resources for cleanup
        self.created_resources = {
            'iam_users': [],
            'iam_roles': [],
            's3_buckets': [],
            'kms_keys': [],
            'cloudtrail_trails': [],
            'waf_web_acls': [],
            'cloudfront_distributions': [],
            'vpc_flow_logs': [],
            'guardduty_detectors': [],
            'security_hub_standards': []
        }
    
    def create_iam_resources(self):
        """Create comprehensive IAM resources"""
        print("🔐 Creating IAM resources...")
        
        iam = self.session.client('iam')
        
        # Create IAM users with different access levels
        users_data = [
            {
                'UserName': 'admin-user',
                'MFA': True,
                'PasswordLastUsed': (datetime.now() - timedelta(days=1)).isoformat(),
                'access_level': 'admin'
            },
            {
                'UserName': 'developer-user',
                'MFA': True,
                'PasswordLastUsed': (datetime.now() - timedelta(hours=2)).isoformat(),
                'access_level': 'developer'
            },
            {
                'UserName': 'readonly-user',
                'MFA': False,
                'PasswordLastUsed': (datetime.now() - timedelta(days=7)).isoformat(),
                'access_level': 'readonly'
            },
            {
                'UserName': 'service-account',
                'MFA': False,
                'PasswordLastUsed': (datetime.now() - timedelta(minutes=30)).isoformat(),
                'access_level': 'service'
            },
            {
                'UserName': 'inactive-user',
                'MFA': False,
                'PasswordLastUsed': (datetime.now() - timedelta(days=90)).isoformat(),
                'access_level': 'inactive'
            },
            {
                'UserName': 'security-analyst',
                'MFA': True,
                'PasswordLastUsed': (datetime.now() - timedelta(hours=6)).isoformat(),
                'access_level': 'security'
            },
            {
                'UserName': 'compliance-officer',
                'MFA': True,
                'PasswordLastUsed': (datetime.now() - timedelta(days=2)).isoformat(),
                'access_level': 'compliance'
            },
            {
                'UserName': 'backup-user',
                'MFA': False,
                'PasswordLastUsed': (datetime.now() - timedelta(days=14)).isoformat(),
                'access_level': 'backup'
            }
        ]
        
        # Create IAM roles with different permission boundaries
        roles_data = [
            {
                'RoleName': 'AdminRole',
                'permissions': 's3:*,iam:*,ec2:*',
                'boundary': None,
                'description': 'Full administrative access'
            },
            {
                'RoleName': 'DeveloperRole',
                'permissions': 's3:GetObject,s3:PutObject,ec2:Describe*',
                'boundary': 'arn:aws:iam::aws:policy/PowerUserAccess',
                'description': 'Developer access with boundaries'
            },
            {
                'RoleName': 'ReadOnlyRole',
                'permissions': 's3:GetObject,iam:List*',
                'boundary': 'arn:aws:iam::aws:policy/ReadOnlyAccess',
                'description': 'Read-only access'
            },
            {
                'RoleName': 'ServiceRole',
                'permissions': 's3:GetObject,s3:PutObject',
                'boundary': 'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess',
                'description': 'Service account role'
            }
        ]
        
        # Create password policy
        password_policy = {
            'MinimumPasswordLength': 14,
            'RequireSymbols': True,
            'RequireNumbers': True,
            'RequireUppercaseCharacters': True,
            'RequireLowercaseCharacters': True,
            'MaxPasswordAge': 90,
            'PasswordReusePrevention': 5
        }
        
        return {
            'users': users_data,
            'roles': roles_data,
            'password_policy': password_policy
        }
    
    def create_s3_resources(self):
        """Create comprehensive S3 resources"""
        print("🪣 Creating S3 resources...")
        
        s3_buckets = [
            {
                'Name': 'protecht-secure-data',
                'Encryption': 'AES256',
                'PublicAccessBlock': True,
                'ObjectLockMode': 'GOVERNANCE',
                'RetentionDays': 2555,  # 7 years
                'KmsKeyId': 'alias/secure-data-key'
            },
            {
                'Name': 'protecht-logs',
                'Encryption': 'aws:kms',
                'PublicAccessBlock': True,
                'ObjectLockMode': 'COMPLIANCE',
                'RetentionDays': 2555,
                'KmsKeyId': 'alias/logs-key'
            },
            {
                'Name': 'protecht-public-assets',
                'Encryption': None,
                'PublicAccessBlock': False,
                'ObjectLockMode': None,
                'RetentionDays': None,
                'KmsKeyId': None
            },
            {
                'Name': 'protecht-backup',
                'Encryption': 'aws:kms',
                'PublicAccessBlock': True,
                'ObjectLockMode': 'GOVERNANCE',
                'RetentionDays': 1095,  # 3 years
                'KmsKeyId': 'alias/backup-key'
            },
            {
                'Name': 'protecht-temp',
                'Encryption': None,
                'PublicAccessBlock': True,
                'ObjectLockMode': None,
                'RetentionDays': None,
                'KmsKeyId': None
            },
            {
                'Name': 'protecht-audit-logs',
                'Encryption': 'aws:kms',
                'PublicAccessBlock': True,
                'ObjectLockMode': 'COMPLIANCE',
                'RetentionDays': 2555,
                'KmsKeyId': 'alias/audit-key'
            },
            {
                'Name': 'protecht-compliance-data',
                'Encryption': 'AES256',
                'PublicAccessBlock': True,
                'ObjectLockMode': 'GOVERNANCE',
                'RetentionDays': 2555,
                'KmsKeyId': 'alias/compliance-key'
            },
            {
                'Name': 'protecht-dev-environment',
                'Encryption': None,
                'PublicAccessBlock': True,
                'ObjectLockMode': None,
                'RetentionDays': 30,
                'KmsKeyId': None
            },
            {
                'Name': 'protecht-staging-data',
                'Encryption': 'AES256',
                'PublicAccessBlock': True,
                'ObjectLockMode': 'GOVERNANCE',
                'RetentionDays': 90,
                'KmsKeyId': 'alias/staging-key'
            },
            {
                'Name': 'protecht-archive',
                'Encryption': 'aws:kms',
                'PublicAccessBlock': True,
                'ObjectLockMode': 'COMPLIANCE',
                'RetentionDays': 2555,
                'KmsKeyId': 'alias/archive-key'
            }
        ]
        
        return s3_buckets
    
    def create_kms_resources(self):
        """Create KMS keys with different configurations"""
        print("🔑 Creating KMS resources...")
        
        kms_keys = [
            {
                'KeyId': 'key-protecht-master',
                'RotationEnabled': True,
                'Alias': 'alias/protecht-master',
                'Description': 'Master encryption key for proTecht'
            },
            {
                'KeyId': 'key-secure-data',
                'RotationEnabled': True,
                'Alias': 'alias/secure-data-key',
                'Description': 'Key for secure data bucket'
            },
            {
                'KeyId': 'key-logs',
                'RotationEnabled': True,
                'Alias': 'alias/logs-key',
                'Description': 'Key for logs bucket'
            },
            {
                'KeyId': 'key-backup',
                'RotationEnabled': False,
                'Alias': 'alias/backup-key',
                'Description': 'Key for backup data (no rotation)'
            },
            {
                'KeyId': 'key-legacy',
                'RotationEnabled': False,
                'Alias': 'alias/legacy-key',
                'Description': 'Legacy key without rotation'
            },
            {
                'KeyId': 'key-audit',
                'RotationEnabled': True,
                'Alias': 'alias/audit-key',
                'Description': 'Key for audit logs'
            },
            {
                'KeyId': 'key-compliance',
                'RotationEnabled': True,
                'Alias': 'alias/compliance-key',
                'Description': 'Key for compliance data'
            },
            {
                'KeyId': 'key-staging',
                'RotationEnabled': True,
                'Alias': 'alias/staging-key',
                'Description': 'Key for staging environment'
            },
            {
                'KeyId': 'key-archive',
                'RotationEnabled': False,
                'Alias': 'alias/archive-key',
                'Description': 'Key for archived data'
            },
            {
                'KeyId': 'key-database',
                'RotationEnabled': True,
                'Alias': 'alias/database-key',
                'Description': 'Key for database encryption'
            }
        ]
        
        return kms_keys
    
    def create_cloudtrail_resources(self):
        """Create CloudTrail trails"""
        print("🛤️ Creating CloudTrail resources...")
        
        cloudtrail_trails = [
            {
                'Name': 'protecht-main-trail',
                'MultiRegion': True,
                'LogFileValidation': True,
                'InsightSelectors': ['ApiCallRateInsight', 'ErrorRateInsight']
            },
            {
                'Name': 'protecht-audit-trail',
                'MultiRegion': False,
                'LogFileValidation': True,
                'InsightSelectors': ['ApiCallRateInsight']
            },
            {
                'Name': 'protecht-security-trail',
                'MultiRegion': True,
                'LogFileValidation': False,
                'InsightSelectors': []
            }
        ]
        
        return cloudtrail_trails
    
    def create_waf_resources(self):
        """Create WAF Web ACLs"""
        print("🛡️ Creating WAF resources...")
        
        waf_web_acls = [
            {
                'Name': f'protecht-main-waf-{int(time.time())}',
                'Rules': 15,
                'BlockedCount7d': 1250,
                'Description': 'Main WAF for proTecht application'
            },
            {
                'Name': f'protecht-api-waf-{int(time.time())}',
                'Rules': 8,
                'BlockedCount7d': 320,
                'Description': 'API-specific WAF rules'
            },
            {
                'Name': f'protecht-admin-waf-{int(time.time())}',
                'Rules': 12,
                'BlockedCount7d': 45,
                'Description': 'Admin interface WAF'
            }
        ]
        
        return waf_web_acls
    
    def create_cloudfront_resources(self):
        """Create CloudFront distributions"""
        print("🌐 Creating CloudFront resources...")
        
        cloudfront_distributions = [
            {
                'Id': 'E1234567890ABC',
                'TLSPolicy': 'TLSv1.2_2021',
                'WAFEnabled': True,
                'Description': 'Main CloudFront distribution'
            },
            {
                'Id': 'E0987654321XYZ',
                'TLSPolicy': 'TLSv1.2_2021',
                'WAFEnabled': False,
                'Description': 'API CloudFront distribution'
            },
            {
                'Id': 'E5555555555DEF',
                'TLSPolicy': 'TLSv1.1_2016',
                'WAFEnabled': True,
                'Description': 'Legacy CloudFront distribution'
            }
        ]
        
        return cloudfront_distributions
    
    def create_vpc_resources(self):
        """Create VPC and flow logs"""
        print("🌐 Creating VPC resources...")
        
        vpc_data = {
            'flow_logs': True,
            'nat_gateways': 3,
            'transit_gateway': {'attachments': 2},
            'security_groups': [
                {
                    'GroupId': 'sg-12345678',
                    'OpenPorts': [22, 443],
                    'AllowedCidrs': ['10.0.0.0/16']
                },
                {
                    'GroupId': 'sg-87654321',
                    'OpenPorts': [80, 443],
                    'AllowedCidrs': ['0.0.0.0/0']
                }
            ]
        }
        
        return vpc_data
    
    def create_guardduty_resources(self):
        """Create GuardDuty detector"""
        print("🔍 Creating GuardDuty resources...")
        
        guardduty_data = {
            'detector_count': 1,
            'findings': {
                'Critical': 2,
                'High': 8,
                'Medium': 15,
                'Low': 42
            }
        }
        
        return guardduty_data
    
    def create_security_hub_resources(self):
        """Create Security Hub standards"""
        print("🔒 Creating Security Hub resources...")
        
        security_hub_data = {
            'enabled': True,
            'standards': {
                'CIS AWS Foundations v1.4.0': 'FAILED',
                'AWS Foundational Security Best Practices': 'FAILED',
                'NIST Cybersecurity Framework': 'PARTIAL'
            },
            'open_findings': 67
        }
        
        return security_hub_data
    
    def create_sso_resources(self):
        """Create SSO/Identity Center resources"""
        print("👥 Creating SSO resources...")
        
        sso_data = {
            'enabled': True,
            'federation': True,
            'application_count': 12,
            'mfa_types': ['Virtual', 'Hardware', 'WebAuthn'],
            'session_management': {
                'concurrent_session_limit': 5,
                'session_timeout': 'PT8H',
                'session_lock_enabled': True,
                'session_termination_enabled': True
            },
            'permission_sets_count': 8
        }
        
        return sso_data
    
    def create_config_resources(self):
        """Create AWS Config rules"""
        print("⚙️ Creating Config resources...")
        
        config_data = {
            'account_lockout_rules': [
                {'name': 'account-lockout-policy', 'state': 'COMPLIANT', 'source': 'AWS::Config::Rule'},
                {'name': 'failed-login-lockout', 'state': 'NON_COMPLIANT', 'source': 'AWS::Config::Rule'}
            ],
            'password_policy_rules': [
                {'name': 'password-policy-strength', 'state': 'COMPLIANT', 'source': 'AWS::Config::Rule'},
                {'name': 'password-reuse-prevention', 'state': 'COMPLIANT', 'source': 'AWS::Config::Rule'}
            ],
            'has_account_lockout_protection': True
        }
        
        return config_data
    
    def create_comprehensive_test_data(self):
        """Create comprehensive test data for all AWS services"""
        print("🚀 Creating comprehensive AWS test environment...")
        
        # Create all resources
        aws_data = {
            'iam': self.create_iam_resources(),
            's3': self.create_s3_resources(),
            'kms': self.create_kms_resources(),
            'cloudtrail': {
                'trails': self.create_cloudtrail_resources()
            },
            'waf': {
                'web_acls': self.create_waf_resources()
            },
            'cloudfront': {
                'distributions': self.create_cloudfront_resources()
            },
            'vpc': self.create_vpc_resources(),
            'guardduty': self.create_guardduty_resources(),
            'security_hub': self.create_security_hub_resources(),
            'sso': self.create_sso_resources(),
            'config': self.create_config_resources()
        }
        
        return aws_data
    
    def load_data_to_database(self, aws_data: Dict[str, Any]):
        """Load the test data into the database"""
        print("💾 Loading test data into database...")
        
        try:
            self.db.load_aws_data(aws_data)
            print("✅ Test data loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading test data: {e}")
            return False
    
    def verify_data_loaded(self):
        """Verify that data was loaded correctly"""
        print("🔍 Verifying loaded data...")
        
        try:
            data = self.db.load_aws_data_from_db()
            
            print("\n📊 Data Summary:")
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
        """Test controls evaluation with the new data"""
        print("🧪 Testing controls evaluation...")
        
        try:
            from technical_engine import evaluate_ac_controls
            
            data = self.db.load_aws_data_from_db()
            results = evaluate_ac_controls(data)
            
            print(f"\n📈 Controls Evaluation Results:")
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

def main():
    """Main function to set up comprehensive test environment"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Set up comprehensive AWS test environment')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--verify-only', action='store_true', help='Only verify existing data')
    
    args = parser.parse_args()
    
    print("🚀 proTecht Comprehensive Test Environment Setup")
    print("=" * 50)
    
    setup = AWSTestEnvironmentSetup(profile_name=args.profile, region=args.region)
    
    if args.verify_only:
        print("🔍 Verifying existing data...")
        setup.verify_data_loaded()
        setup.test_controls_evaluation()
        return
    
    # Create comprehensive test data
    aws_data = setup.create_comprehensive_test_data()
    
    # Load data into database
    if setup.load_data_to_database(aws_data):
        # Verify data was loaded
        if setup.verify_data_loaded():
            # Test controls evaluation
            if setup.test_controls_evaluation():
                print("\n🎉 Comprehensive test environment setup complete!")
                print("✅ You can now test the dashboard with realistic data")
                print("✅ All controls should show meaningful compliance scores")
                print("✅ Services should show proper KPIs and status")
            else:
                print("❌ Controls evaluation test failed")
        else:
            print("❌ Data verification failed")
    else:
        print("❌ Data loading failed")

if __name__ == "__main__":
    main()
