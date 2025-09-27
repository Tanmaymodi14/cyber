#!/usr/bin/env python3
"""
Test script to verify no-data state works correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import ProTechtDatabase
from technical_engine import evaluate_ac_controls

def test_no_data_state():
    """Test that the system properly handles no data state"""
    
    print("🧪 Testing no-data state...")
    
    # Load data from database
    db = ProTechtDatabase()
    data = db.load_aws_data_from_db()
    
    print(f"📊 Database data keys: {list(data.keys())}")
    print(f"👥 IAM Users: {len(data.get('iam', {}).get('users', []))}")
    print(f"🪣 S3 Buckets: {len(data.get('s3', {}).get('buckets', []))}")
    print(f"🔑 KMS Keys: {len(data.get('kms', {}).get('keys', []))}")
    print(f"🛤️ CloudTrail Trails: {len(data.get('cloudtrail', {}).get('trails', []))}")
    
    # Check if we have real data
    has_real_data = any([
        len(data.get('iam', {}).get('users', [])) > 0,
        len(data.get('s3', {}).get('buckets', [])) > 0,
        len(data.get('kms', {}).get('keys', [])) > 0,
        len(data.get('cloudtrail', {}).get('trails', [])) > 0
    ])
    
    print(f"✅ Has real data: {has_real_data}")
    
    if not has_real_data:
        print("🎯 No real data detected - system should show no-data state")
        return True
    else:
        print("❌ Real data detected - system should show compliance data")
        return False

if __name__ == "__main__":
    success = test_no_data_state()
    if success:
        print("\n✅ No-data state test PASSED")
    else:
        print("\n❌ No-data state test FAILED")
        sys.exit(1)
