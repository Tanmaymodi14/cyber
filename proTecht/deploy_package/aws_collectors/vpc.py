import boto3
from typing import Optional, List

def collect(session: boto3.Session, regions: Optional[List[str]] = None) -> dict:
    regions = regions or ['us-east-1']
    out = {'flow_logs': False}
    for r in regions:
        ec2 = session.client('ec2', region_name=r)
        try:
            resp = ec2.describe_flow_logs()
            if resp.get('FlowLogs'):
                out['flow_logs'] = True
                break
        except Exception:
            continue
    return {'vpc': out}
