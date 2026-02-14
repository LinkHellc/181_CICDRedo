# Story 2.14: 启用/禁用工作流阶段

Status: todo

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

- [ ] 任务 1: 设计阶段依赖关系数据结构 (AC: And - 系统自动调整依赖阶段)
  - [ ] 1.1 在 `src/core/models.py` 中创建 `StageDependency` 数据类
  - [ ] 1.2 定义字段：stage_name, requires（前置阶段列表）
  - [ ] 1.3 创建阶段依赖关系常量 `STAGE_DEPENDENCIES`
  - [ ] 1.4 定义 5 个阶段的依赖关系：
      - matlab_gen: 无依赖
      - file_process: 依赖 matlab_gen
      - iar_compile: 依赖 file_process
      - a2l_process: 依赖 iar_compile
      - package: 依赖 a2l_process
  - [ ] 1.5 添加单元测试验证依赖关系定义正确性
  - [ ] 1.6 添加单元测试验证循环依赖检测（预期不应有循环依赖）

- [ ] 任务 2: 实现依赖关系自动调整算法 (AC: And - 系统自动调整依赖阶段)
  - [ ] 2.1 在 `src/core/workflow.py` 中创建 `adjust_stage_dependencies()` 函数
  - [ ] 2.2 接受阶段配置列表和依赖关系定义
  - [ ] 2.3 当某阶段被禁用时，自动禁用所有依赖它的后续阶段
  - [ ] 2.4 当某阶段被启用时，不影响其他阶段状态
  - [ ] 2.5 添加单元测试验证禁用前置阶段时的级联禁用
  - [ ] 2.6 添加单元测试验证启用阶段时不影响其他阶段
  - [ ] 2.7 添加单元测试验证多级依赖关系的级联禁用

- [ ] 任务 3: 扩展 StageConfig 数据模型 (AC: All)
  - [ ] 3.1 在 `src/core/models.py` 中确认 `StageConfig` 数据类
  - [ ] 3.2 确认 `enabled` 字段存在（默认为 True）
  - [ ] 3.3 添加 `depends_on` 字段（依赖的阶段列表，只读）
  - [ ] 3.4 添加 `description` 字段（阶段描述，用于UI显示）
  - [ ] 3.5 添加单元测试验证 StageConfig 默认值
  - [ ] 3.6 添加单元测试验证 enabled 字段的读写

- [ ] 任务 4: 实现阶段状态切换函数 (AC: And - 用户可以切换任何阶段的启用状态)
  - [ ] 4.1 在 `src/core/workflow.py` 中创建 `toggle_stage_enabled()` 函数
  - [ ] 4.2 接受阶段名称、目标状态、阶段配置列表
  - [ ] 4.3 查找目标阶段配置
  - [ ] 4.4 更新目标阶段的 enabled 字段
  - [ ] 4.5 调用 `adjust_stage_dependencies()` 自动调整依赖关系
  - [ ] 4.6 返回更新后的阶段配置列表
  - [ ] 4.7 添加单元测试验证切换到 enabled=True
  - [ ] 4.8 添加单元测试验证切换到 enabled=False
  - [ ] 4.9 添加单元测试验证不存在的阶段名称处理

- [ ] 任务 5: 实现阶段配置持久化 (AC: And - 系统保存用户的阶段配置)
  - [ ] 5.1 在 `src/core/config.py` 中创建 `save_stage_config()` 函数
  - [ ] 5.2 接受阶段配置列表和目标文件路径
  - [ ] 5.3 将阶段配置序列化为 JSON 格式
  - [ ] 5.4 保存到指定路径（文件名包含工作流名称）
  - [ ] 5.5 使用 `try-except` 捕获文件操作错误
  - [ ] 5.6 添加单元测试验证保存成功
  - [ ] 5.7 添加单元测试验证权限不足错误处理
  - [ ] 5.8 添加单元测试验证磁盘空间不足错误处理

- [ ] 任务 6: 实现阶段配置加载 (AC: Given - 用户已加载工作流配置)
  - [ ] 6.1 在 `src/core/config.py` 中创建 `load_stage_config()` 函数
  - [ ] 6.2 接受工作流配置文件路径
  - [ ] 6.3 读取 JSON 文件内容
  - [ ] 6.4 反序列化为阶段配置列表
  - [ ] 6.5 使用 `try-except` 捕获文件操作和解析错误
  - [ ] 6.6 验证加载的配置格式正确性
  - [ ] 6.7 返回阶段配置列表
  - [ ] 6.8 添加单元测试验证加载成功
  - [ ] 6.9 添加单元测试验证文件不存在错误处理
  - [ ] 6.10 添加单元测试验证格式错误处理
  - [ ] 6.11 添加单元测试验证缺少必填字段的处理

- [ ] 任务 7: 创建工作流配置管理器 (AC: All)
  - [ ] 7.1 在 `src/core/workflow.py` 中创建 `WorkflowConfigManager` 类
  - [ ] 7.2 添加属性：current_stages（当前阶段配置列表）
  - [ ] 7.3 添加方法：`load_workflow()` - 加载工作流配置
  - [ ] 7.4 添加方法：`save_workflow()` - 保存工作流配置
  - [ ] 7.5 添加方法：`toggle_stage()` - 切换阶段状态（集成任务 4）
  - [ ] 7.6 添加方法：`get_stages()` - 获取所有阶段配置
  - [ ] 7.7 添加方法：`get_enabled_stages()` - 获取启用的阶段
  - [ ] 7.8 添加单元测试验证配置加载
  - [ ] 7.9 添加单元测试验证配置保存
  - [ ] 7.10 添加单元测试验证阶段切换
  - [ ] 7.11 添加单元测试验证获取启用阶段

