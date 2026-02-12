"""Unit tests for file processing stage executor.

Story 2.6 - 任务 5: 实现阶段执行器
- 测试 execute_stage 函数
- 测试从 context.state["matlab_output"] 获取输出目录
- 测试处理后的文件列表保存到 context.state["processed_files"]
- 测试错误处理和恢复建议
"""

import pytest
from pathlib import Path
import tempfile

from stages.file_process import execute_stage, get_stage_info
from core.models import StageConfig, BuildContext, StageStatus


class TestFileProcessStage:
    """测试文件处理阶段执行器"""

    @pytest.fixture
    def log_callback(self):
        messages = []
        def callback(msg):
            messages.append(msg)
        return callback, messages

    @pytest.fixture
    def context(self, log_callback):
        callback, _ = log_callback
        return BuildContext(
            config={},
            state={},
            log_callback=callback
        )

    @pytest.fixture
    def stage_config(self):
        return StageConfig(
            name="file_process",
            enabled=True,
            timeout=60
        )

    def test_execute_stage_success(self, context, stage_config, log_callback):
        """测试成功执行阶段 (Story 2.6 - 任务 5)"""
        callback, messages = log_callback

        # 创建模拟 MATLAB 输出目录
        with tempfile.TemporaryDirectory() as temp_dir:
            code_dir = Path(temp_dir) / "20_Code"
            code_dir.mkdir()

            # 创建测试文件
            (code_dir / "main.c").write_text("#include <stdio.h>\n\nint main() { return 0; }", encoding="utf-8")
            (code_dir / "utils.c").write_text("#include <stdio.h>\n\nint add(int a, b) { return a + b; }", encoding="utf-8")
            (code_dir / "main.h").write_text("#ifndef MAIN_H\n#define MAIN_H\n\nint main();\n#endif", encoding="utf-8")
            (code_dir / "utils.h").write_text("#ifndef UTILS_H\n#define UTILS_H\n\nint add(int a, int b);\n#endif", encoding="utf-8")
            (code_dir / "Rte_TmsApp.h").write_text("/* interface file */", encoding="utf-8")  # 应被排除
            (code_dir / "Cal.c").write_text("#include <stdio.h>\n\nint cal_value = 0;\n", encoding="utf-8")

            # 设置 context.state["matlab_output"]
            context.state["matlab_output"] = {
                "c_files": ["20_Code/main.c", "20_Code/utils.c"],
                "h_files": ["20_Code/main.h", "20_Code/utils.h", "20_Code/Rte_TmsApp.h"],
                "exclude": ["Rte_TmsApp.h"],
                "base_dir": str(code_dir)
            }

            result = execute_stage(stage_config, context)

            assert result.status == StageStatus.COMPLETED
            assert "文件处理成功" in result.message
            assert result.execution_time >= 0

            # 验证 context.state["processed_files"] (Story 2.6 - 任务 5.6)
            assert "processed_files" in context.state
            processed = context.state["processed_files"]
            assert "c_files" in processed
            assert "h_files" in processed
            assert "cal_modified" in processed
            assert processed["cal_modified"] is True

            # 验证 Rte_TmsApp.h 被排除
            h_files = processed["h_files"]
            assert all("Rte_TmsApp.h" not in f for f in h_files)

    def test_execute_stage_no_matlab_output(self, context, stage_config, log_callback):
        """测试没有 MATLAB 输出 (Story 2.6 - 任务 6.1)"""
        callback, messages = log_callback

        # 不设置 matlab_output
        result = execute_stage(stage_config, context)

        assert result.status == StageStatus.FAILED
        assert "MATLAB 输出目录未找到" in result.message

    def test_execute_stage_missing_base_dir(self, context, stage_config, log_callback):
        """测试 base_dir 不存在"""
        callback, messages = log_callback

        context.state["matlab_output"] = {
            "base_dir": "/nonexistent/path"
        }

        result = execute_stage(stage_config, context)

        assert result.status == StageStatus.FAILED
        assert "不存在" in result.message

    def test_execute_stage_no_source_files(self, context, stage_config, log_callback):
        """测试没有源文件"""
        callback, messages = log_callback

        with tempfile.TemporaryDirectory() as temp_dir:
            code_dir = Path(temp_dir) / "20_Code"
            code_dir.mkdir()

            # 不创建任何 .c 或 .h 文件
            context.state["matlab_output"] = {
                "base_dir": str(code_dir)
            }

            result = execute_stage(stage_config, context)

            assert result.status == StageStatus.FAILED
            assert "未找到任何" in result.message

    def test_execute_stage_no_cal_file(self, context, stage_config, log_callback):
        """测试没有 Cal.c 文件（非致命）"""
        callback, messages = log_callback

        with tempfile.TemporaryDirectory() as temp_dir:
            code_dir = Path(temp_dir) / "20_Code"
            code_dir.mkdir()

            # 创建文件但不包括 Cal.c
            (code_dir / "main.c").write_text("int main() { return 0; }", encoding="utf-8")

            context.state["matlab_output"] = {
                "base_dir": str(code_dir)
            }

            result = execute_stage(stage_config, context)

            assert result.status == StageStatus.COMPLETED
            assert "跳过" in "".join(messages) or "已完成" in "".join(messages)

    def test_execute_stage_saves_correct_file_count(self, context, stage_config, log_callback):
        """测试保存正确的文件数量"""
        callback, messages = log_callback

        with tempfile.TemporaryDirectory() as temp_dir:
            code_dir = Path(temp_dir) / "20_Code"
            code_dir.mkdir()

            # 创建子目录
            subdir = code_dir / "subdir"
            subdir.mkdir()

            (code_dir / "main.c").touch()
            (code_dir / "utils.c").touch()
            (code_dir / "main.h").touch()
            (subdir / "helper.c").touch()
            (subdir / "helper.h").touch()
            (code_dir / "Rte_TmsApp.h").touch()

            context.state["matlab_output"] = {
                "base_dir": str(code_dir)
            }

            result = execute_stage(stage_config, context)

            assert result.status == StageStatus.COMPLETED

            processed = context.state["processed_files"]
            # 应该有 3 个 .c 文件（不包括 Rte_TmsApp.h）
            assert len(processed["c_files"]) == 3
            # 应该有 2 个 .h 文件（排除 Rte_TmsApp.h）
            assert len(processed["h_files"]) == 2

    def test_get_stage_info(self):
        """测试获取阶段信息"""
        info = get_stage_info()

        assert isinstance(info, dict)
        assert info["name"] == "file_process"
        assert info["display_name"] == "代码文件处理"
        assert "matlab_code_path" in info["required_params"]
        assert "processed_files" in info["outputs"]


