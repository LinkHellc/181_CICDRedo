"""Workflow stages module for MBD_CICDKits.

This module implements the workflow execution stages following
Architecture Decision 1.1 (Stage Interface Pattern) and Decision 2.1 (Process Management).
"""

from stages.base import StageBase, execute_stage

__all__ = [
    "StageBase",
    "execute_stage",
]
