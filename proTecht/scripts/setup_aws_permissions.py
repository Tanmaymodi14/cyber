#!/usr/bin/env python3
"""
AWS Permissions Setup for proTecht
Creates IAM roles and policies needed to collect compliance data
"""

import boto3
import json
import sys
import os
from typing import Dict, List

def create_protecht_policy():
    """Create the comprehensive IAM policy for proTecht data collection"""
    
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ProTechtDataCollection",
                "Effect": "Allow",
                "Action": [
                    # IAM permissions
                    "iam:GetAccountPasswordPolicy",
                    "iam:GetAccountSummary",
                    "iam:ListUsers",
                    "iam:ListRoles",
                    "iam:ListPolicies",
                    "iam:ListAttachedUserPolicies",
                    "iam:ListAttachedRolePolicies",
                    "iam:GetRole",
                    "iam:GetUser",
                    "iam:GetPolicy",
                    "iam:GetPolicyVersion",
                    "iam:ListUserPolicies",
                    "iam:ListRolePolicies",
                    "iam:GetUserPolicy",
                    "iam:GetRolePolicy",
                    "iam:ListAccessKeys",
                    "iam:ListMFADevices",
                    "iam:GetLoginProfile",
                    "iam:GetAccessKeyLastUsed",
                    
                    # S3 permissions
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketLocation",
                    "s3:GetBucketVersioning",
                    "s3:GetBucketEncryption",
                    "s3:GetBucketPublicAccessBlock",
                    "s3:GetBucketObjectLockConfiguration",
                    "s3:GetBucketPolicy",
                    "s3:GetBucketPolicyStatus",
                    "s3:GetBucketTagging",
                    "s3:GetBucketLogging",
                    "s3:GetBucketNotification",
                    "s3:GetBucketWebsite",
                    "s3:GetBucketCors",
                    "s3:GetBucketLifecycleConfiguration",
                    "s3:GetBucketReplication",
                    "s3:GetBucketRequestPayment",
                    "s3:GetBucketAcl",
                    "s3:GetBucketOwnershipControls",
                    "s3:GetBucketIntelligentTieringConfiguration",
                    "s3:GetBucketInventoryConfiguration",
                    "s3:GetBucketMetricsConfiguration",
                    "s3:GetBucketAnalyticsConfiguration",
                    "s3:GetBucketAccelerateConfiguration",
                    "s3:GetBucketNotificationConfiguration",
                    "s3:GetBucketPolicyStatus",
                    "s3:GetBucketPublicAccessBlock",
                    "s3:GetBucketTagging",
                    "s3:GetBucketVersioning",
                    "s3:GetBucketWebsite",
                    "s3:GetObject",
                    "s3:GetObjectAcl",
                    "s3:GetObjectVersion",
                    "s3:GetObjectVersionAcl",
                    "s3:GetObjectVersionTagging",
                    "s3:GetObjectTagging",
                    "s3:ListBucket",
                    "s3:ListBucketVersions",
                    "s3:ListBucketMultipartUploads",
                    "s3:ListMultipartUploadParts",
                    
                    # KMS permissions
                    "kms:ListKeys",
                    "kms:ListAliases",
                    "kms:DescribeKey",
                    "kms:GetKeyPolicy",
                    "kms:GetKeyRotationStatus",
                    "kms:ListKeyPolicies",
                    "kms:ListGrants",
                    "kms:DescribeCustomKeyStores",
                    "kms:ListResourceTags",
                    "kms:GetKeyPolicy",
                    "kms:GetKeyRotationStatus",
                    "kms:ListKeyPolicies",
                    "kms:ListGrants",
                    "kms:DescribeCustomKeyStores",
                    "kms:ListResourceTags",
                    
                    # CloudTrail permissions
                    "cloudtrail:DescribeTrails",
                    "cloudtrail:GetTrail",
                    "cloudtrail:GetTrailStatus",
                    "cloudtrail:GetEventSelectors",
                    "cloudtrail:GetInsightSelectors",
                    "cloudtrail:ListTrails",
                    "cloudtrail:GetTrailStatus",
                    "cloudtrail:GetEventSelectors",
                    "cloudtrail:GetInsightSelectors",
                    "cloudtrail:ListTrails",
                    
                    # WAF permissions
                    "wafv2:ListWebACLs",
                    "wafv2:GetWebACL",
                    "wafv2:ListResourcesForWebACL",
                    "wafv2:GetWebACLForResource",
                    "wafv2:ListRuleGroups",
                    "wafv2:GetRuleGroup",
                    "wafv2:ListIPSets",
                    "wafv2:GetIPSet",
                    "wafv2:ListRegexPatternSets",
                    "wafv2:GetRegexPatternSet",
                    "wafv2:ListManagedRuleSets",
                    "wafv2:GetManagedRuleSet",
                    "wafv2:ListLoggingConfigurations",
                    "wafv2:GetLoggingConfiguration",
                    "wafv2:GetSampledRequests",
                    "wafv2:GetWebACL",
                    "wafv2:ListWebACLs",
                    "wafv2:ListResourcesForWebACL",
                    "wafv2:GetWebACLForResource",
                    "wafv2:ListRuleGroups",
                    "wafv2:GetRuleGroup",
                    "wafv2:ListIPSets",
                    "wafv2:GetIPSet",
                    "wafv2:ListRegexPatternSets",
                    "wafv2:GetRegexPatternSet",
                    "wafv2:ListManagedRuleSets",
                    "wafv2:GetManagedRuleSet",
                    "wafv2:ListLoggingConfigurations",
                    "wafv2:GetLoggingConfiguration",
                    "wafv2:GetSampledRequests",
                    
                    # CloudFront permissions
                    "cloudfront:ListDistributions",
                    "cloudfront:GetDistribution",
                    "cloudfront:GetDistributionConfig",
                    "cloudfront:ListCloudFrontOriginAccessIdentities",
                    "cloudfront:GetCloudFrontOriginAccessIdentity",
                    "cloudfront:GetCloudFrontOriginAccessIdentityConfig",
                    "cloudfront:ListStreamingDistributions",
                    "cloudfront:GetStreamingDistribution",
                    "cloudfront:GetStreamingDistributionConfig",
                    "cloudfront:ListDistributions",
                    "cloudfront:GetDistribution",
                    "cloudfront:GetDistributionConfig",
                    "cloudfront:ListCloudFrontOriginAccessIdentities",
                    "cloudfront:GetCloudFrontOriginAccessIdentity",
                    "cloudfront:GetCloudFrontOriginAccessIdentityConfig",
                    "cloudfront:ListStreamingDistributions",
                    "cloudfront:GetStreamingDistribution",
                    "cloudfront:GetStreamingDistributionConfig",
                    
                    # VPC permissions
                    "ec2:DescribeVpcs",
                    "ec2:DescribeFlowLogs",
                    "ec2:DescribeNatGateways",
                    "ec2:DescribeTransitGateways",
                    "ec2:DescribeTransitGatewayAttachments",
                    "ec2:DescribeSecurityGroups",
                    "ec2:DescribeNetworkAcls",
                    "ec2:DescribeRouteTables",
                    "ec2:DescribeInternetGateways",
                    "ec2:DescribeVpcPeeringConnections",
                    "ec2:DescribeVpcEndpoints",
                    "ec2:DescribeVpcEndpointServices",
                    "ec2:DescribeVpcEndpointConnections",
                    "ec2:DescribeVpcEndpointServiceConfigurations",
                    "ec2:DescribeVpcEndpointServicePermissions",
                    "ec2:DescribeVpcEndpointConnections",
                    "ec2:DescribeVpcEndpointServiceConfigurations",
                    "ec2:DescribeVpcEndpointServicePermissions",
                    
                    # GuardDuty permissions
                    "guardduty:ListDetectors",
                    "guardduty:GetDetector",
                    "guardduty:ListFindings",
                    "guardduty:GetFindings",
                    "guardduty:ListFindings",
                    "guardduty:GetFindings",
                    "guardduty:ListMembers",
                    "guardduty:GetMembers",
                    "guardduty:ListInvitations",
                    "guardduty:GetInvitationsCount",
                    "guardduty:ListIPSets",
                    "guardduty:GetIPSet",
                    "guardduty:ListThreatIntelSets",
                    "guardduty:GetThreatIntelSet",
                    "guardduty:ListFilters",
                    "guardduty:GetFilter",
                    "guardduty:ListFindings",
                    "guardduty:GetFindings",
                    "guardduty:ListMembers",
                    "guardduty:GetMembers",
                    "guardduty:ListInvitations",
                    "guardduty:GetInvitationsCount",
                    "guardduty:ListIPSets",
                    "guardduty:GetIPSet",
                    "guardduty:ListThreatIntelSets",
                    "guardduty:GetThreatIntelSet",
                    "guardduty:ListFilters",
                    "guardduty:GetFilter",
                    
                    # Security Hub permissions
                    "securityhub:GetEnabledStandards",
                    "securityhub:GetFindings",
                    "securityhub:ListEnabledProductsForImport",
                    "securityhub:ListInvitations",
                    "securityhub:ListMembers",
                    "securityhub:ListOrganizationAdminAccounts",
                    "securityhub:ListSecurityHubStandards",
                    "securityhub:ListStandardsControlAssociations",
                    "securityhub:ListStandardsControls",
                    "securityhub:GetEnabledStandards",
                    "securityhub:GetFindings",
                    "securityhub:ListEnabledProductsForImport",
                    "securityhub:ListInvitations",
                    "securityhub:ListMembers",
                    "securityhub:ListOrganizationAdminAccounts",
                    "securityhub:ListSecurityHubStandards",
                    "securityhub:ListStandardsControlAssociations",
                    "securityhub:ListStandardsControls",
                    
                    # SSO/Identity Center permissions
                    "sso:ListInstances",
                    "sso:DescribeInstance",
                    "sso:ListPermissionSets",
                    "sso:DescribePermissionSet",
                    "sso:GetPermissionSet",
                    "sso:ListAccountAssignments",
                    "sso:DescribeAccountAssignment",
                    "sso:ListPermissionSetProvisioningStatus",
                    "sso:DescribePermissionSetProvisioningStatus",
                    "sso:ListManagedPoliciesInPermissionSet",
                    "sso:ListPermissionSetProvisioningStatus",
                    "sso:DescribePermissionSetProvisioningStatus",
                    "sso:ListManagedPoliciesInPermissionSet",
                    
                    # AWS Config permissions
                    "config:DescribeConfigRules",
                    "config:GetConfigRule",
                    "config:DescribeConfigurationRecorders",
                    "config:DescribeConfigurationRecorderStatus",
                    "config:DescribeDeliveryChannels",
                    "config:DescribeDeliveryChannelStatus",
                    "config:DescribeConfigRules",
                    "config:GetConfigRule",
                    "config:DescribeConfigurationRecorders",
                    "config:DescribeConfigurationRecorderStatus",
                    "config:DescribeDeliveryChannels",
                    "config:DescribeDeliveryChannelStatus",
                    
                    # General permissions
                    "sts:GetCallerIdentity",
                    "organizations:DescribeOrganization",
                    "organizations:ListAccounts",
                    "organizations:ListRoots",
                    "organizations:ListOrganizationalUnitsForParent",
                    "organizations:ListParents",
                    "organizations:ListChildren",
                    "organizations:DescribeOrganizationalUnit",
                    "organizations:DescribeAccount",
                    "organizations:ListAccountsForParent",
                    "organizations:ListRoots",
                    "organizations:ListOrganizationalUnitsForParent",
                    "organizations:ListParents",
                    "organizations:ListChildren",
                    "organizations:DescribeOrganizationalUnit",
                    "organizations:DescribeAccount",
                    "organizations:ListAccountsForParent"
                ],
                "Resource": "*"
            }
        ]
    }
    
    return policy_document

