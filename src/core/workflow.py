"""Workflow validation and execution module for MBD_CICDKits.

This module implements workflow configuration validation following
Architecture Decision 1.3 (Configuration Validation) and workflow execution
following Architecture Decision 1.1 (Stage Interface Pattern).
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Set, Optional, Callable, TYPE_CHECKING

from core.models import (
    WorkflowConfig,
    ProjectConfig,
    ValidationError,
    ValidationResult,
    ValidationSeverity,
    BuildContext,
    StageResult,
    StageStatus
)

# 类型注解导入（仅在类型检查时使用）
if TYPE_CHECKING:
    from core.models import StageConfig

logger = logging.getLogger(__name__)

# 默认超时值（秒）
DEFAULT_TIMEOUT = 300

# 阶段执行器映射 (Story 2.5 - 任务 8, Story 2.7 - 任务 6, Story 2.8 - 任务 5, Story 2.9 - 任务 9)
# 映射阶段名称到对应的执行函数
STAGE_EXECUTORS: Dict[str, Callable] = {
    # Story 2.5: MATLAB 代码生成阶段
    "matlab_gen": lambda config, context: _execute_matlab_gen(config, context),
    # Story 2.6: 文件处理阶段
    "file_process": lambda config, context: _execute_file_process(config, context),
    # Story 2.7: 文件移动阶段
    "file_move": lambda config, context: _execute_file_move(config, context),
    # Story 2.8: IAR 编译阶段
    "iar_compile": lambda config, context: _execute_iar_compile(config, context),
    # Story 2.9: A2L 处理阶段
    "a2l_process": lambda config, context: _execute_a2l_process(config, context),
    # 后续 Story (2.10-2.12) 会逐步实现
    # "package": stages.package.execute_stage,
}


def _execute_file_process(config, context) -> StageResult:
    """执行文件处理阶段（内部包装函数）

    Story 2.6 - 任务 8.1-8.3:
    - 在 STAGE_EXECUTORS 中注册 file_process
    - 指向 stages.file_process.execute_stage
    - 确保阶段按工作流顺序执行

    Args:
        config: 阶段配置
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    try:
        # 动态导入以避免循环依赖
        from stages.file_process import execute_stage
        return execute_stage(config, context)
    except ImportError as e:
        logger.error(f"无法导入 file_process 模块: {e}")
        return StageResult(
            status=StageStatus.FAILED,
            message=f"文件处理模块未实现",
            error=e,
            suggestions=["确保 Story 2.6 已正确实现"]
        )


def _execute_file_move(config, context) -> StageResult:
    """执行文件移动阶段（内部包装函数）

    Story 2.7 - 任务 6.1-6.3:
    - 在 STAGE_EXECUTORS 中注册 file_move
    - 指向 stages.file_move.execute_stage
    - 确保阶段按工作流顺序执行

    Args:
        config: 阶段配置
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    try:
        # 动态导入以避免循环依赖
        from stages.file_move import execute_stage
        return execute_stage(config, context)
    except ImportError as e:
        logger.error(f"无法导入 file_move 模块: {e}")
        return StageResult(
            status=StageStatus.FAILED,
            message=f"文件移动模块未实现",
            error=e,
            suggestions=["确保 Story 2.7 已正确实现"]
        )


def _execute_iar_compile(config, context) -> StageResult:
    """执行 IAR 编译阶段（内部包装函数）

    Story 2.8 - 任务 5.1-5.3:
    - 在 STAGE_EXECUTORS 中注册 iar_compile
    - 指向 stages.iar_compile.execute_stage
    - 确保阶段按工作流顺序执行
    - 将编译输出传递给下一阶段（A2L 处理）

    Args:
        config: 阶段配置
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    try:
        # 动态导入以避免循环依赖
        from stages.iar_compile import execute_stage
        return execute_stage(config, context)
    except ImportError as e:
        logger.error(f"无法导入 iar_compile 模块: {e}")
        return StageResult(
            status=StageStatus.FAILED,
            message=f"IAR 编译模块未实现",
            error=e,
            suggestions=["确保 Story 2.8 已正确实现"]
        )


