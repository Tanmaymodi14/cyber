#!/usr/bin/env python3
"""
Database-Powered Policy Analysis CLI
Analyze Access Control (AC) policy documents against FedRAMP AC controls using database-stored template
"""

import sys
import os
import argparse
from pathlib import Path
import PyPDF2
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text content from a PDF file."""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Analyze Access Control (AC) policy documents against FedRAMP AC controls using database-stored template')
    parser.add_argument('policy_file', help='Path to policy document (.txt or .pdf file)')
    parser.add_argument('--name', '-n', help='Policy name (optional, uses filename if not provided)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed analysis')
    parser.add_argument('--json', '-j', action='store_true', help='Output results as JSON')
    parser.add_argument('--technical-evidence', '-t', help='Path to technical evidence JSON file (for mixed controls)')
    parser.add_argument('--unified', '-u', action='store_true', help='Use unified analysis (policy + technical evidence)')
    
    args = parser.parse_args()

    policy_path = Path(args.policy_file)
    if not policy_path.exists():
        print(f"❌ Error: File '{args.policy_file}' not found")
        sys.exit(1)
    
    # Validate file format
    supported_extensions = ['.txt', '.pdf']
    if policy_path.suffix.lower() not in supported_extensions:
        print(f"❌ Error: Unsupported file format. Supported: {', '.join(supported_extensions)}")
        sys.exit(1)
    
    # Determine policy name
    policy_name = args.name or policy_path.stem
    
    try:
        # Load technical evidence if provided
        technical_evidence = None
        if args.technical_evidence:
            try:
                with open(args.technical_evidence, 'r') as f:
                    technical_evidence = json.load(f)
                if not args.json:
                    print(f"📊 Loaded technical evidence from: {args.technical_evidence}")
            except Exception as e:
                print(f"❌ Error loading technical evidence: {e}")
                sys.exit(1)
        
        # Read policy file based on format
        if policy_path.suffix.lower() == '.pdf':
            policy_text = extract_text_from_pdf(policy_path)
        else:  # .txt
            with open(policy_path, 'r', encoding='utf-8') as f:
                policy_text = f.read()
        
        if not policy_text.strip():
            print(f"❌ Error: Policy file appears to be empty")
            sys.exit(1)
        
        if not args.json:
            print(f"🔍 Analyzing policy: {policy_name}")
            print(f"📄 File: {policy_path}")
            if technical_evidence:
                print("🔧 Technical evidence: Provided")
            print("⏳ Running database-powered AI analysis...")
        
        # Use database-powered analysis
        from policy.analyzer import analyze_access_control_policy
        report = analyze_access_control_policy(policy_name, policy_text, quiet=args.json)
        
        if args.json:
            # Output JSON format
            result = {
                'policy_name': report.policy_name,
                'summary': report.summary,
                'controls': [
                    {
                        'control_id': control.control_id,
                        'status': control.status,
                        'confidence': control.confidence,
                        'reasons': control.reasons,
                        'missing_elements': control.missing_elements,
                        'policy_citations': control.policy_citations,
                        'template_citations': control.template_citations,
                        'recommendations': control.recommendations,
                        'sections_covered': control.sections_covered
                    }
                    for control in report.controls
                ]
            }
            print(json.dumps(result, indent=2))
        else:
            # Output human-readable format
            _print_report(report, args.verbose)
            
    except ValueError as ve:
        print(f"❌ Error during analysis: {ve}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)


def _print_report(report, verbose=False):
    """Print a human-readable report"""
    print(f"\n{'='*60}")
    print(f"📋 POLICY ANALYSIS REPORT: {report.policy_name}")
    print(f"{'='*60}")
    
    # Summary
    summary = report.summary
    print(f"\n📊 SUMMARY:")
    print(f"  Total Controls: {summary['total_controls']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Partial: {summary['partial']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Compliance: {summary['compliance_pct']}%")
    print(f"  Avg Confidence: {summary['avg_confidence']:.2f}")
    
    # Controls
    print(f"\n🎯 CONTROLS:")
    for control in report.controls:
        status_emoji = {"pass": "✅", "partial": "⚠️", "fail": "❌"}.get(control.status, "❓")
        print(f"\n  {status_emoji} {control.control_id}: {control.status.upper()} (confidence: {control.confidence:.2f})")
        
        if control.reasons:
            print(f"    Reasons:")
            for reason in control.reasons:
                print(f"      • {reason}")
        
        if control.missing_elements:
            print(f"    Missing Elements:")
            for element in control.missing_elements:
                print(f"      • {element}")
        
        if verbose and control.policy_citations:
            print(f"    Policy Citations:")
            for citation in control.policy_citations:
                print(f"      • {citation}")
        
        if verbose and control.template_citations:
            print(f"    Template Citations:")
            for citation in control.template_citations:
                print(f"      • {citation}")
        
        if control.recommendations:
            print(f"    Recommendations:")
            for rec in control.recommendations:
                print(f"      • {rec}")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
