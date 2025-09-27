from __future__ import annotations

"""Caching system for LLM processing to reduce API calls and improve performance."""

import hashlib
import json
import sqlite3
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
try:
    from ..config import get_cache_database_path
except ImportError:
    # Fallback for direct execution
    def get_cache_database_path():
        return "llm_cache.db"


class LLMCache:
    """SQLite-based cache for LLM processing results."""
    
    def __init__(self, cache_db_path: str = None):
        self.cache_db_path = cache_db_path or get_cache_database_path()
        self._init_cache_db()
    
    def _init_cache_db(self):
        """Initialize the cache database with required tables."""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        # Create cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_cache (
                cache_key TEXT PRIMARY KEY,
                operation_type TEXT NOT NULL,
                input_hash TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_input_hash ON llm_cache(input_hash)
        ''')
        
        # Create index for cleanup
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expires_at ON llm_cache(expires_at)
        ''')
        
        conn.commit()
        conn.close()
    
    def _generate_cache_key(self, operation_type: str, input_text: str, **kwargs) -> str:
        """Generate a unique cache key for the operation."""
        # Create a hash of the input text and additional parameters
        input_data = {
            "text": input_text,
            **kwargs
        }
        input_str = json.dumps(input_data, sort_keys=True)
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()[:16]
        return f"{operation_type}_{input_hash}"
    
    def get(self, operation_type: str, input_text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached result for an operation."""
        cache_key = self._generate_cache_key(operation_type, input_text, **kwargs)
        
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT result, expires_at FROM llm_cache 
                WHERE cache_key = ? AND (expires_at IS NULL OR expires_at > ?)
            ''', (cache_key, time.time()))
            
            row = cursor.fetchone()
            if row:
                result, expires_at = row
                # Update access statistics
                cursor.execute('''
                    UPDATE llm_cache 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE cache_key = ?
                ''', (time.time(), cache_key))
                conn.commit()
                
                return json.loads(result)
            return None
        finally:
            conn.close()
    
    def set(self, operation_type: str, input_text: str, result: Dict[str, Any], 
            ttl_seconds: int = 3600, **kwargs) -> None:
        """Cache a result for an operation."""
        cache_key = self._generate_cache_key(operation_type, input_text, **kwargs)
        input_hash = hashlib.sha256(input_text.encode()).hexdigest()[:16]
        
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        try:
            expires_at = time.time() + ttl_seconds if ttl_seconds > 0 else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO llm_cache 
                (cache_key, operation_type, input_hash, result, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (cache_key, operation_type, input_hash, json.dumps(result), expires_at))
            
            conn.commit()
        finally:
            conn.close()
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries and return count of removed entries."""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM llm_cache WHERE expires_at < ?', (time.time(),))
            removed_count = cursor.rowcount
            conn.commit()
            return removed_count
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM llm_cache')
            total_entries = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM llm_cache WHERE expires_at > ?', (time.time(),))
            active_entries = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(access_count) FROM llm_cache')
            total_accesses = cursor.fetchone()[0] or 0
            
            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "total_accesses": total_accesses
            }
        finally:
            conn.close()


# Global cache instance
_cache = None

def get_cache() -> LLMCache:
    """Get the global cache instance."""
    global _cache
    if _cache is None:
        _cache = LLMCache()
    return _cache


def cache_llm_result(operation_type: str, ttl_seconds: int = 3600):
    """Decorator to cache LLM function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Extract input text from args (assuming first arg is text)
            input_text = args[0] if args else ""
            
            # Check cache first
            cached_result = cache.get(operation_type, input_text, **kwargs)
            if cached_result is not None:
                return cached_result
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache.set(operation_type, input_text, result, ttl_seconds, **kwargs)
            
            return result
        return wrapper
    return decorator
