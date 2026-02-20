# Story 3.4: 构建历史记录和查看

Status: planned

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要查看历史构建记录，
以便追溯之前的构建结果、对比不同构建的性能，以及诊断历史问题。

## Acceptance Criteria

**Given** 用户打开主窗口
**When** 用户点击"构建历史"按钮或菜单项
**Then** 系统显示构建历史列表（显示构建 ID、时间、状态、总耗时）
**When** 用户选择一个历史构建记录
**Then** 系统显示该构建的详细信息：
  - 构建配置（项目路径、工作流配置）
  - 各阶段执行时间和状态
  - 构建日志（可查看完整日志）
  - 构建产物文件（HEX、A2L 等文件路径）
**When** 用户选择两个历史构建记录
**Then** 系统显示对比信息（性能对比、配置差异等）

## Tasks / Subtasks

- [ ] 任务 1: 创建构建历史数据模型 (AC: Then - 系统显示构建历史列表)
  - [ ] 1.1 在 `src/core/models.py` 中创建 `BuildHistoryEntry` 数据类
  - [ ] 1.2 添加字段：build_id（构建唯一标识，UUID）
  - [ ] 1.3 添加字段：timestamp（构建时间戳，ISO 8601 格式）
  - [ ] 1.4 添加字段：project_name（项目名称）
  - [ ] 1.5 添加字段：project_path（项目路径）
  - [ ] 1.6 添加字段：workflow_config（工作流配置字典）
  - [ ] 1.7 添加字段：stage_times（各阶段执行时间列表）
  - [ ] 1.8 添加字段：total_duration（总耗时，秒）
  - [ ] 1.9 添加字段：status（状态：success、failed、cancelled）
  - [ ] 1.10 添加字段：artifact_paths（产物文件路径列表）
  - [ ] 1.11 添加字段：log_file_path（日志文件路径）
  - [ ] 1.12 添加 `to_dict()` 方法用于序列化
  - [ ] 1.13 添加 `from_dict()` 类方法用于反序列化
  - [ ] 1.14 添加单元测试验证数据类创建
  - [ ] 1.15 添加单元测试验证序列化/反序列化

- [ ] 任务 2: 创建构建历史管理器 (AC: All)
  - [ ] 2.1 在 `src/utils/build_history.py` 中创建 `BuildHistoryManager` 类
  - [ ] 2.2 实现构造函数，初始化历史文件路径（`%APPDATA%/MBD_CICDKits/build_history.json`）
  - [ ] 2.3 实现 `add_entry()` 方法：添加新的构建记录
  - [ ] 2.4 实现 `get_all_entries()` 方法：获取所有构建记录
  - [ ] 2.5 实现 `get_entry_by_id()` 方法：根据 build_id 获取记录
  - [ ] 2.6 实现 `delete_entry()` 方法：删除指定构建记录
  - [ ] 2.7 实现 `clear_all_entries()` 方法：清空所有历史记录
  - [ ] 2.8 实现 `search_entries()` 方法：按条件搜索（项目名、时间范围、状态）
  - [ ] 2.9 实现记录数量限制（最多保存 100 条，使用 FIFO 策略）
  - [ ] 2.10 实现原子写入（先写入临时文件，再重命名）
  - [ ] 2.11 添加单元测试验证添加记录
  - [ ] 2.12 添加单元测试验证查询记录
  - [ ] 2.13 添加单元测试验证删除记录
  - [ ] 2.14 添加单元测试验证搜索功能
  - [ ] 2.15 添加单元测试验证记录数量限制
  - [ ] 2.16 添加单元测试验证原子写入

- [ ] 任务 3: 在 WorkflowThread 中集成构建历史记录 (AC: All)
  - [ ] 3.1 在 `src/core/workflow_thread.py` 中添加 `build_history_manager` 属性
  - [ ] 3.2 在工作流开始时生成唯一的 build_id（使用 uuid4）
  - [ ] 3.3 在工作流开始时创建 `BuildHistoryEntry` 对象
  - [ ] 3.4 在工作流完成时更新 entry 的状态（success/failed/cancelled）
  - [ ] 3.5 在工作流完成时更新 entry 的 stage_times 和 total_duration
  - [ ] 3.6 在工作流完成时更新 entry 的 artifact_paths（从结果中提取）
  - [ ] 3.7 在工作流完成时记录日志文件路径
  - [ ] 3.8 在工作流完成时调用 `build_history_manager.add_entry()` 保存记录
  - [ ] 3.9 添加单元测试验证记录创建时机
  - [ ] 3.10 添加单元测试验证记录更新逻辑
  - [ ] 3.11 添加单元测试验证保存逻辑

- [ ] 任务 4: 创建构建历史列表 UI 组件 (AC: When - 用户点击"构建历史"按钮或菜单项)
  - [ ] 4.1 在 `src/ui/widgets/build_history_list.py` 中创建 `BuildHistoryList` 类（继承 QWidget）
  - [ ] 4.2 添加 QTableWidget 用于显示历史列表
  - [ ] 4.3 定义列：构建 ID、时间、项目名称、状态、总耗时
  - [ ] 4.4 实现初始化方法，连接到 BuildHistoryManager
  - [ ] 4.5 实现 `refresh_list()` 方法：加载并显示所有构建记录
  - [ ] 4.6 实现状态列的颜色显示（success=绿色、failed=红色、cancelled=灰色）
  - [ ] 4.7 实现时间格式化（显示可读格式，如 "2024-02-20 14:30"）
  - [ ] 4.8 实现耗时格式化（秒、分:秒、时:分:秒）
  - [ ] 4.9 添加右键菜单（查看详情、删除、导出）
  - [ ] 4.10 添加搜索框（按项目名、构建 ID 搜索）
  - [ ] 4.11 添加日期范围筛选器
  - [ ] 4.12 实现列表排序功能（按时间、耗时、状态）
  - [ ] 4.13 添加单元测试验证组件创建
  - [ ] 4.14 添加单元测试验证列表刷新
  - [ ] 4.15 添加单元测试验证搜索和筛选

- [ ] 任务 5: 创建构建详情面板 UI 组件 (AC: When - 用户选择一个历史构建记录)
  - [ ] 5.1 在 `src/ui/widgets/build_detail_panel.py` 中创建 `BuildDetailPanel` 类（继承 QWidget）
  - [ ] 5.2 添加构建信息标签区域（显示构建 ID、时间、状态、总耗时）
  - [ ] 5.3 添加 QTabWidget 用于组织详细信息
  - [ ] 5.4 实现"配置"标签页：显示项目路径、工作流配置（使用 QTreeWidget 或 JSON 格式化显示）
  - [ ] 5.5 实现"阶段时间"标签页：显示各阶段执行时间和状态（使用 QTableWidget）
  - [ ] 5.6 实现"构建日志"标签页：显示完整构建日志（复用 LogViewer）
  - [ ] 5.7 实现"产物文件"标签页：显示产物文件路径列表（使用 QListWidget）
  - [ ] 5.8 为产物文件添加"打开所在文件夹"和"打开文件"功能
  - [ ] 5.9 实现 `load_build_details()` 方法：加载并显示构建详情
  - [ ] 5.10 添加"导出详情"按钮（支持导出为 JSON、Markdown）
  - [ ] 5.11 添加单元测试验证组件创建
  - [ ] 5.12 添加单元测试验证详情加载
  - [ ] 5.13 添加单元测试验证标签页显示

