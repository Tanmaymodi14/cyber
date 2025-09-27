#!/usr/bin/env python3
"""
List Identity Center (SSO) permission sets and set SessionDuration (e.g., PT4H).
Lock/termination generally require IdP policy; this script focuses on duration.
"""

import argparse
import boto3


def list_permission_sets(sso):
    instances = sso.list_instances().get('Instances', [])
    if not instances:
        print('No SSO instances found')
        return None, []
    inst_arn = instances[0]['InstanceArn']
    ps_arns = sso.list_permission_sets(InstanceArn=inst_arn).get('PermissionSets', [])
    return inst_arn, ps_arns


def print_permission_sets(session):
    sso = session.client('sso-admin')
    inst_arn, ps_arns = list_permission_sets(sso)
    if not inst_arn:
        return
    for ps_arn in ps_arns:
        detail = sso.get_permission_set(InstanceArn=inst_arn, PermissionSetArn=ps_arn).get('PermissionSet', {})
        print(ps_arn, detail.get('Name'), detail.get('SessionDuration'))


def set_duration(session, duration: str):
    sso = session.client('sso-admin')
    inst_arn, ps_arns = list_permission_sets(sso)
    if not inst_arn:
        return
    for ps_arn in ps_arns:
        try:
            sso.update_permission_set(InstanceArn=inst_arn, PermissionSetArn=ps_arn, SessionDuration=duration)
            print('Updated', ps_arn, 'to', duration)
        except Exception as e:
            print('Failed', ps_arn, e)


def main():
    ap = argparse.ArgumentParser(description='SSO SessionDuration helper')
    ap.add_argument('--profile')
    ap.add_argument('--duration', help='ISO-8601 duration, e.g., PT4H')
    args = ap.parse_args()
    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    if args.duration:
        set_duration(session, args.duration)
    else:
        print_permission_sets(session)


if __name__ == '__main__':
    main()


