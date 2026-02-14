# Story 2.9: 更新 A2L 文件变量地址

Status: todo

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要系统自动更新 A2L 文件中的变量地址，
以便匹配新编译的 ELF 文件。

## Acceptance Criteria

**Given** IAR 编译成功生成 ELF 文件
**When** 系统进入 A2L 更新阶段
**Then** 系统通过 MATLAB Engine 执行命令：
  ```matlab
  rtw.asap2SetAddress('tmsAPP[_年_月_日_时_分].a2l', 'CYT4BF_M7_Master.elf')
  ```
**And** 系统捕获 MATLAB 命令执行结果
**And** 系统验证 A2L 文件已更新
**And** 如果更新失败，系统报告错误并继续

## Tasks / Subtasks

- [ ] 任务 1: 创建 A2L 更新阶段模块 (AC: When - 系统进入 A2L 更新阶段)
  - [ ] 1.1 创建 `src/stages/a2l_process.py` 文件
  - [ ] 1.2 定义 `A2LProcessConfig` dataclass（继承 StageConfig）
  - [ ] 1.3 添加 A2L 文件路径配置字段
  - [ ] 1.4 添加 ELF 文件路径配置字段
  - [ ] 1.5 添加超时配置字段（默认 600 秒）

- [ ] 任务 2: 实现 MATLAB 命令生成 (AC: Then - 通过 MATLAB Engine 执行命令)
  - [ ] 2.1 创建 `_generate_a2l_update_command()` 辅助函数
  - [ ] 2.2 从 BuildContext 获取时间戳信息
  - [ ] 2.3 生成 A2L 文件名（tmsAPP[_年_月_日_时_分].a2l）
  - [ ] 2.4 生成 ELF 文件名（CYT4BF_M7_Master.elf）
  - [ ] 2.5 构建 MATLAB 命令字符串：`rtw.asap2SetAddress(a2l_file, elf_file)`

- [ ] 任务 3: 实现阶段执行主函数 (AC: Then - 系统通过 MATLAB Engine 执行命令)
  - [ ] 3.1 实现 `execute_stage()` 函数（统一接口）
  - [ ] 3.2 接受 StageConfig 和 BuildContext 参数
  - [ ] 3.3 使用 MATLAB Engine API 执行命令
  - [ ] 3.4 捕获 MATLAB 执行结果
  - [ ] 3.5 返回 StageResult（成功或失败）

- [ ] 任务 4: 实现 MATLAB 集成 (AC: Then - 系统捕获 MATLAB 命令执行结果)
  - [ ] 4.1 在 `src/integrations/matlab.py` 中添加 `execute_command()` 方法
  - [ ] 4.2 接受 MATLAB 命令字符串和超时参数
  - [ ] 4.3 使用 `matlab.engine` 执行命令
  - [ ] 4.4 捕获命令输出和错误信息
  - [ ] 4.5 使用 `time.monotonic()` 实现超时检测（架构 Decision 2.1）
  - [ ] 4.6 返回执行结果（成功/失败、输出、错误）

- [ ] 任务 5: 实现 A2L 文件验证 (AC: Then - 系统验证 A2L 文件已更新)
  - [ ] 5.1 创建 `_verify_a2l_updated()` 辅助函数
  - [ ] 5.2 检查 A2L 文件是否存在
  - [ ] 5.3 验证 A2L 文件大小是否合理（非零）
  - [ ] 5.4 可选：解析 A2L 文件验证变量地址格式
  - [ ] 5.5 返回验证结果（成功/失败）

- [ ] 任务 6: 实现错误处理和恢复 (AC: Then - 如果更新失败，系统报告错误并继续)
  - [ ] 6.1 捕获 MATLAB 执行异常
  - [ ] 6.2 使用 ProcessError 及子类报告错误（架构 Decision 2.2）
  - [ ] 6.3 提供可操作的修复建议
  - [ ] 6.4 记录详细错误日志（context.log_callback）
  - [ ] 6.5 返回 StageResult(status=FAILED, suggestions=[...])

- [ ] 任务 7: 添加超时和进程管理 (AC: Then - 系统捕获 MATLAB 命令执行结果)
  - [ ] 7.1 从 DEFAULT_TIMEOUT 获取 A2L 更新超时值
  - [ ] 7.2 实现超时检测（使用 time.monotonic）
  - [ ] 7.3 超时时抛出 ProcessTimeoutError
  - [ ] 7.4 使用进程管理器确保 MATLAB 进程清理
  - [ ] 7.5 使用 ensure_process_terminated() 强制终止进程