- [ ] 任务 8: 修改工作流执行引擎支持跳过禁用阶段 (AC: And - 执行时系统跳过禁用的阶段)
  - [ ] 8.1 在 `src/core/workflow.py` 中修改 `execute_workflow()` 函数
  - [ ] 8.2 遍历阶段时检查 `stage.enabled` 字段
  - [ ] 8.3 如果阶段被禁用，记录日志并跳过
  - [ ] 8.4 如果阶段被启用，正常执行
  - [ ] 8.5 添加日志记录跳过的阶段名称
  - [ ] 8.6 添加单元测试验证禁用阶段被跳过
  - [ ] 8.7 添加单元测试验证启用阶段正常执行
  - [ ] 8.8 添加单元测试验证部分阶段禁用的场景

- [ ] 任务 9: 实现工作流配置验证 (AC: All)
  - [ ] 9.1 在 `src/core/config.py` 中创建 `validate_workflow_config()` 函数
  - [ ] 9.2 验证所有必填字段存在
  - [ ] 9.3 验证阶段名称有效性
  - [ ] 9.4 验证依赖关系一致性
  - [ ] 9.5 验证至少有一个阶段被启用
  - [ ] 9.6 返回验证错误列表（空列表表示有效）
  - [ ] 9.7 添加单元测试验证有效配置
  - [ ] 9.8 添加单元测试验证缺少必填字段
  - [ ] 9.9 添加单元测试验证无效阶段名称
  - [ ] 9.10 添加单元测试验证循环依赖检测
  - [ ] 9.11 添加单元测试验证所有阶段被禁用的场景

- [ ] 任务 10: 实现预定义工作流模板加载 (AC: Given - 用户已加载工作流配置)
  - [ ] 10.1 在 `src/core/workflow.py` 中创建 `get_default_workflow_templates()` 函数
  - [ ] 10.2 定义 4 个预定义模板：
      - 完整流程（所有阶段启用）
      - 快速编译（跳过 A2L 更新）
      - 跳过 A2L（禁用 a2l_process）
      - 仅代码生成（仅 matlab_gen 和 file_process）
  - [ ] 10.3 每个模板返回 StageConfig 列表
  - [ ] 10.4 添加单元测试验证完整流程模板
  - [ ] 10.5 添加单元测试验证快速编译模板
  - [ ] 10.6 添加单元测试验证跳过 A2L 模板
  - [ ] 10.7 添加单元测试验证仅代码生成模板

- [ ] 任务 11: 添加配置变更通知机制 (AC: All)
  - [ ] 11.1 在 `WorkflowConfigManager` 中添加 `config_changed` 信号（PyQt6）
  - [ ] 11.2 在 `toggle_stage()` 方法中触发信号
  - [ ] 11.3 在 `save_workflow()` 方法中触发信号
  - [ ] 11.4 在 `load_workflow()` 方法中触发信号
  - [ ] 11.5 添加单元测试验证配置变更信号触发
  - [ ] 11.6 添加单元测试验证信号传递的配置数据

- [ ] 任务 12: 添加配置历史记录功能 (AC: All)
  - [ ] 12.1 在 `WorkflowConfigManager` 中添加 `config_history` 列表
  - [ ] 12.2 每次配置变更前保存当前状态到历史
  - [ ] 12.3 添加 `undo()` 方法恢复上一次配置
  - [ ] 12.4 添加 `redo()` 方法重做撤销的配置
  - [ ] 12.5 限制历史记录数量（默认 10 条）
  - [ ] 12.6 添加单元测试验证撤销功能
  - [ ] 12.7 添加单元测试验证重做功能
  - [ ] 12.8 添加单元测试验证历史记录数量限制

- [ ] 任务 13: 创建工作流编辑器 UI 组件 (AC: When - 用户在工作流配置界面调整阶段开关)
  - [ ] 13.1 在 `src/ui/widgets/workflow_editor.py` 中创建 `WorkflowEditor` 类
  - [ ] 13.2 继承 `QWidget`
  - [ ] 13.3 创建阶段列表视图（QTableWidget 或 QListWidget）
  - [ ] 13.4 为每个阶段显示：名称、描述、启用状态（复选框）
  - [ ] 13.5 添加启用/禁用切换控件（QCheckBox）
  - [ ] 13.6 连接复选框状态变化到 `toggle_stage()` 方法
  - [ ] 13.7 添加配置变更通知显示
  - [ ] 13.8 添加 UI 测试验证复选框切换功能
  - [ ] 13.9 添加 UI 测试验证依赖关系级联显示

- [ ] 任务 14: 添加工作流预览功能 (AC: Then - 系统显示所有阶段的启用/禁用状态)
  - [ ] 14.1 在 `WorkflowEditor` 中添加 `refresh_preview()` 方法
  - [ ] 14.2 显示启用的阶段列表（绿色标记）
  - [ ] 14.3 显示禁用的阶段列表（灰色标记）
  - [ ] 14.4 显示阶段依赖关系（使用箭头或缩进）
  - [ ] 14.5 添加预计执行时间计算
  - [ ] 14.6 添加 UI 测试验证预览显示正确性

