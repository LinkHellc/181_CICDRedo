# Story 3.3: 记录并显示阶段执行时间

Status: planned

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要查看每个工作流阶段的执行时间，
以便分析构建性能瓶颈和优化构建流程。

## Acceptance Criteria

**Given** 工作流正在执行
**When** 各个阶段完成（MATLAB代码生成、文件处理、IAR编译、A2L处理、打包等）
**Then** 系统记录每个阶段的开始和结束时间
**And** 系统计算每个阶段的执行时长
**And** 系统在日志中显示阶段执行时间（格式：[阶段名称] 执行时长: XX.XX 秒）
**And** 系统在工作流完成时显示汇总信息（总耗时、最慢阶段、最快阶段）

## Tasks / Subtasks

- [ ] 任务 1: 创建阶段执行时间数据模型 (AC: Then - 系统记录每个阶段的开始和结束时间)
  - [ ] 1.1 在 `src/core/models.py` 中创建 `StageExecutionTime` 数据类
  - [ ] 1.2 添加字段：stage_name（阶段名称）
  - [ ] 1.3 添加字段：start_time（开始时间，time.monotonic()）
  - [ ] 1.4 添加字段：end_time（结束时间，time.monotonic()）
  - [ ] 1.5 添加字段：duration（执行时长，秒）
  - [ ] 1.6 添加字段：status（状态：pending、running、completed、failed）
  - [ ] 1.7 添加 `to_dict()` 方法用于序列化
  - [ ] 1.8 添加单元测试验证数据类创建
  - [ ] 1.9 添加单元测试验证序列化/反序列化

- [ ] 任务 2: 创建工作流执行时间统计模型 (AC: Then - 系统在工作流完成时显示汇总信息)
  - [ ] 2.1 在 `src/core/models.py` 中创建 `WorkflowExecutionSummary` 数据类
  - [ ] 2.2 添加字段：total_duration（总耗时，秒）
  - [ ] 2.3 添加字段：slowest_stage（最慢阶段名称和时长）
  - [ ] 2.4 添加字段：fastest_stage（最快阶段名称和时长）
  - [ ] 2.5 添加字段：stage_times（所有阶段执行时间列表）
  - [ ] 2.6 添加字段：success_rate（成功率）
  - [ ] 2.7 添加 `calculate_statistics()` 方法计算统计数据
  - [ ] 2.8 添加 `format_summary()` 方法格式化汇总信息
  - [ ] 2.9 添加单元测试验证统计计算
  - [ ] 2.10 添加单元测试验证汇总格式化

- [ ] 任务 3: 在 WorkflowThread 中添加时间记录功能 (AC: Then - 系统记录每个阶段的开始和结束时间)
  - [ ] 3.1 在 `src/core/workflow_thread.py` 中创建 `stage_times` 字典（存储各阶段执行时间）
  - [ ] 3.2 在每个阶段开始前记录开始时间（`time.monotonic()`）
  - [ ] 3.3 在每个阶段完成后记录结束时间（`time.monotonic()`）
  - [ ] 3.4 计算阶段执行时长（`end_time - start_time`）
  - [ ] 3.5 创建 `StageExecutionTime` 对象并存储
  - [ ] 3.6 在阶段失败时记录失败状态和部分时长
  - [ ] 3.7 添加单元测试验证开始时间记录
  - [ ] 3.8 添加单元测试验证结束时间记录
  - [ ] 3.9 添加单元测试验证时长计算准确性

- [ ] 任务 4: 实现阶段执行时间日志输出 (AC: Then - 系统在日志中显示阶段执行时间)
  - [ ] 4.1 在 `src/core/workflow_thread.py` 中创建 `_log_stage_execution_time()` 方法
  - [ ] 4.2 格式化日志消息：`[阶段名称] 执行时长: XX.XX 秒`
  - [ ] 4.3 使用 `log_message` 信号发送日志
  - [ ] 4.4 在阶段完成后立即执行日志输出
  - [ ] 4.5 确保日志格式一致（保留2位小数）
  - [ ] 4.6 添加单元测试验证日志格式
  - [ ] 4.7 添加单元测试验证日志发射时机

- [ ] 任务 5: 实现工作流完成时的汇总信息 (AC: Then - 系统在工作流完成时显示汇总信息)
  - [ ] 5.1 在 `src/core/workflow_thread.py` 中创建 `_generate_execution_summary()` 方法
  - [ ] 5.2 创建 `WorkflowExecutionSummary` 对象
  - [ ] 5.3 计算总耗时（所有阶段时长之和）
  - [ ] 5.4 找出最慢阶段（最大 duration）
  - [ ] 5.5 找出最快阶段（最小 duration，排除未完成的）
  - [ ] 5.6 计算成功率（completed_stages / total_stages）
  - [ ] 5.7 格式化汇总信息为多行日志
  - [ ] 5.8 在工作流结束时发射汇总信息
  - [ ] 5.9 添加单元测试验证汇总计算
  - [ ] 5.10 添加单元测试验证汇总格式

- [ ] 任务 6: 在进度面板中显示阶段执行时间 (AC: Then - 系统在日志中显示阶段执行时间)
  - [ ] 6.1 在 `src/ui/widgets/progress_panel.py` 中扩展 `ProgressPanel` 类
  - [ ] 6.2 在阶段状态列表中添加执行时间列
  - [ ] 6.3 更新 `update_progress()` 方法接收执行时间信息
  - [ ] 6.4 为每个阶段显示实时执行时间（进行中）
  - [ ] 6.5 为每个阶段显示最终执行时间（已完成）
  - [ ] 6.6 为失败阶段显示失败时已执行时长
  - [ ] 6.7 格式化时间显示（秒或分:秒格式）
  - [ ] 6.8 添加单元测试验证时间显示更新
  - [ ] 6.9 添加集成测试验证UI显示效果