- [ ] 任务 8: 实现日志记录和进度反馈 (AC: And - 系统捕获 MATLAB 命令执行结果)
  - [ ] 8.1 使用 context.log_callback 记录 A2L 更新开始日志
  - [ ] 8.2 实时记录 MATLAB 命令输出
  - [ ] 8.3 记录 A2L 文件验证结果
  - [ ] 8.4 记录阶段执行时长
  - [ ] 8.5 发送进度更新信号（如适用）

- [ ] 任务 9: 集成到工作流 (AC: When - 系统进入 A2L 更新阶段)
  - [ ] 9.1 在 `src/core/workflow.py` 的 WORKFLOW_STAGES 中添加 a2l_process 阶段
  - [ ] 9.2 确保阶段顺序：iar_compile → a2l_process
  - [ ] 9.3 测试工作流集成
  - [ ] 9.4 验证阶段可以独立启用/禁用

- [ ] 任务 10: 编写单元测试 (AC: Then - 系统验证 A2L 文件已更新)
  - [ ] 10.1 测试 MATLAB 命令生成
  - [ ] 10.2 测试 A2L 文件验证逻辑
  - [ ] 10.3 测试超时处理
  - [ ] 10.4 测试错误处理和恢复建议
  - [ ] 10.5 测试日志回调调用

- [ ] 任务 11: 编写集成测试 (AC: Then - 系统通过 MATLAB Engine 执行命令)
  - [ ] 11.1 测试 A2L 更新阶段的完整执行流程
  - [ ] 11.2 测试与 MATLAB 的真实集成（如环境允许）
  - [ ] 11.3 测试 ELF 文件存在性检查
  - [ ] 11.4 测试 A2L 文件生成和更新
  - [ ] 11.5 测试错误场景（MATLAB 未安装、文件不存在）

- [ ] 任务 12: 添加配置验证 (AC: Given - IAR 编译成功生成 ELF 文件)
  - [ ] 12.1 验证 ELF 文件路径存在
  - [ ] 12.2 验证 ELF 文件有效（非零大小）
  - [ ] 12.3 验证 A2L 输出目录存在
  - [ ] 12.4 如果验证失败，返回 StageResult(FAILED) 并提供修复建议
  - [ ] 12.5 记录验证结果到日志

## Dev Notes

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **ADR-001（渐进式架构）**：MVP 使用函数式模块，PyQt6 类仅用于 UI 层
- **ADR-002（防御性编程）**：所有外部进程调用设置超时，失败时提供可操作的恢复建议
- **ADR-003（可观测性）**：日志是架构基础，实时进度通过信号槽机制实现
- **ADR-004（混合架构模式）**：UI 层用 PyQt6 类，业务逻辑用函数
- **Decision 1.2（数据模型）**：使用 dataclass，所有字段提供默认值
- **Decision 2.1（MATLAB 进程管理）**：每次启动/关闭，超时检测，僵尸进程清理
- **Decision 2.2（进程管理器架构）**：独立的进程管理器模块，统一错误类
- **Decision 5.1（日志框架）**：logging + 自定义 PyQt6 Handler

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 阶段接口：使用统一的 `execute_stage(StageConfig, BuildContext) -> StageResult` 签名
2. ⭐⭐⭐⭐⭐ 超时检测：使用 `time.monotonic()` 而非 `time.time()`
3. ⭐⭐⭐⭐⭐ 错误处理：使用统一的错误类（`ProcessError` 及子类）
4. ⭐⭐⭐⭐⭐ 状态传递：使用 `BuildContext`，不使用全局变量
5. ⭐⭐⭐⭐⶿ 超时配置：从 `DEFAULT_TIMEOUT` 字典获取，不硬编码
6. ⭐⭐⭐ 路径处理：使用 `pathlib.Path` 而非字符串
7. ⭐⭐⭐ 日志记录：使用 `logging` 模块，不使用 `print()`
8. ⭐⭐⭐ 阶段函数命名：必须命名为 `execute_stage`

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/stages/a2l_process.py` | 新建 | A2L 更新阶段模块 |
| `src/integrations/matlab.py` | 修改 | 添加 execute_command() 方法 |
| `src/core/workflow.py` | 修改 | 添加 a2l_process 阶段到工作流 |
| `tests/unit/test_a2l_process.py` | 新建 | A2L 更新阶段单元测试 |
| `tests/integration/test_a2l_integration.py` | 新建 | A2L 更新集成测试 |

**确保符合项目结构**：
```
src/
├── stages/                                   # 工作流阶段（函数模块）
│   ├── base.py                              # 阶段接口定义
│   ├── a2l_process.py                       # A2L 更新阶段（新建）
│   └── ...
├── integrations/                             # 外部工具集成
│   └── matlab.py                            # MATLAB Engine API（需修改）
└── core/                                     # 核心业务逻辑
    ├── workflow.py                          # 工作流编排（需修改）
    └── ...
