"""Unit tests for A2L process stage.

This module contains unit tests for the A2L file processing stage.

Story 2.9 - Task 10: 编写单元测试
- 测试 MATLAB 命令生成
- 测试 A2L 文件验证逻辑
- 测试超时处理
- 测试错误处理和恢复建议
- 测试日志回调调用
"""

import logging
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from stages.a2l_process import (
    A2LProcessConfig,
    _generate_a2l_update_command,
    _verify_a2l_updated,
    _validate_configuration,
    execute_stage,
    _execute_matlab_command
)
from core.models import StageStatus, BuildContext
from utils.errors import ProcessTimeoutError, ProcessError


class TestA2LProcessConfig:
    """测试 A2LProcessConfig 配置类

    Story 2.9 - 任务 1.2-1.5
    """

    def test_a2l_config_defaults(self):
        """测试 A2LProcessConfig 默认值"""
        config = A2LProcessConfig()

        assert config.name == ""
        assert config.enabled is True
        assert config.a2l_path == ""
        assert config.elf_path == ""
        assert config.timestamp_format == "_%Y_%m_%d_%H_%M"
        # timeout 应该从 constants.py 中获取 a2l_process 的默认值

    def test_a2l_config_custom_values(self):
        """测试 A2LProcessConfig 自定义值"""
        config = A2LProcessConfig(
            name="a2l_process",
            a2l_path="path/to/a2l",
            elf_path="path/to/elf",
            timeout=600
        )

        assert config.name == "a2l_process"
        assert config.a2l_path == "path/to/a2l"
        assert config.elf_path == "path/to/elf"
        assert config.timeout == 600


class TestGenerateA2LUpdateCommand:
    """测试 MATLAB 命令生成函数

    Story 2.9 - 任务 2.1-2.5
    """

    def test_generate_command_with_timestamp(self):
        """测试带时间戳的命令生成"""
        context = BuildContext()
        context.state = {"build_timestamp": "_2025_02_14_10_30"}
        config = A2LProcessConfig()

        a2l_file, elf_file, command = _generate_a2l_update_command(context, config)

        assert a2l_file == "tmsAPP_2025_02_14_10_30.a2l"
        assert elf_file == "CYT4BF_M7_Master.elf"
        assert "rtw.asap2SetAddress" in command
        assert "tmsAPP_2025_02_14_10_30.a2l" in command
        assert "CYT4BF_M7_Master.elf" in command

    def test_generate_command_without_timestamp(self):
        """测试不带时间戳的命令生成"""
        context = BuildContext()
        context.state = {}
        config = A2LProcessConfig()

        a2l_file, elf_file, command = _generate_a2l_update_command(context, config)

        assert a2l_file == "tmsAPP.a2l"
        assert elf_file == "CYT4BF_M7_Master.elf"
        assert "rtw.asap2SetAddress" in command

    def test_generate_command_with_custom_elf_path(self):
        """测试自定义 ELF 文件路径"""
        context = BuildContext()
        context.state = {"build_timestamp": "_2025_02_14_10_30"}
        config = A2LProcessConfig(elf_path="custom/path/custom_elf.elf")

        a2l_file, elf_file, command = _generate_a2l_update_command(context, config)

        assert a2l_file == "tmsAPP_2025_02_14_10_30.a2l"
        assert elf_file == "custom_elf.elf"
        assert "custom_elf.elf" in command