- [ ] 任务 7: 实现执行时间历史记录 (AC: All)
  - [ ] 7.1 在 `src/utils/execution_time.py` 中创建 `ExecutionTimeHistory` 类
  - [ ] 7.2 保存每次工作流执行的汇总信息到 JSON 文件
  - [ ] 7.3 文件路径：`%APPDATA%/MBD_CICDKits/execution_history/[项目名]_history.json`
  - [ ] 7.4 记录执行时间戳、总耗时、各阶段耗时
  - [ ] 7.5 实现历史记录查询功能（按时间范围、阶段）
  - [ ] 7.6 实现历史记录统计功能（平均耗时、趋势分析）
  - [ ] 7.7 添加单元测试验证保存功能
  - [ ] 7.8 添加单元测试验证查询功能

- [ ] 任务 8: 在主窗口中添加执行时间汇总面板 (AC: Then - 系统在工作流完成时显示汇总信息)
  - [ ] 8.1 在 `src/ui/widgets/execution_summary_panel.py` 中创建 `ExecutionSummaryPanel` 类
  - [ ] 8.2 显示工作流总耗时（大字体）
  - [ ] 8.3 显示最慢阶段和耗时（红色高亮）
  - [ ] 8.4 显示最快阶段和耗时（绿色高亮）
  - [ ] 8.5 显示各阶段耗时列表（排序或按执行顺序）
  - [ ] 8.6 使用图表（QBarSeries）可视化各阶段耗时对比
  - [ ] 8.7 添加"查看历史记录"按钮
  - [ ] 8.8 添加单元测试验证面板创建
  - [ ] 8.9 添加集成测试验证显示效果

- [ ] 任务 9: 实现性能分析工具 (AC: All)
  - [ ] 9.1 在 `src/utils/performance_analyzer.py` 中创建 `PerformanceAnalyzer` 类
  - [ ] 9.2 对比当前执行与历史平均执行时间
  - [ ] 9.3 计算性能变化百分比（提升/下降）
  - [ ] 9.4 识别性能异常（超过平均时间 50% 视为异常）
  - [ ] 9.5 生成性能报告（Markdown 或 HTML）
  - [ ] 9.6 提供优化建议（基于最慢阶段）
  - [ ] 9.7 添加单元测试验证性能分析算法
  - [ ] 9.8 添加单元测试验证异常检测

- [ ] 任务 10: 添加执行时间警告阈值 (AC: All)
  - [ ] 10.1 在项目配置中添加 `stage_time_thresholds` 配置项
  - [ ] 10.2 为每个阶段设置预期执行时间阈值
  - [ ] 10.3 在阶段完成时检查是否超过阈值
  - [ ] 10.4 超过阈值时发出警告日志
  - [ ] 10.5 在 UI 中标记超时阶段（橙色背景）
  - [ ] 10.6 提供"调整阈值"功能（基于历史数据）
  - [ ] 10.7 添加单元测试验证阈值检测
  - [ ] 10.8 添加集成测试验证警告触发

- [ ] 任务 11: 实现实时执行时间更新 (AC: Then - 系统在日志中显示阶段执行时间)
  - [ ] 11.1 在 `src/core/workflow_thread.py` 中创建定时器（每秒更新一次）
  - [ ] 11.2 计算当前阶段已执行时间（`time.monotonic() - start_time`）
  - [ ] 11.3 在进度面板中显示实时时间（动态更新）
  - [ ] 11.4 在阶段切换时停止上一阶段的计时
  - [ ] 11.5 添加格式化逻辑（秒 → 分:秒 当超过60秒）
  - [ ] 11.6 添加单元测试验证实时时间计算
  - [ ] 11.7 添加集成测试验证UI实时更新

- [ ] 任务 12: 导出执行时间报告 (AC: All)
  - [ ] 12.1 在 `src/utils/report_generator.py` 中创建 `ExecutionTimeReport` 类
  - [ ] 12.2 支持导出为 CSV 格式（包含所有阶段时间）
  - [ ] 12.3 支持导出为 Markdown 格式（包含汇总信息和图表）
  - [ ] 12.4 支持导出为 HTML 格式（包含交互式图表）
  - [ ] 12.5 在主窗口添加"导出报告"按钮
  - [ ] 12.6 支持批量导出历史记录
  - [ ] 12.7 添加单元测试验证 CSV 导出
  - [ ] 12.8 添加单元测试验证 Markdown 导出
  - ] 12.9 添加单元测试验证 HTML 导出

- [ ] 任务 13: 添加集成测试 (AC: All)
  - [ ] 13.1 创建 `tests/integration/test_execution_time.py`
  - [ ] 13.2 测试完整的执行时间记录流程
  - [ ] 13.3 测试阶段开始/结束时间记录准确性
  - [ ] 13.4 测试执行时长计算
  - [ ] 13.5 测试日志输出格式和时机
  - [ ] 13.6 测试工作流汇总信息生成
  - [ ] 13.7 测试进度面板时间显示
  - [ ] 13.8 测试历史记录保存和加载
  - [ ] 13.9 测试性能分析功能
  - [ ] 13.10 测试阈值警告机制
  - [ ] 13.11 测试实时时间更新
  - [ ] 13.12 测试报告导出功能
  - [ ] 13.13 测试失败阶段的时长记录

