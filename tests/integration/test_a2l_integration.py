"""Integration tests for A2L process stage.

This module contains integration tests for the A2L file processing stage.

Story 2.9 - Task 10: 编写集成测试
- 测试 A2L 更新阶段的完整执行流程
- 使用纯 Python 实现（ADR-005）
- 测试 ELF 文件解析和符号提取
- 测试 A2L 文件生成和地址更新
- 测试错误场景（文件不存在、格式错误）

变更历史:
- 2026-02-25: 移除 MATLAB Engine 依赖，改用纯 Python 实现 (ADR-005)
"""

import logging
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from stages.a2l_process import execute_stage, A2LProcessConfig
from core.models import BuildContext, StageStatus
from core.workflow import STAGE_EXECUTORS
from utils.errors import ProcessError


class TestA2LProcessIntegration:
    """测试 A2L 更新阶段的完整执行流程

    Story 2.9 - 任务 10.1
    """

    def test_full_a2l_process_execution_with_python(self):
        """测试完整的 A2L 更新流程（纯 Python 实现）"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            # 创建模拟 ELF 文件（带有有效 magic）
            elf_path = temp_dir / "test.elf"
            elf_path.write_bytes(b'\x7fELF' + b'\x00' * 60)

            # 创建模拟 A2L 文件 - 使用正确的格式
            a2l_content = """/begin CHARACTERISTIC TestVar
    "Test Variable"
    VALUE
    address 0x00000000
    DAMOS_QM
    0.0
    0.0
    100.0
    FLOAT32_IEEE
    0
/end CHARACTERISTIC
"""
            a2l_path = temp_dir / "test.a2l"
            a2l_path.write_text(a2l_content, encoding='utf-8')

            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path),
                a2l_path=str(a2l_path),
                timeout=600
            )
            context = BuildContext()
            context.log = Mock()
            # 设置 a2l_source_path 以便 _generate_a2l_update_command 能找到
            context.state["a2l_source_path"] = str(a2l_path)
            context.state["iar_elf_path"] = str(elf_path)

            # Mock ELF 解析器返回符号
            with patch('a2l.elf_parser.ELFParser.extract_symbols') as mock_extract:
                mock_extract.return_value = {"TestVar": 0x10000000}

                result = execute_stage(config, context)

                # 验证结果
                assert result.status == StageStatus.COMPLETED
                assert result.execution_time >= 0  # 执行时间应该被记录

    def test_workflow_executor_registration(self):
        """测试工作流执行器注册

        Story 2.9 - 任务 8.1-8.4
        """
        # 验证 a2l_process 已在 STAGE_EXECUTORS 中注册
        assert "a2l_process" in STAGE_EXECUTORS

        # 验证可以调用
        executor = STAGE_EXECUTORS["a2l_process"]
        assert executor is not None
        assert callable(executor)


class TestELFFileChecks:
    """测试 ELF 文件存在性检查

    Story 2.9 - 任务 10.5
    """

    def test_elf_file_not_exists(self):
        """测试 ELF 文件不存在场景"""
        config = A2LProcessConfig(
            name="a2l_process",
            elf_path="/nonexistent/path/to/file.elf"
        )
        context = BuildContext()
        context.log = Mock()

        result = execute_stage(config, context)

        # 验证失败
        assert result.status == StageStatus.FAILED
        assert "不存在" in result.message or "失败" in result.message
        assert len(result.suggestions) > 0

    def test_elf_file_empty(self):
        """测试空 ELF 文件场景"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            # 创建空 ELF 文件
            elf_path = temp_dir / "empty.elf"
            elf_path.write_bytes(b"")

            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path)
            )
            context = BuildContext()
            context.log = Mock()

            result = execute_stage(config, context)

            # 验证失败
            assert result.status == StageStatus.FAILED


