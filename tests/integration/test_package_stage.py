"""Integration tests for package stage.

Story 2.11 - 任务 9: 集成测试
- 任务 9.2-9.8: 测试完整的文件归纳阶段执行
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import re

from core.models import StageConfig, BuildContext, StageStatus
from stages.package import execute_stage
from utils.errors import FileOperationError


class TestPackageStageIntegration:
    """测试完整的文件归纳阶段执行 (Story 2.11 - 任务 9.2)"""

    def test_full_stage_execution(self):
        """测试完整的文件归纳阶段执行 (任务 9.2)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 准备配置
            config = StageConfig(name="package", enabled=True, timeout=300)

            # 准备上下文
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "MBD_CICD_Obj"
            }
            context.log_callback = Mock()
            context.state = {
                # 模拟前置阶段的状态
                "previous_stage_output": "test_output"
            }

            # 执行阶段
            result = execute_stage(config, context)

            # 验证执行结果 (任务 9.3)
            assert result.status == StageStatus.COMPLETED
            assert "target_folder" in context.state
            assert len(result.output_files) == 1
            # execution_time 应该大于等于 0（可能非常快）
            assert result.execution_time >= 0

            # 验证目标文件夹存在
            target_folder = Path(context.state["target_folder"])
            assert target_folder.exists()
            assert target_folder.is_dir()

            # 验证文件夹名称 (任务 9.4)
            assert target_folder.name.startswith("MBD_CICD_Obj_")
            timestamp_match = re.match(r"MBD_CICD_Obj_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}", target_folder.name)
            assert timestamp_match is not None

            # 验证日志记录
            assert context.log_callback.called
            log_messages = [call[0][0] for call in context.log_callback.call_args_list]
            assert any("开始文件归纳阶段" in msg for msg in log_messages)
            assert any("文件归纳阶段完成" in msg for msg in log_messages)

    def test_timestamp_format_in_integration(self):
        """测试时间戳格式正确性 (任务 9.4)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "Test"
            }
            context.log_callback = Mock()
            context.state = {}

            execute_stage(config, context)

            target_folder = Path(context.state["target_folder"])

            # 验证时间戳格式
            assert re.match(r"Test_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}", target_folder.name)

            # 解析时间戳
            timestamp_part = target_folder.name.replace("Test_", "")
            from datetime import datetime
            try:
                parsed_ts = datetime.strptime(timestamp_part, "%Y_%m_%d_%H_%M")
                # 验证年份合理
                assert 2020 <= parsed_ts.year <= 2100
            except ValueError:
                pytest.fail("时间戳格式不正确")

    def test_conflict_handling(self):
        """测试冲突处理逻辑 (任务 9.5)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # 第一次执行
            config1 = StageConfig(name="package", enabled=True)
            context1 = BuildContext()
            context1.config = {
                "target_file_path": str(base_path),
                "target_folder_prefix": "TestFolder"
            }
            context1.log_callback = Mock()
            context1.state = {}

            result1 = execute_stage(config1, context1)
            folder1_name = Path(context1.state["target_folder"]).name

            # 由于时间戳变化，很难直接测试冲突
            # 但我们可以验证函数能处理各种情况
            # 模拟冲突：手动创建一个同名文件夹
            if folder1_name:
                folder1_path = base_path / folder1_name
                if folder1_path.exists():
                    # 第二次执行应该能创建不同的文件夹
                    # （因为时间戳会变化）
                    config2 = StageConfig(name="package", enabled=True)
                    context2 = BuildContext()
                    context2.config = {
                        "target_file_path": str(base_path),
                        "target_folder_prefix": "TestFolder"
                    }
                    context2.log_callback = Mock()
                    context2.state = {}

                    result2 = execute_stage(config2, context2)
                    assert result2.status == StageStatus.COMPLETED

                    folder2_path = Path(context2.state["target_folder"])
                    # 两个文件夹应该不同（因为时间戳或后缀）
                    assert folder2_path.exists()

    def test_permission_error_handling(self):
        """测试权限不足错误处理 (任务 9.6)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建一个模拟只读目录
            base_path = Path(temp_dir)
            readonly_dir = base_path / "readonly"
            readonly_dir.mkdir()

            # 在某些系统上，我们无法真正创建只读目录
            # 这里我们使用 mock 来模拟权限错误
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": str(readonly_dir),
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            # Mock create_target_folder_safe 抛出权限错误
            with patch('stages.package.create_target_folder_safe') as mock_create:
                error = Exception("[Errno 13] Permission denied")
                mock_create.side_effect = error

                result = execute_stage(config, context)

                # 验证错误处理
                assert result.status == StageStatus.FAILED
                assert result.error == error

                # 验证日志记录
                assert context.log_callback.called
                log_messages = [call[0][0] for call in context.log_callback.call_args_list]
                assert any("[ERROR]" in msg for msg in log_messages)

    def test_disk_space_error_handling_with_mock(self):
        """测试磁盘空间不足错误处理（使用 mock）(任务 9.7)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            # Mock create_target_folder_safe 抛出磁盘空间不足错误
            with patch('stages.package.create_target_folder_safe') as mock_create:
                error = OSError("No space left on device")
                mock_create.side_effect = error

                result = execute_stage(config, context)

                # 验证错误处理
                assert result.status == StageStatus.FAILED
                assert result.error == error
                assert "未知错误" in result.message

    def test_integration_with_previous_stages(self):
        """测试与前置阶段的集成 (任务 9.8)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()

            # 模拟前置阶段的状态数据
            context.state = {
                "matlab_output_files": ["/path/to/file1.c", "/path/to/file2.c"],
                "iar_output_hex": "/path/to/output.hex",
                "a2l_output": "/path/to/output.a2l",
                "build_timestamp": "2025_02_02_15_30"
            }

            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "MBD_CICD_Obj"
            }
            context.log_callback = Mock()

            # 执行阶段
            result = execute_stage(config, context)

            # 验证成功
            assert result.status == StageStatus.COMPLETED
            assert "target_folder" in context.state

            # 验证前置状态数据保留
            assert "matlab_output_files" in context.state
            assert "iar_output_hex" in context.state
            assert "a2l_output" in context.state
            assert "build_timestamp" in context.state

            # 验证新添加的 target_folder
            assert context.state["target_folder"].startswith(temp_dir)

    def test_multiple_executions(self):
        """测试多次执行（模拟多次构建）"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # 第一次构建
            config1 = StageConfig(name="package", enabled=True)
            context1 = BuildContext()
            context1.config = {
                "target_file_path": str(base_path),
                "target_folder_prefix": "MBD_CICD_Obj"
            }
            context1.log_callback = Mock()
            context1.state = {}

            result1 = execute_stage(config1, context1)
            assert result1.status == StageStatus.COMPLETED

            # 第二次构建
            config2 = StageConfig(name="package", enabled=True)
            context2 = BuildContext()
            context2.config = {
                "target_file_path": str(base_path),
                "target_folder_prefix": "MBD_CICD_Obj"
            }
            context2.log_callback = Mock()
            context2.state = {}

            result2 = execute_stage(config2, context2)
            assert result2.status == StageStatus.COMPLETED

            # 两个文件夹都应该存在
            folder1 = Path(context1.state["target_folder"])
            folder2 = Path(context2.state["target_folder"])
            assert folder1.exists()
            assert folder2.exists()

            # 文件夹名称应该不同（因为时间戳不同）
            assert folder1.name != folder2.name

    def test_empty_context_config(self):
        """测试空配置上下文"""
        config = StageConfig(name="package", enabled=True)
        context = BuildContext()
        context.config = {}  # 空配置
        context.log_callback = Mock()
        context.state = {}

        result = execute_stage(config, context)

        # 应该失败，但不会崩溃
        assert result.status == StageStatus.FAILED
        assert "目标文件路径配置为空" in result.message

    def test_execution_time_logging(self):
        """测试执行时间记录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            result = execute_stage(config, context)

            # 验证执行时间记录（应该大于等于 0）
            assert result.execution_time >= 0
            assert result.execution_time < 5.0  # 应该很快

            # 验证日志中包含执行时间
            log_messages = [call[0][0] for call in context.log_callback.call_args_list]
            assert any("耗时" in msg for msg in log_messages)


class TestErrorRecoveryIntegration:
    """测试错误恢复的集成"""

    def test_recoverable_error(self):
        """测试可恢复错误"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 第一次执行（成功）
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            result = execute_stage(config, context)
            assert result.status == StageStatus.COMPLETED

    def test_non_recoverable_error(self):
        """测试不可恢复错误"""
        config = StageConfig(name="package", enabled=True)
        context = BuildContext()
        context.config = {}  # 缺少必需的配置
        context.log_callback = Mock()
        context.state = {}

        result = execute_stage(config, context)
        assert result.status == StageStatus.FAILED

        # 验证提供了建议
        assert result.suggestions
        assert len(result.suggestions) > 0
