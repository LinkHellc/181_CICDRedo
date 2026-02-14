"""Configuration persistence module for MBD_CICDKits.

This module handles saving and loading project configurations in TOML format
following Architecture Decision 1.1 (Configuration Format: TOML).
"""

import logging
import sys
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

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

from core.models import ProjectConfig, WorkflowConfig, StageConfig
from utils.errors import (
    ConfigSaveError,
    ConfigValidationError,
    ConfigLoadError,
    ConfigError
)

logger = logging.getLogger(__name__)


def get_config_dir() -> Path:
    """获取平台相关的配置目录

    遵循 AC #1: 保存到 %APPDATA%/MBD_CICDKits/projects/ (Windows)
    或 ~/.config/mbd_cicdkits/projects/ (Linux/macOS)

    Returns:
        平台相关的配置目录路径
    """
    if sys.platform == "win32":  # Windows
        return Path.home() / "AppData" / "Roaming" / "MBD_CICDKits" / "projects"
    else:  # macOS/Linux
        return Path.home() / ".config" / "mbd_cicdkits" / "projects"


# 配置存储位置
CONFIG_DIR = get_config_dir()


def get_projects_dir() -> Path:
    """获取项目配置目录（get_config_dir 的别名）

    为了代码清晰性，提供更语义化的函数名。

    Returns:
        项目配置目录路径（与 get_config_dir 相同）
    """
    return get_config_dir()


def save_config(config: ProjectConfig, filename: str, overwrite: bool = False) -> bool:
    """保存项目配置到 TOML 文件

    Args:
        config: 项目配置对象
        filename: 文件名（不含扩展名）
        overwrite: 是否覆盖已存在的文件（默认 False）

    Returns:
        bool: 保存是否成功

    Raises:
        ConfigValidationError: 配置验证失败时抛出
        ConfigSaveError: 保存失败时抛出
    """
    if tomli_w is None:
        logger.error("tomli_w 未安装，请运行: pip install tomli_w")
        raise ConfigSaveError("tomli_w 未安装")

    try:
        # 使用 CONFIG_DIR 常量（与 load_config 保持一致）
        config_dir = CONFIG_DIR

        # 确保配置目录存在（AC #4）
        config_dir.mkdir(parents=True, exist_ok=True)

        # 验证配置（Story 1.2: 保存前验证）
        errors = config.validate_required_fields()
        if errors:
            raise ConfigValidationError(
                f"配置验证失败: {', '.join(errors)}",
                suggestions=["检查所有必填字段是否已填写"]
            )

        # 检查文件是否存在（AC #5）
        config_file = config_dir / f"{filename}.toml"
        if config_file.exists() and not overwrite:
            return False  # 通知UI层显示确认对话框

        # 更新时间戳（Story 1.2: 添加 created_at 和 modified_at）
        now = datetime.now().isoformat()
        config.modified_at = now
        if not config.created_at:
            config.created_at = now

        # 转换为字典（排除 None 值和空字符串）
        config_dict = config.to_dict()

        # 保存为 TOML
        with open(config_file, "wb") as f:
            tomli_w.dump(config_dict, f)

        logger.info(f"配置已保存: {filename}")
        return True

    except ConfigValidationError:
        raise
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        raise ConfigSaveError(str(e))


def config_exists(filename: str) -> bool:
    """检查配置文件是否存在

    Args:
        filename: 配置文件名（不含扩展名）

    Returns:
        bool: 文件是否存在
    """
    if not filename:
        return False
    config_file = get_config_dir() / f"{filename}.toml"
    return config_file.exists()


