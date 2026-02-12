"""Unit tests for file operations utility module.

Story 2.6 - 任务 1: 创建文件处理工具模块
- 测试文件提取函数（各种文件组合）
- 测试排除文件逻辑（Rte_TmsApp.h）
- 测试文件排序（可预测的处理顺序）
"""

import pytest
from pathlib import Path
import tempfile

from utils.file_ops import extract_source_files


class TestExtractSourceFiles:
    """测试源文件提取函数"""

    def test_extract_c_and_h_files(self):
        """测试提取 .c 和 .h 文件 (Story 2.6 - 任务 1.2-1.4)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            # 创建测试文件
            (base_dir / "main.c").touch()
            (base_dir / "utils.c").touch()
            (base_dir / "main.h").touch()
            (base_dir / "utils.h").touch()
            (base_dir / "readme.txt").touch()  # 应被忽略

            result = extract_source_files(base_dir, [".c", ".h"])

            # 验证返回 4 个文件
            assert len(result) == 4
            # 验证文件类型
            assert all(f.suffix in [".c", ".h"] for f in result)
            # 验证文件名
            file_names = {f.name for f in result}
            assert file_names == {"main.c", "utils.c", "main.h", "utils.h"}

    def test_extract_recursive(self):
        """测试递归搜索文件 (Story 2.6 - 任务 1.3)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            # 创建子目录结构
            (base_dir / "subdir1").mkdir()
            (base_dir / "subdir2" / "nested").mkdir(parents=True)

            # 创建各层级的文件
            (base_dir / "root.c").touch()
            (base_dir / "subdir1" / "level1.c").touch()
            (base_dir / "subdir2" / "nested" / "level2.c").touch()

            result = extract_source_files(base_dir, [".c"])

            # 验证找到所有层级的文件
            assert len(result) == 3
            file_names = {f.name for f in result}
            assert file_names == {"root.c", "level1.c", "level2.c"}

    def test_exclude_rte_tmsapp_h(self):
        """测试排除 Rte_TmsApp.h 文件 (Story 2.6 - 任务 1.5)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            # 创建文件，包括 Rte_TmsApp.h
            (base_dir / "main.c").touch()
            (base_dir / "main.h").touch()
            (base_dir / "Rte_TmsApp.h").touch()  # 应被排除
            (base_dir / "utils.h").touch()

            result = extract_source_files(base_dir, [".c", ".h"])

            # 验证 Rte_TmsApp.h 被排除
            assert len(result) == 3
            file_names = {f.name for f in result}
            assert "Rte_TmsApp.h" not in file_names
            assert "main.c" in file_names
            assert "main.h" in file_names
            assert "utils.h" in file_names

    def test_returns_sorted_files(self):
        """测试返回排序后的文件列表 (Story 2.6 - 任务 1.6)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            # 创建文件（非字母顺序）
            (base_dir / "zulu.c").touch()
            (base_dir / "alpha.c").touch()
            (base_dir / "charlie.c").touch()
            (base_dir / "bravo.h").touch()

            result = extract_source_files(base_dir, [".c", ".h"])

            # 验证文件已排序（按路径）
            assert result[0].name == "alpha.c"
            assert result[1].name == "bravo.h"
            assert result[2].name == "charlie.c"
            assert result[3].name == "zulu.c"

    def test_empty_directory(self):
        """测试空目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            result = extract_source_files(base_dir, [".c", ".h"])

            assert len(result) == 0
            assert result == []

    def test_no_matching_extensions(self):
        """测试没有匹配扩展名的文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            # 创建非目标扩展名文件
            (base_dir / "readme.txt").touch()
            (base_dir / "data.json").touch()

            result = extract_source_files(base_dir, [".c", ".h"])

            assert len(result) == 0

    def test_nonexistent_directory(self):
        """测试不存在的目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "nonexistent"

            # 不存在的目录应返回空列表或抛出异常
            # 根据设计决策，这里返回空列表
            result = extract_source_files(base_dir, [".c", ".h"])

            assert len(result) == 0

    def test_single_extension(self):
        """测试单个扩展名"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            (base_dir / "file1.c").touch()
            (base_dir / "file2.c").touch()
            (base_dir / "file1.h").touch()  # 应被忽略

            result = extract_source_files(base_dir, [".c"])

            assert len(result) == 2
            assert all(f.suffix == ".c" for f in result)

    def test_custom_exclude_files(self):
        """测试自定义排除文件列表"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            (base_dir / "main.c").touch()
            (base_dir / "test.c").touch()
            (base_dir / "temp.h").touch()

            # 使用自定义排除列表
            result = extract_source_files(
                base_dir,
                [".c", ".h"],
                exclude=["test.c"]
            )

            assert len(result) == 2
            file_names = {f.name for f in result}
            assert "test.c" not in file_names
            assert "main.c" in file_names
            assert "temp.h" in file_names
