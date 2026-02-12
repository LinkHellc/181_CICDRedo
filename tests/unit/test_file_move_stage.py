"""Unit tests for file move stage.

Story 2.7 - 任务 4: 实现阶段执行器
- 测试 execute_stage() 函数
- 测试从 context.state 读取 processed_files
- 测试从 context.config 读取目标目录
- 测试将 moved_files 保存到 context.state
- 测试错误处理
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.models import StageConfig, BuildContext, StageStatus
from stages.file_move import execute_stage, get_stage_info


class TestFileMoveStage:
    """测试文件移动阶段 (Story 2.7 - 任务 4)"""

    def test_get_stage_info(self):
        """测试获取阶段信息"""
        info = get_stage_info()

        assert info["name"] == "file_move"
        assert info["display_name"] == "文件移动"
        assert "matlab_code_path" in info["required_params"]
        assert "moved_files" in info["outputs"]
        assert "processed_files" in info["inputs"]

    def test_execute_moves_files_to_target(self):
        """测试文件移动到目标目录 (Story 2.7 - 任务 4.3, 4.4)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            source_dir = base_dir / "source"
            target_dir = base_dir / "target"
            source_dir.mkdir()
            target_dir.mkdir()

            # 创建源文件
            files = []
            for i in range(3):
                f = source_dir / f"test{i}.c"
                f.write_text(f"content{i}")
                files.append(f)

            # 创建模拟的 processed_files 状态
            processed_files = {
                "c_files": [str(f) for f in files],
                "h_files": [],
                "cal_modified": False
            }

            # 创建配置和上下文
            config = StageConfig(name="file_move", timeout=300)

            context = BuildContext()
            context.config = {"matlab_code_path": str(target_dir)}
            context.state = {"processed_files": processed_files}
            context.log = MagicMock()
            context.set = MagicMock()

            # 执行阶段
            result = execute_stage(config, context)

            # 验证结果
            assert result.status == StageStatus.COMPLETED
            assert result.message.startswith("文件移动成功")
            assert "moved_files" in context.state

            # 验证文件已移动
            moved_info = context.state["moved_files"]
            assert moved_info["move_count"] == 3
            for f in files:
                assert not f.exists()
                assert (target_dir / f.name).exists()

    def test_execute_reads_from_processed_files(self):
        """测试从 context.state 读取 processed_files (Story 2.7 - 任务 4.3)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            target_dir = base_dir / "target"
            target_dir.mkdir()

            # 模拟前序阶段的状态
            processed_files = {
                "c_files": [str(base_dir / "file1.c")],
                "h_files": [str(base_dir / "file1.h")],
                "cal_modified": True
            }

            config = StageConfig(name="file_move", timeout=300)
            context = BuildContext()
            context.config = {"matlab_code_path": str(target_dir)}
            context.state = {"processed_files": processed_files}
            context.log = MagicMock()

            # 执行阶段
            result = execute_stage(config, context)

            # 验证从 processed_files 读取了数据
            assert "moved_files" in context.state
            moved_info = context.state["moved_files"]
            assert "c_files" in moved_info
            assert "h_files" in moved_info

    def test_execute_fails_without_processed_files(self):
        """测试没有 processed_files 时失败"""
        config = StageConfig(name="file_move", timeout=300)
        context = BuildContext()
        context.config = {"matlab_code_path": "/tmp/target"}
        context.state = {}  # 没有 processed_files
        context.log = MagicMock()

        result = execute_stage(config, context)

        assert result.status == StageStatus.FAILED
        assert "未找到处理后的文件" in result.message

    def test_execute_fails_without_target_dir(self):
        """测试没有目标目录配置时失败 (Story 2.7 - 任务 4.4)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            source_dir = base_dir / "source"
            source_dir.mkdir()

            # 创建源文件
            (source_dir / "test.c").write_text("content")

            processed_files = {
                "c_files": [str(source_dir / "test.c")],
                "h_files": [],
                "cal_modified": False
            }

            config = StageConfig(name="file_move", timeout=300)
            context = BuildContext()
            context.config = {}  # 没有 matlab_code_path
            context.state = {"processed_files": processed_files}
            context.log = MagicMock()

            result = execute_stage(config, context)

            assert result.status == StageStatus.FAILED
            assert "未配置 MATLAB 代码路径" in result.message

    def test_execute_creates_target_if_missing(self):
        """测试目标目录不存在时自动创建 (Story 2.7 - 任务 4.5)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            source_dir = base_dir / "source"
            target_dir = base_dir / "new_target"  # 不存在
            source_dir.mkdir()

            # 创建源文件
            (source_dir / "test.c").write_text("content")

            processed_files = {
                "c_files": [str(source_dir / "test.c")],
                "h_files": [],
                "cal_modified": False
            }

            config = StageConfig(name="file_move", timeout=300)
            context = BuildContext()
            context.config = {"matlab_code_path": str(target_dir)}
            context.state = {"processed_files": processed_files}
            context.log = MagicMock()

            result = execute_stage(config, context)

            # 验证目录已创建并文件已移动
            assert result.status == StageStatus.COMPLETED
            assert target_dir.exists()
            assert (target_dir / "test.c").exists()

    def test_execute_saves_moved_files_to_state(self):
        """测试将 moved_files 保存到 context.state (Story 2.7 - 任务 4.5)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            source_dir = base_dir / "source"
            target_dir = base_dir / "target"
            source_dir.mkdir()
            target_dir.mkdir()

            # 创建源文件
            files = []
            for i in range(2):
                f = source_dir / f"test{i}.c"
                f.write_text(f"content{i}")
                files.append(f)

            processed_files = {
                "c_files": [str(f) for f in files],
                "h_files": [],
                "cal_modified": False
            }

            config = StageConfig(name="file_move", timeout=300)
            context = BuildContext()
            context.config = {"matlab_code_path": str(target_dir)}
            context.state = {"processed_files": processed_files}
            context.log = MagicMock()

            result = execute_stage(config, context)

            # 验证 moved_files 包含正确的信息
            moved_info = context.state["moved_files"]
            assert "c_files" in moved_info
            assert "h_files" in moved_info
            assert "target_dir" in moved_info
            assert "move_count" in moved_info
            assert "timestamp" in moved_info
            assert moved_info["move_count"] == 2

    def test_execute_handles_c_and_h_files(self):
        """测试处理 C 文件和头文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            source_dir = base_dir / "source"
            target_dir = base_dir / "target"
            source_dir.mkdir()
            target_dir.mkdir()

            # 创建 C 文件和头文件
            c_files = []
            h_files = []
            for i in range(2):
                c = source_dir / f"src{i}.c"
                h = source_dir / f"src{i}.h"
                c.write_text(f"// C file {i}")
                h.write_text(f"// H file {i}")
                c_files.append(c)
                h_files.append(h)

            processed_files = {
                "c_files": [str(f) for f in c_files],
                "h_files": [str(f) for f in h_files],
                "cal_modified": False
            }

            config = StageConfig(name="file_move", timeout=300)
            context = BuildContext()
            context.config = {"matlab_code_path": str(target_dir)}
            context.state = {"processed_files": processed_files}
            context.log = MagicMock()

            result = execute_stage(config, context)

            # 验证两种文件都已移动
            assert result.status == StageStatus.COMPLETED
            moved_info = context.state["moved_files"]
            assert len(moved_info["c_files"]) == 2
            assert len(moved_info["h_files"]) == 2

    def test_execute_includes_execution_time(self):
        """测试结果包含执行时间"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            source_dir = base_dir / "source"
            target_dir = base_dir / "target"
            source_dir.mkdir()
            target_dir.mkdir()

            (source_dir / "test.c").write_text("content")

            processed_files = {
                "c_files": [str(source_dir / "test.c")],
                "h_files": [],
                "cal_modified": False
            }

            config = StageConfig(name="file_move", timeout=300)
            context = BuildContext()
            context.config = {"matlab_code_path": str(target_dir)}
            context.state = {"processed_files": processed_files}
            context.log = MagicMock()

            result = execute_stage(config, context)

            # 验证包含执行时间（允许 >= 0，因为快速操作可能舍入为 0）
            assert result.status == StageStatus.COMPLETED
            assert result.execution_time >= 0


