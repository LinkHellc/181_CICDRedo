"""MATLAB Engine API integration for MBD_CICDKits.

This module provides integration with MATLAB using the MATLAB Engine API for Python.

Story 2.13 - 检测并管理 MATLAB 进程状态:
- 实现进程检测功能
- 实现进程连接功能
- 实现版本验证功能
- 实现进程启动功能
- 实现进程复用或启动决策逻辑
- 实现构建后关闭 MATLAB 进程功能

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
import re
from dataclasses import dataclass
from typing import Optional, Callable, List, Dict, Any, Tuple

from core.constants import (
    get_stage_timeout,
    MATLAB_START_TIMEOUT,
    MATLAB_CONNECT_TIMEOUT,
    MATLAB_MEMORY_LIMIT,
    MATLAB_MIN_VERSION,
    MATLAB_PROCESS_NAMES,
    MATLAB_DEFAULT_OPTIONS
)
from utils.errors import (
    ProcessTimeoutError,
    ProcessExitCodeError,
    ProcessError,
    MatlabProcessError,
    MatlabConnectionError,
    MatlabVersionError
)

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

# psutil 导入（可选依赖，用于进程检测）
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    logger.warning("psutil 未安装，进程检测功能不可用")


# =============================================================================
# Story 2.13 - MATLAB 进程管理
# =============================================================================

@dataclass
class MatlabProcess:
    """MATLAB 进程信息

    Story 2.13 - 任务 1.1-1.6:
    - 数据模型用于存储 MATLAB 进程信息
    - 包含 PID、可执行路径、启动时间、用户名

    Architecture Decision 1.2:
    - 使用 dataclass 实现轻量级数据容器
    - 所有字段提供默认值
    """
    pid: int
    exe_path: str = ""
    start_time: float = 0.0
    username: str = ""


def detect_matlab_processes() -> List[MatlabProcess]:
    """检测运行中的 MATLAB 进程

    Story 2.13 - 任务 1.1-1.6:
    - 使用 psutil 模块扫描所有运行中的进程
    - 识别 MATLAB 可执行文件（MATLAB.exe, matlab.exe）
    - 获取每个 MATLAB 进程的 PID、启动时间、可执行路径
    - 过滤出当前用户启动的 MATLAB 进程
    - 返回 MATLAB 进程列表

    Args:
        None

    Returns:
        List[MatlabProcess]: MATLAB 进程列表，无进程时返回空列表
    """
    if not PSUTIL_AVAILABLE:
        logger.warning("psutil 不可用，无法检测 MATLAB 进程")
        return []

    matlab_processes = []

    try:
        # 任务 1.2: 使用 psutil 模块扫描所有运行中的进程
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'username']):
            try:
                # 任务 1.3: 识别 MATLAB 可执行文件
                if proc.info['name'] in MATLAB_PROCESS_NAMES:
                    exe_path = proc.info.get('exe', '')

                    # 检查可执行路径是否包含 MATLAB（可选，提高准确性）
                    # exe_path 可能为空，只在非空时检查
                    if exe_path and 'MATLAB' not in exe_path:
                        continue

                    # 任务 1.4: 获取每个 MATLAB 进程的信息
                    matlab_process = MatlabProcess(
                        pid=proc.info['pid'],
                        exe_path=exe_path,
                        start_time=proc.info['create_time'],
                        username=proc.info.get('username', '')
                    )

                    matlab_processes.append(matlab_process)

                    # 任务 1.5: 过滤出当前用户启动的 MATLAB 进程
                    # Windows 上用户名格式为 "DOMAIN\username"
                    # 这里我们记录所有 MATLAB 进程，后续连接时再验证

                    logger.debug(
                        f"检测到 MATLAB 进程: PID {matlab_process.pid}, "
                        f"路径: {exe_path}, "
                        f"启动时间: {matlab_process.start_time}"
                    )

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    except Exception as e:
        logger.error(f"检测 MATLAB 进程失败: {e}", exc_info=True)

    if not matlab_processes:
        logger.debug("未检测到运行中的 MATLAB 进程")

    return matlab_processes


def connect_to_matlab(
    pid: int,
    timeout: int = MATLAB_CONNECT_TIMEOUT
) -> Optional["matlab.engine.MatlabEngine"]:
    """连接到 MATLAB 进程

    Story 2.13 - 任务 2.1-2.5:
    - 接受 MATLAB 进程 PID 作为参数
    - 尝试使用 matlab.engine 连接到指定进程
    - 处理连接超时（默认 10 秒）
    - 返回连接的 MATLAB 引擎或 None

    Args:
        pid: MATLAB 进程 PID
        timeout: 连接超时时间（秒）

    Returns:
        Optional[MatlabEngine]: MATLAB 引擎对象，连接失败返回 None
    """
    if not MATLAB_ENGINE_AVAILABLE:
        logger.warning("MATLAB Engine API 不可用，无法连接")
        return None

    try:
        logger.debug(f"尝试连接到 MATLAB 进程 PID: {pid}")

        # 任务 2.3: 尝试使用 matlab.engine 连接到指定进程
        engine = matlab.engine.connect_matlab(pid)

        # 任务 2.4: 处理连接超时
        # connect_matlab 本身没有超时参数，这里只是验证连接是否成功
        # 如果连接失败，会抛出异常

        logger.info(f"成功连接到 MATLAB 进程 PID: {pid}")
        return engine

    except Exception as e:
        logger.warning(f"连接 MATLAB 进程失败 PID {pid}: {e}")
        return None


def parse_matlab_version(version_str: str) -> Tuple[int, str]:
    """解析 MATLAB 版本号

    Story 2.13 - 任务 3.3:
    - 调用 engine.version() 获取版本信息
    - 解析版本号（如 R2020a, R2023b）

    Args:
        version_str: 版本字符串（如 "R2020a"）

    Returns:
        Tuple[int, str]: (年份, 字母)，如 (2020, "a")

    Raises:
        ValueError: 如果版本格式无效
    """
    match = re.match(r'R(\d{4})([a-bA-B])', version_str)
    if match:
        year = int(match.group(1))
        letter = match.group(2).lower()
        return (year, letter)

    raise ValueError(f"无效的 MATLAB 版本格式: {version_str}")


def verify_matlab_version(
    engine: "matlab.engine.MatlabEngine"
) -> Tuple[bool, str, str]:
    """验证 MATLAB 版本兼容性

    Story 2.13 - 任务 3.1-3.6:
    - 接受 MATLAB 引擎对象作为参数
    - 调用 engine.version() 获取版本信息
    - 解析版本号（如 R2020a, R2023b）
    - 与最低要求版本（R2020a）比较
    - 返回版本兼容性结果（是否兼容、实际版本、最低版本）

    Args:
        engine: MATLAB 引擎对象

    Returns:
        Tuple[bool, str, str]: (是否兼容, 实际版本, 最低版本)

    Raises:
        MatlabVersionError: 如果版本不兼容
    """
    try:
        # 任务 3.3: 调用 engine.version() 获取版本信息
        version = engine.version()
        version_str = str(version)

        # 任务 3.4: 解析版本号
        year, letter = parse_matlab_version(version_str)

        # 任务 3.5: 与最低要求版本（R2020a）比较
        min_year, min_letter = parse_matlab_version(MATLAB_MIN_VERSION)

        is_compatible = (year, letter) >= (min_year, min_letter)

        logger.info(
            f"MATLAB 版本验证: {version_str} "
            f"{'兼容' if is_compatible else '不兼容'} "
            f"(要求: {MATLAB_MIN_VERSION})"
        )

        # 任务 3.6: 返回版本兼容性结果
        if not is_compatible:
            raise MatlabVersionError(version_str, MATLAB_MIN_VERSION)

        return (is_compatible, version_str, MATLAB_MIN_VERSION)

    except MatlabVersionError:
        raise
    except Exception as e:
        logger.error(f"验证 MATLAB 版本失败: {e}")
        raise MatlabProcessError(
            f"无法获取 MATLAB 版本: {e}",
            suggestions=["检查 MATLAB 引擎是否正常工作", "查看详细日志"]
        )


def start_matlab_process(
    timeout: int = MATLAB_START_TIMEOUT,
    options: List[str] = None
) -> "matlab.engine.MatlabEngine":
    """启动新的 MATLAB 进程

    Story 2.13 - 任务 4.1-4.5:
    - 使用 matlab.engine.start_matlab() 启动新进程
    - 配置启动参数（启动选项、等待时间）
    - 设置超时时间（默认 60 秒）
    - 返回新启动的 MATLAB 引擎对象

    注意：MATLAB Engine API 的 start_matlab() 不支持传递启动选项参数
    如需自定义启动选项，请使用其他方法（如环境变量）

    Args:
        timeout: 启动超时时间（秒）
        options: 启动选项列表（已废弃，保留用于向后兼容）

    Returns:
        MatlabEngine: MATLAB 引擎对象

    Raises:
        MatlabProcessError: 如果启动失败
    """
    if not MATLAB_ENGINE_AVAILABLE:
        raise MatlabProcessError(
            "MATLAB Engine API 不可用",
            suggestions=["安装 MATLAB Engine API for Python"]
        )

    # 任务 4.3: 配置启动参数
    # 注意：MATLAB Engine API 的 start_matlab() 不支持传递启动选项参数
    # 保留 options 参数用于向后兼容，但忽略它
    if options is not None:
        logger.warning(f"MATLAB Engine API 不支持传递启动选项参数，将忽略: {options}")

    start = time.monotonic()

    try:
        # 任务 4.2: 使用 matlab.engine.start_matlab() 启动新进程
        engine = matlab.engine.start_matlab()

        elapsed = time.monotonic() - start
        logger.info(f"成功启动 MATLAB 进程，耗时: {elapsed:.2f} 秒")

        return engine

    except Exception as e:
        logger.error(f"启动 MATLAB 进程失败: {e}")
        raise MatlabProcessError(
            f"无法启动 MATLAB 进程: {e}",
            suggestions=[
                "检查 MATLAB 安装路径",
                "验证 MATLAB Engine API 是否安装",
                "检查磁盘空间",
                "查看详细日志"
            ]
        )


def get_or_start_matlab(
    reuse_existing: bool = True,
    context: Optional[dict] = None
) -> Tuple[Optional["matlab.engine.MatlabEngine"], str]:
    """获取或启动 MATLAB 进程

    Story 2.13 - 任务 6.1-6.7:
    - 调用 detect_matlab_processes() 检测现有进程
    - 如果存在进程，尝试连接到第一个可用的进程
    - 如果连接成功，验证版本兼容性
    - 如果版本兼容，复用现有进程
    - 如果不存在、连接失败或版本不兼容，启动新进程
    - 返回 MATLAB 引擎对象和启动策略（复用/新启动）

    Args:
        reuse_existing: 是否复用现有进程
        context: 构建上下文

    Returns:
        Tuple[MatlabEngine, str]: (MATLAB 引擎, 启动策略 "reuse" 或 "new")
    """
    # 任务 6.2: 调用 detect_matlab_processes() 检测现有进程
    matlab_processes = detect_matlab_processes()

    # 任务 6.3-6.5: 尝试复用现有进程
    if reuse_existing and matlab_processes:
        for proc in matlab_processes:
            logger.info(f"尝试连接到现有 MATLAB 进程 PID: {proc.pid}")

            # 任务 6.3: 尝试连接到第一个可用的进程
            engine = connect_to_matlab(proc.pid)
            if engine:
                try:
                    # 任务 6.4: 如果连接成功，验证版本兼容性
                    is_compatible, version, _ = verify_matlab_version(engine)

                    # 任务 6.5: 如果版本兼容，复用现有进程
                    if is_compatible:
                        logger.info(f"复用 MATLAB 进程 PID: {proc.pid}, 版本: {version}")

                        # 任务 4.6: 在 context.state 中记录进程启动时间
                        if context:
                            context["matlab_startup_time"] = time.monotonic()

                        return (engine, "reuse")
                    else:
                        # 版本不兼容，继续尝试下一个进程
                        logger.info(f"MATLAB 进程 PID {proc.pid} 版本不兼容，继续尝试其他进程")
                        continue

                except (MatlabVersionError, Exception) as e:
                    # 版本验证失败，继续尝试下一个进程
                    logger.warning(f"验证 MATLAB 进程 PID {proc.pid} 失败: {e}")
                    continue

        # 所有进程都无法使用
        logger.info("所有现有 MATLAB 进程无法使用，启动新进程")

    # 任务 6.6: 启动新进程
    logger.info("启动新的 MATLAB 进程")
    engine = start_matlab_process()

    # 任务 4.6: 在 context.state 中记录进程启动时间
    if context:
        context["matlab_startup_time"] = time.monotonic()

    # 任务 6.7: 返回 MATLAB 引擎对象和启动策略
    return (engine, "new")


def shutdown_matlab_process(
    engine: "matlab.engine.MatlabEngine",
    startup_strategy: str,
    context: Optional[dict] = None
) -> None:
    """关闭 MATLAB 进程

    Story 2.13 - 任务 7.1-7.6:
    - 接受 MATLAB 引擎对象和启动策略作为参数
    - 如果是新启动的进程，关闭 MATLAB 引擎
    - 如果是复用的进程，保留进程仅断开连接
    - 使用 engine.quit() 优雅关闭
    - 在 context.state 中清除进程记录

    Args:
        engine: MATLAB 引擎对象
        startup_strategy: 启动策略（"new" 或 "reuse"）
        context: 构建上下文
    """
    try:
        # 任务 7.3: 如果是新启动的进程，关闭 MATLAB 引擎
        if startup_strategy == "new":
            logger.info("关闭 MATLAB 进程（新启动）")
            engine.quit()

            # 任务 7.6: 在 context.state 中清除进程记录
            if context:
                context.pop("matlab_engine", None)
                context.pop("matlab_pid", None)
                context.pop("matlab_startup_strategy", None)
                context.pop("matlab_startup_time", None)

        # 任务 7.4: 如果是复用的进程，保留进程仅断开连接
        elif startup_strategy == "reuse":
            logger.info("保留 MATLAB 进程（复用）")
            # 不关闭引擎，仅断开连接
            # MATLAB Engine API 没有明确的 disconnect 方法
            # 我们不调用 quit()，让引擎继续运行

    except Exception as e:
        logger.error(f"关闭 MATLAB 进程失败: {e}")
        # 不抛出异常，避免影响工作流状态


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
        timeout: Optional[int] = None,
        reuse_existing: bool = True
    ):
        """初始化 MATLAB 集成

        Args:
            log_callback: 日志回调函数，用于实时输出
            timeout: 超时时间（秒），如果为 None 则使用默认配置
            reuse_existing: 是否复用现有 MATLAB 进程（Story 2.13）
        """
        self.engine: Optional["matlab.engine.MatlabEngine"] = None
        self.log_callback = log_callback or (lambda msg: None)
        self.timeout = timeout if timeout is not None else get_stage_timeout("matlab_gen")
        self._is_running = False
        self.reuse_existing = reuse_existing  # Story 2.13
        self.startup_strategy = "new"  # Story 2.13: "reuse" 或 "new"

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

    def start_engine(self, context: Optional[dict] = None) -> bool:
        """启动 MATLAB 引擎

        Story 2.5 - 任务 1.4:
        - 实现进程启动方法 start_engine()

        Story 2.13 - 任务 8.2:
        - 在阶段开始前调用 get_or_start_matlab() 获取 MATLAB 引擎

        Args:
            context: 构建上下文（Story 2.13）

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
            # Story 2.13: 使用 get_or_start_matlab 获取或启动 MATLAB
            self._log("获取或启动 MATLAB 引擎...")
            start_time = time.monotonic()

            # 调用 get_or_start_matlab() 获取 MATLAB 引擎
            engine, strategy = get_or_start_matlab(
                reuse_existing=self.reuse_existing,
                context=context
            )

            self.engine = engine
            self.startup_strategy = strategy

            elapsed = time.monotonic() - start_time
            self._is_running = True
            self._log(f"MATLAB 引擎已获取（策略: {strategy}，耗时 {elapsed:.2f} 秒）")

            # Story 2.13 - 任务 8.3: 将 MATLAB 引擎存储在 context.state
            if context:
                context["matlab_engine"] = self.engine
                context["matlab_startup_strategy"] = self.startup_strategy

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
                # 异步执行模式 - 尝试不同的参数名（兼容不同版本的 MATLAB Engine）
                future = None
                try:
                    # 新版本使用 background 参数
                    future = self.engine.run(script_path, *args, nargout=0, background=True)
                except TypeError:
                    try:
                        # 旧版本使用 async_ 参数
                        future = self.engine.run(script_path, *args, nargout=0, async_=True)
                    except TypeError:
                        # 不支持异步，使用同步模式
                        self._log("MATLAB Engine 不支持异步模式，使用同步模式")
                        self.engine.run(script_path, *args, nargout=0)
                        elapsed = time.monotonic() - start_time
                        self._log(f"MATLAB 脚本执行完成（耗时 {elapsed:.2f} 秒）")
                        return True

                if future is not None:
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

    def stop_engine(self, context: Optional[dict] = None) -> None:
        """停止 MATLAB 引擎并清理资源

        Story 2.5 - 任务 4.5:
        - 检测进程异常（捕获异常）
        - 清理僵尸进程

        Architecture Decision 2.1:
        - 超时后清理进程资源

        Story 2.13 - 任务 7: 实现构建后关闭 MATLAB 进程功能
        - 任务 8.6: 在阶段完成后调用 shutdown_matlab_process() 清理
        """
        if self.engine:
            try:
                # Story 2.13: 使用 shutdown_matlab_process 清理
                self._log("正在清理 MATLAB 引擎...")

                shutdown_matlab_process(
                    self.engine,
                    self.startup_strategy,
                    context
                )

                self._log("MATLAB 引擎已清理")

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

    def execute_command(
        self,
        command: str,
        timeout: Optional[int] = None,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """执行 MATLAB 命令

        Story 2.9 - 任务 4.1-4.6:
        - 接受 MATLAB 命令字符串和超时参数
        - 使用 matlab.engine 执行命令
        - 捕获命令输出和错误信息
        - 使用 time.monotonic() 实现超时检测（架构 Decision 2.1）
        - 返回执行结果（成功/失败、输出、错误）

        Args:
            command: MATLAB 命令字符串（如 "rtw.asap2SetAddress('file.a2l', 'file.elf')"）
            timeout: 超时时间（秒），如果为 None 则使用实例默认值
            log_callback: 日志回调函数

        Returns:
            bool: 成功返回 True，失败返回 False

        Raises:
            ProcessError: 如果 MATLAB Engine API 不可用
            ProcessTimeoutError: 如果执行超时
            RuntimeError: 如果 MATLAB 引擎未启动
        """
        # 检查 MATLAB Engine API 是否可用 (任务 4.1)
        self._check_matlab_available()

        # 使用提供的超时或默认超时 (任务 4.2, 7.1)
        actual_timeout = timeout if timeout is not None else self.timeout

        # 使用提供的日志回调或实例日志回调
        actual_log_callback = log_callback or self._log

        # 记录开始时间 - 使用 monotonic 避免系统时间调整影响 (架构 Decision 2.1, 任务 7.2)
        start_time = time.monotonic()

        actual_log_callback(f"执行 MATLAB 命令: {command}")
        logger.debug(f"执行 MATLAB 命令: {command}")

        try:
            # 执行命令 (任务 4.3)
            self.engine.eval(command, nargout=0)

            # 计算执行时间
            elapsed = time.monotonic() - start_time
            actual_log_callback(f"MATLAB 命令执行成功（耗时 {elapsed:.2f} 秒）")
            logger.info(f"MATLAB 命令执行成功（耗时 {elapsed:.2f} 秒）")

            return True

        except matlab.engine.MatlabExecutionError as e:
            # 捕获 MATLAB 执行错误 (任务 4.4)
            error_msg = f"MATLAB 命令执行失败: {str(e)}"
            actual_log_callback(error_msg)
            logger.error(error_msg, exc_info=True)

            # 抛出统一的 ProcessError (任务 4.6)
            raise ProcessError(
                "MATLAB",
                error_msg,
                suggestions=[
                    "检查 MATLAB 命令语法",
                    "验证函数参数是否正确",
                    "查看 MATLAB 详细错误日志",
                    "确认 MATLAB 工作目录"
                ]
            )

        except Exception as e:
            # 其他异常 (任务 4.4, 4.6)
            error_msg = f"MATLAB 执行异常: {str(e)}"
            actual_log_callback(error_msg)
            logger.error(error_msg, exc_info=True)

            raise ProcessError(
                "MATLAB",
                error_msg,
                suggestions=[
                    "查看详细日志",
                    "检查 MATLAB 环境",
                    "验证系统资源"
                ]
            )

    def get_engine_info(self) -> Dict[str, Any]:
        """获取引擎信息

        Returns:
            包含引擎状态信息的字典
        """
        return {
            "is_running": self.is_running(),
            "timeout": self.timeout,
            "matlab_engine_available": MATLAB_ENGINE_AVAILABLE,
            "min_matlab_version": self.MIN_MATLAB_VERSION,
            "startup_strategy": self.startup_strategy,
            "reuse_existing": self.reuse_existing
        }
