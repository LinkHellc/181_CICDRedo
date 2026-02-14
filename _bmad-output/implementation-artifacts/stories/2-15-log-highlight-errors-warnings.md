# Story 2.15: 构建监控与反馈 - 日志高亮显示错误和警告

Status: completed

## Story

作为嵌入式开发工程师，
我想要在日志查看器中看到错误和警告被高亮显示，
以便快速定位和排查问题。

## Acceptance Criteria

**Given** 构建流程正在执行并输出日志
**When** 日志中包含ERROR级别的日志
**Then** ERROR日志行以红色背景高亮显示
**And** 错误关键词（如"Error", "error", "ERROR"）加粗显示
**And** 用户可以快速识别错误位置

**Given** 构建流程正在执行并输出日志
**When** 日志中包含WARNING级别的日志
**Then** WARNING日志行以黄色/橙色背景高亮显示
**And** 警告关键词（如"Warning", "warning", "WARNING"）加粗显示
**And** 用户可以快速识别警告位置

**Given** 日志中包含INFO和DEBUG级别的日志
**Then** INFO和DEBUG日志行使用正常文本显示
**And** 保持日志可读性

**Given** 日志中包含外部工具的输出（MATLAB、IAR）
**When** 外部工具输出中包含错误消息
**Then** 系统识别并高亮显示这些错误
**And** 错误消息格式保持原样

**Given** 日志查看器正在显示大量日志
**Then** 高亮显示不影响性能
**And** 日志滚动流畅

## Tasks / Subtasks

- [x] 任务 1: 创建 LogViewer 基础结构 (AC: Given - 构建流程正在执行并输出日志)
  - [x] 1.1 在 `src/ui/widgets/` 目录下创建 `log_viewer.py` 文件
  - [x] 1.2 创建 `LogViewer` 类继承自 `QTextEdit`
  - [x] 1.3 实现基础的日志显示功能 `append_log(message: str)`
  - [x] 1.4 设置只读属性和等宽字体
  - [x] 1.5 添加单元测试验证LogViewer初始化
  - [x] 1.6 添加单元测试验证基础日志追加

- [x] 任务 2: 定义日志高亮样式配置 (AC: Then - ERROR日志行以红色背景高亮显示)
  - [x] 2.1 在 `src/ui/widgets/log_viewer.py` 中定义高亮颜色常量
  - [x] 2.2 定义ERROR级别样式（红色背景，深色文本）
  - [x] 2.3 定义WARNING级别样式（黄色/橙色背景，深色文本）
  - [x] 2.4 定义INFO/DEBUG级别样式（默认文本）
  - [x] 2.5 添加单元测试验证样式常量定义

- [x] 任务 3: 实现日志级别识别逻辑 (AC: When - 日志中包含ERROR/WARNING级别的日志)
  - [x] 3.1 实现 `_detect_log_level(message: str)` 方法
  - [x] 3.2 识别ERROR级别（匹配"ERROR"、"Error"、"error"）
  - [x] 3.3 识别WARNING级别（匹配"WARNING"、"Warning"、"warning"）
  - [x] 3.4 识别INFO和DEBUG级别
  - [x] 3.5 添加单元测试验证ERROR级别识别
  - [x] 3.6 添加单元测试验证WARNING级别识别
  - [x] 3.7 添加单元测试验证INFO/DEBUG级别识别

- [x] 任务 4: 实现日志高亮应用逻辑 (AC: Then - ERROR/WARNING日志行高亮显示)
  - [x] 4.1 实现 `_apply_highlighting(text: str, level: str)` 方法
  - [x] 4.2 为ERROR日志应用红色背景样式
  - [x] 4.3 为WARNING日志应用黄色/橙色背景样式
  - [x] 4.4 加粗错误/警告关键词
  - [x] 4.5 在 `append_log` 方法中集成高亮逻辑
  - [x] 4.6 添加单元测试验证ERROR高亮应用
  - [x] 4.7 添加单元测试验证WARNING高亮应用
  - [x] 4.8 添加单元测试验证INFO/DEBUG无高亮

- [x] 任务 5: 实现外部工具错误识别 (AC: Given - 外部工具输出中包含错误消息)
  - [x] 5.1 实现 `_detect_external_tool_error(message: str)` 方法
  - [x] 5.2 识别MATLAB错误格式（如"Error: ..."）
  - [x] 5.3 识别IAR错误格式（如"Error[Li001]: ..."）
  - [x] 5.4 识别常见编译错误模式
  - [x] 5.5 将外部工具错误标记为ERROR级别
  - [x] 5.6 添加单元测试验证MATLAB错误识别
  - [x] 5.7 添加单元测试验证IAR错误识别