def _execute_matlab_gen(config, context) -> StageResult:
    """执行 MATLAB 代码生成阶段（内部包装函数）

    Story 2.5 - 任务 8.1-8.3:
    - 在 STAGE_EXECUTORS 中注册 matlab_gen
    - 指向 stages.matlab_gen.execute_stage
    - 确保阶段按工作流顺序执行

    Args:
        config: 阶段配置
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    try:
        # 动态导入以避免循环依赖
        from stages.matlab_gen import execute_stage
        return execute_stage(config, context)
    except ImportError as e:
        logger.error(f"无法导入 matlab_gen 模块: {e}")
        return StageResult(
            status=StageStatus.FAILED,
            message=f"MATLAB 代码生成模块未实现",
            error=e,
            suggestions=["确保 Story 2.5 已正确实现"]
        )


def _execute_a2l_process(config, context) -> StageResult:
    """执行 A2L 处理阶段（内部包装函数）

    Story 2.9 - 任务 9.1-9.4:
    - 在 STAGE_EXECUTORS 中注册 a2l_process
    - 指向 stages.a2l_process.execute_stage
    - 确保阶段按工作流顺序执行（iar_compile → a2l_process）
    - 测试工作流集成

    Story 2.10 - 任务 8.1-8.5:
    - 更新 a2l_process 执行器为 XCP 头文件替换阶段
    - 指向 stages.a2l_process.execute_xcp_header_replacement_stage
    - 确保 a2l_process 在 iar_compile 之后执行（依赖关系）
    - 确保在 package 之前执行（输出文件传递）
    - 在 BuildContext 中传递 A2L 文件路径给下一阶段

    Args:
        config: 阶段配置
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    try:
        # 动态导入以避免循环依赖
        from stages.a2l_process import execute_xcp_header_replacement_stage
        return execute_xcp_header_replacement_stage(config, context)
    except ImportError as e:
        logger.error(f"无法导入 a2l_process 模块: {e}")
        return StageResult(
            status=StageStatus.FAILED,
            message=f"A2L 处理模块未实现",
            error=e,
            suggestions=["确保 Story 2.9 和 Story 2.10 已正确实现"]
        )

# 阶段依赖规则（Story 2.3 Task 2.2, Story 2.7 任务 6.3, Story 2.8 任务 5.3）
STAGE_DEPENDENCIES = {
    "matlab_gen": [],           # 无依赖
    "file_process": ["matlab_gen"],  # 依赖 matlab_gen
    "file_move": ["file_process"],  # 依赖 file_process (Story 2.7)
    "iar_compile": ["file_move"],  # 依赖 file_move (Story 2.8)
    "a2l_process": ["iar_compile"],  # 依赖 iar_compile
    "package": ["iar_compile", "a2l_process"]  # 依赖 iar_compile 和 a2l_process
}

# 核心阶段依赖关系（Story 2.14 - 任务 2.2）
# 定义 5 个核心阶段的依赖关系（简化版，不包含 file_move）
CORE_STAGE_DEPENDENCIES = {
    "matlab_gen": [],           # 无依赖
    "file_process": ["matlab_gen"],  # 依赖 matlab_gen
    "iar_compile": ["file_process"],  # 依赖 file_process
    "a2l_process": ["iar_compile"],  # 依赖 iar_compile
    "package": ["a2l_process"]  # 依赖 a2l_process
}

# 阶段执行顺序（用于检查顺序合理性）
STAGE_ORDER = [
    "matlab_gen",
    "file_process",
    "file_move",  # Story 2.7: 文件移动阶段
    "iar_compile",
    "a2l_process",
    "package"
]

# 必需参数规则（Story 2.3 Task 3.2, Story 2.7 任务 6.2）
REQUIRED_PARAMS = {
    "matlab_gen": ["simulink_path", "matlab_code_path"],
    "file_process": ["matlab_code_path", "target_path"],
    "file_move": ["matlab_code_path"],  # Story 2.7: 需要 matlab_code_path
    "iar_compile": ["iar_project_path", "matlab_code_path"],
    "a2l_process": ["a2l_path", "target_path"],
    "package": ["target_path"]
}


