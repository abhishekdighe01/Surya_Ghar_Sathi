# ==============================================================================
# File: app/security.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 13 - Enterprise Security Guardrails, Prompt Injection Defense,
#              and Indian PII (Aadhaar/PAN/Phone) Redaction Engine.
# ==============================================================================

import re
from dataclasses import dataclass, field


@dataclass
class SecurityReport:
    """Detailed audit report for input sanitization and threat detection."""
    is_safe: bool
    sanitized_text: str
    violation: str | None = None
    redactions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "is_safe": self.is_safe,
            "sanitized_text": self.sanitized_text,
            "violation": self.violation,
            "redactions": self.redactions,
        }


class SecurityGuard:
    """
    Production security engine providing multi-layer defense against:
    1. Prompt Injection & Jailbreak patterns.
    2. System instruction exfiltration / developer mode bypass.
    3. Indian Personally Identifiable Information (PII) leakage: Aadhaar, PAN, Phone, Email.
    """

    # Signatures for known prompt injection / jailbreak vectors
    INJECTION_PATTERNS = [
        r"(?i)\bignore\b.*?\b(instructions|directions|rules|prompts)\b",
        r"(?i)\bdisregard\b.*?\b(instructions|directions|rules|prompts)\b",
        r"(?i)\b(system override|developer mode|dan mode|unrestricted mode)\b",
        r"(?i)\byou are now (in|unlocked|a new|unrestricted)\b",
        r"(?i)\bpretend (to be|you are)\b",
        r"(?i)\b(print|reveal|output|display|show|leak)\b.*?\b(system prompt|developer instructions|hidden prompt)\b",
        r"(?i)\bact as (dan|an evil|a bypass|unrestricted)\b",
        r"(?i)\bfrom now on you (must|will) obey\b",
        r"(?i)<\s*script[^>]*>.*?<\s*/\s*script\s*>",  # XSS
        r"(?i)\b(drop\s+table|insert\s+into|delete\s+from|union\s+select)\b",  # SQLi
    ]

    # Regex patterns for Indian PII detection and redaction
    # Aadhaar: 12 digits often formatted as XXXX XXXX XXXX or XXXX-XXXX-XXXX
    AADHAAR_REGEX = re.compile(r"\b([2-9]\d{3}[-\s]?\d{4}[-\s]?\d{4})\b")
    # PAN: 5 uppercase letters, 4 digits, 1 uppercase letter (e.g. ABCDE1234F)
    PAN_REGEX = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b", re.IGNORECASE)
    # Indian mobile: 10 digits starting with 6-9, optional +91 prefix
    PHONE_REGEX = re.compile(r"(\+91[\-\s]?)?([6-9]\d{9})\b")
    # Standard email
    EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    def __init__(self):
        self._compiled_injections = [re.compile(p) for p in self.INJECTION_PATTERNS]

    def detect_prompt_injection(self, text: str) -> tuple[bool, str | None]:
        """
        Scan input text for adversarial prompt injection signatures.
        Returns: (is_threat: bool, threat_description: str | None)
        """
        for pattern in self._compiled_injections:
            match = pattern.search(text)
            if match:
                threat_detected = match.group(0)
                return True, f"Adversarial instruction detected: '{threat_detected}'"
        return False, None

    def redact_pii(self, text: str) -> tuple[str, list[str]]:
        """
        Detect and redact sensitive personal information before ingestion or LLM invocation.
        Returns: (redacted_text: str, list_of_redactions: list[str])
        """
        redactions = []
        sanitized = text

        # 1. Redact Aadhaar
        if self.AADHAAR_REGEX.search(sanitized):
            sanitized = self.AADHAAR_REGEX.sub("[AADHAAR_REDACTED]", sanitized)
            redactions.append("AADHAAR_NUMBER")

        # 2. Redact PAN Card
        if self.PAN_REGEX.search(sanitized):
            sanitized = self.PAN_REGEX.sub("[PAN_REDACTED]", sanitized)
            redactions.append("PAN_NUMBER")

        # 3. Redact Indian Phone Numbers
        if self.PHONE_REGEX.search(sanitized):
            sanitized = self.PHONE_REGEX.sub("[PHONE_REDACTED]", sanitized)
            redactions.append("PHONE_NUMBER")

        # 4. Redact Email Addresses
        if self.EMAIL_REGEX.search(sanitized):
            sanitized = self.EMAIL_REGEX.sub("[EMAIL_REDACTED]", sanitized)
            redactions.append("EMAIL_ADDRESS")

        return sanitized, redactions

    def validate_and_sanitize(self, text: str) -> SecurityReport:
        """
        Full security pipeline: validation, injection detection, and PII masking.
        """
        if not text or len(text.strip()) < 2:
            return SecurityReport(
                is_safe=False,
                sanitized_text="",
                violation="Input text is too short (minimum 2 characters required)."
            )

        if len(text) > 1500:
            return SecurityReport(
                is_safe=False,
                sanitized_text=text[:1500],
                violation="Input exceeds maximum permissible length (1500 characters)."
            )

        # Check for adversarial injection
        is_threat, threat_msg = self.detect_prompt_injection(text)
        if is_threat:
            return SecurityReport(
                is_safe=False,
                sanitized_text=text,
                violation=f"Security Policy Violation: {threat_msg}"
            )

        # Redact PII
        sanitized_text, redactions = self.redact_pii(text)

        return SecurityReport(
            is_safe=True,
            sanitized_text=sanitized_text,
            violation=None,
            redactions=redactions
        )


# Singleton instance
security_guard = SecurityGuard()
