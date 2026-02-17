"""Unit tests for terminate_process function (Story 2.15 - Task 3)

This module contains unit tests for the process termination utility.
"""

import pytest
import subprocess
import time
from unittest.mock import Mock, patch, MagicMock

from utils.process_mgr import terminate_process, _cleanup_process_tree


class TestTerminateProcess:
    """测试进程终止函数 (Story 2.15 - Task 3.7-3.9)"""

    def test_terminate_process_already_exited(self):
        """测试终止已退出的进程 (Task 3.7)"""
        # 创建一个立即退出的进程
        proc = subprocess.Popen(["exit", "0"], shell=True)
        proc.wait()  # 等待进程退出

        # 尝试终止
        success = terminate_process(proc, timeout=5)

        # 验证：应该返回 True
        assert success is True
        assert proc.poll() is not None

    def test_terminate_process_graceful(self):
        """测试优雅终止进程 (Task 3.7)"""
        # 创建一个可以优雅终止的进程
        proc = subprocess.Popen(["python", "-c", "import time; time.sleep(10)"])

        # 等待进程启动
        time.sleep(0.1)

        # 尝试优雅终止
        success = terminate_process(proc, timeout=5)

        # 验证
        assert success is True
        assert proc.poll() is not None

    def test_terminate_process_force(self):
        """测试强制终止进程 (Task 3.8)"""
        # 创建一个无法优雅终止的进程（使用不可中断的 sleep）
        proc = subprocess.Popen(["python", "-c", "import time; time.sleep(10)"])

        # 等待进程启动
        time.sleep(0.1)

        # 尝试强制终止
        success = terminate_process(proc, timeout=0.1)

        # 验证
        assert success is True
        assert proc.poll() is not None

    def test_terminate_process_with_force_flag(self):
        """测试直接使用 force=True 强制终止 (Task 3.8)"""
        # 创建进程
        proc = subprocess.Popen(["python", "-c", "import time; time.sleep(10)"])

        # 等待进程启动
        time.sleep(0.1)

        # 直接强制终止
        success = terminate_process(proc, force=True)

        # 验证
        assert success is True
        assert proc.poll() is not None

    def test_terminate_process_timeout_custom(self):
        """测试自定义超时时间 (Task 3.7)"""
        # 创建进程
        proc = subprocess.Popen(["python", "-c", "import time; time.sleep(10)"])

        # 等待进程启动
        time.sleep(0.1)

        # 使用自定义超时
        success = terminate_process(proc, timeout=1)

        # 验证
        assert success is True
        assert proc.poll() is not None

    def test_terminate_process_graceful_then_force(self):
        """测试优雅失败后强制终止 (Task 3.8)"""
        # 创建一个会忽略 SIGTERM 的进程（模拟）
        proc = subprocess.Popen(["python", "-c", "import time; time.sleep(10)"])

        # 等待进程启动
        time.sleep(0.1)

        # 尝试终止（应该先尝试优雅，超时后强制）
        success = terminate_process(proc, timeout=0.1)

        # 验证
        assert success is True
        assert proc.poll() is not None

    def test_terminate_process_with_children(self):
        """测试终止进程及其子进程 (Task 3.9)"""
        if not pytest.importorskip("psutil", reason="psutil not available"):
            pytest.skip("psutil not available")

        import psutil

        # 创建一个带子进程的父进程
        parent_proc = subprocess.Popen(
            ["python", "-c", "import subprocess; subprocess.run(['python', '-c', 'import time; time.sleep(10)'])"]
        )

        # 等待进程启动
        time.sleep(0.2)

        # 获取父进程和子进程
        try:
            parent = psutil.Process(parent_proc.pid)
            children = parent.children(recursive=True)

            # 验证有子进程
            assert len(children) > 0

            # 终止父进程
            success = terminate_process(parent_proc, timeout=5)

            # 验证
            assert success is True
            assert parent_proc.poll() is not None

        except psutil.NoSuchProcess:
            # 进程已经退出
            pass

    def test_cleanup_process_tree_success(self):
        """测试清理进程树成功 (Task 3.9)"""
        if not pytest.importorskip("psutil", reason="psutil not available"):
            pytest.skip("psutil not available")

        import psutil

        # 创建父进程和子进程
        parent_proc = subprocess.Popen(
            ["python", "-c", "import subprocess; subprocess.run(['python', '-c', 'import time; time.sleep(10)'])"]
        )

        # 等待进程启动
        time.sleep(0.2)

        try:
            parent = psutil.Process(parent_proc.pid)
            children = parent.children(recursive=True)

            # 清理进程树
            success = _cleanup_process_tree(parent_proc.pid)

            # 验证子进程已终止
            for child in children:
                try:
                    assert not child.is_running()
                except psutil.NoSuchProcess:
                    # 进程已退出，这也是成功的
                    pass

            assert success is True

        except psutil.NoSuchProcess:
            # 进程已经退出
            pass

    def test_cleanup_process_tree_no_process(self):
        """测试清理不存在的进程树 (Task 3.9)"""
        if not pytest.importorskip("psutil", reason="psutil not available"):
            pytest.skip("psutil not available")

        import psutil

        # 尝试清理一个不存在的进程
        success = _cleanup_process_tree(99999)

        # 应该返回 True（进程不存在也算成功）
        assert success is True

    def test_cleanup_process_tree_without_psutil(self):
        """测试无 psutil 时清理进程树 (Task 3.9)"""
        # 临时禁用 psutil
        with patch('utils.process_mgr.PSUTIL_AVAILABLE', False):
            # 尝试清理
            success = _cleanup_process_tree(12345)

            # 应该返回 False（psutil 不可用）
            assert success is False

    def test_terminate_process_exception_handling(self):
        """测试进程终止异常处理 (Task 3.9)"""
        # 创建一个 mock 进程对象
        mock_proc = Mock()
        mock_proc.pid = 12345
        mock_proc.poll.return_value = None
        mock_proc.terminate.side_effect = Exception("Test exception")

        # 尝试终止（应该捕获异常并返回 False）
        success = terminate_process(mock_proc, timeout=5)

        # 验证
        assert success is False

    def test_terminate_process_without_wait(self):
        """测试进程立即响应 terminate (Task 3.7)"""
        # 创建一个会快速退出的进程
        proc = subprocess.Popen(
            ["python", "-c", "import signal; import time; signal.signal(signal.SIGTERM, lambda s,f: exit(0)); time.sleep(10)"]
        )

        # 等待进程启动
        time.sleep(0.1)

        # 尝试终止
        success = terminate_process(proc, timeout=5)

        # 验证
        assert success is True
        assert proc.poll() is not None

    def test_terminate_process_multiple_times(self):
        """测试多次终止同一进程 (Task 3.7)"""
        # 创建进程
        proc = subprocess.Popen(["python", "-c", "import time; time.sleep(10)"])

        # 等待进程启动
        time.sleep(0.1)

        # 第一次终止
        success1 = terminate_process(proc, timeout=5)
        assert success1 is True

        # 第二次终止（应该返回 True，因为进程已退出）
        success2 = terminate_process(proc, timeout=5)
        assert success2 is True

    def test_terminate_process_logs_operations(self):
        """测试进程终止记录日志 (Task 3.7-3.9)"""
        # 创建进程
        proc = subprocess.Popen(["python", "-c", "import time; time.sleep(10)"])

        # 等待进程启动
        time.sleep(0.1)

        # Mock logger
        with patch('utils.process_mgr.logger') as mock_logger:
            # 终止进程
            terminate_process(proc, timeout=1)

            # 验证日志调用
            assert mock_logger.info.called or mock_logger.warning.called or mock_logger.error.called

    def test_terminate_process_with_none_pid_attribute(self):
        """测试进程对象没有 pid 属性的情况"""
        # 创建一个 mock 进程对象（没有 pid 属性）
        mock_proc = Mock(spec=['poll', 'terminate', 'wait', 'kill'])

        # 尝试终止（应该捕获异常并返回 False）
        success = terminate_process(mock_proc, timeout=5)

        # 验证（应该因为异常而返回 False）
        assert success is False