- [ ] 任务 6: 创建构建对比面板 UI 组件 (AC: When - 用户选择两个历史构建记录)
  - [ ] 6.1 在 `src/ui/widgets/build_comparison_panel.py` 中创建 `BuildComparisonPanel` 类（继承 QWidget）
  - [ ] 6.2 添加选择器（两个 QComboBox 用于选择要对比的构建）
  - [ ] 6.3 添加 QTabWidget 用于组织对比信息
  - [ ] 6.4 实现"性能对比"标签页：显示总耗时、各阶段耗时对比（使用 QTableWidget）
  - [ ] 6.5 实现"配置差异"标签页：显示工作流配置差异（使用文本对比视图）
  - [ ] 6.6 添加性能变化百分比计算和显示（提升=绿色、下降=红色）
  - [ ] 6.7 添加阶段耗时对比图表（使用 QBarSeries）
  - [ ] 6.8 实现 `load_comparison()` 方法：加载并显示对比信息
  - [ ] 6.9 添加"导出对比报告"按钮（支持导出为 CSV、Markdown、HTML）
  - [ ] 6.10 添加单元测试验证组件创建
  - [ ] 6.11 添加单元测试验证对比计算
  - [ ] 6.12 添加单元测试验证对比显示

- [ ] 任务 7: 在主窗口中集成构建历史功能 (AC: When - 用户点击"构建历史"按钮或菜单项)
  - [ ] 7.1 在 `src/ui/main_window.py` 中添加"构建历史"菜单项或按钮
  - [ ] 7.2 创建 `BuildHistoryDialog` 对话框（继承 QDialog）
  - [ ] 7.3 在对话框中创建 `BuildHistoryList` 实例
  - [ ] 7.4 在对话框中创建 `BuildDetailPanel` 实例（初始隐藏）
  - [ ] 7.5 在对话框中创建 `BuildComparisonPanel` 实例（初始隐藏）
  - [ ] 7.6 实现对话框布局（左侧历史列表，右侧详情/对比面板）
  - [ ] 7.7 连接列表选择信号到详情面板加载
  - [ ] 7.8 实现双击列表项显示详情
  - [ ] 7.9 实现 Ctrl+双击列表项显示对比（与上次选择的对比）
  - [ ] 7.10 添加"返回列表"按钮（从详情/对比视图返回）
  - [ ] 7.11 添加单元测试验证对话框创建
  - [ ] 7.12 添加单元测试验证信号连接
  - [ ] 7.13 添加集成测试验证完整交互流程

- [ ] 任务 8: 实现构建历史持久化 (AC: All)
  - [ ] 8.1 在 `src/utils/build_history.py` 中实现历史记录的文件持久化
  - [ ] 8.2 使用 JSON 格式保存构建历史
  - [ ] 8.3 文件路径：`%APPDATA%/MBD_CICDKits/build_history.json`
  - [ ] 8.4 实现原子写入（写入临时文件 `.tmp`，完成后重命名）
  - [ ] 8.5 实现文件备份（每次写入前备份到 `.bak`）
  - [ ] 8.6 实现文件损坏恢复（检测损坏时使用备份恢复）
  - [ ] 8.7 添加 JSON schema 验证（确保数据结构正确）
  - [ ] 8.8 添加数据迁移支持（支持版本升级）
  - [ ] 8.9 添加单元测试验证文件写入
  - [ ] 8.10 添加单元测试验证原子写入
  - [ ] 8.11 添加单元测试验证备份和恢复
  - [ ] 8.12 添加单元测试验证损坏恢复

- [ ] 任务 9: 实现构建历史搜索和筛选 (AC: Then - 系统显示构建历史列表)
  - [ ] 9.1 在 `src/utils/build_history.py` 中实现搜索逻辑
  - [ ] 9.2 支持按项目名称搜索（模糊匹配）
  - [ ] 9.3 支持按构建 ID 搜索（精确匹配）
  - [ ] 9.4 支持按时间范围筛选（开始日期、结束日期）
  - [ ] 9.5 支持按状态筛选（success、failed、cancelled）
  - [ ] 9.6 支持组合条件搜索
  - [ ] 9.7 在 UI 中实时更新搜索结果
  - [ ] 9.8 添加单元测试验证搜索逻辑
  - [ ] 9.9 添加单元测试验证筛选逻辑
  - [ ] 9.10 添加集成测试验证 UI 搜索体验

- [ ] 任务 10: 实现构建历史导出功能 (AC: All)
  - [ ] 10.1 在 `src/utils/build_history_exporter.py` 中创建 `BuildHistoryExporter` 类
  - [ ] 10.2 实现导出为 CSV 格式（包含所有字段）
  - [ ] 10.3 实现导出为 JSON 格式（完整数据结构）
  - [ ] 10.4 实现导出为 Markdown 格式（可读性好）
  - [ ] 10.5 实现导出为 HTML 格式（包含表格和样式）
  - [ ] 10.6 支持导出单个构建详情
  - [ ] 10.7 支持导出构建对比结果
  - [ ] 10.8 支持批量导出（选中的多条记录）
  - [ ] 10.9 在主窗口和详情面板中添加"导出"按钮
  - [ ] 10.10 添加单元测试验证 CSV 导出
  - [ ] 10.11 添加单元测试验证 JSON 导出
  - [ ] 10.12 添加单元测试验证 Markdown 导出
  - [ ] 10.13 添加单元测试验证 HTML 导出

- [ ] 任务 11: 实现构建历史统计功能 (AC: All)
  - [ ] 11.1 在 `src/utils/build_history_stats.py` 中创建 `BuildHistoryStats` 类
  - [ ] 11.2 实现总构建次数统计
  - [ ] 11.3 实现成功率计算（success / total）
  - [ ] 11.4 实现平均构建耗时计算
  - [ ] 11.5 实现最快/最慢构建统计
  - [ ] 11.6 实现最近7天/30天构建趋势
  - [ ] 11.7 实现按项目分组统计
  - [ ] 11.8 实现按失败原因分组统计
  - [ ] 11.9 在历史列表对话框中添加"统计"标签页
  - [ ] 11.10 使用图表（QBarSeries、QLineSeries）可视化统计数据
  - [ ] 11.11 添加单元测试验证统计计算
  - [ ] 11.12 添加集成测试验证统计显示

- [ ] 任务 12: 实现构建产物文件管理 (AC: Then - 系统显示该构建的详细信息 - 构建产物文件)
  - [ ] 12.1 在 `src/core/models.py` 中扩展 `BuildHistoryEntry` 数据类
  - [ ] 12.2 在 `BuildHistoryEntry` 中添加 `artifact_metadata` 字段（文件大小、创建时间）
  - [ ] 12.3 实现产物文件验证（检查文件是否存在）
  - [ ] 12.4 实现产物文件图标显示（根据文件类型显示不同图标）
  - [ ] 12.5 实现"打开所在文件夹"功能
  - [ ] 12.6 实现"复制路径"功能
  - [ ] 12.7 实现产物文件缺失时的警告显示
  - [ ] 12.8 添加单元测试验证产物文件验证
  - [ ] 12.9 添加集成测试验证文件操作