class TestVerifyA2LUpdated:
    """测试 A2L 文件验证函数

    Story 2.9 - 任务 5.1-5.5
    """

    def test_verify_a2l_file_exists(self):
        """测试验证存在的 A2L 文件"""
        log_callback = Mock()

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False) as f:
            a2l_path = Path(f.name)
            f.write("test a2l content")

        try:
            success, message = _verify_a2l_updated(a2l_path, log_callback)

            assert success is True
            assert "验证成功" in message
            log_callback.assert_called()

        finally:
            # 清理临时文件
            a2l_path.unlink()

    def test_verify_a2l_file_not_exists(self):
        """测试验证不存在的 A2L 文件"""
        log_callback = Mock()
        a2l_path = Path("/nonexistent/path/to/file.a2l")

        success, message = _verify_a2l_updated(a2l_path, log_callback)

        assert success is False
        assert "不存在" in message

    def test_verify_a2l_file_empty(self):
        """测试验证空 A2L 文件"""
        log_callback = Mock()

        # 创建空文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.a2l', delete=False) as f:
            a2l_path = Path(f.name)

        try:
            success, message = _verify_a2l_updated(a2l_path, log_callback)

            assert success is False
            assert "大小为 0" in message

        finally:
            # 清理临时文件
            a2l_path.unlink()


class TestValidateConfiguration:
    """测试配置验证函数

    Story 2.9 - 任务 12.1-12.5
    """

    def test_validate_config_with_valid_elf(self):
        """测试验证有效配置"""
        log_callback = Mock()

        # 创建临时 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')  # ELF magic number

        try:
            config = A2LProcessConfig(elf_path=str(elf_path))
            context = BuildContext()

            result = _validate_configuration(config, context, log_callback)

            # 验证应该通过，返回 None
            assert result is None
            log_callback.assert_called()

        finally:
            # 清理临时文件
            elf_path.unlink()

    def test_validate_config_without_elf_path(self):
        """测试验证无 ELF 路径的配置"""
        log_callback = Mock()
        config = A2LProcessConfig()
        context = BuildContext()

        result = _validate_configuration(config, context, log_callback)

        # 验证应该失败
        assert result is not None
        assert result.status == StageStatus.FAILED
        assert "未配置 ELF 文件路径" in result.message
        assert len(result.suggestions) > 0

    def test_validate_config_with_nonexistent_elf(self):
        """测试验证 ELF 文件不存在"""
        log_callback = Mock()
        config = A2LProcessConfig(elf_path="/nonexistent/file.elf")
        context = BuildContext()

        result = _validate_configuration(config, context, log_callback)

        # 验证应该失败
        assert result is not None
        assert result.status == StageStatus.FAILED
        assert "不存在" in result.message

    def test_validate_config_with_empty_elf(self):
        """测试验证空 ELF 文件"""
        log_callback = Mock()

        # 创建空文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)

        try:
            config = A2LProcessConfig(elf_path=str(elf_path))
            context = BuildContext()

            result = _validate_configuration(config, context, log_callback)

            # 验证应该失败
            assert result is not None
            assert result.status == StageStatus.FAILED
            assert "大小为 0" in result.message

        finally:
            # 清理临时文件
            elf_path.unlink()


