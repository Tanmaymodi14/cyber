from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Union, List, Dict, Any
import uvicorn
import sqlite3
import json
import os
from datetime import datetime
import boto3

app = FastAPI(title="proTecht API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def get_db_connection():
    db_path = "protecht.db"  # Use local database
    return sqlite3.connect(db_path)

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create basic tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aws_data (
            id INTEGER PRIMARY KEY,
            service TEXT,
            data TEXT,
            timestamp TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            id TEXT PRIMARY KEY,
            name TEXT,
            filename TEXT,
            content TEXT,
            controls_mapped TEXT,
            last_analyzed TEXT,
            status TEXT,
            type TEXT,
            summary TEXT,
            reasons TEXT,
            missing TEXT,
            recommendations TEXT,
            citations TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

def _now_iso():
    return datetime.now().isoformat()

def _require_token(authorization: Union[str, None]):
    # Simple token validation - in production, use proper JWT validation
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, "Invalid or missing token")

@app.get("/api/health")
def health():
    return {"status": "healthy", "message": "proTecht API is running"}

@app.get("/api/controls")
def get_controls():
    # Return the same data structure as your real backend
    return {
        "status": "success",
        "data": [
            {"id": "AC-1", "status": "pass", "score": 85, "reasons": ["Policy in place"]},
            {"id": "AC-2", "status": "pass", "score": 90, "reasons": ["Access controls configured"]},
            {"id": "AC-3", "status": "fail", "score": 40, "reasons": ["Missing evidence"]},
            {"id": "AC-4", "status": "pass", "score": 70, "reasons": ["WAF deployed"]},
            {"id": "AC-7", "status": "pass", "score": 60, "reasons": ["Strong password policy"]},
            {"id": "AC-10", "status": "pass", "score": 70, "reasons": ["SSO enabled"]},
            {"id": "AC-16", "status": "pass", "score": 60, "reasons": ["S3 encryption enforced"]},
            {"id": "AC-21", "status": "pass", "score": 60, "reasons": ["S3 public access blocked"]}
        ]
    }

@app.get("/api/evidence/aws/services")
def get_services():
    return {
        "status": "success",
        "data": [
            {
                "id": "iam-config",
                "title": "IAM Configuration",
                "status": "Current",
                "kpis": {"Users": 8, "Roles": 4, "Policies": 0}
            },
            {
                "id": "s3-policies",
                "title": "S3 Bucket Policies", 
                "status": "Current",
                "kpis": {"Buckets": 10, "PublicBuckets": 0, "Encrypted": 10, "ObjectLockBuckets": 7}
            },
            {
                "id": "kms",
                "title": "KMS",
                "status": "Current", 
                "kpis": {"Keys": 10, "RotationEnabled": 7}
            },
            {
                "id": "cloudtrail",
                "title": "CloudTrail",
                "status": "Current",
                "kpis": {"Trails": 3, "Events": 0, "RetentionDays": 90}
            },
            {
                "id": "waf",
                "title": "WAF",
                "status": "Current",
                "kpis": {"WebACLs": 3, "Blocked7d": 0}
            },
            {
                "id": "guardduty",
                "title": "GuardDuty",
                "status": "Current",
                "kpis": {"Detector": 1, "Critical/High": 0}
            },
            {
                "id": "security-hub",
                "title": "Security Hub",
                "status": "Current",
                "kpis": {"Enabled": "Yes", "OpenFindings": 201}
            },
            {
                "id": "vpc-cloudfront",
                "title": "VPC/CloudFront",
                "status": "Current",
                "kpis": {"FlowLogs": "On", "Distributions": 0, "TLSPolicy": "v1.2+"}
            },
            {
                "id": "identity-center",
                "title": "Identity Center (SSO)",
                "status": "Current",
                "kpis": {"PermissionSets": 0, "SessionTimeout": "PT8H", "MFA": "Enabled"}
            },
            {
                "id": "aws-config",
                "title": "AWS Config",
                "status": "Current",
                "kpis": {"RulesTotal": 4, "LockoutRules": 2}
            }
        ]
    }

@app.post("/api/evidence/aws/recollect")
def recollect_aws():
    return {
        "status": "success", 
        "message": "AWS data collection started",
        "collected_keys": ["cloudtrail", "s3", "kms", "guardduty", "sso", "config", "vpc"],
        "timestamp": _now_iso()
    }

@app.get("/api/policies")
def get_policies():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM policies')
    rows = cursor.fetchall()
    conn.close()
    
    policies = []
    for row in rows:
        policies.append({
            "id": row[0],
            "name": row[1],
            "status": row[6] or "Unknown",
            "controlsMapped": json.loads(row[4]) if row[4] else [],
            "lastAnalyzed": row[5] or _now_iso()
        })
    
    # Add some sample policies if none exist
    if not policies:
        policies = [
            {
                "id": "policy-1758916848",
                "name": "Test Small Policy",
                "status": "Partial",
                "controlsMapped": ["AC-1"],
                "lastAnalyzed": _now_iso()
            },
            {
                "id": "policy-1758916863", 
                "name": "Test Small Policy 2",
                "status": "Compliant",
                "controlsMapped": ["AC-1", "AC-2"],
                "lastAnalyzed": _now_iso()
            },
            {
                "id": "policy-1758943060",
                "name": "Policy_Permitted_Actions.pdf",
                "status": "Compliant", 
                "controlsMapped": ["AC-1", "AC-2", "AC-3"],
                "lastAnalyzed": _now_iso()
            }
        ]
    
    return {
        "status": "success",
        "data": policies
    }

@app.post("/api/policies/{policy_id}/reanalyze")
def reanalyze_policy(policy_id: str):
    # Simulate policy reanalysis
    return {
        "status": "success",
        "message": f"Policy {policy_id} reanalyzed successfully",
        "data": {
            "id": policy_id,
            "name": "Test Policy",
            "status": "Compliant",
            "controlsMapped": ["AC-1", "AC-2"],
            "lastAnalyzed": _now_iso()
        },
        "timestamp": _now_iso()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
