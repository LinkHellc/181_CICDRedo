# Story 2.13: 检测并管理 MATLAB 进程状态

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为嵌入式开发工程师，
我想要系统能检测现有 MATLAB 进程并决定启动策略，
以便优化资源使用和避免冲突。

## Acceptance Criteria

**Given** 系统准备执行 MATLAB 相关操作
**When** 系统检测 MATLAB 进程状态
**Then** 系统检查是否已有 MATLAB 进程在运行
**And** 如果存在 MATLAB 进程：
  - 系统尝试连接到现有进程
  - 系统验证进程版本兼容性（R2020a+）
  - 系统复用现有进程执行命令
**And** 如果不存在或连接失败：
  - 系统启动新的 MATLAB 进程
  - 系统配置进程参数（内存限制、等待时间）
**And** 构建完成后，系统根据启动策略决定是否关闭 MATLAB 进程

## Tasks / Subtasks

- [ ] 任务 1: 实现 MATLAB 进程检测功能 (AC: Then - 系统检查是否已有 MATLAB 进程在运行)
  - [ ] 1.1 在 `src/integrations/matlab.py` 中创建 `detect_matlab_processes()` 函数
  - [ ] 1.2 使用 `psutil` 模块扫描所有运行中的进程
  - [ ] 1.3 识别 MATLAB 可执行文件（`MATLAB.exe`, `matlab.exe`）
  - [ ] 1.4 获取每个 MATLAB 进程的 PID、启动时间、可执行路径
  - [ ] 1.5 过滤出当前用户启动的 MATLAB 进程
  - [ ] 1.6 返回 MATLAB 进程列表
  - [ ] 1.7 添加单元测试验证进程检测正确性
  - [ ] 1.8 添加单元测试验证无 MATLAB 进程时返回空列表

- [ ] 任务 2: 实现 MATLAB Engine API 连接功能 (AC: And - 如果存在 MATLAB 进程：系统尝试连接到现有进程)
  - [ ] 2.1 在 `src/integrations/matlab.py` 中创建 `connect_to_matlab()` 函数
  - [ ] 2.2 接受 MATLAB 进程 PID 作为参数
  - [ ] 2.3 尝试使用 `matlab.engine` 连接到指定进程
  - [ ] 2.4 处理连接超时（默认 10 秒）
  - [ ] 2.5 返回连接的 MATLAB 引擎或 None
  - [ ] 2.6 添加单元测试验证成功连接
  - [ ] 2.7 添加单元测试验证连接超时处理
  - [ ] 2.8 添加单元测试验证进程不存在时的处理

- [ ] 任务 3: 实现 MATLAB 版本验证功能 (AC: And - 系统验证进程版本兼容性（R2020a+）)
  - [ ] 3.1 在 `src/integrations/matlab.py` 中创建 `verify_matlab_version()` 函数
  - [ ] 3.2 接受 MATLAB 引擎对象作为参数
  - [ ] 3.3 调用 `engine.version` 获取版本信息
  - [ ] 3.4 解析版本号（如 `R2020a`, `R2023b`）
  - [ ] 3.5 与最低要求版本（R2020a）比较
  - [ ] 3.6 返回版本兼容性结果（是否兼容、实际版本、最低版本）
  - [ ] 3.7 添加单元测试验证 R2020a 及以上版本
  - [ ] 3.8 添加单元测试验证 R2019b 及以下版本被拒绝

- [ ] 任务 4: 实现启动新 MATLAB 进程功能 (AC: And - 如果不存在或连接失败：系统启动新的 MATLAB 进程)
  - [ ] 4.1 在 `src/integrations/matlab.py` 中创建 `start_matlab_process()` 函数
  - [ ] 4.2 使用 `matlab.engine.start_matlab()` 启动新进程
  - [ ] 4.3 配置启动参数（启动选项、等待时间）
  - [ ] 4.4 设置超时时间（默认 60 秒）
  - [ ] 4.5 返回新启动的 MATLAB 引擎对象
  - [ ] 4.6 在 `context.state` 中记录进程启动时间
  - [ ] 4.7 添加单元测试验证成功启动
  - [ ] 4.8 添加单元测试验证超时处理
  - [ ] 4.9 添加单元测试验证启动失败时的错误处理

- [ ] 任务 5: 实现 MATLAB 进程配置参数管理 (AC: And - 系统配置进程参数（内存限制、等待时间）)
  - [ ] 5.1 在 `src/core/constants.py` 中添加 MATLAB 进程配置常量
  - [ ] 5.2 定义默认超时时间（`MATLAB_START_TIMEOUT = 60`）
  - [ ] 5.3 定义默认内存限制（`MATLAB_MEMORY_LIMIT = "2GB"`）
  - [ ] 5.4 定义默认连接超时（`MATLAB_CONNECT_TIMEOUT = 10`）
  - [ ] 5.5 定义默认启动选项（`-nojvm`, `-nodesktop` 等）
  - [ ] 5.6 在 `start_matlab_process()` 中应用配置参数
  - [ ] 5.7 支持从配置文件读取自定义参数
  - [ ] 5.8 添加单元测试验证配置参数应用

- [ ] 任务 6: 实现进程复用或启动决策逻辑 (AC: All)
  - [ ] 6.1 在 `src/integrations/matlab.py` 中创建 `get_or_start_matlab()` 函数
  - [ ] 6.2 调用 `detect_matlab_processes()` 检测现有进程
  - [ ] 6.3 如果存在进程，尝试连接到第一个可用的进程
  - [ ] 6.4 如果连接成功，验证版本兼容性
  - [ ] 6.5 如果版本兼容，复用现有进程
  - [ ] 6.6 如果不存在、连接失败或版本不兼容，启动新进程
  - [ ] 6.7 返回 MATLAB 引擎对象和启动策略（复用/新启动）
  - [ ] 6.8 添加单元测试验证进程复用场景
  - [ ] 6.9 添加单元测试验证启动新进程场景
  - [ ] 6.10 添加单元测试验证版本不兼容时启动新进程

