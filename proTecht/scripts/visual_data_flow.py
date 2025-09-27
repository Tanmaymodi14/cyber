#!/usr/bin/env python3
"""
Visual Data Flow Generator for proTecht AWS Compliance System

This script generates ASCII diagrams showing the complete data flow
through the proTecht system.
"""

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

def print_section(title):
    """Print a section header."""
    print(f"\n🔧 {title}")
    print("-" * 60)

def print_data_flow():
    """Print the complete data flow diagram."""
    
    print_header("proTecht AWS Compliance Data Flow")
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AWS SERVICES LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │   IAM   │  │   S3    │  │   KMS   │  │CloudTrail│  │   VPC   │  │CloudFront│  │
│  │         │  │         │  │         │  │         │  │         │  │         │  │
│  │• Users  │  │• Buckets│  │• Keys   │  │• Trails │  │• Flow   │  │• Distros│  │
│  │• Roles  │  │• Encrypt│  │• Rotation│  │• Events │  │  Logs   │  │• TLS    │  │
│  │• Policies│  │• Access │  │• Aliases│  │• Logging│  │• SGs    │  │• Headers│  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
│                                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │   WAF   │  │Security │  │GuardDuty│  │  Config │  │   SSO   │              │
│  │         │  │  Hub    │  │         │  │         │  │         │              │
│  │• WebACLs│  │• Findings│  │• Detectors│  │• Rules  │  │• Sessions│              │
│  │• Rules  │  │• Standards│  │• Findings│  │• Compliance│  │• MFA    │              │
│  │• IP Sets│  │• Controls│  │• Threats │  │• Resources│  │• Policies│              │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    AWS Background Agent                                │    │
│  │  (scripts/aws_background_agent.py)                                    │    │
│  │                                                                       │    │
│  │  • Real-time Analysis                                                 │    │
│  │  • Compliance Mapping                                                 │    │
│  │  • Error Handling                                                     │    │
│  │  • Continuous Monitoring                                              │    │
│  │  • Data Validation                                                    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    Raw AWS Data (JSON)                                │    │
│  │                                                                       │    │
│  │  {                                                                     │    │
│  │    "timestamp": "2025-09-26T16:41:15Z",                              │    │
│  │    "account_id": "957103508532",                                      │    │
│  │    "services": {                                                      │    │
│  │      "iam": { "users": [...], "roles": [...] },                      │    │
│  │      "s3": { "buckets": [...], "encryption": {...} },                │    │
│  │      "kms": { "keys": [...], "rotation": {...} }                     │    │
│  │    }                                                                  │    │
│  │  }                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DATA PROCESSING LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    Data Processor                                      │    │
│  │  (src/database.py)                                                    │    │
│  │                                                                       │    │
│  │  • Data Normalization                                                 │    │
│  │  • Compliance Mapping                                                 │    │
│  │  • Validation & Sanitization                                          │    │
│  │  • Error Handling                                                     │    │
│  │  • Database Storage                                                   │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    SQLite Database                                    │    │
│  │                                                                       │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │  aws_data   │  │  controls   │  │  policies   │  │  evidence   │  │    │
│  │  │             │  │             │  │             │  │             │  │    │
│  │  │• service    │  │• id         │  │• id         │  │• id         │  │    │
│  │  │• data (JSON)│  │• name       │  │• name       │  │• service    │  │    │
│  │  │• timestamp  │  │• status     │  │• type       │  │• data       │  │    │
│  │  │• account_id │  │• score      │  │• analyzed   │  │• timestamp  │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          API SERVER LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    FastAPI Server                                      │    │
│  │  (src/api_server.py)                                                  │    │
│  │                                                                       │    │
│  │  • REST API Endpoints                                                 │    │
│  │  • Business Logic                                                     │    │
│  │  • Data Transformation                                                │    │
│  │  • CORS Handling                                                      │    │
│  │  • Error Handling                                                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    REST Endpoints                                     │    │
│  │                                                                       │    │
│  │  GET  /api/health              - System health check                  │    │
│  │  GET  /api/evidence/aws        - Raw AWS data                         │    │
│  │  GET  /api/evidence/aws/services - Processed services                 │    │
│  │  GET  /api/controls            - Compliance controls                  │    │
│  │  GET  /api/policies            - Policy data                          │    │
│  │  POST /api/evidence/aws/recollect - Trigger data collection           │    │
│  │  GET  /api/analysis/controls   - AI analysis (optional)               │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND API CLIENT LAYER                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    API Client                                          │    │
│  │  (Frontend/src/services/api.ts)                                       │    │
│  │                                                                       │    │
│  │  • HTTP Requests                                                      │    │
│  │  • Data Fetching                                                      │    │
│  │  • State Management                                                   │    │
│  │  • Error Handling                                                     │    │
│  │  • TypeScript Types                                                   │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    Data Types                                          │    │
│  │                                                                       │    │
│  │  interface AWSService {                                               │    │
│  │    id: string;                                                        │    │
│  │    title: string;                                                     │    │
│  │    status: 'Current' | 'Warning' | 'Error';                          │    │
│  │    kpis: Record<string, number | string | boolean>;                  │    │
│  │    mappedControls: string[];                                          │    │
│  │  }                                                                    │    │
│  │                                                                       │    │
│  │  interface ACControl {                                                │    │
│  │    id: string;                                                        │    │
│  │    name: string;                                                      │    │
│  │    status: 'pass' | 'partial' | 'fail' | 'unknown';                  │    │
│  │    score: number;                                                     │    │
│  │    confidence: number;                                                │    │
│  │    reasons: string[];                                                 │    │
│  │    missingEvidence: string[];                                         │    │
│  │  }                                                                    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND COMPONENTS LAYER                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    React Components                                   │    │
│  │  (Frontend/src/components/)                                          │    │
│  │                                                                       │    │
│  │  App.tsx                                                              │    │
│  │  ├── Dashboard.tsx                                                   │    │
│  │  │   ├── ServiceCard.tsx                                             │    │
│  │  │   └── ControlCard.tsx                                             │    │
│  │  ├── EvidenceManagement.tsx                                          │    │
│  │  │   ├── ServiceDetail.tsx                                           │    │
│  │  │   └── EvidenceViewer.tsx                                          │    │
│  │  └── ControlDetails.tsx                                              │    │
│  │       ├── ControlStatus.tsx                                          │    │
│  │       └── ComplianceDetails.tsx                                      │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    User Interface                                     │    │
│  │                                                                       │    │
│  │  • Real-time Dashboard                                                │    │
│  │  • Compliance Status                                                  │    │
│  │  • Evidence Management                                                │    │
│  │  • Control Details                                                    │    │
│  │  • Policy Analysis                                                    │    │
│  │  • Interactive Charts                                                 │    │
│  │  • Responsive Design                                                  │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            USER INTERACTION                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    User Dashboard                                      │    │
│  │                                                                       │    │
│  │  • Compliance Overview                                                 │    │
│  │  • Service Status                                                      │    │
│  │  • Control Scores                                                      │    │
│  │  • Evidence Details                                                    │    │
│  │  • Policy Analysis                                                     │    │
│  │  • Real-time Updates                                                   │    │
│  │  • Export Capabilities                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
""")

def print_real_time_flow():
    """Print the real-time data flow."""
    
    print_section("Real-Time Data Flow")
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CONTINUOUS MONITORING FLOW                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   AWS       │───▶│ Background  │───▶│ Database    │───▶│ API Server  │      │
│  │ Services    │    │ Agent       │    │ Update      │    │ Refresh     │      │
│  │ (Every 60min)│    │ (Analysis)  │    │ (SQLite)    │    │ (FastAPI)   │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                   │                   │                   │          │
│         ▼                   ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Real-time   │    │ Compliance  │    │ Data        │    │ Frontend    │      │
│  │ Data        │    │ Mapping     │    │ Persistence │    │ Auto-Refresh│      │
│  │ Collection  │    │ & Processing│    │ & Caching   │    │ & Updates   │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────────────┘
""")