## Dev Notes

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **ADR-003（可观测性）**：执行时间是性能分析的关键指标，必须准确记录
- **Decision 3.1（PyQt6 线程 + 信号模式）**：使用 QThread + pyqtSignal，跨线程必须使用 `Qt.ConnectionType.QueuedConnection`
- **Decision 5.1（日志框架）**：使用统一日志级别，执行时间信息使用 INFO 级别
- **Decision 4.1（原子性数据传递）**：使用数据类（StageExecutionTime, WorkflowExecutionSummary）传递时间数据
- **时间记录规则**：必须使用 `time.monotonic()` 而非 `time.time()`（避免系统时间调整影响）

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 时间记录：使用 `time.monotonic()` 确保单调递增，不受系统时间调整影响
2. ⭐⭐⭐⭐⭐ 信号连接：跨线程信号必须使用 `Qt.ConnectionType.QueuedConnection`
3. ⭐⭐⭐⭐ 数据传递：使用数据类（StageExecutionTime），不使用全局变量
4. ⭐⭐⭐⭐ 日志格式：执行时间日志格式必须统一：`[阶段名称] 执行时长: XX.XX 秒`
5. ⭐⭐⭐⭐ 时间精度：保留2位小数（毫秒级精度）
6. ⭐⭐⭐⭐ 汇总信息：工作流完成后必须显示汇总（总耗时、最慢阶段、最快阶段）
7. ⭐⭐⭐ 历史记录：每次执行必须保存到历史文件，便于性能分析
8. ⭐⭐⭐ 阈值警告：超过阈值必须发出警告，帮助识别性能问题

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/core/models.py` | 修改 | 添加 `StageExecutionTime` 和 `WorkflowExecutionSummary` 数据类 |
| `src/core/workflow_thread.py` | 修改 | 添加时间记录、日志输出、汇总信息生成 |
| `src/ui/widgets/progress_panel.py` | 修改 | 扩展显示阶段执行时间 |
| `src/ui/widgets/execution_summary_panel.py` | 新建 | 执行时间汇总面板 |
| `src/utils/execution_time.py` | 新建 | 执行时间历史记录工具 |
| `src/utils/performance_analyzer.py` | 新建 | 性能分析工具 |
| `src/utils/report_generator.py` | 新建 | 报告生成工具 |
| `tests/unit/test_execution_time_models.py` | 新建 | 执行时间模型单元测试 |
| `tests/unit/test_execution_time_tracking.py` | 新建 | 执行时间跟踪单元测试 |
| `tests/unit/test_performance_analyzer.py` | 新建 | 性能分析器单元测试 |
| `tests/integration/test_execution_time.py` | 新建 | 执行时间集成测试 |

**确保符合项目结构**：
```
src/
├── core/                                     # 核心业务逻辑（函数）
│   ├── models.py                            # 数据模型（修改）
│   └── workflow_thread.py                   # 工作流执行线程（修改）
├── ui/                                      # PyQt6 UI（类）
│   └── widgets/                             # 自定义控件
│       ├── progress_panel.py                # 进度面板（修改）
│       └── execution_summary_panel.py       # 执行时间汇总面板（新建）
└── utils/                                   # 工具函数
    ├── execution_time.py                    # 执行时间历史记录（新建）
    ├── performance_analyzer.py              # 性能分析（新建）
    └── report_generator.py                  # 报告生成（新建）
tests/
├── unit/
│   ├── test_execution_time_models.py        # 执行时间模型测试（新建）
│   ├── test_execution_time_tracking.py      # 执行时间跟踪测试（新建）
│   └── test_performance_analyzer.py         # 性能分析器测试（新建）
└── integration/
    └── test_execution_time.py               # 执行时间集成测试（新建）
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| PyQt6 | 6.0+ | UI 框架（QWidget, QLabel, QTimer, pyqtSignal） |
| PyQt6-Charts | 6.0+ | 图表库（QBarSeries, QChartView） |
| dataclasses | 内置 | 数据类定义 |
| time | 内置 | 时间计算（time.monotonic()） |
| json | 内置 | 历史记录持久化 |
| pathlib | 内置 | 文件路径处理 |
| csv | 内置 | CSV 报告导出 |
| datetime | 内置 | 时间戳格式化 |
| typing | 内置 | 类型提示 |

### 测试标准

**单元测试要求**：
- 测试 `StageExecutionTime` 数据类创建和序列化
- 测试 `WorkflowExecutionSummary` 统计计算和汇总格式化
- 测试开始/结束时间记录准确性
- 测试执行时长计算（边界情况：0秒、<1秒、>1分钟）
- 测试日志输出格式（`[阶段名称] 执行时长: XX.XX 秒`）
- 测试汇总信息计算（总耗时、最慢/最快阶段）
- 测试历史记录保存和加载
- 测试性能分析算法（平均值、百分比变化、异常检测）
- 测试阈值警告机制
- 测试实时时间更新
- 测试报告导出（CSV、Markdown、HTML）

**集成测试要求**：
- 测试完整的执行时间记录流程（从开始到完成）
- 测试多个阶段的时间记录和汇总
- 测试失败阶段的时长记录
- 测试日志输出时机和格式
- 测试进度面板时间显示（实时和最终）
- 测试汇总面板显示效果（包括图表）
- 测试历史记录持久化和查询
- 测试性能分析报告生成
- 测试阈值警告触发和显示
- 测试实时时间更新准确性
- 测试报告导出功能（各格式）
- 测试长时间构建（>10分钟）的时间记录准确性