- [ ] 任务 15: 集成到主窗口 (AC: All)
  - [ ] 15.1 在 `src/ui/main_window.py` 中添加工作流编辑器
  - [ ] 15.2 添加"编辑工作流"按钮或菜单项
  - [ ] 15.3 添加工作流模板选择下拉框
  - [ ] 15.4 连接模板选择到加载模板方法
  - [ ] 15.5 连接工作流编辑器的保存按钮到主窗口
  - [ ] 15.6 添加集成测试验证编辑工作流流程
  - [ ] 15.7 添加集成测试验证模板选择功能
  - [ ] 15.8 添加集成测试验证配置持久化

- [ ] 任务 16: 添加配置导入导出功能 (AC: And - 系统保存用户的阶段配置)
  - [ ] 16.1 在 `WorkflowConfigManager` 中添加 `export_config()` 方法
  - [ ] 16.2 在 `WorkflowConfigManager` 中添加 `import_config()` 方法
  - [ ] 16.3 支持导出为 JSON 文件
  - [ ] 16.4 支持从 JSON 文件导入
  - [ ] 16.5 添加文件选择对话框（QFileDialog）
  - [ ] 16.6 添加单元测试验证导出功能
  - [ ] 16.7 添加单元测试验证导入功能
  - [ ] 16.8 添加单元测试验证格式错误处理

- [ ] 任务 17: 添加错误处理和可操作建议 (AC: All)
  - [ ] 17.1 在 `src/utils/errors.py` 中创建 `WorkflowConfigError` 错误类
  - [ ] 17.2 在 `src/utils/errors.py` 中创建 `StageDependencyError` 错误类
  - [ ] 17.3 定义配置加载失败建议：["检查文件路径", "验证文件格式", "查看错误日志"]
  - [ ] 17.4 定义依赖冲突建议：["检查阶段依赖关系", "移除冲突的阶段配置"]
  - [ ] 17.5 定义保存失败建议：["检查目录权限", "检查磁盘空间", "选择其他保存位置"]
  - [ ] 17.6 在各函数中捕获异常并返回带建议的错误信息
  - [ ] 17.7 添加单元测试验证错误处理和返回建议

- [ ] 任务 18: 添加集成测试 (AC: All)
  - [ ] 18.1 创建 `tests/integration/test_workflow_stages.py`
  - [ ] 18.2 测试完整的阶段切换流程（启用→禁用→启用）
  - [ ] 18.3 测试依赖关系级联禁用
  - [ ] 18.4 测试配置加载和保存
  - [ ] 18.5 测试预定义模板加载
  - [ ] 18.6 测试工作流执行时跳过禁用阶段
  - [ ] 18.7 测试配置历史记录（撤销/重做）
  - [ ] 18.8 测试配置导入导出
  - [ ] 18.9 测试 UI 组件交互
  - [ ] 18.10 测试错误恢复场景

- [ ] 任务 19: 添加日志记录 (AC: All)
  - [ ] 19.1 在 `toggle_stage_enabled()` 中添加 INFO 级别日志（阶段状态切换）
  - [ ] 19.2 在 `adjust_stage_dependencies()` 中添加 INFO 级别日志（依赖调整）
  - [ ] 19.3 在 `save_stage_config()` 中添加 INFO 级别日志（配置保存）
  - [ ] 19.4 在 `load_stage_config()` 中添加 INFO 级别日志（配置加载）
  - [ ] 19.5 在 `execute_workflow()` 中添加 INFO 级别日志（跳过禁用阶段）
  - [ ] 19.6 在 `validate_workflow_config()` 中添加 WARNING 级别日志（验证失败）
  - [ ] 19.7 确保日志包含时间戳和详细信息

## Dev Notes

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **ADR-004（混合架构模式）**：业务逻辑用函数，UI 层使用 PyQt6 类
- **Decision 1.1（阶段接口模式）**：所有阶段必须遵循 `execute_stage(StageConfig, BuildContext) -> StageResult` 签名
- **Decision 1.2（数据模型）**：使用 dataclass，所有字段提供默认值
- **Decision 3.1（PyQt6 线程 + 信号模式）**：UI 更新使用信号槽机制
- **Decision 5.1（日志框架）**：logging 模块，记录配置变更

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 阶段接口：所有阶段必须遵循 `execute_stage(StageConfig, BuildContext) -> StageResult` 签名
2. ⭐⭐⭐⭐⭐ 数据模型：使用 `dataclass`，所有字段提供默认值
3. ⭐⭐⭐⭐ 状态传递：使用 `BuildContext`，配置信息从 `context.config` 读取
4. ⭐⭐⭐⭐ 日志记录：使用 `logging` 模块，不使用 `print()`
5. ⭐⭐⭐ 配置格式：使用 JSON 格式保存工作流配置
6. ⭐⭐⭐ 错误处理：使用统一的错误类（`WorkflowConfigError`, `StageDependencyError`）
7. ⭐⭐⭐ 信号连接：UI 组件使用信号槽机制，跨线程使用 `QueuedConnection`
8. ⭐⭐ 依赖关系：阶段依赖关系定义为 DAG（有向无环图）

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/core/models.py` | 修改 | 扩展 StageConfig，添加 StageDependency |
| `src/core/workflow.py` | 新建/修改 | 工作流配置管理器、依赖关系调整、执行引擎 |
| `src/core/config.py` | 修改 | 配置加载/保存/验证函数 |
| `src/utils/errors.py` | 新建/修改 | 工作流配置错误类定义 |
| `src/ui/widgets/workflow_editor.py` | 新建 | 工作流编辑器 UI 组件 |
| `src/ui/main_window.py` | 修改 | 集成工作流编辑器到主窗口 |
| `tests/unit/test_workflow_stages.py` | 新建 | 工作流阶段管理单元测试 |
| `tests/unit/test_workflow_config.py` | 新建 | 工作流配置管理单元测试 |
| `tests/integration/test_workflow_stages.py` | 新建 | 工作流阶段管理集成测试 |

**确保符合项目结构**：
```
src/
├── core/                                     # 核心业务逻辑（函数）
│   ├── models.py                             # 数据模型（修改：StageConfig, StageDependency）
│   ├── workflow.py                           # 工作流管理（新建/修改：WorkflowConfigManager）
│   └── config.py                             # 配置管理（修改：save/load/validate）
├── ui/                                       # PyQt6 UI（类）
│   ├── main_window.py                        # 主窗口（修改：集成工作流编辑器）
│   └── widgets/                              # 自定义控件
│       └── workflow_editor.py                # 工作流编辑器（新建）
└── utils/                                    # 工具函数
    └── errors.py                             # 错误类定义（修改：WorkflowConfigError）