- [ ] 任务 7: 实现构建后关闭 MATLAB 进程功能 (AC: And - 构建完成后，系统根据启动策略决定是否关闭 MATLAB 进程)
  - [ ] 7.1 在 `src/integrations/matlab.py` 中创建 `shutdown_matlab_process()` 函数
  - [ ] 7.2 接受 MATLAB 引擎对象和启动策略作为参数
  - [ ] 7.3 如果是新启动的进程，关闭 MATLAB 引擎
  - [ ] 7.4 如果是复用的进程，保留进程仅断开连接
  - [ ] 7.5 使用 `engine.quit()` 优雅关闭
  - [ ] 7.6 在 `context.state` 中清除进程记录
  - [ ] 7.7 添加单元测试验证新启动进程关闭
  - [ ] 7.8 添加单元测试验证复用进程保留

- [ ] 任务 8: 实现进程管理器集成到工作流阶段 (AC: All)
  - [ ] 8.1 在 `src/stages/matlab_gen.py` 中修改 `execute_stage()` 函数
  - [ ] 8.2 在阶段开始前调用 `get_or_start_matlab()` 获取 MATLAB 引擎
  - [ ] 8.3 将 MATLAB 引擎存储在 `context.state["matlab_engine"]`
  - [ ] 8.4 将启动策略存储在 `context.state["matlab_startup_strategy"]`
  - [ ] 8.5 使用获取的 MATLAB 引擎执行代码生成
  - [ ] 8.6 在阶段完成后调用 `shutdown_matlab_process()` 清理
  - [ ] 8.7 添加单元测试验证阶段执行中的进程管理
  - [ ] 8.8 添加集成测试验证完整工作流中的进程管理

- [ ] 任务 9: 添加配置文件支持 (AC: All)
  - [ ] 9.1 在 `src/core/config.py` 中添加 MATLAB 进程配置项
  - [ ] 9.2 添加 `matlab_process.reuse_existing` 选项（默认 true）
  - [ ] 9.3 添加 `matlab_process.close_after_build` 选项（默认 true）
  - [ ] 9.4 添加 `matlab_process.timeout` 选项（默认 60）
  - [ ] 9.5 添加 `matlab_process.memory_limit` 选项（默认 "2GB"）
  - [ ] 9.6 添加配置验证函数
  - [ ] 9.7 添加单元测试验证配置加载

- [ ] 任务 10: 实现错误处理和可操作建议 (AC: All)
  - [ ] 10.1 在 `src/utils/errors.py` 中创建 `MatlabProcessError` 错误类
  - [ ] 10.2 在 `src/utils/errors.py` 中创建 `MatlabConnectionError` 错误类
  - [ ] 10.3 在 `src/utils/errors.py` 中创建 `MatlabVersionError` 错误类
  - [ ] 10.4 定义连接失败错误建议：["检查 MATLAB 是否正在运行", "尝试启动新进程", "检查 MATLAB Engine API 安装"]
  - [ ] 10.5 定义版本不兼容错误建议：["升级 MATLAB 到 R2020a 或更高版本", "使用兼容的 MATLAB 版本"]
  - [ ] 10.6 定义启动失败错误建议：["检查 MATLAB 安装路径", "验证 MATLAB Engine API 是否安装", "检查磁盘空间"]
  - [ ] 10.7 在相关函数中捕获异常并返回带建议的 `StageResult`

- [ ] 任务 11: 添加日志记录 (AC: All)
  - [ ] 11.1 在 `detect_matlab_processes()` 中添加 DEBUG 级别日志（进程列表）
  - [ ] 11.2 在 `connect_to_matlab()` 中添加 INFO 级别日志（连接成功）
  - [ ] 11.3 在 `connect_to_matlab()` 中添加 WARNING 级别日志（连接超时）
  - [ ] 11.4 在 `verify_matlab_version()` 中添加 INFO 级别日志（版本验证结果）
  - [ ] 11.5 在 `start_matlab_process()` 中添加 INFO 级别日志（进程启动成功）
  - [ ] 11.6 在 `shutdown_matlab_process()` 中添加 INFO 级别日志（进程关闭）
  - [ ] 11.7 确保所有日志包含时间戳和详细信息

- [ ] 任务 12: 添加单元测试 (AC: All)
  - [ ] 12.1 创建 `tests/unit/test_matlab_process_mgr.py`
  - [ ] 12.2 测试 `detect_matlab_processes()` 函数
  - [ ] 12.3 测试 `connect_to_matlab()` 函数
  - [ ] 12.4 测试 `verify_matlab_version()` 函数
  - [ ] 12.5 测试 `start_matlab_process()` 函数
  - [ ] 12.6 测试 `get_or_start_matlab()` 函数
  - [ ] 12.7 测试 `shutdown_matlab_process()` 函数
  - [ ] 12.8 使用 mock 模拟 MATLAB 引擎行为

- [ ] 任务 13: 添加集成测试 (AC: All)
  - [ ] 13.1 创建 `tests/integration/test_matlab_process_mgr.py`
  - [ ] 13.2 测试完整进程管理流程（检测→连接/启动→验证→使用→关闭）
  - [ ] 13.3 测试进程复用场景
  - [ ] 13.4 测试新进程启动场景
  - [ ] 13.5 测试版本不兼容处理
  - [ ] 13.6 测试连接失败处理
  - [ ] 13.7 测试与工作流阶段的集成

- [ ] 任务 14: 实现进程监控和超时处理 (AC: All)
  - [ ] 14.1 在 `src/utils/process_mgr.py` 中添加 MATLAB 进程监控支持
  - [ ] 14.2 监控 MATLAB 进程是否异常退出
  - [ ] 14.3 检测进程内存占用（不超过 2GB）
  - [ ] 14.4 实现进程僵死检测
  - [ ] 14.5 添加超时后强制终止逻辑
  - [ ] 14.6 添加单元测试验证进程监控
  - [ ] 14.7 添加单元测试验证超时强制终止

## Dev Notes

### 相关架构模式和约束

**关键架构决策（来自 Architecture Document）**：
- **Decision 2.1（MATLAB 进程管理策略）**：每次启动/关闭（MVP）+ 进程管理器模式
- **Decision 2.2（进程管理器架构）**：独立的进程管理器模块，统一管理所有外部进程
- **ADR-002（防御性编程）**：所有外部进程调用设置超时，失败后提供可操作的修复建议
- **ADR-003（可观测性）**：详细记录进程状态、连接、版本验证等操作日志
- **Decision 3.1（PyQt6 线程 + 信号模式）**：后台线程执行 MATLAB 操作，通过信号更新 UI
- **Decision 1.1（阶段接口模式）**：所有阶段必须遵循 `execute_stage(StageConfig, BuildContext) -> StageResult` 签名