- [ ] 任务 13: 实现构建日志查看功能 (AC: Then - 系统显示该构建的详细信息 - 构建日志)
  - [ ] 13.1 在 `src/ui/widgets/build_detail_panel.py` 中集成 `LogViewer` 组件
  - [ ] 13.2 实现从日志文件路径加载日志内容
  - [ ] 13.3 支持大日志文件的分页加载（避免内存问题）
  - [ ] 13.4 支持日志内容搜索
  - [ ] 13.5 支持错误和警告日志过滤
  - [ ] 13.6 实现"导出日志"功能
  - [ ] 13.7 添加日志文件缺失时的错误提示
  - [ ] 13.8 添加单元测试验证日志加载
  - [ ] 13.9 添加单元测试验证日志搜索
  - [ ] 13.10 添加集成测试验证大日志处理

- [ ] 任务 14: 添加构建历史数据迁移功能 (AC: All)
  - [ ] 14.1 在 `src/utils/build_history.py` 中实现数据版本管理
  - [ ] 14.2 在历史记录 JSON 中添加 `version` 字段
  - [ ] 14.3 实现版本 1 → 版本 2 迁移逻辑
  - [ ] 14.4 实现版本 2 → 版本 3 迁移逻辑
  - [ ] 14.5 在加载历史记录时自动检测版本并迁移
  - [ ] 14.6 迁移前备份原始数据
  - [ ] 14.7 添加迁移日志记录
  - [ ] 14.8 添加单元测试验证版本 1 迁移
  - [ ] 14.9 添加单元测试验证版本 2 迁移
  - [ ] 14.10 添加集成测试验证自动迁移

- [ ] 任务 15: 添加集成测试 (AC: All)
  - [ ] 15.1 创建 `tests/integration/test_build_history.py`
  - [ ] 15.2 测试完整的构建历史记录流程（从构建开始到保存历史）
  - [ ] 15.3 测试构建历史列表加载和显示
  - [ ] 15.4 测试构建详情查看
  - [ ] 15.5 测试构建对比功能
  - [ ] 15.6 测试搜索和筛选功能
  - [ ] 15.7 测试导出功能（各格式）
  - [ ] 15.8 测试统计功能
  - [ ] 15.9 测试产物文件管理
  - [ ] 15.10 测试日志查看功能
  - [ ] 15.11 测试数据迁移功能
  - [ ] 15.12 测试并发构建的历史记录隔离
  - [ ] 15.13 测试大量历史记录（100+）的性能
  - [ ] 15.14 测试历史记录损坏恢复

## Dev Notes

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **ADR-003（可观测性）**：构建历史是关键的可观测性功能，用于追溯和诊断
- **Decision 3.1（PyQt6 线程 + 信号模式）**：使用 QThread + pyqtSignal，跨线程必须使用 `Qt.ConnectionType.QueuedConnection`
- **Decision 4.1（原子性数据传递）**：使用数据类（BuildHistoryEntry）传递构建历史数据
- **Decision 5.1（日志框架）**：构建历史关联日志文件，使用统一日志级别
- **数据持久化规则**：使用原子写入和备份机制确保数据完整性

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 数据完整性：构建历史必须使用原子写入和备份机制
2. ⭐⭐⭐⭐⭐ 构建ID：使用 UUID 确保唯一性，不依赖时间戳
3. ⭐⭐⭐⭐⭐ 记录数量：最多保存 100 条记录，使用 FIFO 策略
4. ⭐⭐⭐⭐⭐ 信号连接：跨线程信号必须使用 `Qt.ConnectionType.QueuedConnection`
5. ⭐⭐⭐⭐ 时间戳：使用 ISO 8601 格式存储，便于排序和查询
6. ⭐⭐⭐⭐ 数据验证：加载历史记录时必须验证 JSON schema
7. ⭐⭐⭐⭐ 文件路径：产物文件和日志文件路径使用绝对路径
8. ⭐⭐⭐ 原子写入：写入临时文件后重命名，避免数据损坏
9. ⭐⭐⭐ 备份恢复：每次写入前备份，损坏时自动恢复
10. ⭐⭐⭐ 数据迁移：支持版本升级，保证向后兼容

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/core/models.py` | 修改 | 添加 `BuildHistoryEntry` 数据类 |
| `src/core/workflow_thread.py` | 修改 | 集成构建历史记录 |
| `src/ui/main_window.py` | 修改 | 添加构建历史菜单和对话框 |
| `src/ui/widgets/build_history_list.py` | 新建 | 构建历史列表 UI 组件 |
| `src/ui/widgets/build_detail_panel.py` | 新建 | 构建详情面板 UI 组件 |
| `src/ui/widgets/build_comparison_panel.py` | 新建 | 构建对比面板 UI 组件 |
| `src/utils/build_history.py` | 新建 | 构建历史管理器 |
| `src/utils/build_history_exporter.py` | 新建 | 构建历史导出工具 |
| `src/utils/build_history_stats.py` | 新建 | 构建历史统计工具 |
| `tests/unit/test_build_history_models.py` | 新建 | 构建历史模型单元测试 |
| `tests/unit/test_build_history_manager.py` | 新建 | 构建历史管理器单元测试 |
| `tests/integration/test_build_history.py` | 新建 | 构建历史集成测试 |

**确保符合项目结构**：
```
src/
├── core/                                     # 核心业务逻辑（函数）
│   ├── models.py                            # 数据模型（修改）
│   └── workflow_thread.py                   # 工作流执行线程（修改）
├── ui/                                      # PyQt6 UI（类）
│   ├── main_window.py                       # 主窗口（修改）
│   └── widgets/                             # 自定义控件
│       ├── build_history_list.py            # 构建历史列表（新建）
│       ├── build_detail_panel.py             # 构建详情面板（新建）
│       └── build_comparison_panel.py         # 构建对比面板（新建）
└── utils/                                   # 工具函数
    ├── build_history.py                     # 构建历史管理（新建）
    ├── build_history_exporter.py            # 构建历史导出（新建）
    └── build_history_stats.py               # 构建历史统计（新建）
tests/
├── unit/
│   ├── test_build_history_models.py         # 构建历史模型测试（新建）
│   └── test_build_history_manager.py        # 构建历史管理器测试（新建）
└── integration/
    └── test_build_history.py                # 构建历史集成测试（新建）
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| PyQt6 | 6.0+ | UI 框架（QWidget, QDialog, QTableWidget, QTreeWidget, QTabWidget, QComboBox, pyqtSignal） |
| PyQt6-Charts | 6.0+ | 图表库（QBarSeries, QLineSeries, QChartView） |
| dataclasses | 内置 | 数据类定义 |
| uuid | 内置 | 构建ID生成（uuid4） |
| json | 内置 | 历史记录持久化 |
| jsonschema | 3.0+ | JSON schema 验证 |
| pathlib | 内置 | 文件路径处理 |
| csv | 内置 | CSV 导出 |
| datetime | 内置 | 时间戳格式化 |
| typing | 内置 | 类型提示 |
| shutil | 内置 | 文件备份和重命名 |

### 测试标准

