"""Unit tests for workflow configuration validation (Story 2.14)

This module tests the validate_workflow_config() function and related functionality.

Story 2.14 - 任务 4:
- 4.5 添加单元测试验证有效配置
- 4.6 添加单元测试验证无效 enabled 字段
- 4.7 添加单元测试验证依赖关系冲突
"""

import unittest
import tempfile
import json
from pathlib import Path
from core.models import StageConfig
from core.config import validate_workflow_config, load_workflow_config


class TestValidateWorkflowConfig(unittest.TestCase):
    """测试 validate_workflow_config() 函数 (Story 2.14 - 任务 4)"""

    def setUp(self):
        """创建测试用的阶段配置列表"""
        self.valid_stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),
            StageConfig(name="file_process", enabled=True, timeout=300),
            StageConfig(name="iar_compile", enabled=True, timeout=1200),
            StageConfig(name="a2l_process", enabled=True, timeout=600),
            StageConfig(name="package", enabled=True, timeout=60)
        ]

    def test_valid_all_stages_enabled(self):
        """测试所有阶段启用的有效配置 (任务 4.5)"""
        errors = validate_workflow_config(self.valid_stages)
        self.assertEqual(errors, [], "所有阶段启用的配置应该有效")

    def test_valid_all_stages_disabled(self):
        """测试所有阶段禁用的有效配置 (任务 4.5)"""
        stages = [
            StageConfig(name="matlab_gen", enabled=False, timeout=1800),
            StageConfig(name="file_process", enabled=False, timeout=300),
            StageConfig(name="iar_compile", enabled=False, timeout=1200),
            StageConfig(name="a2l_process", enabled=False, timeout=600),
            StageConfig(name="package", enabled=False, timeout=60)
        ]
        errors = validate_workflow_config(stages)
        self.assertEqual(errors, [], "所有阶段禁用的配置应该有效")

    def test_valid_partial_stages_enabled(self):
        """测试部分阶段启用的有效配置 (任务 4.5)"""
        # 仅启用 matlab_gen 和 file_process
        stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),
            StageConfig(name="file_process", enabled=True, timeout=300),
            StageConfig(name="iar_compile", enabled=False, timeout=1200),
            StageConfig(name="a2l_process", enabled=False, timeout=600),
            StageConfig(name="package", enabled=False, timeout=60)
        ]
        errors = validate_workflow_config(stages)
        self.assertEqual(errors, [], "部分阶段启用的配置应该有效")

    def test_valid_only_matlab_gen_enabled(self):
        """测试仅启用 matlab_gen 的有效配置 (任务 4.5)"""
        stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),
            StageConfig(name="file_process", enabled=False, timeout=300),
            StageConfig(name="iar_compile", enabled=False, timeout=1200),
            StageConfig(name="a2l_process", enabled=False, timeout=600),
            StageConfig(name="package", enabled=False, timeout=60)
        ]
        errors = validate_workflow_config(stages)
        self.assertEqual(errors, [], "仅启用 matlab_gen 的配置应该有效")

    def test_invalid_enabled_field_type_string(self):
        """测试 enabled 字段为字符串时无效 (任务 4.6)"""
        stages = [
            StageConfig(name="matlab_gen", enabled="true", timeout=1800),  # 字符串 "true"
            StageConfig(name="file_process", enabled=True, timeout=300),
            StageConfig(name="iar_compile", enabled=True, timeout=1200),
            StageConfig(name="a2l_process", enabled=True, timeout=600),
            StageConfig(name="package", enabled=True, timeout=60)
        ]
        errors = validate_workflow_config(stages)
        self.assertGreater(len(errors), 0, "enabled 为字符串时应该返回错误")
        self.assertTrue(
            any("'matlab_gen' 的 enabled 字段必须是布尔值" in err for err in errors),
            "错误消息应该包含 'matlab_gen' 和 '布尔值'"
        )

    def test_invalid_enabled_field_type_integer(self):
        """测试 enabled 字段为整数时无效 (任务 4.6)"""
        stages = [
            StageConfig(name="matlab_gen", enabled=1, timeout=1800),  # 整数 1
            StageConfig(name="file_process", enabled=True, timeout=300),
            StageConfig(name="iar_compile", enabled=True, timeout=1200),
            StageConfig(name="a2l_process", enabled=True, timeout=600),
            StageConfig(name="package", enabled=True, timeout=60)
        ]
        errors = validate_workflow_config(stages)
        self.assertGreater(len(errors), 0, "enabled 为整数时应该返回错误")

    def test_invalid_enabled_field_missing(self):
        """测试缺少 enabled 字段时无效 (任务 4.6)"""
        # 创建一个没有 enabled 字段的阶段对象
        class InvalidStage:
            def __init__(self):
                self.name = "matlab_gen"
                self.timeout = 1800

        stages = [
            InvalidStage(),
            StageConfig(name="file_process", enabled=True, timeout=300),
            StageConfig(name="iar_compile", enabled=True, timeout=1200),
            StageConfig(name="a2l_process", enabled=True, timeout=600),
            StageConfig(name="package", enabled=True, timeout=60)
        ]
        errors = validate_workflow_config(stages)
        self.assertGreater(len(errors), 0, "缺少 enabled 字段时应该返回错误")
        self.assertTrue(
            any("缺少 enabled 字段" in err for err in errors),
            "错误消息应该包含 '缺少 enabled 字段'"
        )

    def test_invalid_dependency_conflict_iar_compile_without_file_process(self):
        """测试启用 iar_compile 但禁用 file_process 的依赖冲突 (任务 4.7)"""
        stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),
            StageConfig(name="file_process", enabled=False, timeout=300),  # 禁用
            StageConfig(name="iar_compile", enabled=True, timeout=1200),  # 启用
            StageConfig(name="a2l_process", enabled=False, timeout=600),
            StageConfig(name="package", enabled=False, timeout=60)
        ]
        errors = validate_workflow_config(stages)
        self.assertGreater(len(errors), 0, "应该检测到依赖冲突")
        self.assertTrue(
            any("iar_compile" in err and "file_process" in err for err in errors),
            "错误消息应该提到 iar_compile 和 file_process"
        )

    def test_invalid_dependency_conflict_package_without_a2l_process(self):
        """测试启用 package 但禁用 a2l_process 的依赖冲突 (任务 4.7)"""
        stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),
            StageConfig(name="file_process", enabled=True, timeout=300),
            StageConfig(name="iar_compile", enabled=True, timeout=1200),
            StageConfig(name="a2l_process", enabled=False, timeout=600),  # 禁用
            StageConfig(name="package", enabled=True, timeout=60)  # 启用
        ]
        errors = validate_workflow_config(stages)
        self.assertGreater(len(errors), 0, "应该检测到依赖冲突")
        self.assertTrue(
            any("package" in err and "a2l_process" in err for err in errors),
            "错误消息应该提到 package 和 a2l_process"
        )

    def test_invalid_dependency_conflict_package_without_all_deps(self):
        """测试启用 package 但禁用所有依赖的依赖冲突 (任务 4.7)"""
        stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),
            StageConfig(name="file_process", enabled=False, timeout=300),  # 禁用
            StageConfig(name="iar_compile", enabled=False, timeout=1200),  # 禁用
            StageConfig(name="a2l_process", enabled=False, timeout=600),  # 禁用
            StageConfig(name="package", enabled=True, timeout=60)  # 启用
        ]
        errors = validate_workflow_config(stages)
        self.assertGreater(len(errors), 0, "应该检测到多个依赖冲突")

    def test_invalid_multiple_dependency_conflicts(self):
        """测试多个依赖冲突 (任务 4.7)"""
        stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),
            StageConfig(name="file_process", enabled=False, timeout=300),  # 禁用
            StageConfig(name="iar_compile", enabled=True, timeout=1200),  # 启用 - 冲突 1
            StageConfig(name="a2l_process", enabled=True, timeout=600),  # 启用 - 冲突 2
            StageConfig(name="package", enabled=True, timeout=60)  # 启用 - 冲突 3
        ]
        errors = validate_workflow_config(stages)
        self.assertGreater(len(errors), 1, "应该检测到多个依赖冲突")

    def test_valid_empty_stages_list(self):
        """测试空阶段列表应该有效"""
        stages = []
        errors = validate_workflow_config(stages)
        self.assertEqual(errors, [], "空阶段列表应该有效")

    def test_handle_stage_missing_name(self):
        """测试处理缺少 name 字段的阶段"""
        class InvalidStage:
            def __init__(self):
                self.enabled = True
                self.timeout = 1800

        stages = [InvalidStage()]
        errors = validate_workflow_config(stages)
        self.assertGreater(len(errors), 0, "缺少 name 字段时应该返回错误")

    def test_valid_cascading_disabled_stages(self):
        """测试级联禁用的阶段配置应该有效 (任务 4.5)"""
        # 级联禁用：matlab_gen 启用，其他都禁用
        stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),
            StageConfig(name="file_process", enabled=False, timeout=300),
            StageConfig(name="iar_compile", enabled=False, timeout=1200),
            StageConfig(name="a2l_process", enabled=False, timeout=600),
            StageConfig(name="package", enabled=False, timeout=60)
        ]
        errors = validate_workflow_config(stages)
        self.assertEqual(errors, [], "级联禁用的配置应该有效")

    def test_valid_middle_stages_enabled(self):
        """测试启用中间阶段的配置应该有效 (任务 4.5)"""
        # 启用从 matlab_gen 到 a2l_process 的中间阶段
        # 注意：如果要启用 file_process，matlab_gen 也必须启用
        stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),  # 必须启用
            StageConfig(name="file_process", enabled=True, timeout=300),
            StageConfig(name="iar_compile", enabled=True, timeout=1200),
            StageConfig(name="a2l_process", enabled=True, timeout=600),
            StageConfig(name="package", enabled=False, timeout=60)  # 禁用 package
        ]
        errors = validate_workflow_config(stages)
        self.assertEqual(errors, [], "启用中间阶段的配置应该有效")


