"""Unit tests for default workflow configuration file (Story 2.1 Task 2)."""

import pytest
import json
from pathlib import Path

# 确保 src 在路径中
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.models import WorkflowConfig


class TestDefaultWorkflowConfigFile:
    """测试默认工作流配置文件 (Story 2.1 Task 2)"""

    def test_config_file_exists(self):
        """测试配置文件存在

        Given: configs 目录
        Then: default_workflow.json 文件应存在
        """
        config_path = Path(__file__).parent.parent.parent / "configs" / "default_workflow.json"
        assert config_path.exists(), f"配置文件不存在: {config_path}"

    def test_config_file_valid_json(self):
        """测试配置文件是有效的 JSON

        Given: default_workflow.json 文件
        When: 读取文件内容
        Then: 应能成功解析为 JSON
        """
        config_path = Path(__file__).parent.parent.parent / "configs" / "default_workflow.json"
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "templates" in data

    def test_config_has_four_templates(self):
        """测试配置包含 4 个预定义模板

        Given: default_workflow.json 文件
        When: 解析 templates 列表
        Then: 应包含 4 个模板
        """
        config_path = Path(__file__).parent.parent.parent / "configs" / "default_workflow.json"
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["templates"]) == 4

    def test_template_structure(self):
        """测试每个模板的结构

        Given: default_workflow.json 中的每个模板
        Then: 每个模板应包含必需字段：id, name, description, estimated_time, stages
        """
        config_path = Path(__file__).parent.parent.parent / "configs" / "default_workflow.json"
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_fields = ["id", "name", "description", "estimated_time", "stages"]
        for template in data["templates"]:
            for field in required_fields:
                assert field in template, f"模板 {template.get('id', '未知')} 缺少字段: {field}"

    def test_full_pipeline_template_exists(self):
        """测试完整流程模板存在

        Given: default_workflow.json
        Then: 应包含 id 为 "full_pipeline" 的模板
        """
        config_path = Path(__file__).parent.parent.parent / "configs" / "default_workflow.json"
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        template_ids = [t["id"] for t in data["templates"]]
        assert "full_pipeline" in template_ids

    def test_template_stages_structure(self):
        """测试模板的 stages 结构

        Given: default_workflow.json 中的每个模板
        Then: 每个 stage 应包含必需字段：name, enabled, timeout
        """
        config_path = Path(__file__).parent.parent.parent / "configs" / "default_workflow.json"
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for template in data["templates"]:
            for stage in template["stages"]:
                required_fields = ["name", "enabled", "timeout"]
                for field in required_fields:
                    assert field in stage, f"Stage 缺少字段: {field}"

    def test_all_templates_have_five_stages(self):
        """测试所有模板都有 5 个阶段

        Given: default_workflow.json 中的每个模板
        Then: 每个 templates 的 stages 列表长度应为 5
        """
        config_path = Path(__file__).parent.parent.parent / "configs" / "default_workflow.json"
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for template in data["templates"]:
            assert len(template["stages"]) == 5, f"模板 {template['id']} 应有 5 个阶段"

    def test_workflow_config_from_file(self):
        """测试从文件创建 WorkflowConfig 对象

        Given: default_workflow.json
        When: 使用 WorkflowConfig.from_dict() 解析模板
        Then: 应成功创建 WorkflowConfig 对象
        """
        config_path = Path(__file__).parent.parent.parent / "configs" / "default_workflow.json"
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 测试第一个模板
        template_data = data["templates"][0]
        workflow = WorkflowConfig.from_dict(template_data)

        assert workflow.id == template_data["id"]
        assert workflow.name == template_data["name"]
        assert len(workflow.stages) == 5
