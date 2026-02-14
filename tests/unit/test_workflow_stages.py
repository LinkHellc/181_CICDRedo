"""Unit tests for workflow stages enabling/disabling (Story 2.14)

This module tests the StageConfig enabled field and related functionality.

Story 2.14 - 任务 1:
- 1.5 添加单元测试验证 StageConfig 的 enabled 字段
- 1.6 添加单元测试验证默认值为 True
- 1.7 添加单元测试验证序列化/反序列化正确性

Story 2.14 - 任务 2:
- 2.5 添加单元测试验证依赖关系映射正确性
- 2.6 添加单元测试验证前置依赖获取
- 2.7 添加单元测试验证后置依赖获取
"""

import unittest
from core.models import StageConfig
from core.workflow import (
    CORE_STAGE_DEPENDENCIES,
    get_stage_dependencies,
    get_dependent_stages,
    adjust_stage_dependencies
)


class TestStageConfigEnabledField(unittest.TestCase):
    """测试 StageConfig 的 enabled 字段 (Story 2.14 - 任务 1.5)"""

    def test_enabled_field_exists(self):
        """测试 enabled 字段存在 (任务 1.5)"""
        stage = StageConfig(name="matlab_gen")
        self.assertTrue(hasattr(stage, "enabled"), "StageConfig 应该有 enabled 字段")

    def test_enabled_field_type(self):
        """测试 enabled 字段类型为 bool (任务 1.5)"""
        stage = StageConfig(name="matlab_gen")
        self.assertIsInstance(stage.enabled, bool, "enabled 字段应该是布尔类型")

    def test_enabled_can_be_set_to_true(self):
        """测试 enabled 可以设置为 True (任务 1.5)"""
        stage = StageConfig(name="matlab_gen", enabled=True)
        self.assertTrue(stage.enabled, "enabled 应该可以设置为 True")

    def test_enabled_can_be_set_to_false(self):
        """测试 enabled 可以设置为 False (任务 1.5)"""
        stage = StageConfig(name="matlab_gen", enabled=False)
        self.assertFalse(stage.enabled, "enabled 应该可以设置为 False")

    def test_enabled_default_value_is_true(self):
        """测试 enabled 默认值为 True (任务 1.6)"""
        stage = StageConfig(name="matlab_gen")
        self.assertTrue(stage.enabled, "enabled 默认值应该是 True")

    def test_enabled_default_when_only_name_provided(self):
        """测试只提供名称时 enabled 默认为 True (任务 1.6)"""
        stage = StageConfig(name="iar_compile")
        self.assertTrue(stage.enabled, "只提供名称时 enabled 默认值为 True")

    def test_to_dict_includes_enabled(self):
        """测试 to_dict() 包含 enabled 字段 (任务 1.7)"""
        stage = StageConfig(name="matlab_gen", enabled=True, timeout=1800)
        stage_dict = stage.to_dict()
        self.assertIn("enabled", stage_dict, "to_dict() 应该包含 enabled 字段")

    def test_to_dict_enabled_value_correct(self):
        """测试 to_dict() 的 enabled 值正确 (任务 1.7)"""
        stage = StageConfig(name="matlab_gen", enabled=True)
        stage_dict = stage.to_dict()
        self.assertTrue(stage_dict["enabled"], "to_dict() 的 enabled 值应该为 True")

        stage = StageConfig(name="matlab_gen", enabled=False)
        stage_dict = stage.to_dict()
        self.assertFalse(stage_dict["enabled"], "to_dict() 的 enabled 值应该为 False")

    def test_from_dict_with_enabled_true(self):
        """测试 from_dict() 读取 enabled=True (任务 1.7)"""
        data = {"name": "matlab_gen", "enabled": True, "timeout": 1800}
        stage = StageConfig.from_dict(data)
        self.assertTrue(stage.enabled, "from_dict() 应该正确读取 enabled=True")

    def test_from_dict_with_enabled_false(self):
        """测试 from_dict() 读取 enabled=False (任务 1.7)"""
        data = {"name": "matlab_gen", "enabled": False, "timeout": 1800}
        stage = StageConfig.from_dict(data)
        self.assertFalse(stage.enabled, "from_dict() 应该正确读取 enabled=False")

    def test_from_dict_missing_enabled_uses_default(self):
        """测试 from_dict() 缺少 enabled 字段时使用默认值 True (任务 1.7)"""
        data = {"name": "matlab_gen", "timeout": 1800}
        stage = StageConfig.from_dict(data)
        self.assertTrue(stage.enabled, "from_dict() 缺少 enabled 时应使用默认值 True")

    def test_serialization_roundtrip(self):
        """测试序列化/反序列化往返保持 enabled 值 (任务 1.7)"""
        original = StageConfig(name="matlab_gen", enabled=True, timeout=1800)
        stage_dict = original.to_dict()
        restored = StageConfig.from_dict(stage_dict)
        self.assertEqual(original.enabled, restored.enabled, "序列化/反序列化应该保持 enabled 值")

        original = StageConfig(name="matlab_gen", enabled=False, timeout=1800)
        stage_dict = original.to_dict()
        restored = StageConfig.from_dict(stage_dict)
        self.assertEqual(original.enabled, restored.enabled, "序列化/反序列化应该保持 enabled 值")

    def test_all_fields_have_defaults(self):
        """测试所有字段都有默认值 (任务 1.3)"""
        stage = StageConfig()
        self.assertIsNotNone(stage.name, "name 应该有默认值")
        self.assertIsNotNone(stage.enabled, "enabled 应该有默认值")
        self.assertIsNotNone(stage.timeout, "timeout 应该有默认值")