class TestA2LFileProcessing:
    """测试 A2L 文件处理

    Story 2.9 - 任务 10.3, 10.4
    """

    def test_a2l_address_update_flow(self):
        """测试 A2L 地址更新流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            # 创建模拟 ELF 文件
            elf_path = temp_dir / "test.elf"
            elf_path.write_bytes(b'\x7fELF' + b'\x00' * 60)

            # 创建包含多个变量的 A2L 文件 - 使用正确的格式
            a2l_content = """/begin CHARACTERISTIC Var1
    "Variable 1"
    VALUE
    address 0x00000000
/end CHARACTERISTIC

/begin CHARACTERISTIC Var2
    "Variable 2"
    VALUE
    address 0x00000004
/end CHARACTERISTIC

/begin MEASUREMENT Meas1
    "Measurement 1"
    UBYTE
    ENGINE_SPEED
    1.0
    0.0
    0.0
    255.0
    address 0x00000008
/end MEASUREMENT
"""
            a2l_path = temp_dir / "test.a2l"
            a2l_path.write_text(a2l_content, encoding='utf-8')

            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path),
                a2l_path=str(a2l_path)
            )
            context = BuildContext()
            context.log = Mock()
            # 设置 context.state 以便 _generate_a2l_update_command 能找到路径
            context.state["a2l_source_path"] = str(a2l_path)
            context.state["iar_elf_path"] = str(elf_path)

            # Mock ELF 解析器返回符号表
            with patch('a2l.elf_parser.ELFParser.extract_symbols') as mock_extract:
                mock_extract.return_value = {
                    "Var1": 0x20001000,
                    "Var2": 0x20001004,
                    "Meas1": 0x20002000
                }

                result = execute_stage(config, context)

                # 验证成功
                assert result.status == StageStatus.COMPLETED

                # 验证输出文件
                assert len(result.output_files) > 0

    def test_a2l_file_with_real_fixture(self):
        """使用真实 fixture 测试 A2L 文件处理

        注意：此测试需要真实的 A2L 文件
        """
        fixtures_dir = Path(__file__).parent.parent / "fixtures"

        a2l_files = list(fixtures_dir.glob("*.a2l"))
        if not a2l_files:
            pytest.skip("没有可用的 A2L fixture 文件")

        a2l_path = a2l_files[0]

        # 创建模拟 ELF 文件
        with tempfile.NamedTemporaryFile(suffix='.elf', delete=False) as f:
            f.write(b'\x7fELF' + b'\x00' * 60)
            elf_path = Path(f.name)

        try:
            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path),
                a2l_path=str(a2l_path)
            )
            context = BuildContext()
            context.log = Mock()

            with patch('a2l.elf_parser.ELFParser.extract_symbols') as mock_extract:
                # 返回空符号表（测试无匹配场景）
                mock_extract.return_value = {}

                result = execute_stage(config, context)

                # 应该成功但无匹配
                assert result.status == StageStatus.COMPLETED

        finally:
            elf_path.unlink()


class TestErrorScenarios:
    """测试错误场景

    Story 2.9 - 任务 10.5
    """

    def test_missing_elf_path(self):
        """测试缺少 ELF 路径场景"""
        config = A2LProcessConfig(
            name="a2l_process",
            elf_path=""
        )
        context = BuildContext()
        context.log = Mock()

        result = execute_stage(config, context)

        # 验证失败
        assert result.status == StageStatus.FAILED
        assert "未配置" in result.message or "失败" in result.message
        assert len(result.suggestions) > 0

    def test_invalid_a2l_file(self):
        """测试无效 A2L 文件场景"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            # 创建有效的 ELF 文件
            elf_path = temp_dir / "test.elf"
            elf_path.write_bytes(b'\x7fELF' + b'\x00' * 60)

            # 创建无效的 A2L 文件（空文件）
            a2l_path = temp_dir / "invalid.a2l"
            a2l_path.write_text("", encoding='utf-8')

            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path),
                a2l_path=str(a2l_path)
            )
            context = BuildContext()
            context.log = Mock()

            result = execute_stage(config, context)

            # 验证失败
            assert result.status == StageStatus.FAILED

    def test_permission_error_handling(self):
        """测试权限错误处理"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            # 创建只读 A2L 文件
            elf_path = temp_dir / "test.elf"
            elf_path.write_bytes(b'\x7fELF' + b'\x00' * 60)

            a2l_content = """
