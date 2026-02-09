# Story 2.4: 启动自动化构建流程

Status: todo

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要一键启动自动化构建流程，
以便系统按顺序执行所有配置的阶段。

## Acceptance Criteria

**Given** 用户已配置项目和选择工作流
**When** 用户点击"开始构建"按钮
**Then** 系统锁定配置界面防止修改
**And** 系统开始执行工作流的第一个阶段
**And** 系统更新 UI 显示当前执行状态
**And** 系统记录构建开始时间戳
**And** 系统启用"取消构建"按钮

## Tasks / Subtasks

- [ ] 任务 1: 创建工作流执行数据模型 (AC: Then - 记录构建开始时间戳)
  - [ ] 1.1 在 `src/core/models.py` 中定义 `BuildExecution` dataclass
  - [ ] 1.2 在 `src/core/models.py` 中定义 `BuildState` enum（IDLE, RUNNING, COMPLETED, FAILED, CANCELLED）
  - [ ] 1.3 在 `src/core/models.py` 中定义 `StageExecution` dataclass
  - [ ] 1.4 确保所有字段提供默认值（架构 Decision 1.2）

- [ ] 任务 2: 创建工作流线程 (AC: Then - 执行工作流的第一个阶段)
  - [ ] 2.1 创建 `src/core/workflow_thread.py`
  - [ ] 2.2 继承 PyQt6 `QThread` 作为基类
  - [ ] 2.3 定义工作流执行信号（进度更新、阶段完成、日志消息、错误发生）
  - [ ] 2.4 实现 `run()` 方法作为工作流执行入口
  - [ ] 2.5 实现 `execute_workflow()` 方法执行所有启用的阶段

- [ ] 任务 3: 实现阶段执行编排 (AC: Then - 按顺序执行所有配置的阶段)
  - [ ] 3.1 在 `src/core/workflow.py` 创建 `execute_workflow()` 函数
  - [ ] 3.2 遍历工作流配置中的所有阶段
  - [ ] 3.3 跳过禁用的阶段（config.enabled = False）
  - [ ] 3.4 按顺序调用每个阶段的 `execute_stage()` 函数
  - [ ] 3.5 使用 `BuildContext` 在阶段间传递状态

- [ ] 任务 4: 实现配置界面锁定 (AC: Then - 锁定配置界面防止修改)
  - [ ] 4.1 在 `src/ui/main_window.py` 添加 `set_config_ui_enabled()` 方法
  - [ ] 4.2 构建开始时禁用配置相关控件（项目配置、工作流选择）
  - [ ] 4.3 构建完成/失败/取消后重新启用控件
  - [ ] 4.4 更新控件视觉状态（灰色显示、禁用状态）

- [ ] 任务 5: 实现实时状态更新 (AC: Then - 更新 UI 显示当前执行状态)
  - [ ] 5.1 在主窗口连接工作流线程信号到 UI 更新槽函数
  - [ ] 5.2 使用 `QueuedConnection` 确保线程安全（架构 Decision 3.1）
  - [ ] 5.3 实现 `update_progress()` 槽函数更新进度条
  - [ ] 5.4 实现 `update_stage_status()` 槽函数更新阶段状态
  - [ ] 5.5 实现 `append_log()` 槽函数追加日志内容

- [ ] 任务 6: 实现构建时间戳记录 (AC: Then - 记录构建开始时间戳)
  - [ ] 6.1 在工作流线程 `run()` 开始时记录开始时间（`time.monotonic()`）
  - [ ] 6.2 计算整体进度百分比（已完成阶段数 / 总阶段数）
  - [ ] 6.3 记录每个阶段的开始和结束时间
  - [ ] 6.4 在构建完成后计算总执行时长

- [ ] 任务 7: 实现取消构建功能 (AC: Then - 启用"取消构建"按钮)
  - [ ] 7.1 在主窗口添加"取消构建"按钮
  - [ ] 7.2 构建开始时启用"取消构建"按钮
  - [ ] 7.3 点击"取消构建"按钮调用线程的 `requestInterruption()`
  - [ ] 7.4 在阶段执行循环中检查中断标志
  - [ ] 7.5 构建完成后禁用"取消构建"按钮