class TestExecuteStage:
    """测试阶段执行主函数

    Story 2.9 - 任务 3.1-3.5, 任务 8
    """

    def test_execute_stage_with_invalid_config_type(self):
        """测试使用无效配置类型"""
        from core.models import StageConfig

        config = StageConfig(name="test")
        context = BuildContext()
        context.log = Mock()

        result = execute_stage(config, context)

        assert result.status == StageStatus.FAILED
        assert "配置类型错误" in result.message

    def test_execute_stage_without_elf_path(self):
        """测试无 ELF 路径时执行"""
        config = A2LProcessConfig(elf_path="")
        context = BuildContext()
        context.log = Mock()

        result = execute_stage(config, context)

        assert result.status == StageStatus.FAILED
        assert "未配置 ELF 文件路径" in result.message
        context.log.assert_called()

    @patch('stages.a2l_process._execute_matlab_command')
    def test_execute_stage_success(self, mock_execute):
        """测试成功执行"""
        # 模拟成功执行 MATLAB 命令
        mock_execute.return_value = True

        # 创建临时 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')

        # 创建临时 A2L 文件（模拟 MATLAB 生成）
        # 注意：文件名必须与生成命令中的一致
        a2l_filename = "tmsAPP_2025_02_14_10_30.a2l"
        a2l_path = Path.cwd() / a2l_filename
        a2l_path.write_text("test a2l content")

        try:
            config = A2LProcessConfig(elf_path=str(elf_path))
            context = BuildContext()
            context.log = Mock()
            context.state = {"build_timestamp": "_2025_02_14_10_30"}

            result = execute_stage(config, context)

            assert result.status == StageStatus.COMPLETED
            assert "成功" in result.message
            assert len(result.output_files) > 0
            context.log.assert_called()

        finally:
            # 清理临时文件
            if elf_path.exists():
                elf_path.unlink()
            if a2l_path.exists():
                a2l_path.unlink()

    @patch('stages.a2l_process._execute_matlab_command')
    def test_execute_stage_timeout(self, mock_execute):
        """测试超时处理"""
        # 模拟超时异常
        mock_execute.side_effect = ProcessTimeoutError("MATLAB", 600)

        # 创建临时 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')

        try:
            config = A2LProcessConfig(elf_path=str(elf_path))
            context = BuildContext()
            context.log = Mock()

            result = execute_stage(config, context)

            assert result.status == StageStatus.FAILED
            assert "超时" in result.message
            assert result.error is not None
            assert len(result.suggestions) > 0

        finally:
            # 清理临时文件
            elf_path.unlink()

    @patch('stages.a2l_process._execute_matlab_command')
    def test_execute_stage_process_error(self, mock_execute):
        """测试进程错误处理"""
        # 模拟进程错误
        mock_execute.side_effect = ProcessError("MATLAB", "Test error")

        # 创建临时 ELF 文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.elf', delete=False) as f:
            elf_path = Path(f.name)
            f.write(b'\x7fELF')

        try:
            config = A2LProcessConfig(elf_path=str(elf_path))
            context = BuildContext()
            context.log = Mock()

            result = execute_stage(config, context)

            assert result.status == StageStatus.FAILED
            assert "失败" in result.message
            assert result.error is not None
            assert len(result.suggestions) > 0

        finally:
            # 清理临时文件
            elf_path.unlink()

    @patch('stages.a2l_process._execute_matlab_command')
    def test_execute_stage_log_callback(self, mock_execute):
        """测试日志回调调用"""
        # 模拟成功执行
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
            config = A2LProcessConfig(elf_path=str(elf_path))
            context = BuildContext()
            context.log = Mock()
            context.state = {"build_timestamp": "_2025_02_14_10_30"}

            result = execute_stage(config, context)

            # 验证日志回调被调用
            assert context.log.call_count > 0

            # 验证至少调用了开始、验证、命令、完成等日志
            log_messages = [call[0][0] for call in context.log.call_args_list]
            assert any("开始" in msg for msg in log_messages)
            assert any("验证" in msg for msg in log_messages)
            assert any("完成" in msg for msg in log_messages)

        finally:
            # 清理临时文件
            if elf_path.exists():
                elf_path.unlink()
            if a2l_path.exists():
                a2l_path.unlink()


class TestExecuteMatlabCommand:
    """测试 MATLAB 命令执行函数

    Story 2.9 - 任务 3.3, 4.1-4.6, 7.1-7.5

    注意：这些测试需要 MATLAB Engine API 环境
    如果未安装，将被跳过
    """

    def test_execute_matlab_command_import_error(self):
        """测试 MATLAB Engine API 未安装"""
        # 使用 __import__ 来模拟导入错误
        with patch('builtins.__import__') as mock_import:
            # 配置 mock_import 抛出 ImportError
            def import_side_effect(name, *args, **kwargs):
                if name == 'matlab.engine':
                    raise ImportError("No module named 'matlab.engine'")
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect
            log_callback = Mock()

            with pytest.raises(ProcessError) as exc_info:
                _execute_matlab_command("test_command()", 600, log_callback)

            # 验证错误消息和建议
            assert "未安装" in str(exc_info.value)
            assert len(exc_info.value.suggestions) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
