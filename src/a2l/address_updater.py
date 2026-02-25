"""A2L address updater for synchronizing ELF symbol addresses.

This module provides functionality to update A2L file variable addresses
based on ELF file symbol table.

Story 2.9 - Task 4: Implement address update logic
Architecture Decision ADR-005: Pure Python implementation

Equivalent to MATLAB: rtw.asap2SetAddress('TmsApp.a2l', 'CYT4BF_M7_Master.elf')
"""

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable

from a2l.elf_parser import ELFParser, ELFParseError
from a2l.a2l_parser import A2LParser, A2LParseError, A2LVariable

logger = logging.getLogger(__name__)


class AddressUpdateError(Exception):
    """地址更新错误

    当地址更新失败时抛出。
    """
    pass


@dataclass
class AddressUpdateResult:
    """地址更新结果

    表示地址更新操作的完整结果。

    Attributes:
        success: 是否成功
        message: 结果消息
        matched_count: 匹配并更新的变量数量
        unmatched_count: 未匹配的变量数量
        total_variables: A2L 中的总变量数
        total_symbols: ELF 中的总符号数
        updated_variables: 更新的变量列表
        unmatched_variables: 未匹配的变量列表
        output_path: 更新后的 A2L 文件路径
    """
    success: bool = False
    message: str = ""
    matched_count: int = 0
    unmatched_count: int = 0
    total_variables: int = 0
    total_symbols: int = 0
    updated_variables: List[str] = field(default_factory=list)
    unmatched_variables: List[str] = field(default_factory=list)
    output_path: str = ""


