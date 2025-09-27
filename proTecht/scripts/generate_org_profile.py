#!/usr/bin/env python3
"""
Comprehensive Organizational Profile Generator for AC Family Testing
Creates realistic enterprise scenarios with multiple users, roles, departments, and security configurations.
"""

from __future__ import annotations
import argparse
import json
import os
import random
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError

STATE_FILE = "org_profile_state.json"
TAG = {"Key": "Project", "Value": "proTecht-OrgProfile"}
KMS_TAG = {"TagKey": "Project", "TagValue": "proTecht-OrgProfile"}

@dataclass
class UserProfile:
    username: str
    department: str
    role: str
    access_level: str  # admin, power_user, standard, read_only
    mfa_enabled: bool
    password_policy: str  # strong, medium, weak
    last_login_days: int

@dataclass
class DepartmentConfig:
    name: str
    security_level: str  # high, medium, low
    data_classification: str  # confidential, internal, public
    compliance_requirements: List[str]
    resource_tags: Dict[str, str]

# Organizational structure
DEPARTMENTS = [
    DepartmentConfig("IT", "high", "confidential", ["SOX", "PCI"], {"Environment": "Production", "DataClass": "Confidential"}),
    DepartmentConfig("Finance", "high", "confidential", ["SOX", "PCI"], {"Environment": "Production", "DataClass": "Confidential"}),
    DepartmentConfig("HR", "medium", "internal", ["PII"], {"Environment": "Production", "DataClass": "Internal"}),
    DepartmentConfig("Marketing", "low", "public", [], {"Environment": "Development", "DataClass": "Public"}),
    DepartmentConfig("Engineering", "medium", "internal", [], {"Environment": "Development", "DataClass": "Internal"}),
    DepartmentConfig("Legal", "high", "confidential", ["SOX", "Legal"], {"Environment": "Production", "DataClass": "Confidential"}),
    DepartmentConfig("Operations", "medium", "internal", [], {"Environment": "Production", "DataClass": "Internal"}),
]

ROLES = {
    "admin": {"permissions": "full", "mfa_required": True, "password_strength": "strong"},
    "power_user": {"permissions": "extended", "mfa_required": True, "password_strength": "strong"},
    "standard": {"permissions": "standard", "mfa_required": False, "password_strength": "medium"},
    "read_only": {"permissions": "read", "mfa_required": False, "password_strength": "weak"},
    "contractor": {"permissions": "limited", "mfa_required": True, "password_strength": "medium"},
    "intern": {"permissions": "minimal", "mfa_required": False, "password_strength": "weak"},
}

def save_state(state: Dict[str, Any]):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def generate_user_profiles(count: int = 50) -> List[UserProfile]:
    """Generate realistic user profiles with varying security configurations."""
    profiles = []
    first_names = ["John", "Jane", "Mike", "Sarah", "David", "Lisa", "Chris", "Amy", "Tom", "Emma", 
                   "Alex", "Maria", "James", "Jessica", "Robert", "Jennifer", "Michael", "Ashley"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"]
    
    for i in range(count):
        dept = random.choice(DEPARTMENTS)
        role = random.choice(list(ROLES.keys()))
        role_config = ROLES[role]
        
        # Adjust MFA and password based on department security level
        mfa_enabled = role_config["mfa_required"]
        if dept.security_level == "high":
            mfa_enabled = True
        elif dept.security_level == "low" and role in ["read_only", "intern"]:
            mfa_enabled = False
            
        password_policy = role_config["password_strength"]
        if dept.security_level == "high":
            password_policy = "strong"
        elif dept.security_level == "low":
            password_policy = "weak"
            
        profiles.append(UserProfile(
            username=f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}{i}",
            department=dept.name,
            role=role,
            access_level=role,
            mfa_enabled=mfa_enabled,
            password_policy=password_policy,
            last_login_days=random.randint(0, 90)
        ))
    
    return profiles

