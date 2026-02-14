"""Integration tests for A2L process stage.

This module contains integration tests for the A2L file processing stage.

Story 2.9 - Task 11: 编写集成测试
- 测试 A2L 更新阶段的完整执行流程
- 测试与 MATLAB 的真实集成（如环境允许）
- 测试 ELF 文件存在性检查
- 测试 A2L 文件生成和更新
- 测试错误场景（MATLAB 未安装、文件不存在）
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

    Story 2.9 - 任务 11.1
    """

    def test_full_a2l_process_execution(self):
        """测试完整的 A2L 更新流程"""
        # 创建临时 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')  # ELF magic number

        # 创建临时 A2L 文件（模拟 MATLAB 生成）
        a2l_filename = "tmsAPP_2025_02_14_10_30.a2l"
        a2l_path = Path.cwd() / a2l_filename
        a2l_path.write_text("test a2l content")

        try:
            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path),
                timeout=600
            )
            context = BuildContext()
            context.log = Mock()
            context.state = {"build_timestamp": "_2025_02_14_10_30"}

            with patch('stages.a2l_process._execute_matlab_command') as mock_execute:
                # 模拟成功执行
                mock_execute.return_value = True

                # 执行阶段
                result = execute_stage(config, context)

                # 验证结果
                assert result.status == StageStatus.COMPLETED
                assert "成功" in result.message
                assert len(result.output_files) > 0
                assert result.execution_time > 0

                # 验证日志
                assert context.log.call_count > 0

                # 验证 MATLAB 命令被调用
                mock_execute.assert_called_once()

        finally:
            # 清理临时文件
            if elf_path.exists():
                elf_path.unlink()
            if a2l_path.exists():
                a2l_path.unlink()

    def test_workflow_executor_registration(self):
        """测试工作流执行器注册

        Story 2.9 - 任务 9.1-9.4
        """
        # 验证 a2l_process 已在 STAGE_EXECUTORS 中注册
        assert "a2l_process" in STAGE_EXECUTORS

        # 验证可以调用
        executor = STAGE_EXECUTORS["a2l_process"]
        assert executor is not None
        assert callable(executor)

        # 创建临时 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')

        # 创建临时 A2L 文件（模拟 MATLAB 生成）
        a2l_filename = "tmsAPP.a2l"
        a2l_path = Path.cwd() / a2l_filename
        a2l_path.write_text("test a2l content")

        try:
            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path)
            )
            context = BuildContext()
            context.log = Mock()

            with patch('stages.a2l_process._execute_matlab_command') as mock_execute:
                mock_execute.return_value = True

                # 通过工作流执行器调用
                result = executor(config, context)

                # 验证结果
                assert result.status == StageStatus.COMPLETED

        finally:
            # 清理临时文件
            if elf_path.exists():
                elf_path.unlink()
            if a2l_path.exists():
                a2l_path.unlink()