- [ ] 任务 8: 集成工作流管理器 (AC: Given - 用户已配置项目和选择工作流)
  - [ ] 8.1 创建 `src/core/workflow_manager.py`
  - [ ] 8.2 管理工作流线程的生命周期（启动、停止、清理）
  - [ ] 8.3 在主窗口初始化工作流管理器
  - [ ] 8.4 将工作流管理器与 UI 控件连接

- [ ] 任务 9: 添加执行前验证 (AC: Given - 用户已配置项目和选择工作流)
  - [ ] 9.1 在"开始构建"前自动调用 `validate_workflow_config()`
  - [ ] 9.2 如果验证失败，显示验证结果对话框并阻止构建
  - [ ] 9.3 如果验证通过，继续启动构建流程
  - [ ] 9.4 记录验证结果到日志

- [ ] 任务 10: 实现构建完成处理 (AC: Then - 更新 UI 显示当前执行状态)
  - [ ] 10.1 实现工作流线程 `finished` 信号处理
  - [ ] 10.2 解锁配置界面
  - [ ] 10.3 禁用"取消构建"按钮
  - [ ] 10.4 显示构建完成摘要（成功/失败/取消）
  - [ ] 10.5 记录最终状态到日志文件

## Dev Notes

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **ADR-001（渐进式架构）**：MVP 使用函数式模块，PyQt6 类仅用于 UI 层
- **ADR-002（防御性编程）**：所有外部进程调用设置超时，文件操作前备份
- **ADR-003（可观测性）**：日志是架构基础，实时进度通过信号槽机制实现
- **ADR-004（混合架构模式）**：UI 层用 PyQt6 类，业务逻辑用函数
- **Decision 1.2（数据模型）**：使用 dataclass，所有字段提供默认值
- **Decision 2.1（MATLAB 进程管理）**：每次启动/关闭，超时检测，僵尸进程清理
- **Decision 2.2（进程管理器架构）**：独立的进程管理器模块，统一错误类
- **Decision 3.1（PyQt6 线程）**：QThread + pyqtSignal，使用 QueuedConnection
- **Decision 5.1（日志框架）**：logging + 自定义 PyQt6 Handler

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 信号连接：跨线程信号必须使用 `Qt.ConnectionType.QueuedConnection`
2. ⭐⭐⭐⭐⭐ 超时检测：使用 `time.monotonic()` 而非 `time.time()`
3. ⭐⭐⭐⭐⭐ 数据模型：使用 `dataclass`，所有字段提供默认值 `field(default=...)`
4. ⭐⭐⭐⭐⭐ 错误处理：使用统一的错误类（`ProcessError` 及子类）
5. ⭐⭐⭐⭐ 状态传递：使用 `BuildContext`，不使用全局变量
6. ⭐⭐⭐⭐ 超时配置：从 `DEFAULT_TIMEOUT` 字典获取，不硬编码
7. ⭐⭐⭐ 路径处理：使用 `pathlib.Path` 而非字符串
8. ⭐⭐⭐ 日志记录：使用 `logging` 模块，不使用 `print()`

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/core/models.py` | 修改 | 添加 BuildExecution, BuildState, StageExecution |
| `src/core/workflow.py` | 修改 | 添加 execute_workflow() 函数 |
| `src/core/workflow_thread.py` | 新建 | 工作流线程 |
| `src/core/workflow_manager.py` | 新建 | 工作流管理器 |
| `src/ui/main_window.py` | 修改 | 集成构建执行功能 |
| `src/utils/process_mgr.py` | 修改 | 进程管理器（如需扩展） |
| `src/utils/logger.py` | 修改 | 日志系统（如需扩展） |

**确保符合项目结构**：
```
src/
├── ui/                                       # PyQt6 类
│   └── main_window.py                       # 主窗口（需修改）
├── core/                                     # 业务逻辑（函数）
│   ├── models.py                            # 数据模型（需修改）
│   ├── workflow.py                          # 工作流逻辑（需修改）
│   ├── workflow_thread.py                  # 工作流线程（新建）
│   └── workflow_manager.py                 # 工作流管理器（新建）
└── utils/                                    # 工具函数
    ├── process_mgr.py                       # 进程管理器（可选修改）
    └── logger.py                            # 日志系统（可选修改）
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| PyQt6 | 最新稳定版 | UI 框架，线程，信号槽 |
| dataclasses | 内置 (3.7+) | 数据模型 |
| enum | 内置 | 枚举类型 |
| pathlib | 内置 | 路径处理 |
| logging | 内置 | 日志记录 |
| time | 内置 | 时间测量（使用 monotonic） |

