# Story 2.5: 执行 MATLAB 代码生成阶段

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要系统自动调用 MATLAB 生成代码，
以便替代手动运行 Simulink 编译。

## Acceptance Criteria

**Given** 构建流程已启动且进入 MATLAB 代码生成阶段
**When** 系统执行代码生成
**Then** 系统启动 MATLAB 进程（使用 MATLAB Engine API）
**And** 系统调用 `genCode.m` 脚本
**And** 系统捕获 MATLAB 输出并实时显示在日志窗口
**And** 系统监控进程状态（运行中/完成/失败）
**And** 系统记录阶段开始和结束时间
**And** 如果代码生成失败，系统停止构建并报告错误

## Tasks / Subtasks

- [x] 任务 1: 创建 MATLAB 集成模块 (AC: Then - 启动 MATLAB 进程)
  - [x] 1.1 创建 `src/integrations/matlab.py`
  - [x] 1.2 实现 `MatlabIntegration` 类
  - [x] 1.3 使用 MATLAB Engine API for Python (`import matlab.engine`)
  - [x] 1.4 实现进程启动方法 `start_engine()`
  - [x] 1.5 设置 MATLAB 进程参数（内存限制、等待时间）
  - [x] 1.6 添加版本兼容性检查（R2020a+）

- [x] 任务 2: 实现 genCode.m 脚本调用 (AC: Then - 调用 genCode.m 脚本)
  - [x] 2.1 在 `src/stages/matlab_gen.py` 创建阶段执行函数
  - [x] 2.2 实现 `execute_stage(config: StageConfig, context: BuildContext) -> StageResult`
  - [x] 2.3 添加 `genCode.m` 脚本路径参数（从配置获取）
  - [x] 2.4 使用 `matlab.engine.eval()` 或 `run()` 调用脚本
  - [x] 2.5 传递 Simulink 工程路径作为参数
  - [x] 2.6 指定代码生成输出目录（`./20_Code`）

- [x] 任务 3: 实现 MATLAB 输出捕获 (AC: Then - 捕获 MATLAB 输出并实时显示)
  - [x] 3.1 设置 MATLAB 输出重定向
  - [x] 3.2 创建输出回调函数，通过信号发送到 UI
  - [x] 3.3 实时追加输出到日志窗口（使用 `log_callback`）
  - [x] 3.4 添加时间戳到每条输出（使用 `[HH:MM:SS]` 格式）
  - [x] 3.5 处理 MATLAB 标准输出和标准错误

- [x] 任务 4: 实现进程状态监控 (AC: Then - 监控进程状态)
  - [x] 4.1 实现 `is_running()` 方法检查 MATLAB 进程状态
  - [x] 4.2 使用 `matlab.engine.future` 异步执行模式
  - [x] 4.3 定期轮询进程状态（每 0.5 秒）
  - [x] 4.4 检测进程完成（`future.done()`）
  - [x] 4.5 检测进程异常（捕获异常）

- [x] 任务 5: 实现超时检测和错误处理 (AC: And - 如果代码生成失败，停止构建并报告错误)
  - [x] 5.1 设置阶段超时（使用 `DEFAULT_TIMEOUT["matlab"]` = 1800 秒）
  - [x] 5.2 使用 `time.monotonic()` 实现超时检测（架构 Decision 2.1）
  - [x] 5.3 超时时调用进程管理器终止 MATLAB 进程
  - [x] 5.4 检查 MATLAB 退出码/异常状态
  - [x] 5.5 返回 `StageResult` 并包含可操作的修复建议

- [x] 任务 6: 实现阶段时间记录 (AC: And - 记录阶段开始和结束时间)
  - [x] 6.1 在阶段开始时记录 `start_time`（`time.monotonic()`）
  - [x] 6.2 在阶段结束时记录 `end_time`
  - [x] 6.3 计算 `duration = end_time - start_time`
  - [x] 6.4 将时间信息保存到 `StageExecution` 数据模型
  - [x] 6.5 通过信号发送阶段完成时间和时长到 UI