def validate_stage_dependencies(workflow_config: WorkflowConfig) -> List[ValidationError]:
    """验证阶段依赖关系 (Story 2.3 Task 2)

    Args:
        workflow_config: 工作流配置对象

    Returns:
        验证错误列表（空列表表示通过）
    """
    errors = []

    if not workflow_config.stages:
        logger.warning("工作流没有配置任何阶段")
        return errors

    # 获取所有启用阶段的名称
    enabled_stages = {stage.name for stage in workflow_config.stages if stage.enabled}

    if not enabled_stages:
        error = ValidationError(
            field="workflow.stages",
            message="至少需要启用一个阶段",
            severity=ValidationSeverity.ERROR,
            suggestions=[
                "启用至少一个工作流阶段",
                "检查工作流配置"
            ]
        )
        errors.append(error)
        return errors

    # 检查每个启用阶段的依赖（Task 2.3）
    for stage in workflow_config.stages:
        if not stage.enabled:
            continue

        if stage.name not in STAGE_DEPENDENCIES:
            # 未知阶段，跳过或警告
            logger.warning(f"未知阶段: {stage.name}")
            continue

        dependencies = STAGE_DEPENDENCIES[stage.name]

        # 检查依赖阶段是否启用
        for dep_stage in dependencies:
            if dep_stage not in enabled_stages:
                error = ValidationError(
                    field=f"workflow.stages.{stage.name}.enabled",
                    message=f'阶段 "{stage.name}" 已启用，但依赖阶段 "{dep_stage}" 未启用',
                    severity=ValidationSeverity.ERROR,
                    suggestions=[
                        f'启用 "{dep_stage}" 阶段',
                        f'禁用 "{stage.name}" 阶段'
                    ],
                    stage=stage.name
                )
                errors.append(error)
                logger.warning(f"阶段依赖检查失败: {error.message}")

    # 检查阶段执行顺序是否合理（Task 2.4）
    enabled_stage_names = [stage.name for stage in workflow_config.stages if stage.enabled]
    order_errors = _check_stage_order(enabled_stage_names)
    errors.extend(order_errors)

    return errors


def _check_stage_order(stage_names: List[str]) -> List[ValidationError]:
    """检查阶段执行顺序是否合理

    Args:
        stage_names: 启用的阶段名称列表

    Returns:
        顺序错误列表
    """
    errors = []

    # 创建阶段名称到顺序索引的映射
    order_index = {stage: idx for idx, stage in enumerate(STAGE_ORDER)}

    # 检查是否违反依赖顺序
    # 对于每个阶段，确保其依赖阶段在前面
    for i, stage in enumerate(stage_names):
        if stage not in order_index:
            continue  # 未知阶段，跳过

        # 检查前面的所有阶段
        for j in range(i):
            prev_stage = stage_names[j]
            if prev_stage not in order_index:
                continue

            # 如果前面的阶段应该在当前阶段之后，则顺序错误
            if order_index[prev_stage] > order_index[stage]:
                # 但如果它们没有直接依赖关系，可能不是错误
                # 只有当前阶段依赖于前面的某个更前面的阶段时才报错
                if stage in STAGE_DEPENDENCIES:
                    for dep in STAGE_DEPENDENCIES[stage]:
                        if dep in stage_names[:j]:
                            error = ValidationError(
                                field="workflow.stages",
                                message=f'阶段执行顺序不合理: "{prev_stage}" 应在 "{stage}" 之前',
                                severity=ValidationSeverity.WARNING,
                                suggestions=[
                                    '调整阶段执行顺序',
                                    '检查阶段依赖关系'
                                ],
                                stage=stage
                            )
                            errors.append(error)
                            break

    return errors


