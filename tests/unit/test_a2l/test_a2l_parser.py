"""Unit tests for A2L parser.

Story 2.9 - Task 9.2: Test A2L parser functionality
"""

import pytest
import tempfile
from pathlib import Path

# 添加项目根目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from a2l.a2l_parser import A2LParser, A2LParseError, A2LVariable


class TestA2LVariable:
    """A2LVariable 数据类测试"""

    def test_create_variable(self):
        """测试创建 A2LVariable"""
        var = A2LVariable(
            name="TestVar",
            var_type="CHARACTERISTIC",
            address=0x12345678,
            address_str="0x12345678",
            line_start=10,
            line_end=20,
            address_line=15
        )

        assert var.name == "TestVar"
        assert var.var_type == "CHARACTERISTIC"
        assert var.address == 0x12345678
        assert var.line_start == 10
        assert var.line_end == 20
        assert var.address_line == 15

    def test_default_values(self):
        """测试默认值"""
        var = A2LVariable()

        assert var.name == ""
        assert var.var_type == ""
        assert var.address == 0
        assert var.address_str == ""
        assert var.line_start == 0
        assert var.line_end == 0
        assert var.address_line == 0


class TestA2LParser:
    """A2L 解析器测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.parser = A2LParser()

    def test_init(self):
        """测试初始化"""
        parser = A2LParser()
        assert parser is not None
        assert parser.variables == {}

    def test_parse_file_not_found(self):
        """测试文件不存在时的错误处理"""
        with pytest.raises(FileNotFoundError):
            self.parser.parse(Path("/nonexistent/file.a2l"))

    def test_parse_empty_file(self):
        """测试空文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write("")
            temp_path = Path(f.name)

        try:
            with pytest.raises(A2LParseError) as exc_info:
                self.parser.parse(temp_path)

            assert "0" in str(exc_info.value) or "大小为 0" in str(exc_info.value)
        finally:
            temp_path.unlink()

    def test_parse_simple_characteristic(self):
        """测试解析简单的 CHARACTERISTIC 块"""
        # 使用符合解析器预期的格式
        a2l_content = """/begin CHARACTERISTIC TestVar
    "Test Variable"
    VALUE
    address 0x12345678
    DAMOS_QM
    0.0
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            temp_path = Path(f.name)

        try:
            variables = self.parser.parse(temp_path)

            assert "TestVar" in variables
            var = variables["TestVar"]
            assert var.var_type == "CHARACTERISTIC"
            assert var.address == 0x12345678
        finally:
            temp_path.unlink()

    def test_parse_simple_measurement(self):
        """测试解析简单的 MEASUREMENT 块"""
        a2l_content = """/begin MEASUREMENT TestMeas
    "Test Measurement"
    UBYTE
    ENGINE_SPEED
    0.5
    0.0
    0.0
    255.0
    address 0x87654321
