# Story 2.7: 移动代码文件到指定目录

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要系统自动移动处理后的代码文件，
以便更新 IAR 工程的源代码。

## Acceptance Criteria

**Given** 代码文件已提取和处理
**When** 系统执行文件移动操作
**Then** 系统清空目标目录（MATLAB 代码路径）
**And** 系统移动所有代码文件到目标目录
**And** 系统验证每个文件移动操作的成功性
**And** 系统记录所有文件操作到日志
**And** 如果移动失败，系统报告具体文件和错误原因

## Tasks / Subtasks

- [x] 任务 1: 创建文件移动工具函数 (AC: Then - 移动代码文件)
  - [x] 1.1 在 `src/utils/file_ops.py` 创建 `move_code_files()` 函数
  - [x] 1.2 实现目录清空功能（可选确认）
  - [x] 1.3 实现原子性文件移动（复制-验证-删除）
  - [x] 1.4 验证每个文件移动的成功性
  - [x] 1.5 使用 `pathlib.Path` 处理所有路径

- [x] 任务 2: 实现目录清空逻辑 (AC: Then - 清空目标目录)
  - [x] 2.1 实现 `clear_directory_safely()` 函数
  - [x] 2.2 支持可选的备份功能
  - [x] 2.3 记录清空的文件列表
  - [x] 2.4 处理目录不存在的情况（自动创建）
  - [x] 2.5 处理权限不足错误

- [x] 任务 3: 实现文件移动验证 (AC: And - 验证移动成功)
  - [x] 3.1 实现 `verify_file_moved()` 函数
  - [x] 3.2 验证文件存在性
  - [x] 3.3 验证文件大小一致性
  - [x] 3.4 验证文件可读性
  - [x] 3.5 生成验证报告

- [x] 任务 4: 实现阶段执行器 (AC: Given - 从前序阶段读取)
  - [x] 4.1 在 `src/stages/` 创建 `file_move.py` 阶段执行器
  - [x] 4.2 实现 `execute_stage(config, context) -> StageResult`
  - [x] 4.3 从 `context.state["processed_files"]` 读取文件列表
  - [x] 4.4 从 `context.config` 读取目标目录路径
  - [x] 4.5 将移动后的文件列表保存到 `context.state["moved_files"]`

- [x] 任务 5: 实现错误处理和恢复
  - [x] 5.1 处理目标目录不可写错误
  - [x] 5.2 处理磁盘空间不足错误
  - [x] 5.3 处理部分文件移动失败（回滚已移动的文件）
  - [x] 5.4 提供可操作的修复建议
  - [x] 5.5 记录详细的操作日志

- [x] 任务 6: 集成到工作流引擎
  - [x] 6.1 在 `src/core/workflow.py` 的 `STAGE_EXECUTORS` 中注册 `file_move`
  - [x] 6.2 指向 `stages.file_move.execute_stage`
  - [x] 6.3 确保阶段在工作流中正确顺序执行（阶段 3）
  - [x] 6.4 将移动后的文件列表传递给下一阶段（IAR 编译）

## Dev Notes

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **ADR-002（防御性编程）**：文件操作前备份，失败后回滚
- **Decision 4.1（原子性文件操作）**：复制-验证-删除模式
- **Decision 4.2（长路径处理）**：使用 `pathlib.Path` 处理 Windows 长路径
- **Decision 5.1（日志框架）**：logging + 实时日志输出

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 阶段接口：使用统一签名 `execute_stage(config, context) -> result`
2. ⭐⭐⭐⭐⭐ 状态传递：从 `context.state["processed_files"]` 读取，写入 `context.state["moved_files"]`
3. ⭐⭐⭐⭐⭐ 路径处理：使用 `pathlib.Path` 处理所有路径
4. ⭐⭐⭐⭐⭐ 日志记录：使用 `context.log_callback` 实时发送日志
5. ⭐⭐⭐⭐⭐ 错误处理：使用 `FileError` 错误类（已存在于 src/utils/errors.py）
6. ⭐⭐⭐⭐⭐ 原子性操作：复制-验证-删除模式
7. ⭐⭐⭐⭐ 超时配置：使用 `DEFAULT_TIMEOUT["file_ops"]`（300 秒）
8. ⭐⭐⭐ 备份策略：移动前可选备份目标目录

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/utils/file_ops.py` | 修改 | 添加文件移动函数 |
| `src/stages/file_move.py` | 新建 | 文件移动阶段执行器 |
| `src/core/workflow.py` | 修改 | 注册 file_move 执行器 |
| `tests/unit/test_file_ops_move.py` | 新建 | 文件移动测试 |
| `tests/unit/test_file_move_stage.py` | 新建 | 文件移动阶段测试 |

**确保符合项目结构**：
```
src/
├── stages/                                    # 工作流阶段
│   ├── base.py                                # 基类（已存在）
│   ├── matlab_gen.py                          # MATLAB 生成阶段（已存在）
│   ├── file_process.py                        # 文件处理阶段（已存在）
│   └── file_move.py                          # 文件移动阶段（新建）
├── core/                                      # 核心业务逻辑
│   ├── workflow.py                            # 工作流编排（修改）
│   └── constants.py                           # DEFAULT_TIMEOUT（已存在）
└── utils/                                     # 工具函数
    └── file_ops.py                            # 文件操作（修改）
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ (64位) | 开发语言 |
| pathlib | 内置 | 路径处理 |
| shutil | 内置 | 文件复制/移动 |
| logging | 内置 | 日志记录 |
| dataclasses | 内置 (3.7+) | 数据模型 |

