from __future__ import annotations

"""Database-powered Access Control (AC) control mapping with FedRAMP template from database."""

import re
from typing import List, Tuple, Optional
import sys
import os

from .llm_utils import get_openai_client, extract_json_from_response
from .schema import NON_TECHNICAL_AC_CONTROLS, MIXED_AC_CONTROLS, ALL_AC_CONTROLS
from .cache import cache_llm_result

# Add src to path for imports
_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _src_path)
from database import ProTechtDatabase

CONTROL_ID_RE = re.compile(r"\b([A-Z]{2}-\d{1,2})\b")


@cache_llm_result("primary_control_identification", ttl_seconds=3600)  # Cache for 1 hour
def identify_primary_control(text: str) -> Tuple[str, float]:
    """Identify the PRIMARY FedRAMP Access Control (AC) control using LLM with database template.
    
    Args:
        text: Full policy document text
        
    Returns: (primary_ac_control_id, confidence_score) tuple
    
    Raises:
        ValueError: If LLM client is unavailable or analysis fails
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
        
        # Query to identify the SINGLE primary control
        query = f"""Analyze this COMPLETE policy document and identify the ONE PRIMARY FedRAMP Access Control (AC) control it is designed to address.

Complete Policy Document:
{text[:4000]}

FedRAMP Template Context (for reference):
{template_content}

Instructions:
1. Read the entire policy document carefully
2. Identify what the PRIMARY purpose of this policy is
3. Map it to exactly ONE FedRAMP Access Control (AC) family control
4. Use the FedRAMP template context to understand control requirements
5. PRIORITIZE NON-TECHNICAL controls that can be validated from policy documents alone:

NON-TECHNICAL AC CONTROLS (Policy/Document Driven):
   - AC-1: Access Control Policy and Procedures
   - AC-14: Permitted Actions without Identification or Authentication
   - AC-20: Use of External Information Systems
   - AC-22: Publicly Accessible Content

MIXED CONTROLS (Need Both Technical + Non-Technical Evidence):
   - AC-2: Account Management
   - AC-8: System Use Notification
   - AC-17: Remote Access
   - AC-18: Wireless Access Restrictions
   - AC-19: Access Control for Portable and Mobile Systems

IMPORTANT: If you identify a MIXED control, explain that it requires both policy documents AND technical evidence (AWS logs, system configurations, etc.) for complete validation.

Return JSON with the SINGLE primary control:
{{
  "primary_control": "AC-1",
  "confidence": 0.90,
  "reasoning": "This is clearly an access control policy document that establishes procedures and responsibilities for managing user access",
  "control_type": "non-technical|mixed",
  "validation_note": "Can be validated from policy documents alone" or "Requires both policy documents and technical evidence"
}}

Only return the ONE Access Control (AC) family control this policy is primarily about. Be confident in your assessment."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "You are a cybersecurity compliance expert specializing in FedRAMP Access Control (AC) family controls. Analyze policy documents and identify the single primary AC control they address."
            }, {
                "role": "user",
                "content": query
            }],
            max_tokens=500,
            temperature=0.1
        )
        
        result = extract_json_from_response(response.choices[0].message.content)
        if result and "primary_control" in result and "confidence" in result:
            control_id = result["primary_control"]
            confidence = float(result["confidence"])
            control_type = result.get("control_type", "unknown")
            
            # Accept both non-technical and mixed controls, but prefer non-technical
            if control_id in ALL_AC_CONTROLS and confidence >= 0.3:
                # Check if it's a mixed control and provide guidance
                if control_id in MIXED_AC_CONTROLS:
                    print(f"⚠️  Note: {control_id} is a MIXED control requiring both policy documents AND technical evidence for complete validation.")
                
                return (control_id, min(confidence, 1.0))
        
        # If we get here, the LLM response was invalid
        raise ValueError(f"LLM returned invalid response for control identification")
                
    except Exception as e:
        raise ValueError(f"Error in LLM control identification: {e}")


def get_assistant_resources() -> Optional[dict]:
    """Get assistant resources - now returns database info instead of OpenAI resources"""
    try:
        db = ProTechtDatabase()
        template_data = db.get_fedramp_template("FedRAMP-SSP-Low-Baseline-Template-v1.1")
        
        if template_data:
            return {
                "template_name": template_data['template_name'],
                "template_type": template_data['template_type'],
                "template_size": template_data['file_size'],
                "upload_date": template_data['upload_date']
            }
        return None
        
    except Exception as e:
        print(f"Warning: Could not get database template info: {e}")
        return None
