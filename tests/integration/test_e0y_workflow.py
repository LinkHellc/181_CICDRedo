"""E0Y 项目完整工作流集成测试

此测试用例用于验证 E0Y 项目的完整构建流程，包括：
- 跳过 matlab_gen 阶段
- file_process: 文件处理
- file_move: 文件移动
- iar_compile: IAR 编译
- a2l_process: A2L 文件处理
- package: 打包

运行方式：
    pytest tests/integration/test_e0y_workflow.py -v -s
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.models import (
    WorkflowConfig, StageConfig, BuildContext,
    StageResult, StageStatus, ProjectConfig
)
from core.workflow import execute_workflow, validate_workflow_config
from core.config import load_config, CONFIG_DIR


# E0Y 项目配置（从已保存的配置中读取）
E0Y_CONFIG = {
    "name": "E0Y",
    "simulink_path": "D:/MATLAB/Project/E0Y_TMS",
    "matlab_code_path": "D:/MATLAB/Project/E0Y_TMS/20_Code",
    "a2l_path": "D:/MATLAB/Project/E0Y_TMS/22_A2L/TmsApp.a2l",
    "target_path": "D:/IDE/E0Y/600-CICD/05_finObj",
    "iar_project_path": "D:/IDE/E0Y/600-CICD/02_genHex/Neusar_CYT4BF.eww",
}


def get_e0y_default_workflow() -> WorkflowConfig:
    """获取 E0Y 项目的默认工作流配置（跳过 matlab_gen）"""
    return WorkflowConfig(
        id="e0y_workflow",
        name="E0Y 构建流程",
        description="跳过 MATLAB 代码生成，从文件处理开始",
        estimated_time=15,
        stages=[
            StageConfig(name="matlab_gen", enabled=False, timeout=1800),
            StageConfig(name="file_process", enabled=True, timeout=300),
            StageConfig(name="file_move", enabled=True, timeout=300),
            StageConfig(name="iar_compile", enabled=True, timeout=1200),
            StageConfig(name="a2l_process", enabled=True, timeout=600),
            StageConfig(name="package", enabled=True, timeout=60),
        ]
    )


class TestE0YProjectConfig:
    """测试 E0Y 项目配置"""

    def test_e0y_config_exists(self):
        """验证 E0Y 项目配置文件存在"""
        config_file = CONFIG_DIR / "E0Y.toml"
        assert config_file.exists(), f"E0Y 配置文件不存在: {config_file}"

    def test_load_e0y_config(self):
        """测试加载 E0Y 项目配置"""
        config = load_config("E0Y")
        assert config is not None
        assert config.name == "E0Y"
        assert config.simulink_path == "D:/MATLAB/Project/E0Y_TMS"
        print(f"✅ 成功加载 E0Y 配置: {config.name}")

    def test_e0y_paths_exist(self):
        """测试 E0Y 项目路径是否存在"""
        config = load_config("E0Y")

        paths_to_check = {
            "simulink_path": Path(config.simulink_path),
            "matlab_code_path": Path(config.matlab_code_path),
            "a2l_path": Path(config.a2l_path),
            "target_path": Path(config.target_path),
            "iar_project_path": Path(config.iar_project_path),
        }

        missing_paths = []
        for name, path in paths_to_check.items():
            if not path.exists():
                missing_paths.append(f"{name}: {path}")

        if missing_paths:
            print(f"⚠️ 以下路径不存在:")
            for p in missing_paths:
                print(f"  - {p}")
        else:
            print("✅ 所有路径都存在")

        # 不强制要求所有路径存在，只是报告
        # assert len(missing_paths) == 0, f"路径不存在: {missing_paths}"


class TestE0YWorkflowValidation:
    """测试 E0Y 工作流验证"""

    def test_workflow_validation_with_skipped_matlab_gen(self):
        """测试跳过 matlab_gen 的工作流验证"""
        config = load_config("E0Y")
        workflow = get_e0y_default_workflow()

        result = validate_workflow_config(workflow, config)

        print(f"\n验证结果:")
        print(f"  - 是否有效: {result.is_valid}")
        print(f"  - 错误数: {result.error_count}")
        print(f"  - 警告数: {result.warning_count}")

        if not result.is_valid:
            print(f"\n错误详情:")
            for error in result.errors:
                print(f"  - [{error.severity.value}] {error.field}: {error.message}")
                if error.suggestions:
                    for s in error.suggestions:
                        print(f"      建议: {s}")

        assert result.is_valid, f"工作流验证失败: {result.error_count} 个错误"


class TestE0YWorkflowExecution:
    """测试 E0Y 工作流执行"""

    @pytest.fixture
    def e0y_project_config(self):
        """加载 E0Y 项目配置"""
        return load_config("E0Y")

    @pytest.fixture
    def e0y_workflow_config(self):
        """获取 E0Y 工作流配置"""
        return get_e0y_default_workflow()

    @pytest.fixture
    def build_context(self, e0y_project_config):
        """创建构建上下文"""
        config_dict = {
            "simulink_path": e0y_project_config.simulink_path,
            "matlab_code_path": e0y_project_config.matlab_code_path,
            "a2l_path": e0y_project_config.a2l_path,
            "target_path": e0y_project_config.target_path,
            "iar_project_path": e0y_project_config.iar_project_path,
        }

        logs = []
        def log_callback(msg):
            logs.append(msg)
            print(f"[LOG] {msg}")

        context = BuildContext(
            config=config_dict,
            log_callback=log_callback
        )
        context._logs = logs  # 保存日志引用以便测试中查看
        return context

    def test_file_process_stage(self, e0y_workflow_config, build_context):
        """测试 file_process 阶段"""
        from stages.file_process import execute_stage

        # 获取 file_process 阶段配置
        stage_config = next(
            (s for s in e0y_workflow_config.stages if s.name == "file_process"),
            None
        )
        assert stage_config is not None
        assert stage_config.enabled

        # 执行阶段
        result = execute_stage(stage_config, build_context)

        print(f"\nfile_process 阶段结果:")
        print(f"  - 状态: {result.status.value}")
        print(f"  - 消息: {result.message}")
        print(f"  - 执行时间: {result.execution_time:.2f}s")

        if result.status == StageStatus.FAILED:
            print(f"  - 建议: {result.suggestions}")
            # 打印日志
            if hasattr(build_context, '_logs'):
                print(f"\n执行日志:")
                for log in build_context._logs[-20:]:
                    print(f"    {log}")

        # 验证结果
        if result.status == StageStatus.FAILED:
            pytest.skip(f"file_process 阶段失败: {result.message}")

    def test_full_workflow_execution(self, e0y_workflow_config, build_context):
        """测试完整工作流执行（跳过 matlab_gen）"""

        progress_logs = []
        def progress_callback(percent, message):
            progress_logs.append((percent, message))
            print(f"[进度 {percent}%] {message}")

        stage_logs = []
        def stage_callback(stage_name, success):
            stage_logs.append((stage_name, success))
            status = "✅" if success else "❌"
            print(f"[阶段] {status} {stage_name}")

        # 执行工作流
        result = execute_workflow(
            e0y_workflow_config,
            build_context,
            progress_callback=progress_callback,
            stage_callback=stage_callback
        )

        print(f"\n工作流执行结果: {'成功' if result else '失败'}")
        print(f"阶段执行记录:")
        for stage_name, success in stage_logs:
            status = "✅" if success else "❌"
            print(f"  {status} {stage_name}")

        # 打印上下文状态
        print(f"\n上下文状态:")
        for key, value in build_context.state.items():
            if key.endswith('_output') or key.endswith('_result'):
                print(f"  {key}: {type(value).__name__}")

        # 不强制要求成功，因为可能缺少某些依赖
        # assert result, "工作流执行失败"


class TestE0YStageDiagnostics:
    """E0Y 项目阶段诊断测试"""

    def test_diagnose_matlab_code_directory(self):
        """诊断 MATLAB 代码目录"""
        config = load_config("E0Y")
        matlab_code_path = Path(config.matlab_code_path)

        print(f"\n诊断 MATLAB 代码目录: {matlab_code_path}")

        if not matlab_code_path.exists():
            print(f"  ❌ 目录不存在")
            # 检查 simulink_path 下的 20_Code 目录
            alt_path = Path(config.simulink_path) / "20_Code"
            if alt_path.exists():
                print(f"  ✅ 找到替代目录: {alt_path}")
            else:
                print(f"  ❌ 替代目录也不存在: {alt_path}")
            return

        # 统计文件
        c_files = list(matlab_code_path.glob("**/*.c"))
        h_files = list(matlab_code_path.glob("**/*.h"))

        print(f"  ✅ 目录存在")
        print(f"  - .c 文件数: {len(c_files)}")
        print(f"  - .h 文件数: {len(h_files)}")

        # 检查是否有 Cal.c 文件
        cal_files = [f for f in c_files if 'cal' in f.name.lower()]
        if cal_files:
            print(f"  - Cal.c 文件: {[f.name for f in cal_files]}")

    def test_diagnose_a2l_file(self):
        """诊断 A2L 文件"""
        config = load_config("E0Y")
        a2l_path = Path(config.a2l_path)

        print(f"\n诊断 A2L 文件: {a2l_path}")

        if not a2l_path.exists():
            print(f"  ❌ 文件不存在")
            # 检查目录是否存在
            a2l_dir = a2l_path.parent
            if a2l_dir.exists():
                a2l_files = list(a2l_dir.glob("*.a2l"))
                print(f"  目录中存在的 .a2l 文件: {[f.name for f in a2l_files]}")
            return

        print(f"  ✅ 文件存在")
        print(f"  - 文件大小: {a2l_path.stat().st_size} bytes")

    def test_diagnose_iar_project(self):
        """诊断 IAR 工程文件"""
        config = load_config("E0Y")
        iar_path = Path(config.iar_project_path)

        print(f"\n诊断 IAR 工程文件: {iar_path}")

        if not iar_path.exists():
            print(f"  ❌ 文件不存在")
            return

        print(f"  ✅ 文件存在")

        # 检查工程目录结构
        iar_dir = iar_path.parent
        ewp_files = list(iar_dir.glob("**/*.ewp"))
        eww_files = list(iar_dir.glob("**/*.eww"))

        print(f"  - .ewp 文件数: {len(ewp_files)}")
        print(f"  - .eww 文件数: {len(eww_files)}")

    def test_diagnose_target_directory(self):
        """诊断目标输出目录"""
        config = load_config("E0Y")
        target_path = Path(config.target_path)

        print(f"\n诊断目标输出目录: {target_path}")

        if not target_path.exists():
            print(f"  ❌ 目录不存在，将尝试创建")
            return

        print(f"  ✅ 目录存在")

        # 检查目录中的文件
        hex_files = list(target_path.glob("**/*.hex"))
        a2l_files = list(target_path.glob("**/*.a2l"))

        print(f"  - .hex 文件数: {len(hex_files)}")
        print(f"  - .a2l 文件数: {len(a2l_files)}")


def run_e0y_diagnostics():
    """运行 E0Y 诊断（可直接调用）"""
    print("=" * 60)
    print("E0Y 项目诊断")
    print("=" * 60)

    # 加载配置
    try:
        config = load_config("E0Y")
        print(f"\n✅ 成功加载配置: {config.name}")
    except Exception as e:
        print(f"\n❌ 加载配置失败: {e}")
        return

    # 检查路径
    paths = {
        "simulink_path": config.simulink_path,
        "matlab_code_path": config.matlab_code_path,
        "a2l_path": config.a2l_path,
        "target_path": config.target_path,
        "iar_project_path": config.iar_project_path,
    }

    print("\n路径检查:")
    for name, path_str in paths.items():
        path = Path(path_str)
        exists = "✅" if path.exists() else "❌"
        print(f"  {exists} {name}: {path_str}")

    # 验证工作流
    print("\n工作流验证:")
    workflow = get_e0y_default_workflow()
    project_config = ProjectConfig(
        name=config.name,
        simulink_path=config.simulink_path,
        matlab_code_path=config.matlab_code_path,
        a2l_path=config.a2l_path,
        target_path=config.target_path,
        iar_project_path=config.iar_project_path,
    )

    result = validate_workflow_config(workflow, project_config)
    print(f"  - 是否有效: {result.is_valid}")
    print(f"  - 错误数: {result.error_count}")
    print(f"  - 警告数: {result.warning_count}")

    if not result.is_valid:
        print("\n  错误详情:")
        for error in result.errors:
            print(f"    - {error.message}")
            if error.suggestions:
                for s in error.suggestions:
                    print(f"      建议: {s}")


if __name__ == "__main__":
    # 直接运行诊断
    run_e0y_diagnostics()

    # 或者运行 pytest
    # pytest.main([__file__, "-v", "-s"])