tests/
├── unit/
│   └── test_a2l_process.py                  # 单元测试（新建）
└── integration/
    └── test_a2l_integration.py              # 集成测试（新建）
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| MATLAB Engine API | latest | 与 MATLAB 交互 |
| dataclasses | 内置 (3.7+) | 数据模型 |
| pathlib | 内置 | 路径处理 |
| logging | 内置 | 日志记录 |
| time | 内置 | 时间测量（使用 monotonic） |
| matlab.engine | - | MATLAB Engine API |

### 测试标准

**单元测试要求**：
- 测试 MATLAB 命令生成逻辑（_generate_a2l_update_command）
- 测试 A2L 文件验证逻辑（_verify_a2l_updated）
- 测试超时处理（ProcessTimeoutError）
- 测试错误处理和恢复建议
- 测试配置验证逻辑
- 测试日志回调调用

**集成测试要求**：
- 测试 A2L 更新阶段的完整执行流程
- 测试与 MATLAB 的真实集成（需要 MATLAB 环境）
- 测试 ELF 文件存在性检查
- 测试 A2L 文件生成和更新
- 测试错误场景（MATLAB 未安装、文件不存在）

**端到端测试要求**：
- 测试从 IAR 编译到 A2L 更新的完整流程
- 测试工作流中的阶段顺序（iar_compile → a2l_process）
- 测试 A2L 更新失败对后续阶段的影响

### 依赖关系

**前置故事**：
- ✅ Story 2.4: 启动自动化构建流程（工作流编排、线程管理）
- ✅ Story 2.5: 执行 MATLAB 代码生成阶段（MATLAB Engine 集成基础）
- ✅ Story 2.8: 调用 IAR 命令行编译（生成 ELF 文件）
- ✅ Story 2.11: 创建时间戳目标文件夹（时间戳格式定义）

**后续故事**：
- Story 2.10: 替换 A2L 文件 XCP 头文件内容
- Story 2.12: 移动 HEX 和 A2L 文件到目标文件夹

### 数据流设计

```
工作流进入 A2L 更新阶段
    │
    ▼
创建 A2LProcessConfig
    │
    ├─→ A2L 文件路径
    ├─→ ELF 文件路径
    └─→ 超时配置（600秒）
    │
    ▼
配置验证（任务 12）
    │
    ├─→ ELF 文件存在？
    │   ├─→ 否 → 返回 StageResult(FAILED, suggestions=[])
    │   └─→ 是 → 继续
    │
    ├─→ A2L 输出目录存在？
    │   ├─→ 否 → 返回 StageResult(FAILED, suggestions=[])
    │   └─→ 是 → 继续
    │
    ▼
生成 MATLAB 命令（任务 2）
    │
    ├─→ 获取时间戳（从 BuildContext.state）
    ├─→ 生成 A2L 文件名：tmsAPP[_年_月_日_时_分].a2l
    ├─→ 生成 ELF 文件名：CYT4BF_M7_Master.elf
    └─→ 构建命令：rtw.asap2SetAddress(a2l_file, elf_file)
    │
    ▼
执行 MATLAB 命令（任务 3, 4）
    │
    ├─→ 调用 matlab.engine.execute_command()
    ├─→ 记录开始时间（time.monotonic）
    ├─→ 实时捕获输出
    ├─→ 检查超时（超时 → ProcessTimeoutError）
    ├─→ 等待命令完成
    └─→ 捕获执行结果
    │
    ├─→ 成功？
    │   ├─→ 是 → 继续
    │   └─→ 否 → 返回 StageResult(FAILED, error=..., suggestions=[])
    │
    ▼
验证 A2L 文件（任务 5）
    │
    ├─→ A2L 文件存在？
    │   ├─→ 否 → 返回 StageResult(FAILED, suggestions=[])
    │   └─→ 是 → 继续
    │
    ├─→ 文件大小合理（非零）？
    │   ├─→ 否 → 返回 StageResult(FAILED, suggestions=[])
    │   └─→ 是 → 继续
    │
    ├─→ 可选：解析 A2L 文件验证变量地址
    │
    ▼
返回 StageResult
    │
    ├─→ status: COMPLETED（成功）
    │   ├─→ message: "A2L 文件变量地址更新成功"
    │   ├─→ output_files: [a2l_file_path]
    │   └─→ suggestions: []
    │
    └─→ status: FAILED（失败）
        ├─→ message: "A2L 文件更新失败：..."
        ├─→ error: ProcessError 或其子类
        └─→ suggestions: ["检查 MATLAB 安装", "验证 ELF 文件路径", ...]
```

