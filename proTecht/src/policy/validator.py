from __future__ import annotations

"""Database-powered policy validation with FedRAMP template from database."""

import re
from typing import Dict, Any, Optional
import sys
import os

from .llm_utils import get_openai_client, extract_json_from_response
from .schema import CHECKLISTS, MIXED_AC_CONTROLS
from .cache import cache_llm_result

# Add src to path for imports
_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _src_path)
from database import ProTechtDatabase


@cache_llm_result("policy_validation", ttl_seconds=3600)  # Cache for 1 hour
def validate_section_against_control(
    section_text: str, 
    control_id: str, 
    technical_evidence: Optional[Dict] = None
) -> Dict:
    """Validate policy section against FedRAMP control requirements using LLM + database template.
    
    Args:
        section_text: Policy section text to validate
        control_id: FedRAMP control ID (e.g., "AC-1")
        technical_evidence: Optional dictionary of technical evidence for mixed controls
        
    Returns: Dict with validation results
    
    Raises:
        ValueError: If LLM client is unavailable or validation fails
    """
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI client is not available. Please check your API key and configuration.")
    
    try:
        # Get FedRAMP template from database
        db = ProTechtDatabase()
        template_data = db.get_fedramp_template("FedRAMP-SSP-Low-Baseline-Template-v1.1")
        
        if not template_data:
            raise ValueError("FedRAMP template not found in database. Please run store_fedramp_template.py first.")
        
        # Extract template content (first 4000 chars for context)
        template_content = template_data['file_content'].decode('utf-8', errors='ignore')[:4000]
        
        # Check if this is a mixed control that needs both policy and technical evidence
        if control_id in MIXED_AC_CONTROLS:
            # Use the unified mixed control handler
            # Note: technical_evidence would need to be passed in from the caller
            # For now, we'll provide guidance about needing technical evidence
            return {
                "status": "partial",
                "confidence": 0.5,
                "reasons": [f"{control_id} is a MIXED control requiring both policy documents AND technical evidence for complete validation. This analysis covers only the policy/document aspects."],
                "missing_elements": ["Technical evidence required: AWS logs, system configurations, screenshots, or technical implementation details"],
                "policy_citations": ["Policy analysis limited to document-based requirements"],
                "template_citations": [f"{control_id} requires both policy and technical implementation evidence"],
                "recommendations": [f"To fully validate {control_id}, you need both this policy document AND technical evidence from your AWS/system logs."]
            }
        
        # Get control checklist for context
        checklist = CHECKLISTS.get(control_id, {})
        required_sections = checklist.get("sections_required", [])
        key_elements = checklist.get("key_elements", [])
        audit_focus = checklist.get("audit_focus", "Policy documents and procedures")
        
        # Construct validation query
        query = f"""Validate this policy document against FedRAMP control {control_id} requirements using the FedRAMP template knowledge.

Policy Document:
{section_text[:4000]}

FedRAMP Template Context (for reference):
{template_content}

Control: {control_id} (NON-TECHNICAL - Policy/Document Driven)
Required Sections: {', '.join(required_sections) if required_sections else 'Not specified'}
Key Elements: {', '.join(key_elements) if key_elements else 'Not specified'}
Audit Focus: {audit_focus}

Instructions:
1. Use the FedRAMP template context to understand {control_id} requirements
2. Focus ONLY on policy/document-based requirements (no technical implementation needed)
3. Compare the entire policy document against these requirements
4. Determine if the policy adequately addresses the control from a documentation perspective
5. Identify any missing elements or gaps in the policy documentation
6. Provide specific citations from both the policy and template
7. Be thorough but fair in your assessment - this is a NON-TECHNICAL control

Return JSON with:
{{
  "status": "pass|partial|fail",
  "confidence": 0.0-1.0,
  "reasons": ["List of specific reasons for the status"],
  "missing_elements": ["List of missing required elements"],
  "policy_citations": ["Relevant quotes from the policy document"],
  "template_citations": ["Relevant quotes from FedRAMP template"],
  "recommendations": ["Specific suggestions for improvement"]
}}

Status definitions:
- "pass": Policy fully satisfies control requirements (90%+ coverage)
- "partial": Policy partially satisfies requirements but has gaps (50-89% coverage)
- "fail": Policy does not adequately address control requirements (<50% coverage)"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": f"You are a cybersecurity compliance expert specializing in FedRAMP control {control_id}. Validate policy documents against FedRAMP requirements using the provided template context."
            }, {
                "role": "user",
                "content": query
            }],
            max_tokens=500,  # Reduced token limit
            temperature=0.1
        )
        
        result = extract_json_from_response(response.choices[0].message.content)
        if result and "status" in result:
            # Validate and sanitize response
            status = result.get("status", "fail")
            if status not in ["pass", "partial", "fail"]:
                status = "fail"
                
            return {
                "status": status,
                "confidence": min(max(float(result.get("confidence", 0.5)), 0.0), 1.0),
                "reasons": result.get("reasons", []),
                "missing_elements": result.get("missing_elements", []),
                "policy_citations": result.get("policy_citations", []),
                "template_citations": result.get("template_citations", []),
                "recommendations": result.get("recommendations", [])
            }
        
        # If we get here, the LLM response was invalid - provide fallback
        print(f"Warning: LLM returned invalid JSON response. Raw response: {response.choices[0].message.content[:200]}...")
        return {
            "status": "partial",
            "confidence": 0.5,
            "reasons": ["LLM response could not be parsed - manual review recommended"],
            "missing_elements": ["Unable to determine due to parsing error"],
            "policy_citations": ["Response parsing failed"],
            "template_citations": ["Response parsing failed"],
            "recommendations": ["Please review the policy manually and try again"]
        }
                
    except Exception as e:
        raise ValueError(f"Error in LLM validation: {e}")
