#!/usr/bin/env python3
"""
Headless proTecht - Database and FedRAMP baseline management only
No Flask/UI - use analyze_technical.py for technical evaluation
"""

import os
import sys
from typing import Dict, Any

# FedRAMP baseline info (simplified for headless system)
    FEDRAMP_AVAILABLE = True

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

# Import database
from database import ProTechtDatabase

# Import AI policy analysis module
try:
    from policy import analyze_access_control_policy
    print("AI policy analysis module loaded successfully")
except ImportError as e:
    print(f"Warning: AI policy analysis module not available: {e}")

def initialize_system() -> bool:
    """Initialize the headless proTecht system - database only"""
    try:
        print("🚀 Initializing headless compliance system...")
        
        # Initialize database
    db = ProTechtDatabase()
    print("Database connection established")
        
        print("✅ Headless proTecht system ready")
        print("📊 FedRAMP Low baseline: 177 controls (AC family: 22 controls)")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return False

def get_aws_data() -> Dict[str, Any]:
    """Get AWS data from database"""
    db = ProTechtDatabase()
    return db.get_aws_data()

def main():
    """Main entry point for headless system"""
    if initialize_system():
        print("System ready. Use analyze_technical.py for technical evaluation.")
        print("Use analyze_policy.py for policy analysis.")
        else:
        print("System initialization failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