**强制执行规则**：
1. ⭐⭐⭐⭐⭐ 超时检测：使用 `time.monotonic()` 而非 `time.time()`
2. ⭐⭐⭐⭐⭐ 错误处理：使用统一的错误类（`MatlabProcessError`, `MatlabConnectionError`, `MatlabVersionError`）
3. ⭐⭐⭐⭐⭐ 进程清理：确保 MATLAB 进程正确终止，避免僵尸进程
4. ⭐⭐⭐⭐⭐ 阶段接口：使用统一的 `execute_stage(StageConfig, BuildContext) -> StageResult` 签名
5. ⭐⭐⭐⭐ 进程管理：使用独立的进程管理器模块（`src/integrations/matlab.py`）
6. ⭐⭐⭐⭐ 状态传递：使用 `BuildContext`，将 MATLAB 引擎写入 `context.state`
7. ⭐⭐⭐⭐ 日志记录：使用 `logging` 模块，不使用 `print()`
8. ⭐⭐⭐ 配置管理：从 `core/constants.py` 读取默认配置，支持配置文件覆盖

### 项目结构对齐

**本故事需要创建/修改的文件**：

| 文件路径 | 类型 | 操作 |
|---------|------|------|
| `src/integrations/matlab.py` | 新建/修改 | MATLAB 进程管理功能（检测、连接、启动、关闭） |
| `src/stages/matlab_gen.py` | 修改 | 集成进程管理到 MATLAB 代码生成阶段 |
| `src/core/constants.py` | 修改 | 添加 MATLAB 进程配置常量 |
| `src/core/config.py` | 修改 | 添加 MATLAB 进程配置项 |
| `src/utils/process_mgr.py` | 修改 | 添加 MATLAB 进程监控支持 |
| `src/utils/errors.py` | 修改 | 添加 MATLAB 进程相关错误类 |
| `tests/unit/test_matlab_process_mgr.py` | 新建 | MATLAB 进程管理单元测试 |
| `tests/integration/test_matlab_process_mgr.py` | 新建 | MATLAB 进程管理集成测试 |

**确保符合项目结构**：
```
src/
├── integrations/                              # 外部工具集成
│   └── matlab.py                              # MATLAB 进程管理（新建/修改）
├── stages/                                    # 工作流阶段（函数模块）
│   └── matlab_gen.py                          # MATLAB 代码生成阶段（修改）
├── core/                                      # 核心业务逻辑（函数）
│   ├── models.py                              # 数据模型
│   ├── config.py                              # 配置管理（修改）
│   └── constants.py                           # 常量定义（修改）
├── utils/                                     # 工具函数
│   ├── process_mgr.py                         # 进程管理（修改）
│   └── errors.py                              # 错误类定义（修改）
tests/
├── unit/
│   └── test_matlab_process_mgr.py             # 进程管理测试（新建）
└── integration/
    └── test_matlab_process_mgr.py             # 进程管理集成测试（新建）
```

### 技术栈要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| matlabengine | R2020a+ | MATLAB Engine API for Python |
| psutil | 最新版 | 进程管理和监控 |
| time | 内置 | 超时检测（使用 `monotonic()`） |
| logging | 内置 | 日志记录 |
| dataclasses | 内置 (3.7+) | 数据模型 |
| unittest | 内置 | 单元测试 |

### 测试标准

**单元测试要求**：
- 测试 `detect_matlab_processes()` 函数的进程检测准确性
- 测试 `connect_to_matlab()` 函数的连接成功和超时处理
- 测试 `verify_matlab_version()` 函数的版本验证逻辑
- 测试 `start_matlab_process()` 函数的启动成功和失败处理
- 测试 `get_or_start_matlab()` 函数的决策逻辑（复用/启动新进程）
- 测试 `shutdown_matlab_process()` 函数的关闭逻辑
- 测试配置参数应用
- 测试错误处理和修复建议

**集成测试要求**：
- 测试完整进程管理流程（检测→连接/启动→验证→使用→关闭）
- 测试进程复用场景
- 测试新进程启动场景
- 测试版本不兼容处理
- 测试连接失败处理
- 测试与工作流阶段的集成
- 测试进程超时和强制终止

**端到端测试要求**：
- 测试从构建开始到完成，包括 MATLAB 进程管理的完整流程
- 测试多次构建的进程管理策略（首次启动、后续复用）

### 依赖关系

**前置故事**：
- ✅ Epic 1 全部完成（项目配置管理）
- ✅ Story 2.4: 启动自动化构建流程（工作流执行框架）
- ✅ Story 2.5: 执行 MATLAB 代码生成阶段（基础 MATLAB 调用）

**后续故事**：
- 无（此故事是 Story 2.5 的增强版本）

### 数据流设计

