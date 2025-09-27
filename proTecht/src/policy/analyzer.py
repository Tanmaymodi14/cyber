from __future__ import annotations

"""Database-powered Access Control (AC) policy analysis pipeline."""

from typing import List, Dict, Any, Optional
import sys
import os

from .llm_utils import split_document_intelligently
from .router import classify_section
from .mapper import identify_primary_control, get_assistant_resources
from .validator import validate_section_against_control
from .mixed_control_handler import validate_mixed_control
from .models import PolicyReport, ValidationResult, Section
from .schema import NON_TECHNICAL_AC_CONTROLS, MIXED_AC_CONTROLS

# Add src to path for imports
_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _src_path)
from database import ProTechtDatabase


def analyze_access_control_policy(policy_name: str, text: str, *, quiet: bool = False) -> PolicyReport:
    """End-to-end database-powered Access Control (AC) policy analysis pipeline.
    
    Args:
        policy_name: Name of the Access Control policy document
        text: Policy document text content
        quiet: Suppress verbose output
        
    Returns: PolicyReport with validation results for the primary AC control
        
    Raises:
        ValueError: If database template is unavailable or analysis fails
    """
    if not quiet:
        print(f"Starting database-powered AC policy analysis: {policy_name}")
    
    # Check if FedRAMP template is available in database
    db = ProTechtDatabase()
    template_data = db.get_fedramp_template("FedRAMP-SSP-Low-Baseline-Template-v1.1")
    if not template_data:
        raise ValueError("FedRAMP template not found in database. Please run store_fedramp_template.py first.")
    
    if not quiet:
        print("Using database-powered AC analysis with FedRAMP template")
        print(f"Template: {template_data['template_name']} ({template_data['file_size']:,} bytes)")
    
    try:
        # Step 1: Intelligent document splitting
        if not quiet:
            print("Step 1: Splitting document into logical sections...")
        section_data = split_document_intelligently(text)
        sections = [
            Section(section_id=sid, title=title, text=content)
            for sid, title, content in section_data
        ]
        if not quiet:
            print(f"Created {len(sections)} sections")
    
        # Step 2: Route sections (technical vs non-technical)
        if not quiet:
            print("Step 2: Classifying sections...")
        
        # Skip classification for small documents or single sections
        if len(sections) == 1 and len(sections[0].text) < 1000:
            if not quiet:
                print("  Skipping classification for small document")
            sections[0].label = "non-technical"
            sections[0].confidence = 0.8
        else:
            for section in sections:
                label, confidence = classify_section(section.text)
                section.label = label
                section.confidence = confidence
                if not quiet:
                    print(f"  {section.section_id}: {label} (confidence: {confidence:.2f})")
        
        # Step 3: Identify the PRIMARY AC control this policy addresses
        if not quiet:
            print("Step 3: Identifying primary Access Control (AC) control...")
        
        # Use the full document text to identify the primary AC control
        primary_control, confidence = identify_primary_control(text)
        
        if not quiet:
            print(f"  Primary AC Control: {primary_control} (confidence: {confidence:.2f})")
        
        # Step 4: Validate the entire policy against the primary AC control
        if not quiet:
            print(f"Step 4: Validating policy against {primary_control} requirements...")
        
        # Validate the entire policy text against the primary control
        validation = validate_section_against_control(text, primary_control)
        
        # Adjust confidence based on primary control identification confidence
        validation["confidence"] = min(validation["confidence"] * confidence, 1.0)
        
        # Create single validation result
        result = ValidationResult(
            control_id=primary_control,
            status=validation["status"],
            confidence=validation["confidence"],
            reasons=validation.get("reasons", []),
            missing_elements=validation.get("missing_elements", []),
            policy_citations=validation.get("policy_citations", []),
            template_citations=validation.get("template_citations", []),
            recommendations=validation.get("recommendations", []),
            sections_covered=[s.section_id for s in sections]  # All sections contribute to the single control
        )
        
        validation_results = [result]
        
        if not quiet:
            print(f"  {primary_control}: {result.status} (confidence: {result.confidence:.2f})")
            if result.missing_elements:
                print(f"    Missing: {', '.join(result.missing_elements)}")
        
        # Step 5: Generate summary
        summary = _build_summary(validation_results)
        if not quiet:
            print(f"Analysis complete: {summary['compliance_pct']}% compliance for {primary_control}")
        
        return PolicyReport(
            policy_name=policy_name,
            controls=validation_results,
            summary=summary
        )
    except ValueError as ve:
        raise ValueError(f"Policy analysis failed: {ve}")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred during policy analysis: {e}")


def _build_summary(controls: List[ValidationResult]) -> Dict[str, Any]:
    """Helper to build a summary of validation results."""
    total_controls = len(controls)
    passed = sum(1 for c in controls if c.status == "pass")
    partial = sum(1 for c in controls if c.status == "partial")
    failed = sum(1 for c in controls if c.status == "fail")
    
    compliance_pct = 0.0
    if total_controls > 0:
        compliance_pct = (passed * 100.0) + (partial * 50.0) / total_controls
    
    avg_confidence = sum(c.confidence for c in controls) / total_controls if total_controls > 0 else 0.0
    
    return {
        "total_controls": total_controls,
        "passed": passed,
        "partial": partial,
        "failed": failed,
        "compliance_pct": round(compliance_pct, 1),
        "avg_confidence": round(avg_confidence, 2)
    }
