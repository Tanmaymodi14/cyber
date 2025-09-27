from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Section:
    section_id: str
    title: str
    text: str
    label: str = "unknown"  # technical | non-technical | mixed | unknown
    confidence: float = 0.0


@dataclass
class ValidationResult:
    control_id: str
    status: str  # pass | partial | fail
    confidence: float
    reasons: List[str] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)
    policy_citations: List[str] = field(default_factory=list)
    template_citations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    sections_covered: List[str] = field(default_factory=list)


@dataclass
class PolicyReport:
    policy_name: str
    controls: List[ValidationResult]  # Now will contain exactly 1 control
    summary: Dict[str, Any]