### 数据模型规格

**A2LProcessConfig**：
```python
@dataclass
class A2LProcessConfig(StageConfig):
    """A2L 更新阶段配置"""
    a2l_path: str = ""                  # A2L 文件路径
    elf_path: str = ""                   # ELF 文件路径
    timestamp_format: str = "_%Y_%m_%d_%H_%M"  # 时间戳格式
    timeout: int = 600                  # 超时时间（秒）
```

**StageResult（通用）**：
```python
@dataclass
class StageResult:
    """阶段执行结果"""
    status: StageStatus                 # PENDING, RUNNING, COMPLETED, FAILED
    message: str                        # 执行消息
    output_files: list[str] = field(default_factory=list)  # 输出文件列表
    error: Exception = None             # 错误对象
    suggestions: list[str] = field(default_factory=list)    # 修复建议
```

### MATLAB 命令生成规格

**命令生成逻辑**：
```python
def _generate_a2l_update_command(context: BuildContext, config: A2LProcessConfig) -> tuple[str, str, str]:
    """
    生成 A2L 更新 MATLAB 命令

    Args:
        context: 构建上下文
        config: A2L 更新配置

    Returns:
        (a2l_file, elf_file, matlab_command)
    """
    # 从 BuildContext.state 获取时间戳
    timestamp = context.state.get("build_timestamp", "")
    
    # 生成 A2L 文件名
    a2l_file = f"tmsAPP{timestamp}.a2l"
    
    # 生成 ELF 文件名
    elf_file = "CYT4BF_M7_Master.elf"
    
    # 构建 MATLAB 命令
    matlab_command = f"rtw.asap2SetAddress('{a2l_file}', '{elf_file}')"
    
    return a2l_file, elf_file, matlab_command
```

**时间戳格式示例**：
```
输入时间戳：_2025_02_14_10_30
生成的 A2L 文件名：tmsAPP_2025_02_14_10_30.a2l
```

### MATLAB 集成规格

**MATLAB 命令执行**：
```python
# src/integrations/matlab.py

class MATLABIntegration:
    def execute_command(
        self,
        command: str,
        timeout: int = 600,
        log_callback: callable = None
    ) -> ProcessResult:
        """
        执行 MATLAB 命令

        Args:
            command: MATLAB 命令字符串
            timeout: 超时时间（秒）
            log_callback: 日志回调函数

        Returns:
            ProcessResult: 执行结果
        """
        import matlab.engine
        import time
        from utils.errors import ProcessTimeoutError
        
        start = time.monotonic()
        
        try:
            # 启动 MATLAB Engine（或连接到现有）
            eng = matlab.engine.start_matlab()
            
            try:
                # 执行命令
                log_callback(f"执行 MATLAB 命令: {command}")
                result = eng.eval(command, nargout=0)
                
                # 记录输出
                log_callback("MATLAB 命令执行成功")
                
                return ProcessResult(success=True, output="")
                
            finally:
                # 确保 MATLAB 引擎关闭
                eng.quit()
                
        except ProcessTimeoutError:
            # 超时处理
            log_callback(f"MATLAB 命令执行超时（>{timeout}秒）")
            raise ProcessTimeoutError("MATLAB", timeout)
            
        except Exception as e:
            # 其他错误
            log_callback(f"MATLAB 执行失败: {str(e)}")
            return ProcessResult(success=False, error=str(e))
```

### A2L 文件验证规格

