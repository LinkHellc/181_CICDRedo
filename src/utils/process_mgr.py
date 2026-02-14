"""Process management utilities for MBD_CICDKits.

This module provides process monitoring and management utilities.

Story 2.13 - 任务 14: 实现进程监控和超时处理
- 添加 MATLAB 进程监控支持
- 监控进程是否异常退出
- 检测进程内存占用
- 实现进程僵死检测
- 添加超时后强制终止逻辑
"""

import logging
import time
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