def load_config(filename: str) -> Optional[ProjectConfig]:
    """加载项目配置

    Args:
        filename: 配置文件名（不含扩展名）

    Returns:
        ProjectConfig 对象

    Raises:
        ConfigLoadError: 配置文件不存在、格式错误或验证失败时抛出
    """
    try:
        config_file = CONFIG_DIR / f"{filename}.toml"

        if not config_file.exists():
            raise ConfigLoadError(
                f"配置文件不存在: {filename}",
                suggestions=[
                    f"检查项目名称 '{filename}' 是否正确",
                    "重新创建项目配置",
                    "查看已保存的项目列表"
                ]
            )

        try:
            with open(config_file, "rb") as f:
                config_dict = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ConfigLoadError(
                f"配置文件格式错误: {filename}",
                suggestions=[
                    "使用文本编辑器检查 TOML 文件格式",
                    "从备份恢复配置文件",
                    "重新创建项目配置"
                ]
            )

        config = ProjectConfig.from_dict(config_dict)

        # 验证必需字段
        errors = config.validate_required_fields()
        if errors:
            raise ConfigLoadError(
                f"配置信息不完整: {', '.join(errors)}",
                suggestions=[
                    "重新创建项目配置",
                    "手动编辑配置文件补充缺失字段",
                    "检查配置文件完整性"
                ]
            )

        logger.info(f"配置已加载: {filename}")
        return config

    except ConfigLoadError:
        raise
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        raise ConfigLoadError(str(e))


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


def list_saved_projects() -> list[str]:
    """列出所有已保存的项目配置（Story 1.3）

    这是 list_configs() 的语义化别名，用于 Story 1.3 加载项目功能。

    Returns:
        项目名称列表（不含扩展名），按字母排序
    """
    return list_configs()


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


def update_config(project_name: str, updated_config: ProjectConfig) -> bool:
    """更新现有项目配置

    Args:
        project_name: 项目名称（文件名，不含扩展名）
        updated_config: 更新后的配置对象

    Returns:
        bool: 更新是否成功

    Raises:
        ConfigLoadError: 原配置不存在时抛出
        ConfigValidationError: 配置验证失败
    """
    try:
        # 验证配置
        errors = updated_config.validate_required_fields()
        if errors:
            raise ConfigValidationError(
                f"配置验证失败: {', '.join(errors)}",
                suggestions=["检查所有必填字段是否已填写"]
            )

        # 加载原配置以保留 created_at
        try:
            original_config = load_config(project_name)
        except ConfigLoadError:
            raise ConfigLoadError(
                f"项目配置不存在: {project_name}",
                suggestions=[
                    "检查项目名称是否正确",
                    "创建新项目配置",
                ]
            )

        # 保留 created_at，更新 modified_at
        updated_config.created_at = original_config.created_at
        updated_config.modified_at = datetime.now().isoformat()

        # 保存更新（覆盖模式）
        return save_config(updated_config, project_name, overwrite=True)

    except (ConfigLoadError, ConfigValidationError):
        raise
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise ConfigError(f"更新配置失败: {str(e)}")


def load_workflow_templates() -> list[WorkflowConfig]:
    """加载工作流模板配置 (Story 2.1 Task 3)

    从 configs/default_workflow.json 加载预定义的工作流模板。

    Returns:
        WorkflowConfig 对象列表

    Raises:
        ConfigLoadError: 文件不存在、格式错误或验证失败时抛出
    """
    try:
        # 获取工作流配置文件路径
        # 优先使用项目根目录下的 configs，否则使用 src 同级目录
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "configs" / "default_workflow.json"

        # 备用路径：src/configs/
        if not config_path.exists():
            config_path = Path(__file__).parent.parent.parent / "src" / "configs" / "default_workflow.json"

        if not config_path.exists():
            raise ConfigLoadError(
                f"工作流配置文件不存在: {config_path}",
                suggestions=[
                    "确保 configs/default_workflow.json 文件存在",
                    "检查文件路径是否正确"
                ]
            )

        # 加载 JSON 文件
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigLoadError(
                f"工作流配置文件格式错误: {e}",
                suggestions=[
                    "检查 JSON 文件格式是否正确",
                    "使用 JSON 验证工具验证文件"
                ]
            )

        # 验证基本结构
        if "templates" not in data:
            raise ConfigLoadError(
                "工作流配置缺少 'templates' 字段",
                suggestions=["确保 JSON 文件包含 'templates' 字段"]
            )

        if not isinstance(data["templates"], list):
            raise ConfigLoadError(
                "'templates' 字段应为列表",
                suggestions=["确保 'templates' 是一个列表"]
            )

        # 转换为 WorkflowConfig 对象列表
        templates = []
        for template_data in data["templates"]:
            try:
                workflow = WorkflowConfig.from_dict(template_data)
                templates.append(workflow)
            except Exception as e:
                logger.warning(f"跳过无效的工作流模板: {e}")
                continue

        if not templates:
            raise ConfigLoadError(
                "没有有效的工作流模板",
                suggestions=["检查 default_workflow.json 中的模板格式"]
            )

        logger.info(f"已加载 {len(templates)} 个工作流模板")
        return templates

    except ConfigLoadError:
        raise
    except Exception as e:
        logger.error(f"加载工作流模板失败: {e}")
        raise ConfigLoadError(str(e))


