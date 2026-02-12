"""Unit tests for MatlabIntegration class.

Story 2.5 - 单元测试要求:
- 测试 MATLAB 进程启动和关闭
- 测试 genCode.m 脚本调用（使用 mock）
- 测试超时检测逻辑
- 测试输出捕获和回调
- 测试错误处理和恢复建议
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path

from integrations.matlab import MatlabIntegration, MATLAB_ENGINE_AVAILABLE
from utils.errors import ProcessTimeoutError, ProcessExitCodeError, ProcessError
from core.constants import get_stage_timeout


class TestMatlabIntegration:
    """测试 MatlabIntegration 类"""

    @pytest.fixture
    def log_callback(self):
        """创建日志回调 fixture"""
        messages = []
        def callback(msg):
            messages.append(msg)
        return callback, messages

    @pytest.fixture
    def matlab(self, log_callback):
        """创建 MatlabIntegration 实例 fixture"""
        callback, _ = log_callback
        return MatlabIntegration(log_callback=callback, timeout=1800)

    def test_init(self, log_callback):
        """测试初始化 (Story 2.5 - 任务 1.2)"""
        callback, messages = log_callback
        matlab = MatlabIntegration(log_callback=callback, timeout=1800)

        assert matlab.engine is None
        assert matlab._is_running is False
        assert matlab.timeout == 1800
        assert matlab.log_callback == callback

    def test_init_default_timeout(self, log_callback):
        """测试默认超时值"""
        callback, _ = log_callback
        matlab = MatlabIntegration(log_callback=callback)

        expected_timeout = get_stage_timeout("matlab_gen")
        assert matlab.timeout == expected_timeout

    def test_check_matlab_available_not_installed(self, matlab):
        """测试 MATLAB Engine API 未安装时的检查"""
        with patch('integrations.matlab.MATLAB_ENGINE_AVAILABLE', False):
            with pytest.raises(ProcessError) as exc_info:
                matlab._check_matlab_available()

            assert "MATLAB Engine API for Python 未安装" in str(exc_info.value)
            assert len(exc_info.value.suggestions) > 0

    def test_start_engine_success(self, matlab, log_callback):
        """测试成功启动 MATLAB 引擎 (Story 2.5 - 任务 1.4)"""
        callback, messages = log_callback

        # Mock matlab.engine
        mock_engine = MagicMock()
        with patch('integrations.matlab.matlab') as mock_matlab:
            mock_matlab.engine.start_matlab.return_value = mock_engine
            mock_matlab.engine.find_matlab.return_value = ["engine_name"]

            result = matlab.start_engine()

            assert result is True
            assert matlab._is_running is True
            assert matlab.engine == mock_engine
            mock_matlab.engine.start_matlab.assert_called_once()

    def test_start_engine_failure(self, matlab, log_callback):
        """测试启动 MATLAB 引擎失败"""
        callback, messages = log_callback

        with patch('integrations.matlab.matlab') as mock_matlab:
            mock_matlab.engine.start_matlab.side_effect = Exception("启动失败")

            result = matlab.start_engine()

            assert result is False
            assert matlab._is_running is False
            assert matlab.engine is None
            assert any("启动失败" in msg for msg in messages)

    def test_is_running_true(self, matlab):
        """测试 is_running 返回 True (Story 2.5 - 任务 4.1)"""
        matlab._is_running = True
        matlab.engine = MagicMock()

        with patch('integrations.matlab.matlab.engine.find_matlab') as mock_find:
            mock_find.return_value = ["engine"]
            assert matlab.is_running() is True

    def test_is_running_false_no_engine(self, matlab):
        """测试 is_running 返回 False（无引擎）"""
        matlab._is_running = False
        matlab.engine = None

        assert matlab.is_running() is False

    def test_is_running_false_not_in_list(self, matlab):
        """测试 is_running 返回 False（引擎连接失败）"""
        matlab._is_running = True
        mock_engine = MagicMock()
        mock_engine.eval.side_effect = Exception("Connection lost")
        matlab.engine = mock_engine

        assert matlab.is_running() is False
        assert matlab._is_running is False  # 状态应该被更新

    def test_eval_script_async_success(self, matlab, log_callback):
        """测试异步执行脚本成功 (Story 2.5 - 任务 2.4, 4.2)"""
        callback, messages = log_callback

        mock_engine = MagicMock()
        matlab.engine = mock_engine
        matlab._is_running = True

        # 创建一个立即完成的 future
        mock_future = MagicMock()
        mock_future.done.return_value = True
        mock_engine.run.return_value = mock_future

        result = matlab.eval_script("genCode", "/path/to/model", async_mode=True)

        assert result is True
        mock_engine.run.assert_called_once_with("genCode", "/path/to/model", nargout=0, async_=True)

    def test_eval_script_timeout(self, matlab, log_callback):
        """测试执行超时 (Story 2.5 - 任务 5.2, 5.3)"""
        callback, messages = log_callback

        mock_engine = MagicMock()
        matlab.engine = mock_engine
        matlab._is_running = True
        matlab.timeout = 0.1  # 设置非常短的超时

        # 创建一个永不完成的 future
        mock_future = MagicMock()
        mock_future.done.return_value = False
        mock_engine.run.return_value = mock_future

        with patch('integrations.matlab.matlab.engine.find_matlab') as mock_find:
            mock_find.return_value = ["engine"]
            with pytest.raises(ProcessTimeoutError) as exc_info:
                matlab.eval_script("genCode", "/path/to/model", async_mode=True)

            assert "MATLAB 代码生成" in str(exc_info.value)
            assert exc_info.value.timeout == 0.1

    def test_eval_script_exception(self, matlab, log_callback):
        """测试执行脚本异常 (Story 2.5 - 任务 4.5)"""
        callback, messages = log_callback

        mock_engine = MagicMock()
        matlab.engine = mock_engine
        matlab._is_running = True

        mock_engine.run.side_effect = Exception("脚本执行失败")

        with pytest.raises(ProcessExitCodeError) as exc_info:
            matlab.eval_script("genCode", "/path/to/model", async_mode=True)

        assert "MATLAB" in str(exc_info.value)

    def test_eval_script_no_engine(self, matlab):
        """测试无引擎时执行脚本"""
        matlab.engine = None

        with pytest.raises(RuntimeError) as exc_info:
            matlab.eval_script("genCode", "/path/to/model")

        assert "MATLAB 引擎未启动" in str(exc_info.value)

    def test_stop_engine_success(self, matlab, log_callback):
        """测试成功停止引擎 (Story 2.5 - 任务 4.5)"""
        callback, messages = log_callback

        mock_engine = MagicMock()
        matlab.engine = mock_engine
        matlab._is_running = True

        matlab.stop_engine()

        assert matlab.engine is None
        assert matlab._is_running is False
        mock_engine.quit.assert_called_once()
        assert any("已关闭" in msg for msg in messages)

    def test_stop_engine_exception_ignored(self, matlab, log_callback):
        """测试停止引擎时忽略异常 (Architecture Decision 2.1)"""
        callback, messages = log_callback

        mock_engine = MagicMock()
        mock_engine.quit.side_effect = Exception("退出时出错")
        matlab.engine = mock_engine
        matlab._is_running = True

        # 不应抛出异常
        matlab.stop_engine()

        assert matlab.engine is None
        assert matlab._is_running is False

    def test_context_manager(self, matlab):
        """测试上下文管理器"""
        mock_engine = MagicMock()

        with patch('integrations.matlab.matlab') as mock_matlab:
            mock_matlab.engine.start_matlab.return_value = mock_engine
            mock_matlab.engine.find_matlab.return_value = ["engine"]

            with matlab as m:
                assert m == matlab
                assert matlab._is_running is True

            # 退出时应清理
            assert matlab._is_running is False

    def test_get_engine_info(self, matlab):
        """测试获取引擎信息"""
        info = matlab.get_engine_info()

        assert isinstance(info, dict)
        assert "is_running" in info
        assert "timeout" in info
        assert "matlab_engine_available" in info
        assert "min_matlab_version" in info
        assert info["timeout"] == 1800

    def test_verify_matlab_version_success(self, matlab, log_callback):
        """测试验证 MATLAB 版本成功 (Story 2.5 - 任务 1.6)"""
        callback, messages = log_callback

        mock_engine = MagicMock()
        mock_engine.version.return_value = "R2023a"
        matlab.engine = mock_engine

        matlab._verify_matlab_version()

        assert any("R2023a" in msg for msg in messages)

    @pytest.mark.skipif(not MATLAB_ENGINE_AVAILABLE, reason="MATLAB Engine API 不可用")
    def test_real_matlab_integration(self):
        """真实 MATLAB 集成测试（需要真实 MATLAB 环境）

        注意：此测试仅在 MATLAB Engine API 可用时运行
        """
        import matlab.engine

        matlab = MatlabIntegration()

        # 注意：如果真实环境不可用，此测试可能会失败
        # 这是一个端到端测试示例
        info = matlab.get_engine_info()
        assert info["matlab_engine_available"] is True