def create_iam_role_and_policy(session: boto3.Session, role_name: str = "ProTechtComplianceRole"):
    """Create IAM role and policy for proTecht data collection"""
    
    iam = session.client('iam')
    
    # Trust policy for the role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{session.client('sts').get_caller_identity()['Account']}:root"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        # Create the role
        print(f"🔐 Creating IAM role: {role_name}")
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Role for proTecht compliance data collection"
        )
        
        # Create the policy
        policy_name = "ProTechtCompliancePolicy"
        policy_document = create_protecht_policy()
        
        print(f"📋 Creating IAM policy: {policy_name}")
        policy_response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description="Policy for proTecht compliance data collection"
        )
        
        policy_arn = policy_response['Policy']['Arn']
        
        # Attach policy to role
        print(f"🔗 Attaching policy to role")
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        
        print(f"✅ Successfully created role and policy!")
        print(f"   Role ARN: arn:aws:iam::{session.client('sts').get_caller_identity()['Account']}:role/{role_name}")
        print(f"   Policy ARN: {policy_arn}")
        
        return {
            'role_name': role_name,
            'role_arn': f"arn:aws:iam::{session.client('sts').get_caller_identity()['Account']}:role/{role_name}",
            'policy_arn': policy_arn
        }
        
    except Exception as e:
        print(f"❌ Error creating IAM resources: {e}")
        return None

