import boto3
from typing import Optional, List

def collect(session: boto3.Session, regions: Optional[List[str]] = None) -> dict:
    regions = regions or ['us-east-1']
    detector_count = 0
    for r in regions:
        gd = session.client('guardduty', region_name=r)
        try:
            dets = gd.list_detectors().get('DetectorIds', [])
            detector_count += len(dets)
        except Exception:
            continue
    return {'guardduty': {'detector_count': detector_count}}
