# AWS Compliance Automation Scripts for proTecht

This directory contains comprehensive scripts for automating AWS compliance with FedRAMP AC controls in the proTecht platform.

## 🚀 Quick Start

```bash
# Run complete AWS compliance deployment
./scripts/run_aws_compliance.sh

# Or run individual phases
./scripts/run_aws_compliance.sh analyze
./scripts/run_aws_compliance.sh implement
./scripts/run_aws_compliance.sh verify
```

## 📋 Scripts Overview

### 1. `aws_background_agent.py`
**Purpose**: Analyzes AWS environment and identifies compliance issues

**Features**:
- Comprehensive AWS service analysis (IAM, S3, KMS, CloudTrail, VPC, CloudFront, WAF, Security Hub, GuardDuty, Config)
- Maps AWS services to FedRAMP AC controls
- Generates compliance recommendations
- Updates proTecht database with real AWS data
- Supports continuous monitoring mode

**Usage**:
```bash
# Single analysis
python scripts/aws_background_agent.py --profile tanmay_modi --region us-east-1

# Continuous monitoring (every 60 minutes)
python scripts/aws_background_agent.py --profile tanmay_modi --region us-east-1 --continuous --interval 60
```

### 2. `implement_aws_recommendations.py`
**Purpose**: Implements security recommendations to improve compliance

**Features**:
- **HIGH PRIORITY**:
  - Password policy implementation (AC-7)
  - S3 public access block (AC-15, AC-16, AC-21)
  - S3 bucket encryption (AC-16)
- **MEDIUM PRIORITY**:
  - Security Hub enablement (AC-13)
  - GuardDuty enablement (AC-13)
  - AWS Config enablement (AC-7)
- **LOW PRIORITY**:
  - S3 lifecycle policies (AC-16)
  - CloudTrail improvements (AC-9)
  - VPC flow logs (AC-4, AC-11, AC-12)
  - CloudFront TLS policy (AC-4, AC-11, AC-12)

**Usage**:
```bash
# Implement all recommendations
python scripts/implement_aws_recommendations.py --profile tanmay_modi --region us-east-1

# With custom report file
python scripts/implement_aws_recommendations.py --profile tanmay_modi --region us-east-1 --report-file /path/to/report.json
```

### 3. `deploy_aws_compliance.py`
**Purpose**: Complete deployment workflow orchestrator

**Features**:
- Runs complete AWS compliance workflow
- Pre-deployment health checks
- Phase-by-phase execution tracking
- Comprehensive reporting
- Error handling and recovery

**Usage**:
```bash
# Complete deployment
python scripts/deploy_aws_compliance.py --profile tanmay_modi --region us-east-1

# Skip specific phases
python scripts/deploy_aws_compliance.py --profile tanmay_modi --region us-east-1 --skip-analysis
```

### 4. `run_aws_compliance.sh`
**Purpose**: User-friendly shell script wrapper

**Features**:
- Pre-flight checks (AWS credentials, Python env, services)
- Automatic service startup
- Colored output and logging
- Multiple execution modes
- Summary reporting

**Usage**:
```bash
# Complete deployment
./scripts/run_aws_compliance.sh

# Individual phases
./scripts/run_aws_compliance.sh analyze
./scripts/run_aws_compliance.sh implement
./scripts/run_aws_compliance.sh verify

# Help
./scripts/run_aws_compliance.sh help
```

## 🔧 Prerequisites

### AWS Configuration
```bash
# Configure AWS credentials
aws configure --profile tanmay_modi

# Verify access
aws sts get-caller-identity --profile tanmay_modi
```

### Required AWS Permissions
The scripts require the following AWS permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:*",
                "s3:*",
                "kms:*",
                "cloudtrail:*",
                "ec2:*",
                "cloudfront:*",
                "wafv2:*",
                "securityhub:*",
                "guardduty:*",
                "config:*",
                "s3control:*"
            ],
            "Resource": "*"
        }
    ]
}
```

### Python Environment
```bash
# Create virtual environment
cd /Users/tanmaymodi/cyber/proTecht
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### proTecht Services
```bash
# Start API server
cd /Users/tanmaymodi/cyber/proTecht
source .venv/bin/activate
python src/api_server.py

# Start frontend (in another terminal)
cd /Users/tanmaymodi/cyber/proTecht/Frontend
npm run dev
```

