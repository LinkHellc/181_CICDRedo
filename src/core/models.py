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

    def to_dict(self) -> dict:
        """转换为字典（排除 None 值）

        Returns:
            配置字典
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}

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
        required_fields = {
            "simulink_path": "Simulink 工程路径",
            "matlab_code_path": "MATLAB 代码路径",
            "a2l_path": "A2L 文件路径",
            "target_path": "目标文件路径",
            "iar_project_path": "IAR 工程路径",
        }

        for field_key, field_name in required_fields.items():
            value = getattr(self, field_key, "")
            if not value or not value.strip():
                errors.append(f"{field_name} 不能为空")

        return errors
