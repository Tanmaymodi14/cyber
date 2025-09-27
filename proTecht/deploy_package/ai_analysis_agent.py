#!/usr/bin/env python3
"""
AI-Powered Analysis Agent for Detailed AC Control Explanations
Provides comprehensive reasoning, evidence, and recommendations for each control.
"""

from __future__ import annotations
import json
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

# Add src to path for imports
_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, _src_path)

from database import ProTechtDatabase
from technical_engine import evaluate_ac_controls

@dataclass
class ControlEvidence:
    """Evidence collected for a specific control."""
    control_id: str
    evidence_type: str  # 'aws_resource', 'configuration', 'policy', 'log'
    resource_name: str
    status: str  # 'compliant', 'non_compliant', 'partial'
    details: Dict[str, Any]
    confidence: float

@dataclass
class DetailedAnalysis:
    """Detailed analysis result for a control."""
    control_id: str
    control_name: str
    overall_status: str  # 'pass', 'fail', 'partial'
    confidence: float
    evidence_summary: str
    compliance_reasoning: str
    specific_checks_performed: List[str]
    missing_requirements: List[str]
    recommendations: List[str]
    evidence_details: List[ControlEvidence]
    fedramp_requirements: str

class AIAnalysisAgent:
    """AI-powered agent for detailed AC control analysis."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if OpenAI is None or not key:
            raise RuntimeError("AI analysis disabled: OpenAI client not available")
        self.client = OpenAI(api_key=key)
        self.db = ProTechtDatabase()
        
    def analyze_control_detailed(self, control_id: str, aws_data: Dict[str, Any]) -> DetailedAnalysis:
        """Perform detailed AI analysis of a single AC control."""
        
        # Get FedRAMP requirements for the control
        fedramp_requirements = self._get_fedramp_requirements(control_id)
        
        # Collect evidence for this control
        evidence = self._collect_control_evidence(control_id, aws_data)
        
        # Generate AI analysis
        analysis = self._generate_ai_analysis(control_id, evidence, fedramp_requirements)
        
        return analysis
    
    def _get_fedramp_requirements(self, control_id: str) -> str:
        """Get FedRAMP requirements for a control."""
        requirements = {
            "AC-3": "The information system enforces approved authorizations for logical access to information and system resources in accordance with applicable access control policies.",
            "AC-4": "The information system enforces approved authorizations for controlling the flow of information between interconnected systems based on organization-defined information flow control policies.",
            "AC-5": "The organization separates duties of individuals as necessary to prevent malevolent activity without collusion.",
            "AC-6": "The organization employs the principle of least privilege, allowing only authorized accesses for users (and processes acting on behalf of users) which are necessary to accomplish assigned organizational tasks.",
            "AC-7": "The information system enforces a limit of [Assignment: organization-defined number] consecutive invalid logon attempts by a user during a [Assignment: organization-defined time period].",
            "AC-9": "The information system displays to users [Assignment: organization-defined information] before granting access to the system.",
            "AC-10": "The information system limits the number of concurrent sessions for each [Assignment: organization-defined account and/or account type] to [Assignment: organization-defined number].",
            "AC-11": "The information system terminates a user session after [Assignment: organization-defined time period] of inactivity.",
            "AC-12": "The information system prevents further access to the system by [Assignment: organization-defined time period] after session termination.",
            "AC-13": "The organization employs automated mechanisms to facilitate the monitoring and control of user actions.",
            "AC-15": "The organization employs [Assignment: organization-defined automated mechanisms] to support the management of remote access sessions.",
            "AC-16": "The information system enforces [Assignment: organization-defined security attributes] on information and information systems.",
            "AC-21": "The information system prevents the display of system information to users, roles, or processes that do not have a need to know."
        }
        return requirements.get(control_id, "FedRAMP requirement not found")
    
    def _collect_control_evidence(self, control_id: str, aws_data: Dict[str, Any]) -> List[ControlEvidence]:
        """Collect evidence for a specific control."""
        evidence = []
        
        if control_id == "AC-3":
            # Access Enforcement
            if 'iam' in aws_data:
                iam_data = aws_data['iam']
                if 'users' in iam_data:
                    evidence.append(ControlEvidence(
                        control_id="AC-3",
                        evidence_type="aws_resource",
                        resource_name="IAM Users",
                        status="compliant" if len(iam_data['users']) > 0 else "non_compliant",
                        details={"user_count": len(iam_data['users']), "users": iam_data['users'][:5]},
                        confidence=0.8
                    ))
                if 'roles' in iam_data:
                    evidence.append(ControlEvidence(
                        control_id="AC-3",
                        evidence_type="aws_resource",
                        resource_name="IAM Roles",
                        status="compliant" if len(iam_data['roles']) > 0 else "non_compliant",
                        details={"role_count": len(iam_data['roles']), "roles": iam_data['roles'][:5]},
                        confidence=0.8
                    ))
        
        elif control_id == "AC-4":
            # Information Flow Enforcement
            if 'vpc' in aws_data:
                vpc_data = aws_data['vpc']
                evidence.append(ControlEvidence(
                    control_id="AC-4",
                    evidence_type="aws_resource",
                    resource_name="VPC Flow Logs",
                    status="compliant" if vpc_data.get('flow_logs', 0) > 0 else "non_compliant",
                    details={"flow_logs_enabled": vpc_data.get('flow_logs', 0) > 0},
                    confidence=0.7
                ))
            if 'waf' in aws_data:
                waf_data = aws_data['waf']
                evidence.append(ControlEvidence(
                    control_id="AC-4",
                    evidence_type="aws_resource",
                    resource_name="WAF WebACLs",
                    status="compliant" if len(waf_data.get('web_acls', [])) > 0 else "non_compliant",
                    details={"web_acl_count": len(waf_data.get('web_acls', []))},
                    confidence=0.7
                ))
        
        elif control_id == "AC-5":
            # Separation of Duties
            if 'iam' in aws_data:
                iam_data = aws_data['iam']
                if 'roles' in iam_data:
                    evidence.append(ControlEvidence(
                        control_id="AC-5",
                        evidence_type="aws_resource",
                        resource_name="IAM Role Separation",
                        status="compliant" if len(iam_data['roles']) > 1 else "partial",
                        details={"role_count": len(iam_data['roles']), "separation_implemented": len(iam_data['roles']) > 1},
                        confidence=0.6
                    ))
        
        elif control_id == "AC-6":
            # Least Privilege
            if 'iam' in aws_data:
                iam_data = aws_data['iam']
                if 'users' in iam_data:
                    # Check for least privilege implementation
                    admin_users = [u for u in iam_data['users'] if u.get('access_level') == 'admin']
                    standard_users = [u for u in iam_data['users'] if u.get('access_level') == 'standard']
                    evidence.append(ControlEvidence(
                        control_id="AC-6",
                        evidence_type="aws_resource",
                        resource_name="User Access Levels",
                        status="compliant" if len(standard_users) > len(admin_users) else "partial",
                        details={"admin_count": len(admin_users), "standard_count": len(standard_users)},
                        confidence=0.7
                    ))
        
        elif control_id == "AC-7":
            # Unsuccessful Logon Attempts
            if 'iam' in aws_data:
                iam_data = aws_data['iam']
                password_policy = iam_data.get('password_policy', {})
                evidence.append(ControlEvidence(
                    control_id="AC-7",
                    evidence_type="configuration",
                    resource_name="Password Policy",
                    status="compliant" if password_policy.get('MinimumPasswordLength', 0) >= 8 else "non_compliant",
                    details=password_policy,
                    confidence=0.9
                ))
        
        elif control_id == "AC-9":
            # Information on Previous Logon
            if 'cloudtrail' in aws_data:
                ct_data = aws_data['cloudtrail']
                evidence.append(ControlEvidence(
                    control_id="AC-9",
                    evidence_type="aws_resource",
                    resource_name="CloudTrail Logging",
                    status="compliant" if ct_data.get('trails', []) else "non_compliant",
                    details={"trail_count": len(ct_data.get('trails', []))},
                    confidence=0.8
                ))
        
        elif control_id == "AC-10":
            # Concurrent Session Control
            if 'iam' in aws_data:
                iam_data = aws_data['iam']
                evidence.append(ControlEvidence(
                    control_id="AC-10",
                    evidence_type="configuration",
                    resource_name="Session Management",
                    status="partial",  # Requires IdP configuration
                    details={"session_control_available": True},
                    confidence=0.5
                ))
        
        elif control_id == "AC-11":
            # Session Lock
            evidence.append(ControlEvidence(
                control_id="AC-11",
                evidence_type="configuration",
                resource_name="Session Timeout",
                status="partial",  # Requires application-level configuration
                details={"session_lock_available": True},
                confidence=0.5
            ))
        
        elif control_id == "AC-12":
            # Session Termination
            evidence.append(ControlEvidence(
                control_id="AC-12",
                evidence_type="configuration",
                resource_name="Session Termination",
                status="partial",  # Requires application-level configuration
                details={"session_termination_available": True},
                confidence=0.5
            ))
        
        elif control_id == "AC-13":
            # Monitoring and Control
            if 'guardduty' in aws_data:
                gd_data = aws_data['guardduty']
                evidence.append(ControlEvidence(
                    control_id="AC-13",
                    evidence_type="aws_resource",
                    resource_name="GuardDuty",
                    status="compliant" if gd_data.get('detector_count', 0) > 0 else "non_compliant",
                    details={"detector_count": gd_data.get('detector_count', 0)},
                    confidence=0.8
                ))
            if 'security_hub' in aws_data:
                sh_data = aws_data['security_hub']
                evidence.append(ControlEvidence(
                    control_id="AC-13",
                    evidence_type="aws_resource",
                    resource_name="Security Hub",
                    status="compliant" if sh_data.get('enabled', False) else "non_compliant",
                    details={"enabled": sh_data.get('enabled', False)},
                    confidence=0.8
                ))
        
        elif control_id == "AC-15":
            # Remote Access Management
            if 's3' in aws_data:
                s3_data = aws_data['s3']
                evidence.append(ControlEvidence(
                    control_id="AC-15",
                    evidence_type="aws_resource",
                    resource_name="S3 Object Lock",
                    status="compliant" if s3_data.get('object_lock_enabled', False) else "partial",
                    details={"object_lock_enabled": s3_data.get('object_lock_enabled', False)},
                    confidence=0.6
                ))
        
        elif control_id == "AC-16":
            # Security Attributes
            if 's3' in aws_data:
                s3_data = aws_data['s3']
                encrypted_buckets = [b for b in s3_data.get('buckets', []) if b.get('encryption_enabled', False)]
                evidence.append(ControlEvidence(
                    control_id="AC-16",
                    evidence_type="aws_resource",
                    resource_name="S3 Encryption",
                    status="compliant" if len(encrypted_buckets) > 0 else "non_compliant",
                    details={"encrypted_bucket_count": len(encrypted_buckets), "total_buckets": len(s3_data.get('buckets', []))},
                    confidence=0.8
                ))
            if 'kms' in aws_data:
                kms_data = aws_data['kms']
                rotating_keys = [k for k in kms_data.get('keys', []) if k.get('rotation_enabled', False)]
                evidence.append(ControlEvidence(
                    control_id="AC-16",
                    evidence_type="aws_resource",
                    resource_name="KMS Key Rotation",
                    status="compliant" if len(rotating_keys) > 0 else "partial",
                    details={"rotating_key_count": len(rotating_keys), "total_keys": len(kms_data.get('keys', []))},
                    confidence=0.8
                ))
        
        elif control_id == "AC-21":
            # Information Display
            if 'waf' in aws_data:
                waf_data = aws_data['waf']
                evidence.append(ControlEvidence(
                    control_id="AC-21",
                    evidence_type="aws_resource",
                    resource_name="WAF Information Control",
                    status="compliant" if len(waf_data.get('web_acls', [])) > 0 else "non_compliant",
                    details={"web_acl_count": len(waf_data.get('web_acls', []))},
                    confidence=0.7
                ))
            if 's3' in aws_data:
                s3_data = aws_data['s3']
                public_buckets = [b for b in s3_data.get('buckets', []) if b.get('public_access', False)]
                evidence.append(ControlEvidence(
                    control_id="AC-21",
                    evidence_type="aws_resource",
                    resource_name="S3 Public Access Control",
                    status="non_compliant" if len(public_buckets) > 0 else "compliant",
                    details={"public_bucket_count": len(public_buckets)},
                    confidence=0.9
                ))
        
        return evidence
    
    def _generate_ai_analysis(self, control_id: str, evidence: List[ControlEvidence], fedramp_requirements: str) -> DetailedAnalysis:
        """Generate AI-powered detailed analysis."""
        
        # Prepare evidence summary
        evidence_summary = self._summarize_evidence(evidence)
        
        # Create AI prompt
        prompt = f"""
        You are a FedRAMP compliance expert analyzing AC control {control_id}.
        
        FedRAMP Requirement: {fedramp_requirements}
        
        Evidence Collected:
        {evidence_summary}
        
        Please provide a detailed analysis including:
        1. Overall compliance status (pass/fail/partial) with confidence score
        2. Specific checks performed and what was examined
        3. Detailed reasoning for the compliance decision
        4. Missing requirements that need to be addressed
        5. Specific recommendations for improvement
        6. Evidence interpretation and validation
        
        Format your response as JSON with these fields:
        - overall_status: "pass", "fail", or "partial"
        - confidence: float between 0.0 and 1.0
        - specific_checks_performed: list of specific checks
        - compliance_reasoning: detailed explanation
        - missing_requirements: list of missing items
        - recommendations: list of specific recommendations
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            
            return DetailedAnalysis(
                control_id=control_id,
                control_name=f"AC-{control_id.split('-')[1]}",
                overall_status=ai_response.get('overall_status', 'partial'),
                confidence=ai_response.get('confidence', 0.5),
                evidence_summary=evidence_summary,
                compliance_reasoning=ai_response.get('compliance_reasoning', 'Analysis pending'),
                specific_checks_performed=ai_response.get('specific_checks_performed', []),
                missing_requirements=ai_response.get('missing_requirements', []),
                recommendations=ai_response.get('recommendations', []),
                evidence_details=evidence,
                fedramp_requirements=fedramp_requirements
            )
            
        except Exception as e:
            # Fallback analysis if AI fails
            return DetailedAnalysis(
                control_id=control_id,
                control_name=f"AC-{control_id.split('-')[1]}",
                overall_status="partial",
                confidence=0.3,
                evidence_summary=evidence_summary,
                compliance_reasoning=f"AI analysis failed: {str(e)}. Manual review required.",
                specific_checks_performed=["Evidence collection completed"],
                missing_requirements=["AI analysis unavailable"],
                recommendations=["Enable AI analysis or perform manual review"],
                evidence_details=evidence,
                fedramp_requirements=fedramp_requirements
            )
    
    def _summarize_evidence(self, evidence: List[ControlEvidence]) -> str:
        """Summarize collected evidence for AI analysis."""
        if not evidence:
            return "No evidence collected"
        
        summary = []
        for ev in evidence:
            status_emoji = "✅" if ev.status == "compliant" else "❌" if ev.status == "non_compliant" else "⚠️"
            summary.append(f"{status_emoji} {ev.resource_name}: {ev.status} (confidence: {ev.confidence:.2f})")
            if ev.details:
                summary.append(f"   Details: {json.dumps(ev.details, indent=2)}")
        
        return "\n".join(summary)
    
    def analyze_all_controls_detailed(self, aws_data: Dict[str, Any]) -> List[DetailedAnalysis]:
        """Perform detailed analysis of all AC controls."""
        control_ids = ["AC-3", "AC-4", "AC-5", "AC-6", "AC-7", "AC-9", "AC-10", "AC-11", "AC-12", "AC-13", "AC-15", "AC-16", "AC-21"]
        
        analyses = []
        for control_id in control_ids:
            print(f"🔍 Analyzing {control_id}...")
            analysis = self.analyze_control_detailed(control_id, aws_data)
            analyses.append(analysis)
        
        return analyses
    
    def generate_detailed_report(self, analyses: List[DetailedAnalysis]) -> str:
        """Generate a comprehensive detailed report."""
        report = []
        report.append("=" * 80)
        report.append("🤖 AI-POWERED DETAILED AC CONTROL ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        total_controls = len(analyses)
        passed_controls = len([a for a in analyses if a.overall_status == "pass"])
        failed_controls = len([a for a in analyses if a.overall_status == "fail"])
        partial_controls = len([a for a in analyses if a.overall_status == "partial"])
        avg_confidence = sum(a.confidence for a in analyses) / len(analyses)
        
        report.append("📊 EXECUTIVE SUMMARY:")
        report.append(f"  Total Controls Analyzed: {total_controls}")
        report.append(f"  ✅ Passed: {passed_controls}")
        report.append(f"  ❌ Failed: {failed_controls}")
        report.append(f"  ⚠️  Partial: {partial_controls}")
        report.append(f"  🎯 Average Confidence: {avg_confidence:.2f}")
        report.append("")
        
        # Detailed analysis for each control
        for analysis in analyses:
            status_emoji = "✅" if analysis.overall_status == "pass" else "❌" if analysis.overall_status == "fail" else "⚠️"
            
            report.append(f"{status_emoji} {analysis.control_id}: {analysis.overall_status.upper()} (confidence: {analysis.confidence:.2f})")
            report.append("-" * 60)
            report.append(f"📋 Control: {analysis.control_name}")
            report.append(f"📖 FedRAMP Requirement: {analysis.fedramp_requirements}")
            report.append("")
            
            report.append("🔍 Specific Checks Performed:")
            for check in analysis.specific_checks_performed:
                report.append(f"  • {check}")
            report.append("")
            
            report.append("💭 Compliance Reasoning:")
            report.append(f"  {analysis.compliance_reasoning}")
            report.append("")
            
            if analysis.missing_requirements:
                report.append("❌ Missing Requirements:")
                for req in analysis.missing_requirements:
                    report.append(f"  • {req}")
                report.append("")
            
            if analysis.recommendations:
                report.append("💡 Recommendations:")
                for rec in analysis.recommendations:
                    report.append(f"  • {rec}")
                report.append("")
            
            report.append("📊 Evidence Details:")
            for ev in analysis.evidence_details:
                ev_emoji = "✅" if ev.status == "compliant" else "❌" if ev.status == "non_compliant" else "⚠️"
                report.append(f"  {ev_emoji} {ev.resource_name} ({ev.evidence_type}): {ev.status}")
                if ev.details:
                    report.append(f"    Details: {json.dumps(ev.details, indent=4)}")
            report.append("")
            report.append("=" * 80)
            report.append("")
        
        return "\n".join(report)

def main():
    """Main function for testing the AI analysis agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-powered detailed AC control analysis')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--control', '-c', help='Analyze specific control (e.g., AC-3)')
    args = parser.parse_args()
    
    # Initialize agent
    agent = AIAnalysisAgent()
    
    # Load AWS data
    aws_data = agent.db.load_aws_data_from_db()
    
    if args.control:
        # Analyze specific control
        analysis = agent.analyze_control_detailed(args.control, aws_data)
        if args.json:
            print(json.dumps({
                "control_id": analysis.control_id,
                "overall_status": analysis.overall_status,
                "confidence": analysis.confidence,
                "compliance_reasoning": analysis.compliance_reasoning,
                "specific_checks_performed": analysis.specific_checks_performed,
                "missing_requirements": analysis.missing_requirements,
                "recommendations": analysis.recommendations
            }, indent=2))
        else:
            print(agent.generate_detailed_report([analysis]))
    else:
        # Analyze all controls
        analyses = agent.analyze_all_controls_detailed(aws_data)
        
        if args.json:
            json_output = []
            for analysis in analyses:
                json_output.append({
                    "control_id": analysis.control_id,
                    "overall_status": analysis.overall_status,
                    "confidence": analysis.confidence,
                    "compliance_reasoning": analysis.compliance_reasoning,
                    "specific_checks_performed": analysis.specific_checks_performed,
                    "missing_requirements": analysis.missing_requirements,
                    "recommendations": analysis.recommendations
                })
            print(json.dumps(json_output, indent=2))
        else:
            print(agent.generate_detailed_report(analyses))

if __name__ == '__main__':
    main()
