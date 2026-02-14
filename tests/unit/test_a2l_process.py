"""Unit tests for A2L XCP header replacement stage (Story 2.10).

This module tests the XCP header replacement functionality including:
- XCP header template reading
- XCP header section localization
- Content replacement
- File saving and renaming
- Verification
- Error handling and recovery suggestions

Test Coverage:
- Task 10.1: Create test file
- Task 10.2: Test XCP header template reading
- Task 10.3: Test XCP header section localization (various formats)
- Task 10.4: Test content replacement
- Task 10.5: Test file saving and renaming
- Task 10.6: Test verification (success and failure scenarios)
- Task 10.7: Test error handling and recovery suggestions
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# 添加 src 到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from stages.a2l_process import (
    read_xcp_header_template,
    find_xcp_header_section,
    replace_xcp_header_content,
    generate_timestamp,
    save_updated_a2l_file,
    verify_a2l_replacement,
    execute_xcp_header_replacement_stage,
    XCP_HEADER_START_PATTERN,
    XCP_HEADER_END_PATTERN,
    XCP_HEADER_SECTION_PATTERN
)
from core.models import (
    StageConfig,
    BuildContext,
    A2LHeaderReplacementConfig,
    StageStatus
)
from utils.errors import FileError


class TestXCPHeaderTemplateReading(unittest.TestCase):
    """测试 XCP 头文件模板读取功能 (Task 10.2)"""

    def setUp(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_messages = []
        self.log_callback = lambda msg: self.log_messages.append(msg)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_read_template_success(self):
        """测试成功读取模板文件"""
        # 创建测试模板文件
        template_path = Path(self.temp_dir) / "template.txt"
        template_content = "/begin XCP\n  /* XCP content */\n/end XCP\n"
        template_path.write_text(template_content, encoding='utf-8')

        # 读取模板
        result = read_xcp_header_template(template_path, self.log_callback)

        # 验证
        self.assertEqual(result, template_content)
        self.assertTrue(any("读取 XCP 头文件模板" in msg for msg in self.log_messages))

    def test_read_template_file_not_found(self):
        """测试模板文件不存在"""
        template_path = Path(self.temp_dir) / "nonexistent.txt"

        # 应该抛出 FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            read_xcp_header_template(template_path, self.log_callback)

    def test_read_template_utf8_encoding(self):
        """测试 UTF-8 编码读取"""
        template_path = Path(self.temp_dir) / "template_utf8.txt"
        template_content = "/begin XCP\n  /* 测试内容 */\n/end XCP\n"
        template_path.write_text(template_content, encoding='utf-8')

        result = read_xcp_header_template(template_path, self.log_callback)
        self.assertEqual(result, template_content)

    def test_read_template_gbk_encoding(self):
        """测试 GBK 编码读取"""
        template_path = Path(self.temp_dir) / "template_gbk.txt"
        template_content = "/begin XCP\n  /* 测试内容 */\n/end XCP\n"
        template_path.write_text(template_content, encoding='gbk')

        # UTF-8 读取失败后会尝试 GBK
        result = read_xcp_header_template(template_path, self.log_callback)
        self.assertEqual(result, template_content)


class TestXCPHeaderSectionLocalization(unittest.TestCase):
    """测试 XCP 头文件部分定位功能 (Task 10.3)"""

    def setUp(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_messages = []
        self.log_callback = lambda msg: self.log_messages.append(msg)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_find_xcp_header_standard_format(self):
        """测试标准格式的 XCP 头文件"""
        a2l_content = """
/begin CHARACTERISTIC
  /* characteristic definition */
/end CHARACTERISTIC

/begin XCP
  /* XCP header content */
  XCP_DRIVER_TYPE = CAN
/end XCP

/begin MEASUREMENT
  /* measurement definition */