- [x] 任务 7: 实现输出文件验证 (AC: Then - 代码生成成功)
  - [x] 7.1 验证代码生成输出目录存在（`./20_Code`）
  - [x] 7.2 检查生成的 `.c` 和 `.h` 文件数量
  - [x] 7.3 验证关键文件存在（至少有代码文件）
  - [x] 7.4 将输出文件列表保存到 `BuildContext.state["matlab_output"]`
  - [x] 7.5 如果验证失败，返回 `StageResult(FAILED)` 并提示

- [x] 任务 8: 集成到工作流引擎 (AC: Given - 构建流程已启动)
  - [x] 8.1 在 `src/core/workflow.py` 的 `STAGE_EXECUTORS` 中注册 `matlab_gen`
  - [x] 8.2 指向 `stages.matlab_gen.execute_stage`
  - [x] 8.3 确保阶段按工作流顺序执行（阶段 1）
  - [x] 8.4 将阶段输出传递给下一阶段（文件处理阶段）

## Dev Notes

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **ADR-002（防御性编程）**：所有外部进程调用设置超时，失败后资源清理
- **Decision 2.1（MATLAB 进程管理策略）**：每次启动/关闭，超时检测，僵尸进程清理
- **Decision 2.2（进程管理器架构）**：使用 `ProcessManager` 统一管理，`ProcessError` 错误类
- **Decision 3.1（PyQt6 线程）**：QThread + QueuedConnection，跨线程信号安全
- **Decision 5.1（日志框架）**：logging + QtSignalHandler，实时输出到 UI

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 超时检测：使用 `time.monotonic()` 而非 `time.time()`
2. ⭐⭐⭐⭐⭐ 错误处理：使用 `ProcessError` 及子类（`ProcessTimeoutError`, `ProcessExitCodeError`）
3. ⭐⭐⭐⭐⭐ 信号连接：跨线程信号必须使用 `Qt.ConnectionType.QueuedConnection`
4. ⭐⭐⭐⭐⭐ 阶段接口：使用统一签名 `execute_stage(config, context) -> result`
5. ⭐⭐⭐⭐ 超时配置：从 `DEFAULT_TIMEOUT["matlab"]` 获取（1800 秒）
6. ⭐⭐⭐⭐ 状态传递：使用 `BuildContext.state["matlab_output"]` 传递文件列表
7. ⭐⭐⭐ 路径处理：使用 `pathlib.Path` 处理 MATLAB 路径
8. ⭐⭐⭐ 日志记录：使用 `context.log_callback` 实时发送日志

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/integrations/matlab.py` | 新建 | MATLAB Engine API 集成 |
| `src/stages/matlab_gen.py` | 新建 | MATLAB 代码生成阶段 |
| `src/core/workflow.py` | 修改 | 注册 matlab_gen 执行器 |
| `src/utils/process_mgr.py` | 修改 | 添加 MATLAB 进程清理支持 |
| `tests/unit/test_matlab_integration.py` | 新建 | MATLAB 集成单元测试 |
| `tests/unit/test_matlab_gen_stage.py` | 新建 | MATLAB 生成阶段测试 |

**确保符合项目结构**：
```
src/
├── integrations/                              # 外部工具集成
│   └── matlab.py                              # MATLAB Engine API（新建）
├── stages/                                    # 工作流阶段
│   ├── base.py                                # 基类（已存在）
│   └── matlab_gen.py                          # MATLAB 生成阶段（新建）
├── core/                                      # 核心业务逻辑
│   ├── workflow.py                            # 工作流编排（修改）
│   └── constants.py                           # DEFAULT_TIMEOUT（已存在）
└── utils/                                     # 工具函数
    ├── process_mgr.py                         # 进程管理器（修改）
    └── errors.py                              # ProcessError（已存在）
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ (64位) | 开发语言 |
| MATLAB Engine API | R2020a+ | MATLAB 集成 |
| matlab.engine | 与 MATLAB 版本匹配 | Python-MATLAB 桥接 |
| PyQt6 | 最新稳定版 | 信号槽通信 |
| pathlib | 内置 | 路径处理 |
| logging | 内置 | 日志记录 |
| time | 内置 | 超时检测（使用 monotonic） |
| dataclasses | 内置 (3.7+) | 数据模型 |

