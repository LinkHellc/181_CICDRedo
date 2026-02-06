"""Core data models for MBD_CICDKits.

This module defines dataclass-based models for project configuration
following Architecture Decision 1.2 (Lightweight Data Containers).
"""

from dataclasses import dataclass, field
from dataclasses import fields
from typing import Optional


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
    custom_params: dict = field(default_factory=dict)
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

    def validate_required_fields(self) -> list[str]:
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
    stages: list[StageConfig] = field(default_factory=list)  # 阶段列表

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
