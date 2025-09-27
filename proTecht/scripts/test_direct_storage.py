#!/usr/bin/env python3
"""
Test direct storage of IAM data
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aws_collect import collect_all
from database import ProTechtDatabase

def test_direct_storage():
    """Test storing IAM data directly"""
    
    print("🔄 Collecting IAM data locally...")
    
    # Collect data locally
    collected = collect_all(profile='tanmay_modi', regions=['us-east-1'])
    
    print(f"✅ Collected data for: {list(collected.keys())}")
    
    if 'iam' in collected:
        iam_data = collected['iam']
        print(f"📊 IAM Users: {len(iam_data.get('users', []))}")
        print(f"📊 IAM Roles: {len(iam_data.get('roles', []))}")
        
        # Test storing in local database
        print("💾 Storing in local database...")
        db = ProTechtDatabase("test_protecht.db")
        db.load_aws_data(collected)
        
        # Check if data was stored
        print("🔍 Checking stored data...")
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM iam_users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Stored IAM users: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM iam_roles")
        role_count = cursor.fetchone()[0]
        print(f"📊 Stored IAM roles: {role_count}")
        
        if user_count > 0:
            cursor.execute("SELECT username, mfa_enabled FROM iam_users LIMIT 3")
            users = cursor.fetchall()
            print(f"📊 Sample users: {users}")
        
        conn.close()
        
        # Test loading data back
        print("🔄 Testing data loading...")
        loaded_data = db.load_aws_data_from_db()
        iam_loaded = loaded_data.get('iam', {})
        print(f"📊 Loaded IAM users: {len(iam_loaded.get('users', []))}")
        print(f"📊 Loaded IAM roles: {len(iam_loaded.get('roles', []))}")
        
        if iam_loaded.get('users'):
            print(f"📊 First loaded user: {iam_loaded['users'][0]}")
    else:
        print("❌ No IAM data collected")

if __name__ == "__main__":
    test_direct_storage()
