import boto3
from typing import Optional, List

def collect(session: boto3.Session, regions: Optional[List[str]] = None) -> dict:
    regions = regions or ['us-east-1']
    rules_total = 0
    account_lockout_rules = []
    password_policy_rules = []
    
    for r in regions:
        cfg = session.client('config', region_name=r)
        try:
            paginator = cfg.get_paginator('describe_config_rules')
            for page in paginator.paginate():
                rules = page.get('ConfigRules', [])
                rules_total += len(rules)
                
                for rule in rules:
                    rule_name = rule.get('ConfigRuleName', '')
                    # Look for account lockout related rules
                    if any(keyword in rule_name.lower() for keyword in ['lockout', 'account', 'password', 'mfa']):
                        account_lockout_rules.append({
                            'name': rule_name,
                            'state': rule.get('ConfigRuleState', 'UNKNOWN'),
                            'source': rule.get('Source', {}).get('SourceIdentifier', 'UNKNOWN')
                        })
                    # Look for password policy rules
                    if 'password' in rule_name.lower() or 'policy' in rule_name.lower():
                        password_policy_rules.append({
                            'name': rule_name,
                            'state': rule.get('ConfigRuleState', 'UNKNOWN'),
                            'source': rule.get('Source', {}).get('SourceIdentifier', 'UNKNOWN')
                        })
        except Exception:
            continue
    
    return {
        'config': {
            'rules_total': rules_total,
            'account_lockout_rules': account_lockout_rules,
            'password_policy_rules': password_policy_rules,
            'has_account_lockout_protection': len(account_lockout_rules) > 0
        }
    }
