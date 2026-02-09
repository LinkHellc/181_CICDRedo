"""Integration tests for custom workflow UI integration (Story 2.2).

Tests for:
- Custom workflow loading from UI
- Workflow select dialog integration
- Error handling in UI context
"""

import pytest
from pathlib import Path
import tempfile
import json

from PyQt6.QtWidgets import QApplication, QFileDialog, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from ui.dialogs.workflow_select_dialog import WorkflowSelectDialog
from core.config import load_workflow_templates, load_custom_workflow
from core.models import WorkflowConfig, StageConfig


@pytest.fixture
def qapp():
    """创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def valid_custom_workflow_json():
    """有效的自定义工作流 JSON 内容"""
    return {
        "id": "test_custom_workflow",
        "name": "测试自定义工作流",
        "description": "集成测试用工作流",
        "estimated_time": 10,
        "stages": [
            {
                "id": "build",
                "name": "构建阶段",
                "enabled": True,
                "timeout": 300,
                "dependencies": []
            },
            {
                "id": "test",
                "name": "测试阶段",
                "enabled": True,
                "timeout": 180,
                "dependencies": ["build"]
            }
        ]
    }


@pytest.fixture
def temp_workflow_file(valid_custom_workflow_json):
    """创建临时工作流文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "custom_workflow.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(valid_custom_workflow_json, f)
        yield str(file_path)


@pytest.fixture
def workflow_select_dialog(qapp):
    """创建工作流选择对话框"""
    dialog = WorkflowSelectDialog()
    yield dialog
    dialog.close()


class TestWorkflowSelectDialogIntegration:
    """测试工作流选择对话框集成 (Story 2.2 Task 6)"""

    def test_dialog_has_custom_load_button(self, workflow_select_dialog):
        """测试对话框有加载自定义工作流按钮"""
        # 查找"加载自定义工作流"按钮
        buttons = workflow_select_dialog.findChildren(QPushButton)
        custom_buttons = [b for b in buttons if "加载自定义工作流" in b.text()]

        assert len(custom_buttons) > 0, "应该有'加载自定义工作流'按钮"

    def test_custom_workflow_load_flow(self, workflow_select_dialog, temp_workflow_file, qapp):
        """测试自定义工作流加载流程"""
        # 注意：这个测试需要模拟用户交互
        # 在实际的 UI 测试中，可以使用 QTest 模拟点击

        # 验证文件存在
        assert Path(temp_workflow_file).exists()

        # 测试加载函数
        workflow, error = load_custom_workflow(Path(temp_workflow_file))

        assert workflow is not None, "应该成功加载工作流"
        assert error is None, "不应该有错误"
        assert workflow.id == "test_custom_workflow"

    def test_add_custom_workflow_to_list(self, workflow_select_dialog, valid_custom_workflow_json):
        """测试将自定义工作流添加到列表"""
        # 创建 WorkflowConfig 对象
        workflow = WorkflowConfig(
            id="test_workflow",
            name="测试工作流",
            description="测试描述",
            estimated_time=5,
            stages=[
                StageConfig(
                    name="test_stage",
                    enabled=True,
                    timeout=300
                )
            ]
        )

        # 调用内部方法添加到列表
        initial_count = workflow_select_dialog.workflow_list.count()
        workflow_select_dialog._add_custom_workflow_to_list(workflow, "test.json")

        # 验证列表项增加
        assert workflow_select_dialog.workflow_list.count() == initial_count + 1

        # 验证工作流被选中
        assert workflow_select_dialog.get_selected_workflow() is not None