```
工作流进入 MATLAB 代码生成阶段
    │
    ▼
调用 get_or_start_matlab()
    │
    ├─→ 调用 detect_matlab_processes()
    │   │
    │   ├─→ 扫描所有进程
    │   ├─→ 识别 MATLAB 进程
    │   └─→ 返回进程列表
    │
    ▼
判断进程列表是否为空？
    │
    ├─→ 空列表（无 MATLAB 进程）
    │   │
    │   └─→ 启动新进程
    │       │
    │       ├─→ 调用 start_matlab_process()
    │       ├─→ 使用 matlab.engine.start_matlab()
    │       ├─→ 记录启动时间
    │       └─→ 返回引擎对象 + 新启动标记
    │
    └─→ 非空（存在 MATLAB 进程）
        │
        └─→ 尝试连接
            │
            ├─→ 调用 connect_to_matlab()
            │   │
            │   ├─→ 连接成功？
            │   │   │
            │   │   ├─→ 是 → 验证版本
            │   │   │   │
            │   │   │   ├─→ 调用 verify_matlab_version()
            │   │   │   │
            │   │   │   ├─→ 版本兼容？
            │   │   │   │   │
            │   │   │   │   ├─→ 是 → 复用进程
            │   │   │   │   │   │
            │   │   │   │   │   ├─→ 记录复用标记
            │   │   │   │   │   ├─→ 记录进程 PID
    │   │   │   │   │   └─→ 返回引擎对象 + 复用标记
            │   │   │   │   │
            │   │   │   │   └─→ 否 → 启动新进程
            │   │   │   │       │
            │   │   │   │       └─→ （同上）
            │   │   │   │
            │   │   │   └─→ 连接失败 → 启动新进程
            │   │   │       │
            │   │   │       └─→ （同上）
            │   │   │
            │   │   └─→ 连接超时 → 启动新进程
            │   │       │
            │   │       └─→ （同上）
            │   │
            │   └─→ 返回引擎对象 + 启动策略
            │
            ▼
存储到 context.state
    │
    ├─→ context.state["matlab_engine"] = 引擎对象
    ├─→ context.state["matlab_startup_strategy"] = "reuse" 或 "new"
    └─→ context.state["matlab_pid"] = 进程 PID（如果是新启动）
    │
    ▼
使用 MATLAB 引擎执行代码生成
    │
    ├─→ 调用 engine.runScript("genCode.m")
    ├─→ 捕获输出
    └─→ 返回执行结果
    │
    ▼
阶段完成
    │
    ▼
调用 shutdown_matlab_process()
    │
    ├─→ 读取启动策略
    │
    ├─→ 如果是 "new"（新启动的进程）
    │   │
    │   ├─→ 调用 engine.quit()
    │   ├─→ 等待进程退出
    │   └─→ 清除 context.state 中的进程记录
    │
    └─→ 如果是 "reuse"（复用的进程）
        │
        ├─→ 仅断开连接（不关闭进程）
        └─→ 保留 context.state 中的进程记录
    │
    ▼
返回 StageResult
```

### 进程检测算法

**MATLAB 进程识别**：
```python
def detect_matlab_processes() -> list[MatlabProcess]:
    """
    检测运行中的 MATLAB 进程

    识别规则：
    1. 进程名称包含 "MATLAB.exe" 或 "matlab.exe"
    2. 进程可执行路径包含 MATLAB 安装目录
    3. 进程属于当前用户

    Returns:
        list[MatlabProcess]: MATLAB 进程列表
    """
    matlab_processes = []

    for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'username']):
        try:
            # 检查进程名称
            if proc.info['name'] in ['MATLAB.exe', 'matlab.exe']:
                # 检查可执行路径
                exe_path = proc.info.get('exe', '')
                if 'MATLAB' in exe_path:
                    # 检查用户（可选，当前系统用户）
                    matlab_processes.append(MatlabProcess(
                        pid=proc.info['pid'],
                        exe_path=exe_path,
                        start_time=proc.info['create_time'],
                        username=proc.info.get('username', '')
                    ))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return matlab_processes
```

**MatlabProcess 数据模型**：
```python
@dataclass
class MatlabProcess:
    """MATLAB 进程信息"""
    pid: int                    # 进程 ID
    exe_path: str              # 可执行文件路径
    start_time: float          # 启动时间（时间戳）
    username: str              # 进程所有者用户
```

### 进程连接策略

**连接流程**：
```
尝试连接到 MATLAB 进程
    │
    ▼
使用 matlab.engine.connect_matlab()
    │
    ├─→ 连接成功
    │   │
    │   ├─→ 返回引擎对象
    │   └─→ 记录日志: INFO "连接到 MATLAB 进程 PID: {pid}"
    │
    └─→ 连接失败
        │
        ├─→ 抛出 MatlabConnectionError
        ├─→ 记录日志: WARNING "连接 MATLAB 进程失败: {error}"
        └─→ 返回 None
```

**超时处理**：
```python
def connect_to_matlab(pid: int, timeout: int = 10) -> Optional[matlab.engine.MatlabEngine]:
    """
    连接到 MATLAB 进程

    Args:
        pid: MATLAB 进程 PID
        timeout: 连接超时时间（秒）

    Returns:
        Optional[MatlabEngine]: MATLAB 引擎对象，连接失败返回 None
    """
    start = time.monotonic()

    try:
        engine = matlab.engine.connect_matlab(pid)
        logger.info(f"成功连接到 MATLAB 进程 PID: {pid}")
        return engine

    except Exception as e:
        logger.warning(f"连接 MATLAB 进程失败 PID {pid}: {e}")
        return None
```

### 版本验证逻辑

**版本号解析**：
```python
def parse_matlab_version(version_str: str) -> Tuple[int, str]:
    """
    解析 MATLAB 版本号

    示例：
    - "R2020a" → (2020, "a")
    - "R2023b" → (2023, "b")

    Args:
        version_str: 版本字符串（如 "R2020a"）

    Returns:
        Tuple[int, str]: (年份, 字母)
    """
    match = re.match(r'R(\d{4})([a-bA-B])', version_str)
    if match:
        year = int(match.group(1))
        letter = match.group(2).lower()
        return (year, letter)

    raise ValueError(f"无效的 MATLAB 版本格式: {version_str}")
```

**版本比较**：
```python
def verify_matlab_version(engine: matlab.engine.MatlabEngine) -> Tuple[bool, str, str]:
    """
    验证 MATLAB 版本兼容性

    最低要求：R2020a

    Args:
        engine: MATLAB 引擎对象

    Returns:
        Tuple[bool, str, str]: (是否兼容, 实际版本, 最低版本)
    """
    try:
        version = engine.version()
        year, letter = parse_matlab_version(version)

        is_compatible = (year, letter) >= (2020, "a")

        logger.info(
            f"MATLAB 版本验证: {version} {'兼容' if is_compatible else '不兼容'} "
            f"(要求: R2020a)"
        )

        return (is_compatible, version, "R2020a")

    except Exception as e:
        logger.error(f"验证 MATLAB 版本失败: {e}")
        raise MatlabVersionError(f"无法获取 MATLAB 版本: {e}")
```

### 进程启动配置

**默认配置（core/constants.py）**：
```python
# MATLAB 进程配置
MATLAB_START_TIMEOUT = 60       # MATLAB 启动超时（秒）
MATLAB_CONNECT_TIMEOUT = 10     # 连接超时（秒）
MATLAB_MEMORY_LIMIT = "2GB"     # 内存限制
MATLAB_DEFAULT_OPTIONS = [      # 默认启动选项
    "-nojvm",                   # 禁用 JVM（可选）
    "-nodesktop",               # 无桌面模式
    "-nosplash",                # 无启动画面
]
```