/end MEASUREMENT
"""
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text(a2l_content, encoding='utf-8')

        result = find_xcp_header_section(a2l_path, self.log_callback)

        self.assertIsNotNone(result)
        start_pos, end_pos = result
        self.assertLess(start_pos, end_pos)
        self.assertTrue(any("找到 XCP 头文件部分" in msg for msg in self.log_messages))

    def test_find_xcp_header_with_comments(self):
        """测试带注释的 XCP 头文件"""
        a2l_content = """
/* This is a comment */
/begin XCP
  /* XCP header with comments */
  XCP_DRIVER_TYPE = CAN  /* Driver type */
/end XCP
"""
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text(a2l_content, encoding='utf-8')

        result = find_xcp_header_section(a2l_path, self.log_callback)

        self.assertIsNotNone(result)

    def test_find_xcp_header_case_insensitive(self):
        """测试大小写不敏感"""
        a2l_content = """
/BEGIN XCP
  /* XCP content */
/END XCP
"""
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text(a2l_content, encoding='utf-8')

        result = find_xcp_header_section(a2l_path, self.log_callback)

        self.assertIsNotNone(result)

    def test_find_xcp_header_not_found(self):
        """测试未找到 XCP 头文件"""
        a2l_content = """
/begin CHARACTERISTIC
  /* characteristic definition */
/end CHARACTERISTIC
"""
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text(a2l_content, encoding='utf-8')

        result = find_xcp_header_section(a2l_path, self.log_callback)

        self.assertIsNone(result)
        self.assertTrue(any("错误" in msg for msg in self.log_messages))

    def test_find_xcp_header_file_not_found(self):
        """测试 A2L 文件不存在"""
        a2l_path = Path(self.temp_dir) / "nonexistent.a2l"

        with self.assertRaises(FileNotFoundError):
            find_xcp_header_section(a2l_path, self.log_callback)


class TestContentReplacement(unittest.TestCase):
    """测试内容替换功能 (Task 10.4)"""

    def setUp(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_messages = []
        self.log_callback = lambda msg: self.log_messages.append(msg)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_replace_xcp_header_content(self):
        """测试替换 XCP 头文件内容"""
        # 创建测试 A2L 文件
        a2l_content = """
/begin CHARACTERISTIC
  /* characteristic */
/end CHARACTERISTIC

/begin XCP
  /* Old XCP header */
  XCP_DRIVER_TYPE = OLD
/end XCP

/begin MEASUREMENT
  /* measurement */
/end MEASUREMENT
"""
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text(a2l_content, encoding='utf-8')

        # 定位 XCP 头文件部分
        header_section = find_xcp_header_section(a2l_path, self.log_callback)
        self.assertIsNotNone(header_section)

        # 新的 XCP 头文件内容
        new_xcp = "/begin XCP\n  /* New XCP header */\n  XCP_DRIVER_TYPE = NEW\n/end XCP\n"

        # 替换
        updated_content = replace_xcp_header_content(
            a2l_path,
            header_section,
            new_xcp,
            self.log_callback
        )

        # 验证
        self.assertIn("New XCP header", updated_content)
        self.assertNotIn("Old XCP header", updated_content)
        self.assertIn("CHARACTERISTIC", updated_content)  # 其他内容保留
        self.assertIn("MEASUREMENT", updated_content)  # 其他内容保留

    def test_replace_content_logging(self):
        """测试替换日志记录"""
        a2l_content = """
/begin XCP
  /* Old header */
