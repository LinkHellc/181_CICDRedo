"""Unit tests for ELF parser.

Story 2.9 - Task 9.1: Test ELF parser functionality
"""

import pytest
import tempfile
import struct
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from a2l.elf_parser import ELFParser, ELFParseError


class TestELFParser:
    """ELF 解析器测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.parser = ELFParser()

    def test_init(self):
        """测试初始化"""
        parser = ELFParser()
        assert parser is not None

    def test_extract_symbols_file_not_found(self):
        """测试文件不存在时的错误处理"""
        with pytest.raises(FileNotFoundError):
            self.parser.extract_symbols(Path("/nonexistent/file.elf"))

    def test_extract_symbols_invalid_elf(self):
        """测试无效 ELF 文件的处理"""
        # 创建一个临时文件，内容不是有效的 ELF
        with tempfile.NamedTemporaryFile(suffix='.elf', delete=False) as f:
            f.write(b"This is not an ELF file")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ELFParseError):
                self.parser.extract_symbols(temp_path)
        finally:
            temp_path.unlink()

    def test_should_filter_symbol(self):
        """测试过滤编译器内部符号"""
        # 测试应该被过滤的符号
        assert self.parser._should_filter_symbol("__libc_start_main")
        assert self.parser._should_filter_symbol("_ZSt4cout")
        assert self.parser._should_filter_symbol(".LC0")
        assert self.parser._should_filter_symbol("._ZNV")
        assert self.parser._should_filter_symbol("module_init")
        assert self.parser._should_filter_symbol("module_fini")

        # 测试应该保留的符号
        assert not self.parser._should_filter_symbol("main")
        assert not self.parser._should_filter_symbol("g_variable")
        assert not self.parser._should_filter_symbol("MyFunction")

    def test_extract_symbols_empty_file(self):
        """测试空 ELF 文件"""
        with tempfile.NamedTemporaryFile(suffix='.elf', delete=False) as f:
            temp_path = Path(f.name)

        try:
            with pytest.raises(ELFParseError) as exc_info:
                self.parser.extract_symbols(temp_path)

            assert "0" in str(exc_info.value) or "大小为 0" in str(exc_info.value)
        finally:
            temp_path.unlink()

    def test_extract_symbols_with_real_elf(self):
        """测试使用真实 ELF 文件提取符号

        注意：此测试需要真实的 ELF 文件，如果没有则跳过
        """
        # 检查是否有测试用的 ELF 文件
        test_elf = Path(__file__).parent.parent.parent / "fixtures" / "test.elf"

        if not test_elf.exists():
            pytest.skip("测试 ELF 文件不存在，跳过测试")

        symbols = self.parser.extract_symbols(test_elf)

        # 验证返回的是字典
        assert isinstance(symbols, dict)

        # 验证没有空符号名
        for name in symbols.keys():
            assert name, f"发现空符号名"
            assert not name.startswith("__"), f"内部符号未被过滤: {name}"


class TestELFParserMocked:
    """使用 Mock 测试 ELF 解析器"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.parser = ELFParser()

    @patch('elftools.elf.elffile.ELFFile')
    def test_extract_symbols_success(self, mock_elffile_class):
        """测试成功提取符号"""
        # 创建 Mock 对象
        mock_elf = MagicMock()
        mock_symtab = MagicMock()

        # 模拟符号
        mock_symbol1 = MagicMock()
        mock_symbol1.name = "variable1"
        mock_symbol1.__getitem__ = lambda self, key: 0x1000 if key == 'st_value' else None

        mock_symbol2 = MagicMock()
        mock_symbol2.name = "variable2"
        mock_symbol2.__getitem__ = lambda self, key: 0x2000 if key == 'st_value' else None

        # 配置 Mock 返回值
        mock_symtab.iter_symbols.return_value = [mock_symbol1, mock_symbol2]
        mock_elf.get_section_by_name.return_value = mock_symtab
        mock_elffile_class.return_value = mock_elf

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.elf', delete=False) as f:
            f.write(b"\x7fELF" + b"\x00" * 60)  # ELF magic header
            temp_path = Path(f.name)

        try:
            symbols = self.parser.extract_symbols(temp_path)

            assert "variable1" in symbols
            assert symbols["variable1"] == 0x1000
            assert "variable2" in symbols
            assert symbols["variable2"] == 0x2000
        finally:
            temp_path.unlink()

    @patch('elftools.elf.elffile.ELFFile')
    def test_extract_symbols_no_symtab(self, mock_elffile_class):
        """测试 ELF 文件没有符号表"""
        mock_elf = MagicMock()
        mock_elf.get_section_by_name.return_value = None  # 没有 .symtab
        mock_elffile_class.return_value = mock_elf

        with tempfile.NamedTemporaryFile(suffix='.elf', delete=False) as f:
            f.write(b"\x7fELF" + b"\x00" * 60)
            temp_path = Path(f.name)

        try:
            symbols = self.parser.extract_symbols(temp_path)

            # 应该返回空字典而不是抛出异常
            assert symbols == {}
        finally:
            temp_path.unlink()


class TestELFParserIntegration:
    """ELF 解析器集成测试"""

    def test_parser_with_fixture(self):
        """使用测试 fixture 进行集成测试"""
        fixtures_dir = Path(__file__).parent.parent.parent / "fixtures"

        # 检查是否有 fixture
        if not fixtures_dir.exists():
            pytest.skip("Fixtures 目录不存在")

        elf_files = list(fixtures_dir.glob("*.elf"))
        if not elf_files:
            pytest.skip("没有可用的 ELF fixture 文件")

        parser = ELFParser()

        for elf_file in elf_files:
            symbols = parser.extract_symbols(elf_file)
            assert isinstance(symbols, dict), f"解析 {elf_file} 失败"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
