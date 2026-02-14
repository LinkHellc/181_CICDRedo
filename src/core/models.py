"""Core data models for MBD_CICDKits.

This module defines dataclass-based models for project configuration
following Architecture Decision 1.2 (Lightweight Data Containers).
"""

import dataclasses
from dataclasses import dataclass, fields
from typing import Optional, List
from enum import Enum

# 创建默认字段对象（在类外部创建，避免Python 3.11的bug）
_empty_dict_factory = dataclasses.field(default_factory=dict)
_empty_list_factory = dataclasses.field(default_factory=list)


class ValidationSeverity(Enum):
    """验证严重级别

    用于分类验证错误的严重程度。

    Attributes:
        ERROR: 阻止执行
        WARNING: 警告，可执行
        INFO: 信息，可执行
    """
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ProjectConfig:
    """项目配置数据模型

    使用 dataclass 实现轻量级数据容器。
    所有字段提供默认值，确保版本兼容性。

    Architecture Decision 1.2:
    - 使用 str 存储路径（便于 TOML 序列化）
    - 所有字段提供默认值
    - 使用 field(default_factory=...) 避免可变默认值陷阱
    """

    # 基本信息
    name: str = ""
    description: str = ""

    # 必需路径
    simulink_path: str = ""           # Simulink 工程路径
    matlab_code_path: str = ""        # MATLAB 代码路径
    a2l_path: str = ""                # A2L 文件路径
    target_path: str = ""             # 目标文件路径
    iar_project_path: str = ""        # IAR 工程路径

    # 可选字段（预留 Phase 2 扩展）
    custom_params: dict = _empty_dict_factory
    created_at: str = ""
    modified_at: str = ""

    # 工作流配置 (Story 2.1)
    workflow_id: str = ""              # 选中的工作流模板 ID
    workflow_name: str = ""            # 工作流名称（用于显示）

    def to_dict(self) -> dict:
        """转换为字典（排除 None 值和空字符串）

        Returns:
            配置字典
        """
        return {k: v for k, v in self.__dict__.items() if v is not None and v != ""}

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectConfig":
        """从字典创建配置对象，过滤未知字段

        Args:
            data: 配置字典

        Returns:
            ProjectConfig 实例
        """
        # 获取dataclass的有效字段名，过滤未知字段
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)

    def validate_required_fields(self) -> List[str]:
        """验证必需字段是否已填写

        Returns:
            错误列表，空列表表示验证通过
        """
        errors = []
        required_fields = [
            ("name", "项目名称"),
            ("simulink_path", "Simulink 工程路径"),
            ("matlab_code_path", "MATLAB 代码路径"),
            ("a2l_path", "A2L 文件路径"),
            ("target_path", "目标文件路径"),
            ("iar_project_path", "IAR 工程路径"),
        ]

        for field_key, field_name in required_fields:
            value = getattr(self, field_key, "")
            if not value or not value.strip():
                errors.append(f"{field_name} 不能为空")

        return errors


@dataclass
class StageConfig:
    """工作流阶段配置数据模型 (Story 2.1)

    表示工作流中的单个阶段配置。

    Architecture Decision 1.2:
    - 所有字段提供默认值
    - 支持序列化/反序列化
    """

    name: str = ""                    # 阶段名称（如 "matlab_gen", "iar_compile"）
    enabled: bool = True              # 是否启用此阶段
    timeout: int = 300                # 超时时间（秒）

    def to_dict(self) -> dict:
        """转换为字典

        Returns:
            阶段配置字典
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "timeout": self.timeout
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StageConfig":
        """从字典创建阶段配置对象

        Args:
            data: 阶段配置字典

        Returns:
            StageConfig 实例
        """
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class WorkflowConfig:
    """工作流配置数据模型 (Story 2.1)

    表示完整的工作流配置，包含多个阶段。

    Architecture Decision 1.2:
    - 所有字段提供默认值
    - 支持序列化/反序列化
    - 使用 field(default_factory=...) 避免可变默认值陷阱
    """

    id: str = ""                      # 工作流唯一标识
    name: str = ""                    # 工作流名称
    description: str = ""             # 工作流描述
    estimated_time: int = 0           # 预计执行时间（分钟）
    stages: List[StageConfig] = dataclasses.field(default_factory=list)  # 阶段列表

    def to_dict(self) -> dict:
        """转换为字典（包括嵌套的 stages）

        Returns:
            工作流配置字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "estimated_time": self.estimated_time,
            "stages": [stage.to_dict() for stage in self.stages]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowConfig":
        """从字典创建工作流配置对象（包括嵌套的 stages）

        Args:
            data: 工作流配置字典

        Returns:
            WorkflowConfig 实例
        """
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        # 处理嵌套的 stages
        if "stages" in filtered_data and isinstance(filtered_data["stages"], list):
            filtered_data["stages"] = [
                StageConfig.from_dict(stage_data) if isinstance(stage_data, dict) else stage_data
                for stage_data in filtered_data["stages"]
            ]

        return cls(**filtered_data)


