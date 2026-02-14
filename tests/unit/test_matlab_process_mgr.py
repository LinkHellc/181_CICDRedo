"""Unit tests for MATLAB process management (Story 2.13)

This module contains unit tests for the MATLAB process detection,
connection, version verification, and management functions.

Story 2.13 - 任务 12: 添加单元测试
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any
import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from integrations.matlab import (
    MatlabProcess,
    detect_matlab_processes,
    connect_to_matlab,
    parse_matlab_version,
    verify_matlab_version,
    start_matlab_process,
    get_or_start_matlab,
    shutdown_matlab_process,
    MATLAB_ENGINE_AVAILABLE,
    PSUTIL_AVAILABLE,
    matlab,
    psutil
)

from utils.errors import (
    MatlabProcessError,
    MatlabConnectionError,
    MatlabVersionError
)


class TestMatlabProcessDetection(unittest.TestCase):
    """测试 MATLAB 进程检测功能（任务 1）"""

    @patch('integrations.matlab.PSUTIL_AVAILABLE', False)
    @patch('integrations.matlab.psutil', None)
    def test_detect_processes_without_psutil(self):
        """测试无 psutil 时返回空列表（任务 1.8）"""
        processes = detect_matlab_processes()
        self.assertEqual(processes, [])

    @patch('integrations.matlab.PSUTIL_AVAILABLE', True)
    @patch('integrations.matlab.psutil')
    def test_detect_processes_no_matlab_running(self, mock_psutil):
        """测试无 MATLAB 进程时返回空列表（任务 1.8）"""
        # 模拟无 MATLAB 进程
        mock_process = Mock()
        mock_process.info = {
            'pid': 1234,
            'name': 'notepad.exe',
            'exe': 'C:\\Windows\\System32\\notepad.exe',
            'create_time': 1234567890.0,
            'username': 'user'
        }
        mock_psutil.process_iter.return_value = [mock_process]

        processes = detect_matlab_processes()

        self.assertEqual(len(processes), 0)

    @patch('integrations.matlab.PSUTIL_AVAILABLE', True)
    @patch('integrations.matlab.psutil')
    def test_detect_processes_with_matlab(self, mock_psutil):
        """测试检测到 MATLAB 进程（任务 1.7）"""
        # 模拟 MATLAB 进程
        mock_process = Mock()
        mock_process.info = {
            'pid': 5678,
            'name': 'MATLAB.exe',
            'exe': 'C:\\Program Files\\MATLAB\\R2023b\\bin\\MATLAB.exe',
            'create_time': 1234567890.0,
            'username': 'user'
        }
        mock_psutil.process_iter.return_value = [mock_process]

        processes = detect_matlab_processes()

        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0].pid, 5678)
        self.assertEqual(processes[0].exe_path, 'C:\\Program Files\\MATLAB\\R2023b\\bin\\MATLAB.exe')

    @patch('integrations.matlab.PSUTIL_AVAILABLE', True)
    @patch('integrations.matlab.psutil')
    def test_detect_processes_multiple_matlab(self, mock_psutil):
        """测试检测到多个 MATLAB 进程（任务 1.7）"""
        # 模拟多个 MATLAB 进程
        mock_process1 = Mock()
        mock_process1.info = {
            'pid': 1001,
            'name': 'MATLAB.exe',
            'exe': 'C:\\MATLAB\\R2020a\\bin\\MATLAB.exe',
            'create_time': 1234567890.0,
            'username': 'user'
        }
        mock_process2 = Mock()
        mock_process2.info = {
            'pid': 1002,
            'name': 'matlab.exe',
            'exe': 'C:\\MATLAB\\R2023b\\bin\\matlab.exe',
            'create_time': 1234567891.0,
            'username': 'user'
        }
        mock_psutil.process_iter.return_value = [mock_process1, mock_process2]

        processes = detect_matlab_processes()

        self.assertEqual(len(processes), 2)
        self.assertEqual(processes[0].pid, 1001)
        self.assertEqual(processes[1].pid, 1002)


class TestMatlabConnection(unittest.TestCase):
    """测试 MATLAB 连接功能（任务 2）"""

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', False)
    @patch('integrations.matlab.matlab', None)
    def test_connect_without_matlab_engine(self):
        """测试无 MATLAB Engine API 时返回 None（任务 2.8）"""
        engine = connect_to_matlab(1234)
        self.assertIsNone(engine)

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', True)
    @patch('integrations.matlab.matlab')
    def test_connect_success(self, mock_matlab):
        """测试成功连接（任务 2.6）"""
        # 模拟成功连接
        mock_engine = Mock()
        mock_matlab.engine.connect_matlab.return_value = mock_engine

        engine = connect_to_matlab(5678)

        self.assertIsNotNone(engine)
        mock_matlab.engine.connect_matlab.assert_called_once_with(5678)

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', True)
    @patch('integrations.matlab.matlab')
    def test_connect_failure(self, mock_matlab):
        """测试连接失败（任务 2.7）"""
        # 模拟连接失败
        mock_matlab.engine.connect_matlab.side_effect = Exception("Connection refused")

        engine = connect_to_matlab(9999)

        self.assertIsNone(engine)

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', True)
    @patch('integrations.matlab.matlab')
    def test_connect_timeout(self, mock_matlab):
        """测试连接超时（任务 2.7）"""
        # 模拟连接超时
        mock_matlab.engine.connect_matlab.side_effect = TimeoutError("Connection timeout")

        engine = connect_to_matlab(8888)

        self.assertIsNone(engine)


class TestMatlabVersion(unittest.TestCase):
    """测试 MATLAB 版本验证功能（任务 3）"""

    def test_parse_version_r2020a(self):
        """测试解析 R2020a（任务 3.7）"""
        year, letter = parse_matlab_version("R2020a")
        self.assertEqual(year, 2020)
        self.assertEqual(letter, "a")

    def test_parse_version_r2023b(self):
        """测试解析 R2023b（任务 3.7）"""
        year, letter = parse_matlab_version("R2023b")
        self.assertEqual(year, 2023)
        self.assertEqual(letter, "b")

    def test_parse_version_invalid(self):
        """测试解析无效版本"""
        with self.assertRaises(ValueError):
            parse_matlab_version("invalid")

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', True)
    @patch('integrations.matlab.matlab')
    def test_verify_version_compatible(self, mock_matlab):
        """测试版本兼容验证（任务 3.7）"""
        # 模拟 MATLAB 版本 R2023b
        mock_engine = Mock()
        mock_engine.version.return_value = "R2023b"
        mock_matlab.engine.MatlabEngine = Mock

        is_compatible, version, min_version = verify_matlab_version(mock_engine)

        self.assertTrue(is_compatible)
        self.assertEqual(version, "R2023b")
        self.assertEqual(min_version, "R2020a")

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', True)
    @patch('integrations.matlab.matlab')
    def test_verify_version_incompatible(self, mock_matlab):
        """测试版本不兼容（任务 3.8）"""
        # 模拟 MATLAB 版本 R2019b（低于 R2020a）
        mock_engine = Mock()
        mock_engine.version.return_value = "R2019b"
        mock_matlab.engine.MatlabEngine = Mock

        with self.assertRaises(MatlabVersionError):
            verify_matlab_version(mock_engine)

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', True)
    @patch('integrations.matlab.matlab')
    def test_verify_version_r2020a(self, mock_matlab):
        """测试版本正好 R2020a（最低要求）（任务 3.7）"""
        mock_engine = Mock()
        mock_engine.version.return_value = "R2020a"
        mock_matlab.engine.MatlabEngine = Mock

        is_compatible, version, min_version = verify_matlab_version(mock_engine)

        self.assertTrue(is_compatible)
        self.assertEqual(version, "R2020a")
        self.assertEqual(min_version, "R2020a")


class TestMatlabStartup(unittest.TestCase):
    """测试 MATLAB 启动功能（任务 4）"""

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', False)
    @patch('integrations.matlab.matlab', None)
    def test_start_without_matlab_engine(self):
        """测试无 MATLAB Engine API 时抛出错误（任务 4.9）"""
        with self.assertRaises(MatlabProcessError):
            start_matlab_process()

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', True)
    @patch('integrations.matlab.matlab')
    @patch('integrations.matlab.time.monotonic')
    def test_start_success(self, mock_monotonic, mock_matlab):
        """测试成功启动（任务 4.7）"""
        # 模拟时间
        mock_monotonic.side_effect = [0.0, 2.5]

        # 模拟成功启动
        mock_engine = Mock()
        mock_matlab.engine.start_matlab.return_value = mock_engine

        engine = start_matlab_process()

        self.assertIsNotNone(engine)
        mock_matlab.engine.start_matlab.assert_called_once()

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', True)
    @patch('integrations.matlab.matlab')
    def test_start_failure(self, mock_matlab):
        """测试启动失败（任务 4.9）"""
        # 模拟启动失败
        mock_matlab.engine.start_matlab.side_effect = Exception("MATLAB not found")

        with self.assertRaises(MatlabProcessError):
            start_matlab_process()

    @patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', True)
    @patch('integrations.matlab.matlab')
    def test_start_with_custom_options(self, mock_matlab):
        """测试使用自定义启动选项（任务 4.3）"""
        # 注意：MATLAB Engine API 不支持传递启动选项参数
        # 这个测试验证即使传递选项也会被忽略
        mock_engine = Mock()
        mock_matlab.engine.start_matlab.return_value = mock_engine

        # 传递自定义选项（会被忽略并发出警告）
        engine = start_matlab_process(options=["-batch", "-wait"])

        self.assertIsNotNone(engine)
        # 验证 start_matlab 被调用且没有传递参数
        mock_matlab.engine.start_matlab.assert_called_once()


class TestGetOrStartMatlab(unittest.TestCase):
    """测试获取或启动 MATLAB 决策逻辑（任务 6）"""

    @patch('integrations.matlab.start_matlab_process')
    @patch('integrations.matlab.detect_matlab_processes')
    def test_no_existing_processes_start_new(self, mock_detect, mock_start):
        """测试无现有进程时启动新进程（任务 6.9）"""
        # 模拟无现有进程
        mock_detect.return_value = []

        # 模拟启动新进程
        mock_engine = Mock()
        mock_start.return_value = mock_engine

        engine, strategy = get_or_start_matlab(reuse_existing=True)

        self.assertIsNotNone(engine)
        self.assertEqual(strategy, "new")
        mock_start.assert_called_once()

    @patch('integrations.matlab.connect_to_matlab')
    @patch('integrations.matlab.verify_matlab_version')
    @patch('integrations.matlab.detect_matlab_processes')
    def test_reuse_existing_process(self, mock_detect, mock_verify, mock_connect):
        """测试复用现有进程（任务 6.8）"""
        # 模拟现有进程
        mock_process = MatlabProcess(pid=5678)
        mock_detect.return_value = [mock_process]

        # 模拟连接成功
        mock_engine = Mock()
        mock_connect.return_value = mock_engine

        # 模拟版本兼容
        mock_verify.return_value = (True, "R2023b", "R2020a")

        engine, strategy = get_or_start_matlab(reuse_existing=True)

        self.assertIsNotNone(engine)
        self.assertEqual(strategy, "reuse")
        mock_connect.assert_called_once_with(5678)

    @patch('integrations.matlab.connect_to_matlab')
    @patch('integrations.matlab.detect_matlab_processes')
    def test_connection_fail_start_new(self, mock_detect, mock_connect):
        """测试连接失败时启动新进程（任务 6.9）"""
        # 模拟现有进程
        mock_process = MatlabProcess(pid=5678)
        mock_detect.return_value = [mock_process]

        # 模拟连接失败
        mock_connect.return_value = None

        with patch('integrations.matlab.start_matlab_process') as mock_start:
            mock_engine = Mock()
            mock_start.return_value = mock_engine

            engine, strategy = get_or_start_matlab(reuse_existing=True)

            self.assertIsNotNone(engine)
            self.assertEqual(strategy, "new")
            mock_start.assert_called_once()

    @patch('integrations.matlab.connect_to_matlab')
    @patch('integrations.matlab.verify_matlab_version')
    @patch('integrations.matlab.detect_matlab_processes')
    def test_version_incompatible_start_new(self, mock_detect, mock_verify, mock_connect):
        """测试版本不兼容时启动新进程（任务 6.10）"""
        # 模拟现有进程
        mock_process = MatlabProcess(pid=5678)
        mock_detect.return_value = [mock_process]

        # 模拟连接成功
        mock_engine = Mock()
        mock_connect.return_value = mock_engine

        # 模拟版本不兼容
        from utils.errors import MatlabVersionError
        mock_verify.side_effect = MatlabVersionError("R2019b", "R2020a")

        with patch('integrations.matlab.start_matlab_process') as mock_start:
            mock_engine_new = Mock()
            mock_start.return_value = mock_engine_new

            engine, strategy = get_or_start_matlab(reuse_existing=True)

            self.assertIsNotNone(engine)
            self.assertEqual(strategy, "new")
            mock_start.assert_called_once()

    @patch('integrations.matlab.detect_matlab_processes')
    def test_reuse_disabled_start_new(self, mock_detect):
        """测试禁用复用时启动新进程"""
        # 模拟现有进程
        mock_process = MatlabProcess(pid=5678)
        mock_detect.return_value = [mock_process]

        with patch('integrations.matlab.start_matlab_process') as mock_start:
            mock_engine = Mock()
            mock_start.return_value = mock_engine

            engine, strategy = get_or_start_matlab(reuse_existing=False)

            self.assertIsNotNone(engine)
            self.assertEqual(strategy, "new")
            mock_start.assert_called_once()


class TestShutdownMatlab(unittest.TestCase):
    """测试 MATLAB 关闭功能（任务 7）"""

    @patch('integrations.matlab.shutdown_matlab_process')
    def test_shutdown_new_process(self, mock_shutdown):
        """测试关闭新启动的进程（任务 7.7）"""
        mock_engine = Mock()
        context = {}

        shutdown_matlab_process(mock_engine, "new", context)

        mock_engine.quit.assert_called_once()
        # context 应该被清空
        self.assertEqual(context, {})

    @patch('integrations.matlab.shutdown_matlab_process')
    def test_shutdown_reused_process(self, mock_shutdown):
        """测试保留复用的进程（任务 7.8）"""
        mock_engine = Mock()
        context = {"matlab_engine": mock_engine}

        shutdown_matlab_process(mock_engine, "reuse", context)

        # 不应该调用 quit()
        mock_engine.quit.assert_not_called()
        # context 应该保留
        self.assertIn("matlab_engine", context)

    def test_shutdown_with_context(self):
        """测试关闭时清理 context"""
        mock_engine = Mock()
        context = {
            "matlab_engine": mock_engine,
            "matlab_startup_strategy": "new",
            "matlab_pid": 1234
        }

        shutdown_matlab_process(mock_engine, "new", context)

        # context 应该被清空
        self.assertNotIn("matlab_engine", context)
        self.assertNotIn("matlab_startup_strategy", context)
        self.assertNotIn("matlab_pid", context)


class TestMatlabDataModel(unittest.TestCase):
    """测试 MatlabProcess 数据模型"""

    def test_matlab_process_creation(self):
        """测试创建 MatlabProcess 对象"""
        process = MatlabProcess(
            pid=1234,
            exe_path="C:\\MATLAB\\bin\\MATLAB.exe",
            start_time=1234567890.0,
            username="user"
        )

        self.assertEqual(process.pid, 1234)
        self.assertEqual(process.exe_path, "C:\\MATLAB\\bin\\MATLAB.exe")
        self.assertEqual(process.start_time, 1234567890.0)
        self.assertEqual(process.username, "user")

    def test_matlab_process_defaults(self):
        """测试 MatlabProcess 默认值"""
        process = MatlabProcess(pid=5678)

        self.assertEqual(process.exe_path, "")
        self.assertEqual(process.start_time, 0.0)
        self.assertEqual(process.username, "")


if __name__ == '__main__':
    unittest.main()
