from __future__ import annotations

"""Access Control (AC) family controls for policy analysis."""

# Focus on NON-TECHNICAL Access Control controls only (policy/document driven)
NON_TECHNICAL_AC_CONTROLS = [
    "AC-1",   # Access Control Policy & Procedures
    "AC-14",  # Permitted Actions without Identification or Authentication  
    "AC-20",  # Use of External Information Systems
    "AC-22"   # Publicly Accessible Content
]

# Mixed controls that need both technical + non-technical evidence
MIXED_AC_CONTROLS = [
    "AC-2",   # Account Management
    "AC-8",   # System Use Notification
    "AC-17",  # Remote Access
    "AC-18",  # Wireless Access Restrictions
    "AC-19"   # Portable & Mobile Systems
]

# All AC controls for LLM knowledge (but only analyze non-technical ones)
ALL_AC_CONTROLS = NON_TECHNICAL_AC_CONTROLS + MIXED_AC_CONTROLS

# Backward compatibility
ACCESS_CONTROL_CONTROLS = NON_TECHNICAL_AC_CONTROLS

# Keep backward compatibility
NON_TECHNICAL_CONTROLS = ACCESS_CONTROL_CONTROLS

NON_TECHNICAL_KEYWORDS = [
    # policy/process
    "policy", "policies", "procedure", "procedures", "roles", "responsibilities", "training",
    "reporting", "escalation", "review", "annually", "cadence", "governance", "program",
    "authorization", "artifacts", "bia", "vendor", "assessment", "records", "evidence",
    # access control specific
    "access control", "authentication", "authorization", "account", "user", "login", "password",
    "remote access", "wireless", "mobile", "external systems", "publicly accessible",
]

# NON-TECHNICAL AC controls checklists (policy/document driven only)
CHECKLISTS = {
    "AC-1": {
        "sections_required": ["Purpose", "Scope", "Roles", "Responsibilities", "Management Commitment", "Coordination", "Compliance", "Procedures", "Review Cadence"],
        "key_elements": ["access control policy", "procedures", "roles", "responsibilities", "management commitment", "coordination", "compliance", "review", "update"],
        "review_frequency": "policy: at least every 3 years, procedures: at least annually",
        "audit_focus": "Policy documents, procedure manuals, review records, training materials"
    },
    "AC-14": {
        "sections_required": ["Permitted Actions", "Identification Requirements", "Authentication Requirements", "Supporting Rationale"],
        "key_elements": ["permitted actions", "without identification", "without authentication", "organizational missions", "business functions", "security plan", "supporting rationale"],
        "audit_focus": "Policy documents defining what actions are allowed without authentication"
    },
    "AC-20": {
        "sections_required": ["Terms and Conditions", "Trust Relationships", "External System Access", "Information Processing"],
        "key_elements": ["external information systems", "terms and conditions", "trust relationships", "authorized individuals", "access from external systems", "process information", "store information", "transmit information"],
        "audit_focus": "Agreements, terms of service, trust relationship documentation"
    },
    "AC-22": {
        "sections_required": ["Authorized Personnel", "Training Requirements", "Content Review", "Regular Reviews"],
        "key_elements": ["publicly accessible content", "authorized individuals", "training", "nonpublic information", "content review", "quarterly review", "remove nonpublic information"],
        "audit_focus": "Training records, content review procedures, personnel authorization lists"
    },
}
