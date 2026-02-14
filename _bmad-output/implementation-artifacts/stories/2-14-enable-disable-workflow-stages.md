# Story 2.14: 启用/禁用工作流阶段

Status: pending

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要启用或禁用工作流中的特定阶段，
以便灵活控制构建流程。

## Acceptance Criteria

**Given** 用户已加载工作流配置
**When** 用户在工作流配置界面调整阶段开关
**Then** 系统显示所有阶段的启用/禁用状态
**And** 用户可以切换任何阶段的启用状态
**And** 系统自动调整依赖阶段（如禁用某阶段，其后续阶段也禁用）
**And** 系统保存用户的阶段配置
**And** 执行时系统跳过禁用的阶段

## Tasks / Subtasks

- [ ] 任务 1: 扩展 StageConfig 数据模型支持启用/禁用 (AC: Then - 显示所有阶段的启用/禁用状态)
  - [ ] 1.1 在 `src/core/models.py` 中确认或修改 `StageConfig` 数据类
  - [ ] 1.2 添加 `enabled: bool = True` 字段（默认启用）
  - [ ] 1.3 确保所有字段提供默认值（Decision 1.2）
  - [ ] 1.4 更新工作流配置文件模板支持 `enabled` 字段
  - [ ] 1.5 添加单元测试验证 StageConfig 的 enabled 字段
  - [ ] 1.6 添加单元测试验证默认值为 True
  - [ ] 1.7 添加单元测试验证序列化/反序列化正确性

- [ ] 任务 2: 定义阶段依赖关系 (AC: And - 系统自动调整依赖阶段)
  - [ ] 2.1 在 `src/core/workflow.py` 中创建阶段依赖关系映射
  - [ ] 2.2 定义 5 个核心阶段的依赖关系：
    - matlab_gen: 无依赖
    - file_process: 依赖 matlab_gen
    - iar_compile: 依赖 file_process
    - a2l_process: 依赖 iar_compile
    - package: 依赖 a2l_process
  - [ ] 2.3 创建 `get_stage_dependencies(stage_name: str) -> list[str]` 函数
  - [ ] 2.4 创建 `get_dependent_stages(stage_name: str) -> list[str]` 函数
  - [ ] 2.5 添加单元测试验证依赖关系映射正确性
  - [ ] 2.6 添加单元测试验证前置依赖获取
  - [ ] 2.7 添加单元测试验证后置依赖获取

- [ ] 任务 3: 实现阶段启用/禁用自动调整逻辑 (AC: And - 系统自动调整依赖阶段)
  - [ ] 3.1 在 `src/core/workflow.py` 中创建 `adjust_stage_dependencies()` 函数
  - [ ] 3.2 接受阶段配置列表和被修改的阶段名称
  - [ ] 3.3 当禁用某阶段时，自动禁用所有后续阶段
  - [ ] 3.4 当启用某阶段时，自动启用所有前置阶段
  - [ ] 3.5 添加单元测试验证禁用阶段时后续阶段自动禁用
  - [ ] 3.6 添加单元测试验证启用阶段时前置阶段自动启用
  - [ ] 3.7 添加单元测试验证多重依赖关系处理
  - [ ] 3.8 添加单元测试验证循环依赖防护（如适用）

- [ ] 任务 4: 创建工作流配置验证函数 (AC: All)
  - [ ] 4.1 在 `src/core/config.py` 中创建 `validate_workflow_config()` 函数
  - [ ] 4.2 验证每个阶段的 `enabled` 字段为布尔值
  - [ ] 4.3 验证依赖关系的完整性（禁用阶段后验证依赖性）
  - [ ] 4.4 返回验证错误列表（空列表表示有效）
  - [ ] 4.5 添加单元测试验证有效配置
  - [ ] 4.6 添加单元测试验证无效 enabled 字段
  - [ ] 4.7 添加单元测试验证依赖关系冲突

- [ ] 任务 5: 实现工作流配置加载时启用/禁用状态读取 (AC: Given - 用户已加载工作流配置)
  - [ ] 5.1 在 `src/core/config.py` 中修改或创建 `load_workflow_config()` 函数
  - [ ] 5.2 读取 JSON 工作流配置文件
  - [ ] 5.3 解析每个阶段的 `enabled` 字段
  - [ ] 5.4 创建 `StageConfig` 对象列表并设置 enabled 状态
  - [ ] 5.5 如果配置文件中缺少 `enabled` 字段，使用默认值 True
  - [ ] 5.6 调用 `validate_workflow_config()` 验证配置
  - [ ] 5.7 添加单元测试验证加载完整配置
  - [ ] 5.8 添加单元测试验证加载缺少 enabled 字段的配置（使用默认值）
  - [ ] 5.9 添加单元测试验证加载无效配置（返回错误）

