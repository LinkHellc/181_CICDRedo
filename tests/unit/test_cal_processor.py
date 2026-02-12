"""Unit tests for Cal.c file processing module.

Story 2.6 - 任务 2-4: Cal.c 文件修改和验证
- 测试 Cal.c 文件定位
- 测试前缀插入（各种头文件格式）
- 测试后缀插入（各种文件结尾格式）
- 测试文件编码处理（UTF-8, UTF-8-BOM, GBK）
- 测试备份和恢复逻辑
"""

import pytest
from pathlib import Path
import tempfile

from stages.file_process import (
    find_cal_file,
    insert_cal_prefix,
    insert_cal_suffix,
    verify_cal_modification
)


class TestFindCalFile:
    """测试 Cal.c 文件定位"""

    def test_find_cal_file_exists(self):
        """测试找到 Cal.c 文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            (base_dir / "main.c").touch()
            (base_dir / "Cal.c").touch()  # 大小写敏感
            (base_dir / "utils.c").touch()

            result = find_cal_file([base_dir / "main.c", base_dir / "Cal.c", base_dir / "utils.c"])

            assert result is not None
            assert result.name == "Cal.c"

    def test_find_cal_file_not_exists(self):
        """测试 Cal.c 不存在"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            (base_dir / "main.c").touch()
            (base_dir / "utils.c").touch()

            result = find_cal_file([base_dir / "main.c", base_dir / "utils.c"])

            assert result is None

    def test_find_cal_file_empty_list(self):
        """测试空文件列表"""
        result = find_cal_file([])
        assert result is None


class TestInsertCalPrefix:
    """测试 Cal.c 前缀插入"""

    @pytest.fixture
    def sample_cal_content(self):
        """示例 Cal.c 内容"""
        return """#include "header1.h"
#include "header2.h"

int cal_value = 0;
"""

    @pytest.fixture
    def cal_with_ifdef(self):
        """包含 ifdef 块的 Cal.c"""
        return """#include "header.h"
#ifdef DEBUG
    #define DEBUG_MODE 1
#endif

int cal_value = 0;
"""

    @pytest.fixture
    def cal_with_extern_c(self):
        """包含 extern "C" 块的 Cal.c"""
        return """#include <stdio.h>
#ifdef __cplusplus
extern "C" {
#endif

int cal_value = 0;
"""

    @pytest.fixture
    def log_callback(self):
        """创建日志回调"""
        messages = []
        def callback(msg):
            messages.append(msg)
        return callback, messages

    def test_insert_prefix_simple_headers(self, sample_cal_content, log_callback):
        """测试简单头文件后插入前缀 (Story 2.6 - 任务 2.3-2.5)"""
        callback, messages = log_callback

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(sample_cal_content, encoding="utf-8")

            result = insert_cal_prefix(cal_file, callback)

            assert result is True
            content = cal_file.read_text(encoding="utf-8")

            # 验证前缀代码插入
            assert '#define ASW_ATECH_START_SEC_CALIB' in content
            assert '#include "Xcp_MemMap.h"' in content
            # 验证插入位置（在头文件之后）
            lines = content.split("\n")
            prefix_idx = next(i for i, line in enumerate(lines) if "ASW_ATECH_START_SEC_CALIB" in line)
            # 前缀应在头文件之后
            assert any("#include" in lines[i] for i in range(prefix_idx))

    def test_insert_prefix_after_ifdef_block(self, cal_with_ifdef, log_callback):
        """测试在 ifdef 块后插入"""
        callback, messages = log_callback

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(cal_with_ifdef, encoding="utf-8")

            result = insert_cal_prefix(cal_file, callback)

            assert result is True
            content = cal_file.read_text(encoding="utf-8")

            assert '#define ASW_ATECH_START_SEC_CALIB' in content

    def test_insert_prefix_with_extern_c(self, cal_with_extern_c, log_callback):
        """测试处理 extern "C" 块"""
        callback, messages = log_callback

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(cal_with_extern_c, encoding="utf-8")

            result = insert_cal_prefix(cal_file, callback)

            assert result is True

    def test_insert_prefix_creates_backup(self, sample_cal_content, log_callback):
        """测试创建备份文件 (Story 2.6 - 任务 7)"""
        callback, messages = log_callback

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(sample_cal_content, encoding="utf-8")

            # 首先创建备份，模拟备份功能
            from utils.file_ops import backup_file
            backup_path = backup_file(cal_file)
            assert backup_path.exists()

            # 备份文件成功创建后，在成功插入后会被清理
            # 这是预期行为 (Story 2.6 - 任务 7.5)
            insert_cal_prefix(cal_file, callback)

            # 备份文件应该已被清理
            backup_file = Path(str(cal_file) + ".bak")
            assert not backup_file.exists()

    def test_insert_prefix_utf8_bom(self, log_callback):
        """测试 UTF-8-BOM 编码处理 (Story 2.6 - 任务 2.6)"""
        callback, messages = log_callback

        content = """#include "header.h"
int cal = 0;
"""
        # UTF-8-BOM 编码
        utf8_bom = "\ufeff".encode("utf-8") + content.encode("utf-8")

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_bytes(utf8_bom)

            result = insert_cal_prefix(cal_file, callback)

            assert result is True
            # 验证内容正确
            new_content = cal_file.read_text(encoding="utf-8-sig")
            assert "ASW_ATECH_START_SEC_CALIB" in new_content


