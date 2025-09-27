#!/usr/bin/env python3
"""
FastAPI server for proTecht frontend integration (AC family only)

Endpoints (no SSP generator):
- GET /api/health
- GET /api/evidence/aws
- GET /api/evidence/aws/services
- GET /api/evidence/aws/services/{service_id}
- POST /api/evidence/aws/recollect
- GET /api/controls
- GET /api/controls/{control_id}
- GET /api/policies
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

from fastapi import FastAPI, HTTPException, Header
from fastapi import Request
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from database import ProTechtDatabase
from policy.cache import get_cache  # type: ignore
from technical_engine import evaluate_ac_controls  # type: ignore
try:
    from ai_analysis_agent import AIAnalysisAgent  # type: ignore
except Exception:  # pragma: no cover
    AIAnalysisAgent = None  # type: ignore
try:
    # Control family groupings used to surface all 22 AC controls in UI
    from policy.schema import (  # type: ignore
        NON_TECHNICAL_AC_CONTROLS,
        MIXED_AC_CONTROLS,
    )
except Exception:  # pragma: no cover
    NON_TECHNICAL_AC_CONTROLS = ["AC-1", "AC-14", "AC-20", "AC-22"]
    MIXED_AC_CONTROLS = ["AC-2", "AC-8", "AC-17", "AC-18", "AC-19"]


app = FastAPI(title="proTecht AC API", version="1.0.0")

# CORS: allow all origins to simplify deployments across ALB/CloudFront
# For production, restrict this to specific domains via FRONTEND_ORIGIN
frontend_origin = os.environ.get("FRONTEND_ORIGIN")
allow_origins = [frontend_origin] if frontend_origin else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = ProTechtDatabase()

# In-memory cache for AWS data
_aws_data_cache = {}
ai_agent = None
if AIAnalysisAgent is not None:
    try:
        ai_agent = AIAnalysisAgent()
    except Exception:
        ai_agent = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

# Realtime progress state (simple in-memory)
_ws_clients: list[WebSocket] = []
_recent_events: list[Dict[str, Any]] = []
_RECENT_MAX = 200

async def _ws_broadcast(event: Dict[str, Any]) -> None:
    for ws in list(_ws_clients):
        try:
            await ws.send_json(event)
        except Exception:
            # Best-effort only
            pass

def _emit(event_type: str, payload: Dict[str, Any]) -> None:
    event = {"type": event_type, "ts": _now_iso(), **payload}
    _recent_events.append(event)
    if len(_recent_events) > _RECENT_MAX:
        del _recent_events[: len(_recent_events) - _RECENT_MAX]
    try:
        import asyncio
        if _ws_clients:
            asyncio.create_task(_ws_broadcast(event))
    except Exception:
        pass


@app.get("/")
def root():
    return {"service": "proTecht AC API", "status": "ok"}


@app.get("/api/health")
def health():
    return {"status": "healthy", "ts": _now_iso()}


@app.get("/api/cache/stats")
def get_cache_stats():
    """Get LLM cache statistics."""
    try:
        cache = get_cache()
        stats = cache.get_stats()
        return {"status": "success", "data": stats, "timestamp": _now_iso()}
    except Exception as exc:
        raise HTTPException(500, f"Failed to get cache stats: {exc}")


@app.post("/api/cache/cleanup")
def cleanup_cache():
    """Clean up expired cache entries."""
    try:
        cache = get_cache()
        removed_count = cache.cleanup_expired()
        return {"status": "success", "message": f"Removed {removed_count} expired entries", "timestamp": _now_iso()}
    except Exception as exc:
        raise HTTPException(500, f"Failed to cleanup cache: {exc}")


# ----------------------------- Evidence -----------------------------

@app.get("/api/evidence/aws")
def get_aws_evidence():
    try:
        data = db.load_aws_data_from_db()
        return {"status": "success", "data": data, "timestamp": _now_iso()}
    except Exception as exc:
        raise HTTPException(500, f"Failed to load AWS evidence: {exc}")


def _services_from_aws(aws_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Handle case where aws_data might be a list instead of dict
    if isinstance(aws_data, list):
        # If it's a list, convert to dict format
        aws_data = {item.get('id', 'unknown'): item for item in aws_data}
    services: List[Dict[str, Any]] = []

    # IAM
    iam = aws_data.get("iam", {})
    services.append({
        "id": "iam-config",
        "title": "IAM Configuration",
        "lastUpdated": _now_iso(),
        "status": "Current",
        "kpis": {
            "Users": len(iam.get("users", [])),
            "Roles": len(iam.get("roles", [])),
            "Policies": len(iam.get("policies", [])),
        },
        "mappedControls": ["AC-3", "AC-5", "AC-6", "AC-7", "AC-9"],
        "evidenceSnippet": "IAM users/roles/policies inventory",
    })

    # SSO / Identity Center
    sso = aws_data.get("sso", {})
    sm = sso.get("session_management", {})
    ps_count = sso.get("permission_sets_count", 0)
    services.append({
        "id": "identity-center",
        "title": "Identity Center (SSO)",
        "lastUpdated": _now_iso(),
        "status": "Current" if sso.get("enabled") else "Warning",
        "kpis": {
            "PermissionSets": ps_count,
            "SessionTimeout": sm.get("session_timeout") or "Not set",
            "MFA": "Enabled" if sso.get("enabled") else "Disabled",
        },
        "mappedControls": ["AC-10", "AC-11", "AC-12"],
        "evidenceSnippet": "SSO session policies and MFA",
    })

    # AWS Config
    cfg = aws_data.get("config", {})
    services.append({
        "id": "aws-config",
        "title": "AWS Config",
        "lastUpdated": _now_iso(),
        "status": "Current" if cfg.get("has_account_lockout_protection") else "Warning",
        "kpis": {
            "RulesTotal": len(cfg.get("account_lockout_rules", [])) + len(cfg.get("password_policy_rules", [])),
            "LockoutRules": len(cfg.get("account_lockout_rules", [])),
        },
        "mappedControls": ["AC-7"],
        "evidenceSnippet": "Config rules for lockout/password policy",
    })

    # S3
    s3 = aws_data.get("s3", {})
    buckets = s3.get("buckets", [])
    services.append({
        "id": "s3-policies",
        "title": "S3 Bucket Policies",
        "lastUpdated": _now_iso(),
        "status": "Current" if s3.get("object_lock_enabled") else "Warning",
        "kpis": {
            "Buckets": len(buckets),
            "PublicBuckets": sum(1 for b in buckets if b.get("public_access")),
            "Encrypted": sum(1 for b in buckets if b.get("encryption_enabled")),
            "ObjectLockBuckets": s3.get("object_lock_buckets", 0),
        },
        "mappedControls": ["AC-15", "AC-16", "AC-21"],
        "evidenceSnippet": "S3 encryption/public access/object lock",
    })

    # KMS
    kms = aws_data.get("kms", {})
    keys = kms.get("keys", [])
    services.append({
        "id": "kms",
        "title": "KMS",
        "lastUpdated": _now_iso(),
        "status": "Current" if any(k.get("rotation_enabled") for k in keys) else "Warning",
        "kpis": {
            "Keys": len(keys),
            "RotationEnabled": sum(1 for k in keys if k.get("rotation_enabled")),
        },
        "mappedControls": ["AC-16"],
        "evidenceSnippet": "KMS key inventory and rotation",
    })

    # CloudTrail
    ct = aws_data.get("cloudtrail", {})
    services.append({
        "id": "cloudtrail",
        "title": "CloudTrail",
        "lastUpdated": _now_iso(),
        "status": "Current" if ct.get("trails") else "Warning",
        "kpis": {
            "Trails": len(ct.get("trails", [])),
            "Events": 0,
            "RetentionDays": 90,
        },
        "mappedControls": ["AC-9"],
        "evidenceSnippet": "Audit trails and retention",
    })

    # WAF
    waf = aws_data.get("waf", {})
    web_acls = waf.get("web_acls", [])
    services.append({
        "id": "waf",
        "title": "WAF",
        "lastUpdated": _now_iso(),
        "status": "Current" if web_acls else "Warning",
        "kpis": {
            "WebACLs": len(web_acls),
            "Blocked7d": 0,
        },
        "mappedControls": ["AC-4", "AC-21"],
        "evidenceSnippet": "Edge filtering controls",
    })

    # GuardDuty
    gd = aws_data.get("guardduty", {})
    services.append({
        "id": "guardduty",
        "title": "GuardDuty",
        "lastUpdated": _now_iso(),
        "status": "Current" if gd.get("detector_count", 0) > 0 else "Warning",
        "kpis": {
            "Detector": gd.get("detector_count", 0),
            "Critical/High": 0,
        },
        "mappedControls": ["AC-13"],
        "evidenceSnippet": "Threat detection status",
    })

    # Security Hub
    sh = aws_data.get("security_hub", {})
    services.append({
        "id": "security-hub",
        "title": "Security Hub",
        "lastUpdated": _now_iso(),
        "status": "Current" if sh.get("enabled") else "Warning",
        "kpis": {
            "Enabled": "Yes" if sh.get("enabled") else "No",
            "OpenFindings": sh.get("open_findings", 0),
        },
        "mappedControls": ["AC-13"],
        "evidenceSnippet": "Security posture aggregation",
    })

    # VPC / CloudFront
    vpc = aws_data.get("vpc", {})
    cf = aws_data.get("cloudfront", {})
    services.append({
        "id": "vpc-cloudfront",
        "title": "VPC/CloudFront",
        "lastUpdated": _now_iso(),
        "status": "Current" if vpc.get("flow_logs") or cf.get("distributions") else "Warning",
        "kpis": {
            "FlowLogs": "On" if vpc.get("flow_logs") else "Off",
            "Distributions": len(cf.get("distributions", [])),
            "TLSPolicy": "v1.2+",
        },
        "mappedControls": ["AC-4", "AC-11", "AC-12", "AC-21"],
        "evidenceSnippet": "Network logging and edge TLS",
    })

    return services


@app.get("/api/evidence/aws/services")
def get_services():
    try:
        # First try to get data from memory cache
        global _aws_data_cache
        if _aws_data_cache:
            services = _services_from_aws(_aws_data_cache)
            return {"status": "success", "data": services, "timestamp": _now_iso()}
        
        # Fallback: try to get data from database
        data = db.load_aws_data_from_db()
        services = _services_from_aws(data)
        return {"status": "success", "data": services, "timestamp": _now_iso()}
    except Exception as exc:
        raise HTTPException(500, f"Failed to load services: {exc}")


_ID_MAP = {
    "iam-config": "iam",
    "identity-center": "sso",
    "aws-config": "config",
    "s3-policies": "s3",
    "security-hub": "security_hub",
    "vpc-cloudfront": "vpc_cloudfront",
}


@app.get("/api/evidence/aws/services/{service_id}")
def get_service_detail(service_id: str):
    try:
        data = db.load_aws_data_from_db()
        sid = _ID_MAP.get(service_id, service_id)
        if sid == "iam":
            return {"status": "success", "data": data.get("iam", {})}
        if sid == "sso":
            return {"status": "success", "data": data.get("sso", {})}
        if sid == "config":
            return {"status": "success", "data": data.get("config", {})}
        if sid == "s3":
            return {"status": "success", "data": data.get("s3", {})}
        if sid == "kms":
            return {"status": "success", "data": data.get("kms", {})}
        if sid == "cloudtrail":
            return {"status": "success", "data": data.get("cloudtrail", {})}
        if sid == "waf":
            return {"status": "success", "data": data.get("waf", {})}
        if sid == "guardduty":
            return {"status": "success", "data": data.get("guardduty", {})}
        if sid == "security_hub":
            return {"status": "success", "data": data.get("security_hub", {})}
        if sid == "vpc_cloudfront":
            return {
                "status": "success",
                "data": {"vpc": data.get("vpc", {}), "cloudfront": data.get("cloudfront", {})},
            }
        raise HTTPException(404, "Unknown service id")
    except Exception as exc:
        raise HTTPException(500, f"Failed to load service: {exc}")


def _require_token(authorization: Union[str, None]):  # minimal placeholder
    if authorization is None:
        return
    # In a real deployment, verify JWT here.
    return


@app.post("/api/evidence/aws/recollect")
def recollect_aws(profile: Union[str, None] = None, regions: Union[str, None] = None, authorization: Union[str, None] = Header(default=None)):
    _require_token(authorization)
    """Trigger re-collection (synchronously) and reload DB.
    regions: comma-separated list (e.g., "us-east-1,us-west-2")
    """
    try:
        from aws_collect import collect_all  # lazy import

        regions_list = [r.strip() for r in regions.split(",")] if regions else None
        # Simple progress capture for polling clients
        def _progress(mod: str, status: str, index: int, total: int):
            _emit("collector_progress", {"module": mod, "status": status, "index": index, "total": total})

        collected = collect_all(profile=profile, regions=regions_list, progress_cb=_progress)
        db.load_aws_data(collected)
        return {"status": "success", "collected_keys": list(collected.keys()), "timestamp": _now_iso()}
    except Exception as exc:
        raise HTTPException(500, f"Re-collect failed: {exc}")


@app.post("/api/evidence/aws/ingest")
async def ingest_aws_evidence(request: Request, authorization: Union[str, None] = Header(default=None)):
    _require_token(authorization)
    try:
        payload = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(400, "Invalid JSON payload")
        
        # Store in database
        db.load_aws_data(payload)
        
        # Also store in memory cache for immediate access
        global _aws_data_cache
        _aws_data_cache.update(payload)
        
        _emit("ingest_complete", {"keys": list(payload.keys())})
        return {"status": "success", "ingested_keys": list(payload.keys()), "timestamp": _now_iso()}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Ingest failed: {exc}")


# ----------------------------- Realtime (WebSocket + Polling) -----------------------------
@app.websocket("/ws/progress")
async def ws_progress(websocket: WebSocket):
    await websocket.accept()
    _ws_clients.append(websocket)
    try:
        while True:
            # Keep the socket alive; we don't expect messages from client
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in _ws_clients:
            _ws_clients.remove(websocket)


@app.get("/api/progress/recent")
def recent_progress(limit: int = 100):
    try:
        return {"status": "success", "data": _recent_events[-limit:], "timestamp": _now_iso()}
    except Exception as exc:
        raise HTTPException(500, f"Failed to read progress: {exc}")


# ----------------------------- Controls -----------------------------

@app.get("/api/controls")
def get_controls():
    try:
        data = db.load_aws_data_from_db()
        
        # Check if we have real data - if not, trigger collection
        has_real_data = any([
            len(data.get('iam', {}).get('users', [])) > 0,
            len(data.get('s3', {}).get('buckets', [])) > 0,
            len(data.get('kms', {}).get('keys', [])) > 0,
            len(data.get('cloudtrail', {}).get('trails', [])) > 0
        ])
        
        if not has_real_data:
            # No real data available - return empty state with instructions
            return {
                "status": "no_data",
                "message": "No AWS data available. Please collect real AWS data first.",
                "data": [],
                "instructions": {
                    "collect_data": "POST /api/evidence/aws/recollect",
                    "upload_policy": "POST /api/policies/upload"
                },
                "timestamp": _now_iso()
            }
        
        technical = evaluate_ac_controls(data)
        controls = []
        # 13 technical controls from evaluator
        for cid, res in technical.items():
            controls.append({
                "id": cid,
                "name": cid,
                "status": res.get("status", "unknown"),
                "score": int(res.get("confidence", 0) * 100),
                "confidence": res.get("confidence", 0),
                "reasons": res.get("reasons", []),
                "missingEvidence": res.get("missing_evidence", []),
                "evidenceSources": [],
                "technicalResult": res,
            })

        # Add remaining AC controls so UI shows full set of 22.
        existing_ids = {c["id"] for c in controls}

        # Non-technical controls (policy-driven)
        for cid in NON_TECHNICAL_AC_CONTROLS:
            if cid in existing_ids:
                continue
            controls.append({
                "id": cid,
                "name": cid,
                "status": "unknown",   # Policy analysis not run yet
                "score": 0,
                "confidence": 0.0,
                "reasons": ["Policy analysis not available"],
                "missingEvidence": ["Upload and analyze policy documents"],
                "evidenceSources": ["policy"],
                "technicalResult": {},
            })

        # Mixed controls are now handled by the technical engine, so no need to add them here
        return {"status": "success", "data": controls, "timestamp": _now_iso()}
    except Exception as exc:
        raise HTTPException(500, f"Failed to load controls: {exc}")


@app.get("/api/controls/{control_id}")
def get_control_detail(control_id: str):
    try:
        data = db.load_aws_data_from_db()
        technical = evaluate_ac_controls(data).get(control_id)
        if not technical:
            raise HTTPException(404, "Control not found")
        return {
            "status": "success",
            "data": {
                "controlId": control_id,
                "technicalResult": technical,
                "whatWeChecked": [],
                "recommendations": [],
            },
            "timestamp": _now_iso(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Failed to load control detail: {exc}")


# ----------------------------- Policies -----------------------------

@app.get("/api/policies")
def get_policies():
    """Return analyzed policies for AC from database."""
    try:
        policies = db.get_policies()
        return {"status": "success", "data": policies, "timestamp": _now_iso()}
    except Exception as exc:
        raise HTTPException(500, f"Failed to load policies: {exc}")


# ----------------------------- AI Analysis -----------------------------

@app.get("/api/analysis/controls")
def ai_controls_analysis():
    if ai_agent is None:
        raise HTTPException(503, "AI analysis unavailable (agent not initialized)")
    try:
        results = ai_agent.analyze_all_controls()
        return {"status": "success", "data": results, "timestamp": _now_iso()}
    except Exception as exc:
        raise HTTPException(500, f"AI analysis failed: {exc}")


@app.get("/api/analysis/controls/{control_id}")
def ai_control_analysis(control_id: str):
    if ai_agent is None:
        raise HTTPException(503, "AI analysis unavailable (agent not initialized)")
    try:
        result = ai_agent.analyze_control(control_id)
        return {"status": "success", "data": result, "timestamp": _now_iso()}
    except Exception as exc:
        raise HTTPException(500, f"AI analysis failed: {exc}")


# ----------------------------- Export -----------------------------

from fastapi.responses import JSONResponse


@app.get("/api/export/services")
def export_services():
    data = db.load_aws_data_from_db()
    services = _services_from_aws(data)
    return JSONResponse(
        content=services,
        headers={"Content-Disposition": "attachment; filename=services.json"},
    )


@app.get("/api/export/controls")
def export_controls():
    data = db.load_aws_data_from_db()
    technical = evaluate_ac_controls(data)
    return JSONResponse(
        content=technical,
        headers={"Content-Disposition": "attachment; filename=controls.json"},
    )


@app.get("/api/export/service/{service_id}")
def export_service(service_id: str):
    res = get_service_detail(service_id)
    return JSONResponse(
        content=res["data"],
        headers={"Content-Disposition": f"attachment; filename={service_id}.json"},
    )


# ----------------------------- OpenAPI -----------------------------

@app.get("/api/openapi.json")
def openapi_spec():
    return app.openapi()


# ----------------------------- Policy Upload & Analysis -----------------------------

from fastapi import UploadFile, File, Form


def _extract_text(file_bytes: bytes, filename: str) -> str:
    name = filename.lower()
    try:
        if name.endswith(".pdf"):
            import io
            from PyPDF2 import PdfReader

            reader = PdfReader(io.BytesIO(file_bytes))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if name.endswith(".docx"):
            from docx import Document  # type: ignore
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=True) as tf:
                tf.write(file_bytes)
                tf.flush()
                doc = Document(tf.name)
                return "\n".join(p.text for p in doc.paragraphs)
        # Fallback: treat as text
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception as exc:  # pragma: no cover
        raise HTTPException(400, f"Failed to extract text: {exc}")


@app.post("/api/fedramp-template/upload")
def upload_fedramp_template(file: UploadFile = File(...), template_name: str = Form("FedRAMP Template"), authorization: Union[str, None] = Header(default=None)):
    _require_token(authorization)
    try:
        content = file.file.read()
        
        # Store FedRAMP template in database
        # First save the file temporarily, then store in database
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            success = db.store_fedramp_template(
                template_name=template_name,
                template_type="SSP-Low-Baseline",
                file_path=tmp_file_path
            )
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
        
        if success:
            return {"status": "success", "message": "FedRAMP template uploaded successfully", "timestamp": _now_iso()}
        else:
            raise HTTPException(500, "Failed to store FedRAMP template")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"FedRAMP template upload failed: {exc}")


@app.post("/api/policies/upload")
def upload_policy(file: UploadFile = File(...), policy_name: str = Form("Uploaded Policy"), authorization: Union[str, None] = Header(default=None)):
    _require_token(authorization)
    try:
        content = file.file.read()
        text = _extract_text(content, file.filename)

        # Call full LLM-powered policy analyzer with FedRAMP template
        from policy.analyzer import analyze_access_control_policy  # type: ignore

        report = analyze_access_control_policy(policy_name, text, quiet=True)
        
        # Store policy in database
        policy_id = f"policy-{int(time.time())}"
        policy_data = {
            "id": policy_id,
            "name": policy_name,
            "filename": file.filename,
            "content": text,
            "controlsMapped": [c.control_id for c in report.controls],
            "lastAnalyzed": _now_iso(),
            "status": "Compliant" if report.summary.get("compliance_pct", 0) >= 80 else "Partial",
            "type": "non-technical",
            "summary": report.summary.get("summary", "Policy analysis completed"),
            "reasons": [c.reasons for c in report.controls if c.reasons],
            "missing": [c.missing_elements for c in report.controls if c.missing_elements],
            "recommendations": [c.recommendations for c in report.controls if c.recommendations],
            "citations": [c.policy_citations for c in report.controls if c.policy_citations],
        }
        
        # Store in database
        db.store_policy(policy_data)
        
        return {"status": "success", "data": policy_data, "timestamp": _now_iso()}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Policy upload/analyze failed: {exc}")


@app.post("/api/policies/{policy_id}/reanalyze")
def reanalyze_policy(policy_id: str, authorization: Union[str, None] = Header(default=None)):
    _require_token(authorization)
    try:
        # Get existing policy from database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM policies WHERE id = ?', (policy_id,))
        policy_row = cursor.fetchone()
        conn.close()
        
        if not policy_row:
            raise HTTPException(404, "Policy not found")
        
        # Extract policy data (columns: id, name, filename, content, controls_mapped, last_analyzed, status, type, summary, reasons, missing, recommendations, citations, created_at, updated_at)
        policy_data = {
            'id': policy_row[0],
            'name': policy_row[1],
            'filename': policy_row[2],
            'content': policy_row[3]
        }
        
        # Re-analyze the policy
        from policy.analyzer import analyze_access_control_policy  # type: ignore
        
        report = analyze_access_control_policy(policy_data['name'], policy_data['content'], quiet=True)
        
        # Update policy data with new analysis
        updated_policy_data = {
            "id": policy_id,
            "name": policy_data['name'],
            "filename": policy_data['filename'],
            "content": policy_data['content'],
            "controlsMapped": [c.control_id for c in report.controls],
            "lastAnalyzed": _now_iso(),
            "status": "Compliant" if report.summary.get("compliance_pct", 0) >= 80 else "Partial",
            "type": "non-technical",
            "summary": report.summary.get("summary", "Policy analysis completed"),
            "reasons": [c.reasons for c in report.controls if c.reasons],
            "missing": [c.missing_elements for c in report.controls if c.missing_elements],
            "recommendations": [c.recommendations for c in report.controls if c.recommendations],
            "citations": [c.policy_citations for c in report.controls if c.policy_citations],
        }
        
        # Update in database
        db.store_policy(updated_policy_data)
        
        return {"status": "success", "data": updated_policy_data, "timestamp": _now_iso()}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Policy reanalysis failed: {exc}")


# ----------------------------- AWS Bootstrap -----------------------------

@app.post("/api/aws/bootstrap")
def aws_bootstrap(profile: Union[str, None] = None, regions: Union[str, None] = None, authorization: Union[str, None] = Header(default=None)):
    _require_token(authorization)
    try:
        from scripts.bootstrap_ac_baseline import main as bootstrap_main  # type: ignore
        # We cannot call argparse main directly with args; instead, shell out via environment
        import subprocess, sys
        cmd = [sys.executable, "scripts/bootstrap_ac_baseline.py"]
        if profile:
            cmd += ["--profile", profile]
        if regions:
            cmd += ["--regions", regions]
        subprocess.check_call(cmd, cwd=os.path.dirname(__file__) + "/..")
        return {"status": "success", "timestamp": _now_iso()}
    except subprocess.CalledProcessError as exc:  # type: ignore
        raise HTTPException(500, f"AWS bootstrap failed: {exc}")
    except Exception as exc:
        raise HTTPException(500, f"AWS bootstrap failed: {exc}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


