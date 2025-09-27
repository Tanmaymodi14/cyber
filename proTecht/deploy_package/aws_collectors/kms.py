import boto3
from typing import Optional, List

def collect(session: boto3.Session, regions: Optional[List[str]] = None) -> dict:
    regions = regions or ['us-east-1']
    keys = []
    for r in regions:
        kms = session.client('kms', region_name=r)
        try:
            paginator = kms.get_paginator('list_keys')
            for page in paginator.paginate():
                for k in page.get('Keys', []):
                    arn = k.get('KeyArn')
                    try:
                        meta = kms.describe_key(KeyId=arn)['KeyMetadata']
                        keys.append({'KeyId': meta['KeyId'], 'Arn': arn, 'RotationEnabled': meta.get('KeyRotationEnabled', False)})
                    except Exception:
                        continue
        except Exception:
            continue
    return {'kms': keys}
