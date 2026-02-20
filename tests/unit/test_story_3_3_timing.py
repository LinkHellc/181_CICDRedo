"""Unit tests for Story 3.3: Stage Execution Time Recording and Display

Tests for recording and displaying stage execution times in workflow_thread.py.
"""

import sys
import unittest
import time
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass, field
from typing import List, Optional

from PyQt6.QtCore import QObject, pyqtSignal

# Import the modules we're testing
from src.core.workflow_thread import WorkflowThread
from src.core.models import (
    ProjectConfig,
    WorkflowConfig,
    StageConfig,
    BuildState,
    BuildContext
)


class TestStory33Timing(unittest.TestCase):
    """测试 Story 3.3: 阶段执行时间记录和显示"""

    def setUp(self):
        """测试前准备"""
        # 创建项目配置
        self.project_config = ProjectConfig(
            name="TestProject",
            description="Test project",
            simulink_path="/test/path",
            matlab_code_path="/test/matlab",
            a2l_path="/test/a2l",
            target_path="/test/target",
            iar_project_path="/test/iar"
        )

        # 创建工作流配置
        self.workflow_config = WorkflowConfig(
            id="workflow-001",
            name="TestWorkflow",
            description="Test workflow",
            stages=[
                StageConfig(
                    name="stage1",
                    enabled=True
                ),
                StageConfig(
                    name="stage2",
                    enabled=True
                ),
                StageConfig(
                    name="stage3",
                    enabled=True
                )
            ]
        )

        # Mock PyQt signals
        self.mock_progress_update = Mock()
        self.mock_stage_started = Mock()
        self.mock_stage_complete = Mock()
        self.mock_log_message = Mock()
        self.mock_error_occurred = Mock()
        self.mock_build_finished = Mock()

    def create_mock_stage_executor(self, duration: float, success: bool = True):
        """创建模拟阶段执行器

        Args:
            duration: 模拟执行时长（秒）
            success: 是否成功

        Returns:
            执行器函数
        """
        def executor(stage_config, context):
            # 模拟执行时间
            time.sleep(min(duration, 0.1))  # 避免测试时间过长

            from src.core.models import StageResult, StageStatus

            if success:
                return StageResult(
                    status=StageStatus.COMPLETED,
                    message=f"阶段 {stage_config.name} 完成"
                )
            else:
                return StageResult(
                    status=StageStatus.FAILED,
                    message=f"阶段 {stage_config.name} 失败"
                )

        return executor

    def test_1_1_stage_execution_time_recorded(self):
        """测试 1.1: 阶段执行时间被记录"""
        # Patch STAGE_EXECUTORS
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05),
            "stage2": self.create_mock_stage_executor(0.1),
            "stage3": self.create_mock_stage_executor(0.03)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            # 创建工作流线程
            thread = WorkflowThread(self.project_config, self.workflow_config)

            # 连接信号
            thread.progress_update.connect(self.mock_progress_update)
            thread.stage_started.connect(self.mock_stage_started)
            thread.stage_complete.connect(self.mock_stage_complete)
            thread.log_message.connect(self.mock_log_message)
            thread.build_finished.connect(self.mock_build_finished)

            # 运行工作流
            thread.run()

            # 获取构建执行信息
            build_execution = thread.get_build_execution()

            # 验证阶段执行时间被记录
            self.assertEqual(len(build_execution.stages), 3)

            # 验证每个阶段都有时间记录
            for stage in build_execution.stages:
                self.assertGreater(stage.start_time, 0)
                self.assertGreater(stage.end_time, stage.start_time)
                self.assertGreater(stage.duration, 0)

    def test_1_2_stage_time_logged(self):
        """测试 1.2: 阶段执行时间通过日志发射"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05),
            "stage2": self.create_mock_stage_executor(0.1),
            "stage3": self.create_mock_stage_executor(0.03)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.log_message.connect(self.mock_log_message)

            # 运行工作流
            thread.run()

            # 验证日志消息被调用
            log_calls = self.mock_log_message.call_args_list

            # 验证包含阶段执行时间的日志消息
            time_log_found = False
            for call in log_calls:
                msg = call[0][0]  # 获取第一个参数（消息）
                if "执行时长:" in msg and "秒" in msg:
                    time_log_found = True
                    # 验证格式
                    self.assertIn("[", msg)
                    self.assertIn("]", msg)
                    break

            self.assertTrue(time_log_found, "应该有包含执行时间的日志消息")

    def test_1_3_stage_time_format(self):
        """测试 1.3: 阶段执行时间格式正确"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.log_message.connect(self.mock_log_message)

            thread.run()

            # 查找包含 "stage1" 和 "执行时长" 的日志消息
            log_messages = [call[0][0] for call in self.mock_log_message.call_args_list]
            time_messages = [msg for msg in log_messages if "stage1" in msg and "执行时长:" in msg]

            self.assertGreater(len(time_messages), 0, "应该有阶段执行时间消息")

            # 验证格式: [stage1] 执行时长: XX.XX 秒
            import re
            pattern = r'\[stage1\] 执行时长: \d+\.\d+ 秒'
            matches = [msg for msg in time_messages if re.search(pattern, msg)]
            self.assertGreater(len(matches), 0, "格式应该匹配 [阶段名称] 执行时长: XX.XX 秒")

    def test_1_4_summary_emitted_on_success(self):
        """测试 1.4: 成功时发射汇总信息"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05),
            "stage2": self.create_mock_stage_executor(0.1),
            "stage3": self.create_mock_stage_executor(0.03)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.log_message.connect(self.mock_log_message)
            thread.build_finished.connect(self.mock_build_finished)

            thread.run()

            # 验证汇总信息被发射
            log_messages = [call[0][0] for call in self.mock_log_message.call_args_list]

            # 验证包含汇总信息的关键词
            summary_found = False
            for msg in log_messages:
                if "工作流执行汇总" in msg:
                    summary_found = True
                    break

            self.assertTrue(summary_found, "应该有工作流执行汇总信息")

    def test_1_5_summary_contains_total_duration(self):
        """测试 1.5: 汇总信息包含总耗时"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05),
            "stage2": self.create_mock_stage_executor(0.1),
            "stage3": self.create_mock_stage_executor(0.03)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.log_message.connect(self.mock_log_message)

            thread.run()

            log_messages = [call[0][0] for call in self.mock_log_message.call_args_list]

            # 验证包含总耗时
            total_duration_found = False
            for msg in log_messages:
                if "总耗时:" in msg and "秒" in msg:
                    total_duration_found = True
                    # 验证格式: 总耗时: XX.XX 秒
                    import re
                    pattern = r'总耗时: \d+\.\d+ 秒'
                    self.assertIsNotNone(re.search(pattern, msg))
                    break

            self.assertTrue(total_duration_found, "汇总信息应该包含总耗时")

    def test_1_6_summary_contains_slowest_stage(self):
        """测试 1.6: 汇总信息包含最慢阶段"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05),
            "stage2": self.create_mock_stage_executor(0.1),  # 最慢
            "stage3": self.create_mock_stage_executor(0.03)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.log_message.connect(self.mock_log_message)

            thread.run()

            log_messages = [call[0][0] for call in self.mock_log_message.call_args_list]

            # 验证包含最慢阶段
            slowest_found = False
            for msg in log_messages:
                if "最慢阶段:" in msg:
                    slowest_found = True
                    # 验证包含 stage2
                    self.assertIn("stage2", msg)
                    # 验证格式: 最慢阶段: [stage2] XX.XX 秒
                    import re
                    pattern = r'最慢阶段: \[stage2\] \d+\.\d+ 秒'
                    self.assertIsNotNone(re.search(pattern, msg))
                    break

            self.assertTrue(slowest_found, "汇总信息应该包含最慢阶段")

    def test_1_7_summary_contains_fastest_stage(self):
        """测试 1.7: 汇总信息包含最快阶段"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05),
            "stage2": self.create_mock_stage_executor(0.1),
            "stage3": self.create_mock_stage_executor(0.03)  # 最快
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.log_message.connect(self.mock_log_message)

            thread.run()

            log_messages = [call[0][0] for call in self.mock_log_message.call_args_list]

            # 验证包含最快阶段
            fastest_found = False
            for msg in log_messages:
                if "最快阶段:" in msg:
                    fastest_found = True
                    # 验证包含 stage3
                    self.assertIn("stage3", msg)
                    # 验证格式: 最快阶段: [stage3] XX.XX 秒
                    import re
                    pattern = r'最快阶段: \[stage3\] \d+\.\d+ 秒'
                    self.assertIsNotNone(re.search(pattern, msg))
                    break

            self.assertTrue(fastest_found, "汇总信息应该包含最快阶段")

    def test_1_8_summary_contains_completed_count(self):
        """测试 1.8: 汇总信息包含已完成阶段数"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05),
            "stage2": self.create_mock_stage_executor(0.1),
            "stage3": self.create_mock_stage_executor(0.03)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.log_message.connect(self.mock_log_message)

            thread.run()

            log_messages = [call[0][0] for call in self.mock_log_message.call_args_list]

            # 验证包含已完成阶段数
            completed_count_found = False
            for msg in log_messages:
                if "已完成阶段数:" in msg:
                    completed_count_found = True
                    # 验证格式: 已完成阶段数: 3/3
                    import re
                    pattern = r'已完成阶段数: \d+/\d+'
                    self.assertIsNotNone(re.search(pattern, msg))
                    # 验证数字正确
                    match = re.search(r'已完成阶段数: (\d+)/(\d+)', msg)
                    self.assertIsNotNone(match)
                    self.assertEqual(match.group(1), "3")  # 已完成
                    self.assertEqual(match.group(2), "3")  # 总数
                    break

            self.assertTrue(completed_count_found, "汇总信息应该包含已完成阶段数")

    def test_1_9_summary_on_failure(self):
        """测试 1.9: 失败时也显示部分汇总信息"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05),
            "stage2": self.create_mock_stage_executor(0.1, success=False),
            "stage3": self.create_mock_stage_executor(0.03)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.log_message.connect(self.mock_log_message)
            thread.build_finished.connect(self.mock_build_finished)

            thread.run()

            log_messages = [call[0][0] for call in self.mock_log_message.call_args_list]

            # 验证即使在失败时也有汇总信息
            summary_found = False
            for msg in log_messages:
                if "工作流执行汇总" in msg:
                    summary_found = True
                    break

            self.assertTrue(summary_found, "失败时也应该显示汇总信息")

    def test_1_10_timestamp_in_logs(self):
        """测试 1.10: 日志消息包含时间戳"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.log_message.connect(self.mock_log_message)

            thread.run()

            # 验证主要日志消息包含时间戳
            log_messages = [call[0][0] for call in self.mock_log_message.call_args_list]

            # 查找工作流开始和完成的日志消息
            timestamp_found = False
            for msg in log_messages:
                if "工作流" in msg or "执行时长" in msg:
                    import re
                    timestamp_pattern = r'^\[\d{2}:\d{2}:\d{2}\]'
                    if re.search(timestamp_pattern, msg):
                        timestamp_found = True
                        break

            self.assertTrue(timestamp_found, "主要日志消息应该包含时间戳")

    def test_1_11_multiple_stages_time_accuracy(self):
        """测试 1.11: 多个阶段的时间记录准确性"""
        durations = [0.05, 0.08, 0.03]
        mock_executors = {
            "stage1": self.create_mock_stage_executor(durations[0]),
            "stage2": self.create_mock_stage_executor(durations[1]),
            "stage3": self.create_mock_stage_executor(durations[2])
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.run()

            build_execution = thread.get_build_execution()

            # 验证时间记录的顺序
            stage_times = {s.name: s.duration for s in build_execution.stages}

            # 验证每个阶段的时间都被记录
            self.assertIn("stage1", stage_times)
            self.assertIn("stage2", stage_times)
            self.assertIn("stage3", stage_times)

            # 验证 stage2 是最慢的
            self.assertGreater(stage_times["stage2"], stage_times["stage1"])
            self.assertGreater(stage_times["stage2"], stage_times["stage3"])

    def test_1_12_build_execution_total_duration(self):
        """测试 1.12: BuildExecution 记录总耗时"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05),
            "stage2": self.create_mock_stage_executor(0.1),
            "stage3": self.create_mock_stage_executor(0.03)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.run()

            build_execution = thread.get_build_execution()

            # 验证总耗时被记录
            self.assertGreater(build_execution.duration, 0)
            # 比较枚举的值而不是枚举本身
            self.assertEqual(build_execution.state.value, BuildState.COMPLETED.value)

    def test_1_13_summary_format_consistency(self):
        """测试 1.13: 汇总信息格式一致性"""
        mock_executors = {
            "stage1": self.create_mock_stage_executor(0.05),
            "stage2": self.create_mock_stage_executor(0.1),
            "stage3": self.create_mock_stage_executor(0.03)
        }

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, self.workflow_config)
            thread.log_message.connect(self.mock_log_message)

            thread.run()

            log_messages = [call[0][0] for call in self.mock_log_message.call_args_list]

            # 验证汇总信息的格式
            # 查找汇总信息的开始和结束
            summary_start = -1
            summary_end = -1
            for i, msg in enumerate(log_messages):
                if "工作流执行汇总" in msg:
                    summary_start = i
                if summary_start >= 0 and summary_end < 0 and "========" in msg and i > summary_start:
                    summary_end = i
                    break

            self.assertGreater(summary_start, -1, "应该找到汇总信息开始")
            self.assertGreater(summary_end, -1, "应该找到汇总信息结束")

            # 验证汇总信息包含所有必需的字段
            summary_section = log_messages[summary_start:summary_end+1]
            summary_text = "\n".join(summary_section)

            required_fields = [
                "工作流执行汇总",
                "总耗时:",
                "已完成阶段数:",
                "最慢阶段:",
                "最快阶段:"
            ]

            for field in required_fields:
                self.assertIn(field, summary_text, f"汇总信息应该包含 {field}")

    def test_1_14_empty_workflow_handling(self):
        """测试 1.14: 空工作流的处理"""
        # 创建没有启用阶段的工作流
        empty_workflow = WorkflowConfig(
            id="workflow-empty",
            name="EmptyWorkflow",
            description="Empty workflow",
            stages=[]
        )

        mock_executors = {}

        with patch('core.workflow.STAGE_EXECUTORS', mock_executors):
            thread = WorkflowThread(self.project_config, empty_workflow)
            thread.log_message.connect(self.mock_log_message)

            thread.run()

            build_execution = thread.get_build_execution()

            # 验证空工作流不会出错
            self.assertEqual(len(build_execution.stages), 0)
            # 比较枚举的值而不是枚举本身
            self.assertEqual(build_execution.state.value, BuildState.FAILED.value)


if __name__ == '__main__':
    unittest.main()