**MATLAB Engine API 安装要求**：
- MATLAB 必须预装（用户环境）
- MATLAB Engine API for Python 已安装
- 安装命令（在 MATLAB 目录执行）：`python setup.py install`
- 版本兼容性：MATLAB R2020a 或更高版本

### 测试标准

**单元测试要求**：
- 测试 MATLAB 进程启动和关闭
- 测试 genCode.m 脚本调用（使用 mock）
- 测试超时检测逻辑
- 测试输出捕获和回调
- 测试错误处理和恢复建议
- 测试输出文件验证逻辑

**集成测试要求**：
- 测试 MATLAB 集成与工作流线程的交互
- 测试 MATLAB 输出实时显示到 UI
- 测试超时后进程清理
- 测试阶段失败后工作流停止

**端到端测试要求**（需要真实 MATLAB 环境）：
- 测试从工作流启动到 MATLAB 代码生成完成的完整流程
- 测试代码生成输出文件验证

### 依赖关系

**前置故事**：
- ✅ Story 2.4: 启动自动化构建流程（已创建工作流线程和阶段执行框架）
- ✅ Story 2.1: 选择预定义工作流模板（已配置工作流）
- ✅ Epic 1 全部完成（项目配置管理，包含 MATLAB 路径配置）

**后续故事**：
- Story 2.6: 提取并处理代码文件（使用 `BuildContext.state["matlab_output"]`）
- Story 2.7: 移动代码文件到指定目录

### 数据流设计

```
工作流线程启动
    │
    ▼
execute_stage("matlab_gen", config, context)
    │
    ├─→ 记录开始时间 (start_time = time.monotonic())
    │
    ├─→ 创建 MATLAB 集成 (MatlabIntegration())
    │
    ├─→ 启动 MATLAB 引擎 (start_engine())
    │   │
    │   ├─→ 成功 → 继续
    │   └─→ 失败 → 返回 StageResult(FAILED, suggestions=[...])
    │
    ├─→ 调用 genCode.m (eval_script("genCode", simulink_path))
    │   │
    │   ├─→ 实时捕获输出 → log_callback(output)
    │   │
    │   ├─→ 监控进程状态
    │   │   ├─→ 轮询 future.done()
    │   │   └─→ 检查超时 (time.monotonic() - start > timeout)
    │   │
    │   ├─→ 成功 → 继续
    │   └─→ 失败/超时 → 清理进程 → 返回 StageResult(FAILED)
    │
    ├─→ 验证输出文件
    │   │
    │   ├─→ 检查 ./20_Code 目录
    │   ├─→ 统计 .c 和 .h 文件
    │   │
    │   ├─→ 验证通过 → 保存文件列表到 context.state["matlab_output"]
    │   └─→ 验证失败 → 返回 StageResult(FAILED, suggestions=[...])
    │
    ├─→ 记录结束时间 (end_time = time.monotonic())
    │
    ├─→ 计算时长 (duration = end_time - start_time)
    │
    └─→ 返回 StageResult(COMPLETED, output_files=[...])
```

### MATLAB 集成规格