tests/
├── unit/
│   ├── test_workflow_stages.py               # 工作流阶段测试（新建）
│   └── test_workflow_config.py               # 工作流配置测试（新建）
└── integration/
    └── test_workflow_stages.py               # 工作流阶段集成测试（新建）
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| PyQt6 | 6.0+ | UI 框架 |
| dataclasses | 内置 (3.7+) | 数据模型 |
| json | 内置 | 配置序列化 |
| logging | 内置 | 日志记录 |
| pathlib | 内置 | 路径处理 |
| typing | 内置 | 类型提示 |
| unittest | 内置 | 单元测试 |

### 测试标准

**单元测试要求**：
- 测试 `StageDependency` 数据类定义
- 测试阶段依赖关系常量 `STAGE_DEPENDENCIES`
- 测试 `adjust_stage_dependencies()` 函数的级联禁用逻辑
- 测试 `toggle_stage_enabled()` 函数的状态切换
- 测试 `save_stage_config()` 和 `load_stage_config()` 函数的持久化
- 测试 `WorkflowConfigManager` 类的所有方法
- 测试 `execute_workflow()` 函数跳过禁用阶段
- 测试 `validate_workflow_config()` 函数的验证逻辑
- 测试预定义工作流模板加载
- 测试配置历史记录（撤销/重做）
- 测试配置导入导出功能

**集成测试要求**：
- 测试完整的阶段切换流程（启用→禁用→启用）
- 测试依赖关系级联禁用
- 测试配置加载和保存的完整流程
- 测试工作流执行时跳过禁用阶段
- 测试 UI 组件与业务逻辑的集成
- 测试错误恢复场景

**UI 测试要求**：
- 测试工作流编辑器的复选框切换功能
- 测试依赖关系级联显示
- 测试工作流预览功能
- 测试模板选择功能
- 测试配置导入导出对话框

### 依赖关系

**前置故事**：
- ✅ Epic 1 全部完成（项目配置管理）
- ✅ Story 2.1: 选择预定义工作流模板
- ✅ Story 2.2: 加载自定义工作流配置
- ✅ Story 2.3: 验证工作流配置有效性
- ✅ Story 2.4: 启动自动化构建流程（工作流执行框架）

**后续故事**：
- Story 2.15: 取消正在执行的构建（可以使用禁用阶段的配置）

### 数据流设计

```
用户操作（UI 层）
    │
    ▼
WorkflowEditor 接收用户输入
    │
    ├─→ 点击复选框 → toggle_stage()
    ├─→ 选择模板 → load_workflow()
    ├─→ 保存配置 → save_workflow()
    └─→ 导入配置 → import_config()
    │
    ▼
WorkflowConfigManager 处理业务逻辑
    │
    ├─→ toggle_stage_enabled()
    │   │
    │   ├─→ 查找目标阶段
    │   ├─→ 更新 enabled 字段
    │   └─→ adjust_stage_dependencies() ← 级联调整
    │       │
    │       ├─→ 遍历所有阶段
    │       ├─→ 如果阶段依赖被禁用的阶段
    │       │   └─→ 将该阶段也禁用
    │       └─→ 记录调整日志
    │
    ├─→ save_workflow()
    │   │
    │   ├─→ 序列化为 JSON
    │   ├─→ 保存到文件
    │   └─→ 触发 config_changed 信号
    │
    └─→ load_workflow()
        │
        ├─→ 从文件读取 JSON
        ├─→ 反序列化为 StageConfig 列表
        ├─→ validate_workflow_config()
        └─→ 触发 config_changed 信号
    │
    ▼
UI 更新（信号槽）
    │
    ├─→ config_changed 信号 → 刷新预览
    ├─→ 刷新阶段列表显示（启用/禁用状态）
    └─→ 更新预计执行时间
    │
    ▼
工作流执行
    │
    ▼
execute_workflow()
    │
    ├─→ 遍历所有阶段
    │   │
    │   ├─→ 检查 stage.enabled
    │   │   │
    │   │   ├─→ False
    │   │   │   │
    │   │   │   ├─→ 记录日志: "跳过阶段: {name}"
    │   │   │   └─→ 继续下一个阶段
    │   │   │
    │   │   └─→ True
    │   │       │
    │   │       ├─→ 记录日志: "执行阶段: {name}"
    │   │       ├─→ 调用 execute_stage()
    │   │       └─→ 处理执行结果
    │   │
    │   └─→ 继续
    │
    └─→ 完成
```