**单元测试要求**：
- 测试 `BuildHistoryEntry` 数据类创建和序列化
- 测试构建历史管理器的添加、查询、删除功能
- 测试搜索和筛选逻辑（项目名、时间范围、状态）
- 测试记录数量限制（100条 FIFO）
- 测试原子写入和备份恢复机制
- 测试数据迁移功能
- 测试构建历史列表 UI 组件
- 测试构建详情面板 UI 组件
- 测试构建对比面板 UI 组件
- 测试导出功能（CSV、JSON、Markdown、HTML）
- 测试统计功能计算
- 测试产物文件验证
- 测试日志加载和搜索

**集成测试要求**：
- 测试完整的构建历史记录流程（从构建开始到保存）
- 测试构建历史列表加载和显示
- 测试构建详情查看（配置、阶段时间、日志、产物）
- 测试构建对比功能（性能对比、配置差异）
- 测试搜索和筛选交互
- 测试导出功能（各格式）
- 测试统计功能和图表显示
- 测试产物文件操作（打开文件夹、复制路径）
- 测试日志查看功能（大文件、搜索、过滤）
- 测试并发构建的历史记录隔离
- 测试大量历史记录（100+）的性能
- 测试历史记录损坏恢复
- 测试数据迁移（版本 1 → 版本 2）

**端到端测试要求**：
- 测试从构建开始到历史查看的完整流程
- 测试多项目构建的历史隔离
- 测试历史记录在不同应用重启后的持久性
- 测试构建失败和取消时的历史记录
- 测试长时间运行应用的历史记录稳定性

### 依赖关系

**前置故事**：
- ✅ Epic 1 全部完成（项目配置管理）
- ✅ Story 2.4: 启动自动化构建流程（工作流执行框架）
- ✅ Story 3.1: 实时显示构建进度（进度面板和信号机制）
- ✅ Story 3.2: 实时显示构建日志输出（日志捕获和显示）
- ✅ Story 3.3: 记录并显示阶段执行时间（阶段时间记录和汇总）

**后续故事**：
- Story 4.3: 导出构建历史记录（可复用导出逻辑）
- Story 4.4: 生成构建性能报告（可复用统计和对比逻辑）

### 数据流设计

```
工作流开始执行
    │
    ▼
WorkflowThread.run()
    │
    ▼
生成构建ID（uuid.uuid4()）
    │
    ▼
创建 BuildHistoryEntry 对象
    │   ├─> build_id: UUID
    │   ├─> timestamp: 当前时间
    │   ├─> project_name: 项目名称
    │   ├─> project_path: 项目路径
    │   └─> workflow_config: 工作流配置
    │
    ▼
执行各阶段（记录阶段时间，见 Story 3.3）
    │
    ▼
工作流完成或失败
    │
    ▼
更新 BuildHistoryEntry
    │   ├─> status: success / failed / cancelled
    │   ├─> stage_times: 各阶段执行时间
    │   ├─> total_duration: 总耗时
    │   ├─> artifact_paths: 产物文件路径
    │   └─> log_file_path: 日志文件路径
    │
    ▼
调用 BuildHistoryManager.add_entry()
    │
    ▼
BuildHistoryManager.add_entry()
    │
    ├─→ 加载现有历史记录
    │
    ├─→ 添加新记录
    │
    ├─→ 检查记录数量（>100则删除最旧的）
    │
    ├─→ 序列化为 JSON
    │
    ├─→ 备份现有文件（.bak）
    │
    ├─→ 原子写入（先写 .tmp，再重命名）
    │
    └─→ 验证写入成功
    │
    ▼
...（下次用户查看历史时）
    │
    ▼
用户点击"构建历史"按钮
    │
    ▼
打开 BuildHistoryDialog
    │
    ▼
BuildHistoryList.refresh_list()
    │
    ├─→ 调用 BuildHistoryManager.get_all_entries()
    │
    ├─→ 填充表格（构建ID、时间、项目、状态、耗时）
    │
    └─→ 应用排序和筛选
    │
    ▼
用户选择一条构建记录
    │
    ▼
BuildDetailPanel.load_build_details(entry)
    │
    ├─→ 显示配置标签页
    ├─→ 显示阶段时间标签页
    ├─→ 加载并显示日志
    └─→ 显示产物文件列表
    │
    ▼
用户选择两条构建记录
    │
    ▼
BuildComparisonPanel.load_comparison(entry1, entry2)
    │
    ├─→ 显示性能对比标签页
    ├─→ 显示配置差异标签页
    └─→ 生成对比图表
```

### 构建历史数据结构

**BuildHistoryEntry 数据类**：
```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime

class BuildStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ArtifactInfo:
    """产物文件信息"""
    path: str                          # 文件路径（绝对路径）
    file_type: str                     # 文件类型（hex, a2l, 等）
    size: int                          # 文件大小（字节）
    created_at: Optional[str] = None   # 创建时间（ISO 8601）

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "file_type": self.file_type,
            "size": self.size,
            "created_at": self.created_at
        }

@dataclass
class BuildHistoryEntry:
    """构建历史记录"""
    build_id: str                      # 构建唯一标识（UUID）
    timestamp: str                     # 构建时间戳（ISO 8601）
    project_name: str                  # 项目名称
    project_path: str                  # 项目路径（绝对路径）
    workflow_config: Dict              # 工作流配置
    stage_times: List[Dict]            # 各阶段执行时间列表
    total_duration: float               # 总耗时（秒）
    status: BuildStatus                # 构建状态
    artifact_paths: List[ArtifactInfo] # 产物文件路径列表
    log_file_path: Optional[str] = None # 日志文件路径
    error_message: Optional[str] = None # 错误信息（失败时）

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "build_id": self.build_id,
            "timestamp": self.timestamp,
            "project_name": self.project_name,
            "project_path": self.project_path,
            "workflow_config": self.workflow_config,
            "stage_times": self.stage_times,
            "total_duration": self.total_duration,
            "status": self.status.value,
            "artifact_paths": [a.to_dict() for a in self.artifact_paths],
            "log_file_path": self.log_file_path,
            "error_message": self.error_message
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BuildHistoryEntry':
        """从字典反序列化"""
        artifact_paths = [
            ArtifactInfo(**a) for a in data.get("artifact_paths", [])
        ]

        return cls(
            build_id=data["build_id"],
            timestamp=data["timestamp"],
            project_name=data["project_name"],
            project_path=data["project_path"],
            workflow_config=data["workflow_config"],
            stage_times=data["stage_times"],
            total_duration=data["total_duration"],
            status=BuildStatus(data["status"]),
            artifact_paths=artifact_paths,
            log_file_path=data.get("log_file_path"),
            error_message=data.get("error_message")
        )
```

### 构建历史管理器实现

