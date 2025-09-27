#!/usr/bin/env python3
"""
Centralized configuration for proTecht
"""

import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# On AWS Lambda, the filesystem is read-only except /tmp. Use /tmp for SQLite files.
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("AWS_EXECUTION_ENV"):
    DATABASE_PATH = Path("/tmp/protecht.db")
    CACHE_DATABASE_PATH = Path("/tmp/llm_cache.db")
else:
    DATABASE_PATH = PROJECT_ROOT / "protecht.db"
    CACHE_DATABASE_PATH = PROJECT_ROOT / "llm_cache.db"

# Ensure database paths are absolute strings
DATABASE_PATH = str(Path(DATABASE_PATH).absolute())
CACHE_DATABASE_PATH = str(Path(CACHE_DATABASE_PATH).absolute())

# API Configuration
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8000"))

# Frontend Configuration
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")

# AWS Configuration
AWS_PROFILE = os.environ.get("AWS_PROFILE")
AWS_REGIONS = os.environ.get("AWS_REGIONS", "us-east-1,us-west-2").split(",")

# Logging Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

def get_database_path():
    """Get the unified database path"""
    return DATABASE_PATH

def get_cache_database_path():
    """Get the cache database path"""
    return CACHE_DATABASE_PATH