### 阶段依赖关系定义

**依赖关系 DAG（有向无环图）**：
```
matlab_gen (无依赖)
    │
    ▼
file_process (依赖: matlab_gen)
    │
    ▼
iar_compile (依赖: file_process)
    │
    ▼
a2l_process (依赖: iar_compile)
    │
    ▼
package (依赖: a2l_process)
```

**依赖关系配置**：
```python
STAGE_DEPENDENCIES: dict[str, list[str]] = {
    "matlab_gen": [],
    "file_process": ["matlab_gen"],
    "iar_compile": ["file_process"],
    "a2l_process": ["iar_compile"],
    "package": ["a2l_process"],
}
```

**依赖关系规则**：
1. **禁用前置阶段**：自动禁用所有依赖它的后续阶段
2. **启用后置阶段**：不影响前置阶段状态
3. **启用前置阶段**：不影响后置阶段状态（需要手动启用）
4. **至少启用一个阶段**：所有阶段都禁用时阻止保存

### 依赖关系调整算法

```
调整阶段依赖关系
    │
    ▼
检查被禁用的阶段
    │
    ▼
遍历所有其他阶段
    │
    ├─→ 阶段依赖被禁用的阶段？
    │   │
    │   ├─→ 是
    │   │   │
    │   │   ├─→ 将该阶段也禁用
    │   │   ├─→ 记录日志: "自动禁用 {name}（依赖 {disabled_stage}）"
    │   │   └─→ 继续检查是否影响其他阶段
    │   │
    │   └─→ 否
    │       │
    │       └─→ 继续下一个阶段
    │
    ▼
检查是否有循环依赖
    │
    ├─→ 检测到循环依赖？
    │   │
    │   ├─→ 是
    │   │   │
    │   │   ├─→ 抛出 StageDependencyError
    │   │   └─→ 终止操作
    │   │
    │   └─→ 否
    │       │
    │       └─→ 返回调整后的配置
    │
    ▼
完成
```

### 预定义工作流模板

**模板 1: 完整流程**
```python
FULL_WORKFLOW = [
    StageConfig(name="matlab_gen", enabled=True),
    StageConfig(name="file_process", enabled=True),
    StageConfig(name="iar_compile", enabled=True),
    StageConfig(name="a2l_process", enabled=True),
    StageConfig(name="package", enabled=True),
]
```

**模板 2: 快速编译（跳过 A2L）**
```python
QUICK_COMPILE_WORKFLOW = [
    StageConfig(name="matlab_gen", enabled=True),
    StageConfig(name="file_process", enabled=True),
    StageConfig(name="iar_compile", enabled=True),
    StageConfig(name="a2l_process", enabled=False),  # 跳过 A2L 更新
    StageConfig(name="package", enabled=True),
]
```

**模板 3: 跳过 A2L**
```python
SKIP_A2L_WORKFLOW = [
    StageConfig(name="matlab_gen", enabled=True),
    StageConfig(name="file_process", enabled=True),
    StageConfig(name="iar_compile", enabled=True),
    StageConfig(name="a2l_process", enabled=False),  # 跳过 A2L 更新
    StageConfig(name="package", enabled=False),    # 级联禁用
]
```

**模板 4: 仅代码生成**
```python
CODE_GEN_ONLY_WORKFLOW = [
    StageConfig(name="matlab_gen", enabled=True),
    StageConfig(name="file_process", enabled=True),
    StageConfig(name="iar_compile", enabled=False),  # 级联禁用
    StageConfig(name="a2l_process", enabled=False),  # 级联禁用
    StageConfig(name="package", enabled=False),      # 级联禁用
]
```

### 工作流配置文件格式

**JSON 格式**：
```json
{
  "workflow_name": "完整流程",
  "stages": [
    {
      "name": "matlab_gen",
      "enabled": true,
      "timeout": 1800,
      "description": "MATLAB 代码生成"
    },
    {
      "name": "file_process",
      "enabled": true,
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
  ],
  "created_at": "2025-02-02T15:43:00",
  "modified_at": "2025-02-02T16:30:00"
}
```

**文件命名规则**：
- 位置：`%APPDATA%/MBD_CICDKits/workflows/`
- 文件名：`{workflow_name}.workflow.json`
- 示例：`完整流程.workflow.json`, `快速编译.workflow.json`

### 工作流执行跳过逻辑

**跳过规则**：
```python
def execute_workflow(stages: List[StageConfig], context: BuildContext) -> bool:
    """执行工作流，跳过禁用的阶段"""
    for stage in stages:
        # 检查阶段是否启用
        if not stage.enabled:
            context.log_callback(f"跳过阶段: {stage.name}（已禁用）")
            continue  # ← 跳过禁用的阶段

        # 执行启用的阶段
        context.log_callback(f"执行阶段: {stage.name}")
        result = execute_stage(stage, context)

        if result.status == StageStatus.FAILED:
            return False

    return True
```

**日志示例**：
```
[10:30:15] 开始工作流执行
[10:30:15] 执行阶段: matlab_gen
[10:32:30] matlab_gen 完成 ✅
[10:32:30] 执行阶段: file_process
[10:32:45] file_process 完成 ✅
[10:32:45] 跳过阶段: iar_compile（已禁用）
[10:32:45] 跳过阶段: a2l_process（已禁用）
[10:32:45] 跳过阶段: package（已禁用）
[10:32:45] 工作流执行完成
```