## 📊 Compliance Controls Mapped

| Control | Description | AWS Services | Implementation |
|---------|-------------|--------------|----------------|
| **AC-3** | Access Enforcement | IAM Users/Roles | ✅ Analyzed |
| **AC-4** | Information Flow | CloudFront, WAF, VPC | ✅ Implemented |
| **AC-5** | Separation of Duties | IAM Roles | ✅ Analyzed |
| **AC-6** | Least Privilege | IAM Policies | ✅ Analyzed |
| **AC-7** | Unsuccessful Logins | Password Policy, Config | ✅ Implemented |
| **AC-9** | Audit Logging | CloudTrail | ✅ Implemented |
| **AC-11** | Session Control | CloudFront, VPC | ✅ Implemented |
| **AC-12** | Session Termination | CloudFront, VPC | ✅ Implemented |
| **AC-13** | Monitoring | Security Hub, GuardDuty | ✅ Implemented |
| **AC-15** | Remote Access | S3, VPC | ✅ Implemented |
| **AC-16** | Encryption | S3, KMS | ✅ Implemented |
| **AC-21** | Information Sharing | S3, WAF | ✅ Implemented |

## 📈 Monitoring and Reporting

### Log Files
- `/tmp/aws_background_agent.log` - Analysis logs
- `/tmp/aws_compliance_implementation.log` - Implementation logs
- `/tmp/aws_compliance_deployment.log` - Deployment logs
- `/tmp/protecht_api.log` - API server logs
- `/tmp/protecht_frontend.log` - Frontend logs

### Report Files
- `/tmp/aws_compliance_deployment_report_*.json` - Complete deployment report
- `/tmp/aws_implementation_report_*.json` - Implementation details

### Real-time Monitoring
```bash
# Monitor logs
tail -f /tmp/aws_compliance_*.log

# Check API health
curl http://localhost:8000/api/health

# Check frontend
curl http://localhost:5173
```

## 🔄 Continuous Monitoring

### Background Agent
```bash
# Run continuous monitoring
python scripts/aws_background_agent.py --profile tanmay_modi --region us-east-1 --continuous --interval 60
```

### Scheduled Execution
```bash
# Add to crontab for hourly monitoring
0 * * * * cd /Users/tanmaymodi/cyber/proTecht && source .venv/bin/activate && python scripts/aws_background_agent.py --profile tanmay_modi --region us-east-1
```

## 🚨 Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   ```bash
   aws configure --profile tanmay_modi
   aws sts get-caller-identity --profile tanmay_modi
   ```

2. **Python Virtual Environment Not Found**
   ```bash
   cd /Users/tanmaymodi/cyber/proTecht
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **API Server Not Running**
   ```bash
   cd /Users/tanmaymodi/cyber/proTecht
   source .venv/bin/activate
   python src/api_server.py
   ```

4. **Frontend Not Running**
   ```bash
   cd /Users/tanmaymodi/cyber/proTecht/Frontend
   npm install
   npm run dev
   ```

5. **Permission Denied Errors**
   - Check AWS IAM permissions
   - Ensure user has required service permissions
   - Verify resource access policies

### Debug Mode
```bash
# Enable debug logging
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=tanmay_modi
python scripts/aws_background_agent.py --profile tanmay_modi --region us-east-1
```

## 📚 Additional Resources

- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
- [FedRAMP AC Controls](https://www.fedramp.gov/assets/resources/documents/FedRAMP_Security_Controls_Baseline_Low-Moderate-High_v3.0.pdf)
- [proTecht Documentation](../README.md)
- [AWS Compliance Programs](https://aws.amazon.com/compliance/programs/)

## 🤝 Support

For issues or questions:
1. Check the log files for detailed error messages
2. Verify AWS permissions and configuration
3. Ensure all prerequisites are met
4. Review the troubleshooting section above

## 📝 License

This project is part of the proTecht compliance platform. See the main project license for details.
