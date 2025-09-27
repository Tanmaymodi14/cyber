import boto3
from typing import Optional, List

def collect(session: boto3.Session, regions: Optional[List[str]] = None) -> dict:
    s3 = session.client('s3')
    buckets = []
    try:
        resp = s3.list_buckets()
        for b in resp.get('Buckets', []):
            name = b['Name']
            info = {'Name': name}
            try:
                enc = s3.get_bucket_encryption(Bucket=name)
                rules = enc['ServerSideEncryptionConfiguration']['Rules']
                info['Encryption'] = True if rules else False
            except Exception:
                info['Encryption'] = False
            try:
                pab = s3.get_public_access_block(Bucket=name)
                info['PublicAccessBlock'] = pab.get('PublicAccessBlockConfiguration', {})
            except Exception:
                info['PublicAccessBlock'] = {}
            try:
                ol = s3.get_object_lock_configuration(Bucket=name)
                config = ol.get('ObjectLockConfiguration', {})
                rule = config.get('Rule', {})
                default_retention = rule.get('DefaultRetention', {})
                info['ObjectLockMode'] = default_retention.get('Mode')
                info['RetentionDays'] = default_retention.get('Days')
            except Exception:
                info['ObjectLockMode'] = None
                info['RetentionDays'] = None
            buckets.append(info)
    except Exception:
        pass
    return {'s3': buckets}