def create_iam_users(session, profiles: List[UserProfile], state: Dict[str, Any]):
    """Create IAM users with varying configurations."""
    iam = session.client('iam')
    created_users = []
    
    for profile in profiles:
        try:
            # Create user
            iam.create_user(
                UserName=profile.username,
                Tags=[
                    {"Key": "Department", "Value": profile.department},
                    {"Key": "Role", "Value": profile.role},
                    {"Key": "AccessLevel", "Value": profile.access_level},
                    {"Key": "MFAEnabled", "Value": str(profile.mfa_enabled)},
                    {"Key": "PasswordPolicy", "Value": profile.password_policy},
                    {"Key": "LastLoginDays", "Value": str(profile.last_login_days)},
                    TAG
                ]
            )
            
            # Create access key
            key_resp = iam.create_access_key(UserName=profile.username)
            
            # Attach policies based on role
            if profile.role == "admin":
                iam.attach_user_policy(UserName=profile.username, PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess")
            elif profile.role == "power_user":
                iam.attach_user_policy(UserName=profile.username, PolicyArn="arn:aws:iam::aws:policy/PowerUserAccess")
            elif profile.role == "read_only":
                iam.attach_user_policy(UserName=profile.username, PolicyArn="arn:aws:iam::aws:policy/ReadOnlyAccess")
            else:
                # Custom policy for standard users
                policy_doc = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": ["s3:GetObject", "s3:ListBucket"],
                            "Resource": f"arn:aws:s3:::protecht-{profile.department.lower()}-*"
                        }
                    ]
                }
                policy_name = f"StandardUserPolicy-{profile.username}"
                iam.create_policy(
                    PolicyName=policy_name,
                    PolicyDocument=json.dumps(policy_doc),
                    Description=f"Custom policy for {profile.username}"
                )
                iam.attach_user_policy(
                    UserName=profile.username,
                    PolicyArn=f"arn:aws:iam::{session.client('sts').get_caller_identity()['Account']}:policy/{policy_name}"
                )
            
            created_users.append(profile.username)
            print(f"✅ Created user: {profile.username} ({profile.department}/{profile.role})")
            
        except ClientError as e:
            print(f"⚠️  Failed to create user {profile.username}: {e}")
    
    state['iam_users'] = created_users
    return state

