"""Integrations package for MBD_CICDKits.

This module provides integration with external tools such as MATLAB and IAR.
"""

from .matlab import MatlabIntegration

__all__ = ["MatlabIntegration"]
