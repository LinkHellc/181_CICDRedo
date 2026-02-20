"""
Log persistence utilities for MBD_CICDKits.

This module provides log file management and persistence functionality
for Story 3.2 Task 9: Implement log persistence.
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class LogFileHandler:
    """日志文件处理器 (Story 3.2 Task 9)

    负责将日志保存到文件，支持日志记录的开始、追加和结束。

    功能：
    - 在工作流开始时创建日志文件
    - 实时追加日志到文件
    - 在工作流结束时关闭日志文件
    - 文件路径：%APPDATA%/MBD_CICDKits/logs/build_[YYYYMMDD_HHMMSS].log
    """

    def __init__(self, log_dir: Optional[Path] = None):
        """初始化日志文件处理器

        Args:
            log_dir: 日志目录，如果为 None 则使用默认目录
        """
        if log_dir is None:
            # 默认日志目录：APPDATA/MBD_CICDKits/logs
            appdata = os.getenv("APPDATA", os.path.expanduser("~/.local/share"))
            self.log_dir = Path(appdata) / "MBD_CICDKits" / "logs"
        else:
            self.log_dir = log_dir

        self.log_file: Optional[Path] = None
        self.file_handle = None

    def start_logging(self, project_name: str = "Unknown") -> Optional[Path]:
        """
        开始日志记录 (Task 9.1, 9.2, 9.4)

        创建日志文件并写入文件头。

        Args:
            project_name: 项目名称

        Returns:
            Optional[Path]: 日志文件路径，失败返回 None
        """
        try:
            # 创建日志目录 (Task 9.3)
            self.log_dir.mkdir(parents=True, exist_ok=True)

            # 生成日志文件名 (Task 9.3)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"build_{timestamp}.log"
            self.log_file = self.log_dir / filename

            # 打开文件 (Task 9.2)
            self.file_handle = open(self.log_file, 'w', encoding='utf-8')

            # 写入日志头 (Task 9.2)
            header = (
                f"=== MBD_CICDKits Build Log ===\n"
                f"Project: {project_name}\n"
                f"Start Time: {datetime.now().isoformat()}\n"
                f"================================\n\n"
            )
            self.file_handle.write(header)
            self.file_handle.flush()

            logging.info(f"日志记录已启动: {self.log_file}")
            return self.log_file

        except Exception as e:
            logging.error(f"启动日志记录失败: {e}")
            return None

    def append_log(self, message: str) -> None:
        """
        追加日志到文件 (Task 9.2)

        Args:
            message: 日志消息
        """
        if self.file_handle:
            try:
                self.file_handle.write(message + '\n')
                self.file_handle.flush()
            except Exception as e:
                logging.error(f"写入日志文件失败: {e}")

    def stop_logging(self) -> None:
        """
        停止日志记录 (Task 9.5)

        写入日志尾并关闭文件。
        """
        if self.file_handle:
            try:
                # 写入日志尾
                footer = (
                    f"\n================================\n"
                    f"End Time: {datetime.now().isoformat()}\n"
                    f"================================\n"
                )
                self.file_handle.write(footer)

                # 关闭文件 (Task 9.5)
                self.file_handle.close()
                self.file_handle = None

                logging.info(f"日志已保存: {self.log_file}")

            except Exception as e:
                logging.error(f"停止日志记录失败: {e}")

    def get_log_file(self) -> Optional[Path]:
        """
        获取当前日志文件路径

        Returns:
            当前日志文件路径，如果没有则返回 None
        """
        return self.log_file

    def is_logging(self) -> bool:
        """
        检查是否正在记录日志

        Returns:
            bool: 如果正在记录返回 True
        """
        return self.file_handle is not None

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop_logging()
        return False