def validate_required_params(workflow_config: WorkflowConfig, project_config: ProjectConfig) -> List[ValidationError]:
    """验证必需参数 (Story 2.3 Task 3)

    Args:
        workflow_config: 工作流配置对象
        project_config: 项目配置对象

    Returns:
        验证错误列表（空列表表示通过）
    """
    errors = []

    if not workflow_config.stages:
        return errors

    # 将项目配置转换为字典便于访问
    config_dict = project_config.to_dict()

    # 检查每个启用阶段的必需参数（Task 3.3）
    for stage in workflow_config.stages:
        if not stage.enabled:
            continue

        if stage.name not in REQUIRED_PARAMS:
            logger.warning(f"未知阶段: {stage.name}")
            continue

        required = REQUIRED_PARAMS[stage.name]

        # 检查必需参数是否存在
        for param in required:
            param_value = config_dict.get(param, "")

            # 处理 Path 对象
            if isinstance(param_value, Path):
                param_value = str(param_value)

            if not param_value or (isinstance(param_value, str) and not param_value.strip()):
                # 参数未配置或为空
                error = ValidationError(
                    field=f"project_config.{param}",
                    message=f'阶段 "{stage.name}" 需要参数 "{param}"，但未配置',
                    severity=ValidationSeverity.ERROR,
                    suggestions=[
                        f'在项目配置中设置 {param}',
                        f'确保 {param} 指向有效的路径或配置'
                    ],
                    stage=stage.name
                )
                errors.append(error)
                logger.warning(f"必需参数检查失败: {error.message}")

        # 验证超时参数的有效性（Task 3.4）
        if stage.timeout <= 0:
            error = ValidationError(
                field=f"workflow.stages.{stage.name}.timeout",
                message=f'阶段 "{stage.name}" 的超时值无效: {stage.timeout} 秒',
                severity=ValidationSeverity.ERROR,
                suggestions=[
                    '设置超时值为正整数（建议 300 秒以上）',
                    '检查工作流配置文件'
                ],
                stage=stage.name
            )
            errors.append(error)
            logger.warning(f"超时值检查失败: {error.message}")

    return errors


def validate_paths_exist(project_config: ProjectConfig) -> List[ValidationError]:
    """验证路径存在性 (Story 2.3 Task 4)

    Args:
        project_config: 项目配置对象

    Returns:
        验证错误列表（空列表表示通过）
    """
    errors = []

    # 将配置转换为字典
    config_dict = project_config.to_dict()

    # 路径字段列表（Task 4.2）
    path_fields = [
        "simulink_path",
        "matlab_code_path",
        "iar_project_path",
        "a2l_path",
        "target_path"
    ]

    # 检查每个路径字段（Task 4.3）
    for field_name in path_fields:
        path_value = config_dict.get(field_name, "")

        # 处理 Path 对象和字符串
        if isinstance(path_value, Path):
            path_str = str(path_value)
            path_obj = path_value
        elif isinstance(path_value, str):
            path_str = path_value
            if not path_str.strip():
                # 路径为空，跳过（由必需参数验证处理）
                continue
            path_obj = Path(path_str)
        else:
            # 路径为其他类型，跳过
            continue

        # 检查路径是否存在
        if not path_obj.exists():
            error = ValidationError(
                field=f"project_config.{field_name}",
                message=f'路径不存在: {path_str}',
                severity=ValidationSeverity.ERROR,
                suggestions=[
                    '检查路径拼写是否正确',
                    '确认目录/文件是否已创建',
                    '使用浏览按钮选择正确的路径',
                    '如果是网络路径，检查网络连接'
                ]
            )
            errors.append(error)
            logger.warning(f"路径不存在: {path_str}")
        else:
            # 路径存在，检查类型是否正确
            # 对于 a2l_path 和 iar_project_path，应该是文件
            # 对于其他路径（simulink_path, matlab_code_path, target_path），应该是目录
            if field_name in ["a2l_path", "iar_project_path"] and not path_obj.is_file():
                error = ValidationError(
                    field=f"project_config.{field_name}",
                    message=f'{field_name} 应该是文件，但指向了目录: {path_str}',
                    severity=ValidationSeverity.ERROR,
                    suggestions=[
                        f'选择正确的文件而不是目录',
                        '检查路径是否正确'
                    ]
                )
                errors.append(error)
            elif field_name not in ["a2l_path", "iar_project_path"] and not path_obj.is_dir():
                error = ValidationError(
                    field=f"project_config.{field_name}",
                    message=f'路径应该是目录，但指向了文件: {path_str}',
                    severity=ValidationSeverity.ERROR,
                    suggestions=[
                        '选择目录而不是文件',
                        '检查路径是否正确'
                    ]
                )
                errors.append(error)

    return errors


