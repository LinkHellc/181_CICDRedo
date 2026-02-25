# Story 2.9: 更新 A2L 文件变量地址

Status: done

> ⚠️ **变更说明 (2026-02-25)：** 改用纯 Python 实现，移除 MATLAB Engine 依赖。
> 基于原有 MATLAB 脚本逻辑转换，使用 pyelftools 解析 ELF 文件。

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要系统自动更新 A2L 文件中的变量地址，
以便匹配新编译的 ELF 文件。

## Acceptance Criteria

**Given** IAR 编译成功生成 ELF 文件
**When** 系统进入 A2L 更新阶段
**Then** 系统使用 Python 解析 ELF 文件提取符号地址（使用 pyelftools）
**And** 系统解析 A2L 文件结构
**And** 系统更新 A2L 文件中的变量地址为 ELF 文件中的对应地址
**And** 系统验证 A2L 文件已更新
**And** 系统在日志中记录更新的变量数量
**And** 如果更新失败，系统报告错误并继续

## Tasks / Subtasks

- [x] 任务 1: 创建 A2L 处理模块结构 (AC: When - 系统进入 A2L 更新阶段)
  - [x] 1.1 创建 `src/a2l/` 目录结构
  - [x] 1.2 创建 `src/a2l/__init__.py`
  - [x] 1.3 创建 `src/a2l/elf_parser.py` - ELF 解析模块
  - [x] 1.4 创建 `src/a2l/a2l_parser.py` - A2L 解析模块
  - [x] 1.5 创建 `src/a2l/address_updater.py` - 地址更新模块
  - [x] 1.6 添加 pyelftools 依赖到 requirements.txt

- [x] 任务 2: 实现 ELF 文件解析 (AC: Then - 系统使用 Python 解析 ELF 文件)
  - [x] 2.1 实现 `ELFParser` 类
  - [x] 2.2 使用 pyelftools 打开 ELF 文件
  - [x] 2.3 提取符号表（.symtab section）
  - [x] 2.4 提取符号名称和地址映射
  - [x] 2.5 过滤出 A2L 需要的变量符号
  - [x] 2.6 返回符号地址字典 {symbol_name: address}

- [x] 任务 3: 实现 A2L 文件解析 (AC: Then - 系统解析 A2L 文件结构)
  - [x] 3.1 实现 `A2LParser` 类
  - [x] 3.2 解析 A2L 文件基本结构
  - [x] 3.3 提取 CHARACTERISTIC 和 MEASUREMENT 块
  - [x] 3.4 识别变量名称和当前地址
  - [x] 3.5 支持大文件流式解析（避免内存溢出）

- [x] 任务 4: 实现地址更新逻辑 (AC: Then - 系统更新 A2L 文件中的变量地址)
  - [x] 4.1 实现 `A2LAddressUpdater` 类
  - [x] 4.2 加载 ELF 符号表
  - [x] 4.3 匹配 A2L 变量名与 ELF 符号名
  - [x] 4.4 更新 A2L 文件中的地址值
  - [x] 4.5 处理未匹配的变量（记录日志）
  - [x] 4.6 保存更新后的 A2L 文件

- [x] 任务 5: 创建 A2L 更新阶段模块 (AC: When - 系统进入 A2L 更新阶段)
  - [x] 5.1 创建 `src/stages/a2l_process.py` 文件
  - [x] 5.2 定义 `A2LProcessConfig` dataclass
  - [x] 5.3 实现 `execute_stage()` 函数（统一接口）
  - [x] 5.4 整合 ELF 解析、A2L 解析、地址更新流程
  - [x] 5.5 返回 StageResult（成功或失败）

- [x] 任务 6: 实现错误处理和恢复 (AC: Then - 如果更新失败，系统报告错误并继续)
  - [x] 6.1 捕获 ELF 解析异常
  - [x] 6.2 捕获 A2L 解析异常
  - [x] 6.3 使用 ProcessError 及子类报告错误
  - [x] 6.4 提供可操作的修复建议
  - [x] 6.5 记录详细错误日志

- [x] 任务 7: 实现日志记录和进度反馈 (AC: And - 系统在日志中记录更新的变量数量)
  - [x] 7.1 记录 ELF 解析进度
  - [x] 7.2 记录 A2L 解析进度
  - [x] 7.3 记录变量匹配和更新数量
  - [x] 7.4 记录未匹配变量列表
  - [x] 7.5 记录阶段执行时长

