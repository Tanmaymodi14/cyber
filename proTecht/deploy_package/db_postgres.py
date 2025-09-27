#!/usr/bin/env python3
"""
PostgreSQL adapter for proTecht database operations.

Implements a compatible subset of the SQLite-backed ProTechtDatabase API using psycopg.
Selection is controlled via the DB_URL environment variable in api_server.py.

Notes:
- Uses synchronous psycopg client for simplicity and compatibility with existing code paths
- DDL is adjusted for PostgreSQL (SERIAL PK, BYTEA instead of BLOB, explicit UNIQUE)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import psycopg


def _get_db_url() -> str:
    url = os.environ.get("DB_URL")
    if not url:
        raise RuntimeError("DB_URL is not set; cannot initialize PostgreSQL database")
    return url


class ProTechtDatabasePG:
    """PostgreSQL-backed database implementation compatible with ProTechtDatabase API."""

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or _get_db_url()
        # Enable autocommit connections (DDL without transactions for init)
        self._conn = None
        self.init_database()

    def get_connection(self):
        if self._conn is None or self._conn.closed:
            self._conn = psycopg.connect(self.db_url, autocommit=False)
        return self._conn

    def init_database(self) -> None:
        conn = psycopg.connect(self.db_url, autocommit=True)
        cur = conn.cursor()
        # Minimal helper to execute DDL
        def ddl(sql: str) -> None:
            cur.execute(sql)

        # Core tables (PostgreSQL types)
        ddl("""
        CREATE TABLE IF NOT EXISTS account_metadata (
            id SERIAL PRIMARY KEY,
            org_id TEXT UNIQUE,
            master_payer_id TEXT,
            regions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS control_tower (
            id SERIAL PRIMARY KEY,
            version TEXT,
            enabled_guardrails INTEGER,
            accounts_managed INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS iam_password_policy (
            id SERIAL PRIMARY KEY,
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
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS iam_users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            mfa_enabled BOOLEAN,
            last_login TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS iam_roles (
            id SERIAL PRIMARY KEY,
            role_name TEXT UNIQUE,
            permissions TEXT,
            boundary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS sso (
            id SERIAL PRIMARY KEY,
            application_count INTEGER,
            mfa_types TEXT,
            federation TEXT,
            enabled BOOLEAN,
            concurrent_session_limit TEXT,
            session_timeout TEXT,
            session_lock_enabled BOOLEAN,
            session_termination_enabled BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS s3_buckets (
            id SERIAL PRIMARY KEY,
            bucket_name TEXT UNIQUE,
            encryption BOOLEAN,
            object_lock_mode TEXT,
            retention_days INTEGER,
            public_access_block TEXT,
            kms_key_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        # Migration: ensure public_access_block is TEXT (not BOOLEAN)
        try:
            cur.execute(
                "ALTER TABLE s3_buckets ALTER COLUMN public_access_block TYPE TEXT USING public_access_block::text"
            )
        except Exception:
            pass

        ddl("""
        CREATE TABLE IF NOT EXISTS kms_keys (
            id SERIAL PRIMARY KEY,
            key_id TEXT UNIQUE,
            rotation_enabled BOOLEAN,
            alias TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS cloudtrail_trails (
            id SERIAL PRIMARY KEY,
            trail_name TEXT UNIQUE,
            multi_region BOOLEAN,
            log_file_validation BOOLEAN,
            insight_selectors TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS config_rules (
            id SERIAL PRIMARY KEY,
            rule_name TEXT UNIQUE,
            compliance_type TEXT,
            rule_state TEXT,
            source_identifier TEXT,
            rule_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS config_conformance_packs (
            id SERIAL PRIMARY KEY,
            pack_name TEXT UNIQUE,
            status TEXT,
            failing_rules INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS guardduty (
            id SERIAL PRIMARY KEY,
            detector_count INTEGER,
            critical_findings INTEGER,
            high_findings INTEGER,
            medium_findings INTEGER,
            low_findings INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS security_hub (
            id SERIAL PRIMARY KEY,
            standard_name TEXT UNIQUE,
            status TEXT,
            open_findings INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS macie_jobs (
            id SERIAL PRIMARY KEY,
            job_id TEXT UNIQUE,
            status TEXT,
            s3_buckets_scanned INTEGER,
            sensitive_findings INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS inspector2 (
            id SERIAL PRIMARY KEY,
            last_run TEXT,
            critical_findings INTEGER,
            high_findings INTEGER,
            medium_findings INTEGER,
            low_findings INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS eks_clusters (
            id SERIAL PRIMARY KEY,
            cluster_name TEXT UNIQUE,
            oidc_enabled BOOLEAN,
            irsa_enabled BOOLEAN,
            k8s_version TEXT,
            public_access BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS ecs_clusters (
            id SERIAL PRIMARY KEY,
            cluster_name TEXT UNIQUE,
            fargate_tasks INTEGER,
            ec2_tasks INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS rds_instances (
            id SERIAL PRIMARY KEY,
            instance_name TEXT UNIQUE,
            engine TEXT,
            encrypted BOOLEAN,
            multi_az BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS dynamodb_tables (
            id SERIAL PRIMARY KEY,
            table_name TEXT UNIQUE,
            encrypted BOOLEAN,
            kms_key_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS efs_file_systems (
            id SERIAL PRIMARY KEY,
            file_system_id TEXT UNIQUE,
            encrypted BOOLEAN,
            kms_key_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS backup (
            id SERIAL PRIMARY KEY,
            vault_name TEXT UNIQUE,
            resources_protected INTEGER,
            cross_region_copy BOOLEAN,
            vault_lock TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS vpc (
            id SERIAL PRIMARY KEY,
            flow_logs BOOLEAN,
            nat_gateways INTEGER,
            transit_gateway_attachments INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS security_groups (
            id SERIAL PRIMARY KEY,
            group_id TEXT UNIQUE,
            open_ports TEXT,
            allowed_cidrs TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS api_gateway (
            id SERIAL PRIMARY KEY,
            stage_name TEXT UNIQUE,
            execution_logging BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS waf (
            id SERIAL PRIMARY KEY,
            web_acl_name TEXT UNIQUE,
            rules_count INTEGER,
            blocked_count_7d INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS cloudfront (
            id SERIAL PRIMARY KEY,
            distribution_id TEXT UNIQUE,
            tls_policy TEXT,
            waf_enabled BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS ssm_patch (
            id SERIAL PRIMARY KEY,
            last_scan TEXT,
            pending_critical INTEGER,
            pending_high INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS eventbridge_rules (
            id SERIAL PRIMARY KEY,
            rule_name TEXT UNIQUE,
            target TEXT,
            state TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS detective (
            id SERIAL PRIMARY KEY,
            graph_enabled BOOLEAN,
            member_accounts INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS codebuild (
            id SERIAL PRIMARY KEY,
            projects_count INTEGER,
            failed_builds_last7d INTEGER,
            passed_builds INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS codepipeline (
            id SERIAL PRIMARY KEY,
            pipelines_count INTEGER,
            failed_executions INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS lambda (
            id SERIAL PRIMARY KEY,
            functions_count INTEGER,
            unreserved_concurrent_executions INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS cloudwatch (
            id SERIAL PRIMARY KEY,
            alarms_count INTEGER,
            metrics_collected INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS route53 (
            id SERIAL PRIMARY KEY,
            hosted_zones INTEGER,
            health_checks INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS direct_connect (
            id SERIAL PRIMARY KEY,
            connections INTEGER,
            locations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS vpn (
            id SERIAL PRIMARY KEY,
            client_vpn_endpoints INTEGER,
            active_sessions INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
        CREATE TABLE IF NOT EXISTS fedramp_templates (
            id SERIAL PRIMARY KEY,
            template_name TEXT UNIQUE,
            template_type TEXT,
            file_path TEXT,
            file_content BYTEA,
            file_size INTEGER,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ddl("""
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
        """)

        cur.close()
        conn.close()

    def clear_all_data(self) -> None:
        conn = self.get_connection()
        cur = conn.cursor()
        tables = [
            'account_metadata', 'control_tower', 'iam_password_policy', 'iam_users', 'iam_roles',
            'sso', 's3_buckets', 'kms_keys', 'cloudtrail_trails', 'config_rules', 'config_conformance_packs',
            'guardduty', 'security_hub', 'macie_jobs', 'inspector2', 'eks_clusters', 'ecs_clusters',
            'rds_instances', 'dynamodb_tables', 'efs_file_systems', 'backup', 'vpc', 'security_groups',
            'api_gateway', 'waf', 'cloudfront', 'ssm_patch', 'eventbridge_rules', 'detective',
            'codebuild', 'codepipeline', 'lambda', 'cloudwatch', 'route53', 'direct_connect', 'vpn'
        ]
        for t in tables:
            cur.execute(f"DELETE FROM {t}")
        conn.commit()

    def load_aws_data(self, aws_data: Dict[str, Any]) -> None:
        self.clear_all_data()
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            if 'account_metadata' in aws_data:
                m = aws_data['account_metadata']
                cur.execute(
                    "INSERT INTO account_metadata (org_id, master_payer_id, regions) VALUES (%s,%s,%s)",
                    (m.get('org_id'), m.get('master_payer_id'), json.dumps(m.get('regions'))),
                )

            if 'control_tower' in aws_data:
                ct = aws_data['control_tower']
                cur.execute(
                    "INSERT INTO control_tower (version, enabled_guardrails, accounts_managed) VALUES (%s,%s,%s)",
                    (ct.get('version'), ct.get('enabled_guardrails'), ct.get('accounts_managed')),
                )

            if 'iam' in aws_data and 'password_policy' in aws_data['iam']:
                p = aws_data['iam'].get('password_policy') or {}
                if 'MinimumPasswordLength' in p:
                    cur.execute(
                        """
                        INSERT INTO iam_password_policy (
                          minimum_password_length, require_symbols, require_numbers, require_uppercase,
                          require_lowercase, max_password_age, password_reuse_prevention
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            p.get('MinimumPasswordLength'), p.get('RequireSymbols'), p.get('RequireNumbers'),
                            p.get('RequireUppercaseCharacters'), p.get('RequireLowercaseCharacters'),
                            p.get('MaxPasswordAge'), p.get('PasswordReusePrevention'),
                        ),
                    )

            if 'iam' in aws_data and 'users' in aws_data['iam']:
                for u in aws_data['iam']['users']:
                    cur.execute(
                        "INSERT INTO iam_users (username, mfa_enabled, last_login) VALUES (%s,%s,%s)",
                        (u.get('UserName'), u.get('MFA', False), u.get('PasswordLastUsed') or u.get('LastLogin')),
                    )

            if 'iam' in aws_data and 'roles' in aws_data['iam']:
                for r in aws_data['iam']['roles']:
                    permissions = r.get('Permissions') or r.get('AttachedPolicies') or []
                    boundary = None
                    if isinstance(r.get('PermissionsBoundary'), dict):
                        boundary = r['PermissionsBoundary'].get('PermissionsBoundaryArn')
                    cur.execute(
                        """
                        INSERT INTO iam_roles (role_name, permissions, boundary) VALUES (%s,%s,%s)
                        ON CONFLICT (role_name) DO UPDATE SET permissions=EXCLUDED.permissions, boundary=EXCLUDED.boundary, updated_at=CURRENT_TIMESTAMP
                        """,
                        (r.get('RoleName'), json.dumps(permissions), boundary),
                    )

            if 's3' in aws_data:
                for b in aws_data['s3']:
                    name = b.get('Name') or b.get('Bucket')
                    public_access_block = b.get('PublicAccessBlock', {})
                    cur.execute(
                        """
                        INSERT INTO s3_buckets (bucket_name, encryption, object_lock_mode, retention_days, public_access_block, kms_key_id)
                        VALUES (%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (bucket_name) DO UPDATE SET
                          encryption=EXCLUDED.encryption,
                          object_lock_mode=EXCLUDED.object_lock_mode,
                          retention_days=EXCLUDED.retention_days,
                          public_access_block=EXCLUDED.public_access_block,
                          kms_key_id=EXCLUDED.kms_key_id,
                          updated_at=CURRENT_TIMESTAMP
                        """,
                        (
                            name, bool(b.get('Encryption')), b.get('ObjectLockMode'), b.get('RetentionDays'),
                            json.dumps(public_access_block), b.get('KmsKeyId')
                        ),
                    )

            if 'kms' in aws_data:
                for k in aws_data['kms']:
                    cur.execute(
                        """
                        INSERT INTO kms_keys (key_id, rotation_enabled, alias) VALUES (%s,%s,%s)
                        ON CONFLICT (key_id) DO UPDATE SET rotation_enabled=EXCLUDED.rotation_enabled, alias=EXCLUDED.alias, updated_at=CURRENT_TIMESTAMP
                        """,
                        (k.get('KeyId'), k.get('RotationEnabled'), k.get('Alias')),
                    )

            if 'cloudtrail' in aws_data and 'trails' in aws_data['cloudtrail']:
                for t in aws_data['cloudtrail']['trails']:
                    name = t.get('Name') or t.get('TrailARN')
                    multi_region = t.get('MultiRegion') or t.get('IsMultiRegionTrail')
                    log_file_validation = t.get('LogFileValidation') or t.get('LogFileValidationEnabled')
                    cur.execute(
                        """
                        INSERT INTO cloudtrail_trails (trail_name, multi_region, log_file_validation, insight_selectors)
                        VALUES (%s,%s,%s,%s)
                        ON CONFLICT (trail_name) DO UPDATE SET multi_region=EXCLUDED.multi_region, log_file_validation=EXCLUDED.log_file_validation, insight_selectors=EXCLUDED.insight_selectors, updated_at=CURRENT_TIMESTAMP
                        """,
                        (name, multi_region, log_file_validation, json.dumps(t.get('InsightSelectors', []))),
                    )

            if 'config' in aws_data:
                cfg = aws_data['config']
                for rule in cfg.get('account_lockout_rules', []):
                    cur.execute(
                        """
                        INSERT INTO config_rules (rule_name, rule_state, source_identifier, rule_type)
                        VALUES (%s,%s,%s,%s)
                        ON CONFLICT (rule_name) DO UPDATE SET rule_state=EXCLUDED.rule_state, source_identifier=EXCLUDED.source_identifier, rule_type=EXCLUDED.rule_type, updated_at=CURRENT_TIMESTAMP
                        """,
                        (rule['name'], rule['state'], rule.get('source'), 'account_lockout'),
                    )
                for rule in cfg.get('password_policy_rules', []):
                    cur.execute(
                        """
                        INSERT INTO config_rules (rule_name, rule_state, source_identifier, rule_type)
                        VALUES (%s,%s,%s,%s)
                        ON CONFLICT (rule_name) DO UPDATE SET rule_state=EXCLUDED.rule_state, source_identifier=EXCLUDED.source_identifier, rule_type=EXCLUDED.rule_type, updated_at=CURRENT_TIMESTAMP
                        """,
                        (rule['name'], rule['state'], rule.get('source'), 'password_policy'),
                    )

            if 'config' in aws_data and 'conformance_packs' in aws_data['config']:
                for pack in aws_data['config']['conformance_packs']:
                    cur.execute(
                        """
                        INSERT INTO config_conformance_packs (pack_name, status, failing_rules)
                        VALUES (%s,%s,%s)
                        ON CONFLICT (pack_name) DO UPDATE SET status=EXCLUDED.status, failing_rules=EXCLUDED.failing_rules, updated_at=CURRENT_TIMESTAMP
                        """,
                        (pack['Name'], pack['Status'], pack['FailingRules']),
                    )

            if 'guardduty' in aws_data:
                gd = aws_data['guardduty']
                f = gd.get('findings', {})
                cur.execute(
                    "INSERT INTO guardduty (detector_count, critical_findings, high_findings, medium_findings, low_findings) VALUES (%s,%s,%s,%s,%s)",
                    (gd.get('detector_count', 0), f.get('Critical', 0), f.get('High', 0), f.get('Medium', 0), f.get('Low', 0)),
                )

            if 'security_hub' in aws_data:
                sh = aws_data['security_hub']
                standards = sh.get('standards', {})
                if isinstance(standards, dict):
                    for standard, status in standards.items():
                        cur.execute(
                            """
                            INSERT INTO security_hub (standard_name, status, open_findings) VALUES (%s,%s,%s)
                            ON CONFLICT (standard_name) DO UPDATE SET status=EXCLUDED.status, open_findings=EXCLUDED.open_findings, updated_at=CURRENT_TIMESTAMP
                            """,
                            (standard, status, sh.get('open_findings', 0)),
                        )

            if 'macie' in aws_data and 'jobs' in aws_data['macie']:
                for job in aws_data['macie']['jobs']:
                    cur.execute(
                        "INSERT INTO macie_jobs (job_id, status, s3_buckets_scanned, sensitive_findings) VALUES (%s,%s,%s,%s)",
                        (job['JobId'], job['Status'], job.get('S3BucketsScanned'), job.get('SensitiveFindings')),
                    )

            if 'inspector2' in aws_data:
                insp = aws_data['inspector2']
                f = insp['findings']
                cur.execute(
                    "INSERT INTO inspector2 (last_run, critical_findings, high_findings, medium_findings, low_findings) VALUES (%s,%s,%s,%s,%s)",
                    (insp['last_run'], f['Critical'], f['High'], f['Medium'], f['Low']),
                )

            if 'eks' in aws_data:
                for cluster in aws_data['eks']:
                    cur.execute(
                        "INSERT INTO eks_clusters (cluster_name, oidc_enabled, irsa_enabled, k8s_version, public_access) VALUES (%s,%s,%s,%s,%s)",
                        (cluster['Cluster'], cluster['OIDC'], cluster['IRSA'], cluster['K8sVersion'], cluster['PublicAccess']),
                    )

            if 'ecs' in aws_data:
                for cluster in aws_data['ecs']:
                    cur.execute(
                        "INSERT INTO ecs_clusters (cluster_name, fargate_tasks, ec2_tasks) VALUES (%s,%s,%s)",
                        (cluster['Cluster'], cluster['FargateTasks'], cluster['EC2Tasks']),
                    )

            if 'rds' in aws_data:
                for inst in aws_data['rds']:
                    cur.execute(
                        "INSERT INTO rds_instances (instance_name, engine, encrypted, multi_az) VALUES (%s,%s,%s,%s)",
                        (inst['DBInstance'], inst['Engine'], inst['Encrypted'], inst['MultiAZ']),
                    )

            if 'dynamodb' in aws_data:
                for t in aws_data['dynamodb']:
                    cur.execute(
                        "INSERT INTO dynamodb_tables (table_name, encrypted, kms_key_id) VALUES (%s,%s,%s)",
                        (t['Table'], t['Encrypted'], t.get('KmsKeyId')),
                    )

            if 'efs' in aws_data:
                for fs in aws_data['efs']:
                    cur.execute(
                        "INSERT INTO efs_file_systems (file_system_id, encrypted, kms_key_id) VALUES (%s,%s,%s)",
                        (fs['FileSystemId'], fs['Encrypted'], fs.get('KmsKeyId')),
                    )

            if 'backup' in aws_data:
                b = aws_data['backup']
                cur.execute(
                    "INSERT INTO backup (vault_name, resources_protected, cross_region_copy, vault_lock) VALUES (%s,%s,%s,%s)",
                    (b['vault_name'], b['resources_protected'], b['cross_region_copy'], b['vault_lock']),
                )

            if 'vpc' in aws_data:
                v = aws_data['vpc']
                tg = v.get('transit_gateway', {})
                cur.execute(
                    "INSERT INTO vpc (flow_logs, nat_gateways, transit_gateway_attachments) VALUES (%s,%s,%s)",
                    (v.get('flow_logs', 0), v.get('nat_gateways', 0), tg.get('attachments', 0)),
                )
                for sg in v.get('security_groups', []) or []:
                    cur.execute(
                        "INSERT INTO security_groups (group_id, open_ports, allowed_cidrs) VALUES (%s,%s,%s)",
                        (sg['GroupId'], json.dumps(sg['OpenPorts']), json.dumps(sg['AllowedCidrs'])),
                    )

            if 'api_gateway' in aws_data and 'endpoints' in aws_data['api_gateway']:
                for ep in aws_data['api_gateway']['endpoints']:
                    cur.execute(
                        "INSERT INTO api_gateway (stage_name, execution_logging) VALUES (%s,%s)",
                        (ep['Stage'], ep['ExecutionLogging']),
                    )

            if 'waf' in aws_data and 'web_acls' in aws_data['waf']:
                for acl in aws_data['waf']['web_acls']:
                    cur.execute(
                        "INSERT INTO waf (web_acl_name, rules_count, blocked_count_7d) VALUES (%s,%s,%s)",
                        (acl.get('Name', ''), acl.get('Rules', 0), acl.get('BlockedCount7d', 0)),
                    )

            if 'cloudfront' in aws_data and 'distributions' in aws_data['cloudfront']:
                for dist in aws_data['cloudfront']['distributions']:
                    tls_policy = dist.get('TLSPolicy') or dist.get('MinTLSVersion') or dist.get('MinimumProtocolVersion') or ''
                    waf_enabled = dist.get('WAFEnabled')
                    if waf_enabled is None:
                        waf_enabled = bool(dist.get('WebACLId'))
                    # Ensure boolean type is passed to PostgreSQL
                    cur.execute(
                        "INSERT INTO cloudfront (distribution_id, tls_policy, waf_enabled) VALUES (%s,%s,%s)",
                        (dist.get('Id'), tls_policy, bool(waf_enabled)),
                    )

            if 'ssm_patch' in aws_data:
                p = aws_data['ssm_patch']
                cur.execute(
                    "INSERT INTO ssm_patch (last_scan, pending_critical, pending_high) VALUES (%s,%s,%s)",
                    (p['last_scan'], p['pending_critical'], p['pending_high']),
                )

            if 'eventbridge' in aws_data and 'rules' in aws_data['eventbridge']:
                for r in aws_data['eventbridge']['rules']:
                    cur.execute(
                        "INSERT INTO eventbridge_rules (rule_name, target, state) VALUES (%s,%s,%s)",
                        (r['Name'], r['Target'], r['State']),
                    )

            if 'detective' in aws_data:
                d = aws_data['detective']
                cur.execute(
                    "INSERT INTO detective (graph_enabled, member_accounts) VALUES (%s,%s)",
                    (d['graph_enabled'], d['member_accounts']),
                )

            if 'codebuild' in aws_data:
                cb = aws_data['codebuild']
                cur.execute(
                    "INSERT INTO codebuild (projects_count, failed_builds_last7d, passed_builds) VALUES (%s,%s,%s)",
                    (cb['projects'], cb['failed_builds_last7d'], cb['passed']),
                )

            if 'codepipeline' in aws_data:
                cp = aws_data['codepipeline']
                cur.execute(
                    "INSERT INTO codepipeline (pipelines_count, failed_executions) VALUES (%s,%s)",
                    (cp['pipelines'], cp['failed_executions']),
                )

            if 'lambda' in aws_data:
                l = aws_data['lambda']
                cur.execute(
                    "INSERT INTO lambda (functions_count, unreserved_concurrent_executions) VALUES (%s,%s)",
                    (l['functions'], l['unreserved_concurrent_executions']),
                )

            if 'cloudwatch' in aws_data:
                cw = aws_data['cloudwatch']
                cur.execute(
                    "INSERT INTO cloudwatch (alarms_count, metrics_collected) VALUES (%s,%s)",
                    (cw['alarms'], cw['metrics_collected']),
                )

            if 'route53' in aws_data:
                r53 = aws_data['route53']
                cur.execute(
                    "INSERT INTO route53 (hosted_zones, health_checks) VALUES (%s,%s)",
                    (r53['hosted_zones'], r53['health_checks']),
                )

            if 'direct_connect' in aws_data:
                dc = aws_data['direct_connect']
                cur.execute(
                    "INSERT INTO direct_connect (connections, locations) VALUES (%s,%s)",
                    (dc['connections'], json.dumps(dc['locations'])),
                )

            if 'vpn' in aws_data:
                vpn = aws_data['vpn']
                cur.execute(
                    "INSERT INTO vpn (client_vpn_endpoints, active_sessions) VALUES (%s,%s)",
                    (vpn['client_vpn_endpoints'], vpn['active_sessions']),
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def load_aws_data_from_db(self) -> Dict[str, Any]:
        conn = self.get_connection()
        cur = conn.cursor()
        aws_data: Dict[str, Any] = {}

        # IAM users
        cur.execute("SELECT username, mfa_enabled, last_login FROM iam_users")
        users = [{
            'UserName': r[0],
            'MFA': bool(r[1]),
            'PasswordLastUsed': r[2],
            'access_level': 'standard',
        } for r in cur.fetchall()]

        cur.execute("SELECT role_name, permissions, boundary FROM iam_roles")
        roles = [{
            'RoleName': r[0],
            'permissions': r[1],
            'boundary': r[2],
        } for r in cur.fetchall()]

        cur.execute("SELECT minimum_password_length, require_symbols, require_numbers, require_uppercase, require_lowercase, max_password_age, password_reuse_prevention FROM iam_password_policy")
        row = cur.fetchone()
        password_policy = {}
        if row:
            password_policy = {
                'MinimumPasswordLength': row[0] or 8,
                'RequireSymbols': bool(row[1]),
                'RequireNumbers': bool(row[2]),
                'RequireUppercaseCharacters': bool(row[3]),
                'RequireLowercaseCharacters': bool(row[4]),
                'MaxPasswordAge': row[5],
                'PasswordReusePrevention': row[6],
            }

        aws_data['iam'] = {'users': users, 'roles': roles, 'password_policy': password_policy}

        # S3
        cur.execute("SELECT bucket_name, encryption, public_access_block, object_lock_mode, retention_days FROM s3_buckets")
        buckets = []
        object_lock_buckets = 0
        for r in cur.fetchall():
            bucket = {
                'bucket_name': r[0],
                'encryption_enabled': bool(r[1]),
                'public_access': not bool(r[2]),
                'object_lock_mode': r[3],
                'retention_days': r[4],
            }
            buckets.append(bucket)
            if r[3]:
                object_lock_buckets += 1
        aws_data['s3'] = {'buckets': buckets, 'object_lock_enabled': object_lock_buckets > 0, 'object_lock_buckets': object_lock_buckets}

        # KMS
        cur.execute("SELECT key_id, rotation_enabled FROM kms_keys")
        keys = [{'key_id': r[0], 'rotation_enabled': bool(r[1])} for r in cur.fetchall()]
        aws_data['kms'] = {'keys': keys}

        # VPC
        cur.execute("SELECT flow_logs, nat_gateways FROM vpc LIMIT 1")
        v = cur.fetchone()
        if v:
            aws_data['vpc'] = {'flow_logs': v[0], 'nat_gateways': v[1]}

        # WAF
        cur.execute("SELECT web_acl_name, rules_count FROM waf")
        web_acls = [{'web_acl_name': r[0], 'rules_count': r[1]} for r in cur.fetchall()]
        aws_data['waf'] = {'web_acls': web_acls}

        # CloudTrail
        cur.execute("SELECT trail_name FROM cloudtrail_trails")
        trails = [r[0] for r in cur.fetchall()]
        aws_data['cloudtrail'] = {'trails': trails}

        # GuardDuty
        cur.execute("SELECT detector_count FROM guardduty LIMIT 1")
        gd = cur.fetchone()
        if gd:
            aws_data['guardduty'] = {'detector_count': gd[0]}

        # Security Hub
        cur.execute("SELECT COUNT(*) FROM security_hub")
        sh_count = cur.fetchone()[0]
        cur.execute("SELECT standard_name, status, open_findings FROM security_hub")
        standards: Dict[str, Any] = {}
        total_findings = 0
        for r in cur.fetchall():
            standards[r[0]] = r[1]
            total_findings += r[2] or 0
        aws_data['security_hub'] = {'enabled': sh_count > 0, 'standards': standards, 'open_findings': total_findings}

        # Config
        cur.execute("SELECT rule_name, rule_state, rule_type FROM config_rules")
        account_lockout_rules: List[Dict[str, Any]] = []
        password_policy_rules: List[Dict[str, Any]] = []
        for r in cur.fetchall():
            d = {'name': r[0], 'state': r[1]}
            if r[2] == 'account_lockout':
                account_lockout_rules.append(d)
            elif r[2] == 'password_policy':
                password_policy_rules.append(d)
        aws_data['config'] = {
            'account_lockout_rules': account_lockout_rules,
            'password_policy_rules': password_policy_rules,
            'has_account_lockout_protection': len(account_lockout_rules) > 0,
        }

        # SSO (Identity Center)
        cur.execute("SELECT enabled, concurrent_session_limit, session_timeout, session_lock_enabled, session_termination_enabled FROM sso LIMIT 1")
        row = cur.fetchone()
        if row:
            aws_data['sso'] = {
                'enabled': bool(row[0]),
                'session_management': {
                    'concurrent_session_limit': row[1],
                    'session_timeout': row[2],
                    'session_lock_enabled': bool(row[3]),
                    'session_termination_enabled': bool(row[4]),
                },
            }

        return aws_data

    # Policies
    def store_policy(self, policy_data: Dict[str, Any]) -> bool:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO policies (
                    id, name, filename, content, controls_mapped, last_analyzed,
                    status, type, summary, reasons, missing, recommendations, citations
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    name=EXCLUDED.name,
                    filename=EXCLUDED.filename,
                    content=EXCLUDED.content,
                    controls_mapped=EXCLUDED.controls_mapped,
                    last_analyzed=EXCLUDED.last_analyzed,
                    status=EXCLUDED.status,
                    type=EXCLUDED.type,
                    summary=EXCLUDED.summary,
                    reasons=EXCLUDED.reasons,
                    missing=EXCLUDED.missing,
                    recommendations=EXCLUDED.recommendations,
                    citations=EXCLUDED.citations,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    policy_data['id'], policy_data['name'], policy_data.get('filename'), policy_data.get('content'),
                    json.dumps(policy_data.get('controlsMapped', [])), policy_data.get('lastAnalyzed'),
                    policy_data.get('status'), policy_data.get('type'), policy_data.get('summary'),
                    json.dumps(policy_data.get('reasons', [])), json.dumps(policy_data.get('missing', [])),
                    json.dumps(policy_data.get('recommendations', [])), json.dumps(policy_data.get('citations', [])),
                ),
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    def get_policies(self) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, name, filename, controls_mapped, last_analyzed, status, type, summary, reasons, missing, recommendations, citations
            FROM policies ORDER BY created_at DESC
            """
        )
        res: List[Dict[str, Any]] = []
        for r in cur.fetchall():
            res.append({
                'id': r[0],
                'name': r[1],
                'filename': r[2],
                'controlsMapped': json.loads(r[3]) if r[3] else [],
                'lastAnalyzed': r[4],
                'status': r[5],
                'type': r[6],
                'summary': r[7],
                'reasons': json.loads(r[8]) if r[8] else [],
                'missing': json.loads(r[9]) if r[9] else [],
                'recommendations': json.loads(r[10]) if r[10] else [],
                'citations': json.loads(r[11]) if r[11] else [],
            })
        return res


