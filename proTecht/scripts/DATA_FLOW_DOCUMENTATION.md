# proTecht AWS Compliance Data Flow Documentation

This document describes the complete data flow through the proTecht AWS compliance system, from AWS data collection to frontend visualization.

## 🔄 Complete Data Flow Overview

```
AWS Services → Background Agent → Database → API Server → Frontend → User Dashboard
     ↓              ↓                ↓           ↓          ↓           ↓
  Real Data    Analysis &        SQLite      FastAPI    React/Vite   Compliance
  Collection   Processing        Storage     REST API   Frontend     Dashboard
```

## 📊 Detailed Data Flow

### Phase 1: AWS Data Collection
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AWS Services  │───▶│  Background Agent │───▶│  Raw AWS Data   │
│                 │    │                  │    │                 │
│ • IAM           │    │ • Analysis       │    │ • JSON Format   │
│ • S3            │    │ • Processing     │    │ • Structured    │
│ • KMS           │    │ • Validation     │    │ • Timestamped   │
│ • CloudTrail    │    │ • Error Handling │    │ • Categorized   │
│ • VPC           │    │                  │    │                 │
│ • CloudFront    │    │                  │    │                 │
│ • WAF           │    │                  │    │                 │
│ • Security Hub  │    │                  │    │                 │
│ • GuardDuty     │    │                  │    │                 │
│ • AWS Config    │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Phase 2: Data Processing & Storage
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Raw AWS Data   │───▶│  Data Processor  │───▶│  SQLite Database│
│                 │    │                  │    │                 │
│ • JSON Format   │    │ • Normalization  │    │ • Tables:       │
│ • Structured    │    │ • Validation     │    │   - aws_data    │
│ • Timestamped   │    │ • Transformation │    │   - controls    │
│ • Categorized   │    │ • Compliance     │    │   - policies    │
│                 │    │   Mapping        │    │   - evidence    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Phase 3: API Server Processing
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  SQLite Database│───▶│   API Server     │───▶│  REST Endpoints │
│                 │    │                  │    │                 │
│ • aws_data      │    │ • FastAPI        │    │ • /api/health   │
│ • controls      │    │ • Data Access    │    │ • /api/evidence │
│ • policies      │    │ • Business Logic │    │ • /api/controls │
│ • evidence      │    │ • Compliance     │    │ • /api/policies │
│                 │    │   Evaluation     │    │ • /api/analysis │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Phase 4: Frontend Consumption
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  REST Endpoints │───▶│  Frontend API    │───▶│  React Components│
│                 │    │  Client          │    │                 │
│ • JSON Response │    │ • HTTP Requests  │    │ • Dashboard     │
│ • Status Codes  │    │ • Data Fetching  │    │ • Controls      │
│ • Error Handling│    │ • State Management│    │ • Evidence      │
│ • Caching       │    │ • Error Handling │    │ • Policies      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Phase 5: User Interface
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  React Components│───▶│  UI Rendering    │───▶│  User Dashboard │
│                 │    │                  │    │                 │
│ • Dashboard     │    │ • Data Binding   │    │ • Compliance    │
│ • Controls      │    │ • State Updates  │    │   Status        │
│ • Evidence      │    │ • Event Handling │    │ • Real-time     │
│ • Policies      │    │ • Responsive UI  │    │   Updates       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔍 Detailed Component Analysis

### 1. AWS Data Collection Layer

**Source**: `scripts/aws_background_agent.py`

**Data Sources**:
- **IAM**: Users, roles, policies, password policies
- **S3**: Buckets, encryption, public access, lifecycle
- **KMS**: Keys, rotation, aliases
- **CloudTrail**: Trails, events, logging
- **VPC**: Flow logs, security groups, subnets
- **CloudFront**: Distributions, TLS policies
- **WAF**: Web ACLs, rules, IP sets
- **Security Hub**: Findings, standards
- **GuardDuty**: Detectors, findings
- **AWS Config**: Rules, compliance

**Data Format**:
```json
{
  "timestamp": "2025-09-26T16:41:15Z",
  "account_id": "957103508532",
  "services": {
    "iam": {
      "users": [...],
      "roles": [...],
      "policies": [...],
      "password_policy": {...}
    },
    "s3": {
      "buckets": [...],
      "encryption": {...},
      "public_access_block": {...}
    }
  }
}
```

### 2. Data Processing Layer

**Source**: `src/database.py`

**Processing Steps**:
1. **Data Validation**: Check required fields
2. **Normalization**: Standardize data formats
3. **Compliance Mapping**: Map to FedRAMP controls
4. **Storage**: Save to SQLite database

**Database Schema**:
```sql
CREATE TABLE aws_data (
    id INTEGER PRIMARY KEY,
    service_name TEXT,
    data JSON,
    timestamp DATETIME,
    account_id TEXT
);
```

### 3. API Server Layer

**Source**: `src/api_server.py`

**Endpoints**:
- `GET /api/health` - System health check
- `GET /api/evidence/aws` - Raw AWS data
- `GET /api/evidence/aws/services` - Processed services
- `GET /api/controls` - Compliance controls
- `GET /api/policies` - Policy data
- `POST /api/evidence/aws/recollect` - Trigger data collection

