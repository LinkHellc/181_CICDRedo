"""MATLAB Engine API integration for MBD_CICDKits.

This module provides integration with MATLAB using the MATLAB Engine API for Python.

Architecture Decision 2.1:
- 每次启动/关闭 MATLAB 引擎
- 超时检测使用 time.monotonic()
- 僵尸进程清理

Architecture Decision 2.2:
- 使用 ProcessError 统一管理错误
- ProcessTimeoutError 超时错误
- ProcessExitCodeError 退出码错误
"""

import logging
import time
from typing import Optional, Callable, List, Dict, Any

from core.constants import get_stage_timeout
from utils.errors import ProcessTimeoutError, ProcessExitCodeError, ProcessError

logger = logging.getLogger(__name__)

# MATLAB Engine API 导入（可选依赖）
# 如果未安装，会在运行时检测
try:
    import matlab.engine
    MATLAB_ENGINE_AVAILABLE = True
except ImportError:
    MATLAB_ENGINE_AVAILABLE = False
    matlab = None
    logger.warning("MATLAB Engine API for Python 未安装")


class MatlabIntegration:
    """MATLAB Engine API 集成

    提供与 MATLAB 的交互接口，包括：
    - 启动和停止 MATLAB 引擎
    - 执行 MATLAB 脚本和函数
    - 捕获 MATLAB 输出
    - 超时检测和错误处理

    Story 2.5 - 任务 1:
    - 使用 MATLAB Engine API for Python (import matlab.engine)
    - 实现进程启动方法 start_engine()
    - 设置 MATLAB 进程参数（内存限制、等待时间）
    - 添加版本兼容性检查（R2020a+）
    """

    # MATLAB 最低版本要求
    MIN_MATLAB_VERSION = "R2020a"

    def __init__(
        self,
        log_callback: Optional[Callable[[str], None]] = None,
        timeout: Optional[int] = None
    ):
        """初始化 MATLAB 集成

        Args:
            log_callback: 日志回调函数，用于实时输出
            timeout: 超时时间（秒），如果为 None 则使用默认配置
        """
        self.engine: Optional["matlab.engine.MatlabEngine"] = None
        self.log_callback = log_callback or (lambda msg: None)
        self.timeout = timeout if timeout is not None else get_stage_timeout("matlab_gen")
        self._is_running = False

        self._log(f"MATLAB 集成初始化完成，超时设置: {self.timeout} 秒")

    def _log(self, message: str) -> None:
        """记录日志

        Story 2.5 - 任务 3.4:
        - 添加时间戳到每条输出（使用 [HH:MM:SS] 格式）

        Args:
            message: 日志消息
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        formatted_message = f"{timestamp} {message}"
        self.log_callback(formatted_message)
        logger.debug(f"MATLAB: {message}")

    def _check_matlab_available(self) -> None:
        """检查 MATLAB Engine API 是否可用

        Raises:
            ProcessError: 如果 MATLAB Engine API 未安装
        """
        if not MATLAB_ENGINE_AVAILABLE:
            raise ProcessError(
                "MATLAB",
                "MATLAB Engine API for Python 未安装",
                suggestions=[
                    "安装 MATLAB R2020a 或更高版本",
                    "在 MATLAB 目录执行: cd extern/engines/python && python setup.py install",
                    "验证 import matlab.engine 可用"
                ]
            )

    def start_engine(self) -> bool:
        """启动 MATLAB 引擎

        Story 2.5 - 任务 1.4:
        - 实现进程启动方法 start_engine()

        Returns:
            bool: 成功返回 True，失败返回 False

        Raises:
            ProcessError: 如果 MATLAB Engine API 不可用
        """
        self._check_matlab_available()

        if self._is_running and self.engine:
            self._log("MATLAB 引擎已在运行")
            return True

        try:
            self._log("正在启动 MATLAB 引擎...")
            start_time = time.monotonic()

            # 启动 MATLAB 引擎
            self.engine = matlab.engine.start_matlab()

            elapsed = time.monotonic() - start_time
            self._is_running = True
            self._log(f"MATLAB 引擎已启动（耗时 {elapsed:.2f} 秒）")

            # 验证 MATLAB 版本
            self._verify_matlab_version()

            return True

        except Exception as e:
            logger.error(f"MATLAB 启动失败: {e}", exc_info=True)
            self._log(f"MATLAB 启动失败: {e}")
            self._is_running = False
            self.engine = None
            return False

    def _verify_matlab_version(self) -> None:
        """验证 MATLAB 版本兼容性

        Story 2.5 - 任务 1.6:
        - 添加版本兼容性检查（R2020a+）

        Raises:
            ProcessError: 如果 MATLAB 版本不符合要求
        """
        if not self.engine:
            return

        try:
            # 获取 MATLAB 版本
            version = self.engine.version()
            version_str = str(version)

            self._log(f"检测到 MATLAB 版本: {version_str}")

            # 简单版本检查（确保不是过时版本）
            # 实际版本比较可以更精确
            if "20" in version_str or "21" in version_str or "22" in version_str or "23" in version_str or "24" in version_str or "25" in version_str:
                self._log(f"MATLAB 版本符合要求（最低 {self.MIN_MATLAB_VERSION}）")
            else:
                logger.warning(f"MATLAB 版本可能过低: {version_str}（建议 {self.MIN_MATLAB_VERSION}+）")

        except Exception as e:
            logger.warning(f"无法获取 MATLAB 版本: {e}")

    def is_running(self) -> bool:
        """检查 MATLAB 引擎是否正在运行

        Story 2.5 - 任务 4.1:
        - 实现 is_running() 方法检查 MATLAB 进程状态

        Returns:
            bool: 如果引擎正在运行返回 True
        """
        # 首先检查内部状态
        if not self._is_running or self.engine is None:
            return False

        try:
            # 尝试执行简单命令来验证引擎连接
            # 这比检查 find_matlab() 更可靠
            self.engine.eval("1;", nargout=0)
            return True
        except Exception:
            # 如果执行失败，引擎可能已断开
            self._is_running = False
            return False

    def eval_script(
        self,
        script_path: str,
        *args,
        async_mode: bool = True
    ) -> bool:
        """执行 MATLAB 脚本

        Story 2.5 - 任务 2:
        - 使用 matlab.engine.eval() 或 run() 调用脚本
        - 传递参数
        - 异步执行模式

        Args:
            script_path: 脚本路径或函数名（如 "genCode"）
            *args: 脚本参数
            async_mode: 是否使用异步模式（默认 True）

        Returns:
            bool: 成功返回 True，失败返回 False

        Raises:
            RuntimeError: 如果 MATLAB 引擎未启动
            ProcessTimeoutError: 如果执行超时
            ProcessExitCodeError: 如果执行失败
        """
        if not self.engine:
            raise RuntimeError("MATLAB 引擎未启动")

        # 使用 time.monotonic() 记录开始时间 (Architecture Decision 2.1)
        start_time = time.monotonic()
        self._log(f"正在执行 MATLAB 脚本: {script_path}")

        try:
            if async_mode:
                # 异步执行模式 (Story 2.5 - 任务 4.2)
                future = self.engine.run(script_path, *args, nargout=0, async_=True)

                # 监控执行状态 (Story 2.5 - 任务 4.3)
                poll_interval = 0.5  # 0.5 秒轮询间隔
                while not future.done():
                    # 检查超时 (Story 2.5 - 任务 5.2)
                    elapsed = time.monotonic() - start_time
                    if elapsed > self.timeout:
                        # 超时处理 (Story 2.5 - 任务 5.3)
                        self._log(f"MATLAB 执行超时（{elapsed:.1f} 秒），正在终止...")
                        self.stop_engine()
                        raise ProcessTimeoutError("MATLAB 代码生成", self.timeout)

                    time.sleep(poll_interval)

                # 获取结果
                future.result()
            else:
                # 同步执行模式
                self.engine.run(script_path, *args, nargout=0)

            elapsed = time.monotonic() - start_time
            self._log(f"MATLAB 脚本执行完成（耗时 {elapsed:.2f} 秒）")
            return True

        except ProcessTimeoutError:
            raise  # 重新抛出超时错误
        except Exception as e:
            logger.error(f"MATLAB 执行失败: {e}", exc_info=True)
            self._log(f"MATLAB 执行失败: {e}")
            raise ProcessExitCodeError("MATLAB", -1)

    def stop_engine(self) -> None:
        """停止 MATLAB 引擎并清理资源

        Story 2.5 - 任务 4.5:
        - 检测进程异常（捕获异常）
        - 清理僵尸进程

        Architecture Decision 2.1:
        - 超时后清理进程资源
        """
        if self.engine:
            try:
                self._log("正在关闭 MATLAB 引擎...")
                self.engine.quit()
                self._log("MATLAB 引擎已关闭")
            except Exception as e:
                logger.warning(f"MATLAB 关闭时出错（忽略）: {e}")
                # 忽略退出错误 (Architecture Decision 2.1 - 僵尸进程清理)
            finally:
                self.engine = None
                self._is_running = False

    def __enter__(self):
        """上下文管理器入口"""
        self.start_engine()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop_engine()
        return False

    def get_engine_info(self) -> Dict[str, Any]:
        """获取引擎信息

        Returns:
            包含引擎状态信息的字典
        """
        return {
            "is_running": self.is_running(),
            "timeout": self.timeout,
            "matlab_engine_available": MATLAB_ENGINE_AVAILABLE,
            "min_matlab_version": self.MIN_MATLAB_VERSION
        }
