from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="proTecht API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "healthy", "message": "proTecht API is running"}

@app.get("/api/controls")
def get_controls():
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
        "timestamp": "2025-09-27T05:30:00+00:00"
    }

@app.get("/api/policies")
def get_policies():
    return {
        "status": "success",
        "data": [
            {
                "id": "policy-1758916848",
                "name": "Test Small Policy",
                "status": "Partial",
                "controlsMapped": ["AC-1"],
                "lastAnalyzed": "2025-09-27T05:30:00+00:00"
            },
            {
                "id": "policy-1758916863", 
                "name": "Test Small Policy 2",
                "status": "Compliant",
                "controlsMapped": ["AC-1", "AC-2"],
                "lastAnalyzed": "2025-09-27T05:30:00+00:00"
            },
            {
                "id": "policy-1758943060",
                "name": "Policy_Permitted_Actions.pdf",
                "status": "Compliant", 
                "controlsMapped": ["AC-1", "AC-2", "AC-3"],
                "lastAnalyzed": "2025-09-27T05:30:00+00:00"
            }
        ]
    }

@app.post("/api/policies/{policy_id}/reanalyze")
def reanalyze_policy(policy_id: str):
    return {
        "status": "success",
        "message": f"Policy {policy_id} reanalyzed successfully",
        "data": {
            "id": policy_id,
            "name": "Test Policy",
            "status": "Compliant",
            "controlsMapped": ["AC-1", "AC-2"],
            "lastAnalyzed": "2025-09-27T05:30:00+00:00"
        },
        "timestamp": "2025-09-27T05:30:00+00:00"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
