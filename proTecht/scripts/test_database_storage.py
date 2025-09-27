#!/usr/bin/env python3
"""
Test database storage to see if data is being stored correctly
"""

import sys
import os
import sqlite3

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import ProTechtDatabase

def test_database_storage():
    """Test what's actually stored in the database"""
    
    print("🔍 Testing database storage...")
    
    # Create a local database instance
    db = ProTechtDatabase("test_protecht.db")
    
    # Check if tables exist
    conn = sqlite3.connect("test_protecht.db")
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"📊 Database tables: {[table[0] for table in tables]}")
    
    # Check IAM tables specifically
    iam_tables = ['iam_users', 'iam_roles', 'iam_password_policy']
    
    for table in iam_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"📊 {table}: {count} records")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                print(f"   Sample data: {rows}")
                
        except Exception as e:
            print(f"❌ Error checking {table}: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_database_storage()