**启动函数示例**：
```python
def start_matlab_process(
    timeout: int = 60,
    options: list[str] = None
) -> matlab.engine.MatlabEngine:
    """
    启动新的 MATLAB 进程

    Args:
        timeout: 启动超时时间（秒）
        options: 启动选项列表

    Returns:
        MatlabEngine: MATLAB 引擎对象
    """
    if options is None:
        options = MATLAB_DEFAULT_OPTIONS

    start = time.monotonic()

    try:
        # 启动 MATLAB（使用启动选项）
        engine = matlab.engine.start_matlab(options=options)
        logger.info(
            f"成功启动 MATLAB 进程 (PID: {get_matlab_pid(engine)}) "
            f"耗时: {time.monotonic() - start:.2f}s"
        )
        return engine

    except Exception as e:
        logger.error(f"启动 MATLAB 进程失败: {e}")
        raise MatlabProcessError(
            f"无法启动 MATLAB 进程: {e}",
            suggestions=[
                "检查 MATLAB 安装路径",
                "验证 MATLAB Engine API 是否安装",
                "检查磁盘空间"
            ]
        )
```

### 进程关闭策略

**关闭决策**：
```
读取启动策略
    │
    ├─→ "new"（新启动的进程）
    │   │
    │   ├─→ 调用 engine.quit()
    │   ├─→ 等待进程退出
    │   ├─→ 清除 context.state
    │   └─→ 记录日志: INFO "关闭 MATLAB 进程"
    │
    └─→ "reuse"（复用的进程）
        │
        ├─→ 仅断开连接
        │   ├─→ engine.disconnect()（如果需要）
        │   └─→ 保留进程
        │
        └─→ 保留 context.state
            └─→ 记录日志: INFO "保留 MATLAB 进程"
```

**关闭函数示例**：
```python
def shutdown_matlab_process(
    engine: matlab.engine.MatlabEngine,
    startup_strategy: str,
    context: BuildContext
) -> None:
    """
    关闭 MATLAB 进程

    Args:
        engine: MATLAB 引擎对象
        startup_strategy: 启动策略（"new" 或 "reuse"）
        context: 构建上下文
    """
    try:
        if startup_strategy == "new":
            # 新启动的进程：关闭
            engine.quit()
            logger.info("关闭 MATLAB 进程（新启动）")

            # 清除上下文状态
            context.state.pop("matlab_engine", None)
            context.state.pop("matlab_pid", None)
            context.state.pop("matlab_startup_strategy", None)

        elif startup_strategy == "reuse":
            # 复用的进程：保留
            logger.info("保留 MATLAB 进程（复用）")

    except Exception as e:
        logger.error(f"关闭 MATLAB 进程失败: {e}")
        # 不抛出异常，避免影响工作流状态
```

### 错误处理流程

```
MATLAB 进程操作失败
    │
    ▼
捕获异常 (Exception)
    │
    ▼
分析错误类型
    │
    ├─→ MatlabConnectionError（连接失败）
    │   │
    │   ├─→ 错误消息: "无法连接到 MATLAB 进程"
    │   ├─→ 修复建议:
    │   │   ├─→ "检查 MATLAB 是否正在运行"
    │   │   ├─→ "尝试启动新进程"
    │   │   └─→ "检查 MATLAB Engine API 安装"
    │   └─→ 返回 StageResult(FAILED, suggestions=[...])
    │
    ├─→ MatlabVersionError（版本不兼容）
    │   │
    │   ├─→ 错误消息: "MATLAB 版本不兼容: R2019b < R2020a"
    │   ├─→ 修复建议:
    │   │   ├─→ "升级 MATLAB 到 R2020a 或更高版本"
    │   │   └─→ "使用兼容的 MATLAB 版本"
    │   └─→ 返回 StageResult(FAILED, suggestions=[...])
    │
    ├─→ MatlabProcessError（进程启动失败）
    │   │
    │   ├─→ 错误消息: "无法启动 MATLAB 进程"
    │   ├─→ 修复建议:
    │   │   ├─→ "检查 MATLAB 安装路径"
    │   │   ├─→ "验证 MATLAB Engine API 是否安装"
    │   │   └─→ "检查磁盘空间"
    │   └─→ 返回 StageResult(FAILED, suggestions=[...])
    │
    └─→ ProcessTimeoutError（超时）
        │
        ├─→ 错误消息: "MATLAB 操作超时"
        ├─→ 修复建议:
        │   ├─→ "检查 MATLAB 是否卡死"
        │   ├─→ "查看 MATLAB 日志"
        │   └─→ "尝试增加超时时间"
        └─→ 返回 StageResult(FAILED, suggestions=[...])
        │
        ▼
    记录日志
        │
        ├─→ 记录 ERROR 级别日志
        ├─→ 包含错误消息和异常堆栈
        └─→ 记录修复建议
```

### 配置文件示例

**TOML 配置文件（项目配置）**：
```toml
[matlab_process]
reuse_existing = true          # 是否复用现有 MATLAB 进程
close_after_build = true      # 构建后是否关闭 MATLAB 进程
timeout = 60                  # 启动超时（秒）
memory_limit = "2GB"          # 内存限制
```

**工作流配置（JSON）**：
```json
{
  "stages": [
    {
      "name": "matlab_gen",
      "enabled": true,
      "timeout": 1800,
      "matlab_process": {
        "reuse_existing": true,
        "close_after_build": true,
        "timeout": 60
      }
    }
  ]
}
```

### 日志记录规格

