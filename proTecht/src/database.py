#!/usr/bin/env python3
"""
Database module for proTecht
Stores AWS infrastructure data for compliance analysis
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
try:
    from .config import get_database_path
except ImportError:
    # Fallback for direct execution
    def get_database_path():
        return "protecht.db"

class ProTechtDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or get_database_path()
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Account metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_metadata (
                id INTEGER PRIMARY KEY,
                org_id TEXT UNIQUE,
                master_payer_id TEXT,
                regions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Control tower table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS control_tower (
                id INTEGER PRIMARY KEY,
                version TEXT,
                enabled_guardrails INTEGER,
                accounts_managed INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # IAM password policy table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iam_password_policy (
                id INTEGER PRIMARY KEY,
                minimum_password_length INTEGER,
                require_symbols BOOLEAN,
                require_numbers BOOLEAN,
                require_uppercase BOOLEAN,
                require_lowercase BOOLEAN,
                max_password_age INTEGER,
                password_reuse_prevention INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # IAM users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iam_users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                mfa_enabled BOOLEAN,
                last_login TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # IAM roles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iam_roles (
                id INTEGER PRIMARY KEY,
                role_name TEXT UNIQUE,
                permissions TEXT,
                boundary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # SSO table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sso (
                id INTEGER PRIMARY KEY,
                application_count INTEGER,
                mfa_types TEXT,
                federation TEXT,
                enabled INTEGER,
                concurrent_session_limit TEXT,
                session_timeout TEXT,
                session_lock_enabled INTEGER,
                session_termination_enabled INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # S3 buckets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS s3_buckets (
                id INTEGER PRIMARY KEY,
                bucket_name TEXT UNIQUE,
                encryption TEXT,
                object_lock_mode TEXT,
                retention_days INTEGER,
                public_access_block BOOLEAN,
                kms_key_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # KMS keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kms_keys (
                id INTEGER PRIMARY KEY,
                key_id TEXT UNIQUE,
                rotation_enabled BOOLEAN,
                alias TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # CloudTrail trails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cloudtrail_trails (
                id INTEGER PRIMARY KEY,
                trail_name TEXT UNIQUE,
                multi_region BOOLEAN,
                log_file_validation BOOLEAN,
                insight_selectors TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Config rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config_rules (
                id INTEGER PRIMARY KEY,
                rule_name TEXT UNIQUE,
                compliance_type TEXT,
                rule_state TEXT,
                source_identifier TEXT,
                rule_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Config conformance packs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config_conformance_packs (
                id INTEGER PRIMARY KEY,
                pack_name TEXT UNIQUE,
                status TEXT,
                failing_rules INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # GuardDuty table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guardduty (
                id INTEGER PRIMARY KEY,
                detector_count INTEGER,
                critical_findings INTEGER,
                high_findings INTEGER,
                medium_findings INTEGER,
                low_findings INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Security Hub table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_hub (
                id INTEGER PRIMARY KEY,
                standard_name TEXT UNIQUE,
                status TEXT,
                open_findings INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Macie jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS macie_jobs (
                id INTEGER PRIMARY KEY,
                job_id TEXT UNIQUE,
                status TEXT,
                s3_buckets_scanned INTEGER,
                sensitive_findings INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inspector2 table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inspector2 (
                id INTEGER PRIMARY KEY,
                last_run TEXT,
                critical_findings INTEGER,
                high_findings INTEGER,
                medium_findings INTEGER,
                low_findings INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # EKS clusters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eks_clusters (
                id INTEGER PRIMARY KEY,
                cluster_name TEXT UNIQUE,
                oidc_enabled BOOLEAN,
                irsa_enabled BOOLEAN,
                k8s_version TEXT,
                public_access BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ECS clusters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ecs_clusters (
                id INTEGER PRIMARY KEY,
                cluster_name TEXT UNIQUE,
                fargate_tasks INTEGER,
                ec2_tasks INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # RDS instances table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rds_instances (
                id INTEGER PRIMARY KEY,
                instance_name TEXT UNIQUE,
                engine TEXT,
                encrypted BOOLEAN,
                multi_az BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # DynamoDB tables table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dynamodb_tables (
                id INTEGER PRIMARY KEY,
                table_name TEXT UNIQUE,
                encrypted BOOLEAN,
                kms_key_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # EFS file systems table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS efs_file_systems (
                id INTEGER PRIMARY KEY,
                file_system_id TEXT UNIQUE,
                encrypted BOOLEAN,
                kms_key_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Backup table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup (
                id INTEGER PRIMARY KEY,
                vault_name TEXT UNIQUE,
                resources_protected INTEGER,
                cross_region_copy BOOLEAN,
                vault_lock TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # VPC table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vpc (
                id INTEGER PRIMARY KEY,
                flow_logs BOOLEAN,
                nat_gateways INTEGER,
                transit_gateway_attachments INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Security groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_groups (
                id INTEGER PRIMARY KEY,
                group_id TEXT UNIQUE,
                open_ports TEXT,
                allowed_cidrs TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # API Gateway table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_gateway (
                id INTEGER PRIMARY KEY,
                stage_name TEXT UNIQUE,
                execution_logging BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # WAF table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waf (
                id INTEGER PRIMARY KEY,
                web_acl_name TEXT UNIQUE,
                rules_count INTEGER,
                blocked_count_7d INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # CloudFront table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cloudfront (
                id INTEGER PRIMARY KEY,
                distribution_id TEXT UNIQUE,
                tls_policy TEXT,
                waf_enabled BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # SSM Patch table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ssm_patch (
                id INTEGER PRIMARY KEY,
                last_scan TEXT,
                pending_critical INTEGER,
                pending_high INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # EventBridge rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eventbridge_rules (
                id INTEGER PRIMARY KEY,
                rule_name TEXT UNIQUE,
                target TEXT,
                state TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Detective table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detective (
                id INTEGER PRIMARY KEY,
                graph_enabled BOOLEAN,
                member_accounts INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # CodeBuild table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS codebuild (
                id INTEGER PRIMARY KEY,
                projects_count INTEGER,
                failed_builds_last7d INTEGER,
                passed_builds INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # CodePipeline table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS codepipeline (
                id INTEGER PRIMARY KEY,
                pipelines_count INTEGER,
                failed_executions INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Lambda table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lambda (
                id INTEGER PRIMARY KEY,
                functions_count INTEGER,
                unreserved_concurrent_executions INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # CloudWatch table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cloudwatch (
                id INTEGER PRIMARY KEY,
                alarms_count INTEGER,
                metrics_collected INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Route53 table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS route53 (
                id INTEGER PRIMARY KEY,
                hosted_zones INTEGER,
                health_checks INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Direct Connect table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS direct_connect (
                id INTEGER PRIMARY KEY,
                connections INTEGER,
                locations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # VPN table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vpn (
                id INTEGER PRIMARY KEY,
                client_vpn_endpoints INTEGER,
                active_sessions INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # FedRAMP template storage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fedramp_templates (
                id INTEGER PRIMARY KEY,
                template_name TEXT UNIQUE,
                template_type TEXT,
                file_path TEXT,
                file_content BLOB,
                file_size INTEGER,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Policies table for uploaded policy documents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                filename TEXT,
                content TEXT,
                controls_mapped TEXT,
                last_analyzed TIMESTAMP,
                status TEXT,
                type TEXT,
                summary TEXT,
                reasons TEXT,
                missing TEXT,
                recommendations TEXT,
                citations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def clear_all_data(self):
        """Clear all data from all tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        tables = [
            'account_metadata', 'control_tower', 'iam_password_policy', 'iam_users', 'iam_roles',
            'sso', 's3_buckets', 'kms_keys', 'cloudtrail_trails', 'config_rules', 'config_conformance_packs',
            'guardduty', 'security_hub', 'macie_jobs', 'inspector2', 'eks_clusters', 'ecs_clusters',
            'rds_instances', 'dynamodb_tables', 'efs_file_systems', 'backup', 'vpc', 'security_groups',
            'api_gateway', 'waf', 'cloudfront', 'ssm_patch', 'eventbridge_rules', 'detective',
            'codebuild', 'codepipeline', 'lambda', 'cloudwatch', 'route53', 'direct_connect', 'vpn'
        ]
        
        for table in tables:
            cursor.execute(f'DELETE FROM {table}')
        
        conn.commit()
        conn.close()
    
    def load_aws_data(self, aws_data: Dict[str, Any]):
        """Load AWS data into database"""
        self.clear_all_data()  # Clear existing data
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Account metadata
            if 'account_metadata' in aws_data:
                metadata = aws_data['account_metadata']
                cursor.execute('''
                    INSERT INTO account_metadata (org_id, master_payer_id, regions)
                    VALUES (?, ?, ?)
                ''', (metadata['org_id'], metadata['master_payer_id'], json.dumps(metadata['regions'])))
            
            # Control tower
            if 'control_tower' in aws_data:
                ct = aws_data['control_tower']
                cursor.execute('''
                    INSERT INTO control_tower (version, enabled_guardrails, accounts_managed)
                    VALUES (?, ?, ?)
                ''', (ct['version'], ct['enabled_guardrails'], ct['accounts_managed']))
            
            # IAM password policy (handle absence gracefully)
            if 'iam' in aws_data and 'password_policy' in aws_data['iam']:
                policy = aws_data['iam'].get('password_policy') or {}
                # Only insert if we have at least a minimum length (policy present). Otherwise skip.
                if 'MinimumPasswordLength' in policy:
                    cursor.execute('''
                        INSERT INTO iam_password_policy 
                        (minimum_password_length, require_symbols, require_numbers, require_uppercase, 
                         require_lowercase, max_password_age, password_reuse_prevention)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        policy.get('MinimumPasswordLength'),
                        policy.get('RequireSymbols'),
                        policy.get('RequireNumbers'),
                        policy.get('RequireUppercaseCharacters'),
                        policy.get('RequireLowercaseCharacters'),
                        policy.get('MaxPasswordAge'),
                        policy.get('PasswordReusePrevention')
                    ))
            
            # IAM users (live data may not include MFA/LastLogin)
            if 'iam' in aws_data and 'users' in aws_data['iam']:
                for user in aws_data['iam']['users']:
                    username = user.get('UserName')
                    mfa_enabled = user.get('MFA', False)
                    last_login = user.get('PasswordLastUsed') or user.get('LastLogin')
                    cursor.execute('''
                        INSERT INTO iam_users (username, mfa_enabled, last_login)
                        VALUES (?, ?, ?)
                    ''', (username, mfa_enabled, last_login))
            
            # IAM roles (boundary/permissions may be absent)
            if 'iam' in aws_data and 'roles' in aws_data['iam']:
                for role in aws_data['iam']['roles']:
                    role_name = role.get('RoleName')
                    # Prefer attached policies evidence if present
                    permissions = role.get('Permissions') or role.get('AttachedPolicies') or []
                    boundary = None
                    if isinstance(role.get('PermissionsBoundary'), dict):
                        boundary = role['PermissionsBoundary'].get('PermissionsBoundaryArn')
                    cursor.execute('''
                        INSERT INTO iam_roles (role_name, permissions, boundary)
                        VALUES (?, ?, ?)
                        ON CONFLICT(role_name) DO UPDATE SET
                            permissions=excluded.permissions,
                            boundary=excluded.boundary,
                            updated_at=CURRENT_TIMESTAMP
                    ''', (role_name, json.dumps(permissions), boundary))
            
            # SSO (Identity Center) - enhanced with session management
            if 'sso' in aws_data:
                sso = aws_data['sso']
                application_count = sso.get('application_count', 0)
                mfa_types = sso.get('mfa_types', [])
                federation = sso.get('federation', False)
                enabled = sso.get('enabled', False)
                
                session_mgmt = sso.get('session_management', {})
                concurrent_limit = session_mgmt.get('concurrent_session_limit')
                session_timeout = session_mgmt.get('session_timeout')
                session_lock = session_mgmt.get('session_lock_enabled', False)
                session_termination = session_mgmt.get('session_termination_enabled', False)
                
                cursor.execute('''
                    INSERT INTO sso (application_count, mfa_types, federation, enabled, 
                                   concurrent_session_limit, session_timeout, session_lock_enabled, 
                                   session_termination_enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (application_count, json.dumps(mfa_types), federation, enabled,
                      concurrent_limit, session_timeout, session_lock, session_termination))
            
            # S3 buckets (align to live collector schema)
            if 's3' in aws_data:
                for bucket in aws_data['s3']:
                    name = bucket.get('Name') or bucket.get('Bucket')
                    encryption = bool(bucket.get('Encryption'))
                    object_lock_mode = bucket.get('ObjectLockMode')
                    retention_days = bucket.get('RetentionDays')
                    public_access_block = bucket.get('PublicAccessBlock', {})
                    kms_key_id = bucket.get('KmsKeyId')
                    cursor.execute('''
                        INSERT INTO s3_buckets 
                        (bucket_name, encryption, object_lock_mode, retention_days, public_access_block, kms_key_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(bucket_name) DO UPDATE SET 
                            encryption=excluded.encryption,
                            object_lock_mode=excluded.object_lock_mode,
                            retention_days=excluded.retention_days,
                            public_access_block=excluded.public_access_block,
                            kms_key_id=excluded.kms_key_id,
                            updated_at=CURRENT_TIMESTAMP
                    ''', (name, encryption, object_lock_mode, retention_days, json.dumps(public_access_block), kms_key_id))
            
            # KMS keys (alias optional)
            if 'kms' in aws_data:
                for key in aws_data['kms']:
                    cursor.execute('''
                        INSERT INTO kms_keys (key_id, rotation_enabled, alias)
                        VALUES (?, ?, ?)
                        ON CONFLICT(key_id) DO UPDATE SET
                            rotation_enabled=excluded.rotation_enabled,
                            alias=excluded.alias,
                            updated_at=CURRENT_TIMESTAMP
                    ''', (key.get('KeyId'), key.get('RotationEnabled'), key.get('Alias')))
            
            # CloudTrail trails (map live keys)
            if 'cloudtrail' in aws_data and 'trails' in aws_data['cloudtrail']:
                for trail in aws_data['cloudtrail']['trails']:
                    name = trail.get('Name') or trail.get('TrailARN')
                    multi_region = trail.get('MultiRegion') or trail.get('IsMultiRegionTrail')
                    log_file_validation = trail.get('LogFileValidation') or trail.get('LogFileValidationEnabled')
                    insight_selectors = trail.get('InsightSelectors', [])
                    cursor.execute('''
                        INSERT INTO cloudtrail_trails (trail_name, multi_region, log_file_validation, insight_selectors)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(trail_name) DO UPDATE SET
                            multi_region=excluded.multi_region,
                            log_file_validation=excluded.log_file_validation,
                            insight_selectors=excluded.insight_selectors,
                            updated_at=CURRENT_TIMESTAMP
                    ''', (name, multi_region, log_file_validation, json.dumps(insight_selectors)))
            
            # Config rules
            if 'config' in aws_data:
                config_data = aws_data['config']
                # Store account lockout rules
                for rule in config_data.get('account_lockout_rules', []):
                    cursor.execute('''
                        INSERT INTO config_rules (rule_name, rule_state, source_identifier, rule_type)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(rule_name) DO UPDATE SET
                            rule_state=excluded.rule_state,
                            source_identifier=excluded.source_identifier,
                            rule_type=excluded.rule_type,
                            updated_at=CURRENT_TIMESTAMP
                    ''', (rule['name'], rule['state'], rule['source'], 'account_lockout'))
                # Store password policy rules
                for rule in config_data.get('password_policy_rules', []):
                    cursor.execute('''
                        INSERT INTO config_rules (rule_name, rule_state, source_identifier, rule_type)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(rule_name) DO UPDATE SET
                            rule_state=excluded.rule_state,
                            source_identifier=excluded.source_identifier,
                            rule_type=excluded.rule_type,
                            updated_at=CURRENT_TIMESTAMP
                    ''', (rule['name'], rule['state'], rule['source'], 'password_policy'))
            
            # Config conformance packs
            if 'config' in aws_data and 'conformance_packs' in aws_data['config']:
                for pack in aws_data['config']['conformance_packs']:
                    cursor.execute('''
                        INSERT INTO config_conformance_packs (pack_name, status, failing_rules)
                        VALUES (?, ?, ?)
                        ON CONFLICT(pack_name) DO UPDATE SET
                            status=excluded.status,
                            failing_rules=excluded.failing_rules,
                            updated_at=CURRENT_TIMESTAMP
                    ''', (pack['Name'], pack['Status'], pack['FailingRules']))
            
            # GuardDuty
            if 'guardduty' in aws_data:
                gd = aws_data['guardduty']
                findings = gd.get('findings', {})
                cursor.execute('''
                    INSERT INTO guardduty (detector_count, critical_findings, high_findings, medium_findings, low_findings)
                    VALUES (?, ?, ?, ?, ?)
                ''', (gd.get('detector_count', 0), findings.get('Critical', 0), findings.get('High', 0), 
                      findings.get('Medium', 0), findings.get('Low', 0)))
            
            # Security Hub
            if 'security_hub' in aws_data:
                sh = aws_data['security_hub']
                standards = sh.get('standards', {})
                if isinstance(standards, dict):
                    for standard, status in standards.items():
                        cursor.execute('''
                            INSERT INTO security_hub (standard_name, status, open_findings)
                            VALUES (?, ?, ?)
                            ON CONFLICT(standard_name) DO UPDATE SET
                                status=excluded.status,
                                open_findings=excluded.open_findings,
                                updated_at=CURRENT_TIMESTAMP
                        ''', (standard, status, sh.get('open_findings', 0)))
            
            # Macie jobs
            if 'macie' in aws_data and 'jobs' in aws_data['macie']:
                for job in aws_data['macie']['jobs']:
                    cursor.execute('''
                        INSERT INTO macie_jobs (job_id, status, s3_buckets_scanned, sensitive_findings)
                        VALUES (?, ?, ?, ?)
                    ''', (job['JobId'], job['Status'], job.get('S3BucketsScanned'), job.get('SensitiveFindings')))
            
            # Inspector2
            if 'inspector2' in aws_data:
                insp = aws_data['inspector2']
                findings = insp['findings']
                cursor.execute('''
                    INSERT INTO inspector2 (last_run, critical_findings, high_findings, medium_findings, low_findings)
                    VALUES (?, ?, ?, ?, ?)
                ''', (insp['last_run'], findings['Critical'], findings['High'], 
                      findings['Medium'], findings['Low']))
            
            # EKS clusters
            if 'eks' in aws_data:
                for cluster in aws_data['eks']:
                    cursor.execute('''
                        INSERT INTO eks_clusters (cluster_name, oidc_enabled, irsa_enabled, k8s_version, public_access)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (cluster['Cluster'], cluster['OIDC'], cluster['IRSA'], 
                          cluster['K8sVersion'], cluster['PublicAccess']))
            
            # ECS clusters
            if 'ecs' in aws_data:
                for cluster in aws_data['ecs']:
                    cursor.execute('''
                        INSERT INTO ecs_clusters (cluster_name, fargate_tasks, ec2_tasks)
                        VALUES (?, ?, ?)
                    ''', (cluster['Cluster'], cluster['FargateTasks'], cluster['EC2Tasks']))
            
            # RDS instances
            if 'rds' in aws_data:
                for instance in aws_data['rds']:
                    cursor.execute('''
                        INSERT INTO rds_instances (instance_name, engine, encrypted, multi_az)
                        VALUES (?, ?, ?, ?)
                    ''', (instance['DBInstance'], instance['Engine'], instance['Encrypted'], instance['MultiAZ']))
            
            # DynamoDB tables
            if 'dynamodb' in aws_data:
                for table in aws_data['dynamodb']:
                    cursor.execute('''
                        INSERT INTO dynamodb_tables (table_name, encrypted, kms_key_id)
                        VALUES (?, ?, ?)
                    ''', (table['Table'], table['Encrypted'], table['KmsKeyId']))
            
            # EFS file systems
            if 'efs' in aws_data:
                for fs in aws_data['efs']:
                    cursor.execute('''
                        INSERT INTO efs_file_systems (file_system_id, encrypted, kms_key_id)
                        VALUES (?, ?, ?)
                    ''', (fs['FileSystemId'], fs['Encrypted'], fs.get('KmsKeyId')))
            
            # Backup
            if 'backup' in aws_data:
                backup = aws_data['backup']
                cursor.execute('''
                    INSERT INTO backup (vault_name, resources_protected, cross_region_copy, vault_lock)
                    VALUES (?, ?, ?, ?)
                ''', (backup['vault_name'], backup['resources_protected'], 
                      backup['cross_region_copy'], backup['vault_lock']))
            
            # VPC
            if 'vpc' in aws_data:
                vpc = aws_data['vpc']
                transit_gateway = vpc.get('transit_gateway', {})
                cursor.execute('''
                    INSERT INTO vpc (flow_logs, nat_gateways, transit_gateway_attachments)
                    VALUES (?, ?, ?)
                ''', (vpc.get('flow_logs', 0), vpc.get('nat_gateways', 0), 
                      transit_gateway.get('attachments', 0)))
            
            # Security groups
            if 'vpc' in aws_data and 'security_groups' in aws_data['vpc']:
                for sg in aws_data['vpc']['security_groups']:
                    cursor.execute('''
                        INSERT INTO security_groups (group_id, open_ports, allowed_cidrs)
                        VALUES (?, ?, ?)
                    ''', (sg['GroupId'], json.dumps(sg['OpenPorts']), json.dumps(sg['AllowedCidrs'])))
            
            # API Gateway
            if 'api_gateway' in aws_data and 'endpoints' in aws_data['api_gateway']:
                for endpoint in aws_data['api_gateway']['endpoints']:
                    cursor.execute('''
                        INSERT INTO api_gateway (stage_name, execution_logging)
                        VALUES (?, ?)
                    ''', (endpoint['Stage'], endpoint['ExecutionLogging']))
            
            # WAF
            if 'waf' in aws_data and 'web_acls' in aws_data['waf']:
                for acl in aws_data['waf']['web_acls']:
                    cursor.execute('''
                        INSERT INTO waf (web_acl_name, rules_count, blocked_count_7d)
                        VALUES (?, ?, ?)
                    ''', (acl.get('Name', ''), acl.get('Rules', 0), acl.get('BlockedCount7d', 0)))
            
            # CloudFront
            if 'cloudfront' in aws_data and 'distributions' in aws_data['cloudfront']:
                for dist in aws_data['cloudfront']['distributions']:
                    # Accept multiple possible keys from different collectors
                    tls_policy = (
                        dist.get('TLSPolicy')
                        or dist.get('MinTLSVersion')
                        or dist.get('MinimumProtocolVersion')
                        or ''
                    )
                    waf_enabled = dist.get('WAFEnabled')
                    if waf_enabled is None:
                        waf_enabled = bool(dist.get('WebACLId'))
                    cursor.execute('''
                        INSERT INTO cloudfront (distribution_id, tls_policy, waf_enabled)
                        VALUES (?, ?, ?)
                    ''', (dist.get('Id'), tls_policy, int(bool(waf_enabled))))
            
            # SSM Patch
            if 'ssm_patch' in aws_data:
                patch = aws_data['ssm_patch']
                cursor.execute('''
                    INSERT INTO ssm_patch (last_scan, pending_critical, pending_high)
                    VALUES (?, ?, ?)
                ''', (patch['last_scan'], patch['pending_critical'], patch['pending_high']))
            
            # EventBridge rules
            if 'eventbridge' in aws_data and 'rules' in aws_data['eventbridge']:
                for rule in aws_data['eventbridge']['rules']:
                    cursor.execute('''
                        INSERT INTO eventbridge_rules (rule_name, target, state)
                        VALUES (?, ?, ?)
                    ''', (rule['Name'], rule['Target'], rule['State']))
            
            # Detective
            if 'detective' in aws_data:
                det = aws_data['detective']
                cursor.execute('''
                    INSERT INTO detective (graph_enabled, member_accounts)
                    VALUES (?, ?)
                ''', (det['graph_enabled'], det['member_accounts']))
            
            # CodeBuild
            if 'codebuild' in aws_data:
                cb = aws_data['codebuild']
                cursor.execute('''
                    INSERT INTO codebuild (projects_count, failed_builds_last7d, passed_builds)
                    VALUES (?, ?, ?)
                ''', (cb['projects'], cb['failed_builds_last7d'], cb['passed']))
            
            # CodePipeline
            if 'codepipeline' in aws_data:
                cp = aws_data['codepipeline']
                cursor.execute('''
                    INSERT INTO codepipeline (pipelines_count, failed_executions)
                    VALUES (?, ?)
                ''', (cp['pipelines'], cp['failed_executions']))
            
            # Lambda
            if 'lambda' in aws_data:
                lambda_data = aws_data['lambda']
                cursor.execute('''
                    INSERT INTO lambda (functions_count, unreserved_concurrent_executions)
                    VALUES (?, ?)
                ''', (lambda_data['functions'], lambda_data['unreserved_concurrent_executions']))
            
            # CloudWatch
            if 'cloudwatch' in aws_data:
                cw = aws_data['cloudwatch']
                cursor.execute('''
                    INSERT INTO cloudwatch (alarms_count, metrics_collected)
                    VALUES (?, ?)
                ''', (cw['alarms'], cw['metrics_collected']))
            
            # Route53
            if 'route53' in aws_data:
                r53 = aws_data['route53']
                cursor.execute('''
                    INSERT INTO route53 (hosted_zones, health_checks)
                    VALUES (?, ?)
                ''', (r53['hosted_zones'], r53['health_checks']))
            
            # Direct Connect
            if 'direct_connect' in aws_data:
                dc = aws_data['direct_connect']
                cursor.execute('''
                    INSERT INTO direct_connect (connections, locations)
                    VALUES (?, ?)
                ''', (dc['connections'], json.dumps(dc['locations'])))
            
            # VPN
            if 'vpn' in aws_data:
                vpn = aws_data['vpn']
                cursor.execute('''
                    INSERT INTO vpn (client_vpn_endpoints, active_sessions)
                    VALUES (?, ?)
                ''', (vpn['client_vpn_endpoints'], vpn['active_sessions']))
            
            conn.commit()
            print("AWS data loaded successfully into database")
            
        except Exception as e:
            conn.rollback()
            print(f"Error loading AWS data: {e}")
            raise
        finally:
            conn.close()
    
    def get_aws_data(self) -> Dict[str, Any]:
        """Retrieve all AWS data from database - only real collected data"""
        # This method is deprecated - use load_aws_data_from_db() instead
        # which only returns real data from the database
        return self.load_aws_data_from_db()

    def get_raw_aws_data(self) -> Dict[str, Any]:
        """Get the raw collected AWS data from the most recent collection"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get the most recent collection timestamp
        cursor.execute('SELECT MAX(timestamp) FROM aws_collections')
        result = cursor.fetchone()
        if not result or not result[0]:
            raise Exception("No AWS data found")
        
        latest_timestamp = result[0]
        
        # Get the raw data for that timestamp
        cursor.execute('SELECT data FROM aws_collections WHERE timestamp = ?', (latest_timestamp,))
        result = cursor.fetchone()
        if not result:
            raise Exception("No raw AWS data found")
        
        return json.loads(result[0])
    
    def get_service_data(self, service_name: str) -> List[Dict[str, Any]]:
        """Get data for a specific service"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT * FROM {service_name}')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting {service_name} data: {e}")
            return []
        finally:
            conn.close()
    
    def store_fedramp_template(self, template_name: str, template_type: str, file_path: str) -> bool:
        """Store FedRAMP template in database"""
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            file_size = len(file_content)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Insert or update template
            cursor.execute('''
                INSERT OR REPLACE INTO fedramp_templates 
                (template_name, template_type, file_path, file_content, file_size, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (template_name, template_type, file_path, file_content, file_size))
            
            conn.commit()
            conn.close()
            
            print(f"✅ FedRAMP template '{template_name}' stored successfully ({file_size} bytes)")
            return True
            
        except Exception as e:
            print(f"❌ Error storing FedRAMP template: {e}")
            return False
    
    def get_fedramp_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve FedRAMP template from database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT template_name, template_type, file_path, file_content, file_size, upload_date
                FROM fedramp_templates 
                WHERE template_name = ?
            ''', (template_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'template_name': row[0],
                    'template_type': row[1],
                    'file_path': row[2],
                    'file_content': row[3],
                    'file_size': row[4],
                    'upload_date': row[5]
                }
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving FedRAMP template: {e}")
            return None
    
    def list_fedramp_templates(self) -> List[Dict[str, Any]]:
        """List all stored FedRAMP templates"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT template_name, template_type, file_size, upload_date
                FROM fedramp_templates 
                ORDER BY upload_date DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ Error listing FedRAMP templates: {e}")
            return []
    
    def load_aws_data_from_db(self) -> Dict[str, Any]:
        """Load AWS data from database in the format expected by analysis engines."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        aws_data = {}
        
        # Load IAM data
        cursor.execute('SELECT username, mfa_enabled, last_login FROM iam_users')
        users = []
        for row in cursor.fetchall():
            users.append({
                'UserName': row[0],  # Match expected field name
                'MFA': bool(row[1]),  # Match expected field name
                'PasswordLastUsed': row[2],  # Match expected field name
                'access_level': 'standard'  # Default
            })
        
        cursor.execute('SELECT role_name, permissions, boundary FROM iam_roles')
        roles = []
        for row in cursor.fetchall():
            roles.append({
                'RoleName': row[0],  # Match expected field name
                'permissions': row[1],
                'boundary': row[2]
            })
        
        # Load password policy - only if data exists
        cursor.execute('SELECT minimum_password_length, require_symbols, require_numbers, require_uppercase, require_lowercase, max_password_age, password_reuse_prevention FROM iam_password_policy')
        password_policy_row = cursor.fetchone()
        password_policy = {}  # Empty if no data
        if password_policy_row:
            password_policy = {
                'MinimumPasswordLength': password_policy_row[0] or 8,
                'RequireSymbols': bool(password_policy_row[1]),
                'RequireNumbers': bool(password_policy_row[2]),
                'RequireUppercaseCharacters': bool(password_policy_row[3]),
                'RequireLowercaseCharacters': bool(password_policy_row[4]),
                'MaxPasswordAge': password_policy_row[5],
                'PasswordReusePrevention': password_policy_row[6]
            }
        
        aws_data['iam'] = {
            'users': users,
            'roles': roles,
            'password_policy': password_policy
        }
        
        # Load S3 data
        cursor.execute('SELECT bucket_name, encryption, public_access_block, object_lock_mode, retention_days FROM s3_buckets')
        buckets = []
        object_lock_buckets = 0
        for row in cursor.fetchall():
            bucket_data = {
                'bucket_name': row[0],
                'encryption_enabled': bool(row[1]),
                'public_access': not bool(row[2]),  # public_access_block is inverse
                'object_lock_mode': row[3],
                'retention_days': row[4]
            }
            buckets.append(bucket_data)
            if row[3]:  # ObjectLockMode is not None
                object_lock_buckets += 1
        
        aws_data['s3'] = {
            'buckets': buckets,
            'object_lock_enabled': object_lock_buckets > 0,
            'object_lock_buckets': object_lock_buckets
        }
        
        # Load KMS data
        cursor.execute('SELECT key_id, rotation_enabled FROM kms_keys')
        keys = []
        for row in cursor.fetchall():
            keys.append({
                'key_id': row[0],
                'rotation_enabled': bool(row[1])
            })
        
        aws_data['kms'] = {'keys': keys}
        
        # Load VPC data
        cursor.execute('SELECT flow_logs, nat_gateways FROM vpc LIMIT 1')
        vpc_row = cursor.fetchone()
        if vpc_row:
            aws_data['vpc'] = {
                'flow_logs': vpc_row[0],
                'nat_gateways': vpc_row[1]
            }
        
        # Load WAF data
        cursor.execute('SELECT web_acl_name, rules_count FROM waf')
        web_acls = []
        for row in cursor.fetchall():
            web_acls.append({
                'web_acl_name': row[0],
                'rules_count': row[1]
            })
        
        aws_data['waf'] = {'web_acls': web_acls}
        
        # Load CloudTrail data
        cursor.execute('SELECT trail_name FROM cloudtrail_trails')
        trails = [row[0] for row in cursor.fetchall()]
        aws_data['cloudtrail'] = {'trails': trails}
        
        # Load GuardDuty data
        cursor.execute('SELECT detector_count FROM guardduty LIMIT 1')
        gd_row = cursor.fetchone()
        if gd_row:
            aws_data['guardduty'] = {'detector_count': gd_row[0]}
        
        # Load Security Hub data
        cursor.execute('SELECT COUNT(*) FROM security_hub')
        sh_count = cursor.fetchone()[0]
        cursor.execute('SELECT standard_name, status, open_findings FROM security_hub')
        standards = {}
        total_findings = 0
        for row in cursor.fetchall():
            standards[row[0]] = row[1]
            total_findings += row[2] or 0
        aws_data['security_hub'] = {
            'enabled': sh_count > 0,
            'standards': standards,
            'open_findings': total_findings
        }
        
        # Load Config data
        cursor.execute('SELECT rule_name, rule_state, rule_type FROM config_rules')
        account_lockout_rules = []
        password_policy_rules = []
        for row in cursor.fetchall():
            rule_data = {'name': row[0], 'state': row[1]}
            if row[2] == 'account_lockout':
                account_lockout_rules.append(rule_data)
            elif row[2] == 'password_policy':
                password_policy_rules.append(rule_data)
        
        aws_data['config'] = {
            'account_lockout_rules': account_lockout_rules,
            'password_policy_rules': password_policy_rules,
            'has_account_lockout_protection': len(account_lockout_rules) > 0
        }
        
        # Load SSO data - only if data exists
        cursor.execute('SELECT enabled, concurrent_session_limit, session_timeout, session_lock_enabled, session_termination_enabled FROM sso LIMIT 1')
        sso_row = cursor.fetchone()
        if sso_row:
            aws_data['sso'] = {
                'enabled': bool(sso_row[0]),
                'session_management': {
                    'concurrent_session_limit': sso_row[1],
                    'session_timeout': sso_row[2],
                    'session_lock_enabled': bool(sso_row[3]),
                    'session_termination_enabled': bool(sso_row[4])
                }
            }
        # No default SSO data - only return if real data exists
        
        conn.close()
        return aws_data
    
    def store_policy(self, policy_data: Dict[str, Any]) -> bool:
        """Store uploaded policy in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO policies (
                    id, name, filename, content, controls_mapped, last_analyzed,
                    status, type, summary, reasons, missing, recommendations, citations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                policy_data['id'],
                policy_data['name'],
                policy_data.get('filename'),
                policy_data.get('content'),
                json.dumps(policy_data.get('controlsMapped', [])),
                policy_data.get('lastAnalyzed'),
                policy_data.get('status'),
                policy_data.get('type'),
                policy_data.get('summary'),
                json.dumps(policy_data.get('reasons', [])),
                json.dumps(policy_data.get('missing', [])),
                json.dumps(policy_data.get('recommendations', [])),
                json.dumps(policy_data.get('citations', []))
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error storing policy: {e}")
            return False
        finally:
            conn.close()
    
    def get_policies(self) -> List[Dict[str, Any]]:
        """Retrieve all stored policies"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, name, filename, controls_mapped, last_analyzed,
                       status, type, summary, reasons, missing, recommendations, citations
                FROM policies ORDER BY created_at DESC
            ''')
            
            policies = []
            for row in cursor.fetchall():
                policies.append({
                    'id': row[0],
                    'name': row[1],
                    'filename': row[2],
                    'controlsMapped': json.loads(row[3]) if row[3] else [],
                    'lastAnalyzed': row[4],
                    'status': row[5],
                    'type': row[6],
                    'summary': row[7],
                    'reasons': json.loads(row[8]) if row[8] else [],
                    'missing': json.loads(row[9]) if row[9] else [],
                    'recommendations': json.loads(row[10]) if row[10] else [],
                    'citations': json.loads(row[11]) if row[11] else []
                })
            return policies
        except Exception as e:
            print(f"Error retrieving policies: {e}")
            return []
        finally:
            conn.close()

# Global database instance
db = ProTechtDatabase() 