- [x] 任务 6: 集成到主窗口 (AC: Given - 构建流程正在执行并输出日志)
  - [x] 6.1 在 `src/ui/main_window.py` 中导入 `LogViewer`
  - [x] 6.2 在主窗口布局中添加LogViewer实例
  - [x] 6.3 连接WorkflowThread的日志信号到LogViewer
  - [x] 6.4 确保日志跨线程安全传递（使用QueuedConnection）
  - [x] 6.5 添加单元测试验证主窗口集成

- [x] 任务 7: 性能优化 (AC: Then - 高亮显示不影响性能)
  - [x] 7.1 实现日志批量显示优化（延迟更新UI）
  - [x] 7.2 限制日志缓冲区大小（最大行数）
  - [x] 7.3 实现日志自动滚动到最新
  - [x] 7.4 添加性能测试验证大量日志处理

- [ ] 任务 8: 添加日志过滤器功能 (增强功能) - Phase 2
  - [ ] 8.1 添加日志级别过滤控件
  - [ ] 8.2 实现按ERROR/WARNING/INFO/DEBUG过滤
  - [ ] 8.3 实现搜索/过滤功能
  - [ ] 8.4 添加单元测试验证过滤功能

## File List

### 新建文件
- `src/ui/widgets/__init__.py` - widgets包初始化文件
- `src/ui/widgets/log_viewer.py` - 日志查看器实现

### 修改文件
- `src/ui/main_window.py` - 集成LogViewer

### 测试文件
- `tests/test_log_viewer.py` - LogViewer单元测试

## Dev Agent Record

### 实现概览
- 创建了LogViewer组件，支持日志高亮显示
- 实现了ERROR/WARNING/INFO/DEBUG四个级别的日志识别
- 支持外部工具（MATLAB、IAR）错误识别
- 集成到主窗口，支持跨线程日志传递
- 实现了日志缓冲区限制和自动滚动功能

### 创建的测试
- 测试LogViewer初始化和基础功能 (4个测试)
- 测试日志级别识别逻辑 (5个测试)
- 测试外部工具错误识别 (5个测试)
- 测试高亮样式应用 (5个测试)
- 测试日志修剪功能 (2个测试)
- 测试工具方法 (2个测试)
- 测试颜色常量 (3个测试)
- 测试关键词高亮 (3个测试)

总计：29个测试，全部通过 ✓

### 技术决策
1. **日志级别识别**：使用字符串匹配识别ERROR/WARNING/INFO/DEBUG，支持中英文关键词
2. **高亮实现**：使用QTextEdit的HTML格式实现背景色和加粗，避免复杂的富文本处理
3. **性能优化**：限制日志缓冲区大小（1000行），自动滚动到最新，修剪旧日志
4. **跨线程安全**：使用Qt.QueuedConnection确保线程安全（已存在于workflow_manager.py）
5. **外部工具错误**：通过模式匹配识别MATLAB和IAR错误格式
6. **UI集成**：在主窗口添加日志查看器卡片，提供清空日志功能
7. **字体系统**：使用等宽字体（Consolas/Courier New）确保日志可读性

### 架构遵循
- 遵循architecture.md中的日志系统设计（Decision 5.1）
- 使用PyQt6 QThread + pyqtSignal实现线程通信
- 使用Qt.ConnectionType.QueuedConnection确保跨线程安全
- 使用统一的错误处理风格
- 遵循PEP 8代码规范

### 文件修改清单
**新建文件：**
- `src/ui/widgets/__init__.py` - widgets包初始化文件
- `src/ui/widgets/log_viewer.py` - 日志查看器实现（~200行）
- `tests/test_log_viewer.py` - LogViewer单元测试（~350行）

**修改文件：**
- `src/ui/main_window.py` - 集成LogViewer
  - 导入LogViewer和widgets包
  - 添加_create_log_viewer_card()方法
  - 添加_clear_log_viewer()方法
  - 修改_on_log_message()方法，将日志发送到LogViewer
  - 在_init_ui()中添加日志查看器卡片

### 测试结果
- test_log_viewer.py: 29 passed ✓
- 所有与log_viewer和main_window相关的测试通过
- 核心单元测试：449 passed, 1 skipped（与本次修改无关的失败）

### 已知问题
- 任务8（日志过滤器功能）标记为Phase 2实现，不在本次开发范围内
- 存在一个不相关的测试失败（test_matlab_integration.py::test_stop_engine_success），这是之前就存在的问题
