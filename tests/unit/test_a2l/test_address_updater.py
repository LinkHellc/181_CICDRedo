"""Unit tests for A2L address updater.

Story 2.9 - Task 9.3: Test address update logic
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from a2l.address_updater import (
    A2LAddressUpdater,
    AddressUpdateResult,
    AddressUpdateError
)


class TestAddressUpdateResult:
    """AddressUpdateResult 数据类测试"""

    def test_default_values(self):
        """测试默认值"""
        result = AddressUpdateResult()

        assert result.success is False
        assert result.message == ""
        assert result.matched_count == 0
        assert result.unmatched_count == 0
        assert result.total_variables == 0
        assert result.total_symbols == 0
        assert result.updated_variables == []
        assert result.unmatched_variables == []
        assert result.output_path == ""

    def test_with_values(self):
        """测试带值创建"""
        result = AddressUpdateResult(
            success=True,
            message="Update completed",
            matched_count=10,
            unmatched_count=2,
            total_variables=12,
            total_symbols=100
        )

        assert result.success is True
        assert result.message == "Update completed"
        assert result.matched_count == 10
        assert result.unmatched_count == 2
        assert result.total_variables == 12
        assert result.total_symbols == 100


class TestA2LAddressUpdater:
    """A2L 地址更新器测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.updater = A2LAddressUpdater()

    def test_init(self):
        """测试初始化"""
        updater = A2LAddressUpdater()
        assert updater is not None

    def test_set_log_callback(self):
        """测试设置日志回调"""
        callback_called = []

        def my_callback(msg):
            callback_called.append(msg)

        self.updater.set_log_callback(my_callback)
        self.updater._log("Test message")

        assert len(callback_called) == 1
        assert callback_called[0] == "Test message"

    def test_update_file_not_found(self):
        """测试文件不存在时的处理"""
        result = self.updater.update(
            elf_path=Path("/nonexistent/file.elf"),
            a2l_path=Path("/nonexistent/file.a2l")
        )

        assert result.success is False
        assert "不存在" in result.message or "失败" in result.message

    def test_update_with_mock_parsers(self):
        """使用 Mock 解析器测试更新逻辑"""
        # 创建测试 A2L 文件 - 使用正确的格式
        a2l_content = """/begin CHARACTERISTIC Var1
    "Variable 1"
    VALUE
    address 0x00000000
/end CHARACTERISTIC

/begin CHARACTERISTIC Var2
    "Variable 2"
    VALUE
    address 0x00000000
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            a2l_path = Path(f.name)

        try:
            # Mock ELF 解析器返回符号表
            elf_symbols = {
                "Var1": 0x10000001,
                "Var2": 0x10000002
            }

            # 使用 update_with_symbol_map 方法
            result = self.updater.update_with_symbol_map(
                symbol_map=elf_symbols,
                a2l_path=a2l_path,
                backup=False
            )

            assert result.success is True
            assert result.matched_count == 2
            assert result.unmatched_count == 0
            assert "Var1" in result.updated_variables
            assert "Var2" in result.updated_variables

            # 读取更新后的文件验证地址
            with open(a2l_path, 'r', encoding='utf-8') as f:
                updated_content = f.read()

            assert "0x10000001" in updated_content
            assert "0x10000002" in updated_content

        finally:
            a2l_path.unlink()

    def test_update_partial_match(self):
        """测试部分匹配情况"""
        a2l_content = """/begin CHARACTERISTIC MatchedVar
    "Matched"
    VALUE
    address 0x00000000
/end CHARACTERISTIC