def validate_workflow_config(workflow_config: WorkflowConfig, project_config: ProjectConfig) -> ValidationResult:
    """统一验证入口 (Story 2.3 Task 5)

    依次调用所有验证函数，收集所有验证错误到 ValidationResult。

    Args:
        workflow_config: 工作流配置对象
        project_config: 项目配置对象

    Returns:
        验证结果对象（包含错误列表和统计信息）
    """
    result = ValidationResult(is_valid=True)

    logger.info("开始验证工作流配置...")

    # 1. 验证阶段依赖关系（Task 5.2）
    logger.debug("验证阶段依赖关系...")
    dependency_errors = validate_stage_dependencies(workflow_config)
    for error in dependency_errors:
        result.add_error(error)

    # 2. 验证必需参数（Task 5.2）
    logger.debug("验证必需参数...")
    param_errors = validate_required_params(workflow_config, project_config)
    for error in param_errors:
        result.add_error(error)

    # 3. 验证路径存在性（Task 5.2）
    logger.debug("验证路径存在性...")
    path_errors = validate_paths_exist(project_config)
    for error in path_errors:
        result.add_error(error)

    # 统计验证结果
    if result.error_count > 0:
        logger.warning(f"验证失败: 发现 {result.error_count} 个错误, {result.warning_count} 个警告")
        result.is_valid = False
    elif result.warning_count > 0:
        logger.info(f"验证通过（有警告）: {result.warning_count} 个警告")
    else:
        logger.info("验证通过: 无错误")

    return result


def get_stage_dependency_info(stage_name: str) -> Dict:
    """获取阶段的依赖信息

    Args:
        stage_name: 阶段名称

    Returns:
        依赖信息字典，包含依赖阶段列表和描述
    """
    if stage_name not in STAGE_DEPENDENCIES:
        return {
            "dependencies": [],
            "description": "未知阶段"
        }

    deps = STAGE_DEPENDENCIES[stage_name]

    # 生成依赖描述
    if not deps:
        description = "无依赖，可以独立执行"
    else:
        description = f"依赖阶段: {', '.join(deps)}"

    return {
        "dependencies": deps,
        "description": description
    }


def get_required_params_info(stage_name: str) -> List[str]:
    """获取阶段所需的参数列表

    Args:
        stage_name: 阶段名称

    Returns:
        必需参数名称列表
    """
    return REQUIRED_PARAMS.get(stage_name, [])


# =============================================================================
# Story 2.14: 启用/禁用工作流阶段 - 依赖关系管理
# =============================================================================

def get_stage_dependencies(stage_name: str) -> List[str]:
    """获取阶段的前置依赖 (Story 2.14 - 任务 2.3)

    获取指定阶段的前置依赖阶段列表。

    Args:
        stage_name: 阶段名称

    Returns:
        前置依赖阶段名称列表

    Examples:
        >>> get_stage_dependencies("iar_compile")
        ["matlab_gen", "file_process"]
        >>> get_stage_dependencies("matlab_gen")
        []
    """
    if stage_name not in CORE_STAGE_DEPENDENCIES:
        logger.warning(f"未知阶段: {stage_name}")
        return []

    dependencies = CORE_STAGE_DEPENDENCIES[stage_name]

    # 递归获取所有前置依赖（包括间接依赖）
    # 注意：先递归获取间接依赖，再添加直接依赖，确保顺序正确
    all_dependencies = []
    for dep in dependencies:
        # 先获取间接依赖
        all_dependencies.extend(get_stage_dependencies(dep))
        # 再添加当前依赖
        all_dependencies.append(dep)

    # 去重并保持顺序
    seen = set()
    result = []
    for dep in all_dependencies:
        if dep not in seen:
            seen.add(dep)
            result.append(dep)

    logger.debug(f"阶段 {stage_name} 的前置依赖: {result}")
    return result