### 测试标准

**单元测试要求**：
- 测试工作流执行数据模型（BuildExecution, StageExecution）
- 测试工作流线程信号发射
- 测试阶段执行编排逻辑
- 测试构建时间戳记录
- 测试取消构建逻辑

**集成测试要求**：
- 测试工作流管理器与主窗口的集成
- 测试完整的构建流程（5 个阶段）
- 测试配置界面锁定/解锁
- 测试实时状态更新

**端到端测试要求**：
- 测试从点击"开始构建"到构建完成的完整流程
- 测试从点击"取消构建"到构建取消的完整流程

### 依赖关系

**前置故事**：
- ✅ Epic 1 全部完成（项目配置管理）
- ✅ Story 2.1: 选择预定义工作流模板（已创建工作流配置数据模型）
- ✅ Story 2.2: 加载自定义工作流配置（已支持工作流配置）
- ✅ Story 2.3: 验证工作流配置有效性（已实现验证功能）

**后续故事**：
- Story 2.5: 执行 MATLAB 代码生成阶段
- Story 2.6: 提取并处理代码文件
- Story 2.7: 移动代码文件到指定目录
- Story 2.8: 调用 IAR 命令行编译
- Story 2.9: 更新 A2L 文件变量地址
- Story 2.10: 替换 A2L 文件 XCP 头文件内容
- Story 2.11: 创建时间戳目标文件夹
- Story 2.12: 移动 HEX 和 A2L 文件到目标文件夹

### 数据流设计

```
用户点击"开始构建"按钮
    │
    ▼
验证工作流配置 (validate_workflow_config)
    │
    ├─→ 验证失败 → 显示验证结果对话框 → 阻止构建
    │
    └─→ 验证通过 → 继续构建
        │
        ▼
    锁定配置界面 (set_config_ui_enabled False)
        │
        ▼
    创建工作流线程 (WorkflowThread)
        │
        ▼
    连接信号 (QueuedConnection)
        │
        ├─→ progress_update → update_progress()
        ├─→ stage_complete → update_stage_status()
        ├─→ log_message → append_log()
        └─→ error_occurred → show_error_dialog()
        │
        ▼
    启动线程 (workflow_thread.start())
        │
        ▼
    工作流线程执行 (run())
        │
        ├─→ 记录构建开始时间戳
        ├─→ 遍历所有启用的阶段
        │   │
        │   └─→ execute_stage(config, context)
        │       │
        │       ├─→ 发送进度更新信号
        │       ├─→ 执行阶段逻辑
        │       └─→ 发送阶段完成信号
        │
        ├─→ 检查中断标志
        │   ├─→ 中断 → 停止构建
        │   └─→ 未中断 → 继续下一个阶段
        │
        └─→ 所有阶段完成 → 发送 finished 信号
        │
        ▼
    工作流完成处理
        │
        ├─→ 解锁配置界面 (set_config_ui_enabled True)
        ├─→ 禁用"取消构建"按钮
        ├─→ 显示构建完成摘要
        └─→ 记录最终状态到日志
```

### 数据模型规格

**BuildState**：
```python
class BuildState(Enum):
    """构建状态"""
    IDLE = "idle"           # 空闲
    RUNNING = "running"     # 运行中
    COMPLETED = "completed" # 已完成
    FAILED = "failed"       # 失败
    CANCELLED = "cancelled" # 已取消
```

**StageExecution**：
```python
@dataclass
class StageExecution:
    """阶段执行信息"""
    name: str                    # 阶段名称
    status: BuildState           # 执行状态
    start_time: float            # 开始时间（time.monotonic）
    end_time: float = 0.0        # 结束时间
    duration: float = 0.0        # 执行时长（秒）
    error_message: str = ""      # 错误消息
    output_files: list[str] = field(default_factory=list)  # 输出文件列表
```