**MatlabIntegration 类接口**：
```python
from typing import Optional, Callable
import matlab.engine
import time
from pathlib import Path
from utils.errors import ProcessTimeoutError, ProcessExitCodeError
from core.constants import DEFAULT_TIMEOUT

class MatlabIntegration:
    """MATLAB Engine API 集成"""

    def __init__(self, log_callback: Callable[[str], None] = None):
        """初始化 MATLAB 集成

        Args:
            log_callback: 日志回调函数，用于实时输出
        """
        self.engine: Optional[matlab.engine.MatlabEngine] = None
        self.log_callback = log_callback or (lambda msg: None)
        self.timeout = DEFAULT_TIMEOUT["matlab"]  # 1800 秒

    def start_engine(self) -> bool:
        """启动 MATLAB 引擎

        Returns:
            bool: 成功返回 True，失败返回 False
        """
        try:
            self.engine = matlab.engine.start_matlab()
            self.log_callback("MATLAB 引擎已启动")
            return True
        except Exception as e:
            self.log_callback(f"MATLAB 启动失败: {e}")
            return False

    def eval_script(self, script_path: str, *args) -> bool:
        """执行 MATLAB 脚本

        Args:
            script_path: 脚本路径（如 "genCode"）
            *args: 脚本参数

        Returns:
            bool: 成功返回 True，失败返回 False
        """
        if not self.engine:
            raise RuntimeError("MATLAB 引擎未启动")

        start = time.monotonic()  # 使用 monotonic

        try:
            # 异步执行
            future = self.engine.eval(script_path, *args, async_=True)

            # 监控执行状态
            while not future.done():
                if time.monotonic() - start > self.timeout:
                    raise ProcessTimeoutError("MATLAB 代码生成", self.timeout)

                time.sleep(0.5)  # 轮询间隔

            # 获取结果
            result = future.result()
            return True

        except ProcessTimeoutError as e:
            self.log_callback(f"MATLAB 执行超时: {e}")
            raise
        except Exception as e:
            self.log_callback(f"MATLAB 执行失败: {e}")
            raise ProcessExitCodeError("MATLAB", -1)

    def stop_engine(self) -> None:
        """停止 MATLAB 引擎并清理资源"""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass  # 忽略退出错误
            finally:
                self.engine = None
            self.log_callback("MATLAB 引擎已关闭")
```

### genCode.m 脚本规格

**脚本路径**（来自用户配置）：
- 默认路径：`00_用户输入需求与材料/genCode.m`
- 通过配置传递：`context.config["gencode_script_path"]`

**脚本参数**：
- Simulink 工程路径
- 输出目录（`./20_Code`）
- 回溯级数（默认 1）

**调用示例**：
```python
# 在 matlab_gen.py 中调用
simulink_path = context.config.get("simulink_path")
output_dir = "./20_Code"

# 调用 genCode.m
matlab.eval_script(
    f"genCode('{simulink_path}', '{output_dir}')"
)
```

### 输出文件规格

**代码生成输出目录**：`./20_Code`

**期望的输出文件**：
- 多个 `.c` 源文件
- 多个 `.h` 头文件
- `Rte_TmsApp.h`（接口文件，需要在下一阶段排除）

**文件列表格式**：
```python
# 保存到 context.state["matlab_output"]
output_files = {
    "c_files": ["file1.c", "file2.c", ...],
    "h_files": ["file1.h", "file2.h", ...],
    "exclude": ["Rte_TmsApp.h"],  # 下一阶段需要排除的文件
    "base_dir": "./20_Code"
}
```

### 错误处理规格

**错误类型和修复建议**：

| 错误类型 | 错误消息 | 修复建议 |
|---------|---------|---------|
| MATLAB 未安装 | "未检测到 MATLAB 安装" | 1. 安装 MATLAB R2020a 或更高版本<br>2. 确保 MATLAB 路径正确配置 |
| MATLAB Engine API 缺失 | "MATLAB Engine API for Python 未安装" | 1. 在 MATLAB 目录执行 `python setup.py install`<br>2. 验证 `import matlab.engine` 可用 |
| 脚本不存在 | "genCode.m 脚本未找到" | 1. 检查配置中的脚本路径<br>2. 确保 genCode.m 在指定目录 |
| Simulink 工程路径错误 | "Simulink 工程路径无效" | 1. 验证 Simulink 工程文件存在<br>2. 检查路径格式（使用正斜杠） |
| 代码生成失败 | "MATLAB 代码生成失败" | 1. 检查 Simulink 模型配置<br>2. 查看 MATLAB 日志输出<br>3. 验证模型编译设置 |
| 执行超时 | "MATLAB 执行超时 (>1800秒)" | 1. 检查模型复杂度<br>2. 增加超时配置<br>3. 查看进程是否卡死 |
| 无输出文件 | "未生成代码文件" | 1. 检查输出目录权限<br>2. 查看 MATLAB 错误日志<br>3. 验证代码生成配置 |