**BuildHistoryManager 类**：
```python
import json
import logging
import uuid
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import asdict

logger = logging.getLogger(__name__)

class BuildHistoryManager:
    """构建历史管理器"""

    def __init__(self, history_file_path: Path):
        """
        初始化构建历史管理器

        Args:
            history_file_path: 历史记录文件路径
        """
        self.history_file_path = history_file_path
        self.max_entries = 100
        self._version = 2  # 数据版本

        # 确保目录存在
        self.history_file_path.parent.mkdir(parents=True, exist_ok=True)

    def add_entry(self, entry: BuildHistoryEntry) -> bool:
        """
        添加构建记录

        Args:
            entry: 构建记录对象

        Returns:
            bool: 成功返回 True
        """
        try:
            # 加载现有记录
            entries = self._load_all_entries()

            # 添加新记录
            entries.append(entry)

            # 应用 FIFO 策略（保留最新的100条）
            if len(entries) > self.max_entries:
                entries = entries[-self.max_entries:]

            # 保存记录
            self._save_all_entries(entries)

            logger.info(f"构建记录已添加: {entry.build_id}")
            return True

        except Exception as e:
            logger.error(f"添加构建记录失败: {e}")
            return False

    def get_all_entries(self) -> List[BuildHistoryEntry]:
        """
        获取所有构建记录

        Returns:
            List[BuildHistoryEntry]: 构建记录列表
        """
        try:
            return self._load_all_entries()
        except Exception as e:
            logger.error(f"加载构建记录失败: {e}")
            return []

    def get_entry_by_id(self, build_id: str) -> Optional[BuildHistoryEntry]:
        """
        根据 build_id 获取构建记录

        Args:
            build_id: 构建ID

        Returns:
            Optional[BuildHistoryEntry]: 构建记录对象，不存在返回 None
        """
        entries = self.get_all_entries()

        for entry in entries:
            if entry.build_id == build_id:
                return entry

        return None

    def delete_entry(self, build_id: str) -> bool:
        """
        删除构建记录

        Args:
            build_id: 构建ID

        Returns:
            bool: 成功返回 True
        """
        try:
            # 加载现有记录
            entries = self._load_all_entries()

            # 删除指定记录
            original_count = len(entries)
            entries = [e for e in entries if e.build_id != build_id]

            if len(entries) == original_count:
                logger.warning(f"未找到构建记录: {build_id}")
                return False

            # 保存记录
            self._save_all_entries(entries)

            logger.info(f"构建记录已删除: {build_id}")
            return True

        except Exception as e:
            logger.error(f"删除构建记录失败: {e}")
            return False

    def clear_all_entries(self) -> bool:
        """
        清空所有构建记录

        Returns:
            bool: 成功返回 True
        """
        try:
            # 备份现有文件
            self._backup_file()

            # 清空文件
            self._save_all_entries([])

            logger.info("所有构建记录已清空")
            return True

        except Exception as e:
            logger.error(f"清空构建记录失败: {e}")
            return False

    def search_entries(
        self,
        project_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[BuildHistoryEntry]:
        """
        按条件搜索构建记录

        Args:
            project_name: 项目名称（模糊匹配）
            start_date: 开始日期（ISO 8601 格式）
            end_date: 结束日期（ISO 8601 格式）
            status: 构建状态（success/failed/cancelled）

        Returns:
            List[BuildHistoryEntry]: 匹配的构建记录列表
        """
        entries = self.get_all_entries()

        filtered_entries = []

        for entry in entries:
            # 项目名称过滤
            if project_name and project_name.lower() not in entry.project_name.lower():
                continue

            # 时间范围过滤
            if start_date:
                if entry.timestamp < start_date:
                    continue

            if end_date:
                if entry.timestamp > end_date:
                    continue

            # 状态过滤
            if status and entry.status.value != status:
                continue

            filtered_entries.append(entry)

        return filtered_entries

    def _load_all_entries(self) -> List[BuildHistoryEntry]:
        """加载所有构建记录"""
        if not self.history_file_path.exists():
            return []

        try:
            # 读取文件
            content = self.history_file_path.read_text(encoding='utf-8')
            data = json.loads(content)

            # 数据迁移
            data = self._migrate_data(data)

            # 解析记录
            entries = [
                BuildHistoryEntry.from_dict(entry_data)
                for entry_data in data.get("entries", [])
            ]

            return entries

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败，尝试恢复备份: {e}")

            # 尝试恢复备份
            if self._restore_from_backup():
                return self._load_all_entries()

            return []

        except Exception as e:
            logger.error(f"加载构建记录失败: {e}")
            return []

    def _save_all_entries(self, entries: List[BuildHistoryEntry]) -> None:
        """保存所有构建记录（原子写入）"""
        # 备份现有文件
        self._backup_file()

        # 准备数据
        data = {
            "version": self._version,
            "entries": [entry.to_dict() for entry in entries]
        }

        # 原子写入：先写入临时文件
        temp_file = self.history_file_path.with_suffix('.tmp')

        try:
            # 写入临时文件
            temp_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )

            # 原子重命名
            temp_file.replace(self.history_file_path)

            logger.debug(f"构建记录已保存: {self.history_file_path}")

        except Exception as e:
            logger.error(f"保存构建记录失败: {e}")

            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()

            raise

    def _backup_file(self) -> None:
        """备份现有文件"""
        if self.history_file_path.exists():
            backup_file = self.history_file_path.with_suffix('.bak')

            try:
                shutil.copy2(self.history_file_path, backup_file)
                logger.debug(f"备份已创建: {backup_file}")
            except Exception as e:
                logger.error(f"创建备份失败: {e}")

    def _restore_from_backup(self) -> bool:
        """从备份恢复"""
        backup_file = self.history_file_path.with_suffix('.bak')

        if not backup_file.exists():
            logger.warning("备份文件不存在，无法恢复")
            return False

        try:
            shutil.copy2(backup_file, self.history_file_path)
            logger.info(f"已从备份恢复: {backup_file}")
            return True

        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            return False

    def _migrate_data(self, data: Dict) -> Dict:
        """数据迁移（版本升级）"""
        version = data.get("version", 1)

        # 版本 1 → 版本 2
        if version < 2:
            data = self._migrate_v1_to_v2(data)

        return data

    def _migrate_v1_to_v2(self, data: Dict) -> Dict:
        """版本 1 → 版本 2 迁移"""
        logger.info("执行数据迁移: 版本 1 → 版本 2")

        # 添加 error_message 字段（默认为 None）
        for entry in data.get("entries", []):
            if "error_message" not in entry:
                entry["error_message"] = None

        # 更新版本
        data["version"] = 2

        return data
```

### 构建历史列表 UI 组件

