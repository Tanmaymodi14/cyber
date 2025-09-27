#!/usr/bin/env python3
"""
Deploy Working Backend to AWS
Deploys the actual working proTecht backend to AWS with proper permissions
"""

import boto3
import json
import os
import sys
import subprocess
import time
import zipfile
import shutil
from datetime import datetime

def create_iam_role_and_policy(session: boto3.Session):
    """Create IAM role and policies for EC2"""
    print("🔐 Creating IAM role and policies...")
    
    try:
        iam = session.client('iam')
        
        # Create trust policy
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Create role
        try:
            response = iam.create_role(
                RoleName='ProTechtBackendRole',
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for proTecht backend EC2 instance'
            )
            print("   Created IAM role: ProTechtBackendRole")
        except iam.exceptions.EntityAlreadyExistsException:
            print("   Using existing IAM role: ProTechtBackendRole")
        
        # Create custom policy for S3 access
        s3_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        "arn:aws:s3:::protecht-deployments/*",
                        "arn:aws:s3:::protecht-deployments"
                    ]
                }
            ]
        }
        
        try:
            iam.put_role_policy(
                RoleName='ProTechtBackendRole',
                PolicyName='ProTechtS3Access',
                PolicyDocument=json.dumps(s3_policy)
            )
            print("   Created S3 access policy")
        except Exception as e:
            print(f"   Policy creation warning: {e}")
        
        # Attach basic EC2 policy
        try:
            iam.attach_role_policy(
                RoleName='ProTechtBackendRole',
                PolicyArn='arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess'
            )
            print("   Attached EC2 read policy")
        except Exception as e:
            print(f"   Policy attachment warning: {e}")
        
        # Create instance profile
        try:
            iam.create_instance_profile(
                InstanceProfileName='ProTechtBackendProfile'
            )
            print("   Created instance profile")
        except iam.exceptions.EntityAlreadyExistsException:
            print("   Instance profile already exists")
        
        # Add role to instance profile
        try:
            iam.add_role_to_instance_profile(
                InstanceProfileName='ProTechtBackendProfile',
                RoleName='ProTechtBackendRole'
            )
            print("   Added role to instance profile")
        except iam.exceptions.LimitExceededException:
            print("   Role already in instance profile")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating IAM role: {e}")
        return False