**错误处理流程**：
```
捕获异常
    │
    ▼
判断异常类型
    │
    ├─→ ProcessTimeoutError
    │   ├─→ 清理 MATLAB 进程
    │   ├─→ 记录超时日志
    │   └─→ 返回 StageResult(FAILED, error=..., suggestions=[...])
    │
    ├─→ ProcessExitCodeError
    │   ├─→ 清理 MATLAB 进程
    │   ├─→ 记录退出码日志
    │   └─→ 返回 StageResult(FAILED, error=..., suggestions=[...])
    │
    └─→ 其他异常
        ├─→ 清理 MATLAB 进程
        ├─→ 记录异常详情
        └─→ 返回 StageResult(FAILED, error=..., suggestions=[...])
```

### 阶段完成信号规格

**发送到 UI 的信号**：
```python
# 阶段开始信号
stage_started.emit("matlab_gen")

# 进度更新信号（执行中）
progress_update.emit(10, "正在启动 MATLAB...")
progress_update.emit(20, "正在执行代码生成...")
progress_update.emit(80, "正在验证输出文件...")

# 日志消息信号（实时输出）
log_message.emit("[10:30:15] MATLAB 引擎已启动")
log_message.emit("[10:30:16] 正在编译模型...")
log_message.emit("[10:32:30] 代码生成完成")

# 阶段完成信号
stage_complete.emit("matlab_gen", True)  # True = 成功
# 或
stage_complete.emit("matlab_gen", False)  # False = 失败

# 错误信号（失败时）
error_occurred.emit("MATLAB 代码生成失败", [
    "检查 Simulink 模型配置",
    "查看 MATLAB 日志输出",
    "验证模型编译设置"
])
```

### 性能要求

