"""Core data models for MBD_CICDKits.

This module defines dataclass-based models for project configuration
following Architecture Decision 1.2 (Lightweight Data Containers).
"""

from dataclasses import dataclass, field
from dataclasses import fields
from typing import Optional, List
from enum import Enum

# 创建默认字段对象（在类外部创建，避免Python 3.11的bug）
_empty_dict_factory = field(default_factory=dict)
_empty_list_factory = field(default_factory=list)


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
    stages: List[StageConfig] = _empty_list_factory  # 阶段列表

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
    suggestions: list = _empty_list_factory
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
    errors: List[ValidationError] = _empty_list_factory
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
