# Story 2.4: 启动自动化构建流程

Status: review

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

- [x] Task 1: 实现工作流执行基础架构 (AC: #)
  - [x] Subtask 1.1: 创建 WorkflowThread 类 (QThread)
  - [x] Subtask 1.2: 定义工作流信号类型 (progress_update, stage_complete, log_message, error_occurred, build_finished)
  - [x] Subtask 1.3: 实现 BuildContext 用于阶段间状态传递
  - [x] Subtask 1.4: 添加单元测试验证线程启动和信号发射

- [x] Task 2: 实现构建流程编排逻辑 (AC: #)
  - [x] Subtask 2.1: 创建 execute_workflow() 函数遍历所有启用阶段
  - [x] Subtask 2.2: 实现阶段执行顺序控制 (基于 workflow.py 中的 STAGE_ORDER)
  - [x] Subtask 2.3: 添加阶段执行前验证 (enabled状态, 依赖检查)
  - [x] Subtask 2.4: 记录构建开始时间戳到 BuildContext

- [x] Task 3: 实现UI状态管理 (AC: #)
  - [x] Subtask 3.1: 创建 _lock_config_ui() 方法锁定配置界面
  - [x] Subtask 3.2: 实现 _unlock_config_ui() 方法解锁配置界面
  - [x] Subtask 3.3: 添加构建状态标志 (_is_building) 防止重复启动
  - [x] Subtask 3.4: 实现 _on_build_finished() 处理构建完成

- [x] Task 4: 实现进度反馈机制 (AC: #)
  - [x] Subtask 4.1: 连接 WorkflowThread 信号到 UI 槽函数 (使用 QueuedConnection)
  - [x] Subtask 4.2: 实现 _on_progress_update() 更新进度条
  - [x] Subtask 4.3: 实现 _on_stage_complete() 更新阶段状态显示
  - [x] Subtask 4.4: 实现 _on_log_message() 追加日志到日志区域

- [x] Task 5: 实现错误处理和恢复 (AC: #)
  - [x] Subtask 5.1: 实现 _on_error_occurred() 显示错误对话框
  - [x] Subtask 5.2: 添加错误时自动解锁配置界面
  - [x] Subtask 5.3: 记录错误日志到文件系统
  - [x] Subtask 5.4: 提供可操作的修复建议 (基于 ProcessError suggestions)

- [x] Task 6: 实现"取消构建"按钮功能 (AC: #)
  - [x] Subtask 6.1: 添加 cancel_btn 到 UI (初始隐藏)
  - [x] Subtask 6.2: 实现 _cancel_build() 方法
  - [x] Subtask 6.3: 在 WorkflowThread 中实现 requestInterruption() 响应
  - [x] Subtask 6.4: 添加阶段取消时的清理逻辑

- [x] Task 7: 集成验证流程 (AC: #)
  - [x] Subtask 7.1: 确保 _start_build() 调用 validate_workflow_config()
  - [x] Subtask 7.2: 验证失败时阻止构建启动
  - [x] Subtask 7.3: 显示验证错误对话框

- [x] Task 8: 添加集成测试 (AC: #)
  - [x] Subtask 8.1: 测试完整构建流程 (使用 mock 阶段)
  - [x] Subtask 8.2: 测试取消构建功能
  - [x] Subtask 8.3: 测试错误处理和恢复
  - [x] Subtask 8.4: 测试UI状态锁定/解锁

## Dev Notes

### 核心架构要求

本Story实现工作流执行的核心框架，必须严格遵循架构文档中的关键决策：

1. **阶段接口模式** (Architecture Decision 1.1 + 2.1)
   ```python
   # 统一阶段签名 - 所有阶段必须遵循
   def execute_stage(
       config: StageConfig,
       context: BuildContext
   ) -> StageResult:
       """阶段执行接口

       Returns:
           StageResult: 包含 status, message, output_files, error, suggestions
       """
   ```

2. **线程安全** (Architecture Decision 3.1 - CRITICAL)
   ```python
   # 跨线程信号必须使用 QueuedConnection
   self.worker.progress_update.connect(
       self._on_progress_update,
       Qt.ConnectionType.QueuedConnection  # ← 必须
   )
   self.worker.error_occurred.connect(
       self._on_error_occurred,
       Qt.ConnectionType.QueuedConnection  # ← 必须
   )
   ```

3. **超时检测** (Architecture Decision 2.1 - CRITICAL)
   ```python
   # 必须使用 time.monotonic() 而非 time.time()
   start = time.monotonic()  # ← 正确
   # 不使用: start = time.time()  # ← 错误：受系统时间调整影响
   ```

4. **状态传递** (Architecture Decision 1.2)
   ```python
   class BuildContext:
       """构建上下文 - 阶段间传递状态

       属性:
           config: dict          # 只读全局配置
           state: dict           # 可写阶段状态
           log_callback: callable # 统一日志接口
       """
   ```

### 项目结构对齐

本Story涉及的新增文件：

```
src/
├── core/
│   ├── workflow.py          # 修改: 添加 execute_workflow()
│   ├── models.py            # 修改: 确保有 BuildContext, StageResult
│   └── constants.py         # 新增: DEFAULT_TIMEOUT (如果不存在)
│
├── ui/
│   ├── main_window.py       # 修改: 实现构建启动和UI管理
│   └── widgets/
│       ├── progress_panel.py    # 新增: 进度显示面板 (可选，Story 3.1)
│       └── log_viewer.py        # 新增: 日志查看器 (可选，Story 3.2)
│
└── stages/                  # 新增目录: 工作流阶段实现 (本Story创建基础)
    ├── __init__.py
    └── base.py              # 新增: 阶段基类定义
```

### 前序Story学习

**Story 2.1 实现模式:**
- WorkflowSelectDialog: 使用 QDialog + 表单布局
- 工作流模板存储在 `configs/default_workflow.json`
- WorkflowConfig 使用 dataclass 序列化

**Story 2.2 实现模式:**
- QFileDialog.getOpenFileName() 用于文件选择
- JSON 反序列化后使用 WorkflowConfig.from_dict()

**Story 2.3 实现模式:**
- ValidationResult 收集所有验证错误后统一显示
- ValidationError 包含可操作的 suggestions 列表
- ValidationResultDialog 使用 QTreeWidget 显示分类错误

### 关键实现细节

**1. WorkflowThread 实现** (Task 1.1-1.2)
```python
# src/ui/main_window.py
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from core.models import ProjectConfig, WorkflowConfig, BuildContext
from core.workflow import execute_workflow
import logging

logger = logging.getLogger(__name__)

class WorkflowThread(QThread):
    """工作流执行线程 - 在后台执行构建流程"""

    # 信号定义 (必须使用 pyqtSignal)
    progress_update = pyqtSignal(int, str)  # (进度百分比, 消息)
    stage_complete = pyqtSignal(str, bool)   # (阶段名, 成功)
    log_message = pyqtSignal(str)            # (日志内容)
    error_occurred = pyqtSignal(str, list)   # (错误, 建议列表)
    finished = pyqtSignal(bool)             # (成功)

    def __init__(self, project_config: ProjectConfig, workflow_config: WorkflowConfig):
        super().__init__()
        self.project_config = project_config
        self.workflow_config = workflow_config
        self._is_cancelled = False

    def run(self):
        """执行工作流 - 在后台线程中运行"""
        try:
            logger.info(f"开始执行工作流: {self.workflow_config.name}")

            # 创建构建上下文
            context = BuildContext()
            context.config = self.project_config.to_dict()
            context.log_callback = self._log

            # 执行工作流
            success = execute_workflow(
                self.workflow_config,
                context,
                progress_callback=self._update_progress,
                stage_callback=self._on_stage_complete,
                cancel_check=lambda: self._is_cancelled
            )

            self.finished.emit(success)

        except Exception as e:
            logger.error(f"工作流执行异常: {e}")
            self.error_occurred.emit(str(e), ["查看日志获取详细信息"])

    def cancel(self):
        """请求取消工作流"""
        self._is_cancelled = True
        logger.info("收到取消请求")

    def _log(self, message: str):
        """日志回调 - 发射信号到UI"""
        self.log_message.emit(message)

    def _update_progress(self, percent: int, message: str):
        """进度更新回调"""
        self.progress_update.emit(percent, message)

    def _on_stage_complete(self, stage_name: str, success: bool):
        """阶段完成回调"""
        self.stage_complete.emit(stage_name, success)
```

**2. execute_workflow() 实现** (Task 2.1-2.4)
```python
# src/core/workflow.py
import time
from typing import Callable, Optional
from core.models import (
    WorkflowConfig, ProjectConfig, BuildContext,
    StageResult, StageStatus
)
from core.constants import DEFAULT_TIMEOUT  # 确保这个文件存在

# 工作流阶段执行顺序
STAGE_ORDER = [
    "matlab_gen",
    "file_process",
    "iar_compile",
    "a2l_process",
    "package"
]

def execute_workflow(
    workflow_config: WorkflowConfig,
    context: BuildContext,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    stage_callback: Optional[Callable[[str, bool], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None
) -> bool:
    """执行工作流

    Args:
        workflow_config: 工作流配置
        context: 构建上下文
        progress_callback: 进度回调 (百分比, 消息)
        stage_callback: 阶段完成回调 (阶段名, 成功)
        cancel_check: 取消检查回调

    Returns:
        bool: 是否全部成功
    """
    # 记录开始时间
    start_time = time.monotonic()  # ← 使用 monotonic
    context.state["build_start_time"] = start_time

    logger.info(f"开始执行工作流: {workflow_config.name}")

    # 获取启用的阶段 (按顺序)
    enabled_stages = [
        s for s in workflow_config.stages
        if s.enabled
    ]

    if not enabled_stages:
        logger.warning("没有启用的阶段")
        return False

    total_stages = len(enabled_stages)

    # 执行每个阶段
    for i, stage_config in enumerate(enabled_stages):
        # 检查取消
        if cancel_check and cancel_check():
            logger.info("工作流被取消")
            context.state["cancel_reason"] = "user_requested"
            return False

        # 更新进度
        stage_name = stage_config.name
        progress = int((i / total_stages) * 100)

        if progress_callback:
            progress_callback(progress, f"执行阶段: {stage_name}")

        logger.info(f"开始执行阶段 {i+1}/{total_stages}: {stage_name}")

        # TODO: 实际执行阶段 (当前为占位实现)
        # 后续Story (2.5-2.12) 会实现具体阶段
        # result = _execute_stage_impl(stage_config, context)

        # 占位: 模拟阶段执行成功
        result = StageResult(
            status=StageStatus.COMPLETED,
            message=f"阶段 {stage_name} 执行成功 (占位实现)"
        )

        # 通知阶段完成
        if stage_callback:
            stage_callback(stage_name, result.status == StageStatus.COMPLETED)

        # 检查阶段是否失败
        if result.status == StageStatus.FAILED:
            logger.error(f"阶段 {stage_name} 失败: {result.message}")
            context.state["failed_stage"] = stage_name
            context.state["failure_reason"] = result.message

            if progress_callback:
                progress_callback(progress, f"阶段失败: {stage_name}")

            return False

        # 保存阶段输出到上下文
        context.state[f"{stage_name}_output"] = result.output_files or []

    # 计算总执行时间
    elapsed = time.monotonic() - start_time
    context.state["build_duration"] = elapsed

    logger.info(f"工作流执行完成，耗时: {elapsed:.2f} 秒")

    if progress_callback:
        progress_callback(100, "工作流完成")

    return True
```

**3. UI状态管理** (Task 3)
```python
# src/ui/main_window.py - MainWindow 类新增方法

def _lock_config_ui(self):
    """锁定配置界面 - 构建期间禁用修改"""
    self.project_combo.setEnabled(False)

    # 禁用所有操作按钮
    for btn in [self.validate_btn, self.build_btn]:
        btn.setEnabled(False)

    # 显示取消按钮 (初始隐藏)
    if hasattr(self, 'cancel_btn'):
        self.cancel_btn.setVisible(True)
        self.cancel_btn.setEnabled(True)

    # 更新状态栏
    self.status_bar.showMessage("🔒 构建进行中 - 配置已锁定")
    logger.info("配置界面已锁定")

def _unlock_config_ui(self):
    """解锁配置界面 - 构建完成后恢复"""
    self.project_combo.setEnabled(True)

    # 恢复按钮状态
    self.validate_btn.setEnabled(bool(self._current_config))
    self.build_btn.setEnabled(bool(self._current_config))

    # 隐藏取消按钮
    if hasattr(self, 'cancel_btn'):
        self.cancel_btn.setVisible(False)

    # 更新状态栏
    self.status_bar.showMessage("✅ 构建完成 - 配置已解锁")
    logger.info("配置界面已解锁")

def _start_build(self):
    """开始构建流程 - 修改现有实现"""
    if not self._current_config:
        QMessageBox.warning(self, "⚠️ 未加载项目", "请先加载一个项目配置。")
        return

    # 防止重复启动
    if hasattr(self, '_is_building') and self._is_building:
        QMessageBox.warning(self, "⚠️ 构建进行中", "已有构建在运行中。")
        return

    # 验证配置
    try:
        self.status_bar.showMessage("🔍 开始前验证配置...")

        # 获取工作流配置
        workflow_config = self._get_workflow_config()

        # 执行验证
        result = validate_workflow_config(workflow_config, self._current_config)

        if not result.is_valid:
            show_validation_result(result, self)
            self.status_bar.showMessage("❌ 配置验证失败")
            return

        # 锁定UI
        self._lock_config_ui()
        self._is_building = True

        # 创建工作流线程
        self._workflow_thread = WorkflowThread(
            self._current_config,
            workflow_config
        )

        # 连接信号 (必须使用 QueuedConnection)
        self._workflow_thread.progress_update.connect(
            self._on_progress_update,
            Qt.ConnectionType.QueuedConnection
        )
        self._workflow_thread.stage_complete.connect(
            self._on_stage_complete,
            Qt.ConnectionType.QueuedConnection
        )
        self._workflow_thread.log_message.connect(
            self._on_log_message,
            Qt.ConnectionType.QueuedConnection
        )
        self._workflow_thread.error_occurred.connect(
            self._on_error_occurred,
            Qt.ConnectionType.QueuedConnection
        )
        self._workflow_thread.finished.connect(
            self._on_build_finished,
            Qt.ConnectionType.QueuedConnection
        )

        # 启动线程
        self._workflow_thread.start()

        self.status_bar.showMessage("🚀 构建流程启动...")
        logger.info("构建流程已启动")

    except Exception as e:
        logger.error(f"启动构建时发生错误: {e}")
        self._unlock_config_ui()
        self._is_building = False
        QMessageBox.critical(self, "❌ 启动失败", f"无法启动构建:\n\n{str(e)}")

def _cancel_build(self):
    """取消构建"""
    if hasattr(self, '_workflow_thread') and self._is_building:
        reply = QMessageBox.question(
            self,
            "⚠️ 确认取消",
            "确定要取消当前构建吗？\n\n正在执行的操作将被中断。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.status_bar.showMessage("⏸️ 正在取消构建...")
            self._workflow_thread.cancel()
            logger.info("用户请求取消构建")

def _on_build_finished(self, success: bool):
    """构建完成回调"""
    self._is_building = False
    self._unlock_config_ui()

    if success:
        QMessageBox.information(
            self,
            "✅ 构建成功",
            f"项目 {self._current_config.name} 构建成功！"
        )
        self.status_bar.showMessage("✅ 构建完成")
    else:
        # 检查是否是用户取消
        if self._workflow_thread.isCancelled():
            self.status_bar.showMessage("⏸️ 构建已取消")
            QMessageBox.information(self, "⏸️ 已取消", "构建已被用户取消。")
        else:
            self.status_bar.showMessage("❌ 构建失败")
            # 错误详情已在 error_occurred 中处理

def _on_progress_update(self, percent: int, message: str):
    """进度更新回调"""
    self.status_bar.showMessage(f"📊 {percent}% - {message}")

def _on_stage_complete(self, stage_name: str, success: bool):
    """阶段完成回调"""
    status = "✅" if success else "❌"
    logger.info(f"{status} 阶段完成: {stage_name}")

    # TODO: 更新UI中的阶段状态显示 (Story 3.1)

def _on_log_message(self, message: str):
    """日志消息回调"""
    # TODO: 显示在日志查看器中 (Story 3.2)
    logger.info(message)

def _on_error_occurred(self, error: str, suggestions: list):
    """错误发生回调"""
    logger.error(f"构建错误: {error}")

    # 构建错误消息
    msg = error
    if suggestions:
        msg += "\n\n建议操作:\n" + "\n".join(f"  • {s}" for s in suggestions)

    QMessageBox.critical(self, "❌ 构建失败", msg)
```

**4. BuildContext 和 StageResult** (确保存在于 models.py)
```python
# src/core/models.py - 确保这些类存在

@dataclass
class BuildContext:
    """构建上下文 - 在阶段间传递状态

    Architecture Decision 1.2:
    - config: 只读全局配置
    - state: 可写阶段状态 (用于传递)
    - log_callback: 统一日志接口
    """
    config: dict = None
    state: dict = _empty_dict_factory
    log_callback: callable = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}

class StageStatus(Enum):
    """阶段执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class StageResult:
    """阶段执行结果

    Architecture Decision 1.2:
    - status: 执行状态
    - message: 状态消息
    - output_files: 输出文件列表
    - error: 异常对象 (如果失败)
    - suggestions: 修复建议列表
    """
    status: StageStatus = StageStatus.PENDING
    message: str = ""
    output_files: list = None
    error: Exception = None
    suggestions: list = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.suggestions is None:
            self.suggestions = []
```

### 测试要求

**单元测试** (Task 1.4, Task 8):
```python
# tests/unit/test_workflow_execution.py

import pytest
from unittest.mock import Mock, patch
from core.workflow import execute_workflow
from core.models import WorkflowConfig, StageConfig, BuildContext, StageStatus

def test_execute_workflow_with_no_stages():
    """测试没有启用阶段的情况"""
    config = WorkflowConfig(stages=[])
    context = BuildContext()

    result = execute_workflow(config, context)

    assert result is False

def test_execute_workflow_progress_callback():
    """测试进度回调"""
    stages = [
        StageConfig(name="test_stage", enabled=True)
    ]
    config = WorkflowConfig(stages=stages)
    context = BuildContext()

    progress_mock = Mock()
    execute_workflow(config, context, progress_callback=progress_mock)

    # 验证进度回调被调用
    assert progress_mock.call_count > 0

def test_workflow_thread_signals():
    """测试工作流线程信号发射"""
    from ui.main_window import WorkflowThread
    from core.models import ProjectConfig, WorkflowConfig

    project_config = ProjectConfig(name="Test")
    workflow_config = WorkflowConfig(stages=[])

    thread = WorkflowThread(project_config, workflow_config)

    # Mock 信号连接
    progress_mock = Mock()
    thread.progress_update.connect(progress_mock)

    # 运行线程
    thread.run()

    # 验证信号发射
    assert thread.finished.emit.called
```

### 依赖关系

**本Story依赖:**
- Story 2.1 (工作流模板选择) - 完成 ✅
- Story 2.2 (自定义工作流加载) - 完成 ✅
- Story 2.3 (工作流配置验证) - 完成 ✅

**本Story为后续Story奠定基础:**
- Story 2.5-2.12: 具体阶段实现 (依赖本Story的执行框架)
- Story 3.1-3.3: 监控与反馈功能 (依赖本Story的信号机制)

### 已知限制

1. **占位阶段实现**: 本Story中的阶段执行是占位实现，实际功能由后续Story (2.5-2.12) 实现

2. **日志查看器**: 本Story假设日志显示功能已存在（或简单使用 logger），完整日志查看器在 Story 3.2 实现

3. **进度面板**: 本Story使用状态栏显示进度，完整进度面板在 Story 3.1 实现

### 参考资料

**架构文档相关章节:**
- Decision 2.1: MATLAB 进程管理策略
- Decision 2.2: 进程管理器架构
- Decision 3.1: PyQt6 线程 + 信号模式
- Decision 1.1: 阶段接口模式
- 项目结构: `src/stages/` 目录组织

**PRD相关需求:**
- FR-010: 用户可以启动自动化构建流程
- FR-011: 系统可以按顺序执行工作流中定义的阶段
- FR-046: 用户可以取消正在执行的构建

### 实现检查清单

在完成Story后，确认以下项目:

- [ ] WorkflowThread 类已创建并正确继承 QThread
- [ ] 所有信号使用 pyqtSignal 正确定义
- [ ] UI 信号连接使用 Qt.ConnectionType.QueuedConnection
- [ ] execute_workflow() 使用 time.monotonic() 记录时间
- [ ] BuildContext 正确用于阶段间状态传递
- [ ] _lock_config_ui() 和 _unlock_config_ui() 已实现
- [ ] _is_building 标志防止重复启动
- [ ] 取消按钮功能已实现
- [ ] 错误对话框包含可操作的建议
- [ ] 单元测试覆盖关键路径
- [ ] 日志记录使用 logging 模块 (不用 print)

## Dev Agent Record

### Agent Model Used

claude-opus-4-5-20251101

### Debug Log References

### Completion Notes List

- Story 创建时间: 2026-02-09
- 实现完成时间: 2026-02-11
- 前序Story完成情况: Epic 2 的 Stories 2.1-2.3 已完成

**实现内容:**
1. 创建了 WorkflowThread 类 (QThread) 用于后台执行工作流
2. 添加了 execute_workflow() 函数实现工作流编排逻辑
3. 实现了 UI 状态管理（锁定/解锁配置界面）
4. 实现了进度反馈机制（信号连接和回调）
5. 实现了错误处理和恢复功能
6. 实现了"取消构建"按钮功能
7. 集成了验证流程
8. 添加了单元测试

**技术决策:**
- 使用 time.monotonic() 而非 time.time() 记录时间，避免系统时间调整影响
- 使用 Qt.ConnectionType.QueuedConnection 确保跨线程信号安全
- 使用 dataclasses.field(default_factory=...) 避免可变默认值陷阱
- 使用 dataclasses.field 完整路径避免属性名冲突

**测试结果:**
- 所有单元测试通过 (196 passed, 3 skipped)
- 新增测试文件: tests/unit/test_workflow_execution.py

### File List

**修改的文件:**
- `src/ui/main_window.py` - 实现构建启动、UI状态管理、信号连接、WorkflowThread类
- `src/core/workflow.py` - 添加 execute_workflow() 函数
- `src/core/models.py` - 添加 BuildContext, StageResult, StageStatus 类

**创建的文件:**
- `src/core/constants.py` - 定义 DEFAULT_TIMEOUT 和 WORKFLOW_STAGE_ORDER
- `src/stages/__init__.py` - 阶段模块初始化
- `src/stages/base.py` - 阶段基类定义
- `tests/unit/test_workflow_execution.py` - 工作流执行单元测试