**端到端测试要求**：
- 测试从构建开始到完成的完整时间记录
- 测试构建失败时的时间记录和汇总
- 测试历史记录查询和趋势分析
- 测试性能报告生成和导出
- 测试多项目并发构建的时间隔离

### 依赖关系

**前置故事**：
- ✅ Epic 1 全部完成（项目配置管理）
- ✅ Story 2.4: 启动自动化构建流程（工作流执行框架）
- ✅ Story 3.1: 实时显示构建进度（进度面板和信号机制）
- ✅ Story 3.2: 实时显示构建日志输出（日志捕获和显示）

**后续故事**：
- Story 3.6: 日志高亮显示错误和警告（可复用日志输出机制）
- Story 4.3: 导出构建历史记录（可复用历史记录逻辑）
- Story 4.4: 生成构建性能报告（可复用报告生成工具）

### 数据流设计

```
工作流开始执行
    │
    ▼
WorkflowThread.run()
    │
    ▼
对于每个阶段：
    │
    ├─→ 阶段开始
    │   │
    │   ▼
    │   记录开始时间（start_time = time.monotonic()）
    │   │
    │   ▼
    │   创建 StageExecutionTime(status=running)
    │   │
    │   ▼
    │   启动实时时间更新定时器（每秒）
    │   │
    │   ▼
    │   执行阶段逻辑
    │   │
    ▼
阶段完成或失败
    │
    ▼
记录结束时间（end_time = time.monotonic()）
    │
    ▼
计算执行时长（duration = end_time - start_time）
    │
    ▼
更新 StageExecutionTime(status=completed/failed)
    │
    ├─→ 发射阶段时间日志
    │   │   格式：[阶段名称] 执行时长: XX.XX 秒
    │   │
    │   └─→ 使用 log_message 信号
    │
    ├─→ 更新进度面板
    │   └─→ 显示阶段执行时间
    │
    ▼
存储到 stage_times 字典
    │
    ▼
...（重复所有阶段）
    │
    ▼
工作流结束
    │
    ▼
生成执行汇总
    │   ├─> 创建 WorkflowExecutionSummary
    │   ├─> 计算总耗时
    │   ├─> 找出最慢/最快阶段
    │   └─> 计算成功率
    │
    ▼
发射汇总日志
    │   └─> 多行日志显示汇总信息
    │
    ▼
更新汇总面板
    │   ├─> 显示总耗时
    │   ├─> 显示最慢/最快阶段
    │   └─> 显示耗时图表
    │
    ▼
保存到历史记录
    │   └─> 写入 JSON 文件
    │
    ▼
（可选）生成性能报告
    │   ├─> 性能分析（对比历史）
    │   ├─> 识别异常
    │   └─> 优化建议
    │
    ▼
（可选）导出报告
    │   └─> CSV / Markdown / HTML
```

### 阶段执行时间数据结构

**StageExecutionTime 数据类**：
```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class StageExecutionStatus(Enum):
    PENDING = "pending"     # 等待执行
    RUNNING = "running"     # 正在执行
    COMPLETED = "completed" # 已完成
    FAILED = "failed"       # 失败

@dataclass
class StageExecutionTime:
    """阶段执行时间记录"""
    stage_name: str                           # 阶段名称
    start_time: float                         # 开始时间（time.monotonic()）
    end_time: Optional[float] = None         # 结束时间（执行中为None）
    duration: Optional[float] = None        # 执行时长（秒）
    status: StageExecutionStatus = StageExecutionStatus.PENDING  # 状态

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "stage_name": self.stage_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "status": self.status.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StageExecutionTime':
        """从字典反序列化"""
        return cls(
            stage_name=data["stage_name"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            duration=data.get("duration"),
            status=StageExecutionStatus(data.get("status", "pending"))
        )
```

**WorkflowExecutionSummary 数据类**：
```python
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class StageTimeSummary:
    """阶段时间摘要"""
    stage_name: str
    duration: float
    status: str

@dataclass
class WorkflowExecutionSummary:
    """工作流执行汇总"""
    total_duration: float                      # 总耗时（秒）
    slowest_stage: StageTimeSummary           # 最慢阶段
    fastest_stage: StageTimeSummary           # 最快阶段
    stage_times: List[StageTimeSummary]      # 所有阶段时间列表
    success_rate: float                       # 成功率（0-1）
    timestamp: str                            # 执行时间戳

    def calculate_statistics(self):
        """计算统计数据"""
        if not self.stage_times:
            return

        # 计算总耗时
        completed_times = [t for t in self.stage_times if t.status == "completed"]
        if completed_times:
            self.total_duration = sum(t.duration for t in completed_times)

        # 找出最慢阶段
        if completed_times:
            self.slowest_stage = max(completed_times, key=lambda x: x.duration)
            self.fastest_stage = min(completed_times, key=lambda x: x.duration)

        # 计算成功率
        total_stages = len(self.stage_times)
        completed_count = len(completed_times)
        self.success_rate = completed_count / total_stages if total_stages > 0 else 0.0

    def format_summary(self) -> str:
        """格式化汇总信息"""
        lines = [
            "=" * 50,
            "工作流执行汇总",
            "=" * 50,
            f"总耗时: {self.total_duration:.2f} 秒",
            f"成功率: {self.success_rate * 100:.1f}%",
            ""
        ]

        if self.slowest_stage:
            lines.append(f"最慢阶段: {self.slowest_stage.stage_name}")
            lines.append(f"  执行时长: {self.slowest_stage.duration:.2f} 秒")
            lines.append("")

        if self.fastest_stage:
            lines.append(f"最快阶段: {self.fastest_stage.stage_name}")
            lines.append(f"  执行时长: {self.fastest_stage.duration:.2f} 秒")
            lines.append("")

        lines.append("各阶段耗时：")
        for stage_time in self.stage_times:
            status_mark = "✅" if stage_time.status == "completed" else "❌"
            duration_str = f"{stage_time.duration:.2f} 秒" if stage_time.duration else "未完成"
            lines.append(f"  {status_mark} {stage_time.stage_name}: {duration_str}")

        lines.append("=" * 50)

        return "\n".join(lines)
```