@dataclass
class ValidationError:
    """验证错误

    表示配置验证过程中发现的单个错误。

    Architecture Decision 1.2:
    - 所有字段提供默认值
    - 支持序列化/反序列化

    Attributes:
        field: 错误字段名
        message: 错误消息
        severity: 严重级别
        suggestions: 修复建议列表
        stage: 相关阶段（可选）
    """
    field: str = ""
    message: str = ""
    severity: ValidationSeverity = ValidationSeverity.ERROR
    suggestions: list = dataclasses.field(default_factory=list)
    stage: str = ""

    def to_dict(self) -> dict:
        """转换为字典

        Returns:
            验证错误字典
        """
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity.value,
            "suggestions": self.suggestions,
            "stage": self.stage
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ValidationError":
        """从字典创建验证错误对象

        Args:
            data: 验证错误字典

        Returns:
            ValidationError 实例
        """
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        # 处理 severity 字符串到枚举的转换
        if "severity" in filtered_data and isinstance(filtered_data["severity"], str):
            filtered_data["severity"] = ValidationSeverity(filtered_data["severity"])

        return cls(**filtered_data)


class StageStatus(Enum):
    """阶段执行状态

    用于表示工作流中单个阶段的执行状态。

    Attributes:
        PENDING: 待执行
        RUNNING: 执行中
        COMPLETED: 已完成
        FAILED: 失败
        CANCELLED: 已取消
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BuildState(Enum):
    """构建状态 (Story 2.4 Task 1.2)

    用于表示整个构建流程的执行状态。

    Attributes:
        IDLE: 空闲
        RUNNING: 运行中
        COMPLETED: 已完成
        FAILED: 失败
        CANCELLED: 已取消
    """
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StageResult:
    """阶段执行结果

    表示工作流中单个阶段的执行结果。

    Architecture Decision 1.2:
    - 所有字段提供默认值
    - 支持序列化/反序列化
    - 使用 field(default_factory=...) 避免可变默认值陷阱

    Attributes:
        status: 执行状态
        message: 状态消息
        output_files: 输出文件列表
        error: 异常对象（如果失败）
        suggestions: 修复建议列表
        execution_time: 执行时间（秒）
    """
    status: StageStatus = StageStatus.PENDING
    message: str = ""
    output_files: List[str] = dataclasses.field(default_factory=list)
    error: Optional[Exception] = None
    suggestions: List[str] = dataclasses.field(default_factory=list)
    execution_time: float = 0.0

    def to_dict(self) -> dict:
        """转换为字典

        Returns:
            阶段结果字典
        """
        return {
            "status": self.status.value,
            "message": self.message,
            "output_files": self.output_files,
            "error": str(self.error) if self.error else None,
            "suggestions": self.suggestions,
            "execution_time": self.execution_time
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StageResult":
        """从字典创建阶段结果对象

        Args:
            data: 阶段结果字典

        Returns:
            StageResult 实例
        """
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        # 处理 status 字符串到枚举的转换
        if "status" in filtered_data and isinstance(filtered_data["status"], str):
            filtered_data["status"] = StageStatus(filtered_data["status"])

        return cls(**filtered_data)


@dataclass
class BuildContext:
    """构建上下文 - 在阶段间传递状态

    用于在工作流执行期间在各个阶段之间传递状态和数据。

    Architecture Decision 1.2:
    - config: 只读全局配置
    - state: 可写阶段状态（用于传递）
    - log_callback: 统一日志接口

    Story 2.5 - 任务 6.5:
    - signal_emit: 信号发送回调（用于发送阶段完成时间和时长到 UI）

    Attributes:
        config: 全局配置字典（只读）
        state: 阶段间传递的状态字典（可写）
        log_callback: 日志回调函数
        signal_emit: 信号发送回调函数（可选）
    """
    config: dict = dataclasses.field(default_factory=dict)
    state: dict = dataclasses.field(default_factory=dict)
    log_callback: Optional[callable] = None
    signal_emit: Optional[callable] = None


@dataclass
class StageExecution:
    """阶段执行信息 (Story 2.4 Task 1.3)

    表示单个阶段的执行信息。

    Architecture Decision 1.2:
    - 所有字段提供默认值
    - 使用 field(default_factory=...) 避免可变默认值陷阱

    Attributes:
        name: 阶段名称
        status: 执行状态
        start_time: 开始时间（time.monotonic）
        end_time: 结束时间
        duration: 执行时长（秒）
        error_message: 错误消息
        output_files: 输出文件列表
    """
    name: str = ""
    status: BuildState = BuildState.IDLE
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    error_message: str = ""
    output_files: List[str] = dataclasses.field(default_factory=list)


@dataclass
class BuildExecution:
    """构建执行信息 (Story 2.4 Task 1.1)

    表示整个构建流程的执行信息。

    Architecture Decision 1.2:
    - 所有字段提供默认值
    - 使用 field(default_factory=...) 避免可变默认值陷阱

    Attributes:
        project_name: 项目名称
        workflow_id: 工作流 ID
        state: 构建状态
        start_time: 开始时间（time.monotonic）
        end_time: 结束时间
        duration: 总执行时长（秒）
        current_stage: 当前阶段名称
        progress_percent: 进度百分比（0-100）
        stages: 阶段执行列表
        error_message: 错误消息
    """
    project_name: str = ""
    workflow_id: str = ""
    state: BuildState = BuildState.IDLE
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    current_stage: str = ""
    progress_percent: int = 0
    stages: List[StageExecution] = dataclasses.field(default_factory=list)
    error_message: str = ""

    def get(self, key: str, default=None):
        """从状态中获取值

        Args:
            key: 键名
            default: 默认值

        Returns:
            状态值
        """
        return self.state.get(key, default)

    def set(self, key: str, value):
        """设置状态值

        Args:
            key: 键名
            value: 值
        """
        self.state[key] = value

    def log(self, message: str):
        """记录日志

        Args:
            message: 日志消息
        """
        if self.log_callback:
            self.log_callback(message)

    def emit_signal(self, signal_name: str, *args, **kwargs):
        """发送信号到 UI

        Story 2.5 - 任务 6.5:
        - 通过信号发送阶段完成时间和时长到 UI

        Args:
            signal_name: 信号名称
            *args: 信号位置参数
            **kwargs: 信号关键字参数
        """
        if self.signal_emit:
            self.signal_emit(signal_name, *args, **kwargs)


@dataclass
class ValidationResult:
    """验证结果

    表示配置验证的完整结果。

    Architecture Decision 1.2:
    - 所有字段提供默认值
    - 支持序列化/反序列化
    - 使用 field(default_factory=...) 避免可变默认值陷阱

    Attributes:
        is_valid: 是否通过验证
        errors: 错误列表
        warning_count: 警告数量
        error_count: 错误数量
    """
    is_valid: bool = True
    errors: List[ValidationError] = dataclasses.field(default_factory=list)
    warning_count: int = 0
    error_count: int = 0

    def to_dict(self) -> dict:
        """转换为字典

        Returns:
            验证结果字典
        """
        return {
            "is_valid": self.is_valid,
            "errors": [error.to_dict() for error in self.errors],
            "warning_count": self.warning_count,
            "error_count": self.error_count
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ValidationResult":
        """从字典创建验证结果对象

        Args:
            data: 验证结果字典

        Returns:
            ValidationResult 实例
        """
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        # 处理嵌套的 errors
        if "errors" in filtered_data and isinstance(filtered_data["errors"], list):
            filtered_data["errors"] = [
                ValidationError.from_dict(error_data) if isinstance(error_data, dict) else error_data
                for error_data in filtered_data["errors"]
            ]

        return cls(**filtered_data)

    def add_error(self, error: ValidationError) -> None:
        """添加一个验证错误

        Args:
            error: 验证错误对象
        """
        self.errors.append(error)
        if error.severity == ValidationSeverity.ERROR:
            self.error_count += 1
        elif error.severity == ValidationSeverity.WARNING:
            self.warning_count += 1
        self.is_valid = (self.error_count == 0)

    def get_errors_by_severity(self, severity: ValidationSeverity) -> List[ValidationError]:
        """按严重级别获取错误列表

        Args:
            severity: 严重级别

        Returns:
            指定严重级别的错误列表
        """
        return [e for e in self.errors if e.severity == severity]


@dataclass
class A2LHeaderReplacementConfig:
    """A2L 头文件替换配置 (Story 2.10 - 任务 1.1-1.5)

    用于 A2L 文件 XCP 头文件内容替换的配置。

    Architecture Decision 1.2:
    - 所有字段提供默认值
    - 使用 field(default_factory=...) 避免可变默认值陷阱
    - 使用 Path 对象处理路径（便于序列化）

    Attributes:
        xcp_template_path: XCP 头文件模板路径
        a2l_source_path: A2L 源文件路径（从 BuildContext 获取）
        output_dir: 输出目录路径（从 BuildContext 获取）
        timestamp_format: 时间戳格式（默认 "_%Y_%m_%d_%H_%M"）
        output_prefix: 输出文件前缀（默认 "tmsAPP_upAdress"）
        encoding: 文件编码（默认 "utf-8"）
        backup_before_replace: 替换前备份（默认 True）
    """
    xcp_template_path: str = "resources/templates/奇瑞热管理XCP头文件.txt"
    a2l_source_path: str = ""
    output_dir: str = ""
    timestamp_format: str = "_%Y_%m_%d_%H_%M"
    output_prefix: str = "tmsAPP_upAdress"
    encoding: str = "utf-8"
    backup_before_replace: bool = True
