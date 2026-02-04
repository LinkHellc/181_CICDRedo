"""Unit tests for configuration module."""

import pytest
import tempfile
from pathlib import Path

# 确保 src 在路径中
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.models import ProjectConfig
from core.config import save_config, load_config, list_configs, delete_config


def test_project_config_defaults():
    """测试配置模型默认值"""
    config = ProjectConfig()
    assert config.name == ""
    assert config.simulink_path == ""
    assert config.matlab_code_path == ""
    assert config.a2l_path == ""
    assert config.target_path == ""
    assert config.iar_project_path == ""


def test_project_config_creation():
    """测试配置对象创建"""
    config = ProjectConfig(
        name="test_project",
        simulink_path="C:\\Projects\\Test",
        matlab_code_path="C:\\MATLAB\\code",
        a2l_path="C:\\A2L",
        target_path="C:\\Target",
        iar_project_path="C:\\IAR\\project.eww",
    )
    assert config.name == "test_project"
    assert config.simulink_path == "C:\\Projects\\Test"


def test_project_config_to_dict():
    """测试配置转换为字典"""
    config = ProjectConfig(
        name="test", simulink_path="C:\\Test", matlab_code_path="C:\\MATLAB"
    )
    data = config.to_dict()
    assert data["name"] == "test"
    assert data["simulink_path"] == "C:\\Test"


def test_project_config_from_dict():
    """测试从字典创建配置"""
    data = {
        "name": "test",
        "simulink_path": "C:\\Test",
        "matlab_code_path": "C:\\MATLAB",
    }
    config = ProjectConfig.from_dict(data)
    assert config.name == "test"
    assert config.simulink_path == "C:\\Test"


def test_validate_required_fields_empty():
    """测试空字段验证"""
    config = ProjectConfig()
    errors = config.validate_required_fields()
    assert len(errors) == 5  # 5个必填字段


def test_validate_required_fields_valid():
    """测试有效字段验证"""
    config = ProjectConfig(
        simulink_path="C:\\Test",
        matlab_code_path="C:\\MATLAB",
        a2l_path="C:\\A2L",
        target_path="C:\\Target",
        iar_project_path="C:\\IAR",
    )
    errors = config.validate_required_fields()
    assert len(errors) == 0


def test_save_and_load_config():
    """测试配置保存和加载"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 修改 CONFIG_DIR 指向临时目录
        import core.config

        original_dir = core.config.CONFIG_DIR
        core.config.CONFIG_DIR = Path(tmpdir)

        try:
            # 创建测试配置
            config = ProjectConfig(
                name="test_project",
                simulink_path="C:\\Projects\\Test",
                matlab_code_path="C:\\MATLAB\\code",
                a2l_path="C:\\A2L",
                target_path="C:\\Target",
                iar_project_path="C:\\IAR\\project.eww",
            )

            # 保存
            assert save_config(config, "test_project") is True

            # 验证文件存在
            config_file = Path(tmpdir) / "test_project.toml"
            assert config_file.exists()

            # 加载
            loaded = load_config("test_project")
            assert loaded is not None
            assert loaded.name == "test_project"
            assert loaded.simulink_path == "C:\\Projects\\Test"
            assert loaded.matlab_code_path == "C:\\MATLAB\\code"

        finally:
            core.config.CONFIG_DIR = original_dir


def test_load_nonexistent_config():
    """测试加载不存在的配置"""
    with tempfile.TemporaryDirectory() as tmpdir:
        import core.config

        original_dir = core.config.CONFIG_DIR
        core.config.CONFIG_DIR = Path(tmpdir)

        try:
            result = load_config("nonexistent")
            assert result is None

        finally:
            core.config.CONFIG_DIR = original_dir


def test_list_configs():
    """测试列出配置"""
    with tempfile.TemporaryDirectory() as tmpdir:
        import core.config

        original_dir = core.config.CONFIG_DIR
        core.config.CONFIG_DIR = Path(tmpdir)

        try:
            # 创建几个配置文件
            config1 = ProjectConfig(name="project1", simulink_path="C:\\P1")
            config2 = ProjectConfig(name="project2", simulink_path="C:\\P2")

            save_config(config1, "project1")
            save_config(config2, "project2")

            # 列出配置
            configs = list_configs()
            assert "project1" in configs
            assert "project2" in configs

        finally:
            core.config.CONFIG_DIR = original_dir


def test_delete_config():
    """测试删除配置"""
    with tempfile.TemporaryDirectory() as tmpdir:
        import core.config

        original_dir = core.config.CONFIG_DIR
        core.config.CONFIG_DIR = Path(tmpdir)

        try:
            # 创建配置
            config = ProjectConfig(name="to_delete", simulink_path="C:\\Test")
            save_config(config, "to_delete")

            # 验证存在
            config_file = Path(tmpdir) / "to_delete.toml"
            assert config_file.exists()

            # 删除
            assert delete_config("to_delete") is True
            assert not config_file.exists()

            # 删除不存在的配置
            assert delete_config("nonexistent") is False

        finally:
            core.config.CONFIG_DIR = original_dir