### 时间记录实现

**在 WorkflowThread 中记录时间**：
```python
import time
import logging
from typing import Dict
from src.core.models import StageExecutionTime, StageExecutionStatus

logger = logging.getLogger(__name__)

class WorkflowThread(QThread):
    def __init__(self, stages, context):
        super().__init__()
        self.stages = stages
        self.context = context

        # 阶段执行时间记录
        self.stage_times: Dict[str, StageExecutionTime] = {}
        self.realtime_update_timer = QTimer()
        self.realtime_update_timer.timeout.connect(self._update_realtime_times)

    def run(self):
        """执行工作流"""
        try:
            # 启动实时时间更新定时器（每秒更新一次）
            self.realtime_update_timer.start(1000)

            # 执行各阶段
            for stage in self.stages:
                # 检查取消标志
                if self.is_cancelled:
                    self._handle_cancellation()
                    return

                # 开始阶段
                self._on_stage_start(stage)

                try:
                    # 执行阶段
                    result = execute_stage(stage, self.context)

                    if result.status == StageStatus.COMPLETED:
                        # 阶段完成
                        self._on_stage_complete(stage)
                    else:
                        # 阶段失败
                        self._on_stage_failed(stage, result.error)

                except Exception as e:
                    # 阶段异常
                    logger.error(f"阶段执行异常: {e}")
                    self._on_stage_failed(stage, str(e))

        except Exception as e:
            logger.error(f"工作流异常: {e}")
        finally:
            # 停止实时时间更新定时器
            self.realtime_update_timer.stop()

            # 生成并显示执行汇总
            self._generate_and_display_summary()

    def _on_stage_start(self, stage):
        """
        阶段开始处理

        Args:
            stage: 阶段对象
        """
        # 记录开始时间
        start_time = time.monotonic()

        # 创建阶段执行时间对象
        stage_time = StageExecutionTime(
            stage_name=stage.name,
            start_time=start_time,
            status=StageExecutionStatus.RUNNING
        )

        # 存储
        self.stage_times[stage.name] = stage_time

        logger.info(f"阶段开始: {stage.name}")

    def _on_stage_complete(self, stage):
        """
        阶段完成处理

        Args:
            stage: 阶段对象
        """
        if stage.name not in self.stage_times:
            return

        # 记录结束时间
        end_time = time.monotonic()

        # 更新阶段执行时间
        stage_time = self.stage_times[stage.name]
        stage_time.end_time = end_time
        stage_time.duration = end_time - stage_time.start_time
        stage_time.status = StageExecutionStatus.COMPLETED

        # 发射阶段时间日志
        self._log_stage_execution_time(stage_time)

        logger.info(f"阶段完成: {stage.name}")

    def _on_stage_failed(self, stage, error):
        """
        阶段失败处理

        Args:
            stage: 阶段对象
            error: 错误信息
        """
        if stage.name not in self.stage_times:
            return

        # 记录结束时间
        end_time = time.monotonic()

        # 更新阶段执行时间
        stage_time = self.stage_times[stage.name]
        stage_time.end_time = end_time
        stage_time.duration = end_time - stage_time.start_time
        stage_time.status = StageExecutionStatus.FAILED

        # 发射阶段时间日志
        self._log_stage_execution_time(stage_time)

        logger.error(f"阶段失败: {stage.name}, 错误: {error}")

    def _log_stage_execution_time(self, stage_time: StageExecutionTime):
        """
        记录阶段执行时间日志

        Args:
            stage_time: 阶段执行时间对象
        """
        if stage_time.duration is None:
            return

        # 格式化日志消息
        log_message = f"[{stage_time.stage_name}] 执行时长: {stage_time.duration:.2f} 秒"

        # 发射日志信号
        self.log_message.emit(log_message)

    def _update_realtime_times(self):
        """更新实时时间（定时器回调）"""
        # 获取当前运行中的阶段
        current_stage = None
        current_time = None

        for stage_name, stage_time in self.stage_times.items():
            if stage_time.status == StageExecutionStatus.RUNNING:
                current_stage = stage_name
                current_time = time.monotonic() - stage_time.start_time
                break

        # 发射实时时间更新信号
        if current_stage and current_time is not None:
            self.realtime_time_update.emit({
                "stage_name": current_stage,
                "elapsed_time": current_time
            })

    def _generate_and_display_summary(self):
        """生成并显示执行汇总"""
        # 创建汇总对象
        from src.core.models import WorkflowExecutionSummary, StageTimeSummary

        # 构建阶段时间列表
        stage_times_list = [
            StageTimeSummary(
                stage_name=stage_time.stage_name,
                duration=stage_time.duration or 0.0,
                status=stage_time.status.value
            )
            for stage_time in self.stage_times.values()
        ]

        # 创建汇总
        summary = WorkflowExecutionSummary(
            total_duration=0.0,
            slowest_stage=None,
            fastest_stage=None,
            stage_times=stage_times_list,
            success_rate=0.0,
            timestamp=datetime.now().isoformat()
        )

        # 计算统计数据
        summary.calculate_statistics()

        # 格式化汇总信息
        summary_text = summary.format_summary()

        # 发射汇总日志
        self.log_message.emit(summary_text)

        # 发射汇总数据信号
        self.execution_summary.emit(summary.to_dict())
```

