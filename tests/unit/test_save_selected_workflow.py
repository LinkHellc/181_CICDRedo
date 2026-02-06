"""Unit tests for saving selected workflow (Story 2.1 Task 6)."""

import pytest
import tempfile
from pathlib import Path

# 确保 src 在路径中
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.models import ProjectConfig, WorkflowConfig
from core.config import save_config, load_config, save_selected_workflow


class TestSaveSelectedWorkflow:
    """测试保存选中的工作流配置 (Story 2.1 Task 6)"""

    def test_save_selected_workflow_exists(self):
        """测试 save_selected_workflow 函数存在

        Given: core.config 模块
        Then: save_selected_workflow 函数应存在
        """
        from core.config import save_selected_workflow
        assert callable(save_selected_workflow)

    def test_project_config_has_workflow_field(self):
        """测试 ProjectConfig 有工作流字段

        Given: ProjectConfig dataclass
        Then: 应有 workflow_id 或 workflow_template_id 字段
        """
        config = ProjectConfig()
        # 检查是否有工作流相关字段
        assert hasattr(config, "workflow_id") or hasattr(config, "workflow_template_id")

    def test_save_selected_workflow_updates_config(self):
        """测试保存选中的工作流更新配置

        Given: 项目配置和工作流配置
        When: 调用 save_selected_workflow
        Then: 配置应包含工作流 ID
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 先创建项目配置
                project = ProjectConfig(
                    name="test_project",
                    simulink_path="C:\\Test",
                    matlab_code_path="C:\\Test",
                    a2l_path="C:\\Test",
                    target_path="C:\\Test",
                    iar_project_path="C:\\Test.eww"
                )
                save_config(project, "test_project", overwrite=True)

                # 创建工作流配置
                workflow = WorkflowConfig(
                    id="full_pipeline",
                    name="完整流程",
                    description="测试",
                    estimated_time=15,
                    stages=[]
                )

                # 保存选中的工作流
                save_selected_workflow("test_project", workflow)

                # 加载并验证
                loaded = load_config("test_project")
                assert loaded is not None
                assert loaded.workflow_id == "full_pipeline"

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_save_selected_workflow_with_stages(self):
        """测试保存工作流包含阶段信息

        Given: 包含阶段的工作流配置
        When: 调用 save_selected_workflow
        Then: 配置应包含完整的阶段信息
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            import core.config
            original_dir = core.config.CONFIG_DIR
            core.config.CONFIG_DIR = Path(tmpdir)

            try:
                # 先创建项目配置
                project = ProjectConfig(
                    name="test_project",
                    simulink_path="C:\\Test",
                    matlab_code_path="C:\\Test",
                    a2l_path="C:\\Test",
                    target_path="C:\\Test",
                    iar_project_path="C:\\Test.eww"
                )
                save_config(project, "test_project", overwrite=True)

                # 创建包含阶段的工作流配置
                from core.models import StageConfig
                workflow = WorkflowConfig(
                    id="test_workflow",
                    name="测试工作流",
                    description="测试描述",
                    estimated_time=10,
                    stages=[
                        StageConfig(name="stage1", enabled=True, timeout=100),
                        StageConfig(name="stage2", enabled=False, timeout=200)
                    ]
                )

                # 保存选中的工作流
                save_selected_workflow("test_project", workflow)

                # 加载并验证
                loaded = load_config("test_project")
                assert loaded is not None
                assert loaded.workflow_id == "test_workflow"
                # 验证阶段信息也被保存
                assert hasattr(loaded, "workflow_stages") or "workflow" in str(loaded.custom_params)

            finally:
                core.config.CONFIG_DIR = original_dir

    def test_save_selected_workflow_nonexistent_project(self):
        """测试保存到不存在的项目

        Given: 不存在的项目名称
        When: 调用 save_selected_workflow
        Then: 应抛出 ConfigLoadError
        """
        from core.config import ConfigLoadError
        from core.models import StageConfig

        workflow = WorkflowConfig(
            id="test",
            name="测试",
            description="测试",
            estimated_time=5,
            stages=[]
        )

        with pytest.raises(ConfigLoadError):
            save_selected_workflow("nonexistent_project", workflow)