**A2L 文件验证逻辑**：
```python
def _verify_a2l_updated(a2l_path: Path, log_callback: callable) -> tuple[bool, str]:
    """
    验证 A2L 文件已更新

    Args:
        a2l_path: A2L 文件路径
        log_callback: 日志回调函数

    Returns:
        (success, message)
    """
    # 检查文件是否存在
    if not a2l_path.exists():
        return False, f"A2L 文件不存在: {a2l_path}"
    
    # 检查文件大小
    file_size = a2l_path.stat().st_size
    if file_size == 0:
        return False, f"A2L 文件大小为 0: {a2l_path}"
    
    log_callback(f"A2L 文件验证成功: {a2l_path} ({file_size} bytes)")
    
    return True, "A2L 文件验证成功"
```

### 错误处理和恢复建议

**常见错误场景和建议**：

| 错误类型 | 可能原因 | 修复建议 |
|---------|---------|---------|
| `ProcessTimeoutError` | MATLAB 命令执行超时 | - 检查 A2L 文件大小是否过大<br>- 检查 ELF 文件是否有效<br>- 尝试增加超时时间 |
| `FileNotFoundError` | ELF 文件不存在 | - 检查 IAR 编译阶段是否成功<br>- 验证 ELF 文件路径配置<br>- 重新执行 IAR 编译 |
| `matlab.engine.MatlabExecutionError` | MATLAB 命令执行失败 | - 检查 MATLAB 安装和版本<br>- 验证 rtw.asap2SetAddress 函数可用<br>- 查看 MATLAB 详细错误日志 |
| `PermissionError` | 文件权限不足 | - 检查 A2L 输出目录权限<br>- 以管理员身份运行<br>- 修改文件权限 |
| `ValueError` | A2L 文件格式错误 | - 检查 A2L 文件原始内容<br>- 验证时间戳格式<br>- 手动检查 A2L 文件结构 |

### 超时配置

**超时值选择**：
```python
# src/core/constants.py

DEFAULT_TIMEOUT = {
    "matlab": 1800,      # 30 分钟 - MATLAB 代码生成
    "iar": 1200,         # 20 分钟 - IAR 编译
    "file_ops": 300,     # 5 分钟 - 文件操作
    "a2l": 600,          # 10 分钟 - A2L 处理（本阶段）
    "stage_default": 3600, # 1 小时 - 默认阶段超时
}
```

**超时检测实现**：
```python
def execute_with_timeout(command: str, timeout: int, log_callback: callable):
    """执行 MATLAB 命令并检测超时"""
    import time
    from utils.errors import ProcessTimeoutError
    
    start = time.monotonic()  # ← 必须使用 monotonic
    
    while True:
        # 检查超时
        if time.monotonic() - start > timeout:
            raise ProcessTimeoutError("MATLAB", timeout)
        
        # 执行命令
        # ...
        
        time.sleep(0.1)
```

### 日志记录示例

**A2L 更新阶段日志**：
```
[10:45:20] INFO: 开始 A2L 更新阶段
[10:45:20] INFO: 验证 ELF 文件: E:\Projects\TMS_APP\CYT4BF_M7_Master.elf
[10:45:20] INFO: ELF 文件验证成功 (1,234,567 bytes)
[10:45:20] INFO: 生成 MATLAB 命令: rtw.asap2SetAddress('tmsAPP_2025_02_14_10_45.a2l', 'CYT4BF_M7_Master.elf')
[10:45:21] INFO: 执行 MATLAB 命令...
[10:45:35] INFO: MATLAB 命令执行成功
[10:45:35] INFO: 验证 A2L 文件: E:\Projects\TMS_APP\tmsAPP_2025_02_14_10_45.a2l
[10:45:35] INFO: A2L 文件验证成功 (567,890 bytes)
[10:45:35] INFO: A2L 更新阶段完成，耗时 15.2 秒
```

**错误日志示例**：
```
[10:45:20] INFO: 开始 A2L 更新阶段
[10:45:20] ERROR: ELF 文件不存在: E:\Projects\TMS_APP\CYT4BF_M7_Master.elf
[10:45:20] ERROR: A2L 更新阶段失败
[10:45:20] INFO: 建议操作:
[10:45:20] INFO:   - 检查 IAR 编译阶段是否成功
[10:45:20] INFO:   - 验证 ELF 文件路径配置
[10:45:20] INFO:   - 重新执行 IAR 编译
```

### 工作流集成

