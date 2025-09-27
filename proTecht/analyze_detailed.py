#!/usr/bin/env python3
"""
CLI for AI-powered detailed AC control analysis
"""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_analysis_agent import AIAnalysisAgent

def main():
    parser = argparse.ArgumentParser(description='AI-powered detailed AC control analysis')
    parser.add_argument('--control', '-c', help='Analyze specific control (e.g., AC-3)')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    print("🤖 Initializing AI Analysis Agent...")
    agent = AIAnalysisAgent()
    
    print("📊 Loading AWS data from database...")
    aws_data = agent.db.load_aws_data_from_db()
    
    if args.control:
        print(f"🔍 Analyzing control {args.control}...")
        analysis = agent.analyze_control_detailed(args.control, aws_data)
        
        if args.json:
            import json
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
        print("🔍 Analyzing all AC controls...")
        analyses = agent.analyze_all_controls_detailed(aws_data)
        
        if args.json:
            import json
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