class TestStageDependencies(unittest.TestCase):
    """测试阶段依赖关系 (Story 2.14 - 任务 2)"""

    def test_core_stage_dependencies_exists(self):
        """测试 CORE_STAGE_DEPENDENCIES 映射存在 (任务 2.1)"""
        self.assertIsInstance(CORE_STAGE_DEPENDENCIES, dict, "CORE_STAGE_DEPENDENCIES 应该是字典")

    def test_core_stage_dependencies_has_5_stages(self):
        """测试 CORE_STAGE_DEPENDENCIES 包含 5 个核心阶段 (任务 2.2)"""
        self.assertEqual(len(CORE_STAGE_DEPENDENCIES), 5, "应该有 5 个核心阶段")

    def test_matlab_gen_has_no_dependencies(self):
        """测试 matlab_gen 无依赖 (任务 2.2)"""
        self.assertIn("matlab_gen", CORE_STAGE_DEPENDENCIES, "应该有 matlab_gen 阶段")
        self.assertEqual(CORE_STAGE_DEPENDENCIES["matlab_gen"], [], "matlab_gen 应该无依赖")

    def test_file_process_depends_on_matlab_gen(self):
        """测试 file_process 依赖 matlab_gen (任务 2.2)"""
        self.assertIn("file_process", CORE_STAGE_DEPENDENCIES, "应该有 file_process 阶段")
        self.assertEqual(CORE_STAGE_DEPENDENCIES["file_process"], ["matlab_gen"],
                         "file_process 应该依赖 matlab_gen")

    def test_iar_compile_depends_on_file_process(self):
        """测试 iar_compile 依赖 file_process (任务 2.2)"""
        self.assertIn("iar_compile", CORE_STAGE_DEPENDENCIES, "应该有 iar_compile 阶段")
        self.assertEqual(CORE_STAGE_DEPENDENCIES["iar_compile"], ["file_process"],
                         "iar_compile 应该依赖 file_process")

    def test_a2l_process_depends_on_iar_compile(self):
        """测试 a2l_process 依赖 iar_compile (任务 2.2)"""
        self.assertIn("a2l_process", CORE_STAGE_DEPENDENCIES, "应该有 a2l_process 阶段")
        self.assertEqual(CORE_STAGE_DEPENDENCIES["a2l_process"], ["iar_compile"],
                         "a2l_process 应该依赖 iar_compile")

    def test_package_depends_on_a2l_process(self):
        """测试 package 依赖 a2l_process (任务 2.2)"""
        self.assertIn("package", CORE_STAGE_DEPENDENCIES, "应该有 package 阶段")
        self.assertEqual(CORE_STAGE_DEPENDENCIES["package"], ["a2l_process"],
                         "package 应该依赖 a2l_process")