def get_dependent_stages(stage_name: str) -> List[str]:
    """获取阶段的后置依赖 (Story 2.14 - 任务 2.4)

    获取依赖指定阶段的所有后续阶段列表。

    Args:
        stage_name: 阶段名称

    Returns:
        后置依赖阶段名称列表

    Examples:
        >>> get_dependent_stages("matlab_gen")
        ["file_process", "iar_compile", "a2l_process", "package"]
        >>> get_dependent_stages("package")
        []
    """
    if stage_name not in CORE_STAGE_DEPENDENCIES:
        logger.warning(f"未知阶段: {stage_name}")
        return []

    dependents = []

    # 查找所有依赖当前阶段的阶段
    for name, deps in CORE_STAGE_DEPENDENCIES.items():
        if stage_name in deps:
            dependents.append(name)
            # 递归获取后置依赖的后置依赖
            dependents.extend(get_dependent_stages(name))

    # 去重并保持顺序
    seen = set()
    result = []
    for dep in dependents:
        if dep not in seen:
            seen.add(dep)
            result.append(dep)

    logger.debug(f"阶段 {stage_name} 的后置依赖: {result}")
    return result


def adjust_stage_dependencies(
    stages: List,
    stage_name: str,
    enabled: bool
) -> None:
    """自动调整阶段依赖关系 (Story 2.14 - 任务 3)

    根据阶段启用/禁用状态，自动调整相关阶段的启用状态。

    Args:
        stages: 阶段配置列表
        stage_name: 被修改的阶段名称
        enabled: 新的启用状态（True=启用，False=禁用）

    Examples:
        >>> # 禁用 file_process，自动禁用 iar_compile, a2l_process, package
        >>> adjust_stage_dependencies(stages, "file_process", False)

        >>> # 启用 package，自动启用 a2l_process, iar_compile, file_process, matlab_gen
        >>> adjust_stage_dependencies(stages, "package", True)
    """
    if not stages:
        logger.warning("阶段配置列表为空")
        return

    # 查找被修改的阶段
    target_stage = None
    for stage in stages:
        if hasattr(stage, "name") and stage.name == stage_name:
            target_stage = stage
            break

    if not target_stage:
        logger.warning(f"未找到阶段: {stage_name}")
        return

    # 更新被修改的阶段
    if hasattr(target_stage, "enabled"):
        target_stage.enabled = enabled
        logger.debug(f"更新阶段 {stage_name} 的启用状态为: {enabled}")

    if enabled:
        # 启用阶段时，自动启用所有前置阶段
        logger.debug(f"启用阶段 {stage_name}，检查前置依赖...")
        deps = get_stage_dependencies(stage_name)

        for dep_name in deps:
            # 查找依赖阶段
            dep_stage = None
            for stage in stages:
                if hasattr(stage, "name") and stage.name == dep_name:
                    dep_stage = stage
                    break

            if dep_stage and hasattr(dep_stage, "enabled"):
                if not dep_stage.enabled:
                    # 递归启用前置阶段
                    logger.debug(f"自动启用前置阶段: {dep_name}")
                    adjust_stage_dependencies(stages, dep_name, True)
                else:
                    logger.debug(f"前置阶段 {dep_name} 已启用")
    else:
        # 禁用阶段时，自动禁用所有后置阶段
        logger.debug(f"禁用阶段 {stage_name}，检查后置依赖...")
        dependents = get_dependent_stages(stage_name)

        for dep_name in dependents:
            # 查找后置依赖阶段
            dep_stage = None
            for stage in stages:
                if hasattr(stage, "name") and stage.name == dep_name:
                    dep_stage = stage
                    break

            if dep_stage and hasattr(dep_stage, "enabled"):
                if dep_stage.enabled:
                    # 递归禁用后置阶段
                    logger.debug(f"自动禁用后置阶段: {dep_name}")
                    adjust_stage_dependencies(stages, dep_name, False)
                else:
                    logger.debug(f"后置阶段 {dep_name} 已禁用")