### 测试标准

**单元测试要求**：
- 测试目录清空功能（有文件/无文件）
- 测试文件移动函数（单个/多个文件）
- 测试原子性操作（复制-验证-删除）
- 测试文件验证功能（存在性、大小、可读性）
- 测试备份功能
- 测试部分失败回滚
- 测试错误处理（权限、磁盘空间、长路径）
- 测试超时处理

**集成测试要求**：
- 测试与文件处理阶段的集成（读取 `processed_files`）
- 测试移动后的文件列表传递给下一阶段
- 测试目标目录不存在时的创建行为

### 依赖关系

**前置故事**：
- ✅ Story 2.5: 执行 MATLAB 代码生成阶段（提供 `matlab_output` 状态）
- ✅ Story 2.6: 提取并处理代码文件（提供 `processed_files` 状态）

**后续故事**：
- Story 2.8: 调用 IAR 命令行编译（使用 `moved_files` 状态）

### 数据流设计

```
execute_stage("file_move", config, context)
    │
    ├─→ 读取处理后的文件列表
    │   │
    │   └─→ processed_files = context.state["processed_files"]
    │           { "c_files": [...], "h_files": [...], "cal_modified": bool }
    │
    ├─→ 读取目标目录配置
    │   │
    │   └─→ target_dir = context.config["matlab_code_path"]
    │
    ├─→ 清空目标目录（可选备份）
    │   │
    │   ├─→ clear_directory_safely(target_dir, backup=True)
    │   └─→ 记录清空的文件列表
    │
    ├─→ 移动所有代码文件
    │   │
    │   ├─→ for file in all_files:
    │   │       ├─→ 复制文件到目标目录
    │   │       ├─→ verify_file_moved(src, dst)
    │   │       ├─→ 验证通过 → 删除源文件
    │   │       └─→ 验证失败 → 回滚已移动的文件
    │
    ├─→ 构建输出状态
    │   │
    │   └─→ context.state["moved_files"] = {
    │           "target_dir": target_dir,
    │           "c_files": [...],
    │           "h_files": [...],
    │           "move_count": int,
    │           "timestamp": str
    │       }
    │
    └─→ 返回 StageResult(COMPLETED)
```

### 文件移动规格

**原子性文件移动流程**：
```
1. 创建目标目录备份（可选）
2. 清空目标目录
3. 对于每个源文件：
   a. 复制文件到目标目录（使用 shutil.copy2 保留元数据）
   b. 验证文件移动成功（存在性、大小、可读性）
   c. 验证通过 → 删除源文件
   d. 验证失败 → 停止移动，回滚已移动的文件
4. 清理备份（如果全部成功）
5. 记录操作结果
```

**文件验证标准**：
- 文件存在于目标目录
- 文件大小与源文件一致
- 文件可读
- 可选：文件哈希值一致（性能考虑，默认禁用）

**错误处理规格**：

| 错误类型 | 错误消息 | 修复建议 |
|---------|---------|---------|
| 目录不可写 | "目标目录不可写: {path}" | 1. 检查目录权限<br>2. 以管理员身份运行<br>3. 检查磁盘是否写保护 |
| 磁盘空间不足 | "磁盘空间不足，需要 {needed}MB，可用 {available}MB" | 1. 清理磁盘空间<br>2. 更换目标磁盘<br>3. 禁用备份功能 |
| 部分文件移动失败 | "{count} 个文件移动失败，已回滚" | 1. 检查失败文件列表<br>2. 检查磁盘空间<br>3. 检查文件权限 |
| 源文件不存在 | "源文件不存在: {path}" | 1. 检查前序阶段是否成功<br>2. 检查文件是否被删除 |
| 验证失败 | "文件验证失败: {path}" | 1. 检查磁盘完整性<br>2. 尝试再次移动<br>3. 跳过验证（不推荐） |

### 前序故事经验

**从 Story 2.6 学到的经验**：

1. **统一阶段接口模式**：
   - 使用 `execute_stage(config, context) -> StageResult` 签名
   - `context.state` 用于阶段间状态传递

