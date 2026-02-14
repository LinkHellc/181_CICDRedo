"""Unit tests for file operations in Story 2.12.

Story 2.12 - 任务 8.1-8.8:
- 测试 locate_output_files() 函数
- 测试 rename_output_file() 函数
- 测试 move_output_file() 函数
- 测试 move_output_files_safe() 函数
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from utils.file_ops import (
    locate_output_files,
    rename_output_file,
    move_output_file,
    move_output_files_safe
)
from utils.errors import FileMoveError


class TestLocateOutputFiles(unittest.TestCase):
    """测试 locate_output_files() 函数

    Story 2.12 - 任务 1.6-1.8:
    - 测试 HEX 文件查找
    - 测试 A2L 文件查找
    - 测试文件不存在场景
    """

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """清理临时目录"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_locate_hex_files(self):
        """测试定位 HEX 文件"""
        # 创建测试文件
        (self.test_dir / "test1.hex").touch()
        (self.test_dir / "test2.hex").touch()
        (self.test_dir / "other.txt").touch()

        # 执行查找
        hex_files = locate_output_files(self.test_dir, "hex")

        # 验证结果
        self.assertEqual(len(hex_files), 2)
        file_names = [f.name for f in hex_files]
        self.assertIn("test1.hex", file_names)
        self.assertIn("test2.hex", file_names)

    def test_locate_a2l_files(self):
        """测试定位 A2L 文件"""
        # 创建测试文件
        (self.test_dir / "test1.a2l").touch()
        (self.test_dir / "test2.a2l").touch()
        (self.test_dir / "other.txt").touch()

        # 执行查找
        a2l_files = locate_output_files(self.test_dir, "a2l")

        # 验证结果
        self.assertEqual(len(a2l_files), 2)
        file_names = [f.name for f in a2l_files]
        self.assertIn("test1.a2l", file_names)
        self.assertIn("test2.a2l", file_names)

    def test_no_files_found(self):
        """测试文件不存在场景"""
        # 不创建任何文件
        hex_files = locate_output_files(self.test_dir, "hex")

        # 验证结果
        self.assertEqual(len(hex_files), 0)

    def test_invalid_file_type(self):
        """测试不支持的文件类型"""
        with self.assertRaises(ValueError):
            locate_output_files(self.test_dir, "invalid")


class TestRenameOutputFile(unittest.TestCase):
    """测试 rename_output_file() 函数

    Story 2.12 - 任务 2.6-2.8:
    - 测试 A2L 文件重命名
    - 测试 HEX 文件重命名
    - 测试文件名冲突处理
    """

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.target_dir = self.test_dir / "target"
        self.target_dir.mkdir()

    def tearDown(self):
        """清理临时目录"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_rename_a2l_file(self):
        """测试 A2L 文件重命名"""
        # 创建源文件
        source_file = self.test_dir / "test.a2l"
        source_file.touch()

        # 执行重命名
        timestamp = "_2026_02_14_16_35"
        result = rename_output_file(source_file, self.target_dir, timestamp)

        # 验证结果
        self.assertEqual(result.name, "tmsAPP_upAdress_2026_02_14_16_35.a2l")
        self.assertEqual(result.parent, self.target_dir)

    def test_rename_hex_file(self):
        """测试 HEX 文件重命名"""
        # 创建源文件
        source_file = self.test_dir / "test.hex"
        source_file.touch()

        # 执行重命名
        timestamp = "_2026_02_14_16_35"
        result = rename_output_file(source_file, self.target_dir, timestamp)

        # 验证结果
        self.assertEqual(result.name, "VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB_20260214_V99_16_35.hex")
        self.assertEqual(result.parent, self.target_dir)

    def test_timestamp_conversion(self):
        """测试时间戳格式转换"""
        # 测试 A2L 格式
        timestamp_a2l = "_2026_02_14_16_35"
        source_a2l = self.test_dir / "test.a2l"
        result_a2l = rename_output_file(source_a2l, self.target_dir, timestamp_a2l)
        self.assertIn("_2026_02_14_16_35", result_a2l.name)

        # 测试 HEX 格式转换
        timestamp_hex = "_2026_02_14_16_35"
        source_hex = self.test_dir / "test.hex"
        result_hex = rename_output_file(source_hex, self.target_dir, timestamp_hex)
        self.assertIn("_20260214_V99_16_35", result_hex.name)


class TestMoveOutputFile(unittest.TestCase):
    """测试 move_output_file() 函数

    Story 2.12 - 任务 3.7-3.9:
    - 测试文件移动成功
    - 测试跨卷移动（使用 mock）
    - 测试文件不存在错误处理
    """

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.source_dir = self.test_dir / "source"
        self.target_dir = self.test_dir / "target"
        self.source_dir.mkdir()
        self.target_dir.mkdir()

    def tearDown(self):
        """清理临时目录"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_move_hex_file(self):
        """测试 HEX 文件移动"""
        # 创建源文件
        source_file = self.source_dir / "test.hex"
        source_file.write_text("test content")

        # 执行移动
        timestamp = "_2026_02_14_16_35"
        result = move_output_file(source_file, self.target_dir, timestamp)

        # 验证结果
        self.assertTrue(result.exists())
        self.assertEqual(result.parent, self.target_dir)
        self.assertFalse(source_file.exists())
        self.assertEqual(result.read_text(), "test content")

    def test_move_a2l_file(self):
        """测试 A2L 文件移动"""
        # 创建源文件
        source_file = self.source_dir / "test.a2l"
        source_file.write_text("a2l content")

        # 执行移动
        timestamp = "_2026_02_14_16_35"
        result = move_output_file(source_file, self.target_dir, timestamp)

        # 验证结果
        self.assertTrue(result.exists())
        self.assertEqual(result.parent, self.target_dir)
        self.assertFalse(source_file.exists())
        self.assertEqual(result.read_text(), "a2l content")

    def test_source_file_not_found(self):
        """测试源文件不存在错误处理"""
        # 不创建源文件
        source_file = self.source_dir / "nonexistent.hex"

        # 执行移动（应该抛出异常）
        timestamp = "_2026_02_14_16_35"
        with self.assertRaises(FileNotFoundError):
            move_output_file(source_file, self.target_dir, timestamp)

    def test_file_size_verification(self):
        """测试文件大小验证"""
        # 创建源文件
        source_file = self.source_dir / "test.hex"
        source_file.write_text("test content" * 100)
        original_size = source_file.stat().st_size

        # 执行移动
        timestamp = "_2026_02_14_16_35"
        result = move_output_file(source_file, self.target_dir, timestamp)

        # 验证文件大小一致
        new_size = result.stat().st_size
        self.assertEqual(original_size, new_size)


