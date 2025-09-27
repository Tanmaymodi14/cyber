import boto3
from typing import Optional, List

def collect(session: boto3.Session, regions: Optional[List[str]] = None) -> dict:
    regions = regions or ['us-east-1']
    trails = []
    for r in regions:
        ct = session.client('cloudtrail', region_name=r)
        try:
            resp = ct.describe_trails(includeShadowTrails=True)
            for t in resp.get('trailList', []):
                t['_region'] = r
                trails.append(t)
        except Exception:
            continue
    return {'cloudtrail': {'trails': trails}}
