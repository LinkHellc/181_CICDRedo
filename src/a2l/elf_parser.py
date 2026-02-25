"""ELF file parser for extracting symbol addresses.

This module provides functionality to parse ELF files and extract
symbol names and their addresses using pyelftools.

Story 2.9 - Task 2: Implement ELF file parsing
Architecture Decision ADR-005: Pure Python implementation

Usage:
    parser = ELFParser()
    symbols = parser.extract_symbols("firmware.elf")
    # Returns: {"symbol_name": 0x12345678, ...}
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)


class ELFParseError(Exception):
    """ELF 解析错误

    当 ELF 文件无法解析时抛出。
    """
    pass


class ELFParser:
    """ELF 文件解析器

    使用 pyelftools 从 ELF 文件中提取符号名称和地址。

    Story 2.9 - 任务 2.1-2.6:
    - 使用 pyelftools 打开 ELF 文件
    - 提取符号表（.symtab section）
    - 提取符号名称和地址映射
    - 过滤出 A2L 需要的变量符号

    Attributes:
        elf_path: ELF 文件路径
        symbols: 符号名称到地址的映射
    """

    # 需要过滤的符号前缀（通常不是用户变量）
    FILTERED_PREFIXES = (
        '__',           # 编译器内部符号
        '_Z',           # C++ mangled names
        '.LC',          # 字符串常量
        '._',           # LLVM 内部符号
    )

    # 需要过滤的符号后缀
    FILTERED_SUFFIXES = (
        '_init',
        '_fini',
    )

    def __init__(self, elf_path: Optional[Path] = None):
        """初始化 ELF 解析器

        Args:
            elf_path: 可选的 ELF 文件路径
        """
        self.elf_path = elf_path
        self._symbols: Dict[str, int] = {}
        self._filtered_count = 0

    @property
    def symbols(self) -> Dict[str, int]:
        """获取已解析的符号字典

        Returns:
            Dict[str, int]: 符号名称到地址的映射
        """
        return self._symbols

    def extract_symbols(self, elf_path: Path) -> Dict[str, int]:
        """从 ELF 文件提取符号地址

        Story 2.9 - 任务 2.2-2.6:
        - 使用 pyelftools 打开 ELF 文件
        - 提取符号表
        - 返回符号地址字典

        Args:
            elf_path: ELF 文件路径

        Returns:
            Dict[str, int]: 符号名称到地址的映射

        Raises:
            ELFParseError: 如果 ELF 文件无法解析
            FileNotFoundError: 如果文件不存在
        """
        self.elf_path = Path(elf_path)
        self._symbols = {}
        self._filtered_count = 0

        # 验证文件存在
        if not self.elf_path.exists():
            raise FileNotFoundError(f"ELF 文件不存在: {self.elf_path}")

        # 验证文件大小
        if self.elf_path.stat().st_size == 0:
            raise ELFParseError(f"ELF 文件大小为 0: {self.elf_path}")

        logger.info(f"开始解析 ELF 文件: {self.elf_path}")

        try:
            from elftools.elf.elffile import ELFFile
        except ImportError:
            raise ELFParseError(
                "pyelftools 未安装。请运行: pip install pyelftools"
            )

        try:
            with open(self.elf_path, 'rb') as f:
                # 验证 ELF 魔数
                magic = f.read(4)
                if magic != b'\x7fELF':
                    raise ELFParseError(f"不是有效的 ELF 文件: {self.elf_path}")
                f.seek(0)

                elf = ELFFile(f)

                # 获取符号表 section
                symtab = elf.get_section_by_name('.symtab')
                if symtab is None:
                    logger.warning("ELF 文件中没有 .symtab section")
                    return self._symbols

                # 提取符号
                symbol_count = 0
                for symbol in symtab.iter_symbols():
                    name = symbol.name
                    addr = symbol['st_value']

                    # 过滤无效符号
                    if not name or addr == 0:
                        continue

                    # 应用过滤器
                    if self._should_filter_symbol(name):
                        self._filtered_count += 1
                        continue

                    self._symbols[name] = addr
                    symbol_count += 1

                logger.info(
                    f"ELF 解析完成: 提取 {symbol_count} 个符号, "
                    f"过滤 {self._filtered_count} 个符号"
                )

        except Exception as e:
            if isinstance(e, (ELFParseError, FileNotFoundError)):
                raise
            raise ELFParseError(f"解析 ELF 文件失败: {e}") from e

        return self._symbols

    def _should_filter_symbol(self, name: str) -> bool:
        """判断符号是否应该被过滤

        Args:
            name: 符号名称

        Returns:
            bool: 如果应该过滤返回 True
        """
        # 检查前缀
        for prefix in self.FILTERED_PREFIXES:
            if name.startswith(prefix):
                return True

        # 检查后缀
        for suffix in self.FILTERED_SUFFIXES:
            if name.endswith(suffix):
                return True

        return False

    def get_address(self, symbol_name: str) -> Optional[int]:
        """获取指定符号的地址

        Args:
            symbol_name: 符号名称

        Returns:
            Optional[int]: 符号地址，如果不存在返回 None
        """
        return self._symbols.get(symbol_name)

    def find_symbols_by_prefix(self, prefix: str) -> Dict[str, int]:
        """按前缀查找符号

        Args:
            prefix: 符号名称前缀

        Returns:
            Dict[str, int]: 匹配的符号字典
        """
        return {
            name: addr
            for name, addr in self._symbols.items()
            if name.startswith(prefix)
        }

    def get_symbol_count(self) -> int:
        """获取符号数量

        Returns:
            int: 已解析的符号数量
        """
        return len(self._symbols)

    def get_filtered_count(self) -> int:
        """获取被过滤的符号数量

        Returns:
            int: 被过滤的符号数量
        """
        return self._filtered_count