- [ ] 任务 6: 实现工作流配置保存时启用/禁用状态写入 (AC: And - 系统保存用户的阶段配置)
  - [ ] 6.1 在 `src/core/config.py` 中修改或创建 `save_workflow_config()` 函数
  - [ ] 6.2 接受阶段配置列表
  - [ ] 6.3 将每个阶段的 `enabled` 字段序列化到 JSON
  - [ ] 6.4 保存到指定路径（`%APPDATA%/MBD_CICDKits/workflows/`）
  - [ ] 6.5 使用原子写入（临时文件 + 重命名）保证数据完整性
  - [ ] 6.6 添加单元测试验证保存配置
  - [ ] 6.7 添加单元测试验证保存后可以正确加载
  - [ ] 6.8 添加单元测试验证权限不足错误处理

- [ ] 任务 7: 修改工作流执行引擎支持跳过禁用阶段 (AC: And - 执行时系统跳过禁用的阶段)
  - [ ] 7.1 在 `src/core/workflow.py` 中修改 `execute_workflow()` 函数
  - [ ] 7.2 在执行每个阶段前检查 `config.enabled` 字段
  - [ ] 7.3 如果 `enabled` 为 False，跳过该阶段并记录日志
  - [ ] 7.4 跳过的阶段不计入进度百分比（或使用不同颜色标记）
  - [ ] 7.5 记录跳过的阶段到日志（INFO 级别）
  - [ ] 7.6 添加单元测试验证跳过单个禁用阶段
  - [ ] 7.7 添加单元测试验证跳过多个连续禁用阶段
  - [ ] 7.8 添加单元测试验证跳过中间阶段后继续执行后续启用阶段

- [ ] 任务 8: 添加 UI 组件显示和调整阶段启用/禁用状态 (AC: When - 用户在工作流配置界面调整阶段开关)
  - [ ] 8.1 在 `src/ui/widgets/workflow_editor.py` 中创建工作流编辑器组件
  - [ ] 8.2 使用 QTableWidget 或 QListWidget 显示阶段列表
  - [ ] 8.3 每个阶段行显示：阶段名称、描述、启用/禁用开关（QCheckBox）
  - [ ] 8.4 实现启用/禁用开关的信号连接
  - [ ] 8.5 当用户切换开关时，调用 `adjust_stage_dependencies()` 自动调整
  - [ ] 8.6 更新 UI 显示受影响的阶段（禁用阶段变灰）
  - [ ] 8.7 添加集成测试验证 UI 显示正确
  - [ ] 8.8 添加集成测试验证切换开关触发自动调整
  - [ ] 8.9 添加集成测试验证多个阶段的状态变化

- [ ] 任务 9: 实现错误处理和可操作建议 (AC: All)
  - [ ] 9.1 在 `src/utils/errors.py` 中创建 `WorkflowConfigError` 错误类
  - [ ] 9.2 定义配置加载失败建议：["检查 JSON 格式", "验证字段完整性", "恢复默认配置"]
  - [ ] 9.3 定义配置保存失败建议：["检查目录权限", "确保磁盘空间充足", "尝试保存到其他位置"]
  - [ ] 9.4 定义依赖关系冲突建议：["检查阶段顺序", "验证工作流逻辑", "重新设计依赖关系"]
  - [ ] 9.5 在配置加载/保存函数中捕获异常并返回带建议的 Result
  - [ ] 9.6 添加单元测试验证错误处理

- [ ] 任务 10: 添加集成测试 (AC: All)
  - [ ] 10.1 创建 `tests/integration/test_workflow_stages_enabling.py`
  - [ ] 10.2 测试加载包含禁用阶段的工作流配置
  - [ ] 10.3 测试保存工作流配置后重新加载
  - [ ] 10.4 测试切换阶段启用/禁用状态
  - [ ] 10.5 测试自动依赖调整逻辑
  - [ ] 10.6 测试执行时跳过禁用阶段
  - [ ] 10.7 测试禁用前置阶段后执行后续阶段（预期失败或跳过）
  - [ ] 10.8 测试配置验证逻辑
  - [ ] 10.9 测试 UI 与后端逻辑的集成

