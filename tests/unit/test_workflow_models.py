"""Unit tests for workflow configuration models (Story 2.1)."""

import pytest
from pathlib import Path

# 确保 src 在路径中
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.models import StageConfig, WorkflowConfig


class TestStageConfig:
    """测试 StageConfig 数据模型 (Story 2.1 Task 1.1)"""

    def test_stage_config_defaults(self):
        """测试阶段配置默认值

        Given: 创建空的 StageConfig
        Then: 所有字段应有正确的默认值
        """
        stage = StageConfig()
        assert stage.name == ""
        assert stage.enabled is True
        assert stage.timeout == 300

    def test_stage_config_creation(self):
        """测试阶段配置创建

        Given: 提供阶段配置参数
        When: 创建 StageConfig 实例
        Then: 实例应具有提供的值
        """
        stage = StageConfig(
            name="matlab_gen",
            enabled=True,
            timeout=1800
        )
        assert stage.name == "matlab_gen"
        assert stage.enabled is True
        assert stage.timeout == 1800

    def test_stage_config_to_dict(self):
        """测试阶段配置转换为字典

        Given: 创建 StageConfig 实例
        When: 调用 to_dict()
        Then: 应返回包含所有字段的字典
        """
        stage = StageConfig(name="test_stage", enabled=False, timeout=600)
        data = stage.to_dict()
        assert data["name"] == "test_stage"
        assert data["enabled"] is False
        assert data["timeout"] == 600

    def test_stage_config_from_dict(self):
        """测试从字典创建阶段配置

        Given: 包含阶段配置的字典
        When: 调用 StageConfig.from_dict()
        Then: 应返回正确的 StageConfig 实例
        """
        data = {
            "name": "iar_compile",
            "enabled": True,
            "timeout": 1200
        }
        stage = StageConfig.from_dict(data)
        assert stage.name == "iar_compile"
        assert stage.enabled is True
        assert stage.timeout == 1200


class TestWorkflowConfig:
    """测试 WorkflowConfig 数据模型 (Story 2.1 Task 1.2)"""

    def test_workflow_config_defaults(self):
        """测试工作流配置默认值

        Given: 创建空的 WorkflowConfig
        Then: 所有字段应有正确的默认值
        """
        workflow = WorkflowConfig()
        assert workflow.id == ""
        assert workflow.name == ""
        assert workflow.description == ""
        assert workflow.estimated_time == 0
        assert workflow.stages == []

    def test_workflow_config_creation(self):
        """测试工作流配置创建

        Given: 提供工作流配置参数
        When: 创建 WorkflowConfig 实例
        Then: 实例应具有提供的值
        """
        stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),
            StageConfig(name="iar_compile", enabled=True, timeout=1200)
        ]
        workflow = WorkflowConfig(
            id="full_pipeline",
            name="完整流程",
            description="包含所有阶段的完整构建流程",
            estimated_time=15,
            stages=stages
        )
        assert workflow.id == "full_pipeline"
        assert workflow.name == "完整流程"
        assert workflow.description == "包含所有阶段的完整构建流程"
        assert workflow.estimated_time == 15
        assert len(workflow.stages) == 2

    def test_workflow_config_to_dict(self):
        """测试工作流配置转换为字典

        Given: 创建 WorkflowConfig 实例
        When: 调用 to_dict()
        Then: 应返回包含所有字段的字典，包括嵌套的 stages
        """
        stages = [
            StageConfig(name="test_stage", enabled=True, timeout=600)
        ]
        workflow = WorkflowConfig(
            id="test_workflow",
            name="测试工作流",
            description="测试描述",
            estimated_time=5,
            stages=stages
        )
        data = workflow.to_dict()
        assert data["id"] == "test_workflow"
        assert data["name"] == "测试工作流"
        assert data["description"] == "测试描述"
        assert data["estimated_time"] == 5
        assert len(data["stages"]) == 1
        assert data["stages"][0]["name"] == "test_stage"

    def test_workflow_config_from_dict(self):
        """测试从字典创建工作流配置

        Given: 包含工作流配置的字典（包括嵌套的 stages）
        When: 调用 WorkflowConfig.from_dict()
        Then: 应返回正确的 WorkflowConfig 实例，包括嵌套的 StageConfig
        """
        data = {
            "id": "quick_compile",
            "name": "快速编译",
            "description": "跳过 A2L 更新",
            "estimated_time": 10,
            "stages": [
                {
                    "name": "matlab_gen",
                    "enabled": True,
                    "timeout": 1800
                },
                {
                    "name": "iar_compile",
                    "enabled": True,
                    "timeout": 1200
                }
            ]
        }
        workflow = WorkflowConfig.from_dict(data)
        assert workflow.id == "quick_compile"
        assert workflow.name == "快速编译"
        assert len(workflow.stages) == 2
        assert workflow.stages[0].name == "matlab_gen"
        assert workflow.stages[1].name == "iar_compile"

    def test_workflow_config_serialization_roundtrip(self):
        """测试工作流配置序列化和反序列化往返

        Given: 创建 WorkflowConfig 实例
        When: 序列化为字典，再反序列化回对象
        Then: 最终对象应与原始对象相同
        """
        original = WorkflowConfig(
            id="test",
            name="测试",
            description="测试描述",
            estimated_time=8,
            stages=[
                StageConfig(name="stage1", enabled=True, timeout=100),
                StageConfig(name="stage2", enabled=False, timeout=200)
            ]
        )

        # 序列化
        data = original.to_dict()

        # 反序列化
        restored = WorkflowConfig.from_dict(data)

        # 验证
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.estimated_time == original.estimated_time
        assert len(restored.stages) == len(original.stages)
        assert restored.stages[0].name == original.stages[0].name
        assert restored.stages[1].enabled == original.stages[1].enabled