**BuildHistoryList 类**：
```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QLabel, QComboBox, QDateEdit,
    QPushButton, QHeaderView, QMenu
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QAction
import logging

logger = logging.getLogger(__name__)

class BuildHistoryList(QWidget):
    """构建历史列表组件"""

    # 信号定义
    entry_selected = pyqtSignal(object)  # BuildHistoryEntry
    compare_entries = pyqtSignal(object, object)  # entry1, entry2

    def __init__(self, history_manager: 'BuildHistoryManager', parent=None):
        super().__init__(parent)

        self.history_manager = history_manager
        self.current_entries = []
        self.last_selected_entry = None

        self._init_ui()
        self._connect_signals()
        self._load_history()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # 搜索栏
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索项目名称或构建ID...")

        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部状态", "成功", "失败", "已取消"])

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setDisplayFormat("yyyy-MM-dd")

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("yyyy-MM-dd")

        search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(QLabel("状态:"))
        search_layout.addWidget(self.status_filter)
        search_layout.addWidget(QLabel("日期:"))
        search_layout.addWidget(self.date_from)
        search_layout.addWidget(QLabel("至"))
        search_layout.addWidget(self.date_to)

        layout.addLayout(search_layout)

        # 历史列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "构建ID", "时间", "项目名称", "状态", "总耗时"
        ])

        # 设置列宽
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # 启用选择
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        layout.addWidget(self.table)

    def _connect_signals(self):
        """连接信号"""
        self.search_input.textChanged.connect(self._apply_filters)
        self.status_filter.currentTextChanged.connect(self._apply_filters)
        self.date_from.dateChanged.connect(self._apply_filters)
        self.date_to.dateChanged.connect(self._apply_filters)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

    def _load_history(self):
        """加载历史记录"""
        self.current_entries = self.history_manager.get_all_entries()
        self._apply_filters()

    def refresh_list(self):
        """刷新列表"""
        self._load_history()

    def _apply_filters(self):
        """应用筛选条件"""
        project_name = self.search_input.text().strip() or None
        status_filter = self.status_filter.currentText()

        # 转换状态
        status_map = {
            "全部状态": None,
            "成功": "success",
            "失败": "failed",
            "已取消": "cancelled"
        }
        status = status_map.get(status_filter)

        # 转换日期
        start_date = None
        end_date = None

        if self.date_from.date().isValid():
            start_date = self.date_from.date().toString("yyyy-MM-dd")

        if self.date_to.date().isValid():
            end_date = self.date_to.date().toString("yyyy-MM-dd")

        # 搜索和筛选
        filtered_entries = self.history_manager.search_entries(
            project_name=project_name,
            start_date=start_date,
            end_date=end_date,
            status=status
        )

        # 更新表格
        self._update_table(filtered_entries)

    def _update_table(self, entries: list):
        """更新表格内容"""
        self.table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            # 构建ID
            item = QTableWidgetItem(entry.build_id[:8])  # 显示前8位
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.table.setItem(row, 0, item)

            # 时间
            timestamp = entry.timestamp
            formatted_time = timestamp[:16]  # 2024-02-20T14:30
            item = QTableWidgetItem(formatted_time)
            self.table.setItem(row, 1, item)

            # 项目名称
            item = QTableWidgetItem(entry.project_name)
            self.table.setItem(row, 2, item)

            # 状态
            status_text = {
                "success": "成功",
                "failed": "失败",
                "cancelled": "已取消"
            }.get(entry.status.value, "未知")

            item = QTableWidgetItem(status_text)

            # 设置颜色
            if entry.status.value == "success":
                item.setForeground(Qt.GlobalColor.green)
            elif entry.status.value == "failed":
                item.setForeground(Qt.GlobalColor.red)
            else:
                item.setForeground(Qt.GlobalColor.gray)

            self.table.setItem(row, 3, item)

            # 总耗时
            duration_str = self._format_duration(entry.total_duration)
            item = QTableWidgetItem(duration_str)
            self.table.setItem(row, 4, item)

    def _format_duration(self, seconds: float) -> str:
        """格式化耗时"""
        if seconds < 60:
            return f"{seconds:.2f} 秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes} 分 {secs} 秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours} 时 {minutes} 分"

    def _on_selection_changed(self):
        """选择改变事件"""
        selected_items = self.table.selectedItems()

        if selected_items:
            entry = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.entry_selected.emit(entry)

    def _on_item_double_clicked(self, item):
        """双击事件"""
        entry = item.data(Qt.ItemDataRole.UserRole)
        self.entry_selected.emit(entry)

    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.table.itemAt(position)

        if not item:
            return

        entry = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu(self)

        # 查看详情
        action_view = QAction("查看详情", self)
        action_view.triggered.connect(lambda: self.entry_selected.emit(entry))
        menu.addAction(action_view)

        # 删除
        action_delete = QAction("删除", self)
        action_delete.triggered.connect(lambda: self._delete_entry(entry))
        menu.addAction(action_delete)

        # 导出
        action_export = QAction("导出", self)
        action_export.triggered.connect(lambda: self._export_entry(entry))
        menu.addAction(action_export)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def _delete_entry(self, entry: 'BuildHistoryEntry'):
        """删除构建记录"""
        confirm = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除构建记录 {entry.build_id} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if self.history_manager.delete_entry(entry.build_id):
                self.refresh_list()
                QMessageBox.information(self, "成功", "构建记录已删除")
            else:
                QMessageBox.warning(self, "失败", "删除构建记录失败")

    def _export_entry(self, entry: 'BuildHistoryEntry'):
        """导出构建记录"""
        # TODO: 实现导出功能
        pass
```

### 构建详情面板 UI 组件