**BuildExecution**：
```python
@dataclass
class BuildExecution:
    """构建执行信息"""
    project_name: str            # 项目名称
    workflow_id: str             # 工作流 ID
    state: BuildState = BuildState.IDLE  # 构建状态
    start_time: float = 0.0      # 开始时间（time.monotonic）
    end_time: float = 0.0        # 结束时间
    duration: float = 0.0        # 总执行时长（秒）
    current_stage: str = ""      # 当前阶段名称
    progress_percent: int = 0    # 进度百分比（0-100）
    stages: list[StageExecution] = field(default_factory=list)  # 阶段执行列表
    error_message: str = ""      # 错误消息
```

### 工作流线程信号规格

**WorkflowThread 信号定义**：
```python
class WorkflowThread(QThread):
    # 定义信号
    progress_update = pyqtSignal(int, str)      # 进度百分比, 消息
    stage_started = pyqtSignal(str)             # 阶段名称
    stage_complete = pyqtSignal(str, bool)      # 阶段名, 成功
    log_message = pyqtSignal(str)               # 日志内容
    error_occurred = pyqtSignal(str, list)      # 错误消息, 建议列表
    build_finished = pyqtSignal(BuildState)     # 构建最终状态
```

### 构建流程规格

**工作流执行逻辑**：
```python
def execute_workflow(workflow_config: WorkflowConfig, context: BuildContext) -> bool:
    """
    执行工作流

    Args:
        workflow_config: 工作流配置
        context: 构建上下文

    Returns:
        bool: True 表示全部成功，False 表示有失败
    """
    # 工作流阶段映射
    STAGE_EXECUTORS = {
        "matlab_gen": stages.matlab_gen.execute_stage,
        "file_process": stages.file_process.execute_stage,
        "iar_compile": stages.iar_compile.execute_stage,
        "a2l_process": stages.a2l_process.execute_stage,
        "package": stages.package.execute_stage,
    }

    total_stages = len([s for s in workflow_config.stages if s.enabled])
    completed_stages = 0

    for stage_config in workflow_config.stages:
        # 跳过禁用的阶段
        if not stage_config.enabled:
            continue

        # 检查中断标志
        if QThread.currentThread().isInterruptionRequested():
            context.log_callback("构建已取消")
            return False

        # 发送阶段开始信号
        stage_started.emit(stage_config.name)

        # 执行阶段
        result = STAGE_EXECUTORS[stage_config.name](stage_config, context)

        # 发送阶段完成信号
        stage_complete.emit(stage_config.name, result.status == StageStatus.COMPLETED)

        # 更新进度
        completed_stages += 1
        progress = int((completed_stages / total_stages) * 100)
        progress_update.emit(progress, f"完成阶段: {stage_config.name}")

        # 检查阶段结果
        if result.status == StageStatus.FAILED:
            error_occurred.emit(result.message, result.suggestions or [])
            return False

    return True
```

### 进度计算规格

**进度计算规则**：
```
进度百分比 = (已完成阶段数 / 总启用阶段数) × 100

示例：
- 总启用阶段数：5（所有阶段都启用）
- 已完成阶段数：3（matlab_gen, file_process, iar_compile）
- 进度百分比：(3 / 5) × 100 = 60%
```

**阶段状态映射**：
| 阶段状态 | BuildState | 说明 |
|---------|-----------|------|
| PENDING | IDLE | 等待执行 |
| RUNNING | RUNNING | 正在执行 |
| COMPLETED | COMPLETED | 已完成 |
| FAILED | FAILED | 失败 |
| CANCELLED | CANCELLED | 已取消 |

### 取消构建流程

```
用户点击"取消构建"按钮
    │
    ▼
检查构建状态
    │
    ├─→ 构建未运行 → 不执行任何操作
    │
    └─→ 构建运行中 → 继续取消流程
        │
        ▼
    调用线程中断 (workflow_thread.requestInterruption())
        │
        ▼
    工作流线程检查中断标志
        │
        ├─→ 阶段执行前检查 → 立即停止
        ├─→ 阶段执行中检查 → 完成当前阶段后停止
        └─→ 进程执行中 → 尝试终止进程
        │
        ▼
    更新 UI 状态
        │
        ├─→ 解锁配置界面
        ├─→ 禁用"取消构建"按钮
        ├─→ 更新构建状态为 CANCELLED
        └─→ 记录取消日志
```