/begin CHARACTERISTIC UnmatchedVar
    "Unmatched"
    VALUE
    address 0x00000000
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            a2l_path = Path(f.name)

        try:
            # 只有 MatchedVar 在 ELF 符号表中
            elf_symbols = {
                "MatchedVar": 0x10000001
            }

            result = self.updater.update_with_symbol_map(
                symbol_map=elf_symbols,
                a2l_path=a2l_path,
                backup=False
            )

            assert result.success is True
            assert result.matched_count == 1
            assert result.unmatched_count == 1
            assert "MatchedVar" in result.updated_variables
            assert "UnmatchedVar" in result.unmatched_variables

        finally:
            a2l_path.unlink()

    def test_update_with_backup(self):
        """测试备份功能"""
        a2l_content = """/begin CHARACTERISTIC Var1
    "Variable 1"
    VALUE
    address 0x00000000
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            a2l_path = Path(f.name)

        backup_path = a2l_path.with_suffix('.a2l.bak')

        try:
            elf_symbols = {"Var1": 0x10000001}

            result = self.updater.update_with_symbol_map(
                symbol_map=elf_symbols,
                a2l_path=a2l_path,
                backup=True
            )

            assert result.success is True
            assert backup_path.exists(), "备份文件应该存在"

            # 验证备份内容是原始内容
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()

            assert "0x00000000" in backup_content

        finally:
            if a2l_path.exists():
                a2l_path.unlink()
            if backup_path.exists():
                backup_path.unlink()

    def test_update_to_different_output(self):
        """测试输出到不同文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建输入 A2L 文件
            a2l_path = Path(temp_dir) / "input.a2l"
            output_path = Path(temp_dir) / "output" / "output.a2l"

            a2l_content = """/begin CHARACTERISTIC Var1
    "Variable 1"
    VALUE
    address 0x00000000
/end CHARACTERISTIC
"""
            a2l_path.write_text(a2l_content, encoding='utf-8')

            elf_symbols = {"Var1": 0x10000001}

            result = self.updater.update_with_symbol_map(
                symbol_map=elf_symbols,
                a2l_path=a2l_path,
                output_path=output_path,
                backup=False
            )

            assert result.success is True
            assert output_path.exists(), "输出文件应该存在"
            assert str(output_path) in result.output_path

            # 原始文件应该不变
            with open(a2l_path, 'r', encoding='utf-8') as f:
                original = f.read()
            assert "0x00000000" in original

            # 输出文件应该更新
            with open(output_path, 'r', encoding='utf-8') as f:
                updated = f.read()
            assert "0x10000001" in updated

    def test_get_match_statistics(self):
        """测试获取匹配统计"""
        a2l_content = """/begin CHARACTERISTIC Var1
    "V1"
    VALUE
    address 0x00000001
/end CHARACTERISTIC

/begin CHARACTERISTIC Var2
    "V2"
    VALUE
    address 0x00000002
/end CHARACTERISTIC

/begin CHARACTERISTIC Var3
    "V3"
    VALUE
    address 0x00000003
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            a2l_path = Path(f.name)

        try:
            # Mock ELF 解析器
            with patch.object(self.updater._elf_parser, 'extract_symbols') as mock_elf:
                mock_elf.return_value = {
                    "Var1": 0x10000001,
                    "Var3": 0x10000003
                    # Var2 不在 ELF 中
                }

                matched, unmatched, total, unmatched_list = self.updater.get_match_statistics(
                    elf_path=Path("/dummy.elf"),
                    a2l_path=a2l_path
                )

                assert matched == 2
                assert unmatched == 1
                assert total == 3
                assert "Var2" in unmatched_list

        finally:
            a2l_path.unlink()


class TestA2LAddressUpdaterErrorHandling:
    """地址更新器错误处理测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.updater = A2LAddressUpdater()

    def test_handle_elf_parse_error(self):
        """测试处理 ELF 解析错误"""
        with patch.object(self.updater._elf_parser, 'extract_symbols') as mock:
            from a2l.elf_parser import ELFParseError
            mock.side_effect = ELFParseError("ELF 解析失败")

            result = self.updater.update(
                elf_path=Path("/dummy.elf"),
                a2l_path=Path("/dummy.a2l")
            )

            assert result.success is False
            assert "失败" in result.message

    def test_handle_a2l_parse_error(self):
        """测试处理 A2L 解析错误"""
        with tempfile.NamedTemporaryFile(suffix='.a2l', delete=False) as f:
            f.write(b"")  # 空文件会导致解析错误
            a2l_path = Path(f.name)

        try:
            with patch.object(self.updater._elf_parser, 'extract_symbols') as mock_elf:
                mock_elf.return_value = {"Var1": 0x1000}

                result = self.updater.update(
                    elf_path=Path("/dummy.elf"),
                    a2l_path=a2l_path
                )

                assert result.success is False

        finally:
            a2l_path.unlink()

    def test_handle_unexpected_exception(self):
        """测试处理意外异常"""
        with patch.object(self.updater._elf_parser, 'extract_symbols') as mock:
            mock.side_effect = RuntimeError("Unexpected error")

            result = self.updater.update(
                elf_path=Path("/dummy.elf"),
                a2l_path=Path("/dummy.a2l")
            )

            assert result.success is False
            assert "异常" in result.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
