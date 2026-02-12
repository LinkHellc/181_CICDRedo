"""Unit tests for MATLAB code generation stage.

Story 2.5 - 单元测试要求:
- 测试 MATLAB 进程启动和关闭
- 测试 genCode.m 脚本调用（使用 mock）
- 测试超时检测逻辑
- 测试输出文件验证逻辑
- 测试错误处理和恢复建议
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import tempfile
import shutil

from stages.matlab_gen import execute_stage, _validate_output_files, get_stage_info
from core.models import StageConfig, BuildContext, StageStatus
from utils.errors import ProcessTimeoutError, ProcessError


class TestMatlabGenStage:
    """测试 MATLAB 代码生成阶段"""

    @pytest.fixture
    def log_callback(self):
        """创建日志回调 fixture"""
        messages = []
        def callback(msg):
            messages.append(msg)
        return callback, messages

    @pytest.fixture
    def context(self, log_callback):
        """创建 BuildContext fixture"""
        callback, _ = log_callback
        return BuildContext(
            config={
                "simulink_path": "C:/Projects/SimulinkModel.slx",
                "matlab_code_path": "C:/Projects/MATLAB_Code"
            },
            state={},
            log_callback=callback
        )

    @pytest.fixture
    def stage_config(self):
        """创建 StageConfig fixture"""
        return StageConfig(
            name="matlab_gen",
            enabled=True,
            timeout=1800
        )

    def test_execute_stage_success(self, context, stage_config, log_callback):
        """测试成功执行阶段 (Story 2.5 - 任务 2)"""
        callback, messages = log_callback

        # Mock MatlabIntegration
        mock_matlab_instance = MagicMock()
        mock_matlab_instance.start_engine.return_value = True

        with patch('stages.matlab_gen.MatlabIntegration', return_value=mock_matlab_instance) as mock_matlab_class:
            # Mock _validate_output_files
            with patch('stages.matlab_gen._validate_output_files') as mock_validate:
                mock_validate.return_value = {
                    "valid": True,
                    "message": "验证通过",
                    "suggestions": [],
                    "output_files": {
                        "c_files": ["20_Code/file1.c", "20_Code/file2.c"],
                        "h_files": ["20_Code/file1.h", "20_Code/file2.h"],
                        "exclude": ["Rte_TmsApp.h"],
                        "base_dir": "C:/Projects/MATLAB_Code/20_Code"
                    }
                }

                result = execute_stage(stage_config, context)

                assert result.status == StageStatus.COMPLETED
                assert "代码生成成功" in result.message
                assert result.execution_time >= 0  # 使用 >= 因为 mock 执行可能非常快

                # 验证 MATLAB 集成被正确调用
                mock_matlab_class.assert_called_once()
                mock_matlab_instance.start_engine.assert_called_once()
                mock_matlab_instance.eval_script.assert_called_once_with("genCode", "C:/Projects/SimulinkModel.slx", "C:/Projects/MATLAB_Code")
                mock_matlab_instance.stop_engine.assert_called_once()

    def test_execute_stage_no_simulink_path(self, context, stage_config):
        """测试缺少 Simulink 路径配置"""
        context.config = {}

        result = execute_stage(stage_config, context)

        assert result.status == StageStatus.FAILED
        assert "Simulink 工程路径未配置" in result.message
        assert len(result.suggestions) > 0

    def test_execute_stage_matlab_start_failed(self, context, stage_config):
        """测试 MATLAB 启动失败"""
        mock_matlab_instance = MagicMock()
        mock_matlab_instance.start_engine.return_value = False

        with patch('stages.matlab_gen.MatlabIntegration', return_value=mock_matlab_instance):
            result = execute_stage(stage_config, context)

            assert result.status == StageStatus.FAILED
            assert "启动失败" in result.message

    def test_execute_stage_timeout(self, context, stage_config):
        """测试执行超时 (Story 2.5 - 任务 5.1-5.3)"""
        mock_matlab_instance = MagicMock()
        mock_matlab_instance.start_engine.return_value = True
        mock_matlab_instance.eval_script.side_effect = ProcessTimeoutError("MATLAB 代码生成", 1800)

        with patch('stages.matlab_gen.MatlabIntegration', return_value=mock_matlab_instance):
            result = execute_stage(stage_config, context)

            assert result.status == StageStatus.FAILED
            assert "超时" in result.message
            assert result.error is not None

    def test_execute_stage_process_error(self, context, stage_config):
        """测试进程错误"""
        mock_matlab_instance = MagicMock()
        mock_matlab_instance.start_engine.return_value = True
        mock_matlab_instance.eval_script.side_effect = ProcessError("MATLAB", "执行失败")

        with patch('stages.matlab_gen.MatlabIntegration', return_value=mock_matlab_instance):
            result = execute_stage(stage_config, context)

            assert result.status == StageStatus.FAILED

    def test_execute_stage_validation_failed(self, context, stage_config):
        """测试输出文件验证失败 (Story 2.5 - 任务 7)"""
        mock_matlab_instance = MagicMock()
        mock_matlab_instance.start_engine.return_value = True

        with patch('stages.matlab_gen.MatlabIntegration', return_value=mock_matlab_instance):
            with patch('stages.matlab_gen._validate_output_files') as mock_validate:
                mock_validate.return_value = {
                    "valid": False,
                    "message": "未生成任何 .c 文件",
                    "suggestions": ["检查 Simulink 模型配置"],
                    "output_files": {}
                }

                result = execute_stage(stage_config, context)

                assert result.status == StageStatus.FAILED
                assert "未生成任何 .c 文件" in result.message

    def test_execute_stage_saves_output_to_context(self, context, stage_config):
        """测试输出保存到 context.state (Story 2.5 - 任务 7.4)"""
        mock_matlab_instance = MagicMock()
        mock_matlab_instance.start_engine.return_value = True

        expected_output = {
            "c_files": ["20_Code/file1.c"],
            "h_files": ["20_Code/file1.h"],
            "exclude": ["Rte_TmsApp.h"],
            "base_dir": "C:/Projects/MATLAB_Code/20_Code"
        }

        with patch('stages.matlab_gen.MatlabIntegration', return_value=mock_matlab_instance):
            with patch('stages.matlab_gen._validate_output_files') as mock_validate:
                mock_validate.return_value = {
                    "valid": True,
                    "message": "验证通过",
                    "suggestions": [],
                    "output_files": expected_output
                }

                result = execute_stage(stage_config, context)

                assert result.status == StageStatus.COMPLETED
                assert context.state["matlab_output"] == expected_output

    def test_validate_output_files_success(self, log_callback):
        """测试验证输出文件成功 (Story 2.5 - 任务 7)"""
        callback, messages = log_callback

        # 创建临时目录和文件
        with tempfile.TemporaryDirectory() as temp_dir:
            code_dir = Path(temp_dir) / "20_Code"
            code_dir.mkdir()

            # 创建测试文件
            (code_dir / "file1.c").touch()
            (code_dir / "file2.c").touch()
            (code_dir / "file1.h").touch()
            (code_dir / "Rte_TmsApp.h").touch()

            context = BuildContext(
                config={},
                state={},
                log_callback=callback
            )

            result = _validate_output_files(temp_dir, context)

            assert result["valid"] is True
            assert len(result["output_files"]["c_files"]) == 2
            assert len(result["output_files"]["h_files"]) == 2
            assert "Rte_TmsApp.h" in result["output_files"]["exclude"]

    def test_validate_output_files_no_directory(self, log_callback):
        """测试输出目录不存在 (Story 2.5 - 任务 7.1)"""
        callback, _ = log_callback

        context = BuildContext(
            config={},
            state={},
            log_callback=callback
        )

        result = _validate_output_files("/nonexistent/path", context)

        assert result["valid"] is False
        assert "不存在" in result["message"]

    def test_validate_output_files_no_c_files(self, log_callback):
        """测试没有生成 .c 文件 (Story 2.5 - 任务 7.3)"""
        callback, _ = log_callback

        with tempfile.TemporaryDirectory() as temp_dir:
            code_dir = Path(temp_dir) / "20_Code"
            code_dir.mkdir()

            # 只创建 .h 文件，不创建 .c 文件
            (code_dir / "file1.h").touch()

            context = BuildContext(
                config={},
                state={},
                log_callback=callback
            )

            result = _validate_output_files(temp_dir, context)

            assert result["valid"] is False
            assert "未生成任何 .c 文件" in result["message"]

    def test_validate_output_files_saves_correct_info(self, log_callback):
        """测试输出文件信息正确保存 (Story 2.5 - 任务 7.4)"""
        callback, _ = log_callback

        with tempfile.TemporaryDirectory() as temp_dir:
            code_dir = Path(temp_dir) / "20_Code"
            code_dir.mkdir()

            (code_dir / "main.c").touch()
            (code_dir / "utils.c").touch()
            (code_dir / "main.h").touch()
            (code_dir / "utils.h").touch()
            (code_dir / "Rte_TmsApp.h").touch()

            context = BuildContext(
                config={},
                state={},
                log_callback=callback
            )

            result = _validate_output_files(temp_dir, context)

            assert result["valid"] is True
            output_files = result["output_files"]

            # 验证文件列表
            assert len(output_files["c_files"]) == 2
            assert len(output_files["h_files"]) == 3

            # 验证排除文件
            assert "Rte_TmsApp.h" in output_files["exclude"]

            # 验证基础目录
            assert "20_Code" in output_files["base_dir"]

    def test_get_stage_info(self):
        """测试获取阶段信息"""
        info = get_stage_info()

        assert isinstance(info, dict)
        assert info["name"] == "matlab_gen"
        assert info["display_name"] == "MATLAB 代码生成"
        assert "simulink_path" in info["required_params"]
        assert "matlab_code_path" in info["required_params"]
        assert "matlab_output" in info["outputs"]
