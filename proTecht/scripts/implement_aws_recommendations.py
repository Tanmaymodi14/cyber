#!/usr/bin/env python3
"""
AWS Compliance Implementation Script for proTecht

This script implements all the recommendations from the AWS background agent analysis
to improve compliance with FedRAMP AC controls.

Author: proTecht Team
Purpose: Automate AWS security improvements and compliance fixes
"""

import json
import sys
import os
import time
import boto3
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/aws_compliance_implementation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AWSComplianceImplementation')

class AWSComplianceImplementer:
    """Implements AWS compliance recommendations to improve security posture."""
    
    def __init__(self, profile_name: str = 'tanmay_modi', region: str = 'us-east-1'):
        self.profile_name = profile_name
        self.region = region
        self.session = boto3.Session(profile_name=profile_name, region_name=region)
        self.account_id = None
        self.user_arn = None
        self.implementation_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'account_id': '',
            'implementations': [],
            'errors': [],
            'summary': {}
        }
        
    def initialize(self) -> bool:
        """Initialize the implementer and verify AWS connectivity."""
        try:
            # Get caller identity
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            self.account_id = identity['Account']
            self.user_arn = identity['Arn']
            self.implementation_results['account_id'] = self.account_id
            
            logger.info(f"✅ Connected to AWS Account: {self.account_id}")
            logger.info(f"✅ User: {self.user_arn}")
            logger.info(f"✅ Region: {self.region}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS connection: {e}")
            return False
    
    def implement_password_policy(self) -> bool:
        """Implement strong password policy for AC-7 compliance."""
        logger.info("🔧 Implementing password policy...")
        
        try:
            iam = self.session.client('iam')
            
            # Define strong password policy
            password_policy = {
                'MinimumPasswordLength': 14,
                'RequireSymbols': True,
                'RequireNumbers': True,
                'RequireUppercaseCharacters': True,
                'RequireLowercaseCharacters': True,
                'AllowUsersToChangePassword': True,
                'MaxPasswordAge': 90,
                'PasswordReusePrevention': 12,
                'HardExpiry': False
            }
            
            # Update password policy
            iam.update_account_password_policy(**password_policy)
            
            self.implementation_results['implementations'].append({
                'service': 'IAM',
                'control': 'AC-7',
                'action': 'Password Policy',
                'status': 'SUCCESS',
                'details': 'Strong password policy implemented with 14+ chars, complexity, 90-day rotation'
            })
            
            logger.info("✅ Password policy implemented successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to implement password policy: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def implement_s3_public_access_block(self) -> bool:
        """Implement account-level S3 public access block for AC-15, AC-16, AC-21 compliance."""
        logger.info("🔧 Implementing S3 public access block...")
        
        try:
            s3_control = self.session.client('s3control')
            
            # Define public access block configuration
            public_access_block = {
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
            
            # Apply account-level public access block
            s3_control.put_public_access_block(
                AccountId=self.account_id,
                PublicAccessBlockConfiguration=public_access_block
            )
            
            self.implementation_results['implementations'].append({
                'service': 'S3',
                'control': 'AC-15, AC-16, AC-21',
                'action': 'Account Public Access Block',
                'status': 'SUCCESS',
                'details': 'Account-level public access block implemented to prevent accidental public access'
            })
            
            logger.info("✅ S3 public access block implemented successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to implement S3 public access block: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def implement_s3_bucket_encryption(self) -> bool:
        """Implement S3 bucket encryption for AC-16 compliance."""
        logger.info("🔧 Implementing S3 bucket encryption...")
        
        try:
            s3 = self.session.client('s3')
            kms = self.session.client('kms')
            
            # Get all buckets
            response = s3.list_buckets()
            buckets_updated = 0
            
            for bucket in response['Buckets']:
                bucket_name = bucket['Name']
                
                try:
                    # Check if bucket already has encryption
                    try:
                        s3.get_bucket_encryption(Bucket=bucket_name)
                        logger.info(f"Bucket {bucket_name} already has encryption")
                        continue
                    except s3.exceptions.NoSuchEncryptionConfiguration:
                        # Bucket doesn't have encryption, add it
                        pass
                    
                    # Create KMS key for S3 encryption if needed
                    key_alias = f'alias/s3-encryption-{bucket_name}'
                    try:
                        # Try to find existing key
                        kms.describe_key(KeyId=key_alias)
                        key_id = key_alias
                    except kms.exceptions.NotFoundException:
                        # Create new KMS key
                        key_response = kms.create_key(
                            Description=f'S3 encryption key for {bucket_name}',
                            KeyUsage='ENCRYPT_DECRYPT',
                            KeySpec='SYMMETRIC_DEFAULT'
                        )
                        key_id = key_response['KeyMetadata']['KeyId']
                        
                        # Create alias
                        kms.create_alias(
                            AliasName=key_alias,
                            TargetKeyId=key_id
                        )
                        
                        # Enable key rotation
                        kms.enable_key_rotation(KeyId=key_id)
                    
                    # Apply encryption to bucket
                    encryption_config = {
                        'Rules': [
                            {
                                'ApplyServerSideEncryptionByDefault': {
                                    'SSEAlgorithm': 'aws:kms',
                                    'KMSMasterKeyID': key_id
                                },
                                'BucketKeyEnabled': True
                            }
                        ]
                    }
                    
                    s3.put_bucket_encryption(
                        Bucket=bucket_name,
                        ServerSideEncryptionConfiguration=encryption_config
                    )
                    
                    buckets_updated += 1
                    logger.info(f"✅ Applied encryption to bucket {bucket_name}")
                    
                except Exception as e:
                    logger.warning(f"Could not encrypt bucket {bucket_name}: {e}")
                    continue
            
            self.implementation_results['implementations'].append({
                'service': 'S3',
                'control': 'AC-16',
                'action': 'Bucket Encryption',
                'status': 'SUCCESS',
                'details': f'Applied KMS encryption to {buckets_updated} buckets'
            })
            
            logger.info(f"✅ S3 bucket encryption implemented for {buckets_updated} buckets")
            return True
            
        except Exception as e:
            error_msg = f"Failed to implement S3 bucket encryption: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def implement_s3_lifecycle_policies(self) -> bool:
        """Implement S3 lifecycle policies for data retention compliance."""
        logger.info("🔧 Implementing S3 lifecycle policies...")
        
        try:
            s3 = self.session.client('s3')
            
            # Get all buckets
            response = s3.list_buckets()
            buckets_updated = 0
            
            for bucket in response['Buckets']:
                bucket_name = bucket['Name']
                
                try:
                    # Check if bucket already has lifecycle configuration
                    try:
                        s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                        logger.info(f"Bucket {bucket_name} already has lifecycle configuration")
                        continue
                    except s3.exceptions.NoSuchLifecycleConfiguration:
                        # Bucket doesn't have lifecycle, add it
                        pass
                    
                    # Define lifecycle policy
                    lifecycle_config = {
                        'Rules': [
                            {
                                'ID': 'ProTechtDataRetention',
                                'Status': 'Enabled',
                                'Filter': {'Prefix': ''},
                                'Transitions': [
                                    {
                                        'Days': 30,
                                        'StorageClass': 'STANDARD_IA'
                                    },
                                    {
                                        'Days': 90,
                                        'StorageClass': 'GLACIER'
                                    },
                                    {
                                        'Days': 365,
                                        'StorageClass': 'DEEP_ARCHIVE'
                                    }
                                ],
                                'Expiration': {
                                    'Days': 2555  # 7 years retention
                                }
                            }
                        ]
                    }
                    
                    s3.put_bucket_lifecycle_configuration(
                        Bucket=bucket_name,
                        LifecycleConfiguration=lifecycle_config
                    )
                    
                    buckets_updated += 1
                    logger.info(f"✅ Applied lifecycle policy to bucket {bucket_name}")
                    
                except Exception as e:
                    logger.warning(f"Could not apply lifecycle to bucket {bucket_name}: {e}")
                    continue
            
            self.implementation_results['implementations'].append({
                'service': 'S3',
                'control': 'AC-16',
                'action': 'Lifecycle Policies',
                'status': 'SUCCESS',
                'details': f'Applied lifecycle policies to {buckets_updated} buckets'
            })
            
            logger.info(f"✅ S3 lifecycle policies implemented for {buckets_updated} buckets")
            return True
            
        except Exception as e:
            error_msg = f"Failed to implement S3 lifecycle policies: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def implement_security_hub(self) -> bool:
        """Enable Security Hub for AC-13 compliance."""
        logger.info("🔧 Enabling Security Hub...")
        
        try:
            securityhub = self.session.client('securityhub')
            
            # Check if Security Hub is already enabled
            try:
                securityhub.describe_hub()
                logger.info("Security Hub is already enabled")
                return True
            except securityhub.exceptions.InvalidAccessException:
                # Security Hub is not enabled, enable it
                pass
            
            # Enable Security Hub
            securityhub.enable_security_hub()
            
            # Enable all security standards
            standards = [
                'arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0',
                'arn:aws:securityhub:us-east-1::standards/cis-aws-foundations-benchmark/v/1.2.0',
                'arn:aws:securityhub:us-east-1::standards/pci-dss/v/3.2.1'
            ]
            
            for standard_arn in standards:
                try:
                    securityhub.batch_enable_standards(
                        StandardsSubscriptionRequests=[
                            {
                                'StandardsArn': standard_arn
                            }
                        ]
                    )
                except Exception as e:
                    logger.warning(f"Could not enable standard {standard_arn}: {e}")
            
            self.implementation_results['implementations'].append({
                'service': 'Security Hub',
                'control': 'AC-13',
                'action': 'Enable Security Hub',
                'status': 'SUCCESS',
                'details': 'Security Hub enabled with AWS Foundational, CIS, and PCI standards'
            })
            
            logger.info("✅ Security Hub enabled successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to enable Security Hub: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def implement_guardduty(self) -> bool:
        """Enable GuardDuty for AC-13 compliance."""
        logger.info("🔧 Enabling GuardDuty...")
        
        try:
            guardduty = self.session.client('guardduty')
            
            # Check if GuardDuty is already enabled
            try:
                detectors = guardduty.list_detectors()
                if detectors['DetectorIds']:
                    logger.info("GuardDuty is already enabled")
                    return True
            except Exception:
                pass
            
            # Create GuardDuty detector
            detector_response = guardduty.create_detector(
                Enable=True,
                FindingPublishingFrequency='FIFTEEN_MINUTES',
                DataSources={
                    'S3Logs': {
                        'Enable': True
                    },
                    'Kubernetes': {
                        'AuditLogs': {
                            'Enable': True
                        }
                    },
                    'MalwareProtection': {
                        'ScanEc2InstanceWithFindings': {
                            'EbsVolumes': {
                                'Enable': True
                            }
                        }
                    }
                }
            )
            
            detector_id = detector_response['DetectorId']
            
            # Create sample findings filter
            try:
                guardduty.create_filter(
                    DetectorId=detector_id,
                    Name='HighSeverityFindings',
                    Description='Filter for high severity findings',
                    Action='ARCHIVE',
                    Rank=1,
                    FindingCriteria={
                        'Criterion': {
                            'severity': {
                                'Gte': 7.0
                            }
                        }
                    }
                )
            except Exception as e:
                logger.warning(f"Could not create GuardDuty filter: {e}")
            
            self.implementation_results['implementations'].append({
                'service': 'GuardDuty',
                'control': 'AC-13',
                'action': 'Enable GuardDuty',
                'status': 'SUCCESS',
                'details': f'GuardDuty enabled with detector {detector_id}'
            })
            
            logger.info("✅ GuardDuty enabled successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to enable GuardDuty: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def implement_aws_config(self) -> bool:
        """Enable AWS Config for AC-7 compliance."""
        logger.info("🔧 Enabling AWS Config...")
        
        try:
            config = self.session.client('config')
            
            # Check if Config is already enabled
            try:
                recorders = config.describe_configuration_recorders()
                if recorders['ConfigurationRecorders']:
                    logger.info("AWS Config is already enabled")
                    return True
            except Exception:
                pass
            
            # Create S3 bucket for Config logs
            s3 = self.session.client('s3')
            config_bucket_name = f'aws-config-logs-{self.account_id}-{self.region}'
            
            try:
                s3.create_bucket(
                    Bucket=config_bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region} if self.region != 'us-east-1' else {}
                )
                
                # Apply public access block to Config bucket
                s3.put_public_access_block(
                    Bucket=config_bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
                
                # Apply bucket policy for Config
                bucket_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "AWSConfigBucketPermissionsCheck",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "config.amazonaws.com"
                            },
                            "Action": "s3:GetBucketAcl",
                            "Resource": f"arn:aws:s3:::{config_bucket_name}"
                        },
                        {
                            "Sid": "AWSConfigBucketExistenceCheck",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "config.amazonaws.com"
                            },
                            "Action": "s3:ListBucket",
                            "Resource": f"arn:aws:s3:::{config_bucket_name}"
                        },
                        {
                            "Sid": "AWSConfigBucketDelivery",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "config.amazonaws.com"
                            },
                            "Action": "s3:PutObject",
                            "Resource": f"arn:aws:s3:::{config_bucket_name}/*"
                        }
                    ]
                }
                
                s3.put_bucket_policy(
                    Bucket=config_bucket_name,
                    Policy=json.dumps(bucket_policy)
                )
                
            except s3.exceptions.BucketAlreadyExists:
                logger.info(f"Config bucket {config_bucket_name} already exists")
            except Exception as e:
                logger.warning(f"Could not create Config bucket: {e}")
                return False
            
            # Create IAM role for Config
            iam = self.session.client('iam')
            role_name = 'AWSConfigRole'
            
            try:
                # Create role
                trust_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "config.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }
                
                iam.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    Description='Role for AWS Config service'
                )
                
                # Attach managed policy
                iam.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn='arn:aws:iam::aws:policy/service-role/ConfigRole'
                )
                
                # Attach S3 policy
                s3_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "s3:GetBucketAcl",
                                "s3:ListBucket"
                            ],
                            "Resource": f"arn:aws:s3:::{config_bucket_name}"
                        },
                        {
                            "Effect": "Allow",
                            "Action": "s3:PutObject",
                            "Resource": f"arn:aws:s3:::{config_bucket_name}/*"
                        }
                    ]
                }
                
                iam.put_role_policy(
                    RoleName=role_name,
                    PolicyName='ConfigS3Policy',
                    PolicyDocument=json.dumps(s3_policy)
                )
                
            except iam.exceptions.EntityAlreadyExistsException:
                logger.info(f"Config role {role_name} already exists")
            except Exception as e:
                logger.warning(f"Could not create Config role: {e}")
                return False
            
            # Create configuration recorder
            try:
                config.put_configuration_recorder(
                    ConfigurationRecorder={
                        'name': 'default',
                        'roleARN': f'arn:aws:iam::{self.account_id}:role/{role_name}',
                        'recordingGroup': {
                            'allSupported': True,
                            'includeGlobalResourceTypes': True
                        }
                    }
                )
            except Exception as e:
                logger.warning(f"Could not create configuration recorder: {e}")
                return False
            
            # Create delivery channel
            try:
                config.put_delivery_channel(
                    DeliveryChannel={
                        'name': 'default',
                        's3BucketName': config_bucket_name,
                        's3KeyPrefix': 'config-logs/',
                        'snsTopicARN': f'arn:aws:sns:{self.region}:{self.account_id}:config-topic'
                    }
                )
            except Exception as e:
                logger.warning(f"Could not create delivery channel: {e}")
                return False
            
            # Start configuration recorder
            try:
                config.start_configuration_recorder(
                    ConfigurationRecorderName='default'
                )
            except Exception as e:
                logger.warning(f"Could not start configuration recorder: {e}")
                return False
            
            self.implementation_results['implementations'].append({
                'service': 'AWS Config',
                'control': 'AC-7',
                'action': 'Enable AWS Config',
                'status': 'SUCCESS',
                'details': f'AWS Config enabled with S3 bucket {config_bucket_name}'
            })
            
            logger.info("✅ AWS Config enabled successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to enable AWS Config: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def implement_cloudtrail_improvements(self) -> bool:
        """Improve CloudTrail configuration for AC-9 compliance."""
        logger.info("🔧 Improving CloudTrail configuration...")
        
        try:
            cloudtrail = self.session.client('cloudtrail')
            
            # Get existing trails
            trails = cloudtrail.describe_trails()
            
            if not trails['trailList']:
                logger.info("No CloudTrail trails found, creating new one")
                return self.create_cloudtrail_trail()
            
            # Improve existing trail
            trail = trails['trailList'][0]
            trail_name = trail['Name']
            
            # Update trail to include all regions
            try:
                cloudtrail.update_trail(
                    Name=trail_name,
                    IncludeGlobalServiceEvents=True,
                    IsMultiRegionTrail=True,
                    EnableLogFileValidation=True
                )
            except Exception as e:
                logger.warning(f"Could not update trail {trail_name}: {e}")
            
            # Start logging
            try:
                cloudtrail.start_logging(Name=trail_name)
            except Exception as e:
                logger.warning(f"Could not start logging for trail {trail_name}: {e}")
            
            self.implementation_results['implementations'].append({
                'service': 'CloudTrail',
                'control': 'AC-9',
                'action': 'Improve CloudTrail',
                'status': 'SUCCESS',
                'details': f'CloudTrail trail {trail_name} improved with multi-region and validation'
            })
            
            logger.info("✅ CloudTrail configuration improved")
            return True
            
        except Exception as e:
            error_msg = f"Failed to improve CloudTrail: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def create_cloudtrail_trail(self) -> bool:
        """Create a new CloudTrail trail."""
        try:
            cloudtrail = self.session.client('cloudtrail')
            s3 = self.session.client('s3')
            
            # Create S3 bucket for CloudTrail
            trail_bucket_name = f'aws-cloudtrail-logs-{self.account_id}-{self.region}'
            
            try:
                s3.create_bucket(
                    Bucket=trail_bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region} if self.region != 'us-east-1' else {}
                )
                
                # Apply public access block
                s3.put_public_access_block(
                    Bucket=trail_bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
                
            except s3.exceptions.BucketAlreadyExists:
                logger.info(f"CloudTrail bucket {trail_bucket_name} already exists")
            except Exception as e:
                logger.warning(f"Could not create CloudTrail bucket: {e}")
                return False
            
            # Create CloudTrail
            trail_name = 'ProTechtCloudTrail'
            try:
                cloudtrail.create_trail(
                    Name=trail_name,
                    S3BucketName=trail_bucket_name,
                    IncludeGlobalServiceEvents=True,
                    IsMultiRegionTrail=True,
                    EnableLogFileValidation=True,
                    KmsKeyId='alias/aws/s3'
                )
                
                # Start logging
                cloudtrail.start_logging(Name=trail_name)
                
                self.implementation_results['implementations'].append({
                    'service': 'CloudTrail',
                    'control': 'AC-9',
                    'action': 'Create CloudTrail',
                    'status': 'SUCCESS',
                    'details': f'CloudTrail trail {trail_name} created with S3 bucket {trail_bucket_name}'
                })
                
                logger.info("✅ CloudTrail trail created successfully")
                return True
                
            except Exception as e:
                logger.warning(f"Could not create CloudTrail: {e}")
                return False
                
        except Exception as e:
            error_msg = f"Failed to create CloudTrail: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def implement_vpc_flow_logs(self) -> bool:
        """Implement VPC flow logs for AC-4, AC-11, AC-12 compliance."""
        logger.info("🔧 Implementing VPC flow logs...")
        
        try:
            ec2 = self.session.client('ec2')
            s3 = self.session.client('s3')
            
            # Create S3 bucket for flow logs
            flow_logs_bucket_name = f'aws-vpc-flow-logs-{self.account_id}-{self.region}'
            
            try:
                s3.create_bucket(
                    Bucket=flow_logs_bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region} if self.region != 'us-east-1' else {}
                )
                
                # Apply public access block
                s3.put_public_access_block(
                    Bucket=flow_logs_bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
                
            except s3.exceptions.BucketAlreadyExists:
                logger.info(f"Flow logs bucket {flow_logs_bucket_name} already exists")
            except Exception as e:
                logger.warning(f"Could not create flow logs bucket: {e}")
                return False
            
            # Get all VPCs
            vpcs = ec2.describe_vpcs()
            flow_logs_created = 0
            
            for vpc in vpcs['Vpcs']:
                vpc_id = vpc['VpcId']
                
                try:
                    # Check if flow logs already exist
                    existing_logs = ec2.describe_flow_logs(
                        Filter=[
                            {
                                'Name': 'resource-id',
                                'Values': [vpc_id]
                            }
                        ]
                    )
                    
                    if existing_logs['FlowLogs']:
                        logger.info(f"Flow logs already exist for VPC {vpc_id}")
                        continue
                    
                    # Create flow log
                    ec2.create_flow_logs(
                        ResourceIds=[vpc_id],
                        ResourceType='VPC',
                        TrafficType='ALL',
                        LogDestinationType='s3',
                        LogDestination=f'arn:aws:s3:::{flow_logs_bucket_name}/vpc-flow-logs/',
                        LogFormat='${version} ${account-id} ${interface-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${packets} ${bytes} ${windowstart} ${windowend} ${action} ${flow-log-status}'
                    )
                    
                    flow_logs_created += 1
                    logger.info(f"✅ Created flow logs for VPC {vpc_id}")
                    
                except Exception as e:
                    logger.warning(f"Could not create flow logs for VPC {vpc_id}: {e}")
                    continue
            
            self.implementation_results['implementations'].append({
                'service': 'VPC',
                'control': 'AC-4, AC-11, AC-12',
                'action': 'VPC Flow Logs',
                'status': 'SUCCESS',
                'details': f'Created flow logs for {flow_logs_created} VPCs'
            })
            
            logger.info(f"✅ VPC flow logs implemented for {flow_logs_created} VPCs")
            return True
            
        except Exception as e:
            error_msg = f"Failed to implement VPC flow logs: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def implement_cloudfront_tls_policy(self) -> bool:
        """Implement CloudFront TLS policy for AC-4, AC-11, AC-12 compliance."""
        logger.info("🔧 Implementing CloudFront TLS policy...")
        
        try:
            cloudfront = self.session.client('cloudfront')
            
            # Get all distributions
            distributions = cloudfront.list_distributions()
            distributions_updated = 0
            
            for dist in distributions['DistributionList']['Items']:
                dist_id = dist['Id']
                
                try:
                    # Get distribution config
                    dist_config = cloudfront.get_distribution_config(Id=dist_id)
                    config = dist_config['DistributionConfig']
                    
                    # Update TLS policy
                    if 'ViewerCertificate' in config:
                        config['ViewerCertificate']['MinimumProtocolVersion'] = 'TLSv1.2_2021'
                        config['ViewerCertificate']['SslSupportMethod'] = 'sni-only'
                    
                    # Update distribution
                    cloudfront.update_distribution(
                        Id=dist_id,
                        DistributionConfig=config,
                        IfMatch=dist_config['ETag']
                    )
                    
                    distributions_updated += 1
                    logger.info(f"✅ Updated TLS policy for distribution {dist_id}")
                    
                except Exception as e:
                    logger.warning(f"Could not update distribution {dist_id}: {e}")
                    continue
            
            self.implementation_results['implementations'].append({
                'service': 'CloudFront',
                'control': 'AC-4, AC-11, AC-12',
                'action': 'TLS Policy',
                'status': 'SUCCESS',
                'details': f'Updated TLS policy for {distributions_updated} distributions'
            })
            
            logger.info(f"✅ CloudFront TLS policy implemented for {distributions_updated} distributions")
            return True
            
        except Exception as e:
            error_msg = f"Failed to implement CloudFront TLS policy: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.implementation_results['errors'].append(error_msg)
            return False
    
    def run_comprehensive_implementation(self) -> Dict[str, Any]:
        """Run comprehensive implementation of all recommendations."""
        logger.info("🚀 Starting comprehensive AWS compliance implementation...")
        
        start_time = time.time()
        
        # Track implementation results
        implementations = []
        errors = []
        
        # High Priority Implementations
        logger.info("🔴 Implementing HIGH PRIORITY recommendations...")
        
        if self.implement_password_policy():
            implementations.append("Password Policy")
        else:
            errors.append("Password Policy")
        
        if self.implement_s3_public_access_block():
            implementations.append("S3 Public Access Block")
        else:
            errors.append("S3 Public Access Block")
        
        if self.implement_s3_bucket_encryption():
            implementations.append("S3 Bucket Encryption")
        else:
            errors.append("S3 Bucket Encryption")
        
        # Medium Priority Implementations
        logger.info("🟡 Implementing MEDIUM PRIORITY recommendations...")
        
        if self.implement_security_hub():
            implementations.append("Security Hub")
        else:
            errors.append("Security Hub")
        
        if self.implement_guardduty():
            implementations.append("GuardDuty")
        else:
            errors.append("GuardDuty")
        
        if self.implement_aws_config():
            implementations.append("AWS Config")
        else:
            errors.append("AWS Config")
        
        # Low Priority Implementations
        logger.info("🟢 Implementing LOW PRIORITY recommendations...")
        
        if self.implement_s3_lifecycle_policies():
            implementations.append("S3 Lifecycle Policies")
        else:
            errors.append("S3 Lifecycle Policies")
        
        if self.implement_cloudtrail_improvements():
            implementations.append("CloudTrail Improvements")
        else:
            errors.append("CloudTrail Improvements")
        
        if self.implement_vpc_flow_logs():
            implementations.append("VPC Flow Logs")
        else:
            errors.append("VPC Flow Logs")
        
        if self.implement_cloudfront_tls_policy():
            implementations.append("CloudFront TLS Policy")
        else:
            errors.append("CloudFront TLS Policy")
        
        # Calculate summary
        implementation_duration = time.time() - start_time
        self.implementation_results['summary'] = {
            'total_implementations': len(implementations),
            'successful_implementations': len(implementations),
            'failed_implementations': len(errors),
            'implementation_duration': implementation_duration,
            'implementations': implementations,
            'errors': errors
        }
        
        logger.info(f"✅ Implementation completed in {implementation_duration:.2f} seconds")
        logger.info(f"📊 Results: {len(implementations)} successful, {len(errors)} failed")
        
        return self.implementation_results
    
    def save_implementation_report(self, filename: str = None) -> str:
        """Save implementation report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/aws_compliance_implementation_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.implementation_results, f, indent=2, default=str)
            
            logger.info(f"✅ Implementation report saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Failed to save implementation report: {e}")
            return ""

def main():
    """Main function to run the AWS compliance implementation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AWS Compliance Implementation Script')
    parser.add_argument('--profile', default='tanmay_modi', help='AWS profile to use')
    parser.add_argument('--region', default='us-east-1', help='AWS region to use')
    parser.add_argument('--report-file', help='Output file for implementation report')
    
    args = parser.parse_args()
    
    # Create and initialize implementer
    implementer = AWSComplianceImplementer(profile_name=args.profile, region=args.region)
    
    if not implementer.initialize():
        logger.error("❌ Failed to initialize implementer")
        sys.exit(1)
    
    # Run comprehensive implementation
    logger.info("🔍 Running comprehensive AWS compliance implementation...")
    results = implementer.run_comprehensive_implementation()
    
    # Save report
    report_file = implementer.save_implementation_report(args.report_file)
    
    # Print summary
    summary = results['summary']
    print(f"\n📊 Implementation Summary:")
    print(f"   Account: {results['account_id']}")
    print(f"   Duration: {summary['implementation_duration']:.2f} seconds")
    print(f"   Successful: {summary['successful_implementations']}")
    print(f"   Failed: {summary['failed_implementations']}")
    
    if summary['implementations']:
        print(f"\n✅ Successful Implementations:")
        for impl in summary['implementations']:
            print(f"   - {impl}")
    
    if summary['errors']:
        print(f"\n❌ Failed Implementations:")
        for error in summary['errors']:
            print(f"   - {error}")
    
    if report_file:
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if summary['failed_implementations'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