- [ ] 任务 11: 添加日志记录 (AC: All)
  - [ ] 11.1 在 `load_workflow_config()` 中添加 DEBUG 级别日志（读取配置）
  - [ ] 11.2 在 `save_workflow_config()` 中添加 INFO 级别日志（保存配置成功）
  - [ ] 11.3 在 `save_workflow_config()` 中添加 ERROR 级别日志（保存失败）
  - [ ] 11.4 在 `execute_workflow()` 中添加 INFO 级别日志（跳过禁用阶段）
  - [ ] 11.5 在 `adjust_stage_dependencies()` 中添加 DEBUG 级别日志（依赖调整）
  - [ ] 11.6 确保日志包含时间戳和详细信息

## Dev Notes

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **ADR-001（渐进式架构）**：MVP 阶段使用简化的函数式架构，启用/禁用状态通过 `enabled` 字段实现
- **ADR-004（混合架构模式）**：UI 层使用 PyQt6 类，业务逻辑使用函数和数据类
- **Decision 1.1（阶段接口模式）**：所有阶段必须遵循 `execute_stage(StageConfig, BuildContext) -> StageResult` 签名
- **Decision 1.2（数据模型）**：使用 dataclass，所有字段提供默认值（enabled 默认 True）
- **Decision 3.1（PyQt6 线程 + 信号模式）**：UI 信号连接必须使用 `QueuedConnection`
- **Decision 5.1（日志框架）**：logging 模块，详细记录配置加载/保存和执行跳过

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 阶段接口：使用统一的 `execute_stage(StageConfig, BuildContext) -> StageResult` 签名
2. ⭐⭐⭐⭐⭐ 数据模型：使用 `dataclass`，所有字段提供默认值
3. ⭐⭐⭐⭐⭐ 状态传递：使用 `BuildContext`，不使用全局变量
4. ⭐⭐⭐⭐ 错误处理：使用统一的错误类（`WorkflowConfigError`）
5. ⭐⭐⭐⭐ 日志记录：使用 `logging` 模块，不使用 `print()`
6. ⭐⭐⭐ 信号连接：跨线程信号必须使用 `QueuedConnection`
7. ⭐⭐⭐ 配置验证：加载和保存时验证配置有效性

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/core/models.py` | 修改 | 扩展 StageConfig 添加 enabled 字段 |
| `src/core/workflow.py` | 新建/修改 | 工作流编排、依赖关系调整、执行引擎 |
| `src/core/config.py` | 修改 | 工作流配置加载/保存、验证 |
| `src/utils/errors.py` | 新建/修改 | 工作流配置错误类定义 |
| `src/ui/widgets/workflow_editor.py` | 新建 | 工作流编辑器 UI 组件 |
| `tests/unit/test_workflow_stages.py` | 新建 | 工作流阶段单元测试 |
| `tests/unit/test_workflow_config.py` | 新建 | 工作流配置单元测试 |
| `tests/integration/test_workflow_stages_enabling.py` | 新建 | 工作流阶段启用/禁用集成测试 |

**确保符合项目结构**：
```
src/
├── core/                                     # 核心业务逻辑（函数）
│   ├── models.py                             # 数据模型（修改）
│   ├── workflow.py                           # 工作流编排（新建/修改）
│   └── config.py                             # 配置管理（修改）
├── ui/                                        # PyQt6 UI（类）
│   └── widgets/                              # 自定义控件
│       └── workflow_editor.py                # 工作流编辑器（新建）
└── utils/                                    # 工具函数
    └── errors.py                              # 错误类定义（新建/修改）
tests/
├── unit/
│   ├── test_workflow_stages.py              # 工作流阶段测试（新建）
│   └── test_workflow_config.py              # 工作流配置测试（新建）
└── integration/
    └── test_workflow_stages_enabling.py     # 阶段启用/禁用集成测试（新建）
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| dataclasses | 内置 (3.7+) | 数据模型 |
| pathlib | 内置 | 路径处理 |
| json | 内置 | 工作流配置格式 |
| logging | 内置 | 日志记录 |
| PyQt6 | 6.x | UI 框架 |
| unittest | 内置 | 单元测试 |

### 测试标准

