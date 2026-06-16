"""
Job ID generation utilities.

Provides UUID v4 based job identifiers for all processing jobs.
UUID v4 is used deliberately:
- Cryptographically random → not guessable / enumerable.
- No sequential pattern → safe to expose in API responses.
- Globally unique → safe for future distributed / cloud deployments.
"""

from __future__ import annotations

import uuid


def generate_job_id() -> str:
    """
    Generate a new unique job identifier as a hyphenated UUID v4 string.

    Returns:
        A UUID v4 string, e.g. "550e8400-e29b-41d4-a716-446655440000".

    Examples:
        >>> job_id = generate_job_id()
        >>> len(job_id)
        36
        >>> job_id.count('-')
        4
    """
    return str(uuid.uuid4())


def generate_job_uuid() -> uuid.UUID:
    """
    Generate a new unique job identifier as a Python UUID object.

    Use this variant when you need UUID type compatibility with
    Pydantic models that declare fields as ``UUID``.

    Returns:
        A ``uuid.UUID`` v4 instance.
    """
    return uuid.uuid4()
