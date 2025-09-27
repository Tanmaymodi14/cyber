import boto3
from typing import Optional, List

def collect(session: boto3.Session, regions: Optional[List[str]] = None) -> dict:
    regions = regions or ['us-east-1']
    web_acls_total = 0
    for r in regions:
        waf = session.client('wafv2', region_name=r)
        try:
            resp = waf.list_web_acls(Scope='CLOUDFRONT')
            web_acls_total += len(resp.get('WebACLs', []))
        except Exception:
            pass
    return {'waf': {'web_acls': [{'count': web_acls_total}] if web_acls_total else []}}