**Data Transformation**:
```python
def _services_from_aws(aws_data):
    services = []
    # IAM processing
    iam = aws_data.get("iam", {})
    services.append({
        "id": "iam-config",
        "title": "IAM Configuration",
        "status": "Current",
        "kpis": {
            "Users": len(iam.get("users", [])),
            "Roles": len(iam.get("roles", [])),
            "Policies": len(iam.get("policies", []))
        },
        "mappedControls": ["AC-3", "AC-5", "AC-6", "AC-7", "AC-9"]
    })
    return services
```

### 4. Frontend API Client

**Source**: `Frontend/src/services/api.ts`

**API Client Functions**:
```typescript
export async function getAWSServices(): Promise<AWSService[]> {
  const res = await fetch(`${API_BASE}/evidence/aws/services`);
  return json.data as AWSService[];
}

export async function getACControls(): Promise<ACControl[]> {
  const res = await fetch(`${API_BASE}/controls`);
  return json.data as ACControl[];
}
```

**Data Types**:
```typescript
interface AWSService {
  id: string;
  title: string;
  status: 'Current' | 'Warning' | 'Error';
  kpis: Record<string, number | string | boolean>;
  mappedControls: string[];
}

interface ACControl {
  id: string;
  name: string;
  status: 'pass' | 'partial' | 'fail' | 'unknown';
  score: number;
  confidence: number;
  reasons: string[];
  missingEvidence: string[];
}
```

### 5. Frontend Components

**Source**: `Frontend/src/components/`

**Component Hierarchy**:
```
App.tsx
├── Dashboard.tsx
│   ├── ServiceCard.tsx
│   └── ControlCard.tsx
├── EvidenceManagement.tsx
│   ├── ServiceDetail.tsx
│   └── EvidenceViewer.tsx
└── ControlDetails.tsx
    ├── ControlStatus.tsx
    └── ComplianceDetails.tsx
```

**Data Flow in Components**:
```typescript
// Dashboard.tsx
const [services, setServices] = useState<AWSService[]>([]);
const [controls, setControls] = useState<ACControl[]>([]);

useEffect(() => {
  getAWSServices().then(setServices);
  getACControls().then(setControls);
}, []);
```

## 🔄 Real-Time Data Flow

### Continuous Monitoring Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Background     │───▶│  Database        │───▶│  API Server     │
│  Agent          │    │  Update          │    │  Refresh        │
│  (Every 60min)  │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  AWS Services   │    │  SQLite          │    │  Frontend       │
│  Data           │    │  Database        │    │  Auto-Refresh   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### User Interaction Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  User Clicks    │───▶│  Frontend        │───▶│  API Request    │
│  "Refresh"      │    │  Event Handler   │    │  to Backend     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  UI Update      │◀───│  Data Processing │◀───│  Database       │
│  & Rendering    │    │  & State Update  │    │  Query          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 Data Storage Architecture

### SQLite Database Structure
```
protecht.db
├── aws_data
│   ├── id (INTEGER PRIMARY KEY)
│   ├── service_name (TEXT)
│   ├── data (JSON)
│   ├── timestamp (DATETIME)
│   └── account_id (TEXT)
├── controls
│   ├── id (TEXT PRIMARY KEY)
│   ├── name (TEXT)
│   ├── status (TEXT)
│   ├── score (INTEGER)
│   └── confidence (REAL)
└── policies
    ├── id (TEXT PRIMARY KEY)
    ├── name (TEXT)
    ├── type (TEXT)
    └── last_analyzed (DATETIME)
```

### Data Persistence
- **AWS Data**: Stored as JSON in `aws_data` table
- **Controls**: Processed and stored in `controls` table
- **Policies**: Analyzed and stored in `policies` table
- **Timestamps**: All data includes creation/update timestamps

## 🔧 Error Handling & Recovery

### Error Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Error Occurs   │───▶│  Error Handler   │───▶│  Fallback       │
│  in Data Flow   │    │                  │    │  Mechanism      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Log Error      │    │  Retry Logic     │    │  User           │
│  to File        │    │  (3 attempts)    │    │  Notification   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Error Types & Handling
1. **AWS API Errors**: Retry with exponential backoff
2. **Database Errors**: Log and continue with cached data
3. **Network Errors**: Show user-friendly error messages
4. **Data Validation Errors**: Skip invalid records, log warnings

## 📈 Performance Optimizations

### Caching Strategy
- **API Responses**: Cached for 5 minutes
- **Database Queries**: Indexed for fast lookups
- **Frontend State**: Memoized with React hooks

### Data Volume Management
- **Incremental Updates**: Only changed data is processed
- **Data Retention**: Old data archived after 90 days
- **Batch Processing**: Multiple AWS services processed in parallel

## 🔒 Security Considerations

### Data Protection
- **Encryption**: All data encrypted at rest and in transit
- **Access Control**: API endpoints require authentication
- **Data Sanitization**: Sensitive data masked in logs

### Compliance
- **FedRAMP AC Controls**: All data mapped to compliance requirements
- **Audit Logging**: All data access logged for compliance
- **Data Retention**: Compliant with regulatory requirements

## 🚀 Deployment Flow

### Initial Setup
```
1. AWS Credentials → Background Agent → Database
2. Database → API Server → Frontend
3. Frontend → User Dashboard
```

### Continuous Operation
```
1. Background Agent (scheduled) → Database Update
2. Frontend (user interaction) → API Server → Database
3. Real-time Updates → User Dashboard
```

This comprehensive data flow ensures that AWS compliance data flows seamlessly from collection to visualization, providing real-time insights into your organization's security posture.
