#!/usr/bin/env python3
"""
Fix ECS IAM permissions to allow proper AWS data collection
"""

import boto3
import json

def fix_ecs_iam_permissions():
    """Add necessary IAM permissions to ECS task role"""
    
    # Initialize AWS clients
    iam = boto3.client('iam', region_name='us-east-1')
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    # Get the ECS task role
    task_role_arn = "arn:aws:iam::957103508532:role/protecht-prod-api-TaskRole-ohXKTW88eNWi"
    role_name = "protecht-prod-api-TaskRole-ohXKTW88eNWi"
    
    print(f"🔧 Updating IAM role: {role_name}")
    
    # Create a custom policy for AWS data collection
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:ListUsers",
                    "iam:ListRoles", 
                    "iam:GetAccountPasswordPolicy",
                    "iam:ListMFADevices",
                    "iam:GetLoginProfile",
                    "iam:ListAttachedRolePolicies",
                    "iam:ListRolePolicies",
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketEncryption",
                    "s3:GetBucketPublicAccessBlock",
                    "s3:GetObjectLockConfiguration",
                    "kms:ListKeys",
                    "kms:DescribeKey",
                    "kms:GetKeyRotationStatus",
                    "cloudtrail:DescribeTrails",
                    "cloudtrail:GetTrailStatus",
                    "config:DescribeConfigRules",
                    "config:GetComplianceDetailsByConfigRule",
                    "sso:ListPermissionSets",
                    "sso:DescribePermissionSet",
                    "sso:GetAccountAssignment",
                    "wafv2:ListWebACLs",
                    "wafv2:GetWebACL",
                    "securityhub:GetEnabledStandards",
                    "securityhub:GetFindings",
                    "guardduty:ListDetectors",
                    "guardduty:GetDetector",
                    "guardduty:ListFindings",
                    "ec2:DescribeVpcs",
                    "ec2:DescribeFlowLogs",
                    "cloudfront:ListDistributions",
                    "cloudfront:GetDistribution",
                    "cloudfront:GetDistributionConfig"
                ],
                "Resource": "*"
            }
        ]
    }
    
    policy_name = "ProTechtDataCollectionPolicy"
    
    try:
        # Create the policy
        print("📝 Creating custom IAM policy...")
        response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description="Custom policy for ProTecht AWS data collection"
        )
        
        policy_arn = response['Policy']['Arn']
        print(f"✅ Created policy: {policy_arn}")
        
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"ℹ️  Policy {policy_name} already exists, getting ARN...")
        # Get existing policy ARN
        response = iam.list_policies(Scope='Local')
        for policy in response['Policies']:
            if policy['PolicyName'] == policy_name:
                policy_arn = policy['Arn']
                break
        else:
            print("❌ Could not find existing policy")
            return
    
    # Attach policy to role
    try:
        print(f"🔗 Attaching policy to role {role_name}...")
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        print("✅ Policy attached successfully")
        
    except Exception as e:
        print(f"❌ Error attaching policy: {e}")
        return
    
    print("🎉 IAM permissions updated successfully!")
    print("🔄 You may need to restart the ECS service for changes to take effect")

if __name__ == "__main__":
    fix_ecs_iam_permissions()