def create_deployment_package():
    """Create deployment package with the real backend code"""
    print("📦 Creating deployment package with real backend code...")
    
    try:
        # Create deployment directory
        deploy_dir = os.path.join(os.path.dirname(__file__), '..', 'deploy_package')
        if os.path.exists(deploy_dir):
            shutil.rmtree(deploy_dir)
        os.makedirs(deploy_dir)
        
        # Copy source code
        src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        for item in os.listdir(src_dir):
            src_path = os.path.join(src_dir, item)
            dst_path = os.path.join(deploy_dir, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
        
        # Create requirements.txt
        requirements = '''fastapi==0.104.1
uvicorn==0.24.0
boto3==1.34.0
pydantic==2.11.9
python-multipart==0.0.6
sqlite3
'''
        
        with open(os.path.join(deploy_dir, 'requirements.txt'), 'w') as f:
            f.write(requirements)
        
        # Create startup script that fixes import issues
        startup_script = '''#!/bin/bash
cd /opt/protecht

# Install Python dependencies
pip3 install -r requirements.txt

# Fix import issues by setting PYTHONPATH
export PYTHONPATH=/opt/protecht

# Create a simple launcher script that handles imports correctly
cat > run_api.py << 'EOF'
import sys
import os
sys.path.insert(0, '/opt/protecht')

# Import and run the API server
from src.api_server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Start the API server
nohup python3 run_api.py > api.log 2>&1 &

# Install nginx
yum install -y nginx

# Configure nginx
cat > /etc/nginx/conf.d/protecht.conf << 'EOF'
server {
    listen 80;
    server_name _;
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location / {
        return 200 "proTecht API Server";
        add_header Content-Type text/plain;
    }
}
EOF

# Start nginx
systemctl start nginx
systemctl enable nginx

# Wait for services to start
sleep 15

# Test the API
curl -f http://localhost/api/health || echo "API not ready yet"
'''
        
        with open(os.path.join(deploy_dir, 'startup.sh'), 'w') as f:
            f.write(startup_script)
        
        # Create zip file
        zip_file = os.path.join(os.path.dirname(__file__), '..', 'backend_deployment.zip')
        with zipfile.ZipFile(zip_file, 'w') as zipf:
            for root, dirs, files in os.walk(deploy_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, deploy_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Deployment package created: {zip_file}")
        return zip_file
        
    except Exception as e:
        print(f"❌ Error creating deployment package: {e}")
        return None

def upload_to_s3(session: boto3.Session, zip_file: str):
    """Upload deployment package to S3"""
    print("📤 Uploading deployment package to S3...")
    
    try:
        s3 = session.client('s3')
        bucket_name = "protecht-deployments"
        
        # Create bucket if it doesn't exist
        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f"   Created S3 bucket: {bucket_name}")
        except s3.exceptions.BucketAlreadyExists:
            print(f"   Using existing S3 bucket: {bucket_name}")
        except s3.exceptions.BucketAlreadyOwnedByYou:
            print(f"   Using existing S3 bucket: {bucket_name}")
        
        # Upload file
        s3_key = f"backend-deployment-{int(time.time())}.zip"
        s3.upload_file(zip_file, bucket_name, s3_key)
        
        print(f"✅ Uploaded to S3: s3://{bucket_name}/{s3_key}")
        return f"s3://{bucket_name}/{s3_key}"
        
    except Exception as e:
        print(f"❌ Error uploading to S3: {e}")
        return None

def create_ec2_instance(session: boto3.Session, s3_url: str):
    """Create EC2 instance and deploy the backend"""
    print("🖥️ Creating EC2 instance for real backend...")
    
    try:
        ec2 = session.client('ec2')
        
        # Get the latest Amazon Linux 2 AMI
        response = ec2.describe_images(
            Owners=['amazon'],
            Filters=[
                {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']},
                {'Name': 'architecture', 'Values': ['x86_64']},
                {'Name': 'state', 'Values': ['available']}
            ]
        )
        
        images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
        ami_id = images[0]['ImageId']
        print(f"   Using AMI: {ami_id}")
        
        # Create security group
        try:
            sg_response = ec2.create_security_group(
                GroupName='protecht-working-backend-sg',
                Description='Security group for proTecht working backend API'
            )
            security_group_id = sg_response['GroupId']
        except ec2.exceptions.ClientError as e:
            if 'already exists' in str(e):
                # Get existing security group
                sg_response = ec2.describe_security_groups(
                    GroupNames=['protecht-working-backend-sg']
                )
                security_group_id = sg_response['SecurityGroups'][0]['GroupId']
            else:
                raise
        
        # Allow HTTP traffic
        try:
            ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8000,
                        'ToPort': 8000,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
        except ec2.exceptions.ClientError as e:
            if 'already exists' not in str(e):
                print(f"   Warning: Could not add security group rules: {e}")
        
        print(f"   Using security group: {security_group_id}")
        
        # User data script
        user_data = f'''#!/bin/bash
yum update -y
yum install -y python3 python3-pip git awscli

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Create app directory
mkdir -p /opt/protecht
cd /opt/protecht

# Download deployment package from S3
aws s3 cp {s3_url} deployment.zip
unzip deployment.zip

# Make startup script executable
chmod +x startup.sh

# Run startup script
./startup.sh

# Wait for services to start
sleep 30

# Test the API
curl -f http://localhost/api/health || echo "API not ready yet"
'''
        
        # Launch instance
        response = ec2.run_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
            InstanceType='t3.small',
            SecurityGroupIds=[security_group_id],
            UserData=user_data,
            IamInstanceProfile={
                'Name': 'ProTechtBackendProfile'
            },
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'protecht-working-backend'},
                        {'Key': 'Project', 'Value': 'protecht'}
                    ]
                }
            ]
        )
        
        instance_id = response['Instances'][0]['InstanceId']
        print(f"   Created instance: {instance_id}")
        
        # Wait for instance to be running
        print("   Waiting for instance to be running...")
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        
        # Get public IP
        response = ec2.describe_instances(InstanceIds=[instance_id])
        public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        
        print(f"✅ EC2 instance created successfully")
        print(f"   Instance ID: {instance_id}")
        print(f"   Public IP: {public_ip}")
        print(f"   API URL: http://{public_ip}/api")
        
        return instance_id, public_ip
        
    except Exception as e:
        print(f"❌ Error creating EC2 instance: {e}")
        return None, None