**单元测试要求**：
- 测试 `StageConfig` 的 `enabled` 字段和默认值
- 测试阶段依赖关系映射的正确性
- 测试 `get_stage_dependencies()` 和 `get_dependent_stages()` 函数
- 测试 `adjust_stage_dependencies()` 函数的自动调整逻辑
- 测试 `validate_workflow_config()` 函数的验证逻辑
- 测试 `load_workflow_config()` 和 `save_workflow_config()` 函数
- 测试 `execute_workflow()` 函数跳过禁用阶段的逻辑
- 测试错误类和错误处理

**集成测试要求**：
- 测试加载包含禁用阶段的工作流配置
- 测试保存工作流配置后重新加载
- 测试切换阶段启用/禁用状态
- 测试自动依赖调整逻辑
- 测试执行时跳过禁用阶段
- 测试配置验证逻辑
- 测试 UI 与后端逻辑的集成

**端到端测试要求**：
- 测试用户在 UI 中切换阶段启用/禁用状态的完整流程
- 测试保存配置后重新加载并执行工作流
- 测试禁用某个阶段后依赖关系的自动调整

### 依赖关系

**前置故事**：
- ✅ Epic 1 全部完成（项目配置管理）
- ✅ Story 2.4: 启动自动化构建流程（工作流执行框架）
- ✅ Story 2.5 至 2.12: 所有工作流阶段实现（提供完整的阶段列表）

**后续故事**：
- Story 2.15: 取消正在执行的构建（可能需要禁用某些阶段后取消）

### 数据流设计

```
用户在 UI 中切换阶段启用/禁用状态
    │
    ▼
UI 组件 (workflow_editor.py)
    │
    ├─→ 用户点击 QCheckBox
    │   │
    │   ├─→ 触发信号 state_changed(bool)
    │   └─→ 连接到槽函数 on_stage_toggled(stage_name, enabled)
    │
    ▼
槽函数调用调整逻辑
    │
    ▼
adjust_stage_dependencies(stages, stage_name, new_enabled)
    │
    ├─→ 如果禁用某阶段
    │   │
    │   ├─→ 调用 get_dependent_stages(stage_name)
    │   │   │
    │   │   └─→ 返回所有后续阶段列表
    │   │
    │   └─→ 设置所有后续阶段的 enabled = False
    │
    └─→ 如果启用某阶段
        │
        ├─→ 调用 get_stage_dependencies(stage_name)
        │   │
        │   └─→ 返回所有前置阶段列表
        │
        └─→ 设置所有前置阶段的 enabled = True
        │
        ▼
更新 UI 显示
    │
    ├─→ 禁用的阶段行变灰
    └─→ 更新 QCheckBox 状态
        │
        ▼
用户点击"保存配置"
    │
    ▼
save_workflow_config(stages, filepath)
    │
    ├─→ 序列化阶段配置到 JSON（包含 enabled 字段）
    ├─→ 原子写入（临时文件 + 重命名）
    ├─→ 记录日志: INFO "工作流配置保存成功"
    │
    └─→ 成功/返回错误
        │
        ▼
用户点击"开始构建"
    │
    ▼
execute_workflow(stages, context)
    │
    ├─→ 遍历每个阶段
    │   │
    │   ├─→ 检查 stage.enabled
    │   │   │
    │   │   ├─→ True → 执行阶段
    │   │   │       │
    │   │   │       ├─→ 调用 execute_stage()
    │   │   │       └─→ 返回 StageResult
    │   │   │
    │   │   └─→ False → 跳过阶段
    │   │           │
    │   │           ├─→ 记录日志: INFO "跳过阶段: {stage_name}"
    │   │           ├─→ 继续下一个阶段
    │   │           └─→ 不计入进度百分比
    │   │
    │   └─→ 处理结果
    │
    └─→ 返回整体执行结果
```

### 阶段依赖关系定义

**5 个核心阶段的依赖关系**：

```python
STAGE_DEPENDENCIES = {
    "matlab_gen": [],           # 无依赖
    "file_process": ["matlab_gen"],
    "iar_compile": ["file_process"],
    "a2l_process": ["iar_compile"],
    "package": ["a2l_process"]
}
```

**依赖关系示例**：
| 阶段名称 | 前置依赖 | 后置依赖 |
|---------|---------|---------|
| matlab_gen | 无 | file_process |
| file_process | matlab_gen | iar_compile |
| iar_compile | file_process | a2l_process |
| a2l_process | iar_compile | package |
| package | a2l_process | 无 |

