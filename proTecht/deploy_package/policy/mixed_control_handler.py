from __future__ import annotations

"""Unified mixed control handler that combines policy + technical evidence validation."""

from typing import Dict, List, Optional, Tuple
import sys
import os

from .llm_utils import get_openai_client, extract_json_from_response
from .schema import MIXED_AC_CONTROLS
from .models import ValidationResult

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def validate_mixed_control(
    policy_text: str,
    control_id: str,
    technical_evidence: Optional[Dict] = None,
    assistant_resources: Optional[Dict] = None
) -> ValidationResult:
    """Validate a mixed control using both policy and technical evidence.
    
    Args:
        policy_text: Policy document text
        control_id: Mixed control ID (AC-2, AC-8, AC-17, AC-18, AC-19)
        technical_evidence: Optional technical evidence (AWS logs, configs, etc.)
        assistant_resources: OpenAI assistant resources for policy validation
        
    Returns:
        ValidationResult with combined policy + technical analysis
    """
    if control_id not in MIXED_AC_CONTROLS:
        raise ValueError(f"Control {control_id} is not a mixed control. Use policy-only validation instead.")
    
    # Step 1: Validate policy component
    policy_result = _validate_policy_component(policy_text, control_id, assistant_resources)
    
    # Step 2: Validate technical component (if provided)
    technical_result = _validate_technical_component(control_id, technical_evidence)
    
    # Step 3: Combine results
    combined_result = _combine_validation_results(policy_result, technical_result, control_id)
    
    return combined_result