- [x] 任务 8: 集成到工作流 (AC: When - 系统进入 A2L 更新阶段)
  - [x] 8.1 在 `src/core/workflow.py` 中添加 a2l_process 阶段
  - [x] 8.2 确保阶段顺序：iar_compile → a2l_process
  - [x] 8.3 测试工作流集成
  - [x] 8.4 验证阶段可以独立启用/禁用

- [x] 任务 9: 编写单元测试 (AC: Then - 系统验证 A2L 文件已更新)
  - [x] 9.1 测试 ELF 解析器
  - [x] 9.2 测试 A2L 解析器
  - [x] 9.3 测试地址更新逻辑
  - [x] 9.4 测试错误处理
  - [x] 9.5 测试日志回调

- [x] 任务 10: 编写集成测试 (AC: All)
  - [x] 10.1 测试完整 A2L 更新流程
  - [x] 10.2 使用真实 ELF 文件测试
  - [x] 10.3 使用真实 A2L 文件测试
  - [x] 10.4 测试边界情况（空文件、大文件）
  - [x] 10.5 测试错误场景（文件不存在、格式错误）

## Dev Notes

### ⚠️ 架构变更说明 (2026-02-25)

**原方案：** 使用 MATLAB Engine API 执行 `rtw.asap2SetAddress()`
**新方案：** 纯 Python 实现，使用 pyelftools 解析 ELF 文件

**变更原因：** PyInstaller 打包后 MATLAB Engine API 在目标机器无法正常工作

**相关文档：**
- Sprint 变更提案: `sprint-change-proposal-2026-02-25.md`
- 架构更新: `architecture.md` ADR-005

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **ADR-001（渐进式架构）**：MVP 使用函数式模块，PyQt6 类仅用于 UI 层
- **ADR-002（防御性编程）**：失败时提供可操作的恢复建议
- **ADR-003（可观测性）**：日志是架构基础，实时进度通过信号槽机制实现
- **ADR-004（混合架构模式）**：UI 层用 PyQt6 类，业务逻辑用函数
- **ADR-005（移除 MATLAB Engine 依赖）**：A2L 处理改用纯 Python 实现

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 阶段接口：使用统一的 `execute_stage(StageConfig, BuildContext) -> StageResult` 签名
2. ⭐⭐⭐⭐⭐ 错误处理：使用统一的错误类（`ProcessError` 及子类）
3. ⭐⭐⭐⭐⭐ 状态传递：使用 `BuildContext`，不使用全局变量
4. ⭐⭐⭐ 路径处理：使用 `pathlib.Path` 而非字符串
5. ⭐⭐⭐ 日志记录：使用 `logging` 模块，不使用 `print()`
6. ⭐⭐⭐ 阶段函数命名：必须命名为 `execute_stage`

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/a2l/__init__.py` | 新建 | A2L 模块初始化 |
| `src/a2l/elf_parser.py` | 新建 | ELF 文件解析器 |
| `src/a2l/a2l_parser.py` | 新建 | A2L 文件解析器 |
| `src/a2l/address_updater.py` | 新建 | 地址更新器 |
| `src/stages/a2l_process.py` | 修改 | A2L 更新阶段模块 |
| `src/core/workflow.py` | 修改 | 添加 a2l_process 阶段 |
| `requirements.txt` | 修改 | 添加 pyelftools 依赖 |
| `tests/unit/test_a2l/` | 新建 | 单元测试目录 |
| `tests/integration/test_a2l_integration.py` | 新建 | 集成测试 |

**确保符合项目结构**：
```
src/
├── a2l/                                      # A2L 处理模块（新建）
│   ├── __init__.py
│   ├── elf_parser.py                         # ELF 解析
│   ├── a2l_parser.py                         # A2L 解析
│   └── address_updater.py                    # 地址更新
├── stages/                                   # 工作流阶段
│   ├── base.py                              # 阶段接口定义
│   ├── a2l_process.py                       # A2L 更新阶段
│   └── ...
└── core/                                     # 核心业务逻辑
    ├── workflow.py                          # 工作流编排
    └── ...
tests/
├── unit/
│   └── test_a2l/                            # A2L 单元测试
└── integration/
    └── test_a2l_integration.py              # 集成测试
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| **pyelftools** | 0.31+ | ELF 文件解析 |
| dataclasses | 内置 (3.7+) | 数据模型 |
| pathlib | 内置 | 路径处理 |
| logging | 内置 | 日志记录 |
| re | 内置 | 正则表达式（A2L 解析） |

### ELF 解析规格