def print_user_interaction_flow():
    """Print the user interaction flow."""
    
    print_section("User Interaction Flow")
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ User Clicks │───▶│ Frontend    │───▶│ API Request │───▶│ Database    │      │
│  │ "Refresh"   │    │ Event       │    │ to Backend  │    │ Query       │      │
│  │ Button      │    │ Handler     │    │ (HTTP)      │    │ (SQLite)    │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                   │                   │                   │          │
│         ▼                   ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ UI Update   │◀───│ Data        │◀───│ JSON        │◀───│ Data        │      │
│  │ & Rendering │    │ Processing  │    │ Response    │    │ Retrieval   │      │
│  │ (React)     │    │ & State     │    │ (REST API)  │    │ (SQL Query) │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────────────┘
""")

def print_error_handling_flow():
    """Print the error handling flow."""
    
    print_section("Error Handling & Recovery Flow")
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ERROR HANDLING FLOW                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Error       │───▶│ Error       │───▶│ Retry       │───▶│ Fallback    │      │
│  │ Occurs      │    │ Handler     │    │ Logic       │    │ Mechanism   │      │
│  │ (Any Layer) │    │ (Logging)   │    │ (3 attempts)│    │ (Cached Data)│      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                   │                   │                   │          │
│         ▼                   ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Log Error   │    │ User        │    │ Continue    │    │ Graceful    │      │
│  │ to File     │    │ Notification│    │ Processing  │    │ Degradation │      │
│  │ (/tmp/*.log)│    │ (UI Alert)  │    │ (Skip Bad)  │    │ (Show Cached)│      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────────────┘
""")

