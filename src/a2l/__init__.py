"""A2L processing module for MBD_CICDKits.

This module provides pure Python implementation for A2L file processing,
including ELF file parsing and address updating.

Architecture Decision ADR-005:
- Removed MATLAB Engine dependency
- Uses pyelftools for ELF parsing
- Based on original MATLAB script logic

Modules:
    elf_parser: ELF file symbol extraction
    a2l_parser: A2L file structure parsing
    address_updater: A2L address update logic
"""

from a2l.elf_parser import ELFParser
from a2l.a2l_parser import A2LParser
from a2l.address_updater import A2LAddressUpdater

__all__ = [
    "ELFParser",
    "A2LParser",
    "A2LAddressUpdater",
]