def create_department_buckets(session, region: str, state: Dict[str, Any]):
    """Create S3 buckets for each department with varying security configurations."""
    s3 = session.client('s3', region_name=region)
    created_buckets = []
    
    for dept in DEPARTMENTS:
        bucket_name = f"protecht-{dept.name.lower()}-{state['suffix']}"
        
        try:
            # Create bucket
            params = {"Bucket": bucket_name}
            if region != 'us-east-1':
                params["CreateBucketConfiguration"] = {"LocationConstraint": region}
            s3.create_bucket(**params)
            
            # Apply security configuration based on department
            if dept.security_level == "high":
                # High security: block public access, enable encryption
                s3.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
                s3.put_bucket_encryption(
                    Bucket=bucket_name,
                    ServerSideEncryptionConfiguration={
                        'Rules': [{
                            'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}
                        }]
                    }
                )
            elif dept.security_level == "low":
                # Low security: allow public access, no encryption
                s3.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=json.dumps({
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/*"
                        }]
                    })
                )
            else:
                # Medium security: block public access, no encryption
                s3.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
            
            # Add tags
            s3.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={'TagSet': [{"Key": k, "Value": v} for k, v in dept.resource_tags.items()] + [TAG]}
            )
            
            created_buckets.append(bucket_name)
            print(f"✅ Created bucket: {bucket_name} (security: {dept.security_level})")
            
        except ClientError as e:
            print(f"⚠️  Failed to create bucket {bucket_name}: {e}")
    
    state['s3_buckets'] = created_buckets
    return state

def create_kms_keys(session, region: str, state: Dict[str, Any]):
    """Create KMS keys with varying rotation settings."""
    kms = session.client('kms', region_name=region)
    created_keys = []
    
    # Create keys for different departments
    for dept in DEPARTMENTS:
        key_id = f"protecht-{dept.name.lower()}-key"
        try:
            resp = kms.create_key(
                Description=f"KMS key for {dept.name} department",
                KeyUsage='ENCRYPT_DECRYPT',
                Origin='AWS_KMS',
                Tags=[KMS_TAG, {"TagKey": "Department", "TagValue": dept.name}]
            )
            key_arn = resp['KeyMetadata']['KeyId']
            
            # Enable rotation for high security departments
            if dept.security_level == "high":
                kms.enable_key_rotation(KeyId=key_arn)
                print(f"✅ Created KMS key with rotation: {key_arn} ({dept.name})")
            else:
                print(f"✅ Created KMS key without rotation: {key_arn} ({dept.name})")
            
            created_keys.append(key_arn)
            
        except ClientError as e:
            print(f"⚠️  Failed to create KMS key for {dept.name}: {e}")
    
    state['kms_keys'] = created_keys
    return state

def create_iam_roles(session, state: Dict[str, Any]):
    """Create IAM roles for different access patterns."""
    iam = session.client('iam')
    created_roles = []
    
    role_configs = [
        {
            "name": "protecht-cross-account-role",
            "description": "Cross-account access role",
            "trust_policy": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{session.client('sts').get_caller_identity()['Account']}:root"},
                    "Action": "sts:AssumeRole"
                }]
            }
        },
        {
            "name": "protecht-lambda-execution-role",
            "description": "Lambda execution role",
            "trust_policy": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
        },
        {
            "name": "protecht-ec2-instance-role",
            "description": "EC2 instance role",
            "trust_policy": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
        }
    ]
    
    for config in role_configs:
        try:
            iam.create_role(
                RoleName=config["name"],
                AssumeRolePolicyDocument=json.dumps(config["trust_policy"]),
                Description=config["description"],
                Tags=[TAG]
            )
            
            # Attach policies
            if "lambda" in config["name"]:
                iam.attach_role_policy(RoleName=config["name"], PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole")
            elif "ec2" in config["name"]:
                iam.attach_role_policy(RoleName=config["name"], PolicyArn="arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess")
            
            created_roles.append(config["name"])
            print(f"✅ Created role: {config['name']}")
            
        except ClientError as e:
            print(f"⚠️  Failed to create role {config['name']}: {e}")
    
    state['iam_roles'] = created_roles
    return state

def create_cloudtrail_trails(session, region: str, state: Dict[str, Any]):
    """Create CloudTrail trails with varying configurations."""
    ct = session.client('cloudtrail', region_name=region)
    created_trails = []
    
    trail_configs = [
        {
            "name": "protecht-management-events",
            "description": "Management events trail",
            "include_management_events": True,
            "include_data_events": False
        },
        {
            "name": "protecht-data-events",
            "description": "Data events trail",
            "include_management_events": False,
            "include_data_events": True
        }
    ]
    
    for config in trail_configs:
        try:
            ct.create_trail(
                Name=config["name"],
                S3BucketName=state['s3_buckets'][0],  # Use first bucket
                IsMultiRegionTrail=True,
                EnableLogFileValidation=True,
                TagsList=[TAG]
            )
            
            ct.start_logging(Name=config["name"])
            created_trails.append(config["name"])
            print(f"✅ Created CloudTrail: {config['name']}")
            
        except ClientError as e:
            print(f"⚠️  Failed to create CloudTrail {config['name']}: {e}")
    
    state['cloudtrail_trails'] = created_trails
    return state

def create_waf_webacls(session, state: Dict[str, Any]):
    """Create WAF WebACLs with different security configurations."""
    waf = session.client('wafv2', region_name='us-east-1')
    created_acls = []
    
    acl_configs = [
        {
            "name": "protecht-strict-security",
            "description": "Strict security WebACL",
            "default_action": "Block",
            "rules": []
        },
        {
            "name": "protecht-permissive",
            "description": "Permissive WebACL",
            "default_action": "Allow",
            "rules": []
        }
    ]
    
    for config in acl_configs:
        try:
            resp = waf.create_web_acl(
                Name=config["name"],
                Scope='CLOUDFRONT',
                DefaultAction={'Block': {}} if config["default_action"] == "Block" else {'Allow': {}},
                VisibilityConfig={
                    'SampledRequestsEnabled': True,
                    'CloudWatchMetricsEnabled': True,
                    'MetricName': config["name"]
                },
                Rules=config["rules"],
                Tags=[TAG]
            )
            
            acl_arn = resp.get('Summary', {}).get('ARN')
            if acl_arn:
                created_acls.append(acl_arn)
                print(f"✅ Created WAF WebACL: {config['name']}")
            
        except ClientError as e:
            print(f"⚠️  Failed to create WAF WebACL {config['name']}: {e}")
    
    state['waf_webacls'] = created_acls
    return state

def create_guardduty_detectors(session, region: str, state: Dict[str, Any]):
    """Create GuardDuty detectors."""
    gd = session.client('guardduty', region_name=region)
    
    try:
        dets = gd.list_detectors().get('DetectorIds', [])
        if dets:
            state['guardduty_detector'] = dets[0]
            print(f"ℹ️  GuardDuty detector exists: {dets[0]}")
        else:
            resp = gd.create_detector(Enable=True)
            state['guardduty_detector'] = resp['DetectorId']
            print(f"✅ Created GuardDuty detector: {resp['DetectorId']}")
    except ClientError as e:
        print(f"⚠️  GuardDuty setup failed: {e}")
    
    return state

def create_security_hub(session, region: str, state: Dict[str, Any]):
    """Enable Security Hub."""
    sh = session.client('securityhub', region_name=region)
    
    try:
        sh.describe_hub()
        print("ℹ️  Security Hub already enabled")
    except ClientError:
        sh.enable_security_hub()
        print("✅ Enabled Security Hub")
    
    state['security_hub'] = True
    return state

def destroy_org_profile(session, region: str):
    """Destroy all created organizational resources."""
    state = load_state()
    iam = session.client('iam')
    s3 = session.client('s3', region_name=region)
    kms = session.client('kms', region_name=region)
    ct = session.client('cloudtrail', region_name=region)
    waf = session.client('wafv2', region_name='us-east-1')
    gd = session.client('guardduty', region_name=region)
    
    # Delete IAM users
    for username in state.get('iam_users', []):
        try:
            # Detach policies
            policies = iam.list_attached_user_policies(UserName=username)
            for policy in policies['AttachedPolicies']:
                iam.detach_user_policy(UserName=username, PolicyArn=policy['PolicyArn'])
            
            # Delete access keys
            keys = iam.list_access_keys(UserName=username)
            for key in keys['AccessKeyMetadata']:
                iam.delete_access_key(UserName=username, AccessKeyId=key['AccessKeyId'])
            
            # Delete user
            iam.delete_user(UserName=username)
            print(f"🗑️  Deleted user: {username}")
        except Exception as e:
            print(f"⚠️  Delete user {username} failed: {e}")
    
    # Delete IAM roles
    for role_name in state.get('iam_roles', []):
        try:
            iam.delete_role(RoleName=role_name)
            print(f"🗑️  Deleted role: {role_name}")
        except Exception as e:
            print(f"⚠️  Delete role {role_name} failed: {e}")
    
    # Delete S3 buckets
    for bucket_name in state.get('s3_buckets', []):
        try:
            s3r = session.resource('s3', region_name=region)
            bucket = s3r.Bucket(bucket_name)
            bucket.objects.all().delete()
            s3.delete_bucket(Bucket=bucket_name)
            print(f"🗑️  Deleted bucket: {bucket_name}")
        except Exception as e:
            print(f"⚠️  Delete bucket {bucket_name} failed: {e}")
    
    # Schedule KMS key deletion
    for key_id in state.get('kms_keys', []):
        try:
            kms.schedule_key_deletion(KeyId=key_id, PendingWindowInDays=7)
            print(f"🗑️  Scheduled KMS key deletion: {key_id}")
        except Exception as e:
            print(f"⚠️  KMS key deletion scheduling failed: {e}")
    
    # Delete CloudTrail trails
    for trail_name in state.get('cloudtrail_trails', []):
        try:
            ct.stop_logging(Name=trail_name)
            ct.delete_trail(Name=trail_name)
            print(f"🗑️  Deleted CloudTrail: {trail_name}")
        except Exception as e:
            print(f"⚠️  Delete CloudTrail {trail_name} failed: {e}")
    
    # Delete GuardDuty detector
    if state.get('guardduty_detector'):
        try:
            gd.delete_detector(DetectorId=state['guardduty_detector'])
            print(f"🗑️  Deleted GuardDuty detector: {state['guardduty_detector']}")
        except Exception as e:
            print(f"⚠️  Delete GuardDuty failed: {e}")
    
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

def main():
    ap = argparse.ArgumentParser(description='Generate comprehensive organizational profile for AC testing')
    ap.add_argument('--profile', help='AWS profile name')
    ap.add_argument('--region', default='us-east-1')
    ap.add_argument('--users', type=int, default=50, help='Number of users to create')
    ap.add_argument('--destroy', action='store_true', help='Destroy all created resources')
    args = ap.parse_args()

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    state = load_state()

    if args.destroy:
        destroy_org_profile(session, args.region)
        return

    suffix = state.get('suffix') or uuid.uuid4().hex[:8]
    state['suffix'] = suffix

    print(f"🏢 Generating organizational profile with {args.users} users (suffix {suffix})...")
    
    # Generate user profiles
    profiles = generate_user_profiles(args.users)
    print(f"📊 Generated {len(profiles)} user profiles across {len(DEPARTMENTS)} departments")
    
    # Create AWS resources
    state = create_iam_users(session, profiles, state)
    state = create_department_buckets(session, args.region, state)
    state = create_kms_keys(session, args.region, state)
    state = create_iam_roles(session, state)
    state = create_cloudtrail_trails(session, args.region, state)
    state = create_waf_webacls(session, state)
    state = create_guardduty_detectors(session, args.region, state)
    state = create_security_hub(session, args.region, state)
    
    # Save profile summary
    state['user_profiles'] = [
        {
            'username': p.username,
            'department': p.department,
            'role': p.role,
            'access_level': p.access_level,
            'mfa_enabled': p.mfa_enabled,
            'password_policy': p.password_policy,
            'last_login_days': p.last_login_days
        } for p in profiles
    ]
    
    save_state(state)
    print("✅ Organizational profile generation complete!")
    print(f"📋 Created {len(state.get('iam_users', []))} users, {len(state.get('s3_buckets', []))} buckets, {len(state.get('kms_keys', []))} KMS keys")
    print(f"📄 Profile details saved to {STATE_FILE}")

if __name__ == '__main__':
    main()
