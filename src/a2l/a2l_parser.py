"""A2L file parser for extracting variable information.

This module provides functionality to parse A2L (ASAM MCD-2 MC) files
and extract variable names and addresses.

Story 2.9 - Task 3: Implement A2L file parsing
Architecture Decision ADR-005: Pure Python implementation

A2L File Structure (relevant parts):
    /begin CHARACTERISTIC
        name "VariableName"
        ...
        address 0x12345678
        ...
    /end CHARACTERISTIC

    /begin MEASUREMENT
        name "MeasurementName"
        ...
        address 0x87654321
        ...
    /end MEASUREMENT
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Generator

logger = logging.getLogger(__name__)


class A2LParseError(Exception):
    """A2L 解析错误

    当 A2L 文件无法解析时抛出。
    """
    pass


@dataclass
class A2LVariable:
    """A2L 变量信息

    表示 A2L 文件中的单个变量（CHARACTERISTIC 或 MEASUREMENT）。

    Attributes:
        name: 变量名称
        var_type: 变量类型（CHARACTERISTIC 或 MEASUREMENT）
        address: 当前地址值
        address_str: 地址字符串（原始格式）
        line_start: 块开始行号
        line_end: 块结束行号
        address_line: 地址所在行号
    """
    name: str = ""
    var_type: str = ""  # CHARACTERISTIC 或 MEASUREMENT
    address: int = 0
    address_str: str = ""
    line_start: int = 0
    line_end: int = 0
    address_line: int = 0


class A2LParser:
    """A2L 文件解析器

    解析 A2L 文件，提取变量名称和地址信息。

    Story 2.9 - 任务 3.1-3.5:
    - 解析 A2L 文件基本结构
    - 提取 CHARACTERISTIC 和 MEASUREMENT 块
    - 识别变量名称和当前地址
    - 支持大文件流式解析

    Attributes:
        a2l_path: A2L 文件路径
        variables: 变量名称到 A2LVariable 的映射
    """

    # 正则表达式模式
    # 匹配 /begin CHARACTERISTIC 或 /begin MEASUREMENT（标准格式：带变量名）
    BLOCK_START_PATTERN = re.compile(
        r'/begin\s+(CHARACTERISTIC|MEASUREMENT)\s+(\S+)',
        re.IGNORECASE
    )

    # 匹配 /begin CHARACTERISTIC 或 /begin MEASUREMENT（Simulink 格式：不带变量名）
    BLOCK_START_PATTERN_SIMULINK = re.compile(
        r'/begin\s+(CHARACTERISTIC|MEASUREMENT)\s*$',
        re.IGNORECASE
    )

    # 匹配 /end CHARACTERISTIC 或 /end MEASUREMENT
    BLOCK_END_PATTERN = re.compile(
        r'/end\s+(CHARACTERISTIC|MEASUREMENT)',
        re.IGNORECASE
    )

    # 匹配地址行（标准格式）
    ADDRESS_PATTERN = re.compile(
        r'^\s*address\s+(0x[0-9A-Fa-f]+|\d+)\s*$',
        re.IGNORECASE | re.MULTILINE
    )

    # 匹配 Simulink 格式的名称行：/* Name */ VarName
    NAME_PATTERN_SIMULINK = re.compile(
        r'/\*\s*Name\s*\*/\s*(\S+)',
        re.IGNORECASE
    )

    # 匹配 Simulink 格式的地址行：/* ECU Address */ 0x...
    ADDRESS_PATTERN_SIMULINK = re.compile(
        r'/\*\s*ECU\s+Address\s*\*/\s*(0x[0-9A-Fa-f]+|\d+)',
        re.IGNORECASE
    )

    def __init__(self, a2l_path: Optional[Path] = None):
        """初始化 A2L 解析器

        Args:
            a2l_path: 可选的 A2L 文件路径
        """
        self.a2l_path = a2l_path
        self._variables: Dict[str, A2LVariable] = {}
        self._lines: List[str] = []

    @property
    def variables(self) -> Dict[str, A2LVariable]:
        """获取已解析的变量字典

        Returns:
            Dict[str, A2LVariable]: 变量名称到 A2LVariable 的映射
        """
        return self._variables

    def parse(self, a2l_path: Path) -> Dict[str, A2LVariable]:
        """解析 A2L 文件

        Story 2.9 - 任务 3.2-3.5:
        - 读取 A2L 文件内容
        - 提取变量名和当前地址

        Args:
            a2l_path: A2L 文件路径

        Returns:
            Dict[str, A2LVariable]: 变量名称到 A2LVariable 的映射

        Raises:
            A2LParseError: 如果 A2L 文件无法解析
            FileNotFoundError: 如果文件不存在
        """
        self.a2l_path = Path(a2l_path)
        self._variables = {}
        self._lines = []

        # 验证文件存在
        if not self.a2l_path.exists():
            raise FileNotFoundError(f"A2L 文件不存在: {self.a2l_path}")

        # 验证文件大小
        file_size = self.a2l_path.stat().st_size
        if file_size == 0:
            raise A2LParseError(f"A2L 文件大小为 0: {self.a2l_path}")

        logger.info(f"开始解析 A2L 文件: {self.a2l_path} ({file_size} bytes)")

        try:
            # 读取文件内容（尝试多种编码）
            content = self._read_file_with_encoding(self.a2l_path)
            self._lines = content.splitlines()

            # 解析变量块
            self._parse_blocks()

            logger.info(f"A2L 解析完成: 提取 {len(self._variables)} 个变量")

        except Exception as e:
            if isinstance(e, (A2LParseError, FileNotFoundError)):
                raise
            raise A2LParseError(f"解析 A2L 文件失败: {e}") from e

        return self._variables

    def _read_file_with_encoding(self, path: Path) -> str:
        """尝试多种编码读取文件

        Args:
            path: 文件路径

        Returns:
            str: 文件内容
        """
        encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']

        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        # 如果所有编码都失败，使用二进制模式并忽略错误
        with open(path, 'rb') as f:
            return f.read().decode('utf-8', errors='ignore')

    def _parse_blocks(self):
        """解析 CHARACTERISTIC 和 MEASUREMENT 块

        支持两种格式：
        1. 标准格式：/begin CHARACTERISTIC VarName ... address 0x...
        2. Simulink 格式：/begin CHARACTERISTIC ... /* Name */ VarName ... /* ECU Address */ 0x...
        """
        current_block: Optional[A2LVariable] = None
        block_depth = 0

        for line_num, line in enumerate(self._lines, start=1):
            # 检查块开始（标准格式：带变量名）
            start_match = self.BLOCK_START_PATTERN.search(line)
            if start_match:
                var_type = start_match.group(1).upper()
                var_name = start_match.group(2)

                if block_depth == 0:
                    # 顶层块开始
                    current_block = A2LVariable(
                        name=var_name,
                        var_type=var_type,
                        line_start=line_num
                    )
                block_depth += 1
                continue

            # 检查块开始（Simulink 格式：不带变量名）
            start_match_simulink = self.BLOCK_START_PATTERN_SIMULINK.search(line)
            if start_match_simulink:
                var_type = start_match_simulink.group(1).upper()

                if block_depth == 0:
                    # 顶层块开始，变量名稍后从 /* Name */ 行获取
                    current_block = A2LVariable(
                        name="",  # 稍后填充
                        var_type=var_type,
                        line_start=line_num
                    )
                block_depth += 1
                continue

            # 检查块结束
            end_match = self.BLOCK_END_PATTERN.search(line)
            if end_match:
                block_depth -= 1
                if block_depth == 0 and current_block:
                    # 顶层块结束
                    current_block.line_end = line_num
                    # 只有当变量名存在时才添加
                    if current_block.name:
                        self._variables[current_block.name] = current_block
                    current_block = None
                continue

            # 在块内部查找信息
            if current_block and block_depth == 1:
                # 查找名称（Simulink 格式）
                if not current_block.name:
                    name_match = self.NAME_PATTERN_SIMULINK.search(line)
                    if name_match:
                        current_block.name = name_match.group(1)

                # 查找地址（标准格式）
                addr_match = self.ADDRESS_PATTERN.match(line)
                if addr_match:
                    addr_str = addr_match.group(1)
                    current_block.address_str = addr_str
                    current_block.address_line = line_num

                    # 解析地址值
                    if addr_str.lower().startswith('0x'):
                        current_block.address = int(addr_str, 16)
                    else:
                        current_block.address = int(addr_str)
                    continue

                # 查找地址（Simulink 格式）
                addr_match_simulink = self.ADDRESS_PATTERN_SIMULINK.search(line)
                if addr_match_simulink:
                    addr_str = addr_match_simulink.group(1)
                    current_block.address_str = addr_str
                    current_block.address_line = line_num

                    # 解析地址值
                    if addr_str.lower().startswith('0x'):
                        current_block.address = int(addr_str, 16)
                    else:
                        current_block.address = int(addr_str)

    def get_variable(self, name: str) -> Optional[A2LVariable]:
        """获取指定变量信息

        Args:
            name: 变量名称

        Returns:
            Optional[A2LVariable]: 变量信息，如果不存在返回 None
        """
        return self._variables.get(name)

    def get_address(self, name: str) -> Optional[int]:
        """获取指定变量的地址

        Args:
            name: 变量名称

        Returns:
            Optional[int]: 变量地址，如果不存在返回 None
        """
        var = self._variables.get(name)
        return var.address if var else None

    def get_variable_count(self) -> int:
        """获取变量数量

        Returns:
            int: 已解析的变量数量
        """
        return len(self._variables)

    def get_lines(self) -> List[str]:
        """获取文件所有行

        Returns:
            List[str]: 文件行列表
        """
        return self._lines

    def get_characteristic_count(self) -> int:
        """获取 CHARACTERISTIC 数量

        Returns:
            int: CHARACTERISTIC 数量
        """
        return sum(1 for v in self._variables.values() if v.var_type == "CHARACTERISTIC")

    def get_measurement_count(self) -> int:
        """获取 MEASUREMENT 数量

        Returns:
            int: MEASUREMENT 数量
        """
        return sum(1 for v in self._variables.values() if v.var_type == "MEASUREMENT")