### 配置验证规格

**验证规则**：
```python
def validate_workflow_config(stages: List[StageConfig]) -> list[str]:
    """验证工作流配置

    Args:
        stages: 阶段配置列表

    Returns:
        list[str]: 错误列表，空列表表示有效
    """
    errors = []

    # 1. 验证至少有一个阶段被启用
    enabled_stages = [s for s in stages if s.enabled]
    if not enabled_stages:
        errors.append("至少需要启用一个阶段")

    # 2. 验证阶段名称有效性
    valid_names = set(STAGE_DEPENDENCIES.keys())
    for stage in stages:
        if stage.name not in valid_names:
            errors.append(f"无效的阶段名称: {stage.name}")

    # 3. 验证依赖关系一致性
    for stage in stages:
        if not stage.enabled:
            # 检查依赖此阶段的阶段是否也被禁用
            for other_stage in stages:
                if (stage.name in STAGE_DEPENDENCIES.get(other_stage.name, []) and
                    other_stage.enabled):
                    errors.append(
                        f"阶段 {other_stage.name} 依赖 {stage.name}，"
                        f"但 {stage.name} 已被禁用"
                    )

    # 4. 检测循环依赖
    if has_cycle_dependency(stages):
        errors.append("检测到循环依赖，工作流配置无效")

    return errors
```

### 配置历史记录实现

**撤销/重做机制**：
```python
class WorkflowConfigManager:
    """工作流配置管理器"""

    def __init__(self):
        self.current_stages: List[StageConfig] = []
        self.config_history: List[List[StageConfig]] = []
        self.history_index: int = -1
        self.max_history: int = 10

    def toggle_stage(self, stage_name: str, enabled: bool) -> bool:
        """切换阶段状态"""
        # 保存当前状态到历史
        self._save_to_history()

        # 切换阶段状态
        stage = next((s for s in self.current_stages if s.name == stage_name), None)
        if stage:
            stage.enabled = enabled

            # 调整依赖关系
            adjust_stage_dependencies(self.current_stages)

            # 触发信号
            self.config_changed.emit(self.current_stages)

            return True
        return False

    def _save_to_history(self):
        """保存当前状态到历史"""
        # 移除当前位置之后的所有历史（如果有重做操作）
        self.config_history = self.config_history[:self.history_index + 1]

        # 保存当前状态
        self.config_history.append(deepcopy(self.current_stages))

        # 限制历史记录数量
        if len(self.config_history) > self.max_history:
            self.config_history.pop(0)
        else:
            self.history_index += 1

    def undo(self) -> bool:
        """撤销上一次配置变更"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_stages = deepcopy(self.config_history[self.history_index])
            self.config_changed.emit(self.current_stages)
            return True
        return False

    def redo(self) -> bool:
        """重做撤销的配置变更"""
        if self.history_index < len(self.config_history) - 1:
            self.history_index += 1
            self.current_stages = deepcopy(self.config_history[self.history_index])
            self.config_changed.emit(self.current_stages)
            return True
        return False
```

### 日志记录规格

**日志级别使用**：
| 场景 | 日志级别 | 示例 |
|------|---------|------|
| 阶段状态切换 | INFO | "切换阶段状态: matlab_gen → True" |
| 依赖关系调整 | INFO | "自动禁用 file_process（依赖 matlab_gen）" |
| 配置保存 | INFO | "工作流配置已保存: 完整流程.workflow.json" |
| 配置加载 | INFO | "工作流配置已加载: 快速编译.workflow.json" |
| 配置验证失败 | WARNING | "配置验证失败: 至少需要启用一个阶段" |
| 跳过禁用阶段 | INFO | "跳过阶段: a2l_process（已禁用）" |
| 执行启用阶段 | INFO | "执行阶段: matlab_gen" |

**日志格式**：
```
[2025-02-02 15:43:15] [INFO] 加载工作流模板: 完整流程
[2025-02-02 15:43:20] [INFO] 切换阶段状态: a2l_process → False
[2025-02-02 15:43:20] [INFO] 自动禁用 package（依赖 a2l_process）
[2025-02-02 15:43:25] [INFO] 工作流配置已保存: 跳过A2L.workflow.json
[2025-02-02 15:44:00] [INFO] 开始工作流执行
[2025-02-02 15:44:00] [INFO] 执行阶段: matlab_gen
[2025-02-02 15:46:15] [INFO] matlab_gen 完成 ✅
[2025-02-02 15:46:15] [INFO] 执行阶段: file_process
[2025-02-02 15:46:30] [INFO] file_process 完成 ✅
[2025-02-02 15:46:30] [INFO] 执行阶段: iar_compile
[2025-02-02 16:00:00] [INFO] iar_compile 完成 ✅
[2025-02-02 16:00:00] [INFO] 跳过阶段: a2l_process（已禁用）
[2025-02-02 16:00:00] [INFO] 跳过阶段: package（已禁用）
[2025-02-02 16:00:00] [INFO] 工作流执行完成
```

### 代码示例

**完整示例：core/models.py**：
```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class StageConfig:
    """阶段配置"""
    name: str
    enabled: bool = True
    timeout: int = 3600
    description: str = ""
    depends_on: List[str] = field(default_factory=list)

@dataclass
class StageDependency:
    """阶段依赖关系"""
    stage_name: str
    requires: List[str]

# 阶段依赖关系常量
STAGE_DEPENDENCIES: dict[str, list[str]] = {
    "matlab_gen": [],
    "file_process": ["matlab_gen"],
    "iar_compile": ["file_process"],
    "a2l_process": ["iar_compile"],
    "package": ["a2l_process"],
}
```