### 历史记录实现

**保存和加载历史记录**：
```python
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class ExecutionTimeHistory:
    """执行时间历史记录"""

    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def save_execution(self, project_name: str, summary: dict) -> Optional[Path]:
        """
        保存执行记录

        Args:
            project_name: 项目名称
            summary: 执行汇总信息

        Returns:
            Optional[Path]: 保存的文件路径
        """
        try:
            # 文件路径
            filename = f"{project_name}_history.json"
            file_path = self.history_dir / filename

            # 加载现有历史
            history = self._load_history_file(file_path)

            # 添加新记录
            record = {
                "timestamp": datetime.now().isoformat(),
                "summary": summary
            }
            history["executions"].append(record)

            # 保留最近 100 条记录
            if len(history["executions"]) > 100:
                history["executions"] = history["executions"][-100:]

            # 保存
            file_path.write_text(json.dumps(history, indent=2))
            logger.info(f"执行记录已保存: {file_path}")

            return file_path

        except Exception as e:
            logger.error(f"保存执行记录失败: {e}")
            return None

    def load_history(self, project_name: str) -> List[dict]:
        """
        加载项目执行历史

        Args:
            project_name: 项目名称

        Returns:
            List[dict]: 执行记录列表
        """
        try:
            filename = f"{project_name}_history.json"
            file_path = self.history_dir / filename

            history = self._load_history_file(file_path)
            return history["executions"]

        except Exception as e:
            logger.error(f"加载执行历史失败: {e}")
            return []

    def get_statistics(self, project_name: str, stage_name: Optional[str] = None) -> dict:
        """
        获取统计信息

        Args:
            project_name: 项目名称
            stage_name: 阶段名称（None 表示全部阶段）

        Returns:
            dict: 统计信息
        """
        try:
            executions = self.load_history(project_name)

            if not executions:
                return {
                    "count": 0,
                    "average_duration": 0.0,
                    "min_duration": 0.0,
                    "max_duration": 0.0
                }

            # 提取时长数据
            durations = []
            for exec_record in executions:
                summary = exec_record["summary"]

                if stage_name:
                    # 特定阶段
                    for stage_time in summary["stage_times"]:
                        if stage_time["stage_name"] == stage_name:
                            durations.append(stage_time["duration"])
                else:
                    # 总耗时
                    durations.append(summary["total_duration"])

            if not durations:
                return {
                    "count": 0,
                    "average_duration": 0.0,
                    "min_duration": 0.0,
                    "max_duration": 0.0
                }

            # 计算统计数据
            return {
                "count": len(durations),
                "average_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations)
            }

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                "count": 0,
                "average_duration": 0.0,
                "min_duration": 0.0,
                "max_duration": 0.0
            }

    def _load_history_file(self, file_path: Path) -> dict:
        """加载历史文件"""
        if not file_path.exists():
            return {
                "project_name": file_path.stem.replace("_history", ""),
                "executions": []
            }

        return json.loads(file_path.read_text())
```

### 性能分析实现

