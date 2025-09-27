"""Access Control (AC) policy analysis package - single AC control identification and validation.

Default export now uses database-powered analyzer (no OpenAI File Search).
"""

from .analyzer import analyze_access_control_policy
from .models import PolicyReport, ValidationResult

__all__ = ["analyze_access_control_policy", "PolicyReport", "ValidationResult"]

# Backward compatibility alias
analyze_non_technical_policy = analyze_access_control_policy