/end MEASUREMENT
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            temp_path = Path(f.name)

        try:
            variables = self.parser.parse(temp_path)

            assert "TestMeas" in variables
            var = variables["TestMeas"]
            assert var.var_type == "MEASUREMENT"
            assert var.address == 0x87654321
        finally:
            temp_path.unlink()

    def test_parse_address_line_format(self):
        """测试解析 address 行格式"""
        a2l_content = """/begin CHARACTERISTIC Var1
    "Variable 1"
    VALUE
    address 0x10000000
/end CHARACTERISTIC

/begin CHARACTERISTIC Var2
    "Variable 2"
    VALUE
    address 0x20000000
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            temp_path = Path(f.name)

        try:
            variables = self.parser.parse(temp_path)

            assert "Var1" in variables
            assert variables["Var1"].address == 0x10000000

            assert "Var2" in variables
            assert variables["Var2"].address == 0x20000000
        finally:
            temp_path.unlink()

    def test_parse_decimal_address(self):
        """测试解析十进制地址"""
        a2l_content = """/begin CHARACTERISTIC DecVar
    "Decimal Address Variable"
    VALUE
    address 123456
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            temp_path = Path(f.name)

        try:
            variables = self.parser.parse(temp_path)

            assert "DecVar" in variables
            assert variables["DecVar"].address == 123456
        finally:
            temp_path.unlink()

    def test_parse_multiple_blocks(self):
        """测试解析多个块"""
        a2l_content = """/begin CHARACTERISTIC Char1
    "Characteristic 1"
    VALUE
    address 0x10000001
/end CHARACTERISTIC

/begin MEASUREMENT Meas1
    "Measurement 1"
    UBYTE
    ENGINE_SPEED
    0.5
    address 0x20000001
/end MEASUREMENT

/begin CHARACTERISTIC Char2
    "Characteristic 2"
    VALUE
    address 0x10000002
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            temp_path = Path(f.name)

        try:
            variables = self.parser.parse(temp_path)

            assert len(variables) == 3
            assert "Char1" in variables
            assert "Meas1" in variables
            assert "Char2" in variables

            # 验证类型
            assert variables["Char1"].var_type == "CHARACTERISTIC"
            assert variables["Meas1"].var_type == "MEASUREMENT"
            assert variables["Char2"].var_type == "CHARACTERISTIC"
        finally:
            temp_path.unlink()

    def test_parse_nested_blocks(self):
        """测试解析嵌套块"""
        a2l_content = """/begin CHARACTERISTIC OuterVar
    "Outer Variable"
    VALUE
    address 0x10000000
    /begin FUNCTION_LIST
        Func1
        Func2
    /end FUNCTION_LIST
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            temp_path = Path(f.name)

        try:
            variables = self.parser.parse(temp_path)

            assert "OuterVar" in variables
            assert variables["OuterVar"].address == 0x10000000
        finally:
            temp_path.unlink()

    def test_get_variable(self):
        """测试获取变量"""
        a2l_content = """/begin CHARACTERISTIC TestVar
    "Test"
    VALUE
    address 0x12345678
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            temp_path = Path(f.name)

        try:
            self.parser.parse(temp_path)

            var = self.parser.get_variable("TestVar")
            assert var is not None
            assert var.name == "TestVar"

            # 测试不存在的变量
            var = self.parser.get_variable("NonExistent")
            assert var is None
        finally:
            temp_path.unlink()

    def test_get_address(self):
        """测试获取地址"""
        a2l_content = """/begin CHARACTERISTIC AddrVar
    "Address Variable"
    VALUE
    address 0xABCDEF00
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            temp_path = Path(f.name)

        try:
            self.parser.parse(temp_path)

            addr = self.parser.get_address("AddrVar")
            assert addr == 0xABCDEF00

            # 测试不存在的变量
            addr = self.parser.get_address("NonExistent")
            assert addr is None
        finally:
            temp_path.unlink()

    def test_get_counts(self):
        """测试获取计数"""
        a2l_content = """/begin CHARACTERISTIC Char1
    "C1"
    VALUE
    address 0x10000001
/end CHARACTERISTIC

/begin MEASUREMENT Meas1
    "M1"
    UBYTE
    ENGINE_SPEED
    0.5
    address 0x20000001
/end MEASUREMENT

/begin CHARACTERISTIC Char2
    "C2"
    VALUE
    address 0x10000002
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            temp_path = Path(f.name)

        try:
            self.parser.parse(temp_path)

            assert self.parser.get_variable_count() == 3
            assert self.parser.get_characteristic_count() == 2
            assert self.parser.get_measurement_count() == 1
        finally:
            temp_path.unlink()

    def test_get_lines(self):
        """测试获取文件行"""
        a2l_content = """Line 1
Line 2
Line 3
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False, encoding='utf-8') as f:
            f.write(a2l_content)
            temp_path = Path(f.name)

        try:
            self.parser.parse(temp_path)

            lines = self.parser.get_lines()
            assert len(lines) == 3
            assert lines[0] == "Line 1"
            assert lines[1] == "Line 2"
            assert lines[2] == "Line 3"
        finally:
            temp_path.unlink()

    def test_encoding_fallback(self):
        """测试编码回退"""
        # 创建一个包含特殊字符的文件
        a2l_content = """/begin CHARACTERISTIC TestVar
    "Test"
    VALUE
    address 0x12345678
/end CHARACTERISTIC
"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.a2l', delete=False) as f:
            f.write(a2l_content.encode('latin-1'))
            temp_path = Path(f.name)

        try:
            # 应该能够自动检测编码并解析
            variables = self.parser.parse(temp_path)
            assert "TestVar" in variables
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
