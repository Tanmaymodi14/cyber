"""Access Control (AC) policy analysis package - single AC control identification and validation.

Default export now uses database-powered analyzer (no OpenAI File Search).
"""

# Avoid importing heavy dependencies at module import time (Lambda cold start)
def analyze_access_control_policy(*args, **kwargs):  # type: ignore
    from .analyzer import analyze_access_control_policy as _impl
    return _impl(*args, **kwargs)

from .models import PolicyReport, ValidationResult  # lightweight

__all__ = ["analyze_access_control_policy", "PolicyReport", "ValidationResult"]

# Backward compatibility alias (resolved lazily)
def analyze_non_technical_policy(*args, **kwargs):  # type: ignore
    return analyze_access_control_policy(*args, **kwargs)