def save_selected_workflow(project_name: str, workflow: WorkflowConfig) -> bool:
    """保存选中的工作流配置到项目配置 (Story 2.1 Task 6)

    将用户选择的工作流模板 ID 和名称保存到项目配置中。

    Args:
        project_name: 项目名称
        workflow: 选中的工作流配置对象

    Returns:
        bool: 保存是否成功

    Raises:
        ConfigLoadError: 项目配置不存在时抛出
        ConfigError: 保存失败时抛出
    """
    try:
        # 加载现有项目配置
        config = load_config(project_name)

        # 更新工作流字段
        config.workflow_id = workflow.id
        config.workflow_name = workflow.name

        # 可选：将完整的工作流配置保存到 custom_params
        # 这样可以在后续阶段使用详细的阶段配置
        config.custom_params["workflow_config"] = workflow.to_dict()

        # 更新时间戳
        config.modified_at = datetime.now().isoformat()

        # 保存更新（覆盖模式）
        result = save_config(config, project_name, overwrite=True)

        if result:
            logger.info(f"工作流已保存到项目 {project_name}: {workflow.id}")
        else:
            logger.error(f"保存工作流到项目 {project_name} 失败")

        return result

    except ConfigLoadError:
        raise
    except Exception as e:
        logger.error(f"保存工作流配置失败: {e}")
        raise ConfigError(f"保存工作流配置失败: {str(e)}")


