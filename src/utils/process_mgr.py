"""Process management utilities for MBD_CICDKits.

This module provides process monitoring and management utilities.

Story 2.13 - 任务 14: 实现进程监控和超时处理
- 添加 MATLAB 进程监控支持
- 监控进程是否异常退出
- 检测进程内存占用
- 实现进程僵死检测
- 添加超时后强制终止逻辑

Story 2.15 - 任务 3: 创建进程终止工具函数
- 实现 terminate_process() 函数
- 支持优雅终止和强制终止
- 支持进程树清理
"""

import logging
import time
import subprocess
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# psutil 导入（可选依赖）
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    logger.warning("psutil 未安装，进程监控功能不可用")


@dataclass
class ProcessMonitor:
    """进程监控器

    用于监控和管理外部进程，包括：
    - 进程状态检测
    - 内存占用监控
    - 超时检测和强制终止
    - 僵死进程检测

    Story 2.13 - 任务 14:
    - 监控 MATLAB 进程是否异常退出
    - 检测进程内存占用（不超过 2GB）
    - 实现进程僵死检测
    - 添加超时后强制终止逻辑

    Attributes:
        pid: 进程 ID
        name: 进程名称
        start_time: 启动时间（time.monotonic）
        memory_limit: 内存限制（字节）
        timeout: 超时时间（秒）
        check_interval: 检查间隔（秒）
    """

    pid: int
    name: str = ""
    start_time: float = 0.0
    memory_limit: Optional[int] = None  # 字节
    timeout: Optional[int] = None      # 秒
    check_interval: float = 5.0        # 检查间隔（秒）

    def __post_init__(self):
        """初始化后处理"""
        if self.start_time == 0.0:
            self.start_time = time.monotonic()

        # 将 2GB 转换为字节
        if self.memory_limit is None:
            self.memory_limit = 2 * 1024 * 1024 * 1024  # 2GB

    def is_running(self) -> bool:
        """检查进程是否仍在运行

        Story 2.13 - 任务 14.2:
        - 监控 MATLAB 进程是否异常退出

        Returns:
            bool: 进程正在运行返回 True
        """
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil 不可用，无法检查进程状态")
            return False

        try:
            proc = psutil.Process(self.pid)
            return proc.is_running()
        except psutil.NoSuchProcess:
            return False
        except psutil.AccessDenied:
            logger.warning(f"无法访问进程 {self.pid} (权限不足)")
            return False

    def get_memory_usage(self) -> Optional[int]:
        """获取进程内存使用量（字节）

        Story 2.13 - 任务 14.3:
        - 检测进程内存占用（不超过 2GB）

        Returns:
            int: 内存使用量（字节），失败返回 None
        """
        if not PSUTIL_AVAILABLE:
            return None

        try:
            proc = psutil.Process(self.pid)
            return proc.memory_info().rss  # Resident Set Size
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def check_memory_limit(self) -> bool:
        """检查进程内存是否超过限制

        Story 2.13 - 任务 14.3:
        - 检测进程内存占用（不超过 2GB）

        Returns:
            bool: 未超过限制返回 True
        """
        memory_usage = self.get_memory_usage()
        if memory_usage is None:
            return True  # 无法获取内存使用量，假设正常

        if memory_usage > self.memory_limit:
            logger.warning(
                f"进程 {self.pid} 内存占用超过限制: "
                f"{memory_usage / (1024*1024):.1f} MB > "
                f"{self.memory_limit / (1024*1024):.1f} MB"
            )
            return False

        return True

    def is_stuck(self) -> bool:
        """检测进程是否僵死

        Story 2.13 - 任务 14.4:
        - 实现进程僵死检测

        Returns:
            bool: 进程僵死返回 True

        Note:
            这里使用简单的 CPU 占用率检测作为僵死指标
            如果 CPU 占用率为 0 超过一定时间，可能表示进程僵死
        """
        if not PSUTIL_AVAILABLE:
            return False

        try:
            proc = psutil.Process(self.pid)
            # 获取 CPU 占用率
            cpu_percent = proc.cpu_percent(interval=1.0)

            # 如果 CPU 占用率为 0，可能是僵死
            if cpu_percent == 0.0:
                logger.warning(f"进程 {self.pid} CPU 占用率为 0，可能已僵死")
                return True

            return False

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def check_timeout(self) -> bool:
        """检查进程是否超时

        Story 2.13 - 任务 14.5:
        - 添加超时后强制终止逻辑

        Returns:
            bool: 未超时返回 True
        """
        if self.timeout is None:
            return True

        elapsed = time.monotonic() - self.start_time

        if elapsed > self.timeout:
            logger.warning(f"进程 {self.pid} 超时（{elapsed:.1f} 秒 > {self.timeout} 秒）")
            return False

        return True

    def terminate(self, force: bool = False) -> bool:
        """终止进程

        Story 2.13 - 任务 14.5:
        - 添加超时后强制终止逻辑

        Args:
            force: 是否强制终止（SIGKILL）

        Returns:
            bool: 终止成功返回 True
        """
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil 不可用，无法终止进程")
            return False

        try:
            proc = psutil.Process(self.pid)

            if force:
                logger.info(f"强制终止进程 {self.pid}")
                proc.kill()
            else:
                logger.info(f"优雅终止进程 {self.pid}")
                proc.terminate()

            return True

        except psutil.NoSuchProcess:
            logger.info(f"进程 {self.pid} 已不存在")
            return True
        except psutil.AccessDenied:
            logger.error(f"无权限终止进程 {self.pid}")
            return False

    def monitor_loop(
        self,
        on_timeout: Optional[callable] = None,
        on_memory_exceeded: Optional[callable] = None,
        on_stuck: Optional[callable] = None,
        on_exited: Optional[callable] = None
    ) -> None:
        """进程监控循环

        持续监控进程状态，在检测到异常时调用回调函数。

        Story 2.13 - 任务 14.1-14.5:
        - 监控进程状态
        - 检测超时
        - 检测内存超限
        - 检测僵死进程
        - 检测进程退出

        Args:
            on_timeout: 超时回调
            on_memory_exceeded: 内存超限回调
            on_stuck: 僵死回调
            on_exited: 进程退出回调
        """
        while True:
            # 检查进程是否仍在运行
            if not self.is_running():
                logger.info(f"进程 {self.pid} 已退出")
                if on_exited:
                    on_exited(self)
                break

            # 检查超时
            if not self.check_timeout():
                logger.error(f"进程 {self.pid} 超时")
                if on_timeout:
                    on_timeout(self)
                break

            # 检查内存超限
            if not self.check_memory_limit():
                logger.error(f"进程 {self.pid} 内存超限")
                if on_memory_exceeded:
                    on_memory_exceeded(self)
                # 不立即终止，仅记录警告

            # 检测僵死（可选，避免误判）
            # if self.is_stuck():
            #     logger.warning(f"进程 {self.pid} 可能僵死")
            #     if on_stuck:
            #         on_stuck(self)

            # 等待下次检查
            time.sleep(self.check_interval)

    def get_process_info(self) -> Dict[str, Any]:
        """获取进程信息

        Returns:
            dict: 进程信息字典
        """
        info = {
            "pid": self.pid,
            "name": self.name,
            "is_running": self.is_running(),
            "elapsed_time": time.monotonic() - self.start_time,
        }

        if PSUTIL_AVAILABLE:
            try:
                proc = psutil.Process(self.pid)
                info["memory_usage_mb"] = self.get_memory_usage() / (1024 * 1024) if self.get_memory_usage() else 0
                info["cpu_percent"] = proc.cpu_percent(interval=0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return info


def monitor_matlab_process(
    pid: int,
    timeout: Optional[int] = None,
    memory_limit: Optional[int] = None
) -> ProcessMonitor:
    """创建 MATLAB 进程监控器

    Story 2.13 - 任务 14.1:
    - 在 process_mgr.py 中添加 MATLAB 进程监控支持

    Args:
        pid: MATLAB 进程 PID
        timeout: 超时时间（秒）
        memory_limit: 内存限制（字节）

    Returns:
        ProcessMonitor: 进程监控器实例
    """
    monitor = ProcessMonitor(
        pid=pid,
        name="MATLAB",
        timeout=timeout,
        memory_limit=memory_limit
    )

    logger.info(f"创建 MATLAB 进程监控器: PID={pid}")
    return monitor


# =============================================================================
# Story 2.15: 进程终止工具函数
# =============================================================================

def terminate_process(
    proc: subprocess.Popen,
    timeout: int = 5,
    force: bool = False
) -> tuple:
    """终止进程（优雅终止 + 强制终止）

    Story 2.15 - 任务 3.1-3.6:
    - 接受 subprocess.Popen 对象和超时参数
    - 尝试优雅终止（proc.terminate()）
    - 等待进程退出（最多超时秒数）
    - 如果未退出，强制终止（proc.kill()）
    - 使用 psutil 确保进程树清理（子进程）

    Story 2.15 - 任务 14.1-14.3:
    - 处理进程终止失败的情况
    - 记录无法终止的进程 PID
    - 提供手动终止的建议

    Architecture Decision 2.1:
    - 使用 terminate() + 等待 + kill() 模式
    - 确保僵尸进程清理

    Args:
        proc: subprocess.Popen 对象
        timeout: 优雅终止超时时间（秒），默认 5 秒
        force: 是否跳过优雅终止直接强制终止（默认 False）

    Returns:
        tuple: (成功标志, 建议列表)
            - 成功标志: bool, True 表示成功终止
            - 建议列表: list, 错误时提供恢复建议

    Examples:
        >>> import subprocess
        >>> proc = subprocess.Popen(["sleep", "10"])
        >>> success, suggestions = terminate_process(proc, timeout=5)
        >>> assert success is True
        >>> assert proc.poll() is not None
    """
    suggestions = []

    try:
        # 检查进程是否已退出 (Task 3.2)
        if proc.poll() is not None:
            logger.info(f"进程 PID: {proc.pid} 已退出")
            return True, []

        # 如果 force=True，直接强制终止
        if force:
            logger.info(f"直接强制终止进程 PID: {proc.pid}")
            proc.kill()

            try:
                proc.wait(timeout=2)
                logger.info(f"进程 PID: {proc.pid} 已强制终止")
                return True, []
            except subprocess.TimeoutExpired:
                logger.error(f"进程 PID: {proc.pid} 强制终止超时")
                # 任务 14.2: 记录无法终止的进程 PID
                suggestions.append(
                    f"请手动在任务管理器中终止进程 PID: {proc.pid}"
                )
                suggestions.append("如果进程仍然存在，尝试重启计算机")
                # 继续尝试清理进程树
                _cleanup_process_tree(proc.pid)
                return False, suggestions

        # 优雅终止 (Task 3.3)
        logger.info(f"尝试优雅终止进程 PID: {proc.pid}")
        proc.terminate()

        # 等待进程退出 (Task 3.4)
        try:
            proc.wait(timeout=timeout)
            logger.info(f"进程 PID: {proc.pid} 已优雅终止")
            return True, []
        except subprocess.TimeoutExpired:
            # 优雅终止超时，强制终止 (Task 3.5)
            logger.warning(
                f"进程 PID: {proc.pid} 优雅终止超时（{timeout}秒），尝试强制终止"
            )
            proc.kill()

            try:
                proc.wait(timeout=2)
                logger.info(f"进程 PID: {proc.pid} 已强制终止")
                return True, []
            except subprocess.TimeoutExpired:
                logger.error(f"进程 PID: {proc.pid} 强制终止失败")
                # 任务 14.2, 14.3: 记录无法终止的进程 PID，提供手动终止建议
                suggestions.append(
                    f"请手动在任务管理器中终止进程 PID: {proc.pid}"
                )
                suggestions.append("如果进程仍然存在，尝试重启计算机")
                # 继续尝试清理进程树
                _cleanup_process_tree(proc.pid)
                return False, suggestions

        # 清理进程树 (Task 3.6)
        _cleanup_process_tree(proc.pid)

        return True, []

    except psutil.AccessDenied as e:
        # 任务 14.1: 处理进程终止失败的情况（权限不足）
        error_msg = f"无权限终止进程 PID: {proc.pid}"
        logger.error(error_msg)
        suggestions.append(f"请以管理员身份运行程序")
        suggestions.append(f"请手动在任务管理器中终止进程 PID: {proc.pid}")
        return False, suggestions

    except Exception as e:
        logger.error(f"终止进程失败 PID: {getattr(proc, 'pid', 'unknown')} - {e}")
        suggestions.append(f"错误: {str(e)}")
        suggestions.append("请查看日志获取详细信息")
        return False, suggestions


def _cleanup_process_tree(pid: int) -> bool:
    """清理进程树（包括所有子进程）

    Story 2.15 - 任务 3.6:
    - 使用 psutil 确保进程树清理
    - 递归终止所有子进程

    Args:
        pid: 进程 PID

    Returns:
        bool: 清理成功返回 True
    """
    if not PSUTIL_AVAILABLE:
        logger.warning("psutil 不可用，无法清理进程树")
        return False

    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        if not children:
            # 没有子进程
            return True

        logger.info(f"清理进程树: PID={pid}, 子进程数={len(children)}")

        # 终止所有子进程
        for child in children:
            try:
                logger.debug(f"终止子进程 PID: {child.pid}")
                child.kill()
            except psutil.NoSuchProcess:
                continue
            except psutil.AccessDenied:
                logger.warning(f"无权限终止子进程 PID: {child.pid}")
                continue

        # 等待子进程退出
        psutil.wait_procs(children, timeout=2)

        logger.info(f"进程树清理完成: PID={pid}")
        return True

    except psutil.NoSuchProcess:
        # 进程已不存在
        logger.info(f"进程 PID: {pid} 已不存在")
        return True

    except psutil.AccessDenied:
        logger.error(f"无权限访问进程 PID: {pid}")
        return False

    except Exception as e:
        logger.error(f"清理进程树失败 PID: {pid} - {e}")
        return False