def update_cloudfront_origin(session: boto3.Session, distribution_id: str, api_url: str):
    """Update CloudFront to point to the new API"""
    print(f"🌐 Updating CloudFront origin to: {api_url}")
    
    try:
        cloudfront = session.client('cloudfront')
        
        # Get current distribution config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        # Update origin
        origins = config.get('Origins', {}).get('Items', [])
        for origin in origins:
            if 'api' in origin.get('Id', '').lower():
                origin['DomainName'] = api_url.replace('https://', '').replace('http://', '')
                origin['CustomOriginConfig'] = {
                    'HTTPPort': 80,
                    'HTTPSPort': 443,
                    'OriginProtocolPolicy': 'http-only',
                    'OriginSslProtocols': {
                        'Quantity': 1,
                        'Items': ['TLSv1.2']
                    },
                    'OriginReadTimeout': 30,
                    'OriginKeepaliveTimeout': 5
                }
                print(f"   Updated origin: {origin['Id']}")
                break
        
        # Update distribution
        update_response = cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print("✅ CloudFront origin updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating CloudFront origin: {e}")
        return False

def create_cache_invalidation(session: boto3.Session, distribution_id: str):
    """Create CloudFront cache invalidation"""
    print("🔄 Creating cache invalidation...")
    
    try:
        cloudfront = session.client('cloudfront')
        
        response = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': f"working-backend-deploy-{int(time.time())}"
            }
        )
        
        invalidation_id = response['Invalidation']['Id']
        print(f"✅ Cache invalidation created: {invalidation_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating invalidation: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Deploying Working Backend to AWS")
    print("=" * 40)
    
    try:
        session = boto3.Session(profile_name='tanmay_modi')
        
        # Create IAM role and policies
        if not create_iam_role_and_policy(session):
            print("⚠️ IAM setup failed, but continuing...")
        
        # Create deployment package
        zip_file = create_deployment_package()
        if not zip_file:
            return False
        
        # Upload to S3
        s3_url = upload_to_s3(session, zip_file)
        if not s3_url:
            return False
        
        # Create EC2 instance
        instance_id, public_ip = create_ec2_instance(session, s3_url)
        if not instance_id or not public_ip:
            return False
        
        # Wait for the instance to fully start
        print("   Waiting for API to be ready...")
        time.sleep(120)  # Wait 2 minutes for full deployment
        
        # Test the API
        import requests
        try:
            response = requests.get(f"http://{public_ip}/api/health", timeout=10)
            if response.status_code == 200:
                print("✅ API is responding")
            else:
                print(f"⚠️ API responded with status: {response.status_code}")
        except Exception as e:
            print(f"⚠️ API test failed: {e}")
            print("   Continuing anyway...")
        
        # Update CloudFront
        distribution_id = 'E2NKZPFHR389VM'
        api_url = f"http://{public_ip}"
        
        if not update_cloudfront_origin(session, distribution_id, api_url):
            return False
        
        # Create cache invalidation
        if not create_cache_invalidation(session, distribution_id):
            return False
        
        print(f"\n🎉 Working backend deployment completed!")
        print(f"✅ EC2 Instance: {instance_id}")
        print(f"✅ API URL: http://{public_ip}/api")
        print(f"✅ CloudFront updated")
        print(f"✅ Cache invalidation created")
        
        print(f"\n📝 Your system is now fully deployed:")
        print(f"   Frontend: https://d2d8obg4v8t84w.cloudfront.net")
        print(f"   Backend API: http://{public_ip}/api")
        print(f"   CloudFront will route API calls to the real backend")
        
        print(f"\n⏰ Next steps:")
        print(f"   1. Wait 5-10 minutes for CloudFront cache to clear")
        print(f"   2. Test the reanalyze buttons on CloudFront")
        print(f"   3. Verify all functionality works with real data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