def load_custom_workflow(file_path: Path) -> tuple[Optional[WorkflowConfig], Optional[str]]:
    """加载并验证自定义工作流配置 (Story 2.2)

    从用户指定的JSON文件加载自定义工作流配置，并进行验证。

    Args:
        file_path: 自定义工作流JSON文件路径

    Returns:
        (WorkflowConfig, error_message):
            - WorkflowConfig: 加载成功时返回配置对象
            - error_message: 加载失败时返回错误信息，成功时为None

    Raises:
        无：所有错误通过返回值传递，便于UI层处理
    """
    try:
        # 检查文件是否存在
        if not file_path.exists():
            error_msg = f"文件不存在: {file_path}"
            logger.error(error_msg)
            return None, error_msg

        # 加载JSON文件
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            error_msg = f"JSON格式错误: {e}"
            logger.error(error_msg)
            return None, error_msg
        except UnicodeDecodeError:
            error_msg = "文件编码错误，请使用UTF-8编码保存"
            logger.error(error_msg)
            return None, error_msg

        # 验证必需字段
        required_fields = ["name", "description", "stages"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            error_msg = f"缺少必需字段: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return None, error_msg

        # 验证stages字段
        if not isinstance(data["stages"], list):
            error_msg = "'stages' 字段必须是一个列表"
            logger.error(error_msg)
            return None, error_msg

        if not data["stages"]:
            error_msg = "stages 列表不能为空"
            logger.error(error_msg)
            return None, error_msg

        # 验证每个stage的必需字段
        stage_required_fields = ["id", "name", "enabled", "dependencies"]
        for idx, stage in enumerate(data["stages"]):
            stage_missing = [field for field in stage_required_fields if field not in stage]
            if stage_missing:
                error_msg = f"阶段 {idx} 缺少必需字段: {', '.join(stage_missing)}"
                logger.error(error_msg)
                return None, error_msg

            # 验证dependencies字段类型
            if not isinstance(stage["dependencies"], list):
                error_msg = f"阶段 {stage.get('id', idx)} 的 'dependencies' 字段必须是一个列表"
                logger.error(error_msg)
                return None, error_msg

        # 检查循环依赖
        stage_ids = [stage["id"] for stage in data["stages"]]
        has_cycle = _check_circular_dependencies(data["stages"])
        if has_cycle:
            error_msg = "检测到循环依赖，请检查stages的dependencies配置"
            logger.error(error_msg)
            return None, error_msg

        # 验证依赖的stage ID是否存在
        for idx, stage in enumerate(data["stages"]):
            for dep_id in stage["dependencies"]:
                if dep_id not in stage_ids:
                    error_msg = f"阶段 {stage.get('id', idx)} 的依赖 '{dep_id}' 不存在"
                    logger.error(error_msg)
                    return None, error_msg

        # 检查至少有一个启用的stage
        enabled_stages = [stage for stage in data["stages"] if stage.get("enabled", False)]
        if not enabled_stages:
            error_msg = "至少需要启用一个阶段"
            logger.error(error_msg)
            return None, error_msg

        # 转换为WorkflowConfig对象
        # 将自定义工作流的stages转换为StageConfig对象
        workflow = WorkflowConfig(
            id=data.get("id", "custom"),  # 如果没有id，使用"custom"
            name=data["name"],
            description=data["description"],
            estimated_time=data.get("estimated_time", 0),  # 可选字段
            stages=[
                StageConfig(
                    name=stage["id"],  # 使用id作为name（内部标识）
                    enabled=stage["enabled"],
                    timeout=stage.get("timeout", 300)  # 默认超时300秒
                )
                for stage in data["stages"]
            ]
        )

        logger.info(f"成功加载自定义工作流: {workflow.name}")
        return workflow, None

    except Exception as e:
        error_msg = f"加载自定义工作流时发生未知错误: {e}"
        logger.exception(error_msg)
        return None, error_msg


def _check_circular_dependencies(stages: list[dict]) -> bool:
    """检查工作流阶段是否存在循环依赖

    使用深度优先搜索（DFS）检测循环。

    Args:
        stages: 工作流阶段列表，每个阶段包含id和dependencies

    Returns:
        bool: 如果存在循环依赖返回True，否则返回False
    """
    # 构建邻接表
    graph = {stage["id"]: stage["dependencies"] for stage in stages}

    # DFS检测循环
    visited = set()
    rec_stack = set()

    def dfs(node: str) -> bool:
        """DFS递归函数

        Args:
            node: 当前访问的节点ID

        Returns:
            bool: 如果发现循环返回True
        """
        if node in rec_stack:
            return True  # 发现循环

        if node in visited:
            return False  # 已访问过，无循环

        visited.add(node)
        rec_stack.add(node)

        # 递归访问所有依赖节点
        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True

        rec_stack.remove(node)
        return False

    # 对所有节点执行DFS
    for stage_id in graph.keys():
        if dfs(stage_id):
            return True

    return False


# =============================================================================
# Story 2.14: 启用/禁用工作流阶段 - 配置验证
# =============================================================================

def validate_workflow_config(stages: list) -> list[str]:
    """验证工作流配置的 enabled 字段和依赖关系 (Story 2.14 - 任务 4)

    验证每个阶段的 enabled 字段为布尔值，并验证依赖关系的完整性。

    Args:
        stages: 阶段配置列表（StageConfig 对象列表）

    Returns:
        验证错误列表，空列表表示配置有效

    Examples:
        >>> # 有效配置
        >>> stages = [StageConfig(name="matlab_gen", enabled=True), ...]
        >>> errors = validate_workflow_config(stages)
        >>> errors == []

        >>> # 无效的 enabled 字段
        >>> stages = [StageConfig(name="matlab_gen", enabled="true"), ...]
        >>> errors = validate_workflow_config(stages)
        >>> len(errors) > 0
    """
    errors = []

    # 动态导入以避免循环依赖
    try:
        from core.workflow import get_stage_dependencies
    except ImportError:
        logger.error("无法导入 get_stage_dependencies")
        return ["无法加载依赖关系验证函数"]

    # 验证每个阶段的 enabled 字段（任务 4.2）
    for i, stage in enumerate(stages):
        if not hasattr(stage, "name"):
            errors.append(f"阶段 {i} 缺少 name 字段")
            continue

        stage_name = getattr(stage, "name", f"阶段 {i}")

        # 验证 enabled 字段存在且为布尔值
        if not hasattr(stage, "enabled"):
            errors.append(f"阶段 '{stage_name}' 缺少 enabled 字段")
            continue

        enabled = getattr(stage, "enabled")
        if not isinstance(enabled, bool):
            errors.append(f"阶段 '{stage_name}' 的 enabled 字段必须是布尔值，当前为 {type(enabled).__name__}")

    # 验证依赖关系的完整性（任务 4.3）
    # 检查启用阶段的依赖是否也被启用
    enabled_stages = {}
    for stage in stages:
        if hasattr(stage, "name") and hasattr(stage, "enabled"):
            enabled_stages[stage.name] = stage.enabled

    for stage in stages:
        if not hasattr(stage, "name") or not hasattr(stage, "enabled"):
            continue

        stage_name = stage.name

        # 只检查启用的阶段
        if not stage.enabled:
            continue

        # 获取前置依赖
        try:
            dependencies = get_stage_dependencies(stage_name)
        except Exception as e:
            logger.warning(f"获取阶段 '{stage_name}' 的依赖失败: {e}")
            continue

        # 检查每个依赖是否也被启用
        for dep_name in dependencies:
            if dep_name in enabled_stages:
                if not enabled_stages[dep_name]:
                    errors.append(
                        f"阶段 '{stage_name}' 已启用，但其依赖阶段 '{dep_name}' 未启用"
                    )
            else:
                logger.warning(f"阶段 '{stage_name}' 依赖未知的阶段 '{dep_name}'")

    return errors


def load_workflow_config(filepath: Path) -> tuple[list, list[str]]:
    """加载工作流配置文件 (Story 2.14 - 任务 5)

    从 JSON 文件加载工作流配置，读取每个阶段的 enabled 字段。

    Args:
        filepath: 工作流配置文件路径

    Returns:
        (stages, errors):
            - stages: 阶段配置列表（StageConfig 对象列表）
            - errors: 错误消息列表（空列表表示成功）

    Examples:
        >>> # 加载完整的工作流配置
        >>> stages, errors = load_workflow_config(Path("workflow.json"))
        >>> if errors:
        ...     print("加载失败:", errors)
    """
    errors = []

    try:
        # 检查文件是否存在 (任务 5.2)
        if not filepath.exists():
            errors.append(f"文件不存在: {filepath}")
            return [], errors

        # 加载 JSON 文件
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"JSON 格式错误: {e}")
            return [], errors
        except UnicodeDecodeError:
            errors.append("文件编码错误，请使用 UTF-8 编码保存")
            return [], errors

        # 验证基本结构
        if "workflow_name" not in data and "name" not in data:
            errors.append("工作流配置缺少 'workflow_name' 或 'name' 字段")
            return [], errors

        if "stages" not in data:
            errors.append("工作流配置缺少 'stages' 字段")
            return [], errors

        if not isinstance(data["stages"], list):
            errors.append("'stages' 字段必须是一个列表")
            return [], errors

        # 解析阶段列表 (任务 5.3, 5.4)
        stages = []
        for i, stage_data in enumerate(data["stages"]):
            if not isinstance(stage_data, dict):
                errors.append(f"阶段 {i} 必须是字典类型")
                continue

            # 验证必填字段
            if "name" not in stage_data:
                errors.append(f"阶段 {i} 缺少 'name' 字段")
                continue

            stage_name = stage_data["name"]

            # 解析 enabled 字段，使用默认值 True (任务 5.5)
            enabled = stage_data.get("enabled", True)
            if not isinstance(enabled, bool):
                errors.append(f"阶段 '{stage_name}' 的 enabled 字段必须是布尔值，当前为 {type(enabled).__name__}")
                # 使用默认值继续
                enabled = True

            # 解析其他字段
            timeout = stage_data.get("timeout", 300)

            # 创建 StageConfig 对象 (任务 5.4)
            stage = StageConfig(
                name=stage_name,
                enabled=enabled,
                timeout=timeout
            )
            stages.append(stage)

        # 验证配置 (任务 5.6)
        validation_errors = validate_workflow_config(stages)
        if validation_errors:
            errors.extend(validation_errors)
            return stages, errors

        logger.info(f"成功加载工作流配置: {filepath}, 包含 {len(stages)} 个阶段")
        return stages, errors

    except Exception as e:
        error_msg = f"加载工作流配置时发生未知错误: {e}"
        logger.exception(error_msg)
        errors.append(error_msg)
        return [], errors
