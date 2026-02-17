"""Cancel configuration management for MBD_CICDKits.

This module provides functionality to save and restore cancelled build configurations.

Story 2.15 - 任务 13: 添加取消操作重试支持
- 保存取消时的配置和状态
- 从保存的配置恢复构建
"""

import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def get_cancelled_builds_dir() -> Path:
    """获取取消配置保存目录

    Story 2.15 - 任务 13.2:
    - 配置保存到 %APPDATA%/MBD_CICDKits/cancelled_builds/

    Returns:
        Path: 取消配置目录路径
    """
    import os

    # Windows: %APPDATA%/MBD_CICDKits/cancelled_builds/
    app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
    cancel_dir = Path(app_data) / "MBD_CICDKits" / "cancelled_builds"

    # 创建目录
    cancel_dir.mkdir(parents=True, exist_ok=True)

    logger.debug(f"取消配置目录: {cancel_dir}")
    return cancel_dir


def save_cancelled_config(
    project_name: str,
    config: Dict[str, Any],
    state: Dict[str, Any],
    current_stage: str = "",
    completed_stages: list = None
) -> Optional[Path]:
    """保存取消时的配置 (Story 2.15 - 任务 13.1-13.3)

    保存取消时的项目配置、状态等信息，以便后续恢复。

    Args:
        project_name: 项目名称
        config: 项目配置字典
        state: 构建状态字典
        current_stage: 当前执行阶段
        completed_stages: 已完成的阶段列表

    Returns:
        Optional[Path]: 保存的文件路径，失败返回 None
    """
    try:
        # 获取保存目录 (任务 13.2)
        cancel_dir = get_cancelled_builds_dir()

        # 生成文件名 (任务 13.3)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cancelled_{project_name}_{timestamp}.json"
        file_path = cancel_dir / filename

        # 准备保存数据 (任务 13.1)
        data = {
            "project_name": project_name,
            "timestamp": timestamp,
            "cancelled_at": datetime.now().isoformat(),
            "config": config,
            "state": state,
            "completed_stages": completed_stages or [],
            "current_stage": current_stage
        }

        # 保存文件
        file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        logger.info(f"取消配置已保存: {file_path}")

        return file_path

    except Exception as e:
        logger.error(f"保存取消配置失败: {e}")
        return None


def load_cancelled_config(file_path: Path) -> Optional[Dict[str, Any]]:
    """加载取消配置 (Story 2.15 - 任务 13.4-13.6)

    从保存的配置文件加载取消时的配置。

    Args:
        file_path: 配置文件路径

    Returns:
        Optional[Dict]: 配置数据字典，失败返回 None
    """
    try:
        if not file_path.exists():
            logger.warning(f"取消配置文件不存在: {file_path}")
            return None

        # 读取文件
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)

        logger.info(f"取消配置已加载: {file_path}")
        return data

    except Exception as e:
        logger.error(f"加载取消配置失败: {e}")
        return None


def list_cancelled_builds() -> list:
    """列出所有取消的构建 (Story 2.15 - 任务 13.4)

    Returns:
        list: 取消配置信息列表，每个元素包含:
            - filename: 文件名
            - filepath: 文件路径
            - project_name: 项目名称
            - cancelled_at: 取消时间
            - current_stage: 当前阶段
            - completed_stages: 已完成阶段
    """
    try:
        cancel_dir = get_cancelled_builds_dir()

        # 获取所有 .json 文件
        cancelled_builds = []
        for file_path in cancel_dir.glob("cancelled_*.json"):
            try:
                # 读取文件头信息
                content = file_path.read_text(encoding="utf-8")
                data = json.loads(content)

                cancelled_builds.append({
                    "filename": file_path.name,
                    "filepath": file_path,
                    "project_name": data.get("project_name", "未知"),
                    "cancelled_at": data.get("cancelled_at", ""),
                    "current_stage": data.get("current_stage", ""),
                    "completed_stages": data.get("completed_stages", [])
                })
            except Exception as e:
                logger.warning(f"读取取消配置文件失败 {file_path}: {e}")
                continue

        # 按取消时间倒序排列
        cancelled_builds.sort(
            key=lambda x: x["cancelled_at"],
            reverse=True
        )

        logger.info(f"找到 {len(cancelled_builds)} 个取消的构建")
        return cancelled_builds

    except Exception as e:
        logger.error(f"列出取消构建失败: {e}")
        return []


def delete_cancelled_config(file_path: Path) -> bool:
    """删除取消配置 (Story 2.15 - 任务 13.4)

    Args:
        file_path: 配置文件路径

    Returns:
        bool: 是否成功删除
    """
    try:
        if not file_path.exists():
            logger.warning(f"取消配置文件不存在: {file_path}")
            return False

        file_path.unlink()
        logger.info(f"取消配置已删除: {file_path}")
        return True

    except Exception as e:
        logger.error(f"删除取消配置失败: {e}")
        return False


def restore_build_from_cancelled_config(
    file_path: Path,
    project_name: str
) -> Optional[Dict[str, Any]]:
    """从取消配置恢复构建 (Story 2.15 - 任务 13.5)

    从取消配置中提取项目配置，用于重新开始构建。

    Args:
        file_path: 取消配置文件路径
        project_name: 项目名称（用于验证）

    Returns:
        Optional[Dict]: 项目配置字典，失败返回 None
    """
    try:
        # 加载取消配置
        data = load_cancelled_config(file_path)
        if not data:
            return None

        # 验证项目名称
        if data.get("project_name") != project_name:
            logger.warning(
                f"项目名称不匹配: 期望 {project_name}, "
                f"实际 {data.get('project_name')}"
            )
            return None

        # 提取项目配置
        config = data.get("config", {})

        logger.info(f"从取消配置恢复构建: {file_path}")
        return config

    except Exception as e:
        logger.error(f"恢复构建失败: {e}")
        return None
