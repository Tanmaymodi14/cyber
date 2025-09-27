#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import time
import uuid
from typing import Dict, Any, List, Optional

import boto3
from botocore.exceptions import ClientError

STATE_FILE = "provision_scenarios_state.json"
TAG = {"Key": "Project", "Value": "proTecht-AC-Scenarios"}
KMS_TAG = {"TagKey": "Project", "TagValue": "proTecht-AC-Scenarios"}


def save_state(state: Dict[str, Any]):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def ensure_bucket(session, region: str, name: str, public: bool, encrypt: bool) -> str:
    s3 = session.client('s3', region_name=region)
    params = {"Bucket": name}
    if region != 'us-east-1':
        params["CreateBucketConfiguration"] = {"LocationConstraint": region}
    s3.create_bucket(**params)
    if public:
        # Remove/disable public access block to simulate insecure
        try:
            s3.delete_public_access_block(Bucket=name)
        except ClientError:
            pass
        # Add a public policy allowing s3:GetObject
        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{name}/*"
            }]
        }
        s3.put_bucket_policy(Bucket=name, Policy=json.dumps(policy))
    else:
        # Block public access
        s3.put_public_access_block(
            Bucket=name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
    if encrypt:
        s3.put_bucket_encryption(
            Bucket=name,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}
                }]
            }
        )
    return name


def ensure_kms_key(session, region: str, description: str, rotation: bool) -> str:
    kms = session.client('kms', region_name=region)
    resp = kms.create_key(Description=description, KeyUsage='ENCRYPT_DECRYPT', Origin='AWS_KMS', Tags=[KMS_TAG])
    key_id = resp['KeyMetadata']['KeyId']
    if rotation:
        kms.enable_key_rotation(KeyId=key_id)
    return key_id


def ensure_password_policy(iam, strong: bool):
    params: Dict[str, Any] = {}
    if strong:
        params = {
            'MinimumPasswordLength': 14,
            'RequireSymbols': True,
            'RequireNumbers': True,
            'RequireUppercaseCharacters': True,
            'RequireLowercaseCharacters': True,
            'AllowUsersToChangePassword': True,
            'HardExpiry': False,
            'MaxPasswordAge': 90,
            'PasswordReusePrevention': 24
        }
    else:
        params = {
            'MinimumPasswordLength': 6,
            'RequireSymbols': False,
            'RequireNumbers': False,
            'RequireUppercaseCharacters': False,
            'RequireLowercaseCharacters': False,
            'AllowUsersToChangePassword': True
        }
    try:
        iam.update_account_password_policy(**params)
    except ClientError as e:
        print(f"⚠️  Update password policy failed: {e}")


def ensure_waf_acl(session, name: str, allow_all: bool) -> Optional[str]:
    waf = session.client('wafv2', region_name='us-east-1')
    try:
        default_action = {'Allow': {}} if allow_all else {'Block': {}}
        resp = waf.create_web_acl(
            Name=name,
            Scope='CLOUDFRONT',
            DefaultAction=default_action,
            VisibilityConfig={'SampledRequestsEnabled': True, 'CloudWatchMetricsEnabled': True, 'MetricName': name},
            Rules=[],
            Tags=[TAG]
        )
        return resp.get('Summary', {}).get('ARN')
    except ClientError as e:
        print(f"⚠️  Create WAF ACL failed: {e}")
        return None


def ensure_guardduty(session, region: str) -> Optional[str]:
    gd = session.client('guardduty', region_name=region)
    dets = gd.list_detectors().get('DetectorIds', [])
    if dets:
        return dets[0]
    resp = gd.create_detector(Enable=True)
    return resp['DetectorId']


def ensure_securityhub(session, region: str):
    sh = session.client('securityhub', region_name=region)
    try:
        sh.describe_hub()
    except ClientError:
        sh.enable_security_hub()


def destroy(session, region: str):
    state = load_state()
    s3 = session.client('s3', region_name=region)
    iam = session.client('iam')
    kms = session.client('kms', region_name=region)
    waf = session.client('wafv2', region_name='us-east-1')

    # Buckets
    for key in ['s3_secure', 's3_public', 's3_noenc']:
        b = state.get(key)
        if not b:
            continue
        try:
            s3r = session.resource('s3', region_name=region)
            bucket = s3r.Bucket(b)
            bucket.objects.all().delete()
            s3.delete_bucket(Bucket=b)
            print(f"🗑️  Deleted S3 bucket {b}")
        except Exception as e:
            print(f"⚠️  Delete S3 {b} failed: {e}")

    # KMS keys (schedule deletion)
    for key in ['kms_rot', 'kms_norot']:
        kid = state.get(key)
        if kid:
            try:
                kms.schedule_key_deletion(KeyId=kid, PendingWindowInDays=7)
                print(f"🗑️  Scheduled KMS key deletion {kid}")
            except Exception as e:
                print(f"⚠️  KMS deletion scheduling failed: {e}")

    # WAF ACL not deleted (token workflow)

    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


def main():
    ap = argparse.ArgumentParser(description='Provision AC test scenarios (secure/insecure/mixed)')
    ap.add_argument('--profile', help='AWS profile name')
    ap.add_argument('--region', default='us-east-1')
    ap.add_argument('--scenario', choices=['secure','insecure','mixed'], default='mixed')
    ap.add_argument('--destroy', action='store_true')
    args = ap.parse_args()

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    iam = session.client('iam')
    state = load_state()

    if args.destroy:
        destroy(session, args.region)
        return

    suffix = state.get('suffix') or uuid.uuid4().hex[:8]
    state['suffix'] = suffix

    print(f"🚀 Provisioning AC {args.scenario} scenarios in {args.region} (suffix {suffix})...")

    # Password policy (AC-7)
    ensure_password_policy(iam, strong=(args.scenario != 'insecure'))

    # S3 scenarios (AC-16, AC-21)
    if args.scenario in ('secure','mixed'):
        state['s3_secure'] = ensure_bucket(session, args.region, f"protecht-secure-{suffix}", public=False, encrypt=True)
    if args.scenario in ('insecure','mixed'):
        state['s3_public'] = ensure_bucket(session, args.region, f"protecht-public-{suffix}", public=True, encrypt=False)
        state['s3_noenc'] = ensure_bucket(session, args.region, f"protecht-noenc-{suffix}", public=False, encrypt=False)

    # KMS keys (AC-16)
    if args.scenario in ('secure','mixed'):
        state['kms_rot'] = ensure_kms_key(session, args.region, f"proTecht rot {suffix}", rotation=True)
    if args.scenario in ('insecure','mixed'):
        state['kms_norot'] = ensure_kms_key(session, args.region, f"proTecht norot {suffix}", rotation=False)

    # WAF (AC-21)
    if args.scenario in ('secure','mixed'):
        state['waf_block'] = ensure_waf_acl(session, f"protecht-waf-block-{suffix}", allow_all=False)
    if args.scenario in ('insecure','mixed'):
        state['waf_allow'] = ensure_waf_acl(session, f"protecht-waf-allow-{suffix}", allow_all=True)

    # GuardDuty/Security Hub (AC-13)
    ensure_guardduty(session, args.region)
    ensure_securityhub(session, args.region)

    save_state(state)
    print("✅ Scenario provisioning complete. State written to provision_scenarios_state.json")

if __name__ == '__main__':
    main()
