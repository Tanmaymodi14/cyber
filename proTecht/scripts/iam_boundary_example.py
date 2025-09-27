#!/usr/bin/env python3
"""
Create a simple IAM permissions boundary policy and attach it to a role.
This helps demonstrate AC-5 (Separation of Duties) and AC-3 (Access Enforcement) evidence.
"""

import argparse
import json
import boto3


def ensure_boundary(session: boto3.Session, policy_name: str) -> str:
    iam = session.client('iam')
    doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Action": ["iam:*", "organizations:*"],
                "Resource": "*"
            }
        ]
    }
    try:
        resp = iam.create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(doc))
        return resp['Policy']['Arn']
    except iam.exceptions.EntityAlreadyExistsException:
        return iam.get_policy(PolicyArn=f"arn:aws:iam::{session.client('sts').get_caller_identity()['Account']}:policy/{policy_name}")['Policy']['Arn']


def attach_boundary(session: boto3.Session, role_name: str, boundary_arn: str) -> None:
    iam = session.client('iam')
    iam.put_role_permissions_boundary(RoleName=role_name, PermissionsBoundary=boundary_arn)
    print('Attached boundary to', role_name)


def main():
    ap = argparse.ArgumentParser(description='Attach IAM permissions boundary to a role')
    ap.add_argument('--profile')
    ap.add_argument('--role-name', required=True)
    ap.add_argument('--policy-name', default='proTechtBoundary')
    args = ap.parse_args()
    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    arn = ensure_boundary(session, args.policy_name)
    attach_boundary(session, args.role_name, arn)


if __name__ == '__main__':
    main()