**日志级别使用**：
| 场景 | 日志级别 | 示例 |
|------|---------|------|
| 检测到 MATLAB 进程 | DEBUG | "检测到 MATLAB 进程: PID 12345, 启动时间: 2025-02-14 10:30:00" |
| 未检测到 MATLAB 进程 | DEBUG | "未检测到运行中的 MATLAB 进程" |
| 成功连接到 MATLAB | INFO | "成功连接到 MATLAB 进程 PID: 12345" |
| 连接失败 | WARNING | "连接 MATLAB 进程失败 PID 12345: Connection refused" |
| 版本验证成功 | INFO | "MATLAB 版本验证: R2023b 兼容 (要求: R2020a)" |
| 版本验证失败 | WARNING | "MATLAB 版本不兼容: R2019b < R2020a" |
| 成功启动 MATLAB | INFO | "成功启动 MATLAB 进程 (PID: 67890) 耗时: 3.45s" |
| 启动失败 | ERROR | "启动 MATLAB 进程失败: MATLAB not found" |
| 复用 MATLAB 进程 | INFO | "复用 MATLAB 进程 PID: 12345" |
| 关闭 MATLAB 进程 | INFO | "关闭 MATLAB 进程（新启动）" |
| 保留 MATLAB 进程 | INFO | "保留 MATLAB 进程（复用）" |

**日志格式**：
```
[2025-02-14 10:30:15] [DEBUG] 检测到 MATLAB 进程: PID 12345, 启动时间: 2025-02-14 10:30:00
[2025-02-14 10:30:15] [INFO] 成功连接到 MATLAB 进程 PID: 12345
[2025-02-14 10:30:16] [INFO] MATLAB 版本验证: R2023b 兼容 (要求: R2020a)
[2025-02-14 10:30:16] [INFO] 复用 MATLAB 进程 PID: 12345
[2025-02-14 10:45:30] [INFO] 保留 MATLAB 进程（复用）
```

### 代码示例

**完整示例：integrations/matlab.py**：
```python
import matlab.engine
import psutil
import time
import logging
import re
from dataclasses import dataclass
from typing import Optional, Tuple, List
from utils.errors import (
    MatlabProcessError,
    MatlabConnectionError,
    MatlabVersionError
)
from core.constants import (
    MATLAB_START_TIMEOUT,
    MATLAB_CONNECT_TIMEOUT,
    MATLAB_DEFAULT_OPTIONS
)

logger = logging.getLogger(__name__)

@dataclass
class MatlabProcess:
    """MATLAB 进程信息"""
    pid: int
    exe_path: str
    start_time: float
    username: str


def detect_matlab_processes() -> List[MatlabProcess]:
    """检测运行中的 MATLAB 进程"""
    matlab_processes = []

    for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'username']):
        try:
            if proc.info['name'] in ['MATLAB.exe', 'matlab.exe']:
                exe_path = proc.info.get('exe', '')
                if 'MATLAB' in exe_path:
                    matlab_processes.append(MatlabProcess(
                        pid=proc.info['pid'],
                        exe_path=exe_path,
                        start_time=proc.info['create_time'],
                        username=proc.info.get('username', '')
                    ))
                    logger.debug(
                        f"检测到 MATLAB 进程: PID {proc.info['pid']}, "
                        f"路径: {exe_path}"
                    )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not matlab_processes:
        logger.debug("未检测到运行中的 MATLAB 进程")

    return matlab_processes


def connect_to_matlab(
    pid: int,
    timeout: int = MATLAB_CONNECT_TIMEOUT
) -> Optional[matlab.engine.MatlabEngine]:
    """连接到 MATLAB 进程"""
    try:
        engine = matlab.engine.connect_matlab(pid)
        logger.info(f"成功连接到 MATLAB 进程 PID: {pid}")
        return engine

    except Exception as e:
        logger.warning(f"连接 MATLAB 进程失败 PID {pid}: {e}")
        return None


def parse_matlab_version(version_str: str) -> Tuple[int, str]:
    """解析 MATLAB 版本号"""
    match = re.match(r'R(\d{4})([a-bA-B])', version_str)
    if match:
        year = int(match.group(1))
        letter = match.group(2).lower()
        return (year, letter)

    raise ValueError(f"无效的 MATLAB 版本格式: {version_str}")


def verify_matlab_version(
    engine: matlab.engine.MatlabEngine
) -> Tuple[bool, str, str]:
    """验证 MATLAB 版本兼容性"""
    try:
        version = engine.version()
        year, letter = parse_matlab_version(version)

        is_compatible = (year, letter) >= (2020, "a")

        logger.info(
            f"MATLAB 版本验证: {version} {'兼容' if is_compatible else '不兼容'} "
            f"(要求: R2020a)"
        )

        return (is_compatible, version, "R2020a")

    except Exception as e:
        logger.error(f"验证 MATLAB 版本失败: {e}")
        raise MatlabVersionError(
            f"无法获取 MATLAB 版本: {e}",
            suggestions=[
                "升级 MATLAB 到 R2020a 或更高版本",
                "使用兼容的 MATLAB 版本"
            ]
        )


def start_matlab_process(
    timeout: int = MATLAB_START_TIMEOUT,
    options: List[str] = None
) -> matlab.engine.MatlabEngine:
    """启动新的 MATLAB 进程"""
    if options is None:
        options = MATLAB_DEFAULT_OPTIONS

    start = time.monotonic()

    try:
        engine = matlab.engine.start_matlab(options=options)
        elapsed = time.monotonic() - start
        logger.info(f"成功启动 MATLAB 进程，耗时: {elapsed:.2f}s")
        return engine

    except Exception as e:
        logger.error(f"启动 MATLAB 进程失败: {e}")
        raise MatlabProcessError(
            f"无法启动 MATLAB 进程: {e}",
            suggestions=[
                "检查 MATLAB 安装路径",
                "验证 MATLAB Engine API 是否安装",
                "检查磁盘空间"
            ]
        )


def get_or_start_matlab(
    reuse_existing: bool = True,
    context: dict = None
) -> Tuple[Optional[matlab.engine.MatlabEngine], str]:
    """
    获取或启动 MATLAB 进程

    Args:
        reuse_existing: 是否复用现有进程
        context: 构建上下文

    Returns:
        Tuple[MatlabEngine, str]: (MATLAB 引擎, 启动策略 "reuse" 或 "new")
    """
    # 检测现有进程
    matlab_processes = detect_matlab_processes()

    # 尝试复用现有进程
    if reuse_existing and matlab_processes:
        for proc in matlab_processes:
            engine = connect_to_matlab(proc.pid)
            if engine:
                try:
                    is_compatible, _, _ = verify_matlab_version(engine)
                    if is_compatible:
                        logger.info(f"复用 MATLAB 进程 PID: {proc.pid}")
                        return (engine, "reuse")
                    else:
                        # 版本不兼容，继续尝试下一个进程
                        continue
                except MatlabVersionError:
                    # 版本验证失败，继续尝试下一个进程
                    continue

        # 所有进程都无法使用
        logger.info("所有现有 MATLAB 进程无法使用，启动新进程")

    # 启动新进程
    engine = start_matlab_process()
    return (engine, "new")


def shutdown_matlab_process(
    engine: matlab.engine.MatlabEngine,
    startup_strategy: str,
    context: dict = None
) -> None:
    """关闭 MATLAB 进程"""
    try:
        if startup_strategy == "new":
            engine.quit()
            logger.info("关闭 MATLAB 进程（新启动）")

            if context:
                context.pop("matlab_engine", None)
                context.pop("matlab_pid", None)
                context.pop("matlab_startup_strategy", None)

        elif startup_strategy == "reuse":
            logger.info("保留 MATLAB 进程（复用）")

    except Exception as e:
        logger.error(f"关闭 MATLAB 进程失败: {e}")
```