class TestGetStageDependencies(unittest.TestCase):
    """测试 get_stage_dependencies() 函数 (Story 2.14 - 任务 2.3, 2.6)"""

    def test_get_matlab_gen_dependencies(self):
        """测试获取 matlab_gen 的前置依赖 (任务 2.6)"""
        deps = get_stage_dependencies("matlab_gen")
        self.assertEqual(deps, [], "matlab_gen 应该无前置依赖")

    def test_get_file_process_dependencies(self):
        """测试获取 file_process 的前置依赖 (任务 2.6)"""
        deps = get_stage_dependencies("file_process")
        self.assertEqual(deps, ["matlab_gen"], "file_process 的前置依赖应该是 matlab_gen")

    def test_get_iar_compile_dependencies(self):
        """测试获取 iar_compile 的前置依赖 (任务 2.6)"""
        deps = get_stage_dependencies("iar_compile")
        self.assertIn("matlab_gen", deps, "iar_compile 的前置依赖应该包含 matlab_gen")
        self.assertIn("file_process", deps, "iar_compile 的前置依赖应该包含 file_process")

    def test_get_a2l_process_dependencies(self):
        """测试获取 a2l_process 的前置依赖 (任务 2.6)"""
        deps = get_stage_dependencies("a2l_process")
        self.assertIn("matlab_gen", deps, "a2l_process 的前置依赖应该包含 matlab_gen")
        self.assertIn("file_process", deps, "a2l_process 的前置依赖应该包含 file_process")
        self.assertIn("iar_compile", deps, "a2l_process 的前置依赖应该包含 iar_compile")

    def test_get_package_dependencies(self):
        """测试获取 package 的前置依赖 (任务 2.6)"""
        deps = get_stage_dependencies("package")
        self.assertIn("matlab_gen", deps, "package 的前置依赖应该包含 matlab_gen")
        self.assertIn("file_process", deps, "package 的前置依赖应该包含 file_process")
        self.assertIn("iar_compile", deps, "package 的前置依赖应该包含 iar_compile")
        self.assertIn("a2l_process", deps, "package 的前置依赖应该包含 a2l_process")

    def test_get_dependencies_for_unknown_stage(self):
        """测试获取未知阶段的依赖返回空列表"""
        deps = get_stage_dependencies("unknown_stage")
        self.assertEqual(deps, [], "未知阶段的依赖应该返回空列表")

    def test_dependencies_order_is_correct(self):
        """测试依赖关系的顺序正确 (任务 2.6)"""
        deps = get_stage_dependencies("iar_compile")
        # matlab_gen 应该在 file_process 之前
        self.assertLess(deps.index("matlab_gen"), deps.index("file_process"),
                        "matlab_gen 应该在 file_process 之前")

    def test_no_duplicate_dependencies(self):
        """测试依赖列表中没有重复 (任务 2.6)"""
        deps = get_stage_dependencies("package")
        self.assertEqual(len(deps), len(set(deps)), "依赖列表中不应该有重复")


