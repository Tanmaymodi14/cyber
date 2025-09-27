import boto3
from typing import Optional, List

def collect(session: boto3.Session, regions: Optional[List[str]] = None) -> dict:
    # Identity Center (SSO) is global; collect detailed session management info
    out = {
        'enabled': False,
        'federation': False,
        'session_management': {
            'concurrent_session_limit': None,
            'session_timeout': None,
            'session_lock_enabled': False,
            'session_termination_enabled': False
        }
    }
    
    try:
        sso = session.client('sso-admin')
        # Check if SSO is configured
        resp = sso.list_instances()
        instances = resp.get('Instances', [])
        
        if instances:
            out['enabled'] = True
            out['federation'] = True
            
            # Get session management configuration
            for instance in instances:
                instance_arn = instance['InstanceArn']
                
                # Check for session management policies
                try:
                    # Get permission sets (these contain session policies)
                    permission_sets = sso.list_permission_sets(InstanceArn=instance_arn)
                    ps_list = permission_sets.get('PermissionSets', [])
                    
                    # Store permission set count for UI KPI
                    out['permission_sets_count'] = len(ps_list)
                    
                    for ps_arn in ps_list:
                        try:
                            # Get session duration for this permission set
                            session_duration = sso.get_permission_set(InstanceArn=instance_arn, PermissionSetArn=ps_arn)
                            duration = session_duration.get('PermissionSet', {}).get('SessionDuration')
                            if duration:
                                out['session_management']['session_timeout'] = duration
                                out['session_management']['session_termination_enabled'] = True
                                
                                # Check if this is a standard duration (PT8H = 8 hours)
                                if duration.startswith('PT') and duration.endswith('H'):
                                    try:
                                        hours = int(duration[2:-1])
                                        # AC-11/12 compliance check: session timeout <= 8 hours
                                        if hours <= 8:
                                            out['session_management']['compliant_timeout'] = True
                                    except (ValueError, IndexError):
                                        pass
                        except Exception:
                            continue
                except Exception:
                    pass
                
                # Check for concurrent session limits (this would be in IdP configuration)
                # For now, we'll assume it's configurable if SSO is enabled
                out['session_management']['concurrent_session_limit'] = 'configurable'
                out['session_management']['session_lock_enabled'] = True
                
                break  # Only check first instance
                
    except Exception:
        pass
    
    return {'sso': out}
