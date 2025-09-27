import json
import boto3
from typing import List, Dict, Any, Optional, Callable

from database import ProTechtDatabase
from aws_collectors import iam, cloudtrail, s3, cloudfront, waf, kms, securityhub, guardduty, identity_center, config as cfg, vpc


def deep_merge(target: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            deep_merge(target[k], v)
        else:
            target[k] = v
    return target


ProgressCallback = Optional[Callable[[str, str, int, int], None]]


def collect_all(profile: Optional[str] = None, regions: Optional[List[str]] = None, *, progress_cb: ProgressCallback = None) -> Dict[str, Any]:
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    regions = regions or ['us-east-1']
    data: Dict[str, Any] = {}

    modules = [iam, cloudtrail, s3, cloudfront, waf, kms, securityhub, guardduty, identity_center, cfg, vpc]
    total = len(modules)
    for index, mod in enumerate(modules):
        try:
            if progress_cb:
                progress_cb(mod.__name__.split('.')[-1], 'starting', index, total)
            part = mod.collect(session, regions) if 'regions' in mod.collect.__code__.co_varnames else mod.collect(session)
            deep_merge(data, part)
            if progress_cb:
                progress_cb(mod.__name__.split('.')[-1], 'success', index, total)
        except Exception as e:
            print(f"Collector {mod.__name__} failed: {e}")
            if progress_cb:
                progress_cb(mod.__name__.split('.')[-1], 'error', index, total)
    return data


def build_mixed_evidence(collected: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'iam_users': collected.get('iam', {}).get('users', []),
        'cloudtrail_logs': collected.get('cloudtrail', {}).get('trails', []),
        'config_rules': collected.get('config', {}).get('rules_total', 0),
        'system_banners': collected.get('waf', {}).get('web_acls', []),  # placeholder for AC-8
        'remote_access': collected.get('vpc', {}).get('flow_logs', False),
        'wireless_controls': collected.get('config', {}).get('rules_total', 0),
        'mobile_controls': collected.get('security_hub', {}).get('standards', False)
    }