**性能分析器**：
```python
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self, history_manager: 'ExecutionTimeHistory'):
        self.history_manager = history_manager

    def compare_with_history(self, project_name: str, current_summary: dict) -> dict:
        """
        对比当前执行与历史记录

        Args:
            project_name: 项目名称
            current_summary: 当前执行汇总

        Returns:
            dict: 对比结果
        """
        try:
            # 获取历史统计数据
            history_stats = self.history_manager.get_statistics(project_name)

            comparison = {
                "total_duration": self._compare_duration(
                    current_summary["total_duration"],
                    history_stats["average_duration"]
                )
            }

            # 对比各阶段
            stage_comparison = {}
            for stage_time in current_summary["stage_times"]:
                stage_name = stage_time["stage_name"]
                stage_history_stats = self.history_manager.get_statistics(
                    project_name,
                    stage_name
                )

                stage_comparison[stage_name] = self._compare_duration(
                    stage_time["duration"],
                    stage_history_stats["average_duration"]
                )

            comparison["stages"] = stage_comparison

            return comparison

        except Exception as e:
            logger.error(f"性能对比失败: {e}")
            return {}

    def _compare_duration(self, current: float, historical: float) -> dict:
        """
        对比时长

        Args:
            current: 当前时长
            historical: 历史平均时长

        Returns:
            dict: 对比结果
        """
        if historical == 0:
            return {
                "current": current,
                "historical": historical,
                "change_percent": 0.0,
                "status": "unknown"
            }

        change_percent = ((current - historical) / historical) * 100

        if change_percent > 0:
            status = "degraded"  # 性能下降
        elif change_percent < 0:
            status = "improved"  # 性能提升
        else:
            status = "stable"  # 稳定

        return {
            "current": current,
            "historical": historical,
            "change_percent": change_percent,
            "status": status
        }

    def detect_anomalies(self, project_name: str, current_summary: dict, threshold: float = 1.5) -> List[dict]:
        """
        检测性能异常

        Args:
            project_name: 项目名称
            current_summary: 当前执行汇总
            threshold: 异常阈值（倍数，默认1.5表示超过平均50%）

        Returns:
            List[dict]: 异常列表
        """
        try:
            anomalies = []

            # 检查各阶段
            for stage_time in current_summary["stage_times"]:
                stage_name = stage_time["stage_name"]

                # 获取历史统计数据
                stage_history_stats = self.history_manager.get_statistics(
                    project_name,
                    stage_name
                )

                if stage_history_stats["count"] == 0:
                    # 没有历史数据，无法判断
                    continue

                avg_duration = stage_history_stats["average_duration"]
                current_duration = stage_time["duration"]

                # 检查是否异常
                if current_duration > avg_duration * threshold:
                    anomalies.append({
                        "stage_name": stage_name,
                        "current_duration": current_duration,
                        "average_duration": avg_duration,
                        "exceed_factor": current_duration / avg_duration
                    })

            return anomalies

        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            return []

    def generate_optimization_suggestions(self, project_name: str, current_summary: dict) -> List[str]:
        """
        生成优化建议

        Args:
            project_name: 项目名称
            current_summary: 当前执行汇总

        Returns:
            List[str]: 优化建议列表
        """
        try:
            suggestions = []

            # 检测异常
            anomalies = self.detect_anomalies(project_name, current_summary)

            if anomalies:
                suggestions.append("发现以下性能异常：")
                for anomaly in anomalies:
                    suggestions.append(
                        f"  - {anomaly['stage_name']} "
                        f"当前耗时 {anomaly['current_duration']:.2f} 秒，"
                        f"比平均耗时高 {anomaly['exceed_factor'] * 100 - 100:.1f}%"
                    )
                suggestions.append("")

            # 对比历史
            comparison = self.compare_with_history(project_name, current_summary)

            # 检查整体性能变化
            total_comparison = comparison.get("total_duration", {})
            if total_comparison.get("status") == "degraded":
                suggestions.append(
                    f"⚠️ 整体性能下降 {total_comparison['change_percent']:.1f}%，"
                    f"建议检查最慢阶段：{current_summary['slowest_stage']['stage_name']}"
                )
            elif total_comparison.get("status") == "improved":
                suggestions.append(
                    f"✅ 整体性能提升 {-total_comparison['change_percent']:.1f}%"
                )

            # 检查特定阶段
            stage_comparison = comparison.get("stages", {})
            for stage_name, comp in stage_comparison.items():
                if comp["status"] == "degraded":
                    suggestions.append(
                        f"  - {stage_name} 性能下降 {comp['change_percent']:.1f}%"
                    )

            if not suggestions:
                suggestions.append("未发现明显的性能问题，系统运行正常。")

            return suggestions

        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")
            return []
```

### 代码示例

**完整示例：src/core/models.py（执行时间模型）**：
```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict

class StageExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class StageExecutionTime:
    """阶段执行时间记录"""
    stage_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status: StageExecutionStatus = StageExecutionStatus.PENDING

    def to_dict(self) -> dict:
        return {
            "stage_name": self.stage_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "status": self.status.value
        }

@dataclass
class StageTimeSummary:
    """阶段时间摘要"""
    stage_name: str
    duration: float
    status: str

@dataclass
class WorkflowExecutionSummary:
    """工作流执行汇总"""
    total_duration: float
    slowest_stage: StageTimeSummary
    fastest_stage: StageTimeSummary
    stage_times: List[StageTimeSummary]
    success_rate: float
    timestamp: str

    def calculate_statistics(self):
        """计算统计数据"""
        if not self.stage_times:
            return

        completed_times = [t for t in self.stage_times if t.status == "completed"]
        if completed_times:
            self.total_duration = sum(t.duration for t in completed_times)
            self.slowest_stage = max(completed_times, key=lambda x: x.duration)
            self.fastest_stage = min(completed_times, key=lambda x: x.duration)

        total_stages = len(self.stage_times)
        completed_count = len(completed_times)
        self.success_rate = completed_count / total_stages if total_stages > 0 else 0.0

    def format_summary(self) -> str:
        """格式化汇总信息"""
        lines = [
            "=" * 50,
            "工作流执行汇总",
            "=" * 50,
            f"总耗时: {self.total_duration:.2f} 秒",
            f"成功率: {self.success_rate * 100:.1f}%",
            ""
        ]

        if self.slowest_stage:
            lines.append(f"最慢阶段: {self.slowest_stage.stage_name}")
            lines.append(f"  执行时长: {self.slowest_stage.duration:.2f} 秒")
            lines.append("")

        if self.fastest_stage:
            lines.append(f"最快阶段: {self.fastest_stage.stage_name}")
            lines.append(f"  执行时长: {self.fastest_stage.duration:.2f} 秒")
            lines.append("")

        lines.append("各阶段耗时：")
        for stage_time in self.stage_times:
            status_mark = "✅" if stage_time.status == "completed" else "❌"
            duration_str = f"{stage_time.duration:.2f} 秒" if stage_time.duration else "未完成"
            lines.append(f"  {status_mark} {stage_time.stage_name}: {duration_str}")

        lines.append("=" * 50)

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "total_duration": self.total_duration,
            "slowest_stage": {
                "stage_name": self.slowest_stage.stage_name,
                "duration": self.slowest_stage.duration,
                "status": self.slowest_stage.status
            } if self.slowest_stage else None,
            "fastest_stage": {
                "stage_name": self.fastest_stage.stage_name,
                "duration": self.fastest_stage.duration,
                "status": self.fastest_stage.status
            } if self.fastest_stage else None,
            "stage_times": [
                {
                    "stage_name": t.stage_name,
                    "duration": t.duration,
                    "status": t.status
                }
                for t in self.stage_times
            ],
            "success_rate": self.success_rate,
            "timestamp": self.timestamp
        }
```

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 3 - Story 3.3](../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-051](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-052](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-053](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-054](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 3.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 4.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 5.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-003](../planning-artifacts/architecture.md)

