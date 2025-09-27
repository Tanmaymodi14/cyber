# proTecht - Complete FedRAMP AC Family Compliance Automation Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FedRAMP](https://img.shields.io/badge/FedRAMP-AC%20Family%20Complete-orange.svg)](https://www.fedramp.gov)
[![NIST](https://img.shields.io/badge/NIST-800--53%20Rev%205-blue.svg)](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-blue.svg)](https://openai.com)
[![AWS](https://img.shields.io/badge/AWS-Live%20Data%20Collection-orange.svg)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **Complete NIST SP 800-53 AC Family compliance automation with AI-powered analysis, live AWS data collection, and comprehensive technical controls evaluation**

proTecht is a comprehensive cybersecurity compliance automation platform that provides **complete coverage of all 22 NIST SP 800-53 AC family controls** with AI-powered policy analysis, live AWS data collection, and sophisticated technical controls evaluation. The system implements **100% of cloud-applicable AC controls** with advanced AI analysis, organizational profile generation, and automated compliance fixing.

## Features

### 🤖 AI-Powered Policy Analysis System
- **LLM-Powered Classification**: GPT-4 powered technical vs non-technical content routing
- **Intelligent Control Mapping**: AI identifies primary FedRAMP Access Control (AC) family controls
- **Template-Grounded Validation**: OpenAI file search with FedRAMP template for accurate validation
- **Unified Mixed Control Validation**: Combines policy documents with technical evidence for complete analysis
- **Command-Line Interface**: Terminal-based policy analysis with JSON output support
- **PDF Support**: Automatic text extraction from PDF policy documents

### 🎯 Complete NIST SP 800-53 AC Family Coverage (22/22 Controls)
- **Non-Technical Controls (4)**: AC-1, AC-14, AC-20, AC-22 (policy/document driven)
- **Technical Controls (13)**: AC-3, AC-4, AC-5, AC-6, AC-7, AC-9, AC-10, AC-11, AC-12, AC-13, AC-15, AC-16, AC-21 (AWS infrastructure evaluation)
- **Mixed Controls (5)**: AC-2, AC-8, AC-17, AC-18, AC-19 (unified policy + technical analysis)
- **Cloud Coverage**: 100% of cloud-applicable NIST AC controls implemented
- **AI Analysis**: Detailed reasoning, evidence collection, and recommendations for each control
- **Live AWS Integration**: Real-time data collection from 10+ AWS services

### 🏢 Organizational Profile Generation
- **Realistic Enterprise Scenarios**: Generate 30+ users across 7 departments
- **Varying Security Configurations**: High, medium, and low security departments
- **Comprehensive Resource Creation**: S3 buckets, KMS keys, IAM roles, CloudTrail, WAF, GuardDuty
- **Department-Based Security**: IT/Finance/Legal (high), HR/Engineering (medium), Marketing (low)
- **Role-Based Access**: Admin, power user, standard, read-only, contractor, intern roles
- **Automated Teardown**: Clean resource management with state tracking

### 🔧 Automated Compliance Fixing
- **AI-Powered Issue Detection**: Identifies specific compliance gaps
- **Automated Remediation**: Fixes AWS configurations automatically
- **Comprehensive Coverage**: Addresses AC-3, AC-4, AC-7, AC-9, AC-13, AC-15, AC-16
- **Live AWS Integration**: Real-time configuration updates
- **Compliance Dashboard**: CloudWatch dashboard for ongoing monitoring

### 📊 AI-Powered Analysis Agent
- **Detailed Control Analysis**: Comprehensive reasoning for each AC control
- **Evidence Collection**: Automated gathering of AWS resource evidence
- **Compliance Reasoning**: AI explanations of why controls pass/fail
- **Specific Recommendations**: Actionable steps for improvement
- **Confidence Scoring**: 0.0-1.0 confidence levels for each assessment
- **Executive Reporting**: High-level compliance summaries and statistics

### 🖥️ Headless Architecture
- **No Flask/UI**: Pure command-line and programmatic interfaces
- **CLI Tools**: Dedicated scripts for policy analysis, technical evaluation, and AWS collection
- **Database Integration**: SQLite database for FedRAMP template storage and AWS data persistence
- **Modular Design**: Clean separation of concerns with focused modules
- **Production Ready**: Enterprise-grade reliability and performance

## 🚀 Quick Start

### 1. Setup Environment
```bash
git clone https://github.com/your-org/proTecht.git
cd proTecht
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Option: Run with Docker
```bash
# Start both backend and frontend
docker-compose up --build

# Or run the dev script for local development
./dev.sh
```

### 2. Configure AWS Credentials
```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment Variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Generate Organizational Test Environment
```bash
# Create realistic enterprise scenario
python scripts/generate_org_profile.py --users 30 --region us-east-1

# Collect live AWS data
python collect_aws.py --regions us-east-1

# Run comprehensive AI analysis
python analyze_detailed.py
```

### 4. Fix Compliance Issues
```bash
# Automatically fix AWS compliance issues
python scripts/fix_compliance_issues.py --region us-east-1

# Re-analyze after fixes
python collect_aws.py --regions us-east-1
python analyze_detailed.py
```

### 5. Analyze Policy Documents
```bash
# Analyze policy documents
python analyze_policy.py your_policy.pdf --verbose

# Output as JSON
python analyze_policy.py your_policy.pdf --json > results.json
```
## 📋 Complete AC Family Controls Coverage

### Technical Controls (13) - AWS Infrastructure Evaluation
| Control | Name | Implementation |
|---------|------|----------------|
| **AC-3** | Access Enforcement | IAM roles, permissions, RBAC |
| **AC-4** | Information Flow Enforcement | VPC Flow Logs, WAF, CloudFront TLS |
| **AC-5** | Separation of Duties | IAM role separation |
| **AC-6** | Least Privilege | User access levels, role scoping |
| **AC-7** | Unsuccessful Logon Attempts | Password policy, account lockout |
| **AC-9** | Information on Previous Logon | CloudTrail logging |
| **AC-10** | Concurrent Session Control | Session management (SSO) |
| **AC-11** | Session Lock | Session timeout controls |
| **AC-12** | Session Termination | Session termination controls |
| **AC-13** | Monitoring and Control | GuardDuty, Security Hub |
| **AC-15** | Remote Access Management | S3 Object Lock, Macie |
| **AC-16** | Security Attributes | S3 encryption, KMS rotation |
| **AC-21** | Information Sharing | WAF, S3 public access control |

### Non-Technical Controls (4) - Policy Document Analysis
| Control | Name | Implementation |
|---------|------|----------------|
| **AC-1** | Access Control Policy & Procedures | Policy document analysis |
| **AC-14** | Permitted Actions without Identification | Policy document analysis |
| **AC-20** | Use of External Information Systems | Policy document analysis |
| **AC-22** | Publicly Accessible Content | Policy document analysis |

### Mixed Controls (5) - Unified Policy + Technical Analysis
| Control | Name | Implementation |
|---------|------|----------------|
| **AC-2** | Account Management | Policy + IAM evidence |
| **AC-8** | System Use Notification | Policy + system banners |
| **AC-17** | Remote Access | Policy + VPN/MFA evidence |
| **AC-18** | Wireless Access Restrictions | Policy + wireless config |
| **AC-19** | Portable & Mobile Systems | Policy + MDM evidence |

## 🛠️ Available Tools

### Core Analysis Tools
- **`analyze_detailed.py`** - AI-powered comprehensive AC control analysis
- **`analyze_policy.py`** - Policy document analysis with AI validation
- **`analyze_technical.py`** - Technical controls evaluation
- **`collect_aws.py`** - Live AWS data collection from 10+ services

### Organizational Testing Tools
- **`scripts/generate_org_profile.py`** - Create realistic enterprise scenarios
- **`scripts/provision_ac_scenarios.py`** - Generate secure/insecure test environments
- **`scripts/fix_compliance_issues.py`** - Automatically fix AWS compliance issues

### Utility Scripts
- **`scripts/store_fedramp_template.py`** - Store FedRAMP template in database
- **`scripts/verify_fedramp_template.py`** - Verify template storage

## 📊 Analysis Output Example

### AI-Powered Detailed Analysis
```
🤖 AI-POWERED DETAILED AC CONTROL ANALYSIS REPORT
================================================================================

📊 EXECUTIVE SUMMARY:
  Total Controls Analyzed: 13
  ✅ Passed: 4
  ❌ Failed: 2
  ⚠️  Partial: 7
  🎯 Average Confidence: 0.69

✅ AC-4: PASS (confidence: 0.70)
------------------------------------------------------------
📋 Control: AC-4
📖 FedRAMP Requirement: The information system enforces approved authorizations for controlling the flow of information between interconnected systems based on organization-defined information flow control policies.

🔍 Specific Checks Performed:
  • VPC Flow Logs
  • WAF WebACLs

💭 Compliance Reasoning:
  The system is compliant with FedRAMP Requirement AC-4 as it enforces approved authorizations for controlling the flow of information between interconnected systems. This is evidenced by the enabled VPC Flow Logs and the presence of WAF WebACLs.

💡 Recommendations:
  • Regularly review and update the WAF WebACLs to ensure they are effective against new and evolving threats.
  • Ensure VPC Flow Logs are regularly monitored and analyzed for any unusual activity or potential security threats.
```

## 🏗️ Architecture

```
proTecht/
├── src/
│   ├── protecht.py         # Headless system initialization
│   ├── database.py         # Database with FedRAMP template storage
│   ├── technical_engine.py # Technical controls evaluation engine
│   ├── ai_analysis_agent.py # AI-powered detailed analysis
│   ├── api_server.py       # FastAPI backend server
│   ├── aws_collectors/     # AWS data collection modules
│   │   ├── iam.py         # IAM users, roles, policies
│   │   ├── s3.py          # S3 buckets, encryption, access
│   │   ├── kms.py         # KMS keys, rotation
│   │   ├── vpc.py         # VPC flow logs, security groups
│   │   ├── cloudtrail.py  # CloudTrail logging
│   │   ├── guardduty.py   # GuardDuty detectors
│   │   ├── securityhub.py # Security Hub
│   │   ├── waf.py         # WAF WebACLs
│   │   └── ...            # Additional collectors
│   ├── aws_collect.py     # AWS data collection orchestrator
│   └── policy/            # AI-powered policy analysis package
│       ├── analyzer.py    # Main analysis pipeline
│       ├── mapper.py      # Control identification
│       ├── validator.py   # Policy validation
│       ├── models.py      # Data models
│       ├── schema.py      # AC family controls
│       └── mixed_control_handler.py # Mixed control validation
├── Frontend/              # React/TypeScript frontend
│   ├── src/               # Frontend source code
│   │   ├── components/    # UI components
│   │   │   ├── Dashboard.tsx       # Dashboard view
│   │   │   ├── ControlDetails.tsx  # Control details view
│   │   │   └── EvidenceManagement.tsx # Evidence management view
│   │   ├── services/      # API client services
│   │   │   └── api.ts     # API client
│   │   └── App.tsx        # Main application component
│   └── package.json       # Frontend dependencies
├── analyze_detailed.py    # AI-powered comprehensive analysis
├── analyze_policy.py      # Policy document analysis
├── analyze_technical.py   # Technical controls evaluation
├── collect_aws.py         # AWS data collection
├── scripts/               # Utility and testing scripts
│   ├── generate_org_profile.py      # Organizational profile generation
│   ├── provision_ac_scenarios.py    # Test environment provisioning
│   ├── fix_compliance_issues.py     # Automated compliance fixing
│   ├── bootstrap_ac_baseline.py     # AWS bootstrap script
│   └── ...                # Additional utilities
├── Dockerfile             # Backend Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── DEPLOYMENT.md          # Deployment documentation
├── docs/                  # Documentation and templates
└── protecht.db           # SQLite database
```

## 🎯 Key Features Summary

- **✅ Complete NIST SP 800-53 AC Family Coverage**: All 22 cloud-applicable controls
- **🤖 AI-Powered Analysis**: Detailed reasoning and recommendations for each control
- **☁️ Live AWS Integration**: Real-time data collection from 10+ AWS services
- **🏢 Organizational Testing**: Generate realistic enterprise scenarios
- **🔧 Automated Compliance Fixing**: Fix AWS configurations automatically
- **📊 Comprehensive Reporting**: Executive summaries and detailed analysis
- **🖥️ Headless Architecture**: CLI-driven, production-ready system

## 📈 Recent Updates

### 🚀 Version 2.1 - Frontend Integration and Deployment
- **React/TypeScript Frontend**: Modern UI with Shadcn components
- **FastAPI Backend**: RESTful API with OpenAPI documentation
- **Docker Deployment**: Containerized backend and frontend
- **Deep Linking**: Control-specific navigation between views
- **Export Functionality**: JSON export for evidence and controls
- **Enhanced AWS Collectors**: Improved data collection for AC controls

### 🚀 Version 2.0 - Complete AC Family Implementation
- **Complete NIST Coverage**: All 22 AC family controls implemented
- **AI Analysis Agent**: Detailed reasoning and evidence collection
- **Organizational Profile Generation**: Realistic enterprise testing scenarios
- **Automated Compliance Fixing**: Fix AWS issues automatically
- **Live AWS Integration**: Real-time data collection and analysis
- **Headless Architecture**: Removed Flask/UI dependencies for production use

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NIST SP 800-53**: Control framework foundation
- **FedRAMP**: Cloud compliance requirements
- **OpenAI**: AI-powered analysis capabilities
- **AWS**: Cloud infrastructure and services

