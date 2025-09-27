#!/usr/bin/env python3
"""
AWS Compliance Fix Script
Automatically fixes all AC control compliance issues identified by AI analysis.
"""

from __future__ import annotations
import argparse
import json
import os
import time
import uuid
from typing import Dict, Any, List, Optional

import boto3
from botocore.exceptions import ClientError

TAG = {"Key": "Project", "Value": "proTecht-ComplianceFix"}
KMS_TAG = {"TagKey": "Project", "TagValue": "proTecht-ComplianceFix"}

def fix_ac7_password_policy(session):
    """Fix AC-7: Implement strong password policy with account lockout."""
    print("🔧 Fixing AC-7: Password Policy...")
    iam = session.client('iam')
    
    try:
        # Update password policy with strong requirements
        iam.update_account_password_policy(
            MinimumPasswordLength=14,
            RequireSymbols=True,
            RequireNumbers=True,
            RequireUppercaseCharacters=True,
            RequireLowercaseCharacters=True,
            AllowUsersToChangePassword=True,
            HardExpiry=False,
            MaxPasswordAge=90,
            PasswordReusePrevention=24
        )
        print("✅ Password policy updated with strong requirements")
        
        # Note: Account lockout requires AWS Config rules or custom Lambda
        print("⚠️  Account lockout requires AWS Config rules - manual setup needed")
        
    except ClientError as e:
        print(f"❌ Failed to update password policy: {e}")

def fix_ac9_cloudtrail(session, region: str, state: Dict[str, Any]):
    """Fix AC-9: Enable CloudTrail logging."""
    print("🔧 Fixing AC-9: CloudTrail Logging...")
    ct = session.client('cloudtrail', region_name=region)
    s3 = session.client('s3', region_name=region)
    
    # Create audit bucket for CloudTrail
    audit_bucket = f"protecht-audit-logs-{state['suffix']}"
    try:
        s3.create_bucket(Bucket=audit_bucket)
        s3.put_bucket_policy(
            Bucket=audit_bucket,
            Policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "AWSCloudTrailAclCheck",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:GetBucketAcl",
                    "Resource": f"arn:aws:s3:::{audit_bucket}"
                }, {
                    "Sid": "AWSCloudTrailWrite",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:PutObject",
                    "Resource": f"arn:aws:s3:::{audit_bucket}/*",
                    "Condition": {
                        "StringEquals": {
                            "s3:x-amz-acl": "bucket-owner-full-control"
                        }
                    }
                }]
            })
        )
        state['audit_bucket'] = audit_bucket
        print(f"✅ Created audit bucket: {audit_bucket}")
    except ClientError as e:
        print(f"⚠️  Audit bucket creation failed: {e}")
    
    # Create CloudTrail
    try:
        ct.create_trail(
            Name="protecht-compliance-trail",
            S3BucketName=audit_bucket,
            IsMultiRegionTrail=True,
            EnableLogFileValidation=True,
            TagsList=[TAG]
        )
        ct.start_logging(Name="protecht-compliance-trail")
        print("✅ CloudTrail enabled with multi-region logging")
    except ClientError as e:
        print(f"❌ CloudTrail creation failed: {e}")

def fix_ac15_s3_object_lock(session, region: str, state: Dict[str, Any]):
    """Fix AC-15: Enable S3 Object Lock."""
    print("🔧 Fixing AC-15: S3 Object Lock...")
    s3 = session.client('s3', region_name=region)
    
    # Create governance bucket with Object Lock
    governance_bucket = f"protecht-governance-{state['suffix']}"
    try:
        s3.create_bucket(Bucket=governance_bucket)
        s3.put_object_lock_configuration(
            Bucket=governance_bucket,
            ObjectLockConfiguration={
                'ObjectLockEnabled': 'Enabled',
                'Rule': {
                    'DefaultRetention': {
                        'Mode': 'GOVERNANCE',
                        'Days': 30
                    }
                }
            }
        )
        state['governance_bucket'] = governance_bucket
        print(f"✅ Created governance bucket with Object Lock: {governance_bucket}")
    except ClientError as e:
        print(f"❌ S3 Object Lock setup failed: {e}")

def fix_ac3_mfa_enforcement(session):
    """Fix AC-3: Enable MFA for users."""
    print("🔧 Fixing AC-3: MFA Enforcement...")
    iam = session.client('iam')
    
    try:
        # Create MFA policy
        mfa_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "DenyAllExceptListedIfNoMFA",
                "Effect": "Deny",
                "NotAction": [
                    "iam:CreateVirtualMFADevice",
                    "iam:EnableMFADevice",
                    "iam:GetUser",
                    "iam:ListMFADevices",
                    "iam:ListVirtualMFADevices",
                    "iam:ResyncMFADevice",
                    "sts:GetSessionToken"
                ],
                "Resource": "*",
                "Condition": {
                    "BoolIfExists": {
                        "aws:MultiFactorAuthPresent": "false"
                    }
                }
            }]
        }
        
        iam.create_policy(
            PolicyName="ProTechtMFAPolicy",
            PolicyDocument=json.dumps(mfa_policy),
            Description="MFA enforcement policy for ProTecht"
        )
        print("✅ MFA enforcement policy created")
        
        # Note: MFA device creation requires user interaction
        print("⚠️  MFA devices must be created manually for each user")
        
    except ClientError as e:
        print(f"❌ MFA policy creation failed: {e}")