## Dev Agent Record

### Agent Model Used

zai/glm-4.7 (Subagent: Story 3.3 Creation)

### Debug Log References

None

### Completion Notes List

**实现摘要**：
- Story 3.3 implementation 文件已创建
- 包含13个主要任务，总计85个子任务
- 定义了两个核心数据模型：StageExecutionTime 和 WorkflowExecutionSummary
- 设计了完整的时间记录、日志输出、汇总显示、历史记录、性能分析、报告导出等功能
- 所有任务都遵循 BMAD implementation 文件格式

**核心功能模块**：
1. **时间记录模块**：使用 time.monotonic() 记录各阶段开始/结束时间，计算执行时长
2. **日志输出模块**：格式化输出 `[阶段名称] 执行时长: XX.XX 秒`
3. **汇总显示模块**：计算并显示总耗时、最慢阶段、最快阶段、成功率
4. **历史记录模块**：保存每次执行到 JSON 文件，支持查询和统计
5. **性能分析模块**：对比历史数据，检测异常，生成优化建议
6. **UI 显示模块**：在进度面板显示实时时间，在汇总面板显示可视化图表
7. **报告导出模块**：支持 CSV、Markdown、HTML 格式导出

**数据模型设计**：
- StageExecutionTime：记录单个阶段的执行时间和状态
- WorkflowExecutionSummary：汇总整个工作流的执行信息和统计数据
- StageTimeSummary：阶段时间摘要，用于汇总和比较

**技术约束**：
- 必须使用 time.monotonic() 确保时间记录的准确性
- 跨线程信号必须使用 Qt.ConnectionType.QueuedConnection
- 日志格式必须统一：`[阶段名称] 执行时长: XX.XX 秒`
- 时间精度保留2位小数
- 历史记录保留最近100条

**测试要求**：
- 单元测试：验证数据模型、时间计算、日志格式、汇总计算、性能分析算法等
- 集成测试：验证完整的执行时间记录流程、多阶段汇总、历史记录、UI显示等
- 端到端测试：验证从构建开始到完成的完整时间记录和报告导出

**文件创建**：
- implementation-artifacts/stories/3-3-record-and-display-stage-execution-time.md（本文档）

### File List

#### 待创建的文件

**源文件**：
1. **src/core/models.py**（修改）
   - 添加 StageExecutionTime 数据类
   - 添加 WorkflowExecutionSummary 数据类
   - 添加 StageTimeSummary 数据类

2. **src/core/workflow_thread.py**（修改）
   - 添加 stage_times 字典
   - 添加时间记录逻辑（开始/结束）
   - 添加阶段时间日志输出
   - 添加汇总信息生成
   - 添加实时时间更新定时器

3. **src/ui/widgets/progress_panel.py**（修改）
   - 扩展显示阶段执行时间列
   - 添加实时时间更新
   - 添加格式化时间显示

4. **src/ui/widgets/execution_summary_panel.py**（新建）
   - 创建执行汇总面板类
   - 显示总耗时、最慢/最快阶段
   - 添加耗时图表（QBarSeries）
   - 添加"查看历史记录"按钮

5. **src/utils/execution_time.py**（新建）
   - 创建 ExecutionTimeHistory 类
   - 实现历史记录保存/加载
   - 实现统计信息查询

6. **src/utils/performance_analyzer.py**（新建）
   - 创建 PerformanceAnalyzer 类
   - 实现性能对比功能
   - 实现异常检测
   - 实现优化建议生成

7. **src/utils/report_generator.py**（新建）
   - 创建 ExecutionTimeReport 类
   - 实现 CSV 导出
   - 实现 Markdown 导出
   - 实现 HTML 导出

**测试文件**：
1. **tests/unit/test_execution_time_models.py**（新建）
   - 测试 StageExecutionTime 数据类
   - 测试 WorkflowExecutionSummary 数据类
   - 测试序列化/反序列化

2. **tests/unit/test_execution_time_tracking.py**（新建）
   - 测试开始/结束时间记录
   - 测试时长计算
   - 测试日志输出格式

3. **tests/unit/test_performance_analyzer.py**（新建）
   - 测试性能对比算法
   - 测试异常检测
   - 测试优化建议生成

4. **tests/integration/test_execution_time.py**（新建）
   - 测试完整的执行时间记录流程
   - 测试多阶段汇总
   - 测试历史记录和查询
   - 测试性能分析和报告导出

#### 文件统计

- 待修改的源文件：3 个
- 待创建的源文件：4 个
- 待创建的测试文件：4 个
- 总任务数：13 个任务
- 总子任务数：85 个
- 预计代码行数：~6000 行（源文件 + 测试文件）