**BuildDetailPanel 类**：
```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import logging
import subprocess
import os

logger = logging.getLogger(__name__)

class BuildDetailPanel(QWidget):
    """构建详情面板组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_entry = None

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # 构建信息标签
        info_layout = QHBoxLayout()

        self.build_info_label = QLabel("选择一个构建记录查看详情")
        self.build_info_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.export_button = QPushButton("导出详情")
        self.export_button.clicked.connect(self._export_details)
        self.export_button.setEnabled(False)

        info_layout.addWidget(self.build_info_label)
        info_layout.addStretch()
        info_layout.addWidget(self.export_button)

        layout.addLayout(info_layout)

        # 标签页
        self.tab_widget = QTabWidget()

        # 配置标签页
        self.config_tab = QWidget()
        self._init_config_tab()
        self.tab_widget.addTab(self.config_tab, "配置")

        # 阶段时间标签页
        self.stage_time_tab = QWidget()
        self._init_stage_time_tab()
        self.tab_widget.addTab(self.stage_time_tab, "阶段时间")

        # 构建日志标签页
        self.log_tab = QWidget()
        self._init_log_tab()
        self.tab_widget.addTab(self.log_tab, "构建日志")

        # 产物文件标签页
        self.artifact_tab = QWidget()
        self._init_artifact_tab()
        self.tab_widget.addTab(self.artifact_tab, "产物文件")

        layout.addWidget(self.tab_widget)

    def _init_config_tab(self):
        """初始化配置标签页"""
        layout = QVBoxLayout(self.config_tab)

        self.config_tree = QTreeWidget()
        self.config_tree.setHeaderLabels(["配置项", "值"])
        self.config_tree.setColumnWidth(0, 200)

        layout.addWidget(self.config_tree)

    def _init_stage_time_tab(self):
        """初始化阶段时间标签页"""
        layout = QVBoxLayout(self.stage_time_tab)

        self.stage_time_table = QTableWidget()
        self.stage_time_table.setColumnCount(4)
        self.stage_time_table.setHorizontalHeaderLabels([
            "阶段名称", "状态", "执行时长", "开始时间"
        ])

        layout.addWidget(self.stage_time_table)

    def _init_log_tab(self):
        """初始化构建日志标签页"""
        layout = QVBoxLayout(self.log_tab)

        # 日志查看器（复用 LogViewer）
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        layout.addWidget(self.log_viewer)

    def _init_artifact_tab(self):
        """初始化产物文件标签页"""
        layout = QVBoxLayout(self.artifact_tab)

        self.artifact_list = QListWidget()

        layout.addWidget(self.artifact_list)

        # 按钮栏
        button_layout = QHBoxLayout()

        self.open_folder_button = QPushButton("打开所在文件夹")
        self.open_folder_button.clicked.connect(self._open_artifact_folder)
        self.open_folder_button.setEnabled(False)

        self.copy_path_button = QPushButton("复制路径")
        self.copy_path_button.clicked.connect(self._copy_artifact_path)
        self.copy_path_button.setEnabled(False)

        button_layout.addWidget(self.open_folder_button)
        button_layout.addWidget(self.copy_path_button)

        layout.addLayout(button_layout)

    def load_build_details(self, entry: 'BuildHistoryEntry'):
        """
        加载构建详情

        Args:
            entry: 构建记录对象
        """
        self.current_entry = entry
        self.export_button.setEnabled(True)
        self.open_folder_button.setEnabled(True)
        self.copy_path_button.setEnabled(True)

        # 更新构建信息标签
        status_text = {
            "success": "成功",
            "failed": "失败",
            "cancelled": "已取消"
        }.get(entry.status.value, "未知")

        self.build_info_label.setText(
            f"构建ID: {entry.build_id} | "
            f"时间: {entry.timestamp[:19]} | "
            f"状态: {status_text} | "
            f"总耗时: {entry.total_duration:.2f} 秒"
        )

        # 加载配置
        self._load_config(entry)

        # 加载阶段时间
        self._load_stage_times(entry)

        # 加载日志
        self._load_log(entry)

        # 加载产物文件
        self._load_artifacts(entry)

    def _load_config(self, entry: 'BuildHistoryEntry'):
        """加载配置"""
        self.config_tree.clear()

        # 项目路径
        project_item = QTreeWidgetItem(["项目路径", entry.project_path])
        self.config_tree.addTopLevelItem(project_item)

        # 工作流配置
        workflow_item = QTreeWidgetItem(["工作流配置", ""])
        self.config_tree.addTopLevelItem(workflow_item)

        for key, value in entry.workflow_config.items():
            item = QTreeWidgetItem([key, str(value)])
            workflow_item.addChild(item)

        self.config_tree.expandAll()

    def _load_stage_times(self, entry: 'BuildHistoryEntry'):
        """加载阶段时间"""
        self.stage_time_table.setRowCount(len(entry.stage_times))

        for row, stage_time in enumerate(entry.stage_times):
            # 阶段名称
            item = QTableWidgetItem(stage_time.get("stage_name", ""))
            self.stage_time_table.setItem(row, 0, item)

            # 状态
            status = stage_time.get("status", "")
            status_text = {
                "completed": "已完成",
                "failed": "失败",
                "running": "进行中",
                "pending": "等待中"
            }.get(status, status)

            item = QTableWidgetItem(status_text)

            # 设置颜色
            if status == "completed":
                item.setForeground(Qt.GlobalColor.green)
            elif status == "failed":
                item.setForeground(Qt.GlobalColor.red)

            self.stage_time_table.setItem(row, 1, item)

            # 执行时长
            duration = stage_time.get("duration", 0)
            item = QTableWidgetItem(f"{duration:.2f} 秒")
            self.stage_time_table.setItem(row, 2, item)

            # 开始时间
            start_time = stage_time.get("start_time", "")
            item = QTableWidgetItem(str(start_time))
            self.stage_time_table.setItem(row, 3, item)

    def _load_log(self, entry: 'BuildHistoryEntry'):
        """加载日志"""
        self.log_viewer.clear()

        if not entry.log_file_path:
            self.log_viewer.append("未找到日志文件")
            return

        try:
            log_path = Path(entry.log_file_path)

            if not log_path.exists():
                self.log_viewer.append(f"日志文件不存在: {entry.log_file_path}")
                return

            # 读取日志文件
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.log_viewer.append(content)

        except Exception as e:
            logger.error(f"加载日志失败: {e}")
            self.log_viewer.append(f"加载日志失败: {e}")

    def _load_artifacts(self, entry: 'BuildHistoryEntry'):
        """加载产物文件"""
        self.artifact_list.clear()

        for artifact_info in entry.artifact_paths:
            path = artifact_info.path
            file_type = artifact_info.file_type
            size = artifact_info.size

            # 检查文件是否存在
            exists = Path(path).exists()

            # 创建条目
            item_text = f"{file_type.upper()}: {os.path.basename(path)}"

            if not exists:
                item_text += " (文件不存在)"

            item = QListWidgetItem(item_text)

            # 设置图标（根据文件类型）
            # TODO: 添加文件类型图标

            # 设置数据
            item.setData(Qt.ItemDataRole.UserRole, artifact_info)

            # 设置颜色（文件不存在显示红色）
            if not exists:
                item.setForeground(Qt.GlobalColor.red)

            self.artifact_list.addItem(item)

    def _open_artifact_folder(self):
        """打开产物文件所在文件夹"""
        current_item = self.artifact_list.currentItem()

        if not current_item:
            return

        artifact_info = current_item.data(Qt.ItemDataRole.UserRole)
        path = artifact_info.path

        try:
            # 打开文件夹并选中文件
            if os.name == 'nt':  # Windows
                subprocess.run(['explorer', '/select,', os.path.normpath(path)])
            elif os.name == 'posix':  # macOS/Linux
                subprocess.run(['open', os.path.dirname(path)])

        except Exception as e:
            logger.error(f"打开文件夹失败: {e}")
            QMessageBox.warning(self, "失败", f"打开文件夹失败: {e}")

    def _copy_artifact_path(self):
        """复制产物文件路径"""
        current_item = self.artifact_list.currentItem()

        if not current_item:
            return

        artifact_info = current_item.data(Qt.ItemDataRole.UserRole)
        path = artifact_info.path

        clipboard = QApplication.clipboard()
        clipboard.setText(path)

        QMessageBox.information(self, "成功", "路径已复制到剪贴板")

    def _export_details(self):
        """导出详情"""
        if not self.current_entry:
            return

        # TODO: 实现导出功能
        pass
```

### 代码示例