**工作流阶段定义**：
```python
# src/core/workflow.py

# 工作流定义：阶段名称 + 执行函数
WORKFLOW_STAGES = [
    ("matlab_gen", stages.matlab_gen.execute_stage),
    ("file_process", stages.file_process.execute_stage),
    ("iar_compile", stages.iar_compile.execute_stage),
    ("a2l_process", stages.a2l_process.execute_stage),    # ← 新增
    ("package", stages.package.execute_stage),
]
```

**阶段顺序验证**：
- IAR 编译（iar_compile）必须先于 A2L 更新（a2l_process）
- A2L 更新（a2l_process）可以独立启用/禁用
- A2L 更新（a2l_process）失败时，工作流停止（不执行后续阶段）

### 测试场景

**单元测试场景**：
```python
# tests/unit/test_a2l_process.py

def test_generate_a2l_update_command():
    """测试 MATLAB 命令生成"""
    # Given: 构建上下文包含时间戳
    context = BuildContext()
    context.state["build_timestamp"] = "_2025_02_14_10_30"
    
    # When: 生成命令
    a2l_file, elf_file, command = _generate_a2l_update_command(context, config)
    
    # Then: 验证命令格式
    assert a2l_file == "tmsAPP_2025_02_14_10_30.a2l"
    assert elf_file == "CYT4BF_M7_Master.elf"
    assert "rtw.asap2SetAddress" in command

def test_verify_a2l_updated():
    """测试 A2L 文件验证"""
    # Given: 有效的 A2L 文件
    a2l_path = create_test_a2l_file("test.a2l")
    
    # When: 验证文件
    success, message = _verify_a2l_updated(a2l_path, log_callback)
    
    # Then: 验证成功
    assert success is True
    assert "验证成功" in message

def test_timeout_handling():
    """测试超时处理"""
    # Given: 配置较短的超时时间
    config = A2LProcessConfig(timeout=1)
    
    # When: 执行超时命令
    result = execute_stage(config, context)
    
    # Then: 验证超时错误
    assert result.status == StageStatus.FAILED
    assert isinstance(result.error, ProcessTimeoutError)
```

**集成测试场景**：
```python
# tests/integration/test_a2l_integration.py

def test_full_a2l_process():
    """测试完整的 A2L 更新流程"""
    # Given: 有效的 ELF 文件和配置
    elf_path = Path("test/CYT4BF_M7_Master.elf")
    config = A2LProcessConfig(elf_path=str(elf_path))
    context = BuildContext()
    
    # When: 执行 A2L 更新阶段
    result = execute_stage(config, context)
    
    # Then: 验证成功
    assert result.status == StageStatus.COMPLETED
    assert len(result.output_files) > 0
    assert Path(result.output_files[0]).exists()

def test_matlab_integration():
    """测试 MATLAB 集成（需要真实环境）"""
    # Given: MATLAB 环境
    matlab = MATLABIntegration()
    
    # When: 执行简单命令
    result = matlab.execute_command("1+1", timeout=10)
    
    # Then: 验证成功
    assert result.success is True
```

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 2 - Story 2.9](../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-017](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 2.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 2.2](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-001](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-002](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-003](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-004](../planning-artifacts/architecture.md)

## Dev Agent Record

### Agent Model Used

zai/glm-4.7 (运行: agent=main | host=Amlia | repo=C:\Users\11245\.openclaw\workspace)

### Debug Log References

- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Story File: `_bmad-output/implementation-artifacts/stories/2-9-update-a2l-file-variable-addresses.md`
- Epics Source: `_bmad-output/planning-artifacts/epics.md` (Lines 427-447)
- Architecture Source: `_bmad-output/planning-artifacts/architecture.md` (Lines 481-575, 856-900, 1851-1925)

### Completion Notes List

### File List

**创建的文件：**

**修改的文件：**

**测试结果：**
- 总测试数：0
- 通过：0
- 失败：0
- 测试覆盖率：0%

**完成的任务清单：**
- [ ] 任务 1: 创建 A2L 更新阶段模块
- [ ] 任务 2: 实现 MATLAB 命令生成
- [ ] 任务 3: 实现阶段执行主函数
- [ ] 任务 4: 实现 MATLAB 集成
- [ ] 任务 5: 实现 A2L 文件验证
- [ ] 任务 6: 实现错误处理和恢复
- [ ] 任务 7: 添加超时和进程管理
- [ ] 任务 8: 实现日志记录和进度反馈
- [ ] 任务 9: 集成到工作流
- [ ] 任务 10: 编写单元测试
- [ ] 任务 11: 编写集成测试
- [ ] 任务 12: 添加配置验证
