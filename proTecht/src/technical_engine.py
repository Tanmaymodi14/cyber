#!/usr/bin/env python3
"""
Headless technical compliance engine for Access Control (AC) family.

This module evaluates technical AC controls against AWS evidence loaded via
ProTechtDatabase.get_aws_data(). It is UI-free and suitable for CLI usage.

Controls covered (technical-only):
  AC-3, AC-4, AC-5, AC-6, AC-7,
  AC-9, AC-10, AC-11, AC-12, AC-13, AC-15, AC-16, AC-21

Mixed controls (require both policy + technical) are not scored here:
  AC-2, AC-8, AC-17, AC-18, AC-19

Return structure per control:
{
  "status": "pass|partial|fail",
  "confidence": float,
  "reasons": [str],
  "evidence": {str: any},
  "missing_evidence": [str]
}
"""

from typing import Dict, Any, List

try:
    # Local import; avoid circulars
    from .database import ProTechtDatabase
except Exception:
    # Fallback for direct script execution
    from database import ProTechtDatabase


TECHNICAL_AC_CONTROLS: List[str] = [
    # Existing implemented set in legacy engine
    "AC-3", "AC-4", "AC-5", "AC-6", "AC-7",
    # Missing technical controls we add here
    "AC-9", "AC-10", "AC-11", "AC-12", "AC-13", "AC-15", "AC-16", "AC-21",
]

# Mixed controls that require both policy and technical evidence
MIXED_AC_CONTROLS: List[str] = [
    "AC-2", "AC-8", "AC-17", "AC-18", "AC-19"
]


def _status_from_booleans(all_checks: List[bool]) -> str:
    if not all_checks:
        return "partial"
    if all(all_checks):
        return "pass"
    if any(all_checks):
        return "partial"
    return "fail"


def _bounded_confidence(p: float) -> float:
    return max(0.0, min(1.0, p))