def execute_workflow(
    workflow_config: WorkflowConfig,
    context: BuildContext,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    stage_callback: Optional[Callable[[str, bool], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None
) -> bool:
    """执行工作流 (Story 2.4 Task 2)

    按顺序执行工作流中所有启用的阶段。

    Architecture Decision 1.1:
    - 统一阶段签名
    - 按顺序执行阶段
    - 阶段间通过 BuildContext 传递状态

    Architecture Decision 2.1:
    - 使用 time.monotonic() 记录时间
    - 支持取消检查

    Args:
        workflow_config: 工作流配置
        context: 构建上下文
        progress_callback: 进度回调 (百分比, 消息)
        stage_callback: 阶段完成回调 (阶段名, 成功)
        cancel_check: 取消检查回调

    Returns:
        bool: 是否全部成功
    """
    # 记录开始时间 - 使用 monotonic 避免系统时间调整影响
    start_time = time.monotonic()
    context.state["build_start_time"] = start_time

    logger.info(f"开始执行工作流: {workflow_config.name}")
    context.log(f"工作流开始: {workflow_config.name}")

    # 获取启用的阶段 (按顺序)
    enabled_stages = [
        s for s in workflow_config.stages
        if s.enabled
    ]

    if not enabled_stages:
        logger.warning("没有启用的阶段")
        context.log("警告: 没有启用的阶段")
        return False

    total_stages = len(enabled_stages)

    # 执行每个阶段
    for i, stage_config in enumerate(enabled_stages):
        # 检查取消
        if cancel_check and cancel_check():
            logger.info("工作流被取消")
            context.log("工作流已被用户取消")
            context.state["cancel_reason"] = "user_requested"
            return False

        # 更新进度
        stage_name = stage_config.name
        progress = int((i / total_stages) * 100)

        if progress_callback:
            progress_callback(progress, f"执行阶段: {stage_name}")

        logger.info(f"开始执行阶段 {i+1}/{total_stages}: {stage_name}")

        # 执行阶段 (Story 2.5 - 任务 8)
        if stage_name in STAGE_EXECUTORS:
            # 使用注册的阶段执行器
            context.log(f"阶段 {stage_name} 执行中...")
            executor = STAGE_EXECUTORS[stage_name]
            result = executor(stage_config, context)
        else:
            # 占位实现 - 尚未实现的阶段
            context.log(f"阶段 {stage_name} 尚未实现（占位实现）...")
            result = StageResult(
                status=StageStatus.COMPLETED,
                message=f"阶段 {stage_name} 执行成功 (占位实现)"
            )

        # 通知阶段完成
        if stage_callback:
            stage_callback(stage_name, result.status == StageStatus.COMPLETED)

        # 检查阶段是否失败
        if result.status == StageStatus.FAILED:
            logger.error(f"阶段 {stage_name} 失败: {result.message}")
            context.log(f"阶段 {stage_name} 失败: {result.message}")
            context.state["failed_stage"] = stage_name
            context.state["failure_reason"] = result.message

            if progress_callback:
                progress_callback(progress, f"阶段失败: {stage_name}")

            return False

        # 保存阶段输出到上下文
        context.state[f"{stage_name}_output"] = result.output_files or []

    # 计算总执行时间
    elapsed = time.monotonic() - start_time
    context.state["build_duration"] = elapsed

    logger.info(f"工作流执行完成，耗时: {elapsed:.2f} 秒")
    context.log(f"工作流执行完成，耗时: {elapsed:.2f} 秒")

    if progress_callback:
        progress_callback(100, "工作流完成")

    return True