class TestGetDependentStages(unittest.TestCase):
    """测试 get_dependent_stages() 函数 (Story 2.14 - 任务 2.4, 2.7)"""

    def test_get_matlab_gen_dependents(self):
        """测试获取 matlab_gen 的后置依赖 (任务 2.7)"""
        dependents = get_dependent_stages("matlab_gen")
        self.assertIn("file_process", dependents, "matlab_gen 的后置依赖应该包含 file_process")
        self.assertIn("iar_compile", dependents, "matlab_gen 的后置依赖应该包含 iar_compile")
        self.assertIn("a2l_process", dependents, "matlab_gen 的后置依赖应该包含 a2l_process")
        self.assertIn("package", dependents, "matlab_gen 的后置依赖应该包含 package")

    def test_get_file_process_dependents(self):
        """测试获取 file_process 的后置依赖 (任务 2.7)"""
        dependents = get_dependent_stages("file_process")
        self.assertIn("iar_compile", dependents, "file_process 的后置依赖应该包含 iar_compile")
        self.assertIn("a2l_process", dependents, "file_process 的后置依赖应该包含 a2l_process")
        self.assertIn("package", dependents, "file_process 的后置依赖应该包含 package")

    def test_get_iar_compile_dependents(self):
        """测试获取 iar_compile 的后置依赖 (任务 2.7)"""
        dependents = get_dependent_stages("iar_compile")
        self.assertIn("a2l_process", dependents, "iar_compile 的后置依赖应该包含 a2l_process")
        self.assertIn("package", dependents, "iar_compile 的后置依赖应该包含 package")

    def test_get_a2l_process_dependents(self):
        """测试获取 a2l_process 的后置依赖 (任务 2.7)"""
        dependents = get_dependent_stages("a2l_process")
        self.assertIn("package", dependents, "a2l_process 的后置依赖应该包含 package")

    def test_get_package_dependents(self):
        """测试获取 package 的后置依赖 (任务 2.7)"""
        dependents = get_dependent_stages("package")
        self.assertEqual(dependents, [], "package 应该无后置依赖")

    def test_get_dependents_for_unknown_stage(self):
        """测试获取未知阶段的后置依赖返回空列表"""
        dependents = get_dependent_stages("unknown_stage")
        self.assertEqual(dependents, [], "未知阶段的后置依赖应该返回空列表")

    def test_dependents_order_is_correct(self):
        """测试后置依赖的顺序正确 (任务 2.7)"""
        dependents = get_dependent_stages("matlab_gen")
        # file_process 应该在 iar_compile 之前
        self.assertLess(dependents.index("file_process"), dependents.index("iar_compile"),
                        "file_process 应该在 iar_compile 之前")
        # iar_compile 应该在 a2l_process 之前
        self.assertLess(dependents.index("iar_compile"), dependents.index("a2l_process"),
                        "iar_compile 应该在 a2l_process 之前")

    def test_no_duplicate_dependents(self):
        """测试后置依赖列表中没有重复 (任务 2.7)"""
        dependents = get_dependent_stages("matlab_gen")
        self.assertEqual(len(dependents), len(set(dependents)), "后置依赖列表中不应该有重复")

    def test_disable_file_process_should_disable_all(self):
        """测试禁用 file_process 应该禁用所有后续阶段 (Story 2.14 - 需求示例)"""
        dependents = get_dependent_stages("file_process")
        self.assertEqual(len(dependents), 3, "file_process 应该有 3 个后置依赖")
        self.assertIn("iar_compile", dependents, "应该包含 iar_compile")
        self.assertIn("a2l_process", dependents, "应该包含 a2l_process")
        self.assertIn("package", dependents, "应该包含 package")

    def test_enable_package_should_enable_all(self):
        """测试启用 package 应该启用所有前置阶段 (Story 2.14 - 需求示例)"""
        deps = get_stage_dependencies("package")
        self.assertEqual(len(deps), 4, "package 应该有 4 个前置依赖")
        self.assertIn("matlab_gen", deps, "应该包含 matlab_gen")
        self.assertIn("file_process", deps, "应该包含 file_process")
        self.assertIn("iar_compile", deps, "应该包含 iar_compile")
        self.assertIn("a2l_process", deps, "应该包含 a2l_process")