class TestInsertCalSuffix:
    """测试 Cal.c 后缀插入"""

    @pytest.fixture
    def log_callback(self):
        messages = []
        def callback(msg):
            messages.append(msg)
        return callback, messages

    def test_insert_suffix_simple_file(self, log_callback):
        """测试简单文件末尾插入后缀"""
        callback, messages = log_callback

        # 使用简单的内容，避免字符串中的特殊字符
        content = """#include <stdio.h>

int cal_value = 0;
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(content, encoding="utf-8")

            result = insert_cal_suffix(cal_file, callback)

            assert result is True
            new_content = cal_file.read_text(encoding="utf-8")

            # 验证后缀代码
            assert '#define ASW_ATECH_STOP_SEC_CALIB' in new_content
            assert '#include "Xcp_MemMap.h"' in new_content
            assert '#ifdef __cplusplus' in new_content
            assert '}' in new_content
            assert '#endif' in new_content

    def test_insert_suffix_before_existing_extern_c(self, log_callback):
        """测试在现有 extern "C" 块前插入"""
        callback, messages = log_callback

        content = """#include <stdio.h>

int cal_value = 0;

#ifdef __cplusplus
}
#endif
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(content, encoding="utf-8")

            result = insert_cal_suffix(cal_file, callback)

            assert result is True
            new_content = cal_file.read_text(encoding="utf-8")

            # 验证后缀在 extern C 块之前
            lines = new_content.split("\n")
            suffix_idx = next(i for i, line in enumerate(lines) if "ASW_ATECH_STOP_SEC_CALIB" in line)
            extern_c_idx = next(i for i, line in enumerate(lines) if "#ifdef __cplusplus" in line and i > suffix_idx)
            assert suffix_idx < extern_c_idx

    def test_insert_suffix_handles_trailing_newlines(self, log_callback):
        """测试处理文件末尾换行符"""
        callback, messages = log_callback

        # 多个换行符结尾
        content = """int cal = 0;


"""

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(content, encoding="utf-8")

            result = insert_cal_suffix(cal_file, callback)

            assert result is True
            # 验证后缀被插入
            new_content = cal_file.read_text(encoding="utf-8")
            assert "ASW_ATECH_STOP_SEC_CALIB" in new_content


class TestVerifyCalModification:
    """测试 Cal.c 修改验证"""

    @pytest.fixture
    def log_callback(self):
        messages = []
        def callback(msg):
            messages.append(msg)
        return callback, messages

    def test_verify_valid_modification(self, log_callback):
        """测试验证成功的修改"""
        callback, messages = log_callback

        content = """#include <stdio.h>
#define ASW_ATECH_START_SEC_CALIB
#include "Xcp_MemMap.h"

int cal = 0;
#define ASW_ATECH_STOP_SEC_CALIB
#include "Xcp_MemMap.h"
#ifdef __cplusplus
}
#endif
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(content, encoding="utf-8")

            result = verify_cal_modification(cal_file, callback, check_brackets=False)

            assert result is True

    def test_verify_missing_prefix(self, log_callback):
        """测试缺少前缀"""
        callback, messages = log_callback

        content = """#include "header.h"

int cal = 0;
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(content, encoding="utf-8")

            result = verify_cal_modification(cal_file, callback)

            assert result is False

    def test_verify_missing_suffix(self, log_callback):
        """测试缺少后缀"""
        callback, messages = log_callback

        content = """#include "header.h"
#define ASW_ATECH_START_SEC_CALIB
#include "Xcp_MemMap.h"

int cal = 0;
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(content, encoding="utf-8")

            result = verify_cal_modification(cal_file, callback)

            assert result is False

    def test_verify_bracket_matching(self, log_callback):
        """测试括号匹配验证"""
        callback, messages = log_callback

        # 括号不匹配
        content = """#include "header.h"
#define ASW_ATECH_START_SEC_CALIB
#include "Xcp_MemMap.h"

int cal = (0 + 1;
#define ASW_ATECH_STOP_SEC_CALIB
#include "Xcp_MemMap.h"
#ifdef __cplusplus
}
#endif
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(content, encoding="utf-8")

            result = verify_cal_modification(cal_file, callback)

            # 括号不匹配应该失败
            assert result is False


class TestBackupAndRestore:
    """测试备份和恢复"""

    @pytest.fixture
    def log_callback(self):
        messages = []
        def callback(msg):
            messages.append(msg)
        return callback, messages

    def test_restore_on_failure(self, log_callback):
        """测试修改失败时恢复备份"""
        callback, messages = log_callback

        original_content = "#include \"header.h\"\n\nint cal = 0;"

        with tempfile.TemporaryDirectory() as temp_dir:
            cal_file = Path(temp_dir) / "Cal.c"
            cal_file.write_text(original_content, encoding="utf-8")

            # 创建备份
            from utils.file_ops import backup_file
            backup_file = backup_file(cal_file)
            assert backup_file.exists()

            # 修改文件
            cal_file.write_text("#include \"header.h\"\n#define ASW_ATECH_START_SEC_CALIB\nint cal = 0;", encoding="utf-8")

            # 验证文件已被修改
            modified_content = cal_file.read_text(encoding="utf-8")
            assert "ASW_ATECH_START_SEC_CALIB" in modified_content

            # 模拟恢复
            from utils.file_ops import restore_from_backup
            restore_result = restore_from_backup(cal_file, backup_file)

            assert restore_result is True

            # 验证内容已恢复
            restored_content = cal_file.read_text(encoding="utf-8")
            assert restored_content == original_content
            assert "ASW_ATECH_START_SEC_CALIB" not in restored_content