/end XCP
"""
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text(a2l_content, encoding='utf-8')

        header_section = find_xcp_header_section(a2l_path, self.log_callback)
        new_xcp = "/begin XCP\n  /* New header */\n/end XCP\n"

        replace_xcp_header_content(a2l_path, header_section, new_xcp, self.log_callback)

        # 验证日志
        self.assertTrue(any("替换 XCP 头文件内容" in msg for msg in self.log_messages))


class TestFileSavingAndRenaming(unittest.TestCase):
    """测试文件保存和重命名功能 (Task 10.5)"""

    def setUp(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_messages = []
        self.log_callback = lambda msg: self.log_messages.append(msg)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_timestamp(self):
        """测试时间戳生成"""
        timestamp = generate_timestamp("_%Y_%m_%d_%H_%M")

        # 验证格式
        self.assertTrue(timestamp.startswith("_"))
        self.assertEqual(len(timestamp), 17)  # _YYYY_MM_DD_HH_MM

    def test_save_a2l_file_success(self):
        """测试成功保存 A2L 文件"""
        a2l_config = A2LHeaderReplacementConfig(
            output_dir=self.temp_dir,
            output_prefix="tmsAPP_upAdress"
        )
        updated_content = "/begin XCP\n  /* content */\n/end XCP\n"

        output_path = save_updated_a2l_file(a2l_config, updated_content, self.log_callback)

        # 验证文件存在
        self.assertTrue(output_path.exists())
        self.assertTrue(output_path.name.startswith("tmsAPP_upAdress_"))
        self.assertTrue(output_path.suffix == ".a2l")

        # 验证文件内容
        content = output_path.read_text(encoding='utf-8')
        self.assertEqual(content, updated_content)

    def test_save_a2l_file_atomically(self):
        """测试原子性写入"""
        a2l_config = A2LHeaderReplacementConfig(
            output_dir=self.temp_dir,
            output_prefix="tmsAPP_test"
        )
        updated_content = "/begin XCP\n  /* content */\n/end XCP\n"

        output_path = save_updated_a2l_file(a2l_config, updated_content, self.log_callback)

        # 验证没有临时文件残留
        temp_files = list(Path(self.temp_dir).glob("tmp*"))
        self.assertEqual(len(temp_files), 0)

    def test_save_a2l_file_create_dir(self):
        """测试自动创建目录"""
        output_dir = Path(self.temp_dir) / "subdir" / "nested"
        a2l_config = A2LHeaderReplacementConfig(
            output_dir=str(output_dir),
            output_prefix="tmsAPP_test"
        )
        updated_content = "/begin XCP\n  /* content */\n/end XCP\n"

        output_path = save_updated_a2l_file(a2l_config, updated_content, self.log_callback)

        # 验证目录和文件创建成功
        self.assertTrue(output_dir.exists())
        self.assertTrue(output_path.exists())


class TestVerification(unittest.TestCase):
    """测试验证功能 (Task 10.6)"""

    def setUp(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_messages = []
        self.log_callback = lambda msg: self.log_messages.append(msg)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_verify_success(self):
        """测试验证成功"""
        xcp_template = "/begin XCP\n  /* Test XCP header */\n  XCP_DRIVER_TYPE = CAN\n/end XCP\n"

        output_path = Path(self.temp_dir) / "output.a2l"
        output_path.write_text(xcp_template, encoding='utf-8')

        result = verify_a2l_replacement(output_path, xcp_template, self.log_callback)

        self.assertTrue(result)
        self.assertTrue(any("验证成功" in msg for msg in self.log_messages))

    def test_verify_file_not_exists(self):
        """测试文件不存在"""
        xcp_template = "/begin XCP\n  /* content */\n/end XCP\n"
        output_path = Path(self.temp_dir) / "nonexistent.a2l"

        result = verify_a2l_replacement(output_path, xcp_template, self.log_callback)

        self.assertFalse(result)
        self.assertTrue(any("验证失败" in msg for msg in self.log_messages))

    def test_verify_empty_file(self):
        """测试空文件"""
        xcp_template = "/begin XCP\n  /* content */\n/end XCP\n"
        output_path = Path(self.temp_dir) / "empty.a2l"
        output_path.write_text("", encoding='utf-8')

        result = verify_a2l_replacement(output_path, xcp_template, self.log_callback)

        self.assertFalse(result)

    def test_verify_content_mismatch(self):
        """测试内容不匹配"""
        xcp_template = "/begin XCP\n  /* Test XCP */\n/end XCP\n"

        output_path = Path(self.temp_dir) / "output.a2l"
        output_path.write_text("/begin OTHER\n  /* Different content */\n/end OTHER\n", encoding='utf-8')

        result = verify_a2l_replacement(output_path, xcp_template, self.log_callback)

        self.assertFalse(result)


class TestErrorHandling(unittest.TestCase):
    """测试错误处理和恢复建议 (Task 10.7)"""

    def setUp(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_messages = []
        self.log_callback = lambda msg: self.log_messages.append(msg)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_template_not_found_error(self):
        """测试模板文件不存在错误"""
        template_path = Path(self.temp_dir) / "nonexistent.txt"

        try:
            read_xcp_header_template(template_path, self.log_callback)
            self.fail("应该抛出 FileNotFoundError")
        except FileNotFoundError:
            # 预期的异常
            pass

    def test_a2l_file_not_found_error(self):
        """测试 A2L 文件不存在错误"""
        a2l_path = Path(self.temp_dir) / "nonexistent.a2l"

        try:
            find_xcp_header_section(a2l_path, self.log_callback)
            self.fail("应该抛出 FileNotFoundError")
        except FileNotFoundError:
            # 预期的异常
            pass

    def test_xcp_header_not_found_suggestion(self):
        """测试未找到 XCP 头文件的建议"""
        a2l_content = "/begin CHARACTERISTIC\n  /* char */\n/end CHARACTERISTIC\n"
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text(a2l_content, encoding='utf-8')

        result = find_xcp_header_section(a2l_path, self.log_callback)

        self.assertIsNone(result)
        self.assertTrue(any("错误" in msg for msg in self.log_messages))


class TestExecuteXCPHeaderReplacementStage(unittest.TestCase):
    """测试 XCP 头文件替换阶段执行 (集成测试)"""

    def setUp(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_messages = []
        self.log_callback = lambda msg: self.log_messages.append(msg)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_execute_stage_success(self):
        """测试成功执行阶段"""
        # 创建测试 A2L 文件
        a2l_content = """