### 错误处理流程

```
阶段执行失败
    │
    ▼
    阶段返回 StageResult(status=FAILED)
        │
        ▼
    工作流线程捕获失败状态
        │
        ▼
    发送错误信号 (error_occurred)
        │
        ├─→ 错误消息
        └─→ 修复建议列表
        │
        ▼
    主窗口显示错误对话框
        │
        ├─→ 显示错误消息
        ├─→ 列出修复建议
        └─→ 提供操作按钮（重试、关闭）
        │
        ▼
    停止后续阶段执行
        │
        ▼
    更新构建状态为 FAILED
        │
        ▼
    解锁配置界面
        │
        ▼
    记录错误日志
```

### 工作流管理器设计

**WorkflowManager 职责**：
- 管理工作流线程的生命周期
- 协调 UI 与工作流线程之间的通信
- 维护构建状态信息
- 处理构建取消请求

**WorkflowManager 接口**：
```python
class WorkflowManager:
    """工作流管理器"""

    def __init__(self, parent):
        self.parent = parent
        self.workflow_thread: WorkflowThread = None
        self.current_execution: BuildExecution = None

    def start_workflow(self, project_config: ProjectConfig, workflow_config: WorkflowConfig):
        """启动工作流"""
        pass

    def stop_workflow(self):
        """停止工作流"""
        pass

    def is_running(self) -> bool:
        """检查是否运行中"""
        return self.workflow_thread is not None and self.workflow_thread.isRunning()

    def get_current_execution(self) -> BuildExecution:
        """获取当前构建执行信息"""
        return self.current_execution
```

### UI 状态管理

**构建前 UI 状态**：
- 项目配置区域：可编辑
- 工作流选择区域：可编辑
- "开始构建"按钮：启用
- "取消构建"按钮：禁用
- 进度面板：隐藏或显示为空闲状态
- 日志窗口：可滚动查看历史日志

**构建中 UI 状态**：
- 项目配置区域：禁用（灰色显示）
- 工作流选择区域：禁用（灰色显示）
- "开始构建"按钮：禁用
- "取消构建"按钮：启用
- 进度面板：显示进度条和阶段状态
- 日志窗口：自动滚动显示实时日志

**构建后 UI 状态**：
- 项目配置区域：启用
- 工作流选择区域：启用
- "开始构建"按钮：启用
- "取消构建"按钮：禁用
- 进度面板：显示最终状态（成功/失败/取消）
- 日志窗口：停止自动滚动，允许用户查看

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 2 - Story 2.4](../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-010](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-011](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 2.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 2.2](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 3.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-001](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-002](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-003](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-004](../planning-artifacts/architecture.md)

## Dev Agent Record

### Agent Model Used

_(待实施时填写)_

### Debug Log References

- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Story File: `_bmad-output/implementation-artifacts/stories/2-4-start-automated-build-process.md`
- Epics Source: `_bmad-output/planning-artifacts/epics.md` (Lines 340-353)
- Architecture Source: `_bmad-output/planning-artifacts/architecture.md` (Lines 481-575, 1169-1250, 1851-1925)

### Completion Notes List

_(待实施时填写)_

### File List

_(待实施时填写)_

**预计创建的文件**：
1. `src/core/workflow_thread.py` - 工作流线程
2. `src/core/workflow_manager.py` - 工作流管理器
3. `tests/unit/test_build_models.py` - 构建数据模型测试
4. `tests/unit/test_workflow_thread.py` - 工作流线程测试
5. `tests/unit/test_workflow_manager.py` - 工作流管理器测试
6. `tests/unit/test_workflow_execution.py` - 工作流执行测试
7. `tests/integration/test_build_ui_integration.py` - UI 集成测试

**预计修改的文件**：
1. `src/core/models.py` - 添加 BuildExecution, BuildState, StageExecution
2. `src/core/workflow.py` - 添加 execute_workflow() 函数
3. `src/ui/main_window.py` - 集成构建执行功能
