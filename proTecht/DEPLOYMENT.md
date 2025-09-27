# proTecht AC Deployment Guide

This guide outlines how to deploy the proTecht Access Control (AC) compliance automation platform.

## Local Development

### Prerequisites
- Docker and Docker Compose
- AWS credentials (for live data collection)
- OpenAI API key (for AI analysis)

### Setup

1. **Environment Variables**

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

2. **Run with Docker Compose**

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Production Deployment

### Option 1: AWS Elastic Beanstalk

1. **Database Migration**

For production, replace the SQLite database with Amazon RDS:

```python
# In src/database.py, modify the connection string:
self.conn = sqlite3.connect(os.environ.get('DATABASE_URL', db_path))
```

2. **Deploy Backend**

Create an Elastic Beanstalk environment with the Docker platform:

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB project
eb init -p docker protecht-ac-api

# Create environment
eb create protecht-ac-api-prod

# Deploy
eb deploy
```

3. **Deploy Frontend**

The frontend can be deployed to S3 + CloudFront:

```bash
# Build frontend with production API URL
cd Frontend
VITE_API_BASE=https://your-api-domain.com/api npm run build

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name/ --delete

# Create CloudFront distribution pointing to the S3 bucket
```

### Option 2: Kubernetes

1. **Create Kubernetes Manifests**

Create `k8s/` directory with the following files:

- `backend-deployment.yaml`
- `frontend-deployment.yaml`
- `backend-service.yaml`
- `frontend-service.yaml`
- `ingress.yaml`
- `configmap.yaml` (for environment variables)
- `secret.yaml` (for sensitive data)

2. **Deploy to Kubernetes**

```bash
kubectl apply -f k8s/
```

## CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy proTecht AC

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Build and push backend Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ secrets.ECR_REPOSITORY_URL }}/protecht-ac-backend:${{ github.sha }}
      
      - name: Build and push frontend Docker image
        uses: docker/build-push-action@v4
        with:
          context: ./Frontend
          push: true
          tags: ${{ secrets.ECR_REPOSITORY_URL }}/protecht-ac-frontend:${{ github.sha }}
      
      - name: Deploy to ECS/EKS
        run: |
          # Update task definition or k8s manifests
          # Deploy to ECS/EKS
```

## Scaling Considerations

1. **Database**
   - For production, migrate from SQLite to RDS PostgreSQL
   - Consider read replicas for high traffic

2. **API Scaling**
   - Use auto-scaling groups in ECS/EKS
   - Consider API Gateway for rate limiting

3. **Frontend**
   - CloudFront for global distribution
   - S3 for static hosting

4. **Security**
   - Implement proper JWT authentication
   - Use AWS Secrets Manager for credentials
   - Enable WAF for API protection

## Monitoring

1. **CloudWatch Metrics**
   - API latency
   - Error rates
   - Resource utilization

2. **Logging**
   - Centralize logs in CloudWatch Logs
   - Set up log-based alarms

3. **Alerts**
   - Create SNS topics for critical alerts
   - Set up PagerDuty integration

## Backup Strategy

1. **Database Backups**
   - Automated RDS snapshots
   - Point-in-time recovery

2. **Configuration Backups**
   - Store infrastructure as code in version control
   - Use AWS Backup for EBS volumes