**自动调整逻辑**：
- 禁用 `file_process` → 自动禁用 `iar_compile`, `a2l_process`, `package`
- 启用 `package` → 自动启用 `a2l_process`, `iar_compile`, `file_process`, `matlab_gen`

### 配置文件格式

**工作流配置 JSON 格式**（新增 `enabled` 字段）：
```json
{
  "workflow_name": "快速编译流程",
  "stages": [
    {
      "name": "matlab_gen",
      "enabled": false,
      "timeout": 1800,
      "description": "MATLAB 代码生成"
    },
    {
      "name": "file_process",
      "enabled": false,
      "timeout": 300,
      "description": "文件处理"
    },
    {
      "name": "iar_compile",
      "enabled": true,
      "timeout": 1200,
      "description": "IAR 编译"
    },
    {
      "name": "a2l_process",
      "enabled": true,
      "timeout": 600,
      "description": "A2L 处理"
    },
    {
      "name": "package",
      "enabled": true,
      "timeout": 300,
      "description": "文件归纳"
    }
  ]
}
```

**配置文件位置**：
- 默认路径：`%APPDATA%/MBD_CICDKits/workflows/`
- 预定义模板：
  - `default_full.workflow.json` - 完整流程（全部启用）
  - `quick_compile.workflow.json` - 快速编译（仅 IAR + A2L + Package）
  - `skip_a2l.workflow.json` - 跳过 A2L（禁用 a2l_process）

### 阶段执行跳过逻辑

**execute_workflow() 伪代码**：
```python
def execute_workflow(stages: List[StageConfig], context: BuildContext) -> bool:
    """执行工作流，跳过禁用的阶段"""
    total_stages = len(stages)
    enabled_stages = [s for s in stages if s.enabled]
    completed_count = 0

    for i, stage in enumerate(stages):
        if not stage.enabled:
            # 跳过禁用的阶段
            logger.info(f"跳过阶段: {stage.name}")
            continue

        # 执行启用的阶段
        progress = int((completed_count / len(enabled_stages)) * 100)
        context.progress_callback(progress, f"正在执行: {stage.name}")

        result = execute_stage(stage, context)

        if result.status == StageStatus.FAILED:
            return False

        completed_count += 1

    return True
```

**进度计算调整**：
- 原进度：`已执行阶段数 / 总阶段数`
- 新进度：`已执行启用阶段数 / 启用阶段总数`
- 目的：禁用阶段不应降低进度百分比

### UI 组件设计

**工作流编辑器布局**：
```
┌─ 工作流编辑器 ─────────────────────────────┐
│                                            │
│  阶段名称          描述          启用       │
│  ───────────────────────────────────────  │
│  ☑ MATLAB代码生成   生成代码        [√]    │
│  ☑ 文件处理        提取文件        [√]    │
│  ☑ IAR编译         编译工程        [√]    │
│  ☐ A2L处理         更新A2L         [ ]    │
│  ☑ 文件归纳        归集文件        [√]    │
│                                            │
│  [保存配置]  [取消]                        │
└────────────────────────────────────────────┘
```

**UI 交互逻辑**：
1. 用户点击 QCheckBox 切换启用/禁用状态
2. 触发 `state_changed` 信号，连接到槽函数
3. 槽函数调用 `adjust_stage_dependencies()` 自动调整
4. 更新 UI 显示（禁用阶段变灰）
5. 保存配置到 JSON 文件

**信号连接示例**：
```python
class WorkflowEditor(QWidget):
    def __init__(self, stages: List[StageConfig]):
        super().__init__()
        self.stages = stages

        # 创建阶段列表
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["阶段名称", "描述", "启用"])

        for i, stage in enumerate(self.stages):
            # 添加复选框
            checkbox = QCheckBox()
            checkbox.setChecked(stage.enabled)
            checkbox.stateChanged.connect(
                lambda state, stage=stage: self.on_stage_toggled(stage, state == Qt.CheckState.Checked.value)
            )
            self.table.setCellWidget(i, 2, checkbox)

    def on_stage_toggled(self, stage: StageConfig, enabled: bool):
        """阶段切换处理"""
        stage.enabled = enabled

        # 自动调整依赖关系
        adjust_stage_dependencies(self.stages, stage.name, enabled)

        # 更新 UI 显示
        self.update_ui()

    def update_ui(self):
        """更新 UI 显示"""
        for i, stage in enumerate(self.stages):
            checkbox = self.table.cellWidget(i, 2)
            checkbox.setChecked(stage.enabled)

            # 禁用阶段变灰
            if not stage.enabled:
                for col in range(self.table.columnCount()):
                    self.table.item(i, col).setBackground(Qt.GlobalColor.lightGray)
```