| 指标 | 要求 | 说明 |
|------|------|------|
| 阶段超时 | 1800 秒（30 分钟） | 可通过 `config.timeout` 覆盖 |
| 轮询间隔 | 0.5 秒 | 检查进程状态和超时 |
| 日志延迟 | < 1 秒 | 输出实时显示到 UI |
| 启动时间 | < 10 秒 | MATLAB 引擎启动时间 |

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 2 - Story 2.5](../../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-012](../../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 2.1](../../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 2.2](../../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-002](../../planning-artifacts/architecture.md)
- [Source: CLAUDE.md#MATLAB代码集成阶段](../../CLAUDE.md)
- [Source: _bmad-output/implementation-artifacts/stories/2-4-start-automated-build-process.md](../2-4-start-automated-build-process.md)

## Dev Agent Record

### Agent Model Used

claude-opus-4-5-20251101

### Debug Log References

- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Story File: `_bmad-output/implementation-artifacts/stories/2-5-execute-matlab-code-generation-phase.md`
- Epics Source: `_bmad-output/planning-artifacts/epics.md` (Lines 382-399)
- Architecture Source: `_bmad-output/planning-artifacts/architecture.md` (Lines 481-691)
- PRD Source: `_bmad-output/planning-artifacts/prd.md` (Lines 454-456)

### Completion Notes List

**实现摘要 (2026-02-11)**:
- ✅ 创建了 `src/integrations/matlab.py` - MATLAB Engine API 集成模块
  - 实现了 `MatlabIntegration` 类，支持启动/停止 MATLAB 引擎
  - 实现了异步脚本执行 `eval_script()` 方法
  - 实现了超时检测（使用 `time.monotonic()`）和进程清理
  - 添加了版本兼容性检查（R2020a+）

- ✅ 创建了 `src/stages/matlab_gen.py` - MATLAB 代码生成阶段执行器
  - 实现了 `execute_stage()` 函数，符合统一阶段接口
  - 实现了输出文件验证 `_validate_output_files()`
  - 支持通过 `BuildContext.state["matlab_output"]` 传递文件列表

- ✅ 扩展了 `src/utils/errors.py` - 添加进程管理错误类
  - `ProcessError` - 进程错误基类
  - `ProcessTimeoutError` - 超时错误
  - `ProcessExitCodeError` - 退出码错误

- ✅ 更新了 `src/core/constants.py` - 添加阶段专用超时配置
  - `STAGE_TIMEOUTS` - 各阶段超时映射
  - `get_stage_timeout()` - 获取阶段超时辅助函数

- ✅ 更新了 `src/core/workflow.py` - 注册 matlab_gen 执行器
  - `STAGE_EXECUTORS` - 阶段执行器映射
  - `_execute_matlab_gen()` - 内部包装函数
  - 使用 TYPE_CHECKING 避免循环导入

- ✅ 编写了 30 个单元测试（18 + 12）
  - `tests/unit/test_matlab_integration.py` - 18 个测试
  - `tests/unit/test_matlab_gen_stage.py` - 12 个测试
  - 所有测试通过，无回归

**技术决策**:
- 使用 MATLAB Engine API for Python 作为集成方案
- 异步执行模式（`async_=True`）配合轮询检测
- 超时检测使用 `time.monotonic()` 避免系统时间调整影响
- 错误处理提供可操作的修复建议

**测试覆盖率**:
- MATLAB 进程启动/关闭测试
- 脚本执行和超时测试
- 输出文件验证测试
- 错误处理和恢复建议测试

### File List

**新建的文件**：
1. `src/integrations/__init__.py` - Integrations 包初始化
2. `src/integrations/matlab.py` - MATLAB Engine API 集成（~330 行）
3. `src/stages/matlab_gen.py` - MATLAB 代码生成阶段（~230 行）
4. `tests/unit/test_matlab_integration.py` - MATLAB 集成测试（~320 行）
5. `tests/unit/test_matlab_gen_stage.py` - MATLAB 生成阶段测试（~280 行）
6. `tests/integration/verify_matlab_integration.py` - 功能验证脚本

**修改的文件**：
1. `src/core/constants.py` - 添加 `STAGE_TIMEOUTS` 和 `get_stage_timeout()`
2. `src/core/workflow.py` - 添加 `STAGE_EXECUTORS` 和 `_execute_matlab_gen()`
3. `src/core/models.py` - 添加 `BuildContext.signal_emit` 和 `emit_signal()` 方法
4. `src/utils/errors.py` - 添加 `ProcessError`, `ProcessTimeoutError`, `ProcessExitCodeError`

**配置文件更新**：
1. `_bmad-output/implementation-artifacts/sprint-status.yaml` - 状态更新
2. `_bmad-output/implementation-artifacts/stories/2-5-execute-matlab-code-generation-phase.md` - 故事状态更新

## Code Review Record (2026-02-11)

**Review Type**: Adversarial Senior Developer Review
**Review Outcome**: ✅ Approved (after fixes)
**Issues Found**: 3 High, 2 Medium, 3 Low
**Issues Fixed**: 5 (all High and Medium)

### Issues Fixed:

1. **[HIGH]** 任务 3.4 - 添加日志时间戳格式 (`[HH:MM:SS]`)
   - File: `src/integrations/matlab.py:73-82`
   - Fix: 在 `_log()` 方法中添加 `datetime.datetime.now().strftime("[%H:%M:%S]")`

2. **[HIGH]** 任务 6.5 - 添加 UI 信号发送支持
   - Files: `src/core/models.py`, `src/stages/matlab_gen.py`
   - Fix: 添加 `BuildContext.signal_emit` 和 `emit_signal()` 方法

3. **[HIGH]** MATLAB 2025 版本支持
   - File: `src/integrations/matlab.py:161`
   - Fix: 版本检查添加 "25" 支持

4. **[MEDIUM]** genCode.m 脚本路径配置
   - File: `src/stages/matlab_gen.py`
   - Fix: 支持从配置读取脚本名称 (`gencode_script_path`)

5. **[MEDIUM]** File List 更新
   - File: 故事文件
   - Fix: 添加 `tests/integration/verify_matlab_integration.py`

### Remaining LOW Issues (Optional):

6. **[LOW]** `process_mgr.py` 未修改 - 功能已在 `MatlabIntegration` 中实现
7. **[LOW]** 版本检查日志优化 - 已在修复 3 中解决
8. **[LOW]** 标准错误处理区分 - MATLAB Engine API 限制