def create_user_with_policy(session: boto3.Session, username: str = "protecht-compliance-user"):
    """Create IAM user with inline policy for proTecht data collection"""
    
    iam = session.client('iam')
    
    try:
        # Create user
        print(f"👤 Creating IAM user: {username}")
        iam.create_user(UserName=username)
        
        # Create access key
        print(f"🔑 Creating access key for user")
        access_key_response = iam.create_access_key(UserName=username)
        
        # Create inline policy
        policy_name = "ProTechtComplianceInlinePolicy"
        policy_document = create_protecht_policy()
        
        print(f"📋 Creating inline policy: {policy_name}")
        iam.put_user_policy(
            UserName=username,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        
        print(f"✅ Successfully created user and policy!")
        print(f"   Username: {username}")
        print(f"   Access Key ID: {access_key_response['AccessKey']['AccessKeyId']}")
        print(f"   Secret Access Key: {access_key_response['AccessKey']['SecretAccessKey']}")
        
        return {
            'username': username,
            'access_key_id': access_key_response['AccessKey']['AccessKeyId'],
            'secret_access_key': access_key_response['AccessKey']['SecretAccessKey']
        }
        
    except Exception as e:
        print(f"❌ Error creating IAM user: {e}")
        return None

def main():
    """Main function to set up AWS permissions"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Set up AWS permissions for proTecht')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--create-user', action='store_true', help='Create IAM user instead of role')
    parser.add_argument('--username', default='protecht-compliance-user', help='Username for IAM user')
    parser.add_argument('--role-name', default='ProTechtComplianceRole', help='Role name for IAM role')
    
    args = parser.parse_args()
    
    print("🔐 proTecht AWS Permissions Setup")
    print("=" * 40)
    
    try:
        session = boto3.Session(profile_name=args.profile, region_name=args.region)
        
        # Test connection
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ Connected to AWS Account: {identity['Account']}")
        print(f"   User/Role: {identity['Arn']}")
        print(f"   Region: {args.region}")
        print()
        
        if args.create_user:
            result = create_user_with_policy(session, args.username)
        else:
            result = create_iam_role_and_policy(session, args.role_name)
        
        if result:
            print()
            print("🎉 AWS permissions setup complete!")
            print("✅ You can now use these credentials to collect compliance data")
            print("✅ Run the comprehensive test environment setup script next")
        else:
            print("❌ Failed to create AWS permissions")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have valid AWS credentials configured")

if __name__ == "__main__":
    main()
