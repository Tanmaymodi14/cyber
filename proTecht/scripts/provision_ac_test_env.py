#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import uuid
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError

STATE_FILE = "provision_state.json"
TAG = {"Key": "Project", "Value": "proTecht-Test"}
# KMS uses a different tag schema (TagKey/TagValue)
KMS_TAG = {"TagKey": "Project", "TagValue": "proTecht-Test"}


def save_state(state: Dict[str, Any]):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def ensure_s3_bucket(session, region: str, suffix: str, state: Dict[str, Any]):
    s3 = session.client('s3', region_name=region)
    bucket = f"protecht-ac-test-{suffix}"
    try:
        params = {"Bucket": bucket}
        if region != 'us-east-1':
            params["CreateBucketConfiguration"] = {"LocationConstraint": region}
        s3.create_bucket(**params)
        # Block public access
        s3.put_public_access_block(
            Bucket=bucket,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        # Default encryption (SSE-S3)
        s3.put_bucket_encryption(
            Bucket=bucket,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}
                }]
            }
        )
        state['s3_bucket'] = bucket
        print(f"✅ S3 bucket created: {bucket}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            state['s3_bucket'] = bucket
            print(f"ℹ️  S3 bucket already exists: {bucket}")
        else:
            print(f"⚠️  S3 create failed: {e}")
    return state


def ensure_kms_key(session, region: str, suffix: str, state: Dict[str, Any]):
    kms = session.client('kms', region_name=region)
    try:
        resp = kms.create_key(
            Description=f"proTecht AC test key {suffix}",
            KeyUsage='ENCRYPT_DECRYPT',
            Origin='AWS_KMS',
            Tags=[KMS_TAG]
        )
        key_id = resp['KeyMetadata']['KeyId']
        kms.enable_key_rotation(KeyId=key_id)
        state['kms_key_id'] = key_id
        print(f"✅ KMS key created: {key_id}")
    except ClientError as e:
        print(f"⚠️  KMS create failed: {e}")
    return state


def ensure_iam_role(session, suffix: str, state: Dict[str, Any]):
    iam = session.client('iam')
    role_name = f"protecht-ac-test-role-{suffix}"
    assume_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    try:
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy),
            Tags=[{"Key": TAG['Key'], "Value": TAG['Value']}]
        )
        state['iam_role'] = role_name
        print(f"✅ IAM role created: {role_name}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            state['iam_role'] = role_name
            print(f"ℹ️  IAM role already exists: {role_name}")
        else:
            print(f"⚠️  IAM role create failed: {e}")
    return state


def ensure_guardduty(session, region: str, state: Dict[str, Any]):
    gd = session.client('guardduty', region_name=region)
    try:
        dets = gd.list_detectors().get('DetectorIds', [])
        if dets:
            state['guardduty_detector'] = dets[0]
            print(f"ℹ️  GuardDuty detector exists: {dets[0]}")
        else:
            resp = gd.create_detector(Enable=True)
            state['guardduty_detector'] = resp['DetectorId']
            print(f"✅ GuardDuty detector created: {resp['DetectorId']}")
    except ClientError as e:
        print(f"⚠️  GuardDuty setup failed: {e}")
    return state


def ensure_securityhub(session, region: str, state: Dict[str, Any]):
    sh = session.client('securityhub', region_name=region)
    try:
        try:
            sh.describe_hub()
            print("ℹ️  Security Hub already enabled")
        except ClientError:
            sh.enable_security_hub()
            print("✅ Security Hub enabled")
        state['securityhub'] = True
    except ClientError as e:
        print(f"⚠️  Security Hub setup failed: {e}")
    return state


def ensure_wafv2(session, region: str, suffix: str, state: Dict[str, Any]):
    # For CloudFront scope, region must be us-east-1
    waf_region = 'us-east-1'
    waf = session.client('wafv2', region_name=waf_region)
    name = f"protecht-ac-test-waf-{suffix}"
    try:
        resp = waf.create_web_acl(
            Name=name,
            Scope='CLOUDFRONT',
            DefaultAction={'Allow': {}},
            VisibilityConfig={'SampledRequestsEnabled': True, 'CloudWatchMetricsEnabled': True, 'MetricName': name},
            Rules=[],
            Tags=[TAG]
        )
        state['waf_web_acl_arn'] = resp['Summary']['ARN'] if 'Summary' in resp else None
        print(f"✅ WAFv2 WebACL created: {name}")
    except ClientError as e:
        if e.response['Error']['Code'] in ('WAFDuplicateItemException', 'WAFV2DuplicateItemException'):
            print(f"ℹ️  WAFv2 WebACL already exists: {name}")
        else:
            print(f"⚠️  WAFv2 create failed: {e}")
    return state


def destroy(session, region: str):
    state = load_state()
    # Best-effort teardown (not exhaustive)
    s3 = session.client('s3', region_name=region)
    kms = session.client('kms', region_name=region)
    iam = session.client('iam')
    gd = session.client('guardduty', region_name=region)
    waf = session.client('wafv2', region_name='us-east-1')

    if state.get('s3_bucket'):
        b = state['s3_bucket']
        try:
            # empty bucket first
            s3r = session.resource('s3', region_name=region)
            bucket = s3r.Bucket(b)
            bucket.objects.all().delete()
            s3.delete_bucket(Bucket=b)
            print(f"🗑️  Deleted S3 bucket {b}")
        except Exception as e:
            print(f"⚠️  Delete S3 failed: {e}")

    if state.get('kms_key_id'):
        try:
            kms.schedule_key_deletion(KeyId=state['kms_key_id'], PendingWindowInDays=7)
            print(f"🗑️  Scheduled KMS key deletion {state['kms_key_id']}")
        except Exception as e:
            print(f"⚠️  KMS deletion scheduling failed: {e}")

    if state.get('iam_role'):
        try:
            iam.delete_role(RoleName=state['iam_role'])
            print(f"🗑️  Deleted IAM role {state['iam_role']}")
        except Exception as e:
            print(f"⚠️  Delete IAM role failed: {e}")

    if state.get('guardduty_detector'):
        try:
            gd.delete_detector(DetectorId=state['guardduty_detector'])
            print(f"🗑️  Deleted GuardDuty detector {state['guardduty_detector']}")
        except Exception as e:
            print(f"⚠️  Delete GuardDuty failed: {e}")

    # WAF teardown omitted (requires listing web ACLs and tokens)

    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


def main():
    ap = argparse.ArgumentParser(description='Provision minimal AC test resources')
    ap.add_argument('--profile', help='AWS profile name')
    ap.add_argument('--region', default='us-east-1', help='Primary region (default us-east-1)')
    ap.add_argument('--destroy', action='store_true', help='Tear down previously created resources')
    args = ap.parse_args()

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()

    if args.destroy:
        destroy(session, args.region)
        return

    state = load_state()
    suffix = state.get('suffix') or uuid.uuid4().hex[:8]
    state['suffix'] = suffix

    print(f"🚀 Provisioning AC test resources in {args.region} (suffix {suffix})...")
    state = ensure_s3_bucket(session, args.region, suffix, state)
    state = ensure_kms_key(session, args.region, suffix, state)
    state = ensure_iam_role(session, suffix, state)
    state = ensure_guardduty(session, args.region, state)
    state = ensure_securityhub(session, args.region, state)
    state = ensure_wafv2(session, args.region, suffix, state)

    save_state(state)
    print("✅ Provisioning complete. State written to provision_state.json")


if __name__ == '__main__':
    main()