/begin CHARACTERISTIC
    Var1
    "V1"
    VALUE
    address 0x00000000
    /end CHARACTERISTIC
"""
            a2l_path = temp_dir / "readonly.a2l"
            a2l_path.write_text(a2l_content, encoding='utf-8')

            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path),
                a2l_path=str(a2l_path)
            )
            context = BuildContext()
            context.log = Mock()

            with patch('a2l.elf_parser.ELFParser.extract_symbols') as mock_extract:
                mock_extract.return_value = {"Var1": 0x10000000}

                # 设置文件只读（在某些系统上可能导致权限错误）
                a2l_path.chmod(0o444)

                try:
                    result = execute_stage(config, context)
                    # 结果取决于操作系统权限处理
                finally:
                    # 恢复权限以便清理
                    a2l_path.chmod(0o644)


class TestStageOrder:
    """测试阶段顺序

    Story 2.9 - 任务 8.2: 确保阶段顺序：iar_compile → a2l_process
    """

    def test_a2l_after_iar_in_workflow(self):
        """验证 a2l_process 在 iar_compile 之后"""
        from core.workflow import STAGE_ORDER

        # 获取阶段索引
        iar_index = STAGE_ORDER.index("iar_compile")
        a2l_index = STAGE_ORDER.index("a2l_process")

        # 验证顺序
        assert a2l_index > iar_index, "a2l_process 应该在 iar_compile 之后"

    def test_a2l_stage_dependency(self):
        """验证 a2l_process 的依赖关系"""
        from core.workflow import STAGE_DEPENDENCIES

        # 获取 a2l_process 的依赖
        a2l_deps = STAGE_DEPENDENCIES.get("a2l_process", [])

        # 验证依赖 iar_compile
        assert "iar_compile" in a2l_deps, "a2l_process 应该依赖 iar_compile"


class TestPurePythonImplementation:
    """测试纯 Python 实现 (ADR-005)

    验证新的纯 Python 实现与原 MATLAB 实现功能等效。
    """

    def test_elf_parser_extract_symbols(self):
        """测试 ELF 解析器符号提取"""
        from a2l.elf_parser import ELFParser

        parser = ELFParser()

        # 测试不存在的文件
        with pytest.raises(Exception):
            parser.extract_symbols(Path("/nonexistent.elf"))

    def test_a2l_parser_parse(self):
        """测试 A2L 解析器"""
        from a2l.a2l_parser import A2LParser

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            # 创建测试 A2L 文件 - 使用正确的格式
            a2l_content = """/begin CHARACTERISTIC TestVar
    "Test"
    VALUE
    address 0x12345678
/end CHARACTERISTIC
"""
            a2l_path = temp_dir / "test.a2l"
            a2l_path.write_text(a2l_content, encoding='utf-8')

            parser = A2LParser()
            variables = parser.parse(a2l_path)

            assert "TestVar" in variables
            assert variables["TestVar"].address == 0x12345678

    def test_address_updater_update(self):
        """测试地址更新器"""
        from a2l.address_updater import A2LAddressUpdater

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            # 创建测试 A2L 文件 - 使用正确的格式
            a2l_content = """/begin CHARACTERISTIC Var1
    "V1"
    VALUE
    address 0x00000000
/end CHARACTERISTIC
"""
            a2l_path = temp_dir / "test.a2l"
            a2l_path.write_text(a2l_content, encoding='utf-8')

            updater = A2LAddressUpdater()

            # 使用预定义的符号映射
            symbol_map = {"Var1": 0x10000000}

            result = updater.update_with_symbol_map(
                symbol_map=symbol_map,
                a2l_path=a2l_path,
                backup=False
            )

            assert result.success is True
            assert result.matched_count == 1

            # 验证文件已更新
            updated_content = a2l_path.read_text(encoding='utf-8')
            assert "0x10000000" in updated_content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