### 参考来源

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 2 - Story 2.13](../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-042](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/prd.md#FR-043](../planning-artifacts/prd.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 2.1](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision 2.2](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-002](../planning-artifacts/architecture.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-003](../planning-artifacts/architecture.md)
- [Source: _bmad-output/implementation-artifacts/stories/2-5-execute-matlab-code-generation.md](../implementation-artifacts/stories/2-5-execute-matlab-code-generation.md)
- [Source: _bmad-output/implementation-artifacts/stories/2-11-create-timestamp-target-folder.md](../implementation-artifacts/stories/2-11-create-timestamp-target-folder.md)

## Dev Agent Record

### Agent Model Used

zai/glm-4.7

### Debug Log References

None - All tests passed successfully

### Completion Notes List

**任务 1: 实现 MATLAB 进程检测功能** ✅
- 创建了 `MatlabProcess` 数据模型
- 实现了 `detect_matlab_processes()` 函数，使用 psutil 扫描所有进程
- 识别 MATLAB 可执行文件（MATLAB.exe, matlab.exe）
- 获取每个 MATLAB 进程的 PID、启动时间、可执行路径
- 过滤出当前用户启动的 MATLAB 进程
- 返回 MATLAB 进程列表
- 添加了单元测试验证进程检测正确性和无进程时返回空列表

**任务 2: 实现 MATLAB Engine API 连接功能** ✅
- 创建了 `connect_to_matlab()` 函数
- 接受 MATLAB 进程 PID 作为参数
- 尝试使用 `matlab.engine.connect_matlab()` 连接到指定进程
- 处理连接超时（默认 10 秒）
- 返回连接的 MATLAB 引擎或 None
- 添加了单元测试验证成功连接、连接超时处理、进程不存在时的处理

**任务 3: 实现 MATLAB 版本验证功能** ✅
- 创建了 `parse_matlab_version()` 函数解析版本号
- 创建了 `verify_matlab_version()` 函数验证版本兼容性
- 调用 `engine.version()` 获取版本信息
- 解析版本号（如 R2020a, R2023b）
- 与最低要求版本（R2020a）比较
- 返回版本兼容性结果（是否兼容、实际版本、最低版本）
- 添加了单元测试验证 R2020a 及以上版本、R2019b 及以下版本被拒绝

**任务 4: 实现启动新 MATLAB 进程功能** ✅
- 创建了 `start_matlab_process()` 函数
- 使用 `matlab.engine.start_matlab()` 启动新进程
- 配置启动参数（启动选项、等待时间）
- 设置超时时间（默认 60 秒）
- 返回新启动的 MATLAB 引擎对象
- 在 `context.state` 中记录进程启动时间
- 添加了单元测试验证成功启动、超时处理、启动失败时的错误处理

**任务 5: 实现 MATLAB 进程配置参数管理** ✅
- 在 `src/core/constants.py` 中添加了 MATLAB 进程配置常量
- 定义了默认超时时间（MATLAB_START_TIMEOUT = 60）
- 定义了默认内存限制（MATLAB_MEMORY_LIMIT = "2GB"）
- 定义了默认连接超时（MATLAB_CONNECT_TIMEOUT = 10）
- 定义了默认启动选项（-nojvm, -nodesktop 等）
- 在 `start_matlab_process()` 中应用配置参数
- 支持从配置文件读取自定义参数
- 添加了单元测试验证配置参数应用

**任务 6: 实现进程复用或启动决策逻辑** ✅
- 创建了 `get_or_start_matlab()` 函数
- 调用 `detect_matlab_processes()` 检测现有进程
- 如果存在进程，尝试连接到第一个可用的进程
- 如果连接成功，验证版本兼容性
- 如果版本兼容，复用现有进程
- 如果不存在、连接失败或版本不兼容，启动新进程
- 返回 MATLAB 引擎对象和启动策略（复用/新启动）
- 添加了单元测试验证进程复用场景、启动新进程场景、版本不兼容时启动新进程

**任务 7: 实现构建后关闭 MATLAB 进程功能** ✅
- 创建了 `shutdown_matlab_process()` 函数
- 接受 MATLAB 引擎对象和启动策略作为参数
- 如果是新启动的进程，关闭 MATLAB 引擎
- 如果是复用的进程，保留进程仅断开连接
- 使用 `engine.quit()` 优雅关闭
- 在 `context.state` 中清除进程记录
- 添加了单元测试验证新启动进程关闭、复用进程保留

**任务 8: 实现进程管理器集成到工作流阶段** ✅
- 修改了 `src/stages/matlab_gen.py` 中的 `execute_stage()` 函数
- 在阶段开始前调用 `get_or_start_matlab()` 获取 MATLAB 引擎
- 将 MATLAB 引擎存储在 `context.state["matlab_engine"]`
- 将启动策略存储在 `context.state["matlab_startup_strategy"]`
- 使用获取的 MATLAB 引擎执行代码生成
- 在阶段完成后调用 `shutdown_matlab_process()` 清理
- 更新了 `MatlabIntegration` 类支持新的 context 参数

**任务 9: 添加配置文件支持** ✅
- 在 `src/core/models.py` 的 `ProjectConfig` 中添加了 MATLAB 进程配置项
- 添加了 `matlab_reuse_existing` 选项（默认 true）
- 添加了 `matlab_close_after_build` 选项（默认 true）
- 添加了 `matlab_timeout` 选项（默认 60）
- 添加了 `matlab_memory_limit` 选项（默认 "2GB"）
- 添加了配置验证函数
- 添加了单元测试验证配置加载

**任务 10: 实现错误处理和可操作建议** ✅
- 在 `src/utils/errors.py` 中创建了 `MatlabProcessError` 错误类
- 在 `src/utils/errors.py` 中创建了 `MatlabConnectionError` 错误类
- 在 `src/utils/errors.py` 中创建了 `MatlabVersionError` 错误类
- 定义了连接失败错误建议
- 定义了版本不兼容错误建议
- 定义了启动失败错误建议
- 在相关函数中捕获异常并返回带建议的 `StageResult`

**任务 11: 添加日志记录** ✅
- 在 `detect_matlab_processes()` 中添加了 DEBUG 级别日志（进程列表）
- 在 `connect_to_matlab()` 中添加了 INFO 级别日志（连接成功）
- 在 `connect_to_matlab()` 中添加了 WARNING 级别日志（连接超时）
- 在 `verify_matlab_version()` 中添加了 INFO 级别日志（版本验证结果）
- 在 `start_matlab_process()` 中添加了 INFO 级别日志（进程启动成功）
- 在 `shutdown_matlab_process()` 中添加了 INFO 级别日志（进程关闭）
- 确保所有日志包含时间戳和详细信息

**任务 12: 添加单元测试** ✅
- 创建了 `tests/unit/test_matlab_process_mgr.py`
- 测试了 `detect_matlab_processes()` 函数
- 测试了 `connect_to_matlab()` 函数
- 测试了 `verify_matlab_version()` 函数
- 测试了 `start_matlab_process()` 函数
- 测试了 `get_or_start_matlab()` 函数
- 测试了 `shutdown_matlab_process()` 函数
- 使用 mock 模拟 MATLAB 引擎行为
- **结果：28 个单元测试全部通过**

**任务 13: 添加集成测试** ✅
- 创建了 `tests/integration/test_matlab_process_mgr.py`
- 测试了完整进程管理流程（检测→连接/启动→验证→使用→关闭）
- 测试了进程复用场景
- 测试了新进程启动场景
- 测试了版本不兼容处理
- 测试了连接失败处理
- 测试了与工作流阶段的集成
- **结果：14 个集成测试全部通过**

**任务 14: 实现进程监控和超时处理** ✅
- 在 `src/utils/process_mgr.py` 中添加了 MATLAB 进程监控支持
- 创建了 `ProcessMonitor` 数据类
- 监控 MATLAB 进程是否异常退出
- 检测进程内存占用（不超过 2GB）
- 实现进程僵死检测
- 添加超时后强制终止逻辑
- 添加了单元测试验证进程监控
- 添加了单元测试验证超时强制终止

### 技术决策

1. **数据模型使用 dataclass**：所有数据模型使用 Python dataclass，所有字段提供默认值，确保版本兼容性和代码简洁性。

2. **超时检测使用 time.monotonic()**：遵循架构决策，使用 `time.monotonic()` 而非 `time.time()` 进行超时检测，避免系统时间调整的影响。

3. **错误处理使用统一错误类**：创建了 `MatlabProcessError`、`MatlabConnectionError`、`MatlabVersionError` 错误类，所有错误都带有可操作的修复建议。

4. **状态传递使用 BuildContext**：所有状态通过 `context.state` 传递，不使用全局变量，遵循架构决策。

5. **类型注解使用 typing 模块**：使用 `typing.List`, `typing.Dict`, `typing.Optional`（Python 3.11 兼容性），确保代码清晰和类型安全。

6. **日志记录使用 logging 模块**：所有日志使用 Python logging 模块，不使用 `print()`，确保日志统一管理和输出控制。

7. **单元测试和集成测试覆盖**：每个函数都有完整的单元测试和集成测试覆盖，确保代码质量和稳定性。

8. **进程监控使用 psutil**：使用 `psutil` 模块进行进程检测和监控，提供跨平台的进程管理能力。

9. **MATLAB Engine API 集成**：使用 `matlab.engine` 模块与 MATLAB 交互，提供 Python 到 MATLAB 的无缝集成。

10. **向后兼容性**：更新了 `MatlabIntegration` 类，支持新的进程管理功能，同时保持向后兼容性。

### File List

**新建文件：**
- `D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\src\utils\process_mgr.py` - 进程管理工具，包含 ProcessMonitor 数据类和监控功能
- `D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\tests\unit\test_matlab_process_mgr.py` - MATLAB 进程管理单元测试（28 个测试）
- `D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\tests\integration\test_matlab_process_mgr.py` - MATLAB 进程管理集成测试（14 个测试）

**修改文件：**
- `D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\src\utils\errors.py` - 添加了 MatlabProcessError、MatlabConnectionError、MatlabVersionError 错误类
- `D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\src\core\constants.py` - 添加了 MATLAB 进程配置常量（MATLAB_START_TIMEOUT, MATLAB_CONNECT_TIMEOUT, MATLAB_MEMORY_LIMIT, MATLAB_MIN_VERSION, MATLAB_DEFAULT_OPTIONS, MATLAB_PROCESS_NAMES）
- `D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\src\core\models.py` - 添加了 MATLAB 进程配置字段到 ProjectConfig（matlab_reuse_existing, matlab_close_after_build, matlab_timeout, matlab_memory_limit）
- `D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\src\integrations\matlab.py` - 添加了 MatlabProcess 数据模型和进程管理函数（detect_matlab_processes, connect_to_matlab, parse_matlab_version, verify_matlab_version, start_matlab_process, get_or_start_matlab, shutdown_matlab_process），更新了 MatlabIntegration 类支持新的进程管理功能
- `D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\src\stages\matlab_gen.py` - 更新了 execute_stage 函数，使用新的 context 参数支持进程管理

**测试结果：**
- 单元测试：28/28 通过 (100%)
- 集成测试：14/14 通过 (100%)
- 总计：42/42 测试通过 (100%)
