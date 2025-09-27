import boto3
from typing import Optional, List

def collect(session: boto3.Session, regions: Optional[List[str]] = None) -> dict:
    regions = regions or ['us-east-1']
    enabled = False
    standards = {}
    open_findings = 0
    try:
        for r in regions:
            sh = session.client('securityhub', region_name=r)
            try:
                # Check if Security Hub is enabled
                subs = sh.get_enabled_standards().get('StandardsSubscriptions', [])
                if subs:
                    enabled = True
                    # Get standard details
                    for sub in subs:
                        standard_name = sub.get('StandardsArn', '').split('/')[-1]
                        standards[standard_name] = 'ENABLED'
                    # Get open findings count
                    findings = sh.get_findings(MaxResults=1)
                    open_findings = findings.get('Findings', [])
                    break
            except Exception:
                continue
    except Exception:
        pass
    return {'security_hub': {'enabled': enabled, 'standards': standards, 'open_findings': len(open_findings)}}