class TestELFFileChecks:
    """测试 ELF 文件存在性检查

    Story 2.9 - 任务 11.3
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
        assert "不存在" in result.message
        assert len(result.suggestions) > 0

    def test_elf_file_empty(self):
        """测试空 ELF 文件场景"""
        # 创建空文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)

        try:
            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path)
            )
            context = BuildContext()
            context.log = Mock()

            result = execute_stage(config, context)

            # 验证失败
            assert result.status == StageStatus.FAILED
            assert "大小为 0" in result.message

        finally:
            # 清理临时文件
            if elf_path.exists():
                elf_path.unlink()

    def test_elf_file_valid(self):
        """测试有效 ELF 文件场景"""
        # 创建有效 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')  # ELF magic number

        try:
            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path)
            )
            context = BuildContext()
            context.log = Mock()

            with patch('stages.a2l_process._execute_matlab_command') as mock_execute:
                mock_execute.return_value = True

                result = execute_stage(config, context)

                # 验证通过配置验证
                mock_execute.assert_called_once()

        finally:
            # 清理临时文件
            if elf_path.exists():
                elf_path.unlink()


class TestA2LFileGeneration:
    """测试 A2L 文件生成和更新

    Story 2.9 - 任务 11.4
    """

    @patch('stages.a2l_process._execute_matlab_command')
    def test_a2l_file_path_in_output(self, mock_execute):
        """测试 A2L 文件路径在输出中"""
        mock_execute.return_value = True

        # 创建临时 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')

        # 创建临时 A2L 文件（模拟 MATLAB 生成）
        a2l_filename = "tmsAPP_2025_02_14_10_30.a2l"
        a2l_path = Path.cwd() / a2l_filename
        a2l_path.write_text("test a2l content")

        try:
            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path)
            )
            context = BuildContext()
            context.log = Mock()
            context.state = {"build_timestamp": "_2025_02_14_10_30"}

            result = execute_stage(config, context)

            # 验证输出文件列表
            assert len(result.output_files) > 0
            assert any(".a2l" in path for path in result.output_files)
            assert "tmsAPP_2025_02_14_10_30.a2l" in result.output_files[0]

        finally:
            # 清理临时文件
            if elf_path.exists():
                elf_path.unlink()
            if a2l_path.exists():
                a2l_path.unlink()

    @patch('stages.a2l_process._execute_matlab_command')
    def test_a2l_file_without_timestamp(self, mock_execute):
        """测试不带时间戳的 A2L 文件"""
        mock_execute.return_value = True

        # 创建临时 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')

        # 创建临时 A2L 文件（模拟 MATLAB 生成）
        a2l_filename = "tmsAPP.a2l"
        a2l_path = Path.cwd() / a2l_filename
        a2l_path.write_text("test a2l content")

        try:
            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path)
            )
            context = BuildContext()
            context.log = Mock()
            # 不设置时间戳

            result = execute_stage(config, context)

            # 验证输出文件名
            assert len(result.output_files) > 0
            assert "tmsAPP.a2l" in result.output_files[0]

        finally:
            # 清理临时文件
            if elf_path.exists():
                elf_path.unlink()
            if a2l_path.exists():
                a2l_path.unlink()


class TestErrorScenarios:
    """测试错误场景

    Story 2.9 - 任务 11.5
    """

    @patch('stages.a2l_process._execute_matlab_command')
    def test_matlab_not_installed(self, mock_execute):
        """测试 MATLAB 未安装场景"""
        # 模拟执行失败（导入错误）
        from utils.errors import ProcessError
        mock_execute.side_effect = ProcessError("MATLAB", "Test error")

        # 创建临时 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')

        # 创建临时 A2L 文件（模拟 MATLAB 生成）
        a2l_filename = "tmsAPP.a2l"
        a2l_path = Path.cwd() / a2l_filename
        a2l_path.write_text("test a2l content")

        try:
            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path)
            )
            context = BuildContext()
            context.log = Mock()

            result = execute_stage(config, context)

            # 验证失败
            assert result.status == StageStatus.FAILED
            assert "失败" in result.message
            assert result.error is not None
            assert isinstance(result.error, ProcessError)
            assert len(result.suggestions) > 0

        finally:
            # 清理临时文件
            if elf_path.exists():
                elf_path.unlink()
            if a2l_path.exists():
                a2l_path.unlink()

    @patch('stages.a2l_process._execute_matlab_command')
    def test_matlab_execution_error(self, mock_execute):
        """测试 MATLAB 执行错误场景"""
        # 模拟 MATLAB 执行错误
        from utils.errors import ProcessError
        mock_execute.side_effect = ProcessError("MATLAB", "Test error")

        # 创建临时 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')

        # 创建临时 A2L 文件（模拟 MATLAB 生成）
        a2l_filename = "tmsAPP.a2l"
        a2l_path = Path.cwd() / a2l_filename
        a2l_path.write_text("test a2l content")

        try:
            config = A2LProcessConfig(
                name="a2l_process",
                elf_path=str(elf_path)
            )
            context = BuildContext()
            context.log = Mock()

            result = execute_stage(config, context)

            # 验证失败
            assert result.status == StageStatus.FAILED
            assert "失败" in result.message
            assert result.error is not None
            assert isinstance(result.error, ProcessError)
            assert len(result.suggestions) > 0

        finally:
            # 清理临时文件
            if elf_path.exists():
                elf_path.unlink()
            if a2l_path.exists():
                a2l_path.unlink()

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
        assert "未配置" in result.message
        assert len(result.suggestions) > 0


class TestMATLABIntegration:
    """测试与 MATLAB 的真实集成（需要 MATLAB 环境）

    Story 2.9 - 任务 11.2

    注意：这些测试需要真实的 MATLAB 环境和 MATLAB Engine API for Python。
    如果环境不可用，这些测试将被跳过。
    """

    # 这些测试需要真实的 MATLAB 环境，在 CI/CD 环境中跳过
    @pytest.mark.skip(reason="需要真实的 MATLAB 环境")
    def test_real_matlab_engine_start_stop(self):
        """测试真实的 MATLAB 引擎启动和停止"""
        try:
            import matlab.engine

            # 启动引擎
            log_callback = Mock()
            engine = matlab.engine.start_matlab()

            try:
                # 执行简单命令
                result = engine.eval("1 + 1", nargout=1)
                assert result == 2

                # 关闭引擎
                engine.quit()
                log_callback.assert_not_called()  # 没有错误

            except Exception as e:
                # 确保引擎被关闭
                try:
                    engine.quit()
                except:
                    pass
                raise

        except ImportError:
            pytest.skip("MATLAB Engine API not installed")

    @pytest.mark.skip(reason="需要真实的 MATLAB 环境")
    def test_real_matlab_command_execution(self):
        """测试真实的 MATLAB 命令执行"""
        try:
            import matlab.engine
            from integrations.matlab import MatlabIntegration

            log_callback = Mock()
            matlab = MatlabIntegration(log_callback=log_callback)

            # 测试命令执行
            result = matlab.execute_command("a = 1 + 1;", timeout=60)

            # 验证结果
            assert result is True
            log_callback.assert_called()

        except ImportError:
            pytest.skip("MATLAB Engine API not installed")


class TestStageOrder:
    """测试阶段顺序

    Story 2.9 - 任务 9.2: 确保阶段顺序：iar_compile → a2l_process
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