class TestErrorHandling:
    """测试错误处理和恢复建议 (Story 2.6 - 任务 6)"""

    @pytest.fixture
    def log_callback(self):
        messages = []
        def callback(msg):
            messages.append(msg)
        return callback, messages

    @pytest.fixture
    def context(self, log_callback):
        callback, _ = log_callback
        return BuildContext(
            config={},
            state={},
            log_callback=callback
        )

    @pytest.fixture
    def stage_config(self):
        return StageConfig(
            name="file_process",
            enabled=True,
            timeout=60
        )

    def test_directory_not_exists_suggestions(self, context, stage_config, log_callback):
        """测试目录不存在错误建议 (Story 2.6 - 任务 6.1)"""
        callback, messages = log_callback

        context.state["matlab_output"] = {
            "base_dir": "/completely/nonexistent/path"
        }

        result = execute_stage(stage_config, context)

        assert result.status == StageStatus.FAILED
        assert len(result.suggestions) > 0
        assert any("MATLAB" in s for s in result.suggestions)

    def test_no_source_files_suggestions(self, context, stage_config, log_callback):
        """测试无源文件错误建议 (Story 2.6 - 任务 6.2)"""
        callback, messages = log_callback

        with tempfile.TemporaryDirectory() as temp_dir:
            code_dir = Path(temp_dir) / "20_Code"
            code_dir.mkdir()

            context.state["matlab_output"] = {
                "base_dir": str(code_dir)
            }

            result = execute_stage(stage_config, context)

            assert result.status == StageStatus.FAILED
            assert len(result.suggestions) > 0