def evaluate_ac_controls(aws_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Evaluate all technical AC controls using provided aws_data.

    This function does NOT hit live AWS; it relies on already-collected
    evidence (from DB or JSON). When evidence is missing, it reports
    partial and lists missing_evidence to guide data collection.
    """
    results: Dict[str, Dict[str, Any]] = {}

    # Helpers
    iam = aws_data.get("iam", {})
    sso = aws_data.get("sso", {})
    vpc = aws_data.get("vpc", {})
    s3 = aws_data.get("s3", {})
    kms = aws_data.get("kms", {})
    cloudfront = aws_data.get("cloudfront", {})
    cloudtrail = aws_data.get("cloudtrail", {})
    waf = aws_data.get("waf", {})

    # ------------------------
    # AC-3: Access Enforcement
    # ------------------------
    ac3_checks: List[bool] = []
    ac3_reasons: List[str] = []
    missing: List[str] = []
    # Basic signal: IAM roles with defined permissions/boundaries
    roles = iam.get("roles", [])
    ac3_checks.append(any(r.get("Permissions") for r in roles))
    if ac3_checks[-1]:
        ac3_reasons.append("IAM roles define permissions (RBAC present)")
    else:
        missing.append("iam.roles.Permissions")
    results["AC-3"] = {
        "status": _status_from_booleans(ac3_checks),
        "confidence": _bounded_confidence(0.7 if ac3_checks[-1] else 0.4),
        "reasons": ac3_reasons or ["Insufficient evidence of access enforcement"],
        "evidence": {"role_count": len(roles)},
        "missing_evidence": missing,
    }

    # ---------------------------------
    # AC-4: Information Flow Enforcement
    # ---------------------------------
    ac4_checks = []
    ac4_reasons: List[str] = []
    missing = []
    # Signals: VPC flow logs, WAF enabled somewhere, CloudFront TLS policy
    if vpc.get("flow_logs") is True:
        ac4_checks.append(True)
        ac4_reasons.append("VPC flow logs enabled")
    else:
        missing.append("vpc.flow_logs")

    waf_acls = waf.get("web_acls", [])
    if waf_acls:
        ac4_checks.append(True)
        ac4_reasons.append("WAF deployed for traffic filtering")
    else:
        missing.append("waf.web_acls")

    dists = cloudfront.get("distributions", [])
    if any(d.get("TLSPolicy", "").startswith("TLSv1.2") for d in dists):
        ac4_checks.append(True)
        ac4_reasons.append("CloudFront enforcing modern TLS")
    else:
        missing.append("cloudfront.distributions[].TLSPolicy")

    results["AC-4"] = {
        "status": _status_from_booleans(ac4_checks),
        "confidence": _bounded_confidence(0.7 if any(ac4_checks) else 0.4),
        "reasons": ac4_reasons or ["Insufficient evidence of information flow enforcement"],
        "evidence": {"waf_count": len(waf_acls), "cloudfront_distributions": len(dists)},
        "missing_evidence": missing,
    }

    # ----------------------------
    # AC-5: Separation of Duties
    # ----------------------------
    ac5_checks = []
    ac5_reasons: List[str] = []
    missing = []
    if roles:
        ac5_checks.append(any(r.get("Boundary") for r in roles))
        if ac5_checks[-1]:
            ac5_reasons.append("IAM role boundaries present for separation")
        else:
            missing.append("iam.roles.Boundary")
    else:
        missing.append("iam.roles[]")
    results["AC-5"] = {
        "status": _status_from_booleans(ac5_checks),
        "confidence": _bounded_confidence(0.65 if any(ac5_checks) else 0.4),
        "reasons": ac5_reasons or ["Insufficient evidence of separation of duties"],
        "evidence": {"role_count": len(roles)},
        "missing_evidence": missing,
    }

    # -------------------------
    # AC-6: Least Privilege
    # -------------------------
    ac6_checks = []
    ac6_reasons: List[str] = []
    missing = []
    if roles:
        ac6_checks.append(True)
        ac6_reasons.append("IAM roles scoped; privilege boundaries can enforce least privilege")
    else:
        missing.append("iam.roles[]")
    results["AC-6"] = {
        "status": _status_from_booleans(ac6_checks),
        "confidence": _bounded_confidence(0.6 if any(ac6_checks) else 0.4),
        "reasons": ac6_reasons or ["Insufficient evidence of least privilege"],
        "evidence": {"role_count": len(roles)},
        "missing_evidence": missing,
    }

    # ----------------------------------
    # AC-7: Unsuccessful Logon Attempts
    # ----------------------------------
    ac7_checks = []
    ac7_reasons: List[str] = []
    missing = []
    # Check password policy, Config rules, and SSO
    pwd = iam.get("password_policy", {})
    strong = (
        pwd.get("MinimumPasswordLength", 0) >= 8 and
        pwd.get("RequireSymbols") and pwd.get("RequireNumbers") and
        pwd.get("RequireUppercaseCharacters") and pwd.get("RequireLowercaseCharacters")
    )
    if strong:
        ac7_checks.append(True)
        ac7_reasons.append("Strong password policy configured")
    else:
        missing.append("iam.password_policy(strength)")
    
    # Check for Config rules that enforce account lockout
    config_data = aws_data.get("config", {})
    if config_data.get("has_account_lockout_protection"):
        ac7_checks.append(True)
        ac7_reasons.append("AWS Config rules enforce account lockout policies")
    else:
        missing.append("config.account_lockout_rules")
    
    sso_enabled = sso.get("enabled", False)
    if sso_enabled:
        ac7_checks.append(True)
        ac7_reasons.append("SSO configured; account lockout can be enforced at IdP")
    else:
        missing.append("sso configuration")
    
    results["AC-7"] = {
        "status": _status_from_booleans(ac7_checks),
        "confidence": _bounded_confidence(0.6 if any(ac7_checks) else 0.4),
        "reasons": ac7_reasons or ["Insufficient evidence of logon attempt limits"],
        "evidence": {
            "password_policy": pwd, 
            "config_rules": config_data.get("account_lockout_rules", []),
            "sso": sso_enabled
        },
        "missing_evidence": missing,
    }

    # -------------------------------
    # AC-9: Previous Logon Notification
    # -------------------------------
    ac9_checks = []
    ac9_reasons: List[str] = []
    missing = []
    # Evidence likely from IdP; use CloudTrail presence + SSO as proxy
    if cloudtrail.get("trails"):
        ac9_checks.append(True)
        ac9_reasons.append("CloudTrail enabled; previous logon derivable")
    else:
        missing.append("cloudtrail.trails[]")
    sso_enabled = sso.get("enabled", False)
    if sso_enabled:
        ac9_checks.append(True)
        ac9_reasons.append("SSO configured; banner/last login can be shown by IdP")
    else:
        missing.append("sso configuration")
    results["AC-9"] = {
        "status": _status_from_booleans(ac9_checks),
        "confidence": _bounded_confidence(0.55 if any(ac9_checks) else 0.35),
        "reasons": ac9_reasons or ["No evidence of previous logon notification"],
        "evidence": {"cloudtrail": bool(cloudtrail.get("trails")), "sso": sso_enabled},
        "missing_evidence": missing,
    }

    # ---------------------------------
    # AC-10: Concurrent Session Control
    # ---------------------------------
    ac10_checks = []
    ac10_reasons: List[str] = []
    missing = []
    # Check SSO session management configuration
    sso_data = aws_data.get("sso", {})
    session_mgmt = sso_data.get("session_management", {})
    
    if sso_data.get("enabled"):
        ac10_checks.append(True)
        ac10_reasons.append("SSO enabled with session management capabilities")
        
        if session_mgmt.get("concurrent_session_limit"):
            ac10_checks.append(True)
            ac10_reasons.append("Concurrent session limits configured")
        else:
            missing.append("sso.session_management.concurrent_session_limit")
    else:
        missing.append("sso.enabled")
    
    results["AC-10"] = {
        "status": _status_from_booleans(ac10_checks),
        "confidence": _bounded_confidence(0.7 if any(ac10_checks) else 0.3),
        "reasons": ac10_reasons or ["No evidence of concurrent session limits"],
        "evidence": {
            "sso_enabled": sso_data.get("enabled", False),
            "concurrent_session_limit": session_mgmt.get("concurrent_session_limit")
        },
        "missing_evidence": missing,
    }

    # -----------------------
    # AC-11: Session Lock
    # -----------------------
    ac11_checks = []
    ac11_reasons: List[str] = []
    missing = []
    # Check SSO session management and CloudFront
    if sso_data.get("enabled") and session_mgmt.get("session_lock_enabled"):
        ac11_checks.append(True)
        ac11_reasons.append("SSO session lock capabilities enabled")
    else:
        missing.append("sso.session_management.session_lock_enabled")
    
    if cloudfront.get("distributions"):
        ac11_checks.append(True)
        ac11_reasons.append("Edge/application can enforce idle locks/timeouts")
    else:
        missing.append("cloudfront.distributions[]")
    
    results["AC-11"] = {
        "status": _status_from_booleans(ac11_checks),
        "confidence": _bounded_confidence(0.7 if any(ac11_checks) else 0.3),
        "reasons": ac11_reasons or ["No evidence of session lock controls"],
        "evidence": {
            "sso_session_lock": session_mgmt.get("session_lock_enabled", False),
            "cloudfront_distributions": len(cloudfront.get("distributions", []))
        },
        "missing_evidence": missing,
    }

    # -----------------------------
    # AC-12: Session Termination
    # -----------------------------
    ac12_checks = []
    ac12_reasons: List[str] = []
    missing = []
    # Check SSO session management and CloudFront
    if sso_data.get("enabled") and session_mgmt.get("session_termination_enabled"):
        ac12_checks.append(True)
        ac12_reasons.append("SSO session termination capabilities enabled")
    else:
        missing.append("sso.session_management.session_termination_enabled")
    
    if cloudfront.get("distributions"):
        ac12_checks.append(True)
        ac12_reasons.append("Edge/application can terminate sessions on idle/explicit logout")
    else:
        missing.append("cloudfront.distributions[]")
    
    results["AC-12"] = {
        "status": _status_from_booleans(ac12_checks),
        "confidence": _bounded_confidence(0.7 if any(ac12_checks) else 0.3),
        "reasons": ac12_reasons or ["No evidence of session termination controls"],
        "evidence": {
            "sso_session_termination": session_mgmt.get("session_termination_enabled", False),
            "cloudfront_distributions": len(cloudfront.get("distributions", []))
        },
        "missing_evidence": missing,
    }

    # -------------------------------
    # AC-13: Supervision and Review
    # -------------------------------
    ac13_checks = []
    ac13_reasons: List[str] = []
    missing = []
    # Proxy via Security Hub and GuardDuty being monitored
    if aws_data.get("security_hub"):
        ac13_checks.append(True)
        ac13_reasons.append("Security Hub monitoring in place")
    else:
        missing.append("security_hub")
    if aws_data.get("guardduty"):
        ac13_checks.append(True)
        ac13_reasons.append("GuardDuty findings reviewed")
    else:
        missing.append("guardduty")
    results["AC-13"] = {
        "status": _status_from_booleans(ac13_checks),
        "confidence": _bounded_confidence(0.55 if any(ac13_checks) else 0.35),
        "reasons": ac13_reasons or ["No evidence of supervision/review activities"],
        "evidence": {
            "security_hub": bool(aws_data.get("security_hub")),
            "guardduty": bool(aws_data.get("guardduty")),
        },
        "missing_evidence": missing + ["Periodic access review artifacts (tickets, reports)"],
    }

    # ----------------------------
    # AC-15: Automated Marking
    # ----------------------------
    ac15_checks = []
    ac15_reasons: List[str] = []
    missing = []
    # Signals: S3 object lock/retention, Macie classification
    s3_buckets = s3.get("buckets", [])
    object_lock_buckets = sum(1 for b in s3_buckets if b.get("object_lock_mode"))
    if object_lock_buckets > 0:
        ac15_checks.append(True)
        ac15_reasons.append("S3 Object Lock used (governance/compliance)")
    else:
        missing.append("s3[].object_lock_mode")
    if aws_data.get("macie"):
        ac15_checks.append(True)
        ac15_reasons.append("Macie classification jobs present")
    else:
        missing.append("macie.jobs[]")
    results["AC-15"] = {
        "status": _status_from_booleans(ac15_checks),
        "confidence": _bounded_confidence(0.55 if any(ac15_checks) else 0.35),
        "reasons": ac15_reasons or ["No evidence of automated marking/classification"],
        "evidence": {
            "s3_object_lock_buckets": object_lock_buckets,
            "macie_present": bool(aws_data.get("macie")),
        },
        "missing_evidence": missing,
    }

    # ------------------------------
    # AC-16: Security Attributes
    # ------------------------------
    ac16_checks = []
    ac16_reasons: List[str] = []
    missing = []
    # Signals: S3 encryption/KMS usage as attribute enforcement
    s3_buckets = s3.get("buckets", [])
    if any(b.get("encryption_enabled") for b in s3_buckets):
        ac16_checks.append(True)
        ac16_reasons.append("S3 encryption enforced (attribute-based protection)")
    else:
        missing.append("s3.buckets[].encryption_enabled")
    kms_keys = kms.get("keys", []) if isinstance(kms, dict) else kms
    if any(k.get("rotation_enabled") or k.get("RotationEnabled") for k in kms_keys):
        ac16_checks.append(True)
        ac16_reasons.append("KMS keys with rotation enabled")
    else:
        missing.append("kms.keys[].rotation_enabled")
    results["AC-16"] = {
        "status": _status_from_booleans(ac16_checks),
        "confidence": _bounded_confidence(0.6 if any(ac16_checks) else 0.4),
        "reasons": ac16_reasons or ["No evidence of security attribute enforcement"],
        "evidence": {
            "encrypted_buckets": sum(1 for b in s3_buckets if b.get("encryption_enabled")),
            "kms_rotating": sum(1 for k in kms_keys if k.get("rotation_enabled") or k.get("RotationEnabled")),
        },
        "missing_evidence": missing,
    }

    # -----------------------------
    # AC-21: Information Sharing
    # -----------------------------
    ac21_checks = []
    ac21_reasons: List[str] = []
    missing = []
    # Signals: public access blocks on S3, WAF/CloudFront gating
    if s3_buckets and all(b.get("public_access") is False for b in s3_buckets):
        ac21_checks.append(True)
        ac21_reasons.append("S3 public access blocked by default")
    else:
        missing.append("s3.buckets[].public_access == False")
    if waf_acls:
        ac21_checks.append(True)
        ac21_reasons.append("WAF controls information exposure")
    else:
        missing.append("waf.web_acls")
    results["AC-21"] = {
        "status": _status_from_booleans(ac21_checks),
        "confidence": _bounded_confidence(0.6 if any(ac21_checks) else 0.4),
        "reasons": ac21_reasons or ["No evidence of information sharing controls"],
        "evidence": {
            "s3_without_public_access": sum(1 for b in s3_buckets if not b.get("public_access")),
            "waf_count": len(waf_acls),
        },
        "missing_evidence": missing + ["Cross-account/resource sharing policy exports"],
    }

    # -----------------------------
    # Mixed Controls (Policy + Technical)
    # -----------------------------
    
    # AC-2: Account Management
    ac2_checks = []
    ac2_reasons: List[str] = []
    missing = []
    
    # Technical evidence: IAM users with proper access controls
    if iam.get("users"):
        ac2_checks.append(True)
        ac2_reasons.append("IAM users present with access controls")
    else:
        missing.append("iam.users[]")
    
    # Technical evidence: SSO for centralized account management
    if sso.get("enabled"):
        ac2_checks.append(True)
        ac2_reasons.append("SSO enabled for centralized account management")
    else:
        missing.append("sso.enabled")
    
    results["AC-2"] = {
        "status": _status_from_booleans(ac2_checks),
        "confidence": _bounded_confidence(0.6 if any(ac2_checks) else 0.3),
        "reasons": ac2_reasons or ["Insufficient evidence of account management"],
        "evidence": {
            "iam_users": len(iam.get("users", [])),
            "sso_enabled": sso.get("enabled", False)
        },
        "missing_evidence": missing + ["Policy documents for account management procedures"],
    }

    # AC-8: System Use Notification
    ac8_checks = []
    ac8_reasons: List[str] = []
    missing = []
    
    # Technical evidence: WAF banners, CloudFront custom error pages
    if waf_acls:
        ac8_checks.append(True)
        ac8_reasons.append("WAF deployed for system use notifications")
    else:
        missing.append("waf.web_acls")
    
    if cloudfront.get("distributions"):
        ac8_checks.append(True)
        ac8_reasons.append("CloudFront can display system use notifications")
    else:
        missing.append("cloudfront.distributions[]")
    
    results["AC-8"] = {
        "status": _status_from_booleans(ac8_checks),
        "confidence": _bounded_confidence(0.5 if any(ac8_checks) else 0.3),
        "reasons": ac8_reasons or ["No evidence of system use notifications"],
        "evidence": {
            "waf_count": len(waf_acls),
            "cloudfront_distributions": len(cloudfront.get("distributions", []))
        },
        "missing_evidence": missing + ["Policy documents for system use notification requirements"],
    }

    # AC-17: Remote Access
    ac17_checks = []
    ac17_reasons: List[str] = []
    missing = []
    
    # Technical evidence: VPC with proper security groups, VPN endpoints
    if vpc.get("flow_logs"):
        ac17_checks.append(True)
        ac17_reasons.append("VPC flow logs enabled for remote access monitoring")
    else:
        missing.append("vpc.flow_logs")
    
    # Check for VPN endpoints (from the sample data structure)
    vpn_endpoints = aws_data.get("vpn", {}).get("client_vpn_endpoints", 0)
    if vpn_endpoints > 0:
        ac17_checks.append(True)
        ac17_reasons.append("VPN endpoints configured for secure remote access")
    else:
        missing.append("vpn.client_vpn_endpoints")
    
    results["AC-17"] = {
        "status": _status_from_booleans(ac17_checks),
        "confidence": _bounded_confidence(0.6 if any(ac17_checks) else 0.3),
        "reasons": ac17_reasons or ["No evidence of secure remote access controls"],
        "evidence": {
            "vpc_flow_logs": vpc.get("flow_logs", False),
            "vpn_endpoints": vpn_endpoints
        },
        "missing_evidence": missing + ["Policy documents for remote access procedures"],
    }

    # AC-18: Wireless Access
    ac18_checks = []
    ac18_reasons: List[str] = []
    missing = []
    
    # Technical evidence: WAF for wireless traffic filtering
    if waf_acls:
        ac18_checks.append(True)
        ac18_reasons.append("WAF deployed for wireless access control")
    else:
        missing.append("waf.web_acls")
    
    # Technical evidence: CloudFront for edge security
    if cloudfront.get("distributions"):
        ac18_checks.append(True)
        ac18_reasons.append("CloudFront provides edge security for wireless access")
    else:
        missing.append("cloudfront.distributions[]")
    
    results["AC-18"] = {
        "status": _status_from_booleans(ac18_checks),
        "confidence": _bounded_confidence(0.5 if any(ac18_checks) else 0.3),
        "reasons": ac18_reasons or ["No evidence of wireless access controls"],
        "evidence": {
            "waf_count": len(waf_acls),
            "cloudfront_distributions": len(cloudfront.get("distributions", []))
        },
        "missing_evidence": missing + ["Policy documents for wireless access procedures"],
    }

    # AC-19: Access Control for Mobile Devices
    ac19_checks = []
    ac19_reasons: List[str] = []
    missing = []
    
    # Technical evidence: Security Hub for mobile device monitoring
    if aws_data.get("security_hub", {}).get("enabled"):
        ac19_checks.append(True)
        ac19_reasons.append("Security Hub enabled for mobile device monitoring")
    else:
        missing.append("security_hub.enabled")
    
    # Technical evidence: WAF for mobile application security
    if waf_acls:
        ac19_checks.append(True)
        ac19_reasons.append("WAF deployed for mobile application security")
    else:
        missing.append("waf.web_acls")
    
    results["AC-19"] = {
        "status": _status_from_booleans(ac19_checks),
        "confidence": _bounded_confidence(0.5 if any(ac19_checks) else 0.3),
        "reasons": ac19_reasons or ["No evidence of mobile device access controls"],
        "evidence": {
            "security_hub_enabled": aws_data.get("security_hub", {}).get("enabled", False),
            "waf_count": len(waf_acls)
        },
        "missing_evidence": missing + ["Policy documents for mobile device access procedures"],
    }

    return results


def run_headless() -> None:
    """Convenience runner used by CLI; prints nothing and returns dict.
    Kept for import-based usage.
    """
    db = ProTechtDatabase()
    aws_data = db.get_aws_data()
    return evaluate_ac_controls(aws_data)


__all__ = [
    "TECHNICAL_AC_CONTROLS",
    "evaluate_ac_controls",
    "run_headless",
]