**完整示例：core/workflow.py**：
```python
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from copy import deepcopy
import logging

from core.models import StageConfig, StageConfig, STAGE_DEPENDENCIES
from utils.errors import WorkflowConfigError, StageDependencyError

logger = logging.getLogger(__name__)

class WorkflowConfigManager(QObject):
    """工作流配置管理器"""

    config_changed = pyqtSignal(list)  # 发送更新后的阶段列表

    def __init__(self):
        super().__init__()
        self.current_stages: List[StageConfig] = []
        self.config_history: List[List[StageConfig]] = []
        self.history_index: int = -1
        self.max_history: int = 10

    def load_workflow(self, workflow_name: str) -> bool:
        """加载工作流模板"""
        from core.workflow import get_default_workflow_templates

        templates = get_default_workflow_templates()
        if workflow_name in templates:
            self.current_stages = deepcopy(templates[workflow_name])
            self._save_to_history()
            self.config_changed.emit(self.current_stages)
            logger.info(f"加载工作流模板: {workflow_name}")
            return True
        return False

    def save_workflow(self, file_path: str) -> bool:
        """保存工作流配置"""
        from core.config import save_stage_config

        try:
            save_stage_config(self.current_stages, file_path)
            logger.info(f"工作流配置已保存: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存工作流配置失败: {e}")
            return False

    def toggle_stage(self, stage_name: str, enabled: bool) -> bool:
        """切换阶段状态"""
        self._save_to_history()

        stage = next((s for s in self.current_stages if s.name == stage_name), None)
        if stage:
            stage.enabled = enabled
            adjust_stage_dependencies(self.current_stages)
            self.config_changed.emit(self.current_stages)
            logger.info(f"切换阶段状态: {stage_name} → {enabled}")
            return True
        return False

    def get_stages(self) -> List[StageConfig]:
        """获取所有阶段配置"""
        return self.current_stages

    def get_enabled_stages(self) -> List[StageConfig]:
        """获取启用的阶段"""
        return [s for s in self.current_stages if s.enabled]

    def _save_to_history(self):
        """保存当前状态到历史"""
        self.config_history = self.config_history[:self.history_index + 1]
        self.config_history.append(deepcopy(self.current_stages))

        if len(self.config_history) > self.max_history:
            self.config_history.pop(0)
        else:
            self.history_index += 1

    def undo(self) -> bool:
        """撤销上一次配置变更"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_stages = deepcopy(self.config_history[self.history_index])
            self.config_changed.emit(self.current_stages)
            logger.info("撤销配置变更")
            return True
        return False

    def redo(self) -> bool:
        """重做撤销的配置变更"""
        if self.history_index < len(self.config_history) - 1:
            self.history_index += 1
            self.current_stages = deepcopy(self.config_history[self.history_index])
            self.config_changed.emit(self.current_stages)
            logger.info("重做配置变更")
            return True
        return False


def adjust_stage_dependencies(stages: List[StageConfig]):
    """调整阶段依赖关系（级联禁用）"""
    for stage in stages:
        if not stage.enabled:
            # 禁用所有依赖此阶段的阶段
            for other_stage in stages:
                if stage.name in STAGE_DEPENDENCIES.get(other_stage.name, []):
                    if other_stage.enabled:
                        other_stage.enabled = False
                        logger.info(
                            f"自动禁用 {other_stage.name}（依赖 {stage.name}）"
                        )


def execute_workflow(stages: List[StageConfig], context: BuildContext) -> bool:
    """执行工作流，跳过禁用的阶段"""
    for stage in stages:
        if not stage.enabled:
            context.log_callback(f"跳过阶段: {stage.name}（已禁用）")
            continue

        context.log_callback(f"执行阶段: {stage.name}")
        result = execute_stage(stage, context)

        if result.status == StageStatus.FAILED:
            return False

    return True


def get_default_workflow_templates() -> dict[str, List[StageConfig]]:
    """获取预定义工作流模板"""
    return {
        "完整流程": [
            StageConfig(name="matlab_gen", enabled=True, description="MATLAB 代码生成"),
            StageConfig(name="file_process", enabled=True, description="文件处理"),
            StageConfig(name="iar_compile", enabled=True, description="IAR 编译"),
            StageConfig(name="a2l_process", enabled=True, description="A2L 处理"),
            StageConfig(name="package", enabled=True, description="文件归纳"),
        ],
        "快速编译": [
            StageConfig(name="matlab_gen", enabled=True, description="MATLAB 代码生成"),
            StageConfig(name="file_process", enabled=True, description="文件处理"),
            StageConfig(name="iar_compile", enabled=True, description="IAR 编译"),
            StageConfig(name="a2l_process", enabled=False, description="A2L 处理（跳过）"),
            StageConfig(name="package", enabled=True, description="文件归纳"),
        ],
        "跳过A2L": [
            StageConfig(name="matlab_gen", enabled=True, description="MATLAB 代码生成"),
            StageConfig(name="file_process", enabled=True, description="文件处理"),
            StageConfig(name="iar_compile", enabled=True, description="IAR 编译"),
            StageConfig(name="a2l_process", enabled=False, description="A2L 处理（跳过）"),
            StageConfig(name="package", enabled=False, description="文件归纳（跳过）"),
        ],
        "仅代码生成": [
            StageConfig(name="matlab_gen", enabled=True, description="MATLAB 代码生成"),
            StageConfig(name="file_process", enabled=True, description="文件处理"),
            StageConfig(name="iar_compile", enabled=False, description="IAR 编译（跳过）"),
            StageConfig(name="a2l_process", enabled=False, description="A2L 处理（跳过）"),
            StageConfig(name="package", enabled=False, description="文件归纳（跳过）"),
        ],
    }
```

