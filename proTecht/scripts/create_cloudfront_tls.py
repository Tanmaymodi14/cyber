#!/usr/bin/env python3
"""
Create a minimal CloudFront distribution that enforces HTTPS (redirect-to-https)
and TLS 1.2+. Assumes you have an S3 website/static bucket origin (public or via OAC not configured here).

WARNING: CloudFront creation incurs costs. This script is minimal and idempotent by checking for an existing distribution with the given comment tag.
"""

import argparse
import boto3
import time


def ensure_distribution(session: boto3.Session, domain_name: str) -> str:
    cf = session.client('cloudfront')
    comment = f'proTecht-minimal-distribution-for-tls12-{domain_name}'
    # try find existing
    try:
        resp = cf.list_distributions()
        items = (resp.get('DistributionList', {}) or {}).get('Items', [])
        for d in items:
            if d.get('Comment') == comment:
                return d['Id']
    except Exception:
        pass

    # Create minimal distribution
    conf = {
        'CallerReference': str(time.time()),
        'Comment': comment,
        'Enabled': True,
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': 'origin-1',
                    'DomainName': domain_name,
                    'CustomOriginConfig': {
                        'HTTPPort': 80,
                        'HTTPSPort': 443,
                        'OriginProtocolPolicy': 'http-only',
                        'OriginSslProtocols': {'Quantity': 1, 'Items': ['TLSv1.2']},
                    },
                }
            ],
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': 'origin-1',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'TrustedSigners': {'Enabled': False, 'Quantity': 0},
            'AllowedMethods': {'Quantity': 2, 'Items': ['GET', 'HEAD']},
            'ForwardedValues': {'QueryString': False, 'Cookies': {'Forward': 'none'}},
            'MinTTL': 0,
        },
        'ViewerCertificate': {
            'CloudFrontDefaultCertificate': True,
            'MinimumProtocolVersion': 'TLSv1.2_2021',
        },
    }

    resp = cf.create_distribution(DistributionConfig=conf)
    return resp['Distribution']['Id']


def main():
    ap = argparse.ArgumentParser(description='Create CloudFront distribution with TLS1.2 and HTTPS redirect')
    ap.add_argument('--profile')
    ap.add_argument('--origin-domain', required=True, help='Origin domain name (e.g., mybucket.s3-website-us-east-1.amazonaws.com)')
    args = ap.parse_args()

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    dist_id = ensure_distribution(session, args.origin_domain)
    print(f'CloudFront distribution ready: {dist_id}')


if __name__ == '__main__':
    main()


