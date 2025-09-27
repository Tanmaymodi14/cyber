#!/usr/bin/env python3
"""Update CloudFront distribution timeout to 40 seconds."""

import boto3
import json
import sys
from botocore.exceptions import ClientError

def update_cloudfront_timeout(distribution_id: str, new_timeout: int = 40):
    """Update CloudFront distribution origin read timeout."""
    try:
        cloudfront = boto3.client('cloudfront')
        
        # Get current configuration
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        print(f"Current origin read timeout: {config['Origins']['Items'][0]['CustomOriginConfig']['OriginReadTimeout']}")
        
        # Update the timeout
        config['Origins']['Items'][0]['CustomOriginConfig']['OriginReadTimeout'] = new_timeout
        
        # Update the distribution
        update_response = cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print(f"Successfully updated CloudFront distribution {distribution_id}")
        print(f"New origin read timeout: {new_timeout} seconds")
        print(f"Status: {update_response['Distribution']['Status']}")
        
        return True
        
    except ClientError as e:
        print(f"Error updating CloudFront distribution: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_cloudfront_timeout.py <distribution_id>")
        print("Example: python update_cloudfront_timeout.py E1OW7N5159H93P")
        sys.exit(1)
    
    distribution_id = sys.argv[1]
    success = update_cloudfront_timeout(distribution_id)
    
    if success:
        print("\n✅ CloudFront timeout updated successfully!")
        print("Note: Changes may take 10-15 minutes to propagate globally.")
    else:
        print("\n❌ Failed to update CloudFront timeout")
        sys.exit(1)

if __name__ == "__main__":
    main()