**完整示例：src/core/workflow_thread.py（集成构建历史）**：
```python
import logging
import uuid
from datetime import datetime
from src.core.models import BuildHistoryEntry, BuildStatus, ArtifactInfo
from src.utils.build_history import BuildHistoryManager
from pathlib import Path

logger = logging.getLogger(__name__)

class WorkflowThread(QThread):
    def __init__(self, stages, context, project_name: str, project_path: str):
        super().__init__()
        self.stages = stages
        self.context = context
        self.project_name = project_name
        self.project_path = project_path

        # 构建历史管理器
        app_data_dir = Path.home() / "AppData" / "Roaming" / "MBD_CICDKits"
        history_file_path = app_data_dir / "build_history.json"
        self.build_history_manager = BuildHistoryManager(history_file_path)

        # 当前构建记录
        self.current_build_entry = None
        self.artifact_paths = []

    def run(self):
        """执行工作流"""
        try:
            # 生成构建ID
            build_id = str(uuid.uuid4())

            # 创建构建记录
            self.current_build_entry = BuildHistoryEntry(
                build_id=build_id,
                timestamp=datetime.now().isoformat(),
                project_name=self.project_name,
                project_path=self.project_path,
                workflow_config=self.context.get("workflow_config", {}),
                stage_times=[],
                total_duration=0.0,
                status=BuildStatus.SUCCESS,
                artifact_paths=[],
                log_file_path=None,
                error_message=None
            )

            logger.info(f"构建开始: {build_id}")

            # 执行各阶段
            for stage in self.stages:
                result = execute_stage(stage, self.context)

                # 记录阶段时间
                stage_time = {
                    "stage_name": stage.name,
                    "status": result.status.value,
                    "duration": result.duration,
                    "start_time": result.start_time
                }
                self.current_build_entry.stage_times.append(stage_time)

                # 如果失败，更新状态
                if result.status != StageStatus.COMPLETED:
                    self.current_build_entry.status = BuildStatus.FAILED
                    self.current_build_entry.error_message = result.error
                    break

                # 收集产物文件路径
                if result.artifacts:
                    for artifact_path in result.artifacts:
                        path_obj = Path(artifact_path)

                        if path_obj.exists():
                            artifact_info = ArtifactInfo(
                                path=str(path_obj.absolute()),
                                file_type=path_obj.suffix[1:] if path_obj.suffix else "unknown",
                                size=path_obj.stat().st_size,
                                created_at=datetime.fromtimestamp(path_obj.stat().st_ctime).isoformat()
                            )
                            self.artifact_paths.append(artifact_info)

            # 工作流完成或失败
            self.current_build_entry.artifact_paths = self.artifact_paths
            self.current_build_entry.total_duration = sum(
                st["duration"] for st in self.current_build_entry.stage_times
            )

            # 保存构建历史
            self.build_history_manager.add_entry(self.current_build_entry)

            logger.info(f"构建完成: {build_id}, 状态: {self.current_build_entry.status.value}")

        except Exception as e:
            logger.error(f"工作流异常: {e}")

            if self.current_build_entry:
                self.current_build_entry.status = BuildStatus.FAILED
                self.current_build_entry.error_message = str(e)
                self.build_history_manager.add_entry(self.current_build_entry)

        finally:
            # 清理资源
            self._cleanup()
```

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 3 - Story 3.4](../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-055](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-056](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-057](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-058](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 3.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 4.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-003](../planning-artifacts/architecture.md)
- [Source: Story 3.1: 实时显示构建进度](./3-1-real-time-build-progress-display.md)
- [Source: Story 3.2: 实时显示构建日志输出](./3-2-real-time-build-log-output-display.md)
- [Source: Story 3.3: 记录并显示阶段执行时间](./3-3-record-and-display-stage-execution-time.md)

## Dev Agent Record

### Agent Model Used

zai/glm-4.7 (Subagent: Story 3.4 Creation)

### Debug Log References

None

### Completion Notes List

**实现摘要**：
- Story 3.4 implementation 文件已创建
- 包含15个主要任务，总计130+个子任务
- 定义了核心数据模型：BuildHistoryEntry、ArtifactInfo
- 设计了完整的构建历史管理、查看、对比、导出、统计功能
- 所有任务都遵循 BMAD implementation 文件格式

**核心功能模块**：
1. **数据模型模块**：BuildHistoryEntry 记录构建信息，ArtifactInfo 记录产物文件
2. **构建历史管理器模块**：BuildHistoryManager 管理历史记录的增删查改、搜索筛选
3. **构建历史列表 UI 模块**：BuildHistoryList 显示历史列表，支持搜索、筛选、排序
4. **构建详情面板 UI 模块**：BuildDetailPanel 显示构建配置、阶段时间、日志、产物文件
5. **构建对比面板 UI 模块**：BuildComparisonPanel 显示性能对比和配置差异
6. **导出功能模块**：支持 CSV、JSON、Markdown、HTML 格式导出
7. **统计功能模块**：BuildHistoryStats 提供构建统计和趋势分析
8. **数据持久化模块**：原子写入、备份恢复、数据迁移

**数据模型设计**：
- BuildHistoryEntry：包含构建ID、时间戳、项目信息、工作流配置、阶段时间、状态、产物、日志等
- ArtifactInfo：包含产物文件路径、类型、大小、创建时间等元数据
- 支持版本管理和数据迁移（version 字段）

**技术约束**：
- 构建ID使用 UUID4 确保唯一性
- 历史记录最多保存100条，使用 FIFO 策略
- 使用原子写入（临时文件 + 重命名）确保数据完整性
- 每次写入前备份（.bak），损坏时自动恢复
- 时间戳使用 ISO 8601 格式
- 文件路径使用绝对路径
- 支持数据版本迁移（v1 → v2）

**测试要求**：
- 单元测试：验证数据模型、管理器、UI组件、导出、统计等
- 集成测试：验证完整的构建历史记录流程、查看、对比、搜索、导出等
- 端到端测试：验证从构建开始到历史查看的完整流程

**文件创建**：
- implementation-artifacts/stories/3-4-build-history-and-viewing.md（本文档）

### File List

#### 待创建的文件

**源文件**：
1. **src/core/models.py**（修改）
   - 添加 BuildHistoryEntry 数据类
   - 添加 ArtifactInfo 数据类
   - 添加 BuildStatus 枚举

2. **src/core/workflow_thread.py**（修改）
   - 添加 build_history_manager 属性
   - 集成构建历史记录创建和保存逻辑

3. **src/ui/main_window.py**（修改）
   - 添加"构建历史"菜单项或按钮
   - 创建 BuildHistoryDialog 对话框

4. **src/ui/widgets/build_history_list.py**（新建）
   - 创建 BuildHistoryList 类
   - 实现历史列表、搜索、筛选功能

5. **src/ui/widgets/build_detail_panel.py**（新建）
   - 创建 BuildDetailPanel 类
   - 实现构建详情查看（配置、阶段时间、日志、产物）

6. **src/ui/widgets/build_comparison_panel.py**（新建）
   - 创建 BuildComparisonPanel 类
   - 实现构建对比功能（性能、配置）

7. **src/utils/build_history.py**（新建）
   - 创建 BuildHistoryManager 类
   - 实现历史记录的增删查改、搜索、原子写入、备份恢复、数据迁移

8. **src/utils/build_history_exporter.py**（新建）
   - 创建 BuildHistoryExporter 类
   - 实现 CSV、JSON、Markdown、HTML 导出

9. **src/utils/build_history_stats.py**（新建）
   - 创建 BuildHistoryStats 类
   - 实现构建统计和趋势分析

**测试文件**：
1. **tests/unit/test_build_history_models.py**（新建）
   - 测试 BuildHistoryEntry 数据类
   - 测试 ArtifactInfo 数据类
   - 测试序列化/反序列化

2. **tests/unit/test_build_history_manager.py**（新建）
   - 测试 BuildHistoryManager 的增删查改
   - 测试搜索和筛选
   - 测试原子写入和备份恢复
   - 测试数据迁移

3. **tests/integration/test_build_history.py**（新建）
   - 测试完整的构建历史记录流程
   - 测试历史列表和详情查看
   - 测试构建对比功能
   - 测试导出和统计功能
   - 测试大量历史记录性能

#### 文件统计

- 待修改的源文件：3 个
- 待创建的源文件：6 个
- 待创建的测试文件：3 个
- 总任务数：15 个任务
- 总子任务数：130+ 个
- 预计代码行数：~8000 行（源文件 + 测试文件）