def print_deployment_flow():
    """Print the deployment flow."""
    
    print_section("Deployment Flow")
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DEPLOYMENT FLOW                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ AWS         │───▶│ Background  │───▶│ Database    │───▶│ API Server  │      │
│  │ Credentials │    │ Agent       │    │ Setup       │    │ Startup     │      │
│  │ Setup       │    │ (Analysis)  │    │ (SQLite)    │    │ (FastAPI)   │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                   │                   │                   │          │
│         ▼                   ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Initial     │    │ Data        │    │ Data        │    │ Frontend    │      │
│  │ Data        │    │ Processing  │    │ Storage     │    │ Startup     │      │
│  │ Collection  │    │ & Mapping   │    │ & Indexing  │    │ (Vite)      │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                   │                   │                   │          │
│         ▼                   ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Compliance  │    │ Real-time   │    │ User        │    │ Continuous  │      │
│  │ Assessment  │    │ Monitoring  │    │ Dashboard   │    │ Operation   │      │
│  │ & Reporting │    │ & Updates   │    │ Ready       │    │ & Updates   │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────────────┘
""")

def main():
    """Generate all data flow diagrams."""
    
    print_data_flow()
    print_real_time_flow()
    print_user_interaction_flow()
    print_error_handling_flow()
    print_deployment_flow()
    
    print_header("Data Flow Summary")
    print("""
📊 DATA SOURCES:
   • AWS Services (IAM, S3, KMS, CloudTrail, VPC, CloudFront, WAF, Security Hub, GuardDuty, Config)
   • Real-time API calls via AWS SDK
   • Continuous monitoring every 60 minutes

🔄 DATA PROCESSING:
   • Background Agent: Analysis, validation, compliance mapping
   • Database: SQLite storage with JSON data
   • API Server: FastAPI REST endpoints with business logic

📡 DATA TRANSPORT:
   • HTTP/HTTPS REST API calls
   • JSON data format
   • Real-time updates via frontend polling

💾 DATA STORAGE:
   • SQLite database with indexed tables
   • JSON data in aws_data table
   • Processed controls and policies in separate tables

🖥️ DATA CONSUMPTION:
   • React frontend with TypeScript
   • Real-time dashboard updates
   • Interactive compliance visualization

🔧 DATA FLOW CONTROL:
   • Error handling and retry logic
   • Caching for performance
   • Graceful degradation on failures
   • Continuous monitoring and updates
""")

if __name__ == "__main__":
    main()