def _validate_policy_component(
    policy_text: str, 
    control_id: str, 
    assistant_resources: Optional[Dict]
) -> Dict:
    """Validate the policy/document component of a mixed control."""
    # assistant_resources no longer required (file search removed)
    
    client = get_openai_client()
    if not client:
        return {
            "status": "partial", 
            "confidence": 0.3,
            "reasons": ["OpenAI client not available"],
            "missing_elements": ["OpenAI API configuration"],
            "policy_citations": ["Policy analysis not available"],
            "template_citations": ["FedRAMP template access required"],
            "recommendations": ["Configure OpenAI API key"]
        }
    
    try:
        # Get control-specific policy requirements
        policy_requirements = _get_mixed_control_policy_requirements(control_id)
        
        # Construct policy validation query
        query = f"""Validate the POLICY COMPONENT of FedRAMP control {control_id} using the FedRAMP template knowledge.

Policy Document:
{policy_text[:4000]}

Control: {control_id} (MIXED - Policy + Technical Evidence Required)
Policy Requirements: {policy_requirements}

Instructions:
1. Focus ONLY on the policy/document aspects of {control_id}
2. Use your knowledge of the FedRAMP template to understand policy requirements
3. Compare the policy document against policy-specific requirements
4. Do NOT evaluate technical implementation - that's handled separately
5. Provide specific citations from both policy and template

Return JSON with:
{{
  "status": "pass|partial|fail",
  "confidence": 0.0-1.0,
  "reasons": ["List of specific reasons for the policy status"],
  "missing_elements": ["List of missing policy elements"],
  "policy_citations": ["Relevant quotes from the policy document"],
  "template_citations": ["Relevant quotes from FedRAMP template"],
  "recommendations": ["Specific suggestions for policy improvement"]
}}

Status definitions:
- "pass": Policy fully satisfies policy requirements (90%+ coverage)
- "partial": Policy partially satisfies policy requirements (50-89% coverage)  
- "fail": Policy does not adequately address policy requirements (<50% coverage)"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a cybersecurity compliance expert specializing in FedRAMP control {control_id}."},
                {"role": "user", "content": query}
            ],
            max_tokens=800,
            temperature=0.1
        )

        result = extract_json_from_response(response.choices[0].message.content)
        if result and "status" in result:
            return {
                "status": result.get("status", "fail"),
                "confidence": min(max(float(result.get("confidence", 0.5)), 0.0), 1.0),
                "reasons": result.get("reasons", []),
                "missing_elements": result.get("missing_elements", []),
                "policy_citations": result.get("policy_citations", []),
                "template_citations": result.get("template_citations", []),
                "recommendations": result.get("recommendations", [])
            }
        
        # Fallback if JSON parsing fails
        return {
            "status": "partial",
            "confidence": 0.5,
            "reasons": ["Policy validation completed but results could not be parsed"],
            "missing_elements": ["Manual review recommended"],
            "policy_citations": ["Policy analysis completed"],
            "template_citations": ["FedRAMP template analysis completed"],
            "recommendations": ["Review policy manually for completeness"]
        }
        
    except Exception as e:
        return {
            "status": "partial",
            "confidence": 0.3,
            "reasons": [f"Policy validation error: {str(e)}"],
            "missing_elements": ["Policy validation failed"],
            "policy_citations": ["Policy analysis not available"],
            "template_citations": ["FedRAMP template analysis not available"],
            "recommendations": ["Fix policy validation configuration and retry"]
        }


def _validate_technical_component(control_id: str, technical_evidence: Optional[Dict]) -> Dict:
    """Validate the technical component of a mixed control."""
    if not technical_evidence:
        return {
            "status": "fail",
            "confidence": 0.0,
            "reasons": ["Technical evidence not provided"],
            "missing_elements": ["AWS logs, system configurations, screenshots, or technical implementation details"],
            "technical_citations": ["No technical evidence available"],
            "recommendations": ["Provide technical evidence for complete validation"]
        }
    
    # Control-specific technical validation logic
    technical_requirements = _get_mixed_control_technical_requirements(control_id)
    
    # Simple technical evidence validation (can be enhanced)
    technical_score = 0.0
    technical_reasons = []
    technical_missing = []
    technical_citations = []
    
    # Check for required technical evidence based on control
    if control_id == "AC-2":  # Account Management
        if "iam_users" in technical_evidence:
            technical_score += 0.3
            technical_citations.append("IAM users found in technical evidence")
        else:
            technical_missing.append("IAM user management evidence")
            
        if "cloudtrail_logs" in technical_evidence:
            technical_score += 0.3
            technical_citations.append("CloudTrail logs found for account monitoring")
        else:
            technical_missing.append("Account monitoring logs")
            
        if "config_rules" in technical_evidence:
            technical_score += 0.4
            technical_citations.append("Config rules found for account compliance")
        else:
            technical_missing.append("Account compliance monitoring")
    
    elif control_id == "AC-8":  # System Use Notification
        if "system_banners" in technical_evidence:
            technical_score += 0.5
            technical_citations.append("System use notification banners found")
        else:
            technical_missing.append("System use notification implementation")
            
        if "banner_configs" in technical_evidence:
            technical_score += 0.5
            technical_citations.append("Banner configuration evidence found")
        else:
            technical_missing.append("Banner configuration evidence")
    
    elif control_id == "AC-17":  # Remote Access
        if "vpn_configs" in technical_evidence:
            technical_score += 0.3
            technical_citations.append("VPN configuration found")
        else:
            technical_missing.append("VPN configuration evidence")
            
        if "mfa_configs" in technical_evidence:
            technical_score += 0.3
            technical_citations.append("MFA configuration found")
        else:
            technical_missing.append("MFA configuration evidence")
            
        if "session_logs" in technical_evidence:
            technical_score += 0.4
            technical_citations.append("Remote session logs found")
        else:
            technical_missing.append("Remote session monitoring")
    
    elif control_id == "AC-18":  # Wireless Access Restrictions
        if "wireless_configs" in technical_evidence:
            technical_score += 0.4
            technical_citations.append("Wireless access configuration found")
        else:
            technical_missing.append("Wireless access configuration")
            
        if "network_policies" in technical_evidence:
            technical_score += 0.3
            technical_citations.append("Network access policies found")
        else:
            technical_missing.append("Network access policy evidence")
            
        if "access_logs" in technical_evidence:
            technical_score += 0.3
            technical_citations.append("Wireless access logs found")
        else:
            technical_missing.append("Wireless access monitoring")
    
    elif control_id == "AC-19":  # Portable & Mobile Systems
        if "mdm_configs" in technical_evidence:
            technical_score += 0.4
            technical_citations.append("Mobile device management configuration found")
        else:
            technical_missing.append("MDM configuration evidence")
            
        if "device_policies" in technical_evidence:
            technical_score += 0.3
            technical_citations.append("Device access policies found")
        else:
            technical_missing.append("Device access policy evidence")
            
        if "device_logs" in technical_evidence:
            technical_score += 0.3
            technical_citations.append("Device access logs found")
        else:
            technical_missing.append("Device access monitoring")
    
    # Determine technical status
    if technical_score >= 0.8:
        technical_status = "pass"
        technical_reasons.append("Technical evidence adequately covers control requirements")
    elif technical_score >= 0.5:
        technical_status = "partial"
        technical_reasons.append("Technical evidence partially covers control requirements")
    else:
        technical_status = "fail"
        technical_reasons.append("Technical evidence insufficient for control requirements")
    
    return {
        "status": technical_status,
        "confidence": technical_score,
        "reasons": technical_reasons,
        "missing_elements": technical_missing,
        "technical_citations": technical_citations,
        "recommendations": [f"Improve technical evidence coverage for {control_id}"]
    }


def _combine_validation_results(
    policy_result: Dict, 
    technical_result: Dict, 
    control_id: str
) -> ValidationResult:
    """Combine policy and technical validation results into unified result."""
    
    # Calculate combined confidence (weighted average)
    policy_weight = 0.4  # Policy is 40% of mixed control
    technical_weight = 0.6  # Technical is 60% of mixed control
    
    combined_confidence = (
        policy_result["confidence"] * policy_weight + 
        technical_result["confidence"] * technical_weight
    )
    
    # Determine combined status
    policy_status = policy_result["status"]
    technical_status = technical_result["status"]
    
    if policy_status == "pass" and technical_status == "pass":
        combined_status = "pass"
    elif policy_status == "fail" or technical_status == "fail":
        combined_status = "fail"
    else:
        combined_status = "partial"
    
    # Combine reasons
    combined_reasons = []
    combined_reasons.extend([f"Policy: {reason}" for reason in policy_result.get("reasons", [])])
    combined_reasons.extend([f"Technical: {reason}" for reason in technical_result.get("reasons", [])])
    
    # Combine missing elements
    combined_missing = []
    combined_missing.extend(policy_result.get("missing_elements", []))
    combined_missing.extend(technical_result.get("missing_elements", []))
    
    # Combine citations
    combined_policy_citations = policy_result.get("policy_citations", [])
    combined_template_citations = policy_result.get("template_citations", [])
    combined_technical_citations = technical_result.get("technical_citations", [])
    
    # Combine recommendations
    combined_recommendations = []
    combined_recommendations.extend(policy_result.get("recommendations", []))
    combined_recommendations.extend(technical_result.get("recommendations", []))
    
    return ValidationResult(
        control_id=control_id,
        status=combined_status,
        confidence=combined_confidence,
        reasons=combined_reasons,
        missing_elements=combined_missing,
        policy_citations=combined_policy_citations,
        template_citations=combined_template_citations,
        recommendations=combined_recommendations,
        sections_covered=["policy", "technical"]  # Mixed controls cover both
    )


def _get_mixed_control_policy_requirements(control_id: str) -> str:
    """Get policy-specific requirements for mixed controls."""
    requirements = {
        "AC-2": "Account types, account managers, group membership, user authorization, approval process, account lifecycle, monitoring, notifications",
        "AC-8": "System use notification message, banner content, user acknowledgment, privacy notices, security notices",
        "AC-17": "Remote access policy, usage restrictions, configuration requirements, connection requirements, authorization process",
        "AC-18": "Wireless access policy, usage restrictions, configuration requirements, connection requirements, authorization process", 
        "AC-19": "Mobile device policy, usage restrictions, configuration requirements, connection requirements, device authorization"
    }
    return requirements.get(control_id, "Policy requirements not defined")


def _get_mixed_control_technical_requirements(control_id: str) -> List[str]:
    """Get technical-specific requirements for mixed controls."""
    requirements = {
        "AC-2": ["IAM user management", "CloudTrail logs", "Config rules", "Account monitoring"],
        "AC-8": ["System banners", "Banner configuration", "User acknowledgment system"],
        "AC-17": ["VPN configuration", "MFA setup", "Session management", "Remote access logs"],
        "AC-18": ["Wireless configuration", "Network policies", "Access monitoring"],
        "AC-19": ["MDM configuration", "Device policies", "Device monitoring"]
    }
    return requirements.get(control_id, [])