class TestFileMoveStageErrorHandling:
    """测试文件移动阶段的错误处理 (Story 2.7 - 任务 5)"""

    def test_handles_empty_file_list(self):
        """测试处理空文件列表"""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "target"
            target_dir.mkdir()

            processed_files = {
                "c_files": [],
                "h_files": [],
                "cal_modified": False
            }

            config = StageConfig(name="file_move", timeout=300)
            context = BuildContext()
            context.config = {"matlab_code_path": str(target_dir)}
            context.state = {"processed_files": processed_files}
            context.log = MagicMock()

            result = execute_stage(config, context)

            assert result.status == StageStatus.FAILED
            assert "没有需要移动的文件" in result.message

    def test_logs_progress_messages(self):
        """测试记录进度日志"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            source_dir = base_dir / "source"
            target_dir = base_dir / "target"
            source_dir.mkdir()
            target_dir.mkdir()

            (source_dir / "test.c").write_text("content")

            processed_files = {
                "c_files": [str(source_dir / "test.c")],
                "h_files": [],
                "cal_modified": False
            }

            config = StageConfig(name="file_move", timeout=300)
            context = BuildContext()
            context.config = {"matlab_code_path": str(target_dir)}
            context.state = {"processed_files": processed_files}
            log_mock = MagicMock()
            context.log = log_mock

            execute_stage(config, context)

            # 验证日志被调用
            assert log_mock.call_count > 0
            # 检查关键日志消息
            log_messages = [str(call) for call in log_mock.call_args_list]
            log_text = " ".join(log_messages)
            assert "文件移动" in log_text or "移动" in log_text
