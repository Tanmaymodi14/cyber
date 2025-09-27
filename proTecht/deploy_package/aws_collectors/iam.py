import boto3

def collect(session: boto3.Session) -> dict:
    iam = session.client('iam')
    out = {
        'password_policy': {},
        'users': [],
        'roles': []
    }
    try:
        out['password_policy'] = iam.get_account_password_policy().get('PasswordPolicy', {})
    except iam.exceptions.NoSuchEntityException:
        out['password_policy'] = {}
    # Users with MFA status for AC-7 and last login for AC-9
    marker = None
    while True:
        if marker:
            resp = iam.list_users(Marker=marker)
        else:
            resp = iam.list_users()
        
        users = resp.get('Users', [])
        for user in users:
            # Check MFA status for each user (AC-7)
            try:
                mfa_devices = iam.list_mfa_devices(UserName=user['UserName']).get('MFADevices', [])
                user['MFA'] = len(mfa_devices) > 0
            except Exception:
                user['MFA'] = False
                
            # Check last login (AC-9)
            # PasswordLastUsed is already in the user object
            # Add last console login time if available
            try:
                login_profile = iam.get_login_profile(UserName=user['UserName'])
                user['HasConsoleAccess'] = True
            except Exception:
                user['HasConsoleAccess'] = False
        
        out['users'].extend(users)
        if not resp.get('IsTruncated'):
            break
        marker = resp.get('Marker')
    # Roles
    marker = None
    while True:
        if marker:
            resp = iam.list_roles(Marker=marker)
        else:
            resp = iam.list_roles()
        roles = resp.get('Roles', [])
        # Enrich roles with attached policies (permissions) and permissions boundary
        for r in roles:
            role_name = r.get('RoleName')
            try:
                attached = iam.list_attached_role_policies(RoleName=role_name).get('AttachedPolicies', [])
            except Exception:
                attached = []
            r['AttachedPolicies'] = attached
            # PermissionsBoundary in role dict already; keep as is
        out['roles'].extend(roles)
        if not resp.get('IsTruncated'):
            break
        marker = resp.get('Marker')
    return {'iam': out}