class TestLoadWorkflowConfig(unittest.TestCase):
    """测试 load_workflow_config() 函数 (Story 2.14 - 任务 5)"""

    def setUp(self):
        """创建临时文件用于测试"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """清理临时文件"""
        self.temp_dir.cleanup()

    def test_load_complete_workflow_with_enabled_true(self):
        """测试加载包含所有阶段启用的工作流配置 (任务 5.7)"""
        config_data = {
            "workflow_name": "完整流程",
            "stages": [
                {"name": "matlab_gen", "enabled": True, "timeout": 1800},
                {"name": "file_process", "enabled": True, "timeout": 300},
                {"name": "iar_compile", "enabled": True, "timeout": 1200},
                {"name": "a2l_process", "enabled": True, "timeout": 600},
                {"name": "package", "enabled": True, "timeout": 60}
            ]
        }
        config_file = self.temp_path / "workflow.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        stages, errors = load_workflow_config(config_file)
        self.assertEqual(len(stages), 5, "应该加载 5 个阶段")
        self.assertEqual(errors, [], "不应该有错误")
        for stage in stages:
            self.assertTrue(stage.enabled, f"阶段 {stage.name} 应该被启用")

    def test_load_workflow_with_enabled_false(self):
        """测试加载包含禁用阶段的工作流配置 (任务 5.7)"""
        config_data = {
            "workflow_name": "快速编译",
            "stages": [
                {"name": "matlab_gen", "enabled": True, "timeout": 1800},
                {"name": "file_process", "enabled": True, "timeout": 300},
                {"name": "iar_compile", "enabled": True, "timeout": 1200},
                {"name": "a2l_process", "enabled": False, "timeout": 600},  # 禁用
                {"name": "package", "enabled": False, "timeout": 60}  # 也禁用 package（避免依赖冲突）
            ]
        }
        config_file = self.temp_path / "workflow.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        stages, errors = load_workflow_config(config_file)
        self.assertEqual(len(stages), 5, "应该加载 5 个阶段")
        self.assertEqual(errors, [], "不应该有错误")

        a2l_process = next(s for s in stages if s.name == "a2l_process")
        self.assertFalse(a2l_process.enabled, "a2l_process 应该被禁用")

        package = next(s for s in stages if s.name == "package")
        self.assertFalse(package.enabled, "package 应该被禁用")

        # 其他阶段应该启用
        for stage in stages:
            if stage.name not in ["a2l_process", "package"]:
                self.assertTrue(stage.enabled, f"阶段 {stage.name} 应该被启用")

    def test_load_workflow_missing_enabled_uses_default(self):
        """测试加载缺少 enabled 字段的配置，使用默认值 True (任务 5.8)"""
        config_data = {
            "workflow_name": "默认启用",
            "stages": [
                {"name": "matlab_gen", "timeout": 1800},  # 缺少 enabled
                {"name": "file_process", "timeout": 300},
                {"name": "iar_compile", "timeout": 1200},
                {"name": "a2l_process", "timeout": 600},
                {"name": "package", "timeout": 60}
            ]
        }
        config_file = self.temp_path / "workflow.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        stages, errors = load_workflow_config(config_file)
        self.assertEqual(len(stages), 5, "应该加载 5 个阶段")
        # 应该有警告但没有错误
        self.assertTrue(all(stage.enabled for stage in stages), "所有阶段应该默认启用")

    def test_load_workflow_invalid_enabled_field(self):
        """测试加载 enabled 字段类型无效的配置 (任务 5.9)"""
        config_data = {
            "workflow_name": "无效配置",
            "stages": [
                {"name": "matlab_gen", "enabled": "true", "timeout": 1800},  # 字符串
                {"name": "file_process", "enabled": True, "timeout": 300},
                {"name": "iar_compile", "enabled": True, "timeout": 1200},
                {"name": "a2l_process", "enabled": True, "timeout": 600},
                {"name": "package", "enabled": True, "timeout": 60}
            ]
        }
        config_file = self.temp_path / "workflow.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        stages, errors = load_workflow_config(config_file)
        # 应该返回错误，但仍加载阶段（使用默认值）
        self.assertGreater(len(errors), 0, "应该返回错误")
        self.assertTrue(any("enabled 字段必须是布尔值" in err for err in errors),
                       "错误消息应该提到 enabled 字段类型")

    def test_load_workflow_file_not_exists(self):
        """测试加载不存在的文件 (任务 5.9)"""
        config_file = self.temp_path / "not_exists.json"
        stages, errors = load_workflow_config(config_file)
        self.assertEqual(stages, [], "阶段列表应该为空")
        self.assertGreater(len(errors), 0, "应该返回错误")
        self.assertTrue(any("文件不存在" in err for err in errors),
                       "错误消息应该提到文件不存在")

    def test_load_workflow_invalid_json(self):
        """测试加载无效的 JSON 文件 (任务 5.9)"""
        config_file = self.temp_path / "invalid.json"
        with open(config_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        stages, errors = load_workflow_config(config_file)
        self.assertEqual(stages, [], "阶段列表应该为空")
        self.assertGreater(len(errors), 0, "应该返回错误")
        self.assertTrue(any("JSON 格式错误" in err for err in errors),
                       "错误消息应该提到 JSON 格式错误")

    def test_load_workflow_missing_stages_field(self):
        """测试加载缺少 stages 字段的配置 (任务 5.9)"""
        config_data = {"workflow_name": "缺少stages"}
        config_file = self.temp_path / "workflow.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        stages, errors = load_workflow_config(config_file)
        self.assertEqual(stages, [], "阶段列表应该为空")
        self.assertGreater(len(errors), 0, "应该返回错误")
        self.assertTrue(any("缺少 'stages' 字段" in err for err in errors),
                       "错误消息应该提到缺少 stages 字段")

    def test_load_workflow_validates_dependencies(self):
        """测试加载时验证依赖关系 (任务 5.6)"""
        config_data = {
            "workflow_name": "依赖冲突",
            "stages": [
                {"name": "matlab_gen", "enabled": True, "timeout": 1800},
                {"name": "file_process", "enabled": False, "timeout": 300},  # 禁用
                {"name": "iar_compile", "enabled": True, "timeout": 1200},  # 启用 - 冲突
                {"name": "a2l_process", "enabled": False, "timeout": 600},
                {"name": "package", "enabled": False, "timeout": 60}
            ]
        }
        config_file = self.temp_path / "workflow.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        stages, errors = load_workflow_config(config_file)
        self.assertGreater(len(errors), 0, "应该检测到依赖冲突")


if __name__ == "__main__":
    unittest.main()
