"""Configuration persistence module for MBD_CICDKits.

This module handles saving and loading project configurations in TOML format
following Architecture Decision 1.1 (Configuration Format: TOML).
"""

import logging
import os
from pathlib import Path
from typing import Optional

# Python 3.11+ has built-in tomllib, Python 3.10 needs tomli
try:
    import tomllib
except ImportError:
    import tomli as tomllib

# tomli_w is needed for writing TOML
try:
    import tomli_w
except ImportError:
    tomli_w = None

from core.models import ProjectConfig

logger = logging.getLogger(__name__)


def get_config_dir() -> Path:
    """获取平台相关的配置目录

    Returns:
        平台相关的配置目录路径
    """
    if os.name == 'nt':  # Windows
        return Path.home() / "AppData" / "Roaming" / "MBD_CICDKits" / "configs"
    else:  # macOS/Linux
        return Path.home() / ".config" / "mbd_cicdkits" / "configs"


# 配置存储位置
CONFIG_DIR = get_config_dir()


def save_config(config: ProjectConfig, filename: str) -> bool:
    """保存项目配置到 TOML 文件

    Args:
        config: 项目配置对象
        filename: 文件名（不含扩展名）

    Returns:
        bool: 保存是否成功
    """
    if tomli_w is None:
        logger.error("tomli_w 未安装，请运行: pip install tomli_w")
        return False

    try:
        # 检查目录权限
        try:
            test_file = CONFIG_DIR / ".write_test"
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            test_file.touch()
            test_file.unlink()
        except (OSError, PermissionError) as e:
            logger.error(f"配置目录无写入权限: {e}")
            return False

        # 转换为字典（排除 None 值）
        config_dict = config.to_dict()

        # 保存为 TOML
        config_file = CONFIG_DIR / f"{filename}.toml"
        with open(config_file, "wb") as f:
            tomli_w.dump(config_dict, f)

        logger.info(f"配置已保存: {config_file}")
        return True

    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return False


def load_config(filename: str) -> Optional[ProjectConfig]:
    """加载项目配置

    Args:
        filename: 配置文件名（不含扩展名）

    Returns:
        ProjectConfig 或 None
    """
    try:
        config_file = CONFIG_DIR / f"{filename}.toml"

        if not config_file.exists():
            logger.debug(f"配置文件不存在: {config_file}")
            return None

        with open(config_file, "rb") as f:
            config_dict = tomllib.load(f)

        config = ProjectConfig.from_dict(config_dict)

        # 验证必需字段
        errors = config.validate_required_fields()
        if errors:
            logger.error(f"配置验证失败: {errors}")
            return None

        return config

    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return None


def list_configs() -> list[str]:
    """列出所有已保存的配置文件

    Returns:
        配置文件名列表（不含扩展名）
    """
    try:
        if not CONFIG_DIR.exists():
            return []

        config_files = []
        for file in CONFIG_DIR.glob("*.toml"):
            config_files.append(file.stem)

        return sorted(config_files)

    except Exception as e:
        logger.error(f"列出配置失败: {e}")
        return []


def delete_config(filename: str) -> bool:
    """删除配置文件

    Args:
        filename: 配置文件名（不含扩展名）

    Returns:
        bool: 删除是否成功
    """
    try:
        config_file = CONFIG_DIR / f"{filename}.toml"

        if not config_file.exists():
            logger.warning(f"配置文件不存在: {config_file}")
            return False

        config_file.unlink()
        logger.info(f"配置已删除: {config_file}")
        return True

    except Exception as e:
        logger.error(f"删除配置失败: {e}")
        return False