**完整示例：ui/widgets/workflow_editor.py**：
```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QCheckBox,
    QPushButton, QLabel, QComboBox
)
from PyQt6.QtCore import Qt
from typing import List
import logging

from core.models import StageConfig
from core.workflow import WorkflowConfigManager, get_default_workflow_templates

logger = logging.getLogger(__name__)

class WorkflowEditor(QWidget):
    """工作流编辑器"""

    def __init__(self, manager: WorkflowConfigManager):
        super().__init__()
        self.manager = manager
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # 模板选择
        template_layout = QHBoxLayout()
        template_label = QLabel("工作流模板:")
        self.template_combo = QComboBox()
        templates = get_default_workflow_templates()
        self.template_combo.addItems(templates.keys())
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_combo)
        template_layout.addStretch()
        layout.addLayout(template_layout)

        # 阶段列表
        self.stage_table = QTableWidget()
        self.stage_table.setColumnCount(4)
        self.stage_table.setHorizontalHeaderLabels(
            ["启用", "阶段名称", "描述", "预计时间"]
        )
        self.stage_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.stage_table)

        # 操作按钮
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存配置")
        self.undo_button = QPushButton("撤销")
        self.redo_button = QPushButton("重做")
        button_layout.addWidget(self.undo_button)
        button_layout.addWidget(self.redo_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        # 预计执行时间
        self.time_label = QLabel("预计执行时间: 0 分钟")
        layout.addWidget(self.time_label)

    def connect_signals(self):
        """连接信号"""
        self.manager.config_changed.connect(self.refresh_preview)
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        self.save_button.clicked.connect(self.on_save)
        self.undo_button.clicked.connect(self.on_undo)
        self.redo_button.clicked.connect(self.on_redo)
        self.stage_table.cellChanged.connect(self.on_stage_changed)

    def refresh_preview(self, stages: List[StageConfig]):
        """刷新预览"""
        self.stage_table.setRowCount(len(stages))

        for row, stage in enumerate(stages):
            # 启用状态（复选框）
            checkbox = QCheckBox()
            checkbox.setChecked(stage.enabled)
            checkbox.blockSignals(True)  # 防止触发 cellChanged
            self.stage_table.setCellWidget(row, 0, checkbox)
            checkbox.blockSignals(False)

            # 阶段名称
            name_item = QTableWidgetItem(stage.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.stage_table.setItem(row, 1, name_item)

            # 描述
            desc_item = QTableWidgetItem(stage.description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.stage_table.setItem(row, 2, desc_item)

            # 预计时间
            time_item = QTableWidgetItem(f"{stage.timeout // 60} 分钟")
            time_item.setFlags(time_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.stage_table.setItem(row, 3, time_item)

            # 根据启用状态设置行颜色
            if not stage.enabled:
                for col in range(4):
                    item = self.stage_table.item(row, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.lightGray)

        # 更新预计执行时间
        total_time = sum(s.timeout for s in stages if s.enabled) // 60
        self.time_label.setText(f"预计执行时间: {total_time} 分钟")

        logger.info(f"工作流预览已刷新，{len([s for s in stages if s.enabled])} 个阶段启用")

    def on_stage_changed(self, row: int, col: int):
        """阶段状态改变"""
        if col == 0:  # 启用状态列
            checkbox = self.stage_table.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox):
                stage_name = self.stage_table.item(row, 1).text()
                enabled = checkbox.isChecked()
                self.manager.toggle_stage(stage_name, enabled)

    def on_template_changed(self, template_name: str):
        """模板改变"""
        self.manager.load_workflow(template_name)

    def on_save(self):
        """保存配置"""
        # 触发主窗口的保存逻辑
        self.parent().parent().save_workflow_config()

    def on_undo(self):
        """撤销"""
        self.manager.undo()

    def on_redo(self):
        """重做"""
        self.manager.redo()
```

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 2 - Story 2.14](../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-044](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-045](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-006](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 1.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 1.2](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 3.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 5.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-004](../planning-artifacts/architecture.md)
- [Source: _bmad-output/implementation-artifacts/stories/2-1-select-predefined-workflow-template.md](../implementation-artifacts/stories/2-1-select-predefined-workflow-template.md)
- [Source: _bmad-output/implementation-artifacts/stories/2-2-load-custom-workflow-config.md](../implementation-artifacts/stories/2-2-load-custom-workflow-config.md)
- [Source: _bmad-output/implementation-artifacts/stories/2-3-validate-workflow-config.md](../implementation-artifacts/stories/2-3-validate-workflow-config.md)
- [Source: _bmad-output/implementation-artifacts/stories/2-4-start-automated-build-process.md](../implementation-artifacts/stories/2-4-start-automated-build-process.md)

## Dev Agent Record

### Agent Model Used

(待开发时填写)

### Debug Log References

(待开发时填写)

### Completion Notes List

(待开发时填写)

### File List

(待开发时填写)