2. **错误处理模式**：
   - 使用 `ProcessError` 和 `FileError` 错误类层次
   - 提供可操作的修复建议（`suggestions` 列表）

3. **超时检测模式**：
   - 使用 `time.monotonic()` 而非 `time.time()`
   - 从 `DEFAULT_TIMEOUT` 获取超时值

4. **日志模式**：
   - 使用 `context.log_callback` 实时发送日志
   - 日志格式：`[HH:MM:SS] 消息内容`

5. **文件验证模式**：
   - 操作后验证结果
   - 验证失败返回 `StageResult(FAILED)`

6. **工作流集成模式**：
   - 在 `STAGE_EXECUTORS` 中注册执行器
   - 使用 TYPE_CHECKING 避免循环导入

7. **file_ops 工具模块模式**：
   - 复用 `src/utils/file_ops.py` 模式
   - 函数命名：`<action>_<object>`（如 `move_code_files`）
   - 使用 `pathlib.Path` 处理所有路径

### 性能要求

| 指标 | 要求 | 说明 |
|------|------|------|
| 阶段超时 | 300 秒（5 分钟） | 可通过 `config.timeout` 覆盖 |
| 目录清空 | < 30 秒 | 典型项目（< 1000 文件） |
| 文件移动 | < 60 秒 | 典型项目（< 500 文件） |
| 文件验证 | < 30 秒 | 取决于文件数量和大小 |

### 配置参数

**阶段配置（StageConfig）**：
```python
@dataclass
class FileMoveConfig(StageConfig):
    """文件移动阶段配置"""
    name: str = "file_move"
    enabled: bool = True
    timeout: int = 300  # 5 分钟

    # 特定配置
    target_dir: str = ""  # 从 context.config["matlab_code_path"] 读取
    backup_before_clear: bool = True  # 清空前备份
    verify_after_move: bool = True  # 移动后验证
    skip_verification: bool = False  # 跳过验证（不推荐）
```

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 2 - Story 2.7](../../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-015](../../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 4.1, 4.2](../../planning-artifacts/architecture.md)
- [Source: CLAUDE.md#文件移动规则](../../CLAUDE.md)
- [Source: _bmad-output/implementation-artifacts/stories/2-6-extract-process-code-files.md](../2-6-extract-process-code-files.md)

## Dev Agent Record

### Agent Model Used

claude-opus-4-5-20251101

### Debug Log References

- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Story File: `_bmad-output/implementation-artifacts/stories/2-7-move-code-files-specified-directory.md`
- Epics Source: `_bmad-output/planning-artifacts/epics.md` (Lines 430-446)
- Architecture Source: `_bmad-output/planning-artifacts/architecture.md` (Lines 805-883)
- PRD Source: `_bmad-output/planning-artifacts/prd.md` (FR-015)
- Previous Story: `_bmad-output/implementation-artifacts/stories/2-6-extract-process-code-files.md`

### Completion Notes List

**2026-02-12**
- ✅ 任务 1 完成：在 `src/utils/file_ops.py` 实现了 `move_code_files()`, `clear_directory_safely()`, `verify_file_moved()` 函数
  - 使用 pathlib.Path 处理所有路径
  - 实现原子性复制-验证-删除模式
  - 支持可选的备份和清空功能
- ✅ 任务 2 完成：目录清空功能支持备份、自动创建目录、失败恢复
- ✅ 任务 3 完成：文件验证支持存在性、大小、可读性检查
- ✅ 任务 4 完成：在 `src/stages/file_move.py` 实现阶段执行器
  - 从 context.state 读取 processed_files
  - 从 context.config 读取 matlab_code_path
  - 将 moved_files 保存到 context.state
- ✅ 任务 5 完成：添加 FileError 错误类层次（DirectoryNotWritableError, DiskSpaceError, FileVerificationError）
- ✅ 任务 6 完成：在 workflow.py 注册 file_move 执行器，更新依赖关系

**测试覆盖**：
- 22 个文件操作测试全部通过
- 11 个阶段执行器测试全部通过
- 293 个单元测试全部通过（无回归）

### File List

**新建文件**：
- `src/stages/file_move.py` - 文件移动阶段执行器
- `tests/unit/test_file_ops_move.py` - 文件移动操作测试
- `tests/unit/test_file_move_stage.py` - 文件移动阶段测试

**修改文件**：
- `src/utils/file_ops.py` - 添加 move_code_files(), clear_directory_safely(), verify_file_moved() 函数
- `src/utils/errors.py` - 添加 FileError, DirectoryNotWritableError, DiskSpaceError, FileVerificationError 类
- `src/core/workflow.py` - 注册 file_move 执行器，更新 STAGE_DEPENDENCIES, STAGE_ORDER, REQUIRED_PARAMS
- `tests/unit/test_workflow_validation.py` - 更新 valid_workflow_config fixture 包含 file_move 阶段
