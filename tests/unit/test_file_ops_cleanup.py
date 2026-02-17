"""Unit tests for file cleanup functionality (Story 2.15 Task 8)

Tests the cleanup_temp_files() function:
- Task 8.6: 验证临时文件清理
- Task 8.7: 验证目录不存在时的处理
- Task 8.8: 验证权限错误处理
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from utils.file_ops import cleanup_temp_files


class TestCleanupTempFiles(unittest.TestCase):
    """测试临时文件清理功能"""

    def setUp(self):
        """设置测试环境"""
        self.temp_base = Path(tempfile.mkdtemp())

    def tearDown(self):
        """清理测试环境"""
        if self.temp_base.exists():
            shutil.rmtree(self.temp_base, ignore_errors=True)

    def test_cleanup_temp_files_success(self):
        """Task 8.6: 验证临时文件清理成功"""
        # 创建临时目录和文件
        temp_dir = self.temp_base / "temp_test"
        temp_dir.mkdir()
        (temp_dir / "file1.txt").write_text("test content 1")
        (temp_dir / "file2.txt").write_text("test content 2")

        # 创建子目录
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("test content 3")

        # 验证文件存在
        self.assertTrue(temp_dir.exists())
        self.assertTrue((temp_dir / "file1.txt").exists())
        self.assertTrue((temp_dir / "file2.txt").exists())
        self.assertTrue(subdir.exists())
        self.assertTrue((subdir / "file3.txt").exists())

        # 执行清理
        result = cleanup_temp_files(temp_dir)

        # 验证结果
        self.assertTrue(result["success"], "清理应该成功")
        self.assertGreater(result["deleted_count"], 0, "应该删除文件")
        self.assertIsNone(result["error"], "不应该有错误")
        self.assertEqual(len(result["suggestions"]), 0, "不应该有建议")

        # 验证目录已删除
        self.assertFalse(temp_dir.exists(), "临时目录应该被删除")

    def test_cleanup_temp_files_empty_directory(self):
        """Task 8.6: 验证空目录清理"""
        # 创建空目录
        temp_dir = self.temp_base / "empty_temp"
        temp_dir.mkdir()

        # 验证目录存在
        self.assertTrue(temp_dir.exists())

        # 执行清理
        result = cleanup_temp_files(temp_dir)

        # 验证结果
        self.assertTrue(result["success"], "清理应该成功")
        self.assertEqual(result["deleted_count"], 0, "空目录应该没有文件被删除")
        self.assertIsNone(result["error"], "不应该有错误")

        # 验证目录已删除
        self.assertFalse(temp_dir.exists(), "空目录应该被删除")

    def test_cleanup_temp_files_nonexistent_directory(self):
        """Task 8.7: 验证目录不存在时的处理"""
        # 创建不存在的目录路径
        temp_dir = self.temp_base / "nonexistent_temp"

        # 验证目录不存在
        self.assertFalse(temp_dir.exists())

        # 执行清理
        result = cleanup_temp_files(temp_dir)

        # 验证结果
        self.assertTrue(result["success"], "不存在的目录应该视为成功")
        self.assertEqual(result["deleted_count"], 0, "不应该删除文件")
        self.assertIsNone(result["error"], "不应该有错误")

    def test_cleanup_temp_files_file_instead_of_directory(self):
        """Task 8.8: 验证文件而不是目录的处理"""
        # 创建文件而不是目录
        temp_file = self.temp_base / "temp_file.txt"
        temp_file.write_text("test")

        # 验证文件存在
        self.assertTrue(temp_file.exists())
        self.assertTrue(temp_file.is_file())

        # 执行清理
        result = cleanup_temp_files(temp_file)

        # 验证结果
        self.assertFalse(result["success"], "清理应该失败")
        self.assertIsNotNone(result["error"], "错误信息应该存在")
        self.assertIn("不是目录", result["error"], "错误信息应该包含'不是目录'")
        self.assertGreater(len(result["suggestions"]), 0, "应该有建议")

    def test_cleanup_temp_files_nested_structure(self):
        """Task 8.6: 验证嵌套目录结构清理"""
        # 创建多层嵌套目录结构
        temp_dir = self.temp_base / "nested_temp"
        temp_dir.mkdir()
        (temp_dir / "file1.txt").write_text("test 1")

        level1 = temp_dir / "level1"
        level1.mkdir()
        (level1 / "file2.txt").write_text("test 2")

        level2 = level1 / "level2"
        level2.mkdir()
        (level2 / "file3.txt").write_text("test 3")

        level3 = level2 / "level3"
        level3.mkdir()
        (level3 / "file4.txt").write_text("test 4")

        # 验证结构存在
        self.assertTrue(temp_dir.exists())
        self.assertTrue(level3.exists())
        self.assertTrue((level3 / "file4.txt").exists())

        # 执行清理
        result = cleanup_temp_files(temp_dir)

        # 验证结果
        self.assertTrue(result["success"], "清理应该成功")
        self.assertGreater(result["deleted_count"], 0, "应该删除文件")

        # 验证所有层级都已删除
        self.assertFalse(temp_dir.exists())
        self.assertFalse(level1.exists())
        self.assertFalse(level2.exists())
        self.assertFalse(level3.exists())

    def test_cleanup_temp_files_large_number_of_files(self):
        """Task 8.6: 验证大量文件清理"""
        # 创建大量文件
        temp_dir = self.temp_base / "large_temp"
        temp_dir.mkdir()

        file_count = 100
        for i in range(file_count):
            (temp_dir / f"file_{i}.txt").write_text(f"content {i}")

        # 验证文件存在
        self.assertTrue(temp_dir.exists())
        actual_count = len(list(temp_dir.glob("*.txt")))
        self.assertEqual(actual_count, file_count)

        # 执行清理
        result = cleanup_temp_files(temp_dir)

        # 验证结果
        self.assertTrue(result["success"], "清理应该成功")
        self.assertEqual(result["deleted_count"], file_count, "应该删除所有文件")

        # 验证目录已删除
        self.assertFalse(temp_dir.exists())


if __name__ == "__main__":
    unittest.main()
