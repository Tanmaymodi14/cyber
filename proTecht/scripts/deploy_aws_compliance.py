#!/usr/bin/env python3
"""
AWS Compliance Deployment Script for proTecht

This script runs the complete AWS compliance workflow:
1. Analyzes current AWS environment
2. Implements security recommendations
3. Updates proTecht database with new data
4. Verifies compliance improvements

Author: proTecht Team
Purpose: Complete AWS compliance automation
"""

import json
import sys
import os
import time
import subprocess
from datetime import datetime, timezone
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/aws_compliance_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AWSComplianceDeployment')

class AWSComplianceDeployment:
    """Complete AWS compliance deployment workflow."""
    
    def __init__(self, profile_name: str = 'tanmay_modi', region: str = 'us-east-1'):
        self.profile_name = profile_name
        self.region = region
        self.deployment_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'profile': profile_name,
            'region': region,
            'phases': {},
            'summary': {}
        }
        
    def run_phase(self, phase_name: str, command: list, description: str) -> bool:
        """Run a deployment phase and track results."""
        logger.info(f"🚀 Starting {phase_name}: {description}")
        
        start_time = time.time()
        
        try:
            # Run command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=os.path.join(os.path.dirname(__file__), '..')
            )
            
            duration = time.time() - start_time
            
            # Track results
            self.deployment_results['phases'][phase_name] = {
                'description': description,
                'command': ' '.join(command),
                'duration': duration,
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
            if result.returncode == 0:
                logger.info(f"✅ {phase_name} completed successfully in {duration:.2f}s")
                return True
            else:
                logger.error(f"❌ {phase_name} failed with return code {result.returncode}")
                logger.error(f"Error output: {result.stderr}")
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ {phase_name} failed with exception: {e}")
            
            self.deployment_results['phases'][phase_name] = {
                'description': description,
                'command': ' '.join(command),
                'duration': duration,
                'success': False,
                'error': str(e),
                'returncode': -1
            }
            
            return False
    
    def run_aws_analysis(self) -> bool:
        """Run AWS environment analysis."""
        command = [
            'python', 'scripts/aws_background_agent.py',
            '--profile', self.profile_name,
            '--region', self.region
        ]
        
        return self.run_phase(
            'aws_analysis',
            command,
            'Analyze AWS environment and identify compliance issues'
        )
    
    def run_aws_implementation(self) -> bool:
        """Run AWS compliance implementation."""
        command = [
            'python', 'scripts/implement_aws_recommendations.py',
            '--profile', self.profile_name,
            '--region', self.region,
            '--report-file', f'/tmp/aws_implementation_report_{int(time.time())}.json'
        ]
        
        return self.run_phase(
            'aws_implementation',
            command,
            'Implement security recommendations and compliance fixes'
        )
    
    def run_compliance_verification(self) -> bool:
        """Run compliance verification."""
        command = [
            'python', 'scripts/aws_background_agent.py',
            '--profile', self.profile_name,
            '--region', self.region
        ]
        
        return self.run_phase(
            'compliance_verification',
            command,
            'Verify compliance improvements and update database'
        )
    
    def run_database_update(self) -> bool:
        """Update proTecht database with latest AWS data."""
        logger.info("🔄 Updating proTecht database with latest AWS data...")
        
        try:
            # Import database module
            from database import ProTechtDatabase
            
            # Load latest AWS data
            db = ProTechtDatabase()
            
            # Run AWS collection
            from aws_collect import collect_all
            aws_data = collect_all(profile=self.profile_name, regions=[self.region])
            
            # Load into database
            db.load_aws_data(aws_data)
            
            logger.info("✅ Database updated with latest AWS data")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update database: {e}")
            return False
    
    def run_api_health_check(self) -> bool:
        """Check if proTecht API is healthy."""
        logger.info("🔍 Checking proTecht API health...")
        
        try:
            import requests
            
            # Check API health
            response = requests.get('http://localhost:8000/api/health', timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ proTecht API is healthy")
                return True
            else:
                logger.error(f"❌ proTecht API returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to check API health: {e}")
            return False
    
    def run_frontend_health_check(self) -> bool:
        """Check if proTecht frontend is accessible."""
        logger.info("🔍 Checking proTecht frontend health...")
        
        try:
            import requests
            
            # Check frontend
            response = requests.get('http://localhost:5173', timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ proTecht frontend is accessible")
                return True
            else:
                logger.error(f"❌ proTecht frontend returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to check frontend health: {e}")
            return False
    
    def generate_deployment_report(self) -> str:
        """Generate comprehensive deployment report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"/tmp/aws_compliance_deployment_report_{timestamp}.json"
        
        try:
            # Calculate summary
            total_phases = len(self.deployment_results['phases'])
            successful_phases = sum(1 for phase in self.deployment_results['phases'].values() if phase['success'])
            failed_phases = total_phases - successful_phases
            
            self.deployment_results['summary'] = {
                'total_phases': total_phases,
                'successful_phases': successful_phases,
                'failed_phases': failed_phases,
                'success_rate': (successful_phases / total_phases * 100) if total_phases > 0 else 0,
                'deployment_status': 'SUCCESS' if failed_phases == 0 else 'PARTIAL' if successful_phases > 0 else 'FAILED'
            }
            
            # Save report
            with open(report_file, 'w') as f:
                json.dump(self.deployment_results, f, indent=2, default=str)
            
            logger.info(f"✅ Deployment report saved to {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"❌ Failed to generate deployment report: {e}")
            return ""
    
    def run_complete_deployment(self) -> bool:
        """Run complete AWS compliance deployment."""
        logger.info("🚀 Starting complete AWS compliance deployment...")
        
        start_time = time.time()
        
        # Phase 1: Pre-deployment checks
        logger.info("📋 Phase 1: Pre-deployment checks")
        
        if not self.run_api_health_check():
            logger.warning("⚠️ API health check failed, but continuing...")
        
        if not self.run_frontend_health_check():
            logger.warning("⚠️ Frontend health check failed, but continuing...")
        
        # Phase 2: AWS Analysis
        logger.info("📋 Phase 2: AWS environment analysis")
        
        if not self.run_aws_analysis():
            logger.error("❌ AWS analysis failed, stopping deployment")
            return False
        
        # Phase 3: AWS Implementation
        logger.info("📋 Phase 3: AWS compliance implementation")
        
        if not self.run_aws_implementation():
            logger.error("❌ AWS implementation failed, stopping deployment")
            return False
        
        # Phase 4: Database Update
        logger.info("📋 Phase 4: Database update")
        
        if not self.run_database_update():
            logger.warning("⚠️ Database update failed, but continuing...")
        
        # Phase 5: Compliance Verification
        logger.info("📋 Phase 5: Compliance verification")
        
        if not self.run_compliance_verification():
            logger.warning("⚠️ Compliance verification failed, but continuing...")
        
        # Phase 6: Final Health Check
        logger.info("📋 Phase 6: Final health check")
        
        self.run_api_health_check()
        self.run_frontend_health_check()
        
        # Generate report
        report_file = self.generate_deployment_report()
        
        # Calculate total duration
        total_duration = time.time() - start_time
        
        # Print summary
        summary = self.deployment_results['summary']
        logger.info(f"🎉 Deployment completed in {total_duration:.2f} seconds")
        logger.info(f"📊 Results: {summary['successful_phases']}/{summary['total_phases']} phases successful")
        logger.info(f"📈 Success rate: {summary['success_rate']:.1f}%")
        logger.info(f"🎯 Status: {summary['deployment_status']}")
        
        if report_file:
            logger.info(f"📄 Detailed report: {report_file}")
        
        return summary['deployment_status'] == 'SUCCESS'

def main():
    """Main function to run the complete AWS compliance deployment."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AWS Compliance Deployment Script')
    parser.add_argument('--profile', default='tanmay_modi', help='AWS profile to use')
    parser.add_argument('--region', default='us-east-1', help='AWS region to use')
    parser.add_argument('--skip-analysis', action='store_true', help='Skip AWS analysis phase')
    parser.add_argument('--skip-implementation', action='store_true', help='Skip AWS implementation phase')
    parser.add_argument('--skip-verification', action='store_true', help='Skip compliance verification phase')
    
    args = parser.parse_args()
    
    # Create deployment instance
    deployment = AWSComplianceDeployment(profile_name=args.profile, region=args.region)
    
    # Run deployment
    success = deployment.run_complete_deployment()
    
    # Exit with appropriate code
    if success:
        logger.info("🎉 AWS compliance deployment completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ AWS compliance deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