def fix_ac4_vpc_flow_logs(session, region: str, state: Dict[str, Any]):
    """Fix AC-4: Enable VPC Flow Logs."""
    print("🔧 Fixing AC-4: VPC Flow Logs...")
    ec2 = session.client('ec2', region_name=region)
    s3 = session.client('s3', region_name=region)
    
    # Create flow logs bucket
    flow_logs_bucket = f"protecht-flow-logs-{state['suffix']}"
    try:
        s3.create_bucket(Bucket=flow_logs_bucket)
        state['flow_logs_bucket'] = flow_logs_bucket
        print(f"✅ Created flow logs bucket: {flow_logs_bucket}")
    except ClientError as e:
        print(f"⚠️  Flow logs bucket creation failed: {e}")
    
    # Enable VPC Flow Logs
    try:
        vpcs = ec2.describe_vpcs()
        for vpc in vpcs['Vpcs']:
            ec2.create_flow_logs(
                ResourceIds=[vpc['VpcId']],
                ResourceType='VPC',
                TrafficType='ALL',
                LogDestinationType='s3',
                LogDestination=f"arn:aws:s3:::{flow_logs_bucket}/"
            )
            print(f"✅ VPC Flow Logs enabled for {vpc['VpcId']}")
    except ClientError as e:
        print(f"❌ VPC Flow Logs setup failed: {e}")

def fix_ac13_security_hub(session, region: str):
    """Fix AC-13: Enable Security Hub."""
    print("🔧 Fixing AC-13: Security Hub...")
    sh = session.client('securityhub', region_name=region)
    
    try:
        sh.enable_security_hub()
        print("✅ Security Hub enabled")
    except ClientError as e:
        if "already enabled" in str(e).lower():
            print("ℹ️  Security Hub already enabled")
        else:
            print(f"❌ Security Hub setup failed: {e}")

def fix_ac16_kms_rotation(session, region: str):
    """Fix AC-16: Enable KMS key rotation."""
    print("🔧 Fixing AC-16: KMS Key Rotation...")
    kms = session.client('kms', region_name=region)
    
    try:
        # List existing keys
        keys = kms.list_keys()
        for key in keys['Keys']:
            try:
                kms.enable_key_rotation(KeyId=key['KeyId'])
                print(f"✅ Enabled rotation for key: {key['KeyId']}")
            except ClientError as e:
                if "already enabled" in str(e).lower():
                    print(f"ℹ️  Key {key['KeyId']} already has rotation enabled")
                else:
                    print(f"⚠️  Failed to enable rotation for {key['KeyId']}: {e}")
    except ClientError as e:
        print(f"❌ KMS rotation setup failed: {e}")

def fix_ac10_11_12_session_management(session):
    """Fix AC-10, AC-11, AC-12: Session Management (requires SSO)."""
    print("🔧 Fixing AC-10/11/12: Session Management...")
    
    try:
        # Check if SSO is available
        sso = session.client('sso-admin')
        instances = sso.list_instances()
        
        if instances['Instances']:
            print("ℹ️  AWS SSO instances found - session management available")
            print("⚠️  Session timeouts must be configured in SSO console")
        else:
            print("⚠️  No AWS SSO instances found - session management requires SSO setup")
            print("💡 Consider setting up AWS SSO for proper session management")
    except ClientError as e:
        print(f"⚠️  SSO check failed: {e}")

def create_compliance_dashboard(session, region: str, state: Dict[str, Any]):
    """Create a CloudWatch dashboard for compliance monitoring."""
    print("🔧 Creating Compliance Dashboard...")
    cloudwatch = session.client('cloudwatch', region_name=region)
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/CloudTrail", "DataEvents"],
                        ["AWS/CloudTrail", "ManagementEvents"]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": region,
                    "title": "CloudTrail Events",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/GuardDuty", "Findings"]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": region,
                    "title": "GuardDuty Findings",
                    "period": 300
                }
            }
        ]
    }
    
    try:
        cloudwatch.put_dashboard(
            DashboardName="ProTecht-Compliance",
            DashboardBody=json.dumps(dashboard_body)
        )
        print("✅ Compliance dashboard created")
    except ClientError as e:
        print(f"❌ Dashboard creation failed: {e}")

def main():
    parser = argparse.ArgumentParser(description='Fix AWS compliance issues for AC controls')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--region', default='us-east-1')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    state = {'suffix': uuid.uuid4().hex[:8]}

    print("🚀 Starting AWS Compliance Fix Process...")
    print(f"📍 Region: {args.region}")
    print(f"🏷️  Suffix: {state['suffix']}")
    print("=" * 60)

    if args.dry_run:
        print("🔍 DRY RUN - No changes will be made")
        print("📋 Issues that would be fixed:")
        print("  • AC-3: MFA enforcement policy")
        print("  • AC-4: VPC Flow Logs")
        print("  • AC-7: Strong password policy")
        print("  • AC-9: CloudTrail logging")
        print("  • AC-13: Security Hub")
        print("  • AC-15: S3 Object Lock")
        print("  • AC-16: KMS key rotation")
        print("  • AC-10/11/12: Session management (requires SSO)")
        return

    # Fix all compliance issues
    fix_ac7_password_policy(session)
    fix_ac9_cloudtrail(session, args.region, state)
    fix_ac15_s3_object_lock(session, args.region, state)
    fix_ac3_mfa_enforcement(session)
    fix_ac4_vpc_flow_logs(session, args.region, state)
    fix_ac13_security_hub(session, args.region)
    fix_ac16_kms_rotation(session, args.region)
    fix_ac10_11_12_session_management(session)
    create_compliance_dashboard(session, args.region, state)

    print("=" * 60)
    print("✅ Compliance fix process completed!")
    print("📊 Next steps:")
    print("  1. Run: python collect_aws.py --regions us-east-1")
    print("  2. Run: python analyze_detailed.py")
    print("  3. Check CloudWatch dashboard: ProTecht-Compliance")
    print("  4. Manually enable MFA for users in IAM console")
    print("  5. Consider setting up AWS SSO for session management")

if __name__ == '__main__':
    main()