class TestAdjustStageDependencies(unittest.TestCase):
    """测试 adjust_stage_dependencies() 函数 (Story 2.14 - 任务 3)"""

    def setUp(self):
        """创建测试用的阶段配置列表"""
        self.stages = [
            StageConfig(name="matlab_gen", enabled=True, timeout=1800),
            StageConfig(name="file_process", enabled=True, timeout=300),
            StageConfig(name="iar_compile", enabled=True, timeout=1200),
            StageConfig(name="a2l_process", enabled=True, timeout=600),
            StageConfig(name="package", enabled=True, timeout=60)
        ]

    def test_disable_file_process_disables_all_dependents(self):
        """测试禁用 file_process 自动禁用所有后续阶段 (任务 3.5)"""
        adjust_stage_dependencies(self.stages, "file_process", False)

        # file_process 应该被禁用
        file_process = next(s for s in self.stages if s.name == "file_process")
        self.assertFalse(file_process.enabled, "file_process 应该被禁用")

        # iar_compile 应该被禁用
        iar_compile = next(s for s in self.stages if s.name == "iar_compile")
        self.assertFalse(iar_compile.enabled, "iar_compile 应该被禁用")

        # a2l_process 应该被禁用
        a2l_process = next(s for s in self.stages if s.name == "a2l_process")
        self.assertFalse(a2l_process.enabled, "a2l_process 应该被禁用")

        # package 应该被禁用
        package = next(s for s in self.stages if s.name == "package")
        self.assertFalse(package.enabled, "package 应该被禁用")

        # matlab_gen 应该保持启用
        matlab_gen = next(s for s in self.stages if s.name == "matlab_gen")
        self.assertTrue(matlab_gen.enabled, "matlab_gen 应该保持启用")

    def test_disable_iar_compile_disables_dependents(self):
        """测试禁用 iar_compile 自动禁用后续阶段 (任务 3.5)"""
        adjust_stage_dependencies(self.stages, "iar_compile", False)

        # iar_compile 应该被禁用
        iar_compile = next(s for s in self.stages if s.name == "iar_compile")
        self.assertFalse(iar_compile.enabled, "iar_compile 应该被禁用")

        # a2l_process 应该被禁用
        a2l_process = next(s for s in self.stages if s.name == "a2l_process")
        self.assertFalse(a2l_process.enabled, "a2l_process 应该被禁用")

        # package 应该被禁用
        package = next(s for s in self.stages if s.name == "package")
        self.assertFalse(package.enabled, "package 应该被禁用")

        # matlab_gen 和 file_process 应该保持启用
        matlab_gen = next(s for s in self.stages if s.name == "matlab_gen")
        self.assertTrue(matlab_gen.enabled, "matlab_gen 应该保持启用")

        file_process = next(s for s in self.stages if s.name == "file_process")
        self.assertTrue(file_process.enabled, "file_process 应该保持启用")

    def test_enable_package_enables_all_dependencies(self):
        """测试启用 package 自动启用所有前置阶段 (任务 3.6)"""
        # 先禁用所有阶段
        for stage in self.stages:
            stage.enabled = False

        # 启用 package
        adjust_stage_dependencies(self.stages, "package", True)

        # package 应该被启用
        package = next(s for s in self.stages if s.name == "package")
        self.assertTrue(package.enabled, "package 应该被启用")

        # a2l_process 应该被启用
        a2l_process = next(s for s in self.stages if s.name == "a2l_process")
        self.assertTrue(a2l_process.enabled, "a2l_process 应该被启用")

        # iar_compile 应该被启用
        iar_compile = next(s for s in self.stages if s.name == "iar_compile")
        self.assertTrue(iar_compile.enabled, "iar_compile 应该被启用")

        # file_process 应该被启用
        file_process = next(s for s in self.stages if s.name == "file_process")
        self.assertTrue(file_process.enabled, "file_process 应该被启用")

        # matlab_gen 应该被启用
        matlab_gen = next(s for s in self.stages if s.name == "matlab_gen")
        self.assertTrue(matlab_gen.enabled, "matlab_gen 应该被启用")

    def test_enable_iar_compile_enables_dependencies(self):
        """测试启用 iar_compile 自动启用前置阶段 (任务 3.6)"""
        # 先禁用所有阶段
        for stage in self.stages:
            stage.enabled = False

        # 启用 iar_compile
        adjust_stage_dependencies(self.stages, "iar_compile", True)

        # iar_compile 应该被启用
        iar_compile = next(s for s in self.stages if s.name == "iar_compile")
        self.assertTrue(iar_compile.enabled, "iar_compile 应该被启用")

        # file_process 应该被启用
        file_process = next(s for s in self.stages if s.name == "file_process")
        self.assertTrue(file_process.enabled, "file_process 应该被启用")

        # matlab_gen 应该被启用
        matlab_gen = next(s for s in self.stages if s.name == "matlab_gen")
        self.assertTrue(matlab_gen.enabled, "matlab_gen 应该被启用")

        # a2l_process 和 package 应该保持禁用
        a2l_process = next(s for s in self.stages if s.name == "a2l_process")
        self.assertFalse(a2l_process.enabled, "a2l_process 应该保持禁用")

        package = next(s for s in self.stages if s.name == "package")
        self.assertFalse(package.enabled, "package 应该保持禁用")

    def test_enable_matlab_gen_no_dependencies(self):
        """测试启用 matlab_gen 不影响其他阶段 (任务 3.7)"""
        # 先禁用所有阶段
        for stage in self.stages:
            stage.enabled = False

        # 启用 matlab_gen
        adjust_stage_dependencies(self.stages, "matlab_gen", True)

        # matlab_gen 应该被启用
        matlab_gen = next(s for s in self.stages if s.name == "matlab_gen")
        self.assertTrue(matlab_gen.enabled, "matlab_gen 应该被启用")

        # 其他阶段应该保持禁用
        for stage in self.stages:
            if stage.name != "matlab_gen":
                self.assertFalse(stage.enabled, f"{stage.name} 应该保持禁用")

    def test_disable_package_no_dependents(self):
        """测试禁用 package 不影响其他阶段 (任务 3.7)"""
        adjust_stage_dependencies(self.stages, "package", False)

        # package 应该被禁用
        package = next(s for s in self.stages if s.name == "package")
        self.assertFalse(package.enabled, "package 应该被禁用")

        # 其他阶段应该保持启用
        for stage in self.stages:
            if stage.name != "package":
                self.assertTrue(stage.enabled, f"{stage.name} 应该保持启用")

    def test_multiple_dependency_levels(self):
        """测试多重依赖关系处理 (任务 3.7)"""
        # 禁用 file_process
        adjust_stage_dependencies(self.stages, "file_process", False)

        # 验证所有后续阶段都被禁用
        expected_disabled = ["file_process", "iar_compile", "a2l_process", "package"]
        for stage_name in expected_disabled:
            stage = next(s for s in self.stages if s.name == stage_name)
            self.assertFalse(stage.enabled, f"{stage_name} 应该被禁用")

        # 重新启用 package，应该启用所有前置阶段
        adjust_stage_dependencies(self.stages, "package", True)

        # 验证所有阶段都被启用
        for stage in self.stages:
            self.assertTrue(stage.enabled, f"{stage.name} 应该被启用")

    def test_partial_enabling(self):
        """测试部分启用场景 (任务 3.7)"""
        # 初始状态：仅 matlab_gen 和 file_process 启用
        self.stages[0].enabled = True   # matlab_gen
        self.stages[1].enabled = True   # file_process
        self.stages[2].enabled = False  # iar_compile
        self.stages[3].enabled = False  # a2l_process
        self.stages[4].enabled = False  # package

        # 启用 a2l_process
        adjust_stage_dependencies(self.stages, "a2l_process", True)

        # a2l_process 应该被启用
        a2l_process = next(s for s in self.stages if s.name == "a2l_process")
        self.assertTrue(a2l_process.enabled, "a2l_process 应该被启用")

        # 前置依赖应该被启用（iar_compile, file_process, matlab_gen）
        iar_compile = next(s for s in self.stages if s.name == "iar_compile")
        self.assertTrue(iar_compile.enabled, "iar_compile 应该被启用")

        file_process = next(s for s in self.stages if s.name == "file_process")
        self.assertTrue(file_process.enabled, "file_process 应该保持启用")

        matlab_gen = next(s for s in self.stages if s.name == "matlab_gen")
        self.assertTrue(matlab_gen.enabled, "matlab_gen 应该保持启用")

        # package 应该保持禁用
        package = next(s for s in self.stages if s.name == "package")
        self.assertFalse(package.enabled, "package 应该保持禁用")

    def test_handle_empty_stages_list(self):
        """测试处理空阶段列表"""
        stages = []
        # 不应该抛出异常
        adjust_stage_dependencies(stages, "matlab_gen", True)

    def test_handle_unknown_stage(self):
        """测试处理未知阶段"""
        # 不应该抛出异常
        adjust_stage_dependencies(self.stages, "unknown_stage", True)

        # 所有阶段的状态应该保持不变
        for stage in self.stages:
            self.assertTrue(stage.enabled, f"{stage.name} 应该保持启用")


if __name__ == "__main__":
    unittest.main()