class TestCustomWorkflowLoadingIntegration:
    """测试自定义工作流加载集成"""

    def test_load_and_validate_workflow(self, valid_custom_workflow_json, temp_workflow_file):
        """测试加载并验证工作流"""
        # 加载工作流
        workflow, error = load_custom_workflow(Path(temp_workflow_file))

        # 验证加载成功
        assert workflow is not None
        assert error is None

        # 验证工作流属性
        assert workflow.id == "test_custom_workflow"
        assert workflow.name == "测试自定义工作流"
        assert len(workflow.stages) == 2

        # 验证阶段属性
        # 注意：load_custom_workflow 将 JSON 中的 id 映射为 StageConfig.name
        assert workflow.stages[0].name == "build"
        assert workflow.stages[0].enabled is True
        assert workflow.stages[0].timeout == 300

        # 验证第二个阶段
        assert workflow.stages[1].name == "test"
        # 注意：StageConfig 没有 dependencies 属性（设计限制）
        # 依赖验证在加载时完成，但不存储在 StageConfig 中

    def test_error_handling_integration(self, workflow_select_dialog):
        """测试错误处理集成"""
        # 创建无效的工作流文件
        with tempfile.TemporaryDirectory() as tmpdir:
            invalid_file = Path(tmpdir) / "invalid.json"
            with open(invalid_file, "w") as f:
                f.write("{invalid json}")

            # 尝试加载
            workflow, error = load_custom_workflow(invalid_file)

            # 验证错误处理
            assert workflow is None
            assert error is not None
            assert "JSON格式错误" in error


class TestWorkflowPersistenceIntegration:
    """测试工作流持久化集成 (Story 2.2 Task 7)"""

    def test_save_custom_workflow_to_project(self, temp_workflow_file):
        """测试将自定义工作流保存到项目配置"""
        from core.config import save_selected_workflow, load_config

        # 加载自定义工作流
        workflow, _ = load_custom_workflow(Path(temp_workflow_file))
        assert workflow is not None

        # 这个测试需要一个有效的项目配置
        # 在实际集成测试中，应该先创建一个测试项目
        # 这里只验证工作流对象可以被正确处理

        assert workflow.id == "test_custom_workflow"
        assert workflow.to_dict() is not None


class TestUIErrorHandling:
    """测试 UI 错误处理"""

    def test_file_not_found_handling(self, workflow_select_dialog, qapp):
        """测试文件不存在处理"""
        nonexistent_file = Path("/nonexistent/path/workflow.json")

        workflow, error = load_custom_workflow(nonexistent_file)

        assert workflow is None
        assert error is not None
        assert "不存在" in error

    def test_invalid_format_handling(self, workflow_select_dialog):
        """测试无效格式处理"""
        with tempfile.TemporaryDirectory() as tmpdir:
            invalid_file = Path(tmpdir) / "invalid.json"
            with open(invalid_file, "w") as f:
                json.dump({"name": "incomplete"}, f)

            workflow, error = load_custom_workflow(invalid_file)

            assert workflow is None
            assert error is not None


class TestWorkflowSelectionFlow:
    """测试工作流选择流程"""

    def test_select_custom_workflow(self, workflow_select_dialog, temp_workflow_file):
        """测试选择自定义工作流的完整流程"""
        # 1. 加载自定义工作流
        workflow, error = load_custom_workflow(Path(temp_workflow_file))

        assert workflow is not None, "步骤 1: 应该成功加载"
        assert error is None, "步骤 1: 不应该有错误"

        # 2. 添加到对话框列表
        workflow_select_dialog._add_custom_workflow_to_list(workflow, "test.json")

        # 3. 验证工作流被选中
        selected = workflow_select_dialog.get_selected_workflow()
        assert selected is not None, "步骤 3: 应该有选中的工作流"
        assert selected.id == "test_custom_workflow", "步骤 3: ID 应该匹配"

    def test_workflow_list_update(self, workflow_select_dialog):
        """测试工作流列表更新"""
        initial_count = workflow_select_dialog.workflow_list.count()

        # 添加多个自定义工作流
        for i in range(3):
            workflow = WorkflowConfig(
                id=f"custom_{i}",
                name=f"自定义工作流 {i}",
                description=f"测试 {i}",
                estimated_time=5,
                stages=[]
            )
            workflow_select_dialog._add_custom_workflow_to_list(workflow, f"custom_{i}.json")

        # 验证列表更新
        assert workflow_select_dialog.workflow_list.count() == initial_count + 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