### 错误处理流程

```
配置加载失败
    │
    ▼
捕获异常 (JSONDecodeError, FileNotFoundError, etc.)
    │
    ▼
创建 WorkflowConfigError
    │
    ├─→ 错误消息: "工作流配置加载失败: {str(e)}"
    ├─→ 修复建议:
    │   ├─→ "检查 JSON 格式"
    │   ├─→ "验证字段完整性"
    │   └─→ "恢复默认配置"
    └─→ 返回错误 Result
        │
        ▼
    UI 显示错误对话框
        │
        ├─→ 显示错误消息
        └─→ 显示修复建议

配置保存失败
    │
    ▼
捕获异常 (PermissionError, OSError, etc.)
    │
    ▼
创建 WorkflowConfigError
    │
    ├─→ 错误消息: "工作流配置保存失败: {str(e)}"
    ├─→ 修复建议:
    │   ├─→ "检查目录权限"
    │   ├─→ "确保磁盘空间充足"
    │   └─→ "尝试保存到其他位置"
    └─→ 返回错误 Result
        │
        ▼
    UI 显示错误对话框
```

### 日志记录规格

**日志级别使用**：
| 场景 | 日志级别 | 示例 |
|------|---------|------|
| 加载配置 | DEBUG | "加载工作流配置: %APPDATA%/MBD_CICDKits/workflows/default.json" |
| 保存配置 | INFO | "工作流配置保存成功: %APPDATA%/MBD_CICDKits/workflows/default.json" |
| 保存配置失败 | ERROR | "工作流配置保存失败: [Errno 13] Permission denied" |
| 跳过阶段 | INFO | "跳过阶段: matlab_gen (已禁用)" |
| 依赖调整 | DEBUG | "调整依赖关系: 禁用 file_process，同时禁用 iar_compile, a2l_process, package" |
| 配置验证失败 | WARNING | "工作流配置验证失败: enabled 字段类型错误" |

**日志格式**：
```
[2025-02-14 16:35:00] [DEBUG] 加载工作流配置: C:\Users\...\AppData\Roaming\MBD_CICDKits\workflows\quick_compile.json
[2025-02-14 16:35:00] [DEBUG] 调整依赖关系: 禁用 a2l_process，同时禁用 package
[2025-02-14 16:35:01] [INFO] 工作流配置保存成功: C:\Users\...\AppData\Roaming\MBD_CICDKits\workflows\quick_compile.json
[2025-02-14 16:35:05] [INFO] 跳过阶段: matlab_gen (已禁用)
[2025-02-14 16:35:05] [INFO] 跳过阶段: file_process (已禁用)
```

### 代码示例

**完整示例：models.py**
```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class StageConfig:
    """阶段配置"""
    name: str
    enabled: bool = True  # 新增：启用/禁用状态，默认启用
    timeout: int = 3600
    description: str = ""
    # ... 其他配置字段
```

**完整示例：workflow.py**
```python
from typing import List
import logging
from core.models import StageConfig

logger = logging.getLogger(__name__)

# 阶段依赖关系映射
STAGE_DEPENDENCIES = {
    "matlab_gen": [],
    "file_process": ["matlab_gen"],
    "iar_compile": ["file_process"],
    "a2l_process": ["iar_compile"],
    "package": ["a2l_process"]
}

def get_stage_dependencies(stage_name: str) -> List[str]:
    """获取阶段的前置依赖"""
    return STAGE_DEPENDENCIES.get(stage_name, [])

def get_dependent_stages(stage_name: str) -> List[str]:
    """获取阶段的后置依赖"""
    dependents = []
    for name, deps in STAGE_DEPENDENCIES.items():
        if stage_name in deps:
            dependents.append(name)
    return dependents

def adjust_stage_dependencies(
    stages: List[StageConfig],
    stage_name: str,
    enabled: bool
) -> None:
    """自动调整阶段依赖关系"""
    if enabled:
        # 启用阶段时，自动启用所有前置阶段
        deps = get_stage_dependencies(stage_name)
        for dep_name in deps:
            stage = next((s for s in stages if s.name == dep_name), None)
            if stage and not stage.enabled:
                stage.enabled = True
                adjust_stage_dependencies(stages, dep_name, True)
    else:
        # 禁用阶段时，自动禁用所有后置阶段
        dependents = get_dependent_stages(stage_name)
        for dep_name in dependents:
            stage = next((s for s in stages if s.name == dep_name), None)
            if stage and stage.enabled:
                stage.enabled = False
                adjust_stage_dependencies(stages, dep_name, False)

def execute_workflow(stages: List[StageConfig], context) -> bool:
    """执行工作流，跳过禁用的阶段"""
    enabled_stages = [s for s in stages if s.enabled]
    completed_count = 0

    for stage in stages:
        if not stage.enabled:
            logger.info(f"跳过阶段: {stage.name} (已禁用)")
            continue

        # 执行阶段
        logger.info(f"执行阶段: {stage.name}")
        result = execute_stage(stage, context)

        if result.status != StageStatus.COMPLETED:
            return False

        completed_count += 1

    return True
```