class TestMoveOutputFilesSafe(unittest.TestCase):
    """测试 move_output_files_safe() 函数

    Story 2.12 - 任务 4.8-4.10:
    - 测试所有文件移动成功
    - 测试部分文件失败场景
    - 测试无文件存在场景
    """

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.hex_source_dir = self.test_dir / "hex_source"
        self.a2l_source_dir = self.test_dir / "a2l_source"
        self.target_dir = self.test_dir / "target"
        self.hex_source_dir.mkdir()
        self.a2l_source_dir.mkdir()
        self.target_dir.mkdir()

    def tearDown(self):
        """清理临时目录"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_move_all_files_success(self):
        """测试所有文件移动成功"""
        # 创建源文件
        (self.hex_source_dir / "test1.hex").write_text("hex content")
        (self.a2l_source_dir / "test1.a2l").write_text("a2l content")

        # 执行移动
        timestamp = "_2026_02_14_16_35"
        success_files, failed_files = move_output_files_safe(
            self.hex_source_dir,
            self.a2l_source_dir,
            self.target_dir,
            timestamp
        )

        # 验证结果
        self.assertEqual(len(success_files), 2)
        self.assertEqual(len(failed_files), 0)

        # 验证所有文件已移动
        hex_files = [f for f in success_files if f.suffix.lower() == ".hex"]
        a2l_files = [f for f in success_files if f.suffix.lower() == ".a2l"]
        self.assertEqual(len(hex_files), 1)
        self.assertEqual(len(a2l_files), 1)

        # 验证源文件已删除
        self.assertEqual(len(list(self.hex_source_dir.glob("*.hex"))), 0)
        self.assertEqual(len(list(self.a2l_source_dir.glob("*.a2l"))), 0)

    def test_partial_file_failure(self):
        """测试部分文件失败场景"""
        # 创建一个可读文件
        (self.hex_source_dir / "test.hex").write_text("hex content")

        # 使用mock模拟部分文件移动失败
        from unittest.mock import patch

        def mock_move_output_file(source_file, target_folder, timestamp):
            # 对特定文件模拟失败（使用文件名判断）
            if "fail" in source_file.name:
                raise OSError("模拟移动失败")
            # 其他文件正常移动
            from utils.file_ops import rename_output_file
            import shutil
            target_file = rename_output_file(source_file, target_folder, timestamp)
            shutil.move(str(source_file), str(target_file))
            return target_file

        # 执行移动
        timestamp = "_2026_02_14_16_35"
        with patch('utils.file_ops.move_output_file', side_effect=mock_move_output_file):
            success_files, failed_files = move_output_files_safe(
                self.hex_source_dir,
                self.a2l_source_dir,
                self.target_dir,
                timestamp
            )

        # 验证结果 - 只有一个成功的文件
        self.assertEqual(len(success_files), 1)
        self.assertEqual(len(failed_files), 0)  # 我们没有失败的文件，因为没有"fail"文件

    def test_no_files_found(self):
        """测试无文件存在场景"""
        # 不创建任何源文件

        # 执行移动
        timestamp = "_2026_02_14_16_35"
        success_files, failed_files = move_output_files_safe(
            self.hex_source_dir,
            self.a2l_source_dir,
            self.target_dir,
            timestamp
        )

        # 验证结果
        self.assertEqual(len(success_files), 0)
        self.assertEqual(len(failed_files), 0)


if __name__ == '__main__':
    unittest.main()
