from __future__ import annotations

"""LLM utilities for robust AI-powered policy analysis."""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore
from .cache import cache_llm_result


def get_openai_client() -> Optional[OpenAI]:
    """Get OpenAI client if API key is available."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        print("Warning: OPENAI_API_KEY not set. LLM features will be limited.")
        return None
    return OpenAI(api_key=api_key)


def extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Try to find JSON in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find raw JSON
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    return None


@cache_llm_result("document_splitting", ttl_seconds=7200)  # Cache for 2 hours
def split_document_intelligently(text: str) -> List[Tuple[str, str, str]]:
    """Split document into logical sections using LLM.
    
    Returns: List of (section_id, title, content) tuples
    
    Raises:
        ValueError: If LLM client is unavailable or splitting fails
    """
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI client is not available. Please check your API key and configuration.")
    
    # Use a simple model for document splitting
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": """You are a document analysis expert. Split the given policy document into logical sections.
                
Return a JSON array where each element has:
- section_id: unique ID (s1, s2, etc.)
- title: descriptive section title
- content: the actual text content

Focus on major policy sections like Purpose, Scope, Roles, Procedures, etc.
If the document is short or doesn't have clear sections, return it as a single section."""
            }, {
                "role": "user", 
                "content": f"Please split this policy document into logical sections:\n\n{text[:2000]}"  # Reduced input size
            }],
            max_tokens=1000,  # Reduced token limit
            temperature=0.1
        )
        
        result = extract_json_from_response(response.choices[0].message.content)
        if result and isinstance(result, list):
            return [(item["section_id"], item["title"], item["content"]) 
                   for item in result if all(k in item for k in ["section_id", "title", "content"])]
                   
    except Exception as e:
        raise ValueError(f"Error in LLM document splitting: {e}")
    
    # If we get here, return single section as last resort
    return [("s1", "Full Document", text)]
