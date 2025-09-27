from __future__ import annotations

"""LLM-powered technical vs non-technical router."""

from typing import Tuple
import json

from .llm_utils import get_openai_client, extract_json_from_response
from .cache import cache_llm_result


@cache_llm_result("section_classification", ttl_seconds=3600)  # Cache for 1 hour
def classify_section(text: str) -> Tuple[str, float]:
    """Classify section as technical, non-technical, or mixed using LLM.
    
    Returns: (label, confidence) where label is one of:
    - "technical": Focuses on system configs, code, infrastructure
    - "non-technical": Focuses on policies, procedures, training, governance
    - "mixed": Contains both technical and non-technical elements
    
    Raises:
        ValueError: If LLM client is unavailable
    """
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI client is not available. Please check your API key and configuration.")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": """You are a cybersecurity compliance expert. Analyze the given policy text and classify it as:

1. "technical" - Focuses on system configurations, technical implementations, code, infrastructure, specific technologies (AWS services, encryption algorithms, etc.)
2. "non-technical" - Focuses on organizational policies, procedures, training, governance, roles/responsibilities, business processes
3. "mixed" - Contains significant elements of both technical and non-technical content

Return JSON with:
{
  "classification": "technical|non-technical|mixed",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of why this classification was chosen"
}

Be precise - even if technical terms are mentioned, if the focus is on policy/procedure, classify as non-technical.
Be confident in your assessment."""
            }, {
                "role": "user",
                "content": f"Classify this policy section:\n\n{text[:1000]}"  # Further reduced input size
            }],
            max_tokens=200,  # Reduced token limit
            temperature=0.1
        )
        
        result = extract_json_from_response(response.choices[0].message.content)
        if result and "classification" in result and "confidence" in result:
            label = result["classification"]
            confidence = float(result["confidence"])
            if label in ["technical", "non-technical", "mixed"]:
                return (label, min(max(confidence, 0.0), 1.0))
        
        # If we get here, the LLM response was invalid
        raise ValueError("LLM returned invalid response for classification")
                
    except Exception as e:
        raise ValueError(f"Error in LLM classification: {e}")