**完整示例：config.py**
```python
import json
from pathlib import Path
import logging
from typing import List, Tuple
from core.models import StageConfig
from utils.errors import WorkflowConfigError

logger = logging.getLogger(__name__)

def load_workflow_config(filepath: Path) -> Tuple[List[StageConfig], List[str]]:
    """加载工作流配置"""
    try:
        logger.debug(f"加载工作流配置: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        stages = []
        for stage_data in data.get("stages", []):
            stage = StageConfig(
                name=stage_data["name"],
                enabled=stage_data.get("enabled", True),  # 默认启用
                timeout=stage_data.get("timeout", 3600),
                description=stage_data.get("description", "")
            )
            stages.append(stage)

        # 验证配置
        errors = validate_workflow_config(stages)
        if errors:
            raise WorkflowConfigError(
                "工作流配置验证失败",
                suggestions=errors
            )

        return stages, []

    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {e}")
        return [], [f"JSON 格式错误: {str(e)}"]
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return [], [str(e)]

def save_workflow_config(stages: List[StageConfig], filepath: Path) -> Tuple[bool, List[str]]:
    """保存工作流配置"""
    try:
        # 验证配置
        errors = validate_workflow_config(stages)
        if errors:
            return False, errors

        # 序列化
        data = {
            "workflow_name": "自定义工作流",
            "stages": [
                {
                    "name": stage.name,
                    "enabled": stage.enabled,
                    "timeout": stage.timeout,
                    "description": stage.description
                }
                for stage in stages
            ]
        }

        # 原子写入
        temp_path = filepath.with_suffix('.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_path.replace(filepath)

        logger.info(f"工作流配置保存成功: {filepath}")
        return True, []

    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return False, [str(e)]

def validate_workflow_config(stages: List[StageConfig]) -> List[str]:
    """验证工作流配置"""
    errors = []

    for stage in stages:
        # 验证 enabled 字段
        if not isinstance(stage.enabled, bool):
            errors.append(f"阶段 '{stage.name}' 的 enabled 字段必须是布尔值")

        # 验证依赖关系
        if stage.enabled:
            deps = get_stage_dependencies(stage.name)
            for dep_name in deps:
                dep_stage = next((s for s in stages if s.name == dep_name), None)
                if dep_stage and not dep_stage.enabled:
                    errors.append(
                        f"阶段 '{stage.name}' 启用但其依赖 '{dep_name}' 被禁用"
                    )

    return errors
```

**完整示例：utils/errors.py**
```python
class WorkflowConfigError(Exception):
    """工作流配置错误"""
    def __init__(self, message: str, suggestions: list[str] = None):
        super().__init__(message)
        self.suggestions = suggestions or []

    def __str__(self):
        msg = super().__str__()
        if self.suggestions:
            msg += "\n建议操作:\n" + "\n".join(f"  - {s}" for s in self.suggestions)
        return msg
```

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 2 - Story 2.14](../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-044](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-045](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 1.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 1.2](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 3.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-001](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-004](../planning-artifacts/architecture.md)
- [Source: _bmad-output/implementation-artifacts/stories/2-4-start-automated-build-process.md](../implementation-artifacts/stories/2-4-start-automated-build-process.md)
- [Source: _bmad-output/implementation-artifacts/stories/2-11-create-timestamp-target-folder.md](../implementation-artifacts/stories/2-11-create-timestamp-target-folder.md)