/begin CHARACTERISTIC
  /* characteristic */
/end CHARACTERISTIC

/begin XCP
  /* Old XCP header */
  XCP_DRIVER_TYPE = OLD
/end XCP

/begin MEASUREMENT
  /* measurement */
/end MEASUREMENT
"""
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text(a2l_content, encoding='utf-8')

        # 创建 XCP 模板
        template_path = Path(self.temp_dir) / "template.txt"
        template_content = "/begin XCP\n  /* New XCP header */\n  XCP_DRIVER_TYPE = NEW\n/end XCP\n"
        template_path.write_text(template_content, encoding='utf-8')

        # 创建配置
        a2l_config = A2LHeaderReplacementConfig(
            xcp_template_path=str(template_path),
            a2l_source_path=str(a2l_path),
            output_dir=self.temp_dir,
            output_prefix="tmsAPP_test"
        )

        # 使用 setattr 添加 custom_config 属性
        stage_config = StageConfig(
            name="a2l_process"
        )
        setattr(stage_config, "custom_config", a2l_config)

        context = BuildContext(
            log_callback=self.log_callback
        )

        # 执行阶段
        result = execute_xcp_header_replacement_stage(stage_config, context)

        # 验证结果
        self.assertEqual(result.status, StageStatus.COMPLETED)
        self.assertEqual(len(result.output_files), 1)

        # 验证输出文件
        output_path = Path(result.output_files[0])
        self.assertTrue(output_path.exists())
        self.assertTrue(output_path.name.startswith("tmsAPP_test_"))

        # 验证内容已替换
        content = output_path.read_text(encoding='utf-8')
        self.assertIn("New XCP header", content)
        self.assertNotIn("Old XCP header", content)

    def test_execute_stage_template_not_found(self):
        """测试模板文件不存在"""
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text("/begin XCP\n  /* content */\n/end XCP\n", encoding='utf-8')

        a2l_config = A2LHeaderReplacementConfig(
            xcp_template_path="nonexistent.txt",
            a2l_source_path=str(a2l_path),
            output_dir=self.temp_dir
        )

        # 使用 setattr 添加 custom_config 属性
        stage_config = StageConfig(
            name="a2l_process"
        )
        setattr(stage_config, "custom_config", a2l_config)

        context = BuildContext(log_callback=self.log_callback)

        result = execute_xcp_header_replacement_stage(stage_config, context)

        self.assertEqual(result.status, StageStatus.FAILED)
        self.assertTrue(len(result.suggestions) > 0)

    def test_execute_stage_a2l_not_found(self):
        """测试 A2L 文件不存在"""
        template_path = Path(self.temp_dir) / "template.txt"
        template_path.write_text("/begin XCP\n  /* content */\n/end XCP\n", encoding='utf-8')

        a2l_config = A2LHeaderReplacementConfig(
            xcp_template_path=str(template_path),
            a2l_source_path="nonexistent.a2l",
            output_dir=self.temp_dir
        )

        # 使用 setattr 添加 custom_config 属性
        stage_config = StageConfig(
            name="a2l_process"
        )
        setattr(stage_config, "custom_config", a2l_config)

        context = BuildContext(log_callback=self.log_callback)

        result = execute_xcp_header_replacement_stage(stage_config, context)

        self.assertEqual(result.status, StageStatus.FAILED)
        self.assertTrue(len(result.suggestions) > 0)

    def test_execute_stage_xcp_header_not_found(self):
        """测试未找到 XCP 头文件"""
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text("/begin CHARACTERISTIC\n  /* char */\n/end CHARACTERISTIC\n", encoding='utf-8')

        template_path = Path(self.temp_dir) / "template.txt"
        template_path.write_text("/begin XCP\n  /* content */\n/end XCP\n", encoding='utf-8')

        a2l_config = A2LHeaderReplacementConfig(
            xcp_template_path=str(template_path),
            a2l_source_path=str(a2l_path),
            output_dir=self.temp_dir
        )

        # 使用 setattr 添加 custom_config 属性
        stage_config = StageConfig(
            name="a2l_process"
        )
        setattr(stage_config, "custom_config", a2l_config)

        context = BuildContext(log_callback=self.log_callback)

        result = execute_xcp_header_replacement_stage(stage_config, context)

        self.assertEqual(result.status, StageStatus.FAILED)
        self.assertTrue(len(result.suggestions) > 0)

    def test_execute_stage_context_integration(self):
        """测试 BuildContext 集成"""
        a2l_path = Path(self.temp_dir) / "test.a2l"
        a2l_path.write_text("/begin XCP\n  /* Old */\n/end XCP\n", encoding='utf-8')

        template_path = Path(self.temp_dir) / "template.txt"
        template_path.write_text("/begin XCP\n  /* New */\n/end XCP\n", encoding='utf-8')

        a2l_config = A2LHeaderReplacementConfig(
            xcp_template_path=str(template_path),
            a2l_source_path=str(a2l_path),
            output_dir=self.temp_dir
        )

        # 使用 setattr 添加 custom_config 属性
        stage_config = StageConfig(
            name="a2l_process"
        )
        setattr(stage_config, "custom_config", a2l_config)

        context = BuildContext(log_callback=self.log_callback)

        result = execute_xcp_header_replacement_stage(stage_config, context)

        # 验证 BuildContext 已更新
        self.assertEqual(result.status, StageStatus.COMPLETED)
        self.assertIn("a2l_output_path", context.state)
        self.assertIn("a2l_xcp_replaced_path", context.state)


if __name__ == '__main__':
    unittest.main()
