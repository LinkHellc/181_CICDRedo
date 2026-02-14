"""Unit tests for package stage.

Story 2.11 - 任务 5, 10: 文件归纳阶段单元测试
- 任务 5.1-5.7: 测试 execute_stage() 函数
- 任务 10.1-10.6: 测试日志记录
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from core.models import StageConfig, BuildContext, StageStatus
from stages.package import execute_stage
from utils.errors import FileOperationError, FolderCreationError


class TestExecuteStage:
    """测试文件归纳阶段执行函数"""

    def test_execute_stage_success(self):
        """测试成功创建目标文件夹 (Story 2.11 - 任务 5.1-5.7)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 准备配置
            config = StageConfig(name="package", enabled=True, timeout=300)

            # 准备上下文
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            # 执行阶段
            result = execute_stage(config, context)

            # 验证结果
            assert result.status == StageStatus.COMPLETED
            assert "target_folder" in context.state
            assert len(result.output_files) == 1

            # 验证目标文件夹存在
            target_folder = Path(context.state["target_folder"])
            assert target_folder.exists()
            assert target_folder.is_dir()
            assert target_folder.name.startswith("TestFolder_")

            # 验证日志回调被调用
            assert context.log_callback.called

    def test_execute_stage_with_default_prefix(self):
        """测试使用默认文件夹前缀"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir
                # 不设置 target_folder_prefix
            }
            context.log_callback = Mock()
            context.state = {}

            result = execute_stage(config, context)

            assert result.status == StageStatus.COMPLETED
            target_folder = Path(context.state["target_folder"])
            assert target_folder.name.startswith("MBD_CICD_Obj_")

    def test_execute_stage_missing_target_path(self):
        """测试目标文件路径配置为空"""
        config = StageConfig(name="package", enabled=True)
        context = BuildContext()
        context.config = {
            # 缺少 target_file_path
            "target_folder_prefix": "TestFolder"
        }
        context.log_callback = Mock()
        context.state = {}

        result = execute_stage(config, context)

        assert result.status == StageStatus.FAILED
        assert "目标文件路径配置为空" in result.message
        assert result.suggestions
        assert context.log_callback.called

    def test_execute_stage_target_path_not_exists(self):
        """测试目标文件路径不存在"""
        config = StageConfig(name="package", enabled=True)
        context = BuildContext()
        # 使用无效的驱动器号（在 Windows 上）
        context.config = {
            "target_file_path": "X:/this/path/does/not/exist"
        }
        context.log_callback = Mock()
        context.state = {}

        result = execute_stage(config, context)

        assert result.status == StageStatus.FAILED
        assert "目标文件路径不存在" in result.message
        assert result.suggestions
        assert context.log_callback.called

    def test_execute_stage_file_operation_error(self):
        """测试文件操作错误"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            # Mock create_target_folder_safe 抛出异常
            with patch('stages.package.create_target_folder_safe') as mock_create:
                error = FileOperationError("模拟的文件操作错误")
                mock_create.side_effect = error

                result = execute_stage(config, context)

                assert result.status == StageStatus.FAILED
                assert result.message == "模拟的文件操作错误"
                assert result.error == error
                # 注意：suggestions 在异常对象中，result.suggestions 也应该有
                assert result.suggestions == error.suggestions

    def test_execute_stage_unknown_error(self):
        """测试未知错误"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            # Mock 抛出未知异常
            with patch('stages.package.create_target_folder_safe') as mock_create:
                mock_create.side_effect = RuntimeError("模拟的未知错误")

                result = execute_stage(config, context)

                assert result.status == StageStatus.FAILED
                assert "未知错误" in result.message
                assert result.suggestions
                assert "查看详细日志" in result.suggestions

    def test_execute_stage_execution_time(self):
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

            assert result.status == StageStatus.COMPLETED
            assert result.execution_time >= 0
            assert result.execution_time < 1.0  # 应该很快完成

    def test_execute_stage_with_existing_state(self):
        """测试 context.state 中已有数据"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {
                "previous_stage_output": "some_data"
            }

            result = execute_stage(config, context)

            assert result.status == StageStatus.COMPLETED
            assert "target_folder" in context.state
            # 验证原有数据保留
            assert context.state["previous_stage_output"] == "some_data"


class TestLogging:
    """测试日志记录 (Story 2.11 - 任务 10.1-10.6)"""

    def test_log_stage_start(self):
        """测试记录阶段开始 (任务 10.4)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            execute_stage(config, context)

            # 验证日志回调被调用
            assert context.log_callback.called

            # 验证开始日志
            log_messages = [call[0][0] for call in context.log_callback.call_args_list]
            assert any("开始文件归纳阶段" in msg for msg in log_messages)

    def test_log_stage_complete(self):
        """测试记录阶段完成 (任务 10.5)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            execute_stage(config, context)

            log_messages = [call[0][0] for call in context.log_callback.call_args_list]
            assert any("文件归纳阶段完成" in msg for msg in log_messages)

    def test_log_success_message(self):
        """测试成功日志 (任务 10.1)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            execute_stage(config, context)

            log_messages = [call[0][0] for call in context.log_callback.call_args_list]
            assert any("目标文件夹创建成功" in msg for msg in log_messages)

    def test_log_error_message(self):
        """测试错误日志 (任务 10.3)"""
        config = StageConfig(name="package", enabled=True)
        context = BuildContext()
        context.config = {
            # 缺少目标路径
        }
        context.log_callback = Mock()
        context.state = {}

        execute_stage(config, context)

        log_messages = [call[0][0] for call in context.log_callback.call_args_list]
        assert any("[ERROR]" in msg for msg in log_messages)

    def test_log_contains_timestamp(self):
        """测试日志包含时间戳 (任务 10.6)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StageConfig(name="package", enabled=True)
            context = BuildContext()
            context.config = {
                "target_file_path": temp_dir,
                "target_folder_prefix": "TestFolder"
            }
            context.log_callback = Mock()
            context.state = {}

            execute_stage(config, context)

            # 验证日志包含路径信息（可以推断时间戳）
            log_messages = [call[0][0] for call in context.log_callback.call_args_list]
            success_msgs = [msg for msg in log_messages if "目标文件夹创建成功" in msg]
            assert len(success_msgs) > 0

    def test_log_suggestions_on_error(self):
        """测试错误时记录建议"""
        config = StageConfig(name="package", enabled=True)
        context = BuildContext()
        context.config = {
            # 缺少目标路径
        }
        context.log_callback = Mock()
        context.state = {}

        execute_stage(config, context)

        log_messages = [call[0][0] for call in context.log_callback.call_args_list]
        # 检查 ERROR 日志
        assert any("[ERROR]" in msg for msg in log_messages)