**使用 pyelftools 解析 ELF**：
```python
from elftools.elf.elffile import ELFFile

class ELFParser:
    """ELF 文件解析器"""

    def extract_symbols(self, elf_path: Path) -> dict[str, int]:
        """
        从 ELF 文件提取符号地址

        Args:
            elf_path: ELF 文件路径

        Returns:
            {symbol_name: address} 字典
        """
        symbols = {}

        with open(elf_path, 'rb') as f:
            elf = ELFFile(f)

            # 获取符号表
            symtab = elf.get_section_by_name('.symtab')
            if symtab:
                for symbol in symtab.iter_symbols():
                    name = symbol.name
                    addr = symbol['st_value']
                    if name and addr:
                        symbols[name] = addr

        return symbols
```

### A2L 解析规格

**A2L 文件结构**：
```
/begin CHARACTERISTIC
  name "VariableName"
  ...
  address 0x12345678
  ...
/end CHARACTERISTIC

/begin MEASUREMENT
  name "MeasurementName"
  ...
  address 0x87654321
  ...
/end MEASUREMENT
```

**解析逻辑**：
```python
import re

class A2LParser:
    """A2L 文件解析器"""

    # 匹配 CHARACTERISTIC 和 MEASUREMENT 块中的地址
    ADDRESS_PATTERN = re.compile(r'address\s+(0x[0-9A-Fa-f]+|\d+)')

    def extract_variables(self, a2l_path: Path) -> dict[str, int]:
        """
        从 A2L 文件提取变量名称和地址

        Args:
            a2l_path: A2L 文件路径

        Returns:
            {variable_name: current_address} 字典
        """
        variables = {}
        # ... 解析实现
        return variables
```

### 地址更新流程

```
工作流进入 A2L 更新阶段
    │
    ▼
1. 配置验证
    ├─→ ELF 文件存在？
    ├─→ A2L 文件存在？
    └─→ 输出目录存在？
    │
    ▼
2. 解析 ELF 文件
    ├─→ 使用 pyelftools 打开 ELF
    ├─→ 提取 .symtab 符号表
    └─→ 构建符号地址字典 {name: address}
    │
    ▼
3. 解析 A2L 文件
    ├─→ 读取 A2L 文件内容
    ├─→ 提取变量名和当前地址
    └─→ 记录需要更新的位置
    │
    ▼
4. 匹配和更新地址
    ├─→ 遍历 A2L 变量
    ├─→ 查找 ELF 符号表中对应地址
    ├─→ 替换 A2L 中的地址值
    └─→ 记录匹配/未匹配统计
    │
    ▼
5. 保存更新后的 A2L
    ├─→ 写入更新后的 A2L 文件
    └─→ 验证文件完整性
    │
    ▼
返回 StageResult
```

### 错误处理和恢复建议

| 错误类型 | 可能原因 | 修复建议 |
|---------|---------|---------|
| `ELFParseError` | ELF 文件格式错误或损坏 | - 检查 IAR 编译是否成功<br>- 验证 ELF 文件路径<br>- 使用 readelf 工具验证 |
| `A2LParseError` | A2L 文件格式错误 | - 检查 A2L 文件编码<br>- 验证 A2L 文件结构<br>- 使用文本编辑器检查 |
| `SymbolNotFoundError` | ELF 中找不到变量符号 | - 检查编译选项是否包含符号表<br>- 验证变量名称匹配规则 |
| `FileNotFoundError` | 文件不存在 | - 检查文件路径配置<br>- 验证前置阶段是否成功 |
| `PermissionError` | 文件权限不足 | - 检查目录权限<br>- 以管理员身份运行 |

### 测试场景

**单元测试场景**：
```python
def test_elf_parser_extract_symbols():
    """测试 ELF 符号提取"""
    parser = ELFParser()
    symbols = parser.extract_symbols(test_elf_path)

    assert len(symbols) > 0
    assert "expected_symbol_name" in symbols

def test_a2l_parser_extract_variables():
    """测试 A2L 变量提取"""
    parser = A2LParser()
    variables = parser.extract_variables(test_a2l_path)

    assert len(variables) > 0

def test_address_updater():
    """测试地址更新"""
    updater = A2LAddressUpdater()
    result = updater.update_addresses(
        elf_symbols={"var1": 0x1234, "var2": 0x5678},
        a2l_content=test_a2l_content
    )

    assert result.matched_count > 0
    assert "0x1234" in result.updated_content
```

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 2 - Story 2.9](../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-017](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-005](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-02-25.md](../planning-artifacts/sprint-change-proposal-2026-02-25.md)
- [pyelftools 文档](https://github.com/eliben/pyelftools)
