"""Progress calculation utilities for build progress display (Story 2.14)

This module provides functions for calculating progress percentage,
estimating remaining time, formatting duration, and persisting progress.

Architecture Decision 1.2:
- 使用 typing 模块的类型注解（Python 3.11 兼容性）
- 统一的错误处理
"""

import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)


def calculate_progress(completed: int, total: int) -> float:
    """计算进度百分比 (Story 2.14 - 任务 3)

    Args:
        completed: 已完成的阶段数
        total: 总阶段数

    Returns:
        float: 进度百分比（0-100）

    Examples:
        >>> calculate_progress(2, 5)
        40.0
        >>> calculate_progress(0, 5)
        0.0
        >>> calculate_progress(5, 5)
        100.0
    """
    if total == 0:
        return 0.0
    return (completed / total) * 100


def calculate_time_remaining(elapsed: float, percentage: float) -> float:
    """估算剩余时间 (Story 2.14 - 任务 4)

    Args:
        elapsed: 已用时间（秒）
        percentage: 当前进度百分比

    Returns:
        float: 预计剩余时间（秒）

    Examples:
        >>> calculate_time_remaining(60, 50)
        60.0
        >>> calculate_time_remaining(60, 0)
        0.0
        >>> calculate_time_remaining(60, 100)
        0.0
    """
    if percentage <= 0 or percentage >= 100:
        return 0.0
    return elapsed * ((100 - percentage) / percentage)


def format_duration(seconds: float) -> str:
    """格式化时长为 HH:MM:SS 或 MM:SS 格式 (Story 2.14 - 任务 10)

    Args:
        seconds: 时长（秒）

    Returns:
        str: 格式化后的时长字符串

    Examples:
        >>> format_duration(3665)
        '01:01:05'
        >>> format_duration(125)
        '02:05'
        >>> format_duration(0)
        '00:00'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def save_progress(progress: Dict, temp_dir: Path) -> Optional[Path]:
    """保存进度到临时文件 (Story 2.14 - 任务 11)

    Args:
        progress: 进度字典
        temp_dir: 临时目录

    Returns:
        Optional[Path]: 保存的文件路径，失败返回 None
    """
    try:
        temp_dir.mkdir(parents=True, exist_ok=True)
        progress_file = temp_dir / "progress.json"
        progress_file.write_text(json.dumps(progress, indent=2), encoding='utf-8')
        logger.debug(f"进度保存: {progress_file}")
        return progress_file
    except Exception as e:
        logger.error(f"进度保存失败: {e}")
        return None


def load_progress(temp_dir: Path) -> Optional[Dict]:
    """从临时文件加载进度 (Story 2.14 - 任务 11)

    Args:
        temp_dir: 临时目录

    Returns:
        Optional[Dict]: 进度字典，失败返回 None
    """
    try:
        progress_file = temp_dir / "progress.json"
        if progress_file.exists():
            progress = json.loads(progress_file.read_text(encoding='utf-8'))
            logger.info(f"进度恢复: 从 {progress_file} 加载")
            return progress
        return None
    except Exception as e:
        logger.error(f"进度恢复失败: {e}")
        return None