class A2LAddressUpdater:
    """A2L 地址更新器

    将 ELF 文件中的符号地址更新到 A2L 文件中。

    Story 2.9 - 任务 4.1-4.6:
    - 加载 ELF 符号表
    - 匹配 A2L 变量名与 ELF 符号名
    - 更新 A2L 文件中的地址值
    - 处理未匹配的变量
    - 保存更新后的 A2L 文件

    Equivalent to MATLAB: rtw.asap2SetAddress(a2l_file, elf_file)

    Usage:
        updater = A2LAddressUpdater()
        result = updater.update("firmware.elf", "config.a2l")
        if result.success:
            print(f"Updated {result.matched_count} variables")
    """

    def __init__(self):
        """初始化地址更新器"""
        self._elf_parser = ELFParser()
        self._a2l_parser = A2LParser()
        self._log_callback: Optional[Callable[[str], None]] = None

    def set_log_callback(self, callback: Callable[[str], None]):
        """设置日志回调函数

        Args:
            callback: 日志回调函数
        """
        self._log_callback = callback

    def _log(self, message: str):
        """记录日志

        Args:
            message: 日志消息
        """
        logger.info(message)
        if self._log_callback:
            self._log_callback(message)

    def update(
        self,
        elf_path: Path,
        a2l_path: Path,
        output_path: Optional[Path] = None,
        backup: bool = True
    ) -> AddressUpdateResult:
        """更新 A2L 文件中的变量地址

        这是主入口函数，等效于 MATLAB 的 rtw.asap2SetAddress。

        Story 2.9 - 任务 4.1-4.6:
        - 加载 ELF 符号表
        - 解析 A2L 文件
        - 匹配并更新地址
        - 保存更新后的文件

        Args:
            elf_path: ELF 文件路径
            a2l_path: A2L 文件路径
            output_path: 输出文件路径（可选，默认覆盖原文件）
            backup: 是否备份原文件

        Returns:
            AddressUpdateResult: 更新结果
        """
        elf_path = Path(elf_path)
        a2l_path = Path(a2l_path)
        output_path = Path(output_path) if output_path else a2l_path

        self._log(f"开始 A2L 地址更新: ELF={elf_path.name}, A2L={a2l_path.name}")

        result = AddressUpdateResult()

        try:
            # 步骤 1: 解析 ELF 文件 (任务 4.2)
            self._log(f"解析 ELF 文件: {elf_path}")
            elf_symbols = self._elf_parser.extract_symbols(elf_path)
            result.total_symbols = len(elf_symbols)
            self._log(f"ELF 符号数量: {result.total_symbols}")

            # 步骤 2: 解析 A2L 文件 (任务 4.3)
            self._log(f"解析 A2L 文件: {a2l_path}")
            a2l_variables = self._a2l_parser.parse(a2l_path)
            result.total_variables = len(a2l_variables)
            self._log(f"A2L 变量数量: {result.total_variables}")

            # 步骤 3: 备份原文件 (任务 4.6)
            if backup and output_path == a2l_path:
                backup_path = a2l_path.with_suffix('.a2l.bak')
                shutil.copy2(a2l_path, backup_path)
                self._log(f"已备份原文件: {backup_path}")

            # 步骤 4: 匹配和更新地址 (任务 4.4)
            lines = self._a2l_parser.get_lines()
            updated_lines = lines.copy()

            for var_name, var_info in a2l_variables.items():
                if var_name in elf_symbols:
                    new_addr = elf_symbols[var_name]
                    old_addr = var_info.address

                    # 更新地址行
                    if var_info.address_line > 0:
                        old_line = lines[var_info.address_line - 1]
                        new_line = old_line.replace(
                            var_info.address_str,
                            f"0x{new_addr:08X}"
                        )
                        updated_lines[var_info.address_line - 1] = new_line

                        result.matched_count += 1
                        result.updated_variables.append(var_name)

                        logger.debug(
                            f"更新变量 {var_name}: "
                            f"0x{old_addr:08X} -> 0x{new_addr:08X}"
                        )
                else:
                    result.unmatched_count += 1
                    result.unmatched_variables.append(var_name)
                    logger.debug(f"未匹配变量: {var_name}")

            # 步骤 5: 保存更新后的文件 (任务 4.6)
            self._log(f"保存更新后的 A2L 文件: {output_path}")
            self._write_file(output_path, updated_lines)
            result.output_path = str(output_path)

            # 设置结果
            result.success = True
            result.message = (
                f"A2L 地址更新完成: 匹配 {result.matched_count}/{result.total_variables} 个变量"
            )

            self._log(result.message)
            if result.unmatched_variables:
                self._log(f"未匹配变量 ({result.unmatched_count}): {', '.join(result.unmatched_variables[:10])}"
                         + ("..." if result.unmatched_count > 10 else ""))

        except (ELFParseError, A2LParseError, FileNotFoundError) as e:
            result.success = False
            result.message = f"地址更新失败: {e}"
            self._log(f"错误: {result.message}")

        except Exception as e:
            result.success = False
            result.message = f"地址更新异常: {e}"
            logger.error(result.message, exc_info=True)
            self._log(f"错误: {result.message}")

        return result

    def _write_file(self, path: Path, lines: List[str]):
        """写入文件

        Args:
            path: 文件路径
            lines: 行列表
        """
        # 确保输出目录存在
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def update_with_symbol_map(
        self,
        symbol_map: Dict[str, int],
        a2l_path: Path,
        output_path: Optional[Path] = None,
        backup: bool = True
    ) -> AddressUpdateResult:
        """使用预解析的符号映射更新 A2L 文件

        当 ELF 文件已经解析过时可以使用此方法。

        Args:
            symbol_map: 符号名称到地址的映射
            a2l_path: A2L 文件路径
            output_path: 输出文件路径（可选）
            backup: 是否备份原文件

        Returns:
            AddressUpdateResult: 更新结果
        """
        a2l_path = Path(a2l_path)
        output_path = Path(output_path) if output_path else a2l_path

        result = AddressUpdateResult()
        result.total_symbols = len(symbol_map)

        try:
            # 解析 A2L 文件
            a2l_variables = self._a2l_parser.parse(a2l_path)
            result.total_variables = len(a2l_variables)

            # 备份
            if backup and output_path == a2l_path:
                backup_path = a2l_path.with_suffix('.a2l.bak')
                shutil.copy2(a2l_path, backup_path)

            # 更新地址
            lines = self._a2l_parser.get_lines()
            updated_lines = lines.copy()

            for var_name, var_info in a2l_variables.items():
                if var_name in symbol_map:
                    new_addr = symbol_map[var_name]

                    if var_info.address_line > 0:
                        old_line = lines[var_info.address_line - 1]
                        new_line = old_line.replace(
                            var_info.address_str,
                            f"0x{new_addr:08X}"
                        )
                        updated_lines[var_info.address_line - 1] = new_line

                        result.matched_count += 1
                        result.updated_variables.append(var_name)
                else:
                    result.unmatched_count += 1
                    result.unmatched_variables.append(var_name)

            # 保存文件
            self._write_file(output_path, updated_lines)
            result.output_path = str(output_path)

            result.success = True
            result.message = f"A2L 地址更新完成: 匹配 {result.matched_count}/{result.total_variables} 个变量"

        except Exception as e:
            result.success = False
            result.message = f"地址更新失败: {e}"

        return result

    def get_match_statistics(
        self,
        elf_path: Path,
        a2l_path: Path
    ) -> Tuple[int, int, int, List[str]]:
        """获取匹配统计信息（不执行更新）

        用于预览匹配情况。

        Args:
            elf_path: ELF 文件路径
            a2l_path: A2L 文件路径

        Returns:
            Tuple[int, int, int, List[str]]: (匹配数, 未匹配数, 总变量数, 未匹配列表)
        """
        elf_symbols = self._elf_parser.extract_symbols(elf_path)
        a2l_variables = self._a2l_parser.parse(a2l_path)

        matched = 0
        unmatched_list = []

        for var_name in a2l_variables:
            if var_name in elf_symbols:
                matched += 1
            else:
                unmatched_list.append(var_name)

        return matched, len(unmatched_list), len(a2l_variables), unmatched_list
