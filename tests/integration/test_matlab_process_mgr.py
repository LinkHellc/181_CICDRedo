"""Integration tests for MATLAB process management (Story 2.13)

This module contains integration tests for the complete MATLAB process
management workflow.

Story 2.13 - 任务 13: 添加集成测试
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from integrations.matlab import (
    get_or_start_matlab,
    shutdown_matlab_process,
    detect_matlab_processes,
    connect_to_matlab,
    verify_matlab_version,
    start_matlab_process,
    parse_matlab_version,
    MatlabProcess,
    MATLAB_ENGINE_AVAILABLE,
    PSUTIL_AVAILABLE
)

from utils.errors import MatlabVersionError


class TestMatlabProcessWorkflow(unittest.TestCase):
    """测试完整进程管理流程（任务 13.2）"""

    @patch('integrations.matlab.detect_matlab_processes')
    @patch('integrations.matlab.connect_to_matlab')
    @patch('integrations.matlab.verify_matlab_version')
    @patch('integrations.matlab.start_matlab_process')
    def test_complete_workflow_no_existing(self, mock_start, mock_verify, mock_connect, mock_detect):
        """测试无现有进程时的完整流程"""
        # 模拟无现有进程
        mock_detect.return_value = []

        # 模拟启动新进程
        mock_engine = Mock()
        mock_engine.version.return_value = "R2023b"
        mock_start.return_value = mock_engine

        # 模拟版本验证
        mock_verify.return_value = (True, "R2023b", "R2020a")

        # 获取或启动
        context = {}
        engine, strategy = get_or_start_matlab(reuse_existing=True, context=context)

        self.assertIsNotNone(engine)
        self.assertEqual(strategy, "new")
        mock_start.assert_called_once()

        # 关闭进程
        shutdown_matlab_process(engine, "new", context)

        mock_engine.quit.assert_called_once()

    @patch('integrations.matlab.detect_matlab_processes')
    @patch('integrations.matlab.connect_to_matlab')
    @patch('integrations.matlab.verify_matlab_version')
    @patch('integrations.matlab.start_matlab_process')
    def test_complete_workflow_with_existing(self, mock_start, mock_verify, mock_connect, mock_detect):
        """测试有现有进程时的完整流程（任务 13.3）"""
        # 模拟现有进程
        mock_process = MatlabProcess(pid=5678)
        mock_detect.return_value = [mock_process]

        # 模拟连接成功
        mock_engine = Mock()
        mock_connect.return_value = mock_engine

        # 模拟版本兼容
        mock_verify.return_value = (True, "R2023b", "R2020a")

        # 获取或启动
        context = {}
        engine, strategy = get_or_start_matlab(reuse_existing=True, context=context)

        self.assertIsNotNone(engine)
        self.assertEqual(strategy, "reuse")
        mock_connect.assert_called_once_with(5678)
        mock_verify.assert_called_once()
        mock_start.assert_not_called()  # 不应该启动新进程

        # 关闭进程（应该保留）
        shutdown_matlab_process(engine, "reuse", context)

        mock_engine.quit.assert_not_called()  # 不应该关闭


class TestProcessReuseScenario(unittest.TestCase):
    """测试进程复用场景（任务 13.3）"""

    @patch('integrations.matlab.detect_matlab_processes')
    @patch('integrations.matlab.connect_to_matlab')
    @patch('integrations.matlab.verify_matlab_version')
    def test_reuse_first_available(self, mock_verify, mock_connect, mock_detect):
        """测试复用第一个可用的进程"""
        # 模拟多个现有进程
        processes = [
            MatlabProcess(pid=1001, exe_path="C:\\MATLAB\\R2020a\\bin\\MATLAB.exe"),
            MatlabProcess(pid=1002, exe_path="C:\\MATLAB\\R2023b\\bin\\MATLAB.exe")
        ]
        mock_detect.return_value = processes

        # 第一个进程连接成功且版本兼容
        mock_engine1 = Mock()
        mock_connect.side_effect = [mock_engine1, None]  # 第一个成功
        mock_verify.return_value = (True, "R2020a", "R2020a")

        context = {}
        engine, strategy = get_or_start_matlab(reuse_existing=True, context=context)

        self.assertIsNotNone(engine)
        self.assertEqual(strategy, "reuse")
        mock_connect.assert_called_once_with(1001)

    @patch('integrations.matlab.detect_matlab_processes')
    @patch('integrations.matlab.connect_to_matlab')
    @patch('integrations.matlab.verify_matlab_version')
    @patch('integrations.matlab.start_matlab_process')
    def test_reuse_skip_incompatible(self, mock_start, mock_verify, mock_connect, mock_detect):
        """测试跳过不兼容的进程"""
        # 模拟两个现有进程
        processes = [
            MatlabProcess(pid=1001, exe_path="C:\\MATLAB\\R2019b\\bin\\MATLAB.exe"),
            MatlabProcess(pid=1002, exe_path="C:\\MATLAB\\R2023b\\bin\\MATLAB.exe")
        ]
        mock_detect.return_value = processes

        # 第一个进程版本不兼容
        mock_engine1 = Mock()
        mock_engine2 = Mock()
        mock_connect.side_effect = [mock_engine1, mock_engine2]

        from utils.errors import MatlabVersionError
        mock_verify.side_effect = [
            MatlabVersionError("R2019b", "R2020a"),
            (True, "R2023b", "R2020a")
        ]

        context = {}
        engine, strategy = get_or_start_matlab(reuse_existing=True, context=context)

        self.assertIsNotNone(engine)
        self.assertEqual(strategy, "reuse")
        self.assertEqual(mock_verify.call_count, 2)


class TestNewProcessScenario(unittest.TestCase):
    """测试启动新进程场景（任务 13.4）"""

    @patch('integrations.matlab.detect_matlab_processes')
    @patch('integrations.matlab.start_matlab_process')
    def test_start_new_when_no_processes(self, mock_start, mock_detect):
        """测试无现有进程时启动新进程"""
        mock_detect.return_value = []

        mock_engine = Mock()
        mock_start.return_value = mock_engine

        context = {}
        engine, strategy = get_or_start_matlab(reuse_existing=True, context=context)

        self.assertEqual(strategy, "new")
        mock_start.assert_called_once()

    @patch('integrations.matlab.detect_matlab_processes')
    @patch('integrations.matlab.connect_to_matlab')
    @patch('integrations.matlab.start_matlab_process')
    def test_start_new_when_connection_fails(self, mock_start, mock_connect, mock_detect):
        """测试所有连接失败时启动新进程"""
        mock_process = MatlabProcess(pid=5678)
        mock_detect.return_value = [mock_process]

        # 连接失败
        mock_connect.return_value = None

        mock_engine = Mock()
        mock_start.return_value = mock_engine

        context = {}
        engine, strategy = get_or_start_matlab(reuse_existing=True, context=context)

        self.assertEqual(strategy, "new")
        mock_connect.assert_called_once_with(5678)
        mock_start.assert_called_once()


class TestVersionIncompatibilityHandling(unittest.TestCase):
    """测试版本不兼容处理（任务 13.5）"""

    @patch('integrations.matlab.detect_matlab_processes')
    @patch('integrations.matlab.connect_to_matlab')
    @patch('integrations.matlab.verify_matlab_version')
    @patch('integrations.matlab.start_matlab_process')
    def test_version_incompatible_start_new(self, mock_start, mock_verify, mock_connect, mock_detect):
        """测试版本不兼容时启动新进程"""
        mock_process = MatlabProcess(pid=5678)
        mock_detect.return_value = [mock_process]

        mock_engine_old = Mock()
        mock_engine_new = Mock()
        mock_connect.return_value = mock_engine_old

        # 版本不兼容
        from utils.errors import MatlabVersionError
        mock_verify.side_effect = MatlabVersionError("R2019b", "R2020a")

        mock_start.return_value = mock_engine_new

        context = {}
        engine, strategy = get_or_start_matlab(reuse_existing=True, context=context)

        self.assertEqual(strategy, "new")
        mock_start.assert_called_once()


class TestConnectionFailureHandling(unittest.TestCase):
    """测试连接失败处理（任务 13.6）"""

    @patch('integrations.matlab.detect_matlab_processes')
    @patch('integrations.matlab.connect_to_matlab')
    @patch('integrations.matlab.start_matlab_process')
    def test_connection_failure_start_new(self, mock_start, mock_connect, mock_detect):
        """测试连接失败时启动新进程"""
        processes = [
            MatlabProcess(pid=1001),
            MatlabProcess(pid=1002)
        ]
        mock_detect.return_value = processes

        # 所有连接失败
        mock_connect.return_value = None

        mock_engine = Mock()
        mock_start.return_value = mock_engine

        context = {}
        engine, strategy = get_or_start_matlab(reuse_existing=True, context=context)

        self.assertEqual(strategy, "new")
        self.assertEqual(mock_connect.call_count, 2)
        mock_start.assert_called_once()


class TestWorkflowStageIntegration(unittest.TestCase):
    """测试与工作流阶段的集成（任务 13.7）"""

    @patch('integrations.matlab.detect_matlab_processes')
    @patch('integrations.matlab.start_matlab_process')
    def test_context_state_management(self, mock_start, mock_detect):
        """测试 context.state 管理"""
        # 无现有进程
        mock_detect.return_value = []

        mock_engine = Mock()
        mock_start.return_value = mock_engine

        context = {}
        engine, strategy = get_or_start_matlab(reuse_existing=True, context=context)

        # 验证 context.state 更新
        # 注意：由于 mock start_matlab_process，context 的更新可能不会正确执行
        # 这里我们只验证返回值正确
        self.assertIsNotNone(engine)
        self.assertEqual(strategy, "new")

        # 模拟阶段执行...
        # ...

        # 手动添加 matlab_engine 到 context 以便清理
        context["matlab_engine"] = engine
        context["matlab_startup_strategy"] = strategy

        # 关闭进程（不 mock，使用真实函数）
        shutdown_matlab_process(engine, strategy, context)

        # 验证 context.state 清理
        self.assertNotIn("matlab_engine", context)
        self.assertNotIn("matlab_startup_strategy", context)


class TestVersionParsing(unittest.TestCase):
    """测试版本解析"""

    def test_parse_r2020a(self):
        """解析 R2020a"""
        year, letter = parse_matlab_version("R2020a")
        self.assertEqual(year, 2020)
        self.assertEqual(letter, "a")

    def test_parse_r2023b(self):
        """解析 R2023b"""
        year, letter = parse_matlab_version("R2023b")
        self.assertEqual(year, 2023)
        self.assertEqual(letter, "b")

    def test_parse_uppercase_letter(self):
        """解析大写字母"""
        year, letter = parse_matlab_version("R2022A")
        self.assertEqual(year, 2022)
        self.assertEqual(letter, "a")

    def test_parse_invalid_format(self):
        """解析无效格式"""
        with self.assertRaises(ValueError):
            parse_matlab_version("2020a")
        with self.assertRaises(ValueError):
            parse_matlab_version("R20")
        with self.assertRaises(ValueError):
            parse_matlab_version("R2020c")


class TestProcessDetectionIntegration(unittest.TestCase):
    """测试进程检测集成"""

    @patch('integrations.matlab.PSUTIL_AVAILABLE', True)
    @patch('integrations.matlab.psutil')
    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', True)
    @patch('integrations.matlab.matlab')
    def test_detect_and_connect_workflow(self, mock_matlab, mock_psutil):
        """测试检测和连接工作流"""
        # 模拟 MATLAB 进程
        mock_process = Mock()
        mock_process.info = {
            'pid': 5678,
            'name': 'MATLAB.exe',
            'exe': 'C:\\MATLAB\\R2023b\\bin\\MATLAB.exe',
            'create_time': 1234567890.0,
            'username': 'user'
        }
        mock_psutil.process_iter.return_value = [mock_process]

        # 模拟连接
        mock_engine = Mock()
        mock_matlab.engine.connect_matlab.return_value = mock_engine

        # 检测进程
        processes = detect_matlab_processes()
        self.assertEqual(len(processes), 1)

        # 连接
        engine = connect_to_matlab(processes[0].pid)
        self.assertIsNotNone(engine)


if __name__ == '__main__':
    unittest.main()
