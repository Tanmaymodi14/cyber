#!/usr/bin/env python3
"""
AWS Background Agent for proTecht Compliance Platform

This agent analyzes the current AWS environment, maps services to FedRAMP AC controls,
and provides recommendations for better integration with the proTecht platform.

Author: proTecht Team
Purpose: Continuous AWS environment monitoring and compliance assessment
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

from database import ProTechtDatabase
from technical_engine import evaluate_ac_controls

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/aws_background_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AWSBackgroundAgent')

class AWSBackgroundAgent:
    """Background agent for continuous AWS environment analysis and compliance monitoring."""
    
    def __init__(self, profile_name: str = 'tanmay_modi', region: str = 'us-east-1'):
        self.profile_name = profile_name
        self.region = region
        self.session = boto3.Session(profile_name=profile_name, region_name=region)
        self.account_id = None
        self.user_arn = None
        self.db = ProTechtDatabase()
        self.analysis_results = {}
        
    def initialize(self) -> bool:
        """Initialize the agent and verify AWS connectivity."""
        try:
            # Get caller identity
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            self.account_id = identity['Account']
            self.user_arn = identity['Arn']
            
            logger.info(f"✅ Connected to AWS Account: {self.account_id}")
            logger.info(f"✅ User: {self.user_arn}")
            logger.info(f"✅ Region: {self.region}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS connection: {e}")
            return False
    
    def analyze_iam_environment(self) -> Dict[str, Any]:
        """Analyze IAM configuration for AC-3, AC-5, AC-6, AC-7, AC-9 controls."""
        logger.info("🔍 Analyzing IAM environment...")
        
        iam = self.session.client('iam')
        results = {
            'users': [],
            'roles': [],
            'policies': [],
            'password_policy': {},
            'account_summary': {},
            'compliance_issues': []
        }
        
        try:
            # Get account summary
            summary = iam.get_account_summary()
            results['account_summary'] = summary['SummaryMap']
            
            # Get password policy
            try:
                password_policy = iam.get_account_password_policy()
                results['password_policy'] = password_policy['PasswordPolicy']
            except iam.exceptions.NoSuchEntityException:
                results['compliance_issues'].append("No password policy configured")
            
            # List users with detailed info
            paginator = iam.get_paginator('list_users')
            for page in paginator.paginate():
                for user in page['Users']:
                    user_info = {
                        'UserName': user['UserName'],
                        'CreateDate': user['CreateDate'].isoformat(),
                        'PasswordLastUsed': user.get('PasswordLastUsed', 'Never'),
                        'AttachedPolicies': [],
                        'InlinePolicies': [],
                        'Groups': [],
                        'AccessKeys': []
                    }
                    
                    # Get attached policies
                    try:
                        policies = iam.list_attached_user_policies(UserName=user['UserName'])
                        user_info['AttachedPolicies'] = [p['PolicyName'] for p in policies['AttachedPolicies']]
                    except Exception as e:
                        logger.warning(f"Could not get policies for user {user['UserName']}: {e}")
                    
                    # Get inline policies
                    try:
                        inline_policies = iam.list_user_policies(UserName=user['UserName'])
                        user_info['InlinePolicies'] = inline_policies['PolicyNames']
                    except Exception as e:
                        logger.warning(f"Could not get inline policies for user {user['UserName']}: {e}")
                    
                    # Get groups
                    try:
                        groups = iam.get_groups_for_user(UserName=user['UserName'])
                        user_info['Groups'] = [g['GroupName'] for g in groups['Groups']]
                    except Exception as e:
                        logger.warning(f"Could not get groups for user {user['UserName']}: {e}")
                    
                    # Get access keys
                    try:
                        access_keys = iam.list_access_keys(UserName=user['UserName'])
                        user_info['AccessKeys'] = [
                            {
                                'AccessKeyId': key['AccessKeyId'],
                                'Status': key['Status'],
                                'CreateDate': key['CreateDate'].isoformat()
                            }
                            for key in access_keys['AccessKeyMetadata']
                        ]
                    except Exception as e:
                        logger.warning(f"Could not get access keys for user {user['UserName']}: {e}")
                    
                    results['users'].append(user_info)
            
            # List roles with detailed info
            paginator = iam.get_paginator('list_roles')
            for page in paginator.paginate():
                for role in page['Roles']:
                    role_info = {
                        'RoleName': role['RoleName'],
                        'CreateDate': role['CreateDate'].isoformat(),
                        'AssumeRolePolicyDocument': role['AssumeRolePolicyDocument'],
                        'AttachedPolicies': [],
                        'InlinePolicies': [],
                        'PermissionsBoundary': role.get('PermissionsBoundary', {}),
                        'MaxSessionDuration': role.get('MaxSessionDuration', 3600)
                    }
                    
                    # Get attached policies
                    try:
                        policies = iam.list_attached_role_policies(RoleName=role['RoleName'])
                        role_info['AttachedPolicies'] = [p['PolicyName'] for p in policies['AttachedPolicies']]
                    except Exception as e:
                        logger.warning(f"Could not get policies for role {role['RoleName']}: {e}")
                    
                    # Get inline policies
                    try:
                        inline_policies = iam.list_role_policies(RoleName=role['RoleName'])
                        role_info['InlinePolicies'] = inline_policies['PolicyNames']
                    except Exception as e:
                        logger.warning(f"Could not get inline policies for role {role['RoleName']}: {e}")
                    
                    results['roles'].append(role_info)
            
            logger.info(f"✅ Found {len(results['users'])} users, {len(results['roles'])} roles")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing IAM: {e}")
            results['compliance_issues'].append(f"IAM analysis failed: {str(e)}")
        
        return results
    
    def analyze_s3_environment(self) -> Dict[str, Any]:
        """Analyze S3 configuration for AC-15, AC-16, AC-21 controls."""
        logger.info("🔍 Analyzing S3 environment...")
        
        s3 = self.session.client('s3')
        s3_config = self.session.client('s3control')
        results = {
            'buckets': [],
            'account_public_access_block': {},
            'compliance_issues': []
        }
        
        try:
            # Get account public access block
            try:
                pab = s3_config.get_public_access_block(AccountId=self.account_id)
                results['account_public_access_block'] = pab['PublicAccessBlockConfiguration']
            except Exception as e:
                logger.warning(f"Could not get account public access block: {e}")
                results['compliance_issues'].append("No account-level public access block")
            
            # List all buckets
            response = s3.list_buckets()
            for bucket in response['Buckets']:
                bucket_name = bucket['Name']
                bucket_info = {
                    'Name': bucket_name,
                    'CreationDate': bucket['CreationDate'].isoformat(),
                    'encryption': {},
                    'public_access_block': {},
                    'versioning': {},
                    'lifecycle': {},
                    'object_lock': {},
                    'policy': None
                }
                
                try:
                    # Get encryption configuration
                    try:
                        encryption = s3.get_bucket_encryption(Bucket=bucket_name)
                        bucket_info['encryption'] = encryption['ServerSideEncryptionConfiguration']
                    except s3.exceptions.NoSuchEncryptionConfiguration:
                        bucket_info['encryption'] = {'Rules': []}
                        results['compliance_issues'].append(f"Bucket {bucket_name} has no encryption")
                    
                    # Get public access block
                    try:
                        pab = s3.get_public_access_block(Bucket=bucket_name)
                        bucket_info['public_access_block'] = pab['PublicAccessBlockConfiguration']
                    except s3.exceptions.NoSuchPublicAccessBlockConfiguration:
                        bucket_info['public_access_block'] = {'BlockPublicAcls': False, 'BlockPublicPolicy': False}
                        results['compliance_issues'].append(f"Bucket {bucket_name} has no public access block")
                    
                    # Get versioning
                    try:
                        versioning = s3.get_bucket_versioning(Bucket=bucket_name)
                        bucket_info['versioning'] = versioning
                    except Exception as e:
                        logger.warning(f"Could not get versioning for bucket {bucket_name}: {e}")
                    
                    # Get lifecycle configuration
                    try:
                        lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                        bucket_info['lifecycle'] = lifecycle
                    except s3.exceptions.NoSuchLifecycleConfiguration:
                        bucket_info['lifecycle'] = {'Rules': []}
                    
                    # Get object lock configuration
                    try:
                        object_lock = s3.get_object_lock_configuration(Bucket=bucket_name)
                        bucket_info['object_lock'] = object_lock
                    except s3.exceptions.NoSuchObjectLockConfiguration:
                        bucket_info['object_lock'] = {'ObjectLockEnabled': 'Disabled'}
                    
                    # Get bucket policy
                    try:
                        policy = s3.get_bucket_policy(Bucket=bucket_name)
                        bucket_info['policy'] = json.loads(policy['Policy'])
                    except s3.exceptions.NoSuchBucketPolicy:
                        bucket_info['policy'] = None
                    
                except Exception as e:
                    logger.warning(f"Error analyzing bucket {bucket_name}: {e}")
                    bucket_info['error'] = str(e)
                
                results['buckets'].append(bucket_info)
            
            logger.info(f"✅ Found {len(results['buckets'])} S3 buckets")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing S3: {e}")
            results['compliance_issues'].append(f"S3 analysis failed: {str(e)}")
        
        return results
    
    def analyze_kms_environment(self) -> Dict[str, Any]:
        """Analyze KMS configuration for AC-16 control."""
        logger.info("🔍 Analyzing KMS environment...")
        
        kms = self.session.client('kms')
        results = {
            'keys': [],
            'aliases': [],
            'compliance_issues': []
        }
        
        try:
            # List all keys
            paginator = kms.get_paginator('list_keys')
            for page in paginator.paginate():
                for key in page['Keys']:
                    key_id = key['KeyId']
                    key_info = {
                        'KeyId': key_id,
                        'Arn': key['KeyArn'],
                        'KeyState': key['KeyState'],
                        'KeyUsage': key['KeyUsage'],
                        'KeySpec': key['KeySpec'],
                        'CreationDate': key['CreationDate'].isoformat(),
                        'rotation_enabled': False,
                        'description': '',
                        'key_policy': None
                    }
                    
                    try:
                        # Get key details
                        key_details = kms.describe_key(KeyId=key_id)
                        key_info['description'] = key_details['KeyMetadata'].get('Description', '')
                        
                        # Get rotation status
                        try:
                            rotation = kms.get_key_rotation_status(KeyId=key_id)
                            key_info['rotation_enabled'] = rotation['KeyRotationEnabled']
                        except kms.exceptions.InvalidKeyUsageException:
                            # Some key types don't support rotation
                            pass
                        
                        # Get key policy
                        try:
                            policy = kms.get_key_policy(KeyId=key_id, PolicyName='default')
                            key_info['key_policy'] = json.loads(policy['Policy'])
                        except Exception as e:
                            logger.warning(f"Could not get policy for key {key_id}: {e}")
                    
                    except Exception as e:
                        logger.warning(f"Error analyzing key {key_id}: {e}")
                        key_info['error'] = str(e)
                    
                    results['keys'].append(key_info)
            
            # List aliases
            paginator = kms.get_paginator('list_aliases')
            for page in paginator.paginate():
                for alias in page['Aliases']:
                    alias_info = {
                        'AliasName': alias['AliasName'],
                        'AliasArn': alias['AliasArn'],
                        'TargetKeyId': alias['TargetKeyId'],
                        'CreationDate': alias['CreationDate'].isoformat()
                    }
                    results['aliases'].append(alias_info)
            
            logger.info(f"✅ Found {len(results['keys'])} KMS keys, {len(results['aliases'])} aliases")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing KMS: {e}")
            results['compliance_issues'].append(f"KMS analysis failed: {str(e)}")
        
        return results
    
    def analyze_cloudtrail_environment(self) -> Dict[str, Any]:
        """Analyze CloudTrail configuration for AC-9 control."""
        logger.info("🔍 Analyzing CloudTrail environment...")
        
        cloudtrail = self.session.client('cloudtrail')
        results = {
            'trails': [],
            'event_selectors': [],
            'compliance_issues': []
        }
        
        try:
            # List all trails
            response = cloudtrail.describe_trails()
            for trail in response['trailList']:
                trail_info = {
                    'Name': trail['Name'],
                    'S3BucketName': trail.get('S3BucketName', ''),
                    'S3KeyPrefix': trail.get('S3KeyPrefix', ''),
                    'IncludeGlobalServiceEvents': trail.get('IncludeGlobalServiceEvents', False),
                    'IsMultiRegionTrail': trail.get('IsMultiRegionTrail', False),
                    'HomeRegion': trail.get('HomeRegion', ''),
                    'TrailARN': trail.get('TrailARN', ''),
                    'LogFileValidationEnabled': trail.get('LogFileValidationEnabled', False),
                    'KmsKeyId': trail.get('KmsKeyId', ''),
                    'IsOrganizationTrail': trail.get('IsOrganizationTrail', False),
                    'Status': {}
                }
                
                try:
                    # Get trail status
                    status = cloudtrail.get_trail_status(Name=trail['Name'])
                    trail_info['Status'] = status
                except Exception as e:
                    logger.warning(f"Could not get status for trail {trail['Name']}: {e}")
                
                results['trails'].append(trail_info)
            
            # Get event selectors for each trail
            for trail in results['trails']:
                try:
                    selectors = cloudtrail.get_event_selectors(TrailName=trail['Name'])
                    trail['EventSelectors'] = selectors.get('EventSelectors', [])
                except Exception as e:
                    logger.warning(f"Could not get event selectors for trail {trail['Name']}: {e}")
                    trail['EventSelectors'] = []
            
            logger.info(f"✅ Found {len(results['trails'])} CloudTrail trails")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing CloudTrail: {e}")
            results['compliance_issues'].append(f"CloudTrail analysis failed: {str(e)}")
        
        return results
    
    def analyze_vpc_environment(self) -> Dict[str, Any]:
        """Analyze VPC configuration for AC-4, AC-11, AC-12, AC-21 controls."""
        logger.info("🔍 Analyzing VPC environment...")
        
        ec2 = self.session.client('ec2')
        results = {
            'vpcs': [],
            'security_groups': [],
            'flow_logs': [],
            'compliance_issues': []
        }
        
        try:
            # List VPCs
            response = ec2.describe_vpcs()
            for vpc in response['Vpcs']:
                vpc_info = {
                    'VpcId': vpc['VpcId'],
                    'CidrBlock': vpc['CidrBlock'],
                    'State': vpc['State'],
                    'IsDefault': vpc['IsDefault'],
                    'Tags': vpc.get('Tags', [])
                }
                results['vpcs'].append(vpc_info)
            
            # List security groups
            response = ec2.describe_security_groups()
            for sg in response['SecurityGroups']:
                sg_info = {
                    'GroupId': sg['GroupId'],
                    'GroupName': sg['GroupName'],
                    'Description': sg['Description'],
                    'VpcId': sg['VpcId'],
                    'IpPermissions': sg['IpPermissions'],
                    'IpPermissionsEgress': sg['IpPermissionsEgress'],
                    'Tags': sg.get('Tags', [])
                }
                results['security_groups'].append(sg_info)
            
            # List flow logs
            response = ec2.describe_flow_logs()
            for flow_log in response['FlowLogs']:
                flow_log_info = {
                    'FlowLogId': flow_log['FlowLogId'],
                    'FlowLogStatus': flow_log['FlowLogStatus'],
                    'ResourceId': flow_log['ResourceId'],
                    'ResourceType': flow_log['ResourceType'],
                    'TrafficType': flow_log['TrafficType'],
                    'LogDestinationType': flow_log['LogDestinationType'],
                    'LogDestination': flow_log.get('LogDestination', ''),
                    'LogFormat': flow_log.get('LogFormat', ''),
                    'DeliverLogsStatus': flow_log.get('DeliverLogsStatus', ''),
                    'CreationTime': flow_log['CreationTime'].isoformat()
                }
                results['flow_logs'].append(flow_log_info)
            
            logger.info(f"✅ Found {len(results['vpcs'])} VPCs, {len(results['security_groups'])} security groups, {len(results['flow_logs'])} flow logs")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing VPC: {e}")
            results['compliance_issues'].append(f"VPC analysis failed: {str(e)}")
        
        return results
    
    def analyze_cloudfront_environment(self) -> Dict[str, Any]:
        """Analyze CloudFront configuration for AC-4, AC-11, AC-12, AC-21 controls."""
        logger.info("🔍 Analyzing CloudFront environment...")
        
        cloudfront = self.session.client('cloudfront')
        results = {
            'distributions': [],
            'compliance_issues': []
        }
        
        try:
            # List distributions
            paginator = cloudfront.get_paginator('list_distributions')
            for page in paginator.paginate():
                for dist in page['DistributionList']['Items']:
                    dist_info = {
                        'Id': dist['Id'],
                        'ARN': dist['ARN'],
                        'Status': dist['Status'],
                        'DomainName': dist['DomainName'],
                        'Comment': dist.get('Comment', ''),
                        'PriceClass': dist.get('PriceClass', ''),
                        'Enabled': dist['Enabled'],
                        'HttpVersion': dist.get('HttpVersion', ''),
                        'IsIPV6Enabled': dist.get('IsIPV6Enabled', False),
                        'LastModifiedTime': dist['LastModifiedTime'].isoformat(),
                        'ViewerCertificate': dist.get('ViewerCertificate', {}),
                        'DefaultCacheBehavior': dist.get('DefaultCacheBehavior', {}),
                        'CacheBehaviors': dist.get('CacheBehaviors', {}),
                        'Origins': dist.get('Origins', {}),
                        'DefaultRootObject': dist.get('DefaultRootObject', ''),
                        'CustomErrorResponses': dist.get('CustomErrorResponses', {}),
                        'Logging': dist.get('Logging', {}),
                        'WebACLId': dist.get('WebACLId', ''),
                        'Restrictions': dist.get('Restrictions', {})
                    }
                    results['distributions'].append(dist_info)
            
            logger.info(f"✅ Found {len(results['distributions'])} CloudFront distributions")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing CloudFront: {e}")
            results['compliance_issues'].append(f"CloudFront analysis failed: {str(e)}")
        
        return results
    
    def analyze_waf_environment(self) -> Dict[str, Any]:
        """Analyze WAF configuration for AC-4, AC-21 controls."""
        logger.info("🔍 Analyzing WAF environment...")
        
        wafv2 = self.session.client('wafv2')
        results = {
            'web_acls': [],
            'ip_sets': [],
            'regex_pattern_sets': [],
            'rule_groups': [],
            'compliance_issues': []
        }
        
        try:
            # List Web ACLs
            response = wafv2.list_web_acls(Scope='CLOUDFRONT')
            for acl in response['WebACLs']:
                acl_info = {
                    'Name': acl['Name'],
                    'Id': acl['Id'],
                    'ARN': acl['ARN'],
                    'Description': acl.get('Description', ''),
                    'Rules': acl.get('Rules', []),
                    'DefaultAction': acl.get('DefaultAction', {}),
                    'VisibilityConfig': acl.get('VisibilityConfig', {}),
                    'Capacity': acl.get('Capacity', 0),
                    'ManagedByFirewallManager': acl.get('ManagedByFirewallManager', False)
                }
                results['web_acls'].append(acl_info)
            
            # List IP sets
            response = wafv2.list_ip_sets(Scope='CLOUDFRONT')
            for ip_set in response['IPSets']:
                ip_set_info = {
                    'Name': ip_set['Name'],
                    'Id': ip_set['Id'],
                    'ARN': ip_set['ARN'],
                    'Description': ip_set.get('Description', ''),
                    'IPAddressVersion': ip_set.get('IPAddressVersion', ''),
                    'Addresses': ip_set.get('Addresses', [])
                }
                results['ip_sets'].append(ip_set_info)
            
            logger.info(f"✅ Found {len(results['web_acls'])} Web ACLs, {len(results['ip_sets'])} IP sets")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing WAF: {e}")
            results['compliance_issues'].append(f"WAF analysis failed: {str(e)}")
        
        return results
    
    def analyze_security_services(self) -> Dict[str, Any]:
        """Analyze Security Hub, GuardDuty, and Config for AC-13 control."""
        logger.info("🔍 Analyzing security services...")
        
        results = {
            'security_hub': {},
            'guardduty': {},
            'config': {},
            'compliance_issues': []
        }
        
        try:
            # Security Hub
            try:
                sh = self.session.client('securityhub')
                sh_info = sh.describe_hub()
                results['security_hub'] = {
                    'HubArn': sh_info['HubArn'],
                    'SubscribedAt': sh_info['SubscribedAt'].isoformat(),
                    'AutoEnableControls': sh_info.get('AutoEnableControls', False)
                }
            except Exception as e:
                results['security_hub'] = {'enabled': False, 'error': str(e)}
                results['compliance_issues'].append("Security Hub not enabled")
            
            # GuardDuty
            try:
                gd = self.session.client('guardduty')
                detectors = gd.list_detectors()
                if detectors['DetectorIds']:
                    detector_id = detectors['DetectorIds'][0]
                    detector_info = gd.get_detector(DetectorId=detector_id)
                    results['guardduty'] = {
                        'DetectorId': detector_id,
                        'CreatedAt': detector_info['CreatedAt'].isoformat(),
                        'Status': detector_info['Status'],
                        'FindingPublishingFrequency': detector_info.get('FindingPublishingFrequency', ''),
                        'DataSources': detector_info.get('DataSources', {})
                    }
                else:
                    results['guardduty'] = {'enabled': False}
                    results['compliance_issues'].append("GuardDuty not enabled")
            except Exception as e:
                results['guardduty'] = {'enabled': False, 'error': str(e)}
                results['compliance_issues'].append("GuardDuty analysis failed")
            
            # Config
            try:
                config = self.session.client('config')
                recorders = config.describe_configuration_recorders()
                results['config'] = {
                    'ConfigurationRecorders': recorders.get('ConfigurationRecorders', []),
                    'enabled': len(recorders.get('ConfigurationRecorders', [])) > 0
                }
                if not results['config']['enabled']:
                    results['compliance_issues'].append("AWS Config not enabled")
            except Exception as e:
                results['config'] = {'enabled': False, 'error': str(e)}
                results['compliance_issues'].append("Config analysis failed")
            
            logger.info("✅ Security services analysis completed")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing security services: {e}")
            results['compliance_issues'].append(f"Security services analysis failed: {str(e)}")
        
        return results
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive AWS environment analysis."""
        logger.info("🚀 Starting comprehensive AWS environment analysis...")
        
        start_time = time.time()
        analysis_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'account_id': self.account_id,
            'user_arn': self.user_arn,
            'region': self.region,
            'analysis_duration': 0,
            'services': {},
            'compliance_summary': {},
            'recommendations': []
        }
        
        try:
            # Run all analyses
            analysis_results['services']['iam'] = self.analyze_iam_environment()
            analysis_results['services']['s3'] = self.analyze_s3_environment()
            analysis_results['services']['kms'] = self.analyze_kms_environment()
            analysis_results['services']['cloudtrail'] = self.analyze_cloudtrail_environment()
            analysis_results['services']['vpc'] = self.analyze_vpc_environment()
            analysis_results['services']['cloudfront'] = self.analyze_cloudfront_environment()
            analysis_results['services']['waf'] = self.analyze_waf_environment()
            analysis_results['services']['security_services'] = self.analyze_security_services()
            
            # Calculate analysis duration
            analysis_results['analysis_duration'] = time.time() - start_time
            
            # Generate compliance summary
            analysis_results['compliance_summary'] = self.generate_compliance_summary(analysis_results)
            
            # Generate recommendations
            analysis_results['recommendations'] = self.generate_recommendations(analysis_results)
            
            logger.info(f"✅ Analysis completed in {analysis_results['analysis_duration']:.2f} seconds")
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    def generate_compliance_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance summary based on analysis results."""
        summary = {
            'total_services_analyzed': len(analysis_results['services']),
            'critical_issues': 0,
            'warnings': 0,
            'compliant_services': 0,
            'control_coverage': {}
        }
        
        # Count issues across all services
        for service_name, service_data in analysis_results['services'].items():
            if 'compliance_issues' in service_data:
                summary['critical_issues'] += len(service_data['compliance_issues'])
            
            # Count specific resources
            if service_name == 'iam':
                summary['iam_users'] = len(service_data.get('users', []))
                summary['iam_roles'] = len(service_data.get('roles', []))
            elif service_name == 's3':
                summary['s3_buckets'] = len(service_data.get('buckets', []))
            elif service_name == 'kms':
                summary['kms_keys'] = len(service_data.get('keys', []))
            elif service_name == 'cloudtrail':
                summary['cloudtrail_trails'] = len(service_data.get('trails', []))
        
        return summary
    
    def generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # IAM recommendations
        iam_data = analysis_results['services'].get('iam', {})
        if not iam_data.get('password_policy'):
            recommendations.append({
                'service': 'IAM',
                'priority': 'High',
                'control': 'AC-7',
                'issue': 'No password policy configured',
                'recommendation': 'Configure a strong password policy with minimum length, complexity, and rotation requirements'
            })
        
        # S3 recommendations
        s3_data = analysis_results['services'].get('s3', {})
        unencrypted_buckets = [b for b in s3_data.get('buckets', []) if not b.get('encryption', {}).get('Rules')]
        if unencrypted_buckets:
            recommendations.append({
                'service': 'S3',
                'priority': 'High',
                'control': 'AC-16',
                'issue': f'{len(unencrypted_buckets)} buckets without encryption',
                'recommendation': 'Enable server-side encryption for all S3 buckets'
            })
        
        # KMS recommendations
        kms_data = analysis_results['services'].get('kms', {})
        keys_without_rotation = [k for k in kms_data.get('keys', []) if not k.get('rotation_enabled')]
        if keys_without_rotation:
            recommendations.append({
                'service': 'KMS',
                'priority': 'Medium',
                'control': 'AC-16',
                'issue': f'{len(keys_without_rotation)} keys without rotation',
                'recommendation': 'Enable automatic key rotation for all customer-managed KMS keys'
            })
        
        # CloudTrail recommendations
        ct_data = analysis_results['services'].get('cloudtrail', {})
        if not ct_data.get('trails'):
            recommendations.append({
                'service': 'CloudTrail',
                'priority': 'High',
                'control': 'AC-9',
                'issue': 'No CloudTrail trails configured',
                'recommendation': 'Enable CloudTrail logging for all regions and services'
            })
        
        # Security services recommendations
        security_data = analysis_results['services'].get('security_services', {})
        if not security_data.get('security_hub', {}).get('enabled'):
            recommendations.append({
                'service': 'Security Hub',
                'priority': 'Medium',
                'control': 'AC-13',
                'issue': 'Security Hub not enabled',
                'recommendation': 'Enable Security Hub for centralized security findings'
            })
        
        return recommendations
    
    def save_analysis_to_database(self, analysis_results: Dict[str, Any]) -> bool:
        """Save analysis results to the proTecht database."""
        try:
            # Convert analysis results to the format expected by the database
            aws_data = {
                'iam': analysis_results['services'].get('iam', {}),
                's3': analysis_results['services'].get('s3', {}),
                'kms': analysis_results['services'].get('kms', {}),
                'cloudtrail': analysis_results['services'].get('cloudtrail', {}),
                'vpc': analysis_results['services'].get('vpc', {}),
                'cloudfront': analysis_results['services'].get('cloudfront', {}),
                'waf': analysis_results['services'].get('waf', {}),
                'security_hub': analysis_results['services'].get('security_services', {}).get('security_hub', {}),
                'guardduty': analysis_results['services'].get('security_services', {}).get('guardduty', {}),
                'config': analysis_results['services'].get('security_services', {}).get('config', {})
            }
            
            # Ensure all values are dictionaries, not strings
            for key, value in aws_data.items():
                if isinstance(value, str):
                    aws_data[key] = {'error': value}
                elif not isinstance(value, dict):
                    aws_data[key] = {}
            
            # Save to database
            self.db.load_aws_data(aws_data)
            logger.info("✅ Analysis results saved to database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save analysis to database: {e}")
            return False
    
    def run_continuous_monitoring(self, interval_minutes: int = 60):
        """Run continuous monitoring of AWS environment."""
        logger.info(f"🔄 Starting continuous monitoring (every {interval_minutes} minutes)")
        
        while True:
            try:
                logger.info("🔄 Running scheduled analysis...")
                analysis_results = self.run_comprehensive_analysis()
                
                # Save to database
                self.save_analysis_to_database(analysis_results)
                
                # Log summary
                summary = analysis_results['compliance_summary']
                logger.info(f"📊 Analysis Summary: {summary['total_services_analyzed']} services, "
                          f"{summary['critical_issues']} critical issues, "
                          f"{len(analysis_results['recommendations'])} recommendations")
                
                # Wait for next interval
                logger.info(f"⏰ Waiting {interval_minutes} minutes until next analysis...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                logger.info("⏰ Waiting 5 minutes before retry...")
                time.sleep(300)  # Wait 5 minutes before retry

def main():
    """Main function to run the AWS background agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AWS Background Agent for proTecht')
    parser.add_argument('--profile', default='tanmay_modi', help='AWS profile to use')
    parser.add_argument('--region', default='us-east-1', help='AWS region to analyze')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in minutes')
    
    args = parser.parse_args()
    
    # Create and initialize agent
    agent = AWSBackgroundAgent(profile_name=args.profile, region=args.region)
    
    if not agent.initialize():
        logger.error("❌ Failed to initialize agent")
        sys.exit(1)
    
    if args.continuous:
        # Run continuous monitoring
        agent.run_continuous_monitoring(interval_minutes=args.interval)
    else:
        # Run single analysis
        logger.info("🔍 Running single analysis...")
        analysis_results = agent.run_comprehensive_analysis()
        
        # Save to database
        agent.save_analysis_to_database(analysis_results)
        
        # Print summary
        summary = analysis_results['compliance_summary']
        print(f"\n📊 Analysis Summary:")
        print(f"   Account: {analysis_results['account_id']}")
        print(f"   User: {analysis_results['user_arn']}")
        print(f"   Services Analyzed: {summary['total_services_analyzed']}")
        print(f"   Critical Issues: {summary['critical_issues']}")
        print(f"   Recommendations: {len(analysis_results['recommendations'])}")
        
        # Print recommendations
        if analysis_results['recommendations']:
            print(f"\n🔧 Top Recommendations:")
            for i, rec in enumerate(analysis_results['recommendations'][:5], 1):
                print(f"   {i}. [{rec['priority']}] {rec['service']}: {rec['recommendation']}")

if __name__ == "__main__":
    main()
