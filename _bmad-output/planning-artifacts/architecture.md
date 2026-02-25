---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
partyReviewCompleted: true
validationCompleted: true
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/epics.md
  - 00_用户输入需求与材料/MBD_CICDKits需求.md
  - CLAUDE.md
workflowType: 'architecture'
project_name: '181_CICDRedo'
user_name: 'link'
communication_language: 'Chinese'
document_output_language: 'Chinese'
date: '2026-02-03'
classification:
  projectType: desktop_app
  domain: embedded_development_tools
  complexity: medium
  projectContext: brownfield
  toolType: critical_dev_tool
keyInsights:
  - 高可靠性要求 - 关键开发路径工具
  - 外部工具集成 - IAR 命令行、Python A2L 处理
  - 5阶段自动化流程 - 配置→MATLAB→IAR→A2L→归纳
  - 离线桌面应用 - 无网络依赖，本地配置存储
  - 渐进式架构 - 从简单开始，按需演进
  - 借鉴不使用 - 学习成熟实践但保持架构控制权
  - 纯Python实现A2L处理 - 移除MATLAB Engine依赖，简化部署
---

# Architecture Decision Document

_本文档通过协作式逐步发现构建。各章节将随着我们一起完成每个架构决策而逐步添加。_

---

## 文档状态

| 状态 | 说明 |
|------|------|
| 工作流步骤完成 | Step 1: 初始化, Step 2: 项目上下文分析, Step 3: 架构启动点, Step 4: 核心架构决策, Step 5: 实现模式, Step 6: 项目结构 |
| 派对模式审查 | ✅ 已完成 (2026-02-03) |
| 审查结果 | ✅ 有条件批准 (条件已满足) |
| 文档版本 | 0.8 (更新 - 移除 MATLAB Engine 依赖) |
| 最后更新 | 2026-02-25 |

### 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-02-25 | 0.8 | 移除 MATLAB Engine API 依赖，改用纯 Python 实现 A2L 地址替换 |
| 2026-02-03 | 0.7 | 初始版本 - 项目结构已添加 |

---

## 输入文档清单

| # | 文档类型 | 文件路径 |
|---|---------|---------|
| 1 | PRD | `_bmad-output/planning-artifacts/prd.md` |
| 2 | Epics | `_bmad-output/planning-artifacts/epics.md` |
| 3 | 原始需求 | `00_用户输入需求与材料/MBD_CICDKits需求.md` |
| 4 | 项目上下文 | `CLAUDE.md` |

---

## 项目概述

**MBD_CICDKits** 是一款面向嵌入式开发工程师的桌面自动化工具，专注于 Simulink 模型开发的 CI/CD 流程自动化。

### 核心目标

- 将 60 分钟手动构建流程自动化为 15 分钟
- 实现 5 阶段完整自动化（配置 → MATLAB → IAR → A2L → 文件归纳）
- 提供可靠的结构化日志和可操作的错误提示
- 支持团队配置共享和离线运行

### 技术栈决策（来自 PRD）

| 类别 | 技术 |
|------|------|
| 开发语言 | Python 3.10+ (64位) |
| UI 框架 | PyQt6 |
| MATLAB 集成 | 预留接口（暂不实现） |
| IAR 集成 | 命令行接口 (iarbuild.exe) |
| A2L 处理 | 纯 Python 实现（pyelftools 解析 ELF） |
| 配置格式 | TOML (项目配置)、JSON (工作流配置) |
| 打包方式 | PyInstaller 单文件 exe |

---

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

基于 PRD 中的 57 个功能需求，项目架构需要支持 5 个核心 Epic：

| Epic | 功能模块 | 核心能力 |
|------|---------|---------|
| **Epic 1** | 项目配置管理 | 配置的创建、保存、加载、编辑、删除，TOML 格式持久化 |
| **Epic 2** | 工作流执行 | 5 阶段自动化流程（MATLAB → 文件处理 → IAR → A2L → 归纳） |
| **Epic 3** | 构建监控与反馈 | 实时进度、日志输出、阶段状态跟踪 |
| **Epic 4** | 错误处理与诊断 | 失败识别、错误报告、可操作的修复建议 |
| **Epic 5** | 环境验证与文件管理 | MATLAB/IAR 检测、文件操作、命名规范 |

**Non-Functional Requirements:**

| 类别 | 要求 | 架构影响 |
|------|------|----------|
| **可靠性** | ≥98% 成功率 | 健壮的错误处理、重试机制、详细日志 |
| **性能** | 15-20 分钟完整构建，启动 <3 秒，UI 响应 <500ms | 高效的文件处理、后台线程执行 |
| **集成** | MATLAB R2020a+、IAR 9.x | 进程管理、输出捕获、版本检测 |
| **可用性** | 30 分钟上手、清晰错误提示 | 用户友好的 UI、可操作的错误消息 |

**Scale & Complexity:**

| 维度 | 评估 |
|------|------|
| **项目类型** | 桌面应用 / 开发工具 / 自动化脚本 |
| **复杂度级别** | 中等 |
| **估计架构组件** | 6-8 个主要模块 |
| **Epic 数量** | 5 |
| **Story 数量** | 38 |

### Technical Constraints & Dependencies

**外部依赖（用户环境预装）：**
- MATLAB R2020a 或更高版本（代码生成功能预留，暂不需要）
- IAR Embedded Workbench for ARM 9.x

> ⚠️ **变更说明 (2026-02-25)：** 已移除 MATLAB Engine API for Python 依赖。A2L 地址替换功能改用纯 Python 实现（pyelftools 解析 ELF）。

**平台约束：**
- Windows 10/11 (64-bit) 仅
- 完全离线运行，无网络依赖
- 配置存储位置：`%APPDATA%/MBD_CICDKits/`

**技术栈决策：**
- Python 3.10+ (64-bit)
- PyQt6 (UI 框架)
- TOML (项目配置)、JSON (工作流配置)
- PyInstaller (单文件 exe 打包)

### Cross-Cutting Concerns Identified

| 关注点 | 影响范围 | 架构考虑 |
|--------|---------|----------|
| **错误处理与日志** | 所有 5 个阶段 | 统一的错误报告格式、结构化日志、可操作的修复建议 |
| **进程管理** | MATLAB/IAR 集成 | 进程启动/监控/终止、输出捕获、超时检测、僵尸进程清理 |
| **配置持久化** | 所有模块 | TOML/JSON 读写、配置验证、默认值处理 |
| **UI 响应性** | 主界面 | 后台线程执行耗时操作、信号槽通信、进度更新 |
| **文件操作事务性** | 文件管理模块 | 移动/备份/清空的原子性、失败回滚、权限检查 |

---

## Starter Template Evaluation

### Primary Technology Domain

Python 桌面应用 (Desktop Application) - 使用 PyQt6 作为 UI 框架

### Starter Options Research

研究过的 PyQt6 模板和 Python 自动化工具：

| 项目 | 类型 | 评价 |
|------|------|------|
| [ktxo/main-template-pyqt](https://github.com/ktxo/main-template-pyqt) | PyQt6 基础模板 | 仅提供 UI 脚手架 |
| [gciftci/PyQT-Template](https://github.com/gciftci/PyQT-Template) | 模块化模板 | 通用项目结构 |
| [PinnacleQt](https://github.com/Frica01/PinnacleQt_GUI_PySide6_PyQt6) | MVC 架构框架 | 过度设计 |
| [tox](https://tox.wiki/) | 命令行自动化 | ❌ 非桌面应用 |
| [Buildbot](https://www.buildbot.net/) | CI/CD 服务器 | ❌ Web UI，非桌面 |

**关键发现：没有与我们需求匹配的现成工程**

我们的需求是利niche 市场的交叉领域：
- PyQt6 桌面应用 ✅ 有模板
- 5 阶段自动化工作流 ❌ 无
- MATLAB/IAR 外部工具集成 ❌ 无
- 实时进度显示 ❌ 无
- PyInstaller 单文件打包 ⚠️ 示例少

**总体匹配度：仅 30-40%**

### 现成工程 vs 自定义架构分析

| 维度 | 现成模板 | 自定义架构 |
|------|---------|-----------|
| **节省时间** | 4-7 天（表面） | 0 天 |
| **学习成本** | 1-2 天 | 0 天 |
| **修改适配** | 3-5 天 | 0 天 |
| **兼容性问题** | 2-3 天风险 | 0 天 |
| **净节省** | 0-2 天（可能为负） | - |
| **架构控制** | 受限于模板 | 完全控制 |
| **PyInstaller 风险** | 中高 | 低 |

### Selected Approach: Custom Architecture with Learned Patterns

**决策理由：**

1. **匹配度太低**：60-70% 核心功能仍需自建
2. **PyInstaller 兼容性风险**：模板的动态机制可能与单文件打包冲突
3. **认知负担 > 时间节省**：学习别人的架构比自己写更慢
4. **架构需求独特**：利niche 市场，无通用解决方案
5. **长期维护成本**：自定义架构更易于团队理解和维护

**混合方案：借鉴不使用**

- ✅ 从 PyQt6 模板学习 UI 组织模式
- ✅ 从 QProcess 示例学习进程管理
- ✅ 参考 pyproject.toml 标准格式
- ❌ 不直接使用现成模板
- ✅ 保持架构简洁和完全控制权

---

## Architecture Evolution Strategy

### MVP Phase (当前阶段)

**架构原则：** 渐进式架构 - 从简单开始，按需演进

**架构特征：**
- 函数式模块为主（业务逻辑）
- PyQt6 类仅用于 UI 层（继承必需）
- 统一的阶段接口（伪插件模式）
- 硬编码 5 阶段工作流
- 防御性编程和可观测性优先

**项目结构：**

```
mbd_cicdkits/
├── src/
│   ├── __init__.py
│   ├── main.py                  # 应用入口
│   ├── ui/                      # PyQt6 UI（类）
│   │   ├── __init__.py
│   │   ├── main_window.py        # 主窗口
│   │   ├── widgets/              # 自定义控件
│   │   │   ├── progress_panel.py # 进度面板
│   │   │   └── log_viewer.py     # 日志查看器
│   │   └── dialogs/              # 对话框
│   ├── core/                    # 核心业务逻辑（函数）
│   │   ├── __init__.py
│   │   ├── config.py             # 配置管理
│   │   ├── workflow.py           # 工作流编排
│   │   └── models.py             # 数据模型
│   ├── stages/                   # 工作流阶段（函数模块）
│   │   ├── __init__.py
│   │   ├── base.py               # 阶段接口定义
│   │   ├── matlab_gen.py         # 阶段 1: MATLAB 代码生成（预留接口）
│   │   ├── file_process.py       # 阶段 2: 文件处理
│   │   ├── iar_compile.py        # 阶段 3: IAR 编译
│   │   ├── a2l_process.py        # 阶段 4: A2L 处理（Python 实现）
│   │   └── package.py            # 阶段 5: 文件归纳
│   ├── integrations/             # 外部工具集成
│   │   ├── __init__.py
│   │   ├── matlab.py             # MATLAB 预留接口（暂不实现）
│   │   └── iar.py                # IAR 命令行
│   ├── a2l/                      # A2L 处理模块（新增）
│   │   ├── __init__.py
│   │   ├── elf_parser.py         # ELF 文件解析（pyelftools）
│   │   ├── a2l_parser.py         # A2L 文件解析
│   │   └── address_updater.py    # A2L 地址更新
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── process_mgr.py       # 进程管理（防御性）
│       ├── errors.py            # 结构化错误
│       ├── logger.py            # 可观测性
│       └── file_ops.py          # 文件操作
├── resources/                   # 资源文件
│   ├── icons/                   # 图标
│   └── templates/               # 模板文件（XCP 头文件等）
├── configs/                     # 默认配置模板
│   ├── default_workflow.json
│   └── settings.toml
├── tests/                       # 测试
│   ├── __init__.py
│   ├── unit/
│   └── integration/
├── pyproject.toml               # 项目配置
├── requirements.txt
├── README.md
└── build.spec                   # PyInstaller 配置
```

### Phase 2 Expansion

**演进触发：** 当需要自定义工作流时

**架构升级：**
- `stages/` 目录：模块化的 `stage_xxx.py`
- 函数 → `Stage` 基类 + 具体实现类
- 伪插件 → 真正的插件系统

---

## Architecture Decision Records

### ADR-001: 渐进式架构

```
Status: Accepted
Date: 2026-02-03

Context:
MVP 阶段需要快速验证核心价值，同时为未来扩展预留空间。

Decision:
采用渐进式架构方法：
- MVP 使用简化的函数式架构
- Phase 2 演进到类插件系统
- 统一的阶段接口作为演进桥梁

Consequences:
Positive:
  + 快速启动，减少初期架构负担
  + 可以基于实际使用调整设计
  + 代码简洁，易于理解

Negative:
  - 后期可能需要重构（但架构会演进）
  - 需要保持接口一致性

```

### ADR-002: 防御性编程优先

```
Status: Accepted
Date: 2026-02-03

Context:
98% 成功率要求意味着假设外部工具会失败是合理的。

Decision:
采用防御性编程策略：
- 所有外部进程调用设置超时
- 文件操作前备份，失败后回滚
- 结构化错误捕获和可操作的恢复建议
- 详细的日志记录用于故障诊断

Consequences:
Positive:
  + 提高系统可靠性
  + 降低故障排查成本
  + 改善用户体验

Negative:
  - 增加代码复杂度
  - 可能略微影响性能
```

### ADR-003: 可观测性即架构

```
Status: Accepted
Date: 2026-02-03

Context:
故障诊断和用户体验依赖于清晰的进度反馈。

Decision:
将可观测性作为架构核心组件：
- 日志不是事后添加，是架构基础
- 实时进度通过信号槽机制实现
- 结构化日志支持搜索和高亮
- 错误信息包含可操作的建议

Consequences:
Positive:
  + 快速定位问题
  + 降低支持成本
  + 提升用户信心

Negative:
  - 增加初期开发工作量
```

### ADR-004: 混合架构模式

```
Status: Accepted
Date: 2026-02-03

Context:
PyQt6 要求面向对象，但业务逻辑可以用简单方式实现。

Decision:
采用混合架构模式：
- UI 层：PyQt6 类（继承必需）
- 业务逻辑：函数式模块 + 简单数据类
- 工作流：统一的阶段接口（函数签名）

Consequences:
Positive:
  + 平衡 PyQt6 要求和开发效率
  + 代码组织清晰
  + 易于测试

Negative:
  - 风格不统一（但适应实际需求）
```

### ADR-005: 移除 MATLAB Engine 依赖

```
Status: Accepted
Date: 2026-02-25

Context:
PyInstaller 打包后，MATLAB Engine API for Python 在目标机器上无法正常工作。
这导致 A2L 处理阶段失败，影响了工具的部署和分发能力。

Decision:
移除 MATLAB Engine API for Python 依赖，采用以下策略：
- MATLAB 代码生成功能：保留接口，暂不实现（返回成功状态）
- A2L 地址替换功能：改用纯 Python 实现
  - 使用 pyelftools 解析 ELF 文件提取符号地址
  - 基于原有 MATLAB 脚本逻辑实现 Python 版本
- 环境检测：移除 MATLAB Engine API 检测

Consequences:
Positive:
  + 简化部署 - 无需在目标机器配置 MATLAB Engine
  + 提高可靠性 - 纯 Python 实现更稳定
  + 降低打包复杂度 - 减少依赖冲突风险
  + 保持功能完整 - A2L 处理功能不受影响

Negative:
  - 需要实现 Python 版 A2L 地址替换（基于原有脚本）
  - MATLAB 代码生成功能暂不可用（预留接口）

Related:
- Sprint Change Proposal: sprint-change-proposal-2026-02-25.md
- Affected Stories: 2.5, 2.9, 5.1, 5.2
```

---

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- 进程管理架构（超时、清理、错误处理）
- 文件操作原子性（备份、回滚、确认）

**Important Decisions (Shape Architecture):**
- 数据模型（dataclass vs Pydantic）
- UI 通信模式（QThread + signals）
- 日志系统集成

**Deferred Decisions (Post-MVP):**
- 日志搜索功能（FR-052）
- 自动路径检测（FR-047）
- 断点续传（Phase 2/3）

---

### Decision 1.1: 配置文件管理

**选择**: 混合方案（TOML 项目配置 + JSON 工作流配置）

**理由**:
- TOML 支持注释，适合用户手动编辑的项目配置
- JSON 与工作流引擎兼容
- Python 3.11+ 内置 tomllib，Python 3.10 使用 tomli

**可靠性考虑**:
- 配置损坏时回退到默认配置
- 友好的解析错误消息（避免暴露技术细节）
- 配置验证在加载时执行，失败时提供修复建议

**版本**:
- tomllib (Python 3.11+) / tomli (Python 3.10)
- json (标准库)

**影响模块**: Epic 1 (项目配置管理)

---

### Decision 1.2: 数据模型

**选择**: dataclass (Python 3.7+)

**理由**:
- 轻量、无额外依赖
- 类型提示支持
- 与 JSON/TOML 序列化兼容
- 适合简单数据结构

**可靠性考虑**:
- 所有字段提供默认值 `field(default=...)`
- 版本兼容性：新增字段使用默认值

**版本**: Python 3.7+ (dataclasses)

**影响模块**: 所有模块

---

### Decision 1.3: 配置验证

**选择**: 手动验证（MVP）+ Pydantic（Phase 2 可选）

**理由**:
- MVP 阶段保持简单
- 友好的错误消息比严格验证更重要
- Pydantic 可作为 Phase 2 增强功能

**实现示例**:
```python
def validate_config(config: dict) -> list[str]:
    """返回错误列表，空列表表示有效"""
    errors = []
    if not config.get("simulink_path"):
        errors.append("Simulink 工程路径不能为空")
    return errors
```

**影响模块**: Epic 1 (项目配置管理)

---

### Decision 2.1: MATLAB 进程管理策略 ⚠️ 关键决策

**选择**: 每次启动/关闭（MVP）+ 进程管理器模式

**理由**:
- 符合 PRD "一天 1-5 次频率"的使用场景
- 避免 MATLAB 进程内存泄漏
- 每次构建是独立的环境，状态更可预测

**关键实现要点**:

1. **超时检测**（强制）:
```python
import time

def execute_matlab_with_timeout(script: str, timeout: int = 1800) -> ProcessResult:
    """执行 MATLAB 脚本，超时返回失败

    重要: 使用 time.monotonic() 而非 time.time()
    - monotonic 不受系统时间调整影响
    - 适合测量时间间隔
    """
    start = time.monotonic()  # ← 使用 monotonic 避免系统时间调整影响

    # ... 进程执行逻辑

    if time.monotonic() - start > timeout:
        # 超时处理
        pass
```

2. **僵尸进程清理**（强制）:
```python
def ensure_process_terminated(proc: subprocess.Popen):
    """确保进程被终止，使用 psutil 强制清理"""
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except TimeoutExpired:
            proc.kill()
```

3. **退出码检查**（强制）:
```python
if proc.returncode != 0:
    return ProcessResult(
        success=False,
        error=f"MATLAB 退出码: {proc.returncode}",
        suggestions=["检查 MATLAB 脚本语法", "查看 MATLAB 日志"]
    )
```

**版本**:
- subprocess (标准库)
- psutil (第三方，用于进程清理)

> ⚠️ **变更说明 (2026-02-25)：** 已移除 MATLAB Engine API for Python 依赖。MATLAB 代码生成功能预留接口暂不实现。

**影响模块**: Epic 2 (工作流执行), Epic 4 (错误处理)

**可靠性影响**: 高 - 这是实现 98% 成功率的关键组件

---

### Decision 2.2: 进程管理器架构

**选择**: 独立的进程管理器模块

**架构设计**:
```python
# utils/process_mgr.py
class ProcessManager:
    """统一的进程管理器，处理所有外部进程"""

    def execute_monitored(
        self,
        command: list[str],
        timeout: int,
        name: str
    ) -> ProcessResult:
        """
        执行命令并监控

        特性:
        - 超时检测
        - 输出实时捕获
        - 退出码检查
        - 资源清理保证
        """
```

**理由**:
- 进程管理逻辑集中，易于测试
- 可独立优化和增强
- 降低错误处理复杂度

**测试策略**:
- 使用 mock 子进程进行单元测试
- 测试超时场景
- 测试僵尸进程清理

**统一错误基类**（新增 - 派对模式审查建议）:
```python
# utils/errors.py
class ProcessError(Exception):
    """进程相关错误基类

    提供统一的错误处理和可操作的修复建议
    """
    def __init__(self, message: str, suggestions: list[str] = None):
        super().__init__(message)
        self.suggestions = suggestions or []

    def __str__(self):
        msg = super().__str__()
        if self.suggestions:
            msg += "\n建议操作:\n" + "\n".join(f"  - {s}" for s in self.suggestions)
        return msg

class ProcessTimeoutError(ProcessError):
    """进程执行超时"""
    def __init__(self, process_name: str, timeout: int):
        super().__init__(
            f"{process_name} 执行超时 (>{timeout}秒)",
            suggestions=[
                "检查进程是否卡死",
                "查看进程日志文件",
                "尝试增加超时时间",
                "检查输入文件是否过大"
            ]
        )
        self.process_name = process_name
        self.timeout = timeout

class ProcessTerminationError(ProcessError):
    """进程终止失败"""
    def __init__(self, pid: int, reason: str = ""):
        super().__init__(
            f"无法终止进程 PID {pid}: {reason}",
            suggestions=[
                "手动检查任务管理器",
                "尝试使用系统工具终止进程",
                "重启开发环境"
            ]
        )
        self.pid = pid

class ProcessExitCodeError(ProcessError):
    """进程退出码异常"""
    def __init__(self, process_name: str, exit_code: int):
        super().__init__(
            f"{process_name} 异常退出 (退出码: {exit_code})",
            suggestions=[
                "检查进程日志",
                "验证输入文件格式",
                "检查环境配置",
                "联系工具供应商支持"
            ]
        )
        self.process_name = process_name
        self.exit_code = exit_code
```

**ProcessManager 使用错误类**:
```python
# utils/process_mgr.py
from utils.errors import ProcessTimeoutError, ProcessTerminationError, ProcessExitCodeError

class ProcessManager:
    def execute_monitored(
        self,
        command: list[str],
        timeout: int,
        name: str
    ) -> ProcessResult:
        """执行命令并监控"""
        start = time.monotonic()
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            # 等待进程完成或超时
            while True:
                if time.monotonic() - start > timeout:
                    raise ProcessTimeoutError(name, timeout)

                if proc.poll() is not None:
                    break

                time.sleep(0.1)

            # 检查退出码
            if proc.returncode != 0:
                raise ProcessExitCodeError(name, proc.returncode)

            return ProcessResult(success=True)

        except ProcessTimeoutError as e:
            # 超时: 尝试终止进程
            ensure_process_terminated(proc)
            return ProcessResult(success=False, error=str(e), suggestions=e.suggestions)

        except ProcessError as e:
            # 其他进程错误
            return ProcessResult(success=False, error=str(e), suggestions=e.suggestions)
```

---

### Decision 3.1: PyQt6 线程 + 信号模式

**选择**: QThread + pyqtSignal

**实现模式**:
```python
class WorkflowThread(QThread):
    # 定义信号
    progress_update = pyqtSignal(int, str)  # 进度百分比, 消息
    stage_complete = pyqtSignal(str, bool)   # 阶段名, 成功
    log_message = pyqtSignal(str)            # 日志内容
    error_occurred = pyqtSignal(str, list)   # 错误, 建议

    def run(self):
        """在后台线程执行工作流"""
        try:
            # 执行各阶段
            for stage in self.stages:
                self.progress_update.emit(...)
        except Exception as e:
            self.error_occurred.emit(...)
```

**关键实现要点**:

1. **信号连接**（必须使用 QueuedConnection）:
```python
# 在主窗口连接信号
# 重要: 跨线程信号必须使用 QueuedConnection
self.worker.log_message.connect(
    self.log_viewer.append,
    Qt.ConnectionType.QueuedConnection  # ← 必须: 确保线程安全
)
self.worker.error_occurred.connect(
    self.show_error_dialog,
    Qt.ConnectionType.QueuedConnection  # ← 必须: 确保线程安全
)
self.worker.progress_update.connect(
    self.update_progress,
    Qt.ConnectionType.QueuedConnection  # ← 必须: 确保线程安全
)
```

**为什么必须使用 QueuedConnection:**
- **AutoConnection** (默认) 在跨线程时等同于 QueuedConnection，但显式指定更安全
- **DirectConnection** 会导致接收者在发送者线程中执行，可能造成 UI 线程竞争
- **QueuedConnection** 确保槽函数在接收者线程（UI 线程）中执行
- 避免：UI 冻结、竞态条件、信号丢失

2. **完整的工作流线程示例**:
```python
class WorkflowThread(QThread):
    # 定义信号
    progress_update = pyqtSignal(int, str)  # 进度百分比, 消息
    stage_complete = pyqtSignal(str, bool)   # 阶段名, 成功
    log_message = pyqtSignal(str)            # 日志内容
    error_occurred = pyqtSignal(str, list)   # 错误, 建议

    def __init__(self, stages: list[StageConfig], context: BuildContext):
        super().__init__()
        self.stages = stages
        self.context = context

    def run(self):
        """在后台线程执行工作流"""
        try:
            # 执行各阶段
            for stage in self.stages:
                # 发送进度更新
                self.progress_update.emit(
                    self.calculate_progress(),
                    f"正在执行: {stage.name}"
                )

                # 执行阶段（在线程中）
                result = execute_stage(stage, self.context)

                # 发送完成信号
                self.stage_complete.emit(stage.name, result.status == StageStatus.COMPLETED)

                if result.status == StageStatus.FAILED:
                    # 发送错误信号
                    self.error_occurred.emit(
                        result.message,
                        result.suggestions or []
                    )
                    return  # 停止工作流

        except Exception as e:
            # 捕获所有未预期的异常
            self.error_occurred.emit(
                f"工作流异常: {str(e)}",
                ["查看详细日志", "检查配置文件"]
            )
```

3. **线程崩溃处理**:
```python
def run(self):
    try:
        # 工作流逻辑
    except Exception as e:
        # 捕获所有异常，通过信号传递
        self.error_occurred.emit(str(e), [])
```

**影响模块**: Epic 3 (构建监控与反馈)

---

### Decision 4.1: 原子性文件操作

**选择**: 复制-验证-删除模式

**实现模式**:
```python
def safe_move_files(src_files: list[Path], dst_dir: Path) -> OperationResult:
    """
    安全移动文件，保证原子性

    流程:
    1. 创建备份
    2. 复制文件到目标
    3. 验证复制成功
    4. 删除源文件
    5. 清理备份
    """
    backup_dir = create_backup(dst_dir)
    try:
        # 复制
        for src in src_files:
            shutil.copy2(src, dst_dir / src.name)

        # 验证
        if not verify_files_copied(src_files, dst_dir):
            raise OperationError("文件验证失败")

        # 删除源
        for src in src_files:
            src.unlink()

    except Exception as e:
        # 回滚：从备份恢复
        restore_from_backup(backup_dir, dst_dir)
        raise OperationError(f"文件操作失败: {e}")
    finally:
        # 清理备份
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
```

**用户体验增强**:
```python
def confirm_directory_clear(target_dir: Path) -> bool:
    """清空前显示文件列表，要求用户确认"""
    files = list(target_dir.rglob("*"))
    if not files:
        return True

    # 显示对话框
    return show_confirmation_dialog(
        title="确认清空目录",
        message=f"将清空 {target_dir}，包含 {len(files)} 个文件",
        file_list=files[:20]  # 最多显示 20 个
    )
```

**影响模块**: Epic 5 (文件管理)

**可靠性影响**: 高 - 防止数据丢失

---

### Decision 4.2: 长路径处理

**选择**: 使用 `\\?\` 前缀

**实现**:
```python
def safe_path(path: str) -> Path:
    """处理 Windows 长路径"""
    if len(path) > 200:  # 接近 260 限制时
        return Path(f"\\\\?\\{path}")
    return Path(path)
```

**影响模块**: 所有文件操作

---

### Decision 5.1: 日志框架

**选择**: logging + 自定义 PyQt6 Handler

**实现**:
```python
# utils/log_handler.py
class QtSignalHandler(logging.Handler):
    """将日志发送到 PyQt6 信号"""
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        msg = self.format(record)
        self.signal.emit(msg)

# 使用
class MainWindow(QMainWindow):
    def __init__(self):
        # 配置日志
        self.logger = logging.getLogger(__name__)

        # 添加 PyQt6 信号 Handler
        handler = QtSignalHandler(self.log_signal)
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        ))
        self.logger.addHandler(handler)
```

**日志级别使用**:
- DEBUG: 详细调试信息（开发时）
- INFO: 一般信息（阶段完成、文件操作）
- WARNING: 警告（配置缺失、使用默认值）
- ERROR: 错误（阶段失败、文件操作失败）
- CRITICAL: 严重错误（无法恢复）

**日志高亮**:
```python
class LogViewer(QTextEdit):
    def append_log(self, message: str):
        """追加日志，带颜色高亮"""
        if "ERROR" in message:
            # 红色
            self.setTextColor(Qt.GlobalColor.red)
        elif "WARNING" in message:
            # 黄色
            self.setTextColor(Qt.GlobalColor.darkYellow)
        else:
            # 默认
            self.setTextColor(Qt.GlobalColor.black)

        self.append(message)
```

**日志行数限制**:
```python
class LogViewer(QTextEdit):
    MAX_LINES = 10000

    def append_log(self, message: str):
        self.append(message)

        # 限制行数
        if self.document().blockCount() > self.MAX_LINES:
            cursor = self.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.BlockUnderCursor)
            cursor.removeSelectedText()
```

**影响模块**: Epic 3 (构建监控与反馈)

---

### Decision Impact Analysis

**Implementation Sequence（按实施顺序）**:

1. **数据架构** (Decision 1.x) → 基础，无依赖
2. **日志系统** (Decision 5.x) → 独立，可并行开发
3. **进程管理器** (Decision 2.x) → 核心组件，依赖日志
4. **文件操作** (Decision 4.x) → 依赖日志和进程管理
5. **UI 通信** (Decision 3.x) → 依赖所有后端组件

**Cross-Component Dependencies（跨组件依赖）**:

```
数据架构 ←┐
           ├──→ 进程管理器 ←┐
日志系统 ←┘               │
                          ├──→ UI 通信
文件操作 ←─────────────────┘
```

**Reliability Impact Ranking（可靠性影响排名）**:

1. ⭐⭐⭐⭐⭐ 进程管理（最高）
2. ⭐⭐⭐⭐ 文件操作
3. ⭐⭐⭐ UI 通信
4. ⭐⭐ 日志系统
5. ⭐ 数据架构

---

## Party Mode Review Results

**审查日期**: 2026-02-03
**审查委员会**: Winston (Architect), Murat (Test), John (PM), Amelia (Dev), Bond (Agent Builder)
**审查结果**: ✅ 有条件批准

### 审查发现的关键问题

| 问题 | 影响 | 修正状态 |
|------|------|---------|
| `time.time()` vs `time.monotonic()` | 超时检测可能失效 | ✅ 已修正 |
| 缺少统一错误基类 | 错误处理不一致 | ✅ 已添加 |
| PyQt6 信号未显式指定连接类型 | 线程安全风险 | ✅ 已修正 |

### 可靠性影响排名 (Murat - Test Architect)

```
1. ⭐⭐⭐⭐⭐ 进程管理 (Decision 2.1, 2.2) - 直接决定 98% 成功率
2. ⭐⭐⭐⭐ 文件操作 (Decision 4.1) - 数据丢失风险
3. ⭐⭐⭐ UI 通信 (Decision 3.1) - 用户体验
4. ⭐⭐ 日志系统 (Decision 5.1) - 可观测性
5. ⭐ 数据架构 (Decision 1.x) - 基础
```

### 测试优先级建议

```python
# 测试金字塔
         /\     E2E (1) - 完整工作流 + 真实环境
        /  \
       /____\
      /      \  Integration (5) - 进程管理器 + 文件操作
     /       \
    /          \| 单元测试 (15+)
   /____________\ - ProcessManager, safe_move_files, QtSignalHandler
```

### 实施工作量估算 (Amelia - Developer)

| 决策 | 工作量 | 复杂度 |
|------|--------|--------|
| 1.1 配置 | 1-2 天 | Easy |
| 1.2 数据模型 | 0.5 天 | Trivial |
| 1.3 配置验证 | 1 天 | Easy |
| 2.1 MATLAB 进程 | 3-5 天 | Medium-Hard |
| 2.2 进程管理器 | 2-3 天 | Medium |
| 3.1 PyQt6 线程 | 2 天 | Medium |
| 4.1 文件操作 | 2 天 | Medium |
| 4.2 长路径 | 0.5 天 | Trivial |
| 5.1 日志 | 1-2 天 | Easy |
| **总计** | **15-19 天** | |

### 架构健康度评分 (Bond - Agent Builder)

```yaml
Architecture Health Score: 8.5/10

✅ Strengths:
   - 单一职责原则
   - 依赖注入 (BuildContext)
   - 接口一致性
   - 可测试性

⚠️ Concerns:
   - 混合架构模式 (类+函数)
   - 缺少统一错误基类 → 已修正
   - 配置迁移策略
```

### 批准条件

1. ✅ 修正 `time.monotonic()` 问题
2. ✅ 添加统一的错误基类
3. ✅ 所有 PyQt6 信号使用 `QueuedConnection`
4. 🔄 进程管理器必须有单元测试 (实施时)

---

## Technical Implementation Details

### 统一的阶段接口（MVP）

```python
# stages/base.py
from dataclasses import dataclass
from typing import Protocol
from enum import Enum

class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class StageConfig:
    """阶段配置基类"""
    name: str
    enabled: bool = True
    timeout: int = 3600  # 默认 1 小时超时

@dataclass
class StageResult:
    """阶段执行结果"""
    status: StageStatus
    message: str
    output_files: list[str] = None
    error: Exception = None
    suggestions: list[str] = None  # 可操作的修复建议

class BuildContext:
    """构建上下文 - 在阶段间传递状态"""
    def __init__(self):
        self.config: dict = {}
        self.state: dict = {}
        self.log_callback: callable = None

# 阶段函数签名
def execute_stage(
    config: StageConfig,
    context: BuildContext
) -> StageResult:
    """
    所有工作流阶段遵循此接口

    Args:
        config: 阶段配置参数
        context: 构建上下文（状态、日志、进度）

    Returns:
        StageResult: 包含成功/失败、输出、错误信息、建议
    """
    pass
```

### 工作流执行示例

```python
# core/workflow.py
from typing import List, Tuple
from stages.base import StageConfig, BuildContext, StageResult

# 工作流定义：阶段名称 + 执行函数
WORKFLOW_STAGES = [
    ("matlab_gen", stages.matlab_gen.execute_stage),
    ("file_process", stages.file_process.execute_stage),
    ("iar_compile", stages.iar_compile.execute_stage),
    ("a2l_process", stages.a2l_process.execute_stage),
    ("package", stages.package.execute_stage),
]

def execute_workflow(stages_config: List[StageConfig], context: BuildContext) -> bool:
    """
    执行工作流

    Returns:
        bool: True 表示全部成功，False 表示有失败
    """
    for stage_name, stage_func in WORKFLOW_STAGES:
        # 找到对应的配置
        config = next((s for s in stages_config if s.name == stage_name), None)
        if not config or not config.enabled:
            continue

        # 执行阶段
        result = stage_func(config, context)

        # 处理结果
        if result.status == StageStatus.FAILED:
            # 记录错误，显示建议
            context.log_callback(f"阶段 {stage_name} 失败: {result.message}")
            if result.suggestions:
                context.log_callback("建议操作:")
                for suggestion in result.suggestions:
                    context.log_callback(f"  - {suggestion}")
            return False

    return True
```

---

## Implementation Patterns & Consistency Rules

### Critical Conflict Points Analysis

基于 MBD_CICDKits 作为 **Python 桌面工作流自动化工具** 的特点，识别出 **7 个高影响冲突点**，这些是 AI Agent 实施时最可能产生分歧的地方：

| # | 冲突点 | 影响级别 | AI Agent 分歧示例 |
|---|--------|---------|------------------|
| 1 | 阶段函数签名 | ⭐⭐⭐⭐⭐ | `execute(stage)` vs `run(config)` vs `process(ctx)` |
| 2 | 信号连接类型 | ⭐⭐⭐⭐⭐ | `AutoConnection` vs `QueuedConnection`（线程安全！） |
| 3 | 超时时间函数 | ⭐⭐⭐⭐⭐ | `time.time()` vs `time.monotonic()`（系统时间调整影响） |
| 4 | 状态传递方式 | ⭐⭐⭐⭐ | 全局变量 vs 参数传递 vs Context 对象 |
| 5 | 错误传播方式 | ⭐⭐⭐⭐ | 异常 vs 返回码 vs Result 对象 |
| 6 | 超时值管理 | ⭐⭐⭐⭐ | 分散硬编码 vs 集中配置 |
| 7 | 资源清理时机 | ⭐⭐⭐ | 即时清理 vs 延迟清理 vs 上下文管理器 |

---

### 1. 工作流核心模式 (Core Workflow Patterns)

#### 1.1 阶段接口模式 ⭐⭐⭐⭐⭐

**统一签名（所有阶段必须遵循）**：

```python
from dataclasses import dataclass
from enum import Enum

class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class StageConfig:
    """阶段配置"""
    name: str
    enabled: bool = True
    timeout: int = 3600
    # ... 其他配置字段

@dataclass
class StageResult:
    """阶段执行结果"""
    status: StageStatus
    message: str
    output_files: list[str] = None
    error: Exception = None
    suggestions: list[str] = None  # 可操作的修复建议

class BuildContext:
    """构建上下文 - 在阶段间传递状态"""
    def __init__(self):
        self.config: dict = {}           # 全局配置（只读）
        self.state: dict = {}            # 阶段状态（可写，用于传递）
        self.log_callback: callable = None  # 日志回调

# 统一阶段接口
def execute_stage(
    config: StageConfig,
    context: BuildContext
) -> StageResult:
    """
    所有工作流阶段必须遵循此签名

    Args:
        config: 阶段配置参数
        context: 构建上下文（状态、日志、进度）

    Returns:
        StageResult: 包含成功/失败、输出、错误信息、建议
    """
    pass
```

**关键规则**：
- ✅ 所有阶段函数命名为 `execute_stage`
- ✅ 必须接受 `StageConfig` 和 `BuildContext`
- ✅ 必须返回 `StageResult`
- ✅ 失败时必须包含可操作的 `suggestions`

#### 1.2 状态传播模式

```python
# BuildContext 使用规则

class BuildContext:
    def __init__(self):
        self.config: dict = {}      # ✅ 只读：全局配置
        self.state: dict = {}       # ✅ 可写：阶段间传递状态
        self.log_callback: callable # ✅ 统一日志接口

# 使用示例
def execute_stage(config: StageConfig, context: BuildContext) -> StageResult:
    # 读取全局配置（只读）
    matlab_path = context.config.get("matlab_path")

    # 读取前阶段状态
    prev_output = context.state.get("prev_stage_output")

    # 写入当前阶段状态（供后续阶段使用）
    context.state["current_stage_output"] = {
        "files": ["file1.c", "file2.h"],
        "timestamp": time.time()
    }

    # 使用统一日志接口
    context.log_callback("INFO: 阶段开始执行")

    return StageResult(status=StageStatus.COMPLETED, message="成功")
```

**状态传递规则**：
| 属性 | 读写 | 用途 | 示例 |
|------|------|------|------|
| `config` | 只读 | 全局配置 | MATLAB 路径、超时值 |
| `state` | 可写 | 阶段间传递 | 生成的文件列表、时间戳 |
| `log_callback` | 调用 | 统一日志 | 进度输出、错误日志 |

---

### 2. 可靠性保证模式 (Reliability Patterns)

#### 2.1 超时配置集中管理 ⭐⭐⭐⭐⭐

```python
# core/constants.py - 集中管理所有超时值
import time

DEFAULT_TIMEOUT = {
    "matlab": 1800,      # 30 分钟 - MATLAB 代码生成
    "iar": 1200,         # 20 分钟 - IAR 编译
    "file_ops": 300,     # 5 分钟 - 文件操作
    "a2l": 600,          # 10 分钟 - A2L 处理
    "stage_default": 3600, # 1 小时 - 默认阶段超时
}

def get_timeout(operation: str) -> int:
    """获取指定操作的超时值"""
    return DEFAULT_TIMEOUT.get(operation, DEFAULT_TIMEOUT["stage_default"])

# 使用示例
def execute_with_timeout(operation: str):
    timeout = get_timeout(operation)
    start = time.monotonic()  # ← 必须使用 monotonic

    while True:
        if time.monotonic() - start > timeout:
            raise ProcessTimeoutError(operation, timeout)
        # ... 执行逻辑
```

**超时值选择指南**：
| 操作类型 | 推荐超时 | 考虑因素 |
|---------|---------|---------|
| MATLAB 代码生成 | 1800s (30分) | 模型复杂度、机器性能 |
| IAR 编译 | 1200s (20分) | 代码量、优化级别 |
| 文件操作 | 300s (5分) | 文件数量、磁盘速度 |
| A2L 处理 | 600s (10分) | 变量数量 |
| 默认阶段 | 3600s (1小时) | 保守估计 |

#### 2.2 重试策略模式

```python
# utils/retry.py
from dataclasses import dataclass
from typing import Callable, Type
import time

@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    base_delay: float = 1.0  # 秒
    max_delay: float = 60.0
    backoff_factor: float = 2.0

# 可重试错误定义
RETRYABLE_ERRORS = (
    ConnectionError,      # 网络相关（如果有）
    TimeoutError,         # 超时（保守重试）
    OSError,             # 文件系统临时错误
)

def with_retry(
    func: Callable,
    config: RetryConfig = None,
    retryable_errors: tuple = RETRYABLE_ERRORS
):
    """重试装饰器"""
    if config is None:
        config = RetryConfig()

    def wrapper(*args, **kwargs):
        last_error = None
        delay = config.base_delay

        for attempt in range(config.max_attempts):
            try:
                return func(*args, **kwargs)
            except retryable_errors as e:
                last_error = e
                if attempt < config.max_attempts - 1:
                    logging.warning(f"重试 {attempt + 1}/{config.max_attempts}: {e}")
                    time.sleep(min(delay, config.max_delay))
                    delay *= config.backoff_factor
                else:
                    logging.error(f"重试失败: {e}")

        raise last_error

    return wrapper
```

**重试决策**：
| 错误类型 | 是否重试 | 原因 |
|---------|---------|------|
| `ConnectionError` | ✅ 是 | 网络临时问题 |
| `TimeoutError` | ⚠️ 谨慎 | 可能是真实超时 |
| `OSError` | ✅ 是 | 文件系统临时错误 |
| `ProcessExitCodeError` | ❌ 否 | 退出码异常通常重试无效 |
| `ProcessTerminationError` | ❌ 否 | 进程终止问题重试无效 |

#### 2.3 资源清理保证模式

```python
# utils/cleanup.py
import atexit
from typing import List
import psutil

class ResourceManager:
    """资源管理器 - 确保清理"""

    def __init__(self):
        self._processes: List[subprocess.Popen] = []
        self._temp_dirs: List[Path] = []

        # 注册退出清理
        atexit.register(self.cleanup_all)

    def register_process(self, proc: subprocess.Popen):
        """注册需要清理的进程"""
        self._processes.append(proc)

    def register_temp_dir(self, path: Path):
        """注册临时目录"""
        self._temp_dirs.append(path)

    def cleanup_all(self):
        """清理所有资源"""
        # 清理进程
        for proc in self._processes:
            ensure_process_terminated(proc)

        # 清理临时目录
        for temp_dir in self._temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
```

---

### 3. 线程安全模式 (Thread Safety Patterns)

#### 3.1 信号连接规范 ⭐⭐⭐⭐⭐

```python
# ✅ 正确 - 跨线程必须使用 QueuedConnection
class MainWindow(QMainWindow):
    def __init__(self):
        self.worker = WorkflowThread()

        # 在 __init__ 中建立所有连接
        self.worker.progress_update.connect(
            self.update_progress,
            Qt.ConnectionType.QueuedConnection  # ← 必须
        )
        self.worker.error_occurred.connect(
            self.show_error,
            Qt.ConnectionType.QueuedConnection  # ← 必须
        )
```

#### 3.2 线程生命周期管理

```python
class WorkflowManager:
    """工作流管理器 - 管理线程生命周期"""

    def start_workflow(self, stages: List[StageConfig]):
        """启动工作流"""
        if self.is_running:
            return  # 已有工作流运行中

        self.worker = WorkflowThread(stages, context)
        self.worker.finished.connect(self.on_workflow_finished)
        self.is_running = True
        self.worker.start()

    def stop_workflow(self):
        """停止工作流"""
        if not self.is_running or not self.worker:
            return

        # 优雅终止
        self.worker.requestInterruption()
        if not self.worker.wait(5000):
            # 强制终止
            self.worker.terminate()
            self.worker.wait()

    def on_workflow_finished(self):
        """工作流完成回调"""
        self.is_running = False
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
```

---

### 4. 错误处理模式 (Error Handling Patterns)

#### 4.1 错误处理决策树

```
错误发生
    │
    ├─→ 可恢复（如使用默认值）
    │     │
    │     ├─ 记录 WARNING 日志
    │     ├─ 使用默认值继续
    │     └─ 返回 StageResult(COMPLETED)
    │
    ├─→ 阶段失败（如文件不存在）
    │     │
    │     ├─ 记录 ERROR 日志
    │     ├─ 返回 StageResult(FAILED, suggestions=[...])
    │     └─ 停止当前阶段
    │
    └─→ 致命错误（如配置无效）
          │
          ├─ 记录 CRITICAL 日志
          ├─ 抛出异常
          └─ 终止整个工作流
```

#### 4.2 日志级别决策树

```
需要记录日志？
    │
    ├─→ 开发诊断信息
    │     └─→ DEBUG（生产环境关闭）
    │
    ├─→ 正常流程的关键节点
    │     └─→ INFO（阶段开始/完成、文件操作成功）
    │
    ├─→ 非致命问题，使用默认值继续
    │     └─→ WARNING（配置缺失、使用默认值）
    │
    ├─→ 阶段失败，但有恢复建议
    │     └─→ ERROR（文件操作失败、外部工具失败）
    │
    └─→ 系统无法继续，需要人工介入
          └─→ CRITICAL（配置无效、无法恢复）
```

---

### 5. 配置模式 (Configuration Patterns)

#### 5.1 配置格式边界

```python
# ✅ 正确 - 严格区分配置用途

# TOML 用于：用户项目配置（可手动编辑）
[project]
name = "TMS APP"
simulink_path = "E:\\Projects\\Simulink\\TMS_APP"

# JSON 用于：工作流定义（程序生成/读取）
{
    "stages": [
        {"name": "matlab_gen", "enabled": true, "timeout": 1800}
    ]
}

# ❌ 错误 - 不要混用
```

#### 5.2 配置验证时机

```python
# 三种验证时机

# 1. 加载时验证 - 验证格式和必填字段
def load_config(path: Path) -> dict:
    config = tomllib.loads(path.read_text())
    required = ["simulink_path", "matlab_code_path"]
    errors = [f for f in required if f not in config]
    if errors:
        raise ValueError(f"缺少必填字段: {errors}")
    return config

# 2. 使用前验证 - 验证路径存在性
def validate_paths_exist(config: dict) -> list[str]:
    missing = []
    for key in ["simulink_path", "matlab_code_path"]:
        if not Path(config.get(key, "")).exists():
            missing.append(f"{key}: {config[key]}")
    return missing

# 3. 变更时验证 - 验证新值的有效性
def update_config(config: dict, key: str, value: str) -> bool:
    if key.endswith("_path"):
        if not Path(value).exists():
            return False
    config[key] = value
    return True
```

---

### Enforcement Guidelines

**All AI Agents MUST:**

1. ⭐⭐⭐⭐⭐ 阶段接口：使用统一的 `execute_stage(StageConfig, BuildContext) -> StageResult` 签名
2. ⭐⭐⭐⭐⭐ 信号连接：跨线程信号必须使用 `Qt.ConnectionType.QueuedConnection`
3. ⭐⭐⭐⭐⭐ 超时检测：使用 `time.monotonic()` 而非 `time.time()`
4. ⭐⭐⭐⭐ 错误处理：使用统一的错误类（`ProcessError` 及子类）
5. ⭐⭐⭐⭐ 状态传递：使用 `BuildContext`，不使用全局变量
6. ⭐⭐⭐⭐ 超时配置：从 `DEFAULT_TIMEOUT` 字典获取，不硬编码
7. ⭐⭐⭐ 路径处理：使用 `pathlib.Path` 而非字符串
8. ⭐⭐⭐ 日志记录：使用 `logging` 模块，不使用 `print()`

**代码审查检查清单**：
```python
- [ ] 阶段函数签名: execute_stage(config, context) -> result
- [ ] 信号连接: 所有跨线程信号使用 QueuedConnection
- [ ] 超时函数: 使用 time.monotonic()
- [ ] 错误类: 使用 ProcessError 及子类
- [ ] 路径处理: 使用 pathlib.Path
- [ ] 日志模块: 使用 logging，不用 print
- [ ] 超时配置: 从 DEFAULT_TIMEOUT 获取
- [ ] 状态传递: 使用 BuildContext，不用全局变量
```

---

### Pattern Examples

**完整示例：符合所有模式**

```python
from pathlib import Path
import time
import logging
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from utils.errors import ProcessTimeoutError
from core.models import StageConfig, StageResult, StageStatus, BuildContext
from core.constants import DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)

class MatlabGenStage:
    """MATLAB 代码生成阶段"""

    @staticmethod
    def execute_stage(config: StageConfig, context: BuildContext) -> StageResult:
        """统一的阶段接口"""
        timeout = config.timeout or DEFAULT_TIMEOUT["matlab"]
        matlab_path = Path(context.config.get("simulink_path"))

        # 使用前验证路径
        if not matlab_path.exists():
            return StageResult(
                status=StageStatus.FAILED,
                message=f"Simulink 路径不存在: {matlab_path}",
                suggestions=["检查配置文件中的 simulink_path"]
            )

        logger.info(f"开始 MATLAB 代码生成: {matlab_path}")
        start = time.monotonic()  # 使用 monotonic

        try:
            result = MatlabGenStage._run_matlab(matlab_path, timeout, start)
            # 状态传递
            context.state["matlab_output"] = result.output_files
            return result

        except ProcessTimeoutError as e:
            logger.error(f"MATLAB 超时: {e}")
            return StageResult(
                status=StageStatus.FAILED,
                message=str(e),
                suggestions=e.suggestions
            )

# PyQt6 线程包装
class WorkflowThread(QThread):
    progress_update = pyqtSignal(int, str)
    stage_complete = pyqtSignal(StageResult)

    def run(self):
        for stage_config in self.stages:
            result = execute_stage(stage_config, self.context)
            self.stage_complete.emit(result)
            if result.status == StageStatus.FAILED:
                return
```

---

## Project Structure & Boundaries

### Complete Project Directory Structure

```
mbd_cicdkits/
├── pyproject.toml                   # Python 项目配置（现代标准）
├── requirements.txt                 # 依赖列表
├── README.md                        # 项目说明
├── LICENSE                          # 许可证
├── .gitignore                       # Git 忽略文件
├── build.spec                       # PyInstaller 打包配置
│
├── src/                             # 源代码根目录
│   ├── __init__.py
│   ├── __main__.py                  # 支持 python -m mbd_cicdkits
│   ├── main.py                      # 应用入口点
│   │
│   ├── ui/                          # PyQt6 UI 层（类）
│   │   ├── __init__.py
│   │   ├── main_window.py           # 主窗口类
│   │   ├── widgets/                 # 自定义控件
│   │   │   ├── __init__.py
│   │   │   ├── progress_panel.py    # 进度面板
│   │   │   ├── log_viewer.py        # 日志查看器
│   │   │   ├── stage_status.py      # 阶段状态显示
│   │   │   └── config_form.py       # 配置表单
│   │   └── dialogs/                 # 对话框
│   │       ├── __init__.py
│   │       ├── new_project_dialog.py    # 新建项目对话框
│   │       ├── settings_dialog.py        # 设置对话框
│   │       ├── env_check_dialog.py       # 环境检查对话框
│   │       └── confirm_dialog.py         # 确认对话框
│   │
│   ├── core/                        # 核心业务逻辑（函数）
│   │   ├── __init__.py
│   │   ├── config.py                # 配置管理（加载/保存/验证）
│   │   ├── workflow.py              # 工作流编排
│   │   ├── models.py                # 数据模型（StageConfig, StageResult, BuildContext）
│   │   └── constants.py             # 常量定义（DEFAULT_TIMEOUT）
│   │
│   ├── stages/                      # 工作流阶段（函数模块）
│   │   ├── __init__.py
│   │   ├── base.py                  # 阶段基类和接口定义
│   │   ├── matlab_gen.py            # 阶段1: MATLAB 代码生成（预留接口）
│   │   ├── file_process.py          # 阶段2: 文件处理
│   │   ├── iar_compile.py           # 阶段3: IAR 编译
│   │   ├── a2l_process.py           # 阶段4: A2L 处理（Python 实现）
│   │   └── package.py               # 阶段5: 文件归纳
│   │
│   ├── integrations/                # 外部工具集成
│   │   ├── __init__.py
│   │   ├── matlab.py                # MATLAB 预留接口（暂不实现）
│   │   ├── iar.py                   # IAR 命令行集成
│   │   └── env_detector.py          # 环境检测（MATLAB/IAR 版本检测）
│   │
│   ├── a2l/                         # A2L 处理模块（新增 2026-02-25）
│   │   ├── __init__.py
│   │   ├── elf_parser.py            # ELF 文件解析（pyelftools）
│   │   ├── a2l_parser.py            # A2L 文件解析
│   │   └── address_updater.py       # A2L 地址更新
│   │
│   └── utils/                       # 工具函数
│       ├── __init__.py
│       ├── process_mgr.py           # 进程管理器（超时、清理）
│       ├── errors.py                # 统一错误类（ProcessError 等）
│       ├── logger.py                # 日志配置（QtSignalHandler）
│       ├── file_ops.py              # 文件操作（原子性移动）
│       ├── retry.py                 # 重试装饰器
│       ├── cleanup.py               # 资源清理管理器
│       └── path_utils.py            # 路径工具（长路径处理）
│
├── resources/                       # 资源文件
│   ├── icons/                       # 图标
│   │   ├── app_icon.ico             # 应用图标
│   │   ├── start.png                # 启动按钮图标
│   │   ├── stop.png                 # 停止按钮图标
│   │   └── status_*.png             # 状态图标
│   └── templates/                   # 模板文件
│       ├── xcp_header.txt           # XCP 协议头文件模板
│       └── workflow_template.json   # 工作流模板
│
├── configs/                         # 默认配置模板
│   ├── default_workflow.json        # 默认工作流配置
│   ├── settings.toml                # 应用设置模板
│   └── logging.conf                 # 日志配置
│
├── tests/                           # 测试代码
│   ├── __init__.py
│   ├── conftest.py                  # pytest 配置
│   ├── unit/                        # 单元测试
│   │   ├── __init__.py
│   │   ├── test_process_mgr.py      # 进程管理器测试
│   │   ├── test_file_ops.py         # 文件操作测试
│   │   ├── test_config.py           # 配置管理测试
│   │   ├── test_errors.py           # 错误类测试
│   │   └── test_models.py           # 数据模型测试
│   └── integration/                 # 集成测试
│       ├── __init__.py
│       ├── test_matlab_integration.py   # MATLAB 集成测试
│       ├── test_workflow.py             # 工作流测试
│       └── test_env_detection.py        # 环境检测测试
│
└── docs/                            # 文档
    ├── architecture.md              # 架构文档（本文档）
    ├── api.md                       # API 文档
    └── user_guide.md                # 用户指南
```

### Architectural Boundaries

#### Component Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer (PyQt6)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ MainWindow   │  │  Dialogs     │  │  Widgets     │      │
│  │ (主窗口)      │  │ (对话框)      │  │ (自定义控件)  │      │
│  └───────┬──────┘  └───────┬──────┘  └───────┬──────┘      │
│          │                 │                 │              │
│          └─────────────────┴─────────────────┘              │
│                            │                                │
│                    ┌───────▼───────┐                        │
│                    │ Qt Signals    │ (QueuedConnection)    │
│                    └───────┬───────┘                        │
└────────────────────────────┼────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Core Layer      │
                    │  (业务逻辑)       │
                    │  ┌───────────┐   │
                    │  │ workflow  │   │
                    │  │ config    │   │
                    │  │ models    │   │
                    │  └─────┬─────┘   │
                    └──────────┼────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
        ┌───────▼──────┐ ┌────▼─────┐ ┌─────▼─────┐
        │   Stages     │ │Integrations│ │  Utils   │
        │ (5个阶段)    │ │ (外部工具) │ │ (工具函数) │
        │              │ │            │ │           │
        │ matlab_gen   │ │ matlab    │ │ process_mgr│
        │ file_process │ │ iar       │ │ errors    │
        │ iar_compile  │ │ detector  │ │ logger    │
        │ a2l_process  │ └────────────┘ │ file_ops  │
        │ package      │                └───────────┘
        └──────────────┘
```

#### Communication Boundaries

| 层级 | 通信方式 | 连接类型 |
|------|---------|---------|
| UI → Core | PyQt6 信号槽 | QueuedConnection |
| Core → Stages | 直接函数调用 | N/A（同线程） |
| Core → Integrations | 直接函数调用 | N/A |
| Utils → 所有 | 直接导入 | N/A |
| 所有 → 日志 | logging 模块 | QtSignalHandler |

#### Data Boundaries

| 数据类型 | 存储位置 | 访问方式 |
|---------|---------|---------|
| 项目配置 | TOML 文件 | `core/config.py` |
| 工作流定义 | JSON 文件 | `core/config.py` |
| 应用设置 | TOML 文件 | `core/config.py` |
| 构建状态 | BuildContext（内存） | 阶段间传递 |
| 日志 | 文件 + UI | `utils/logger.py` |

### Requirements to Structure Mapping

#### Epic 1: 项目配置管理

| 需求 | 实现文件 |
|------|---------|
| FR-001: 创建配置 | `src/ui/dialogs/new_project_dialog.py` |
| FR-002: 保存 TOML | `src/core/config.py` |
| FR-003: 加载配置 | `src/core/config.py` |
| FR-004: 删除配置 | `src/core/config.py` |
| FR-005: 编辑配置 | `src/ui/dialogs/new_project_dialog.py` |
| FR-006: 工作流模板 | `configs/default_workflow.json` |

#### Epic 2: 工作流执行

| 需求 | 实现文件 |
|------|---------|
| FR-010: 启动构建 | `src/ui/main_window.py` |
| FR-011: 执行工作流 | `src/core/workflow.py` |
| FR-012: MATLAB 执行 | `src/stages/matlab_gen.py` |
| FR-013: 提取代码文件 | `src/stages/file_process.py` |
| FR-014: Cal.c 处理 | `src/stages/file_process.py` |
| FR-015: 移动文件 | `src/utils/file_ops.py` |
| FR-016: IAR 编译 | `src/stages/iar_compile.py` |
| FR-017: A2L 更新 | `src/stages/a2l_process.py` |
| FR-018: XCP 替换 | `src/stages/a2l_process.py` |
| FR-019: 时间戳文件夹 | `src/stages/package.py` |
| FR-020: 归集文件 | `src/stages/package.py` |

#### Epic 3: 构建监控与反馈

| 需求 | 实现文件 |
|------|---------|
| FR-022: 进度显示 | `src/ui/widgets/progress_panel.py` |
| FR-023: 日志查看 | `src/ui/widgets/log_viewer.py` |
| FR-024: 进程输出捕获 | `src/utils/process_mgr.py` |
| FR-025: 阶段状态 | `src/ui/widgets/stage_status.py` |
| FR-026: 时间戳记录 | `src/core/models.py` |

#### Epic 4: 错误处理与诊断

| 需求 | 实现文件 |
|------|---------|
| FR-027: 错误信息 | `src/utils/errors.py` |
| FR-028: 失败阶段 | `src/core/workflow.py` |
| FR-029: 修复建议 | `src/utils/errors.py` |
| FR-030: 错误日志 | `src/utils/logger.py` |
| FR-031: 异常退出检测 | `src/utils/process_mgr.py` |

#### Epic 5: 环境验证与文件管理

| 需求 | 实现文件 |
|------|---------|
| FR-032: MATLAB 检测 | `src/integrations/env_detector.py` |
| FR-033: IAR 检测 | `src/integrations/env_detector.py` |
| FR-034: MATLAB 版本 | `src/integrations/env_detector.py` |
| FR-035: IAR 版本 | `src/integrations/env_detector.py` |
| FR-036: 环境提示 | `src/ui/dialogs/env_check_dialog.py` |
| FR-037: 权限检查 | `src/utils/file_ops.py` |
| FR-038: 清空目录 | `src/utils/file_ops.py` |
| FR-039: 验证文件操作 | `src/utils/file_ops.py` |
| FR-040: 文件操作日志 | `src/utils/logger.py` |
| FR-041: 命名规范 | `src/stages/package.py` |

#### Cross-Cutting Concerns

| 关注点 | 实现位置 |
|--------|---------|
| 错误处理 | `src/utils/errors.py` |
| 日志记录 | `src/utils/logger.py` |
| 进程管理 | `src/utils/process_mgr.py` |
| 配置验证 | `src/core/config.py` |
| 状态传递 | `src/core/models.py` (BuildContext) |
| 超时管理 | `src/core/constants.py` |
| 线程通信 | `src/ui/main_window.py` (信号槽) |

### Integration Points

#### Internal Communication

```
MainWindow (UI Thread)
    │
    ├─ progress_update ──────┐
    ├─ stage_complete ───────┤
    ├─ log_message ───────────┼───► WorkflowThread (Worker Thread)
    └─ error_occurred ────────┘
                                  │
                                  ▼
                           execute_workflow()
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              matlab_gen()  file_process()  iar_compile()
                    │             │             │
                    └─────────────┴─────────────┘
                                  │
                           BuildContext
                           (状态传递)
```

#### External Integrations

| 外部工具 | 集成方式 | 接口文件 |
|---------|---------|---------|
| MATLAB | 预留接口（暂不实现） | `src/integrations/matlab.py` |
| IAR | 命令行 (subprocess) | `src/integrations/iar.py` |
| A2L 处理 | Python (pyelftools) | `src/a2l/address_updater.py` |
| 文件系统 | pathlib + shutil | `src/utils/file_ops.py` |

> ⚠️ **变更说明 (2026-02-25)：** MATLAB 集成改为预留接口。A2L 地址替换改用纯 Python 实现。

#### Data Flow

```
用户输入 → ProjectConfig (TOML)
    │
    ▼
加载配置 → BuildContext.config
    │
    ▼
执行工作流 → 5个阶段顺序执行
    │
    ├─→ 阶段1: MATLAB 生成 → 输出文件
    │       │
    │       └─→ BuildContext.state["matlab_output"]
    │
    ├─→ 阶段2: 文件处理 → 输出文件
    │       │
    │       └─→ BuildContext.state["processed_files"]
    │
    ├─→ 阶段3: IAR 编译 → ELF/HEX
    │       │
    │       └─→ BuildContext.state["build_output"]
    │
    ├─→ 阶段4: A2L 处理 → A2L文件
    │       │
    │       └─→ BuildContext.state["a2l_file"]
    │
    └─→ 阶段5: 文件归纳 → 目标文件夹
            │
            └─→ StageResult (成功/失败)
                    │
                    ▼
              UI 显示结果
```

### File Organization Patterns

#### Configuration Files

| 文件 | 用途 | 格式 |
|------|------|------|
| `pyproject.toml` | Python 项目配置 | TOML |
| `requirements.txt` | 依赖列表 | 文本 |
| `build.spec` | PyInstaller 配置 | Python |
| `configs/default_workflow.json` | 默认工作流 | JSON |
| `configs/settings.toml` | 应用设置 | TOML |

#### Source Organization

| 目录 | 内容 | 类型 |
|------|------|------|
| `src/ui/` | PyQt6 类 | 类 |
| `src/core/` | 业务逻辑 | 函数 |
| `src/stages/` | 工作流阶段 | 函数模块 |
| `src/integrations/` | 外部工具集成 | 函数模块 |
| `src/utils/` | 工具函数 | 函数 |

**configs/ vs resources/templates/ 区别**：
- `configs/` - 可编辑的配置文件（默认工作流、应用设置）
- `resources/templates/` - 只读模板文件（XCP 头文件模板）

#### Test Organization

| 目录 | 内容 |
|------|------|
| `tests/unit/` | 单元测试（测试单个函数/类） |
| `tests/integration/` | 集成测试（测试模块间交互） |

**测试与源码完全分离**，便于打包时排除测试代码。

### Party Mode Review Results

**审查日期**: 2026-02-03
**审查委员会**: Winston (Architect), Amelia (Dev), Bond (Agent Builder), Murat (Test)
**总体评分**: 8.5/10

**审查结论**: ✅ 批准项目结构

**改进建议**:

| # | 建议 | 优先级 | 实施阶段 |
|---|------|--------|---------|
| 1 | 添加 `src/__main__.py` | Medium | MVP |
| 2 | 文档化 ui/ 组织策略 | Low | MVP |
| 3 | 明确 integrations/stages 边界 | Medium | MVP |
| 4 | 文档说明 configs vs templates | Low | MVP |

**架构健康度**: 9/10 (Bond)
- ✅ 单一职责原则
- ✅ 单向依赖流
- ✅ 无循环依赖
- ⚠️ models.py 可能需要拆分（未来）

**可测试性评分**: 8.5/10 (Murat)
- ✅ 测试与源码分离
- ✅ utils/ 完全可独立测试
- ⚠️ MATLAB/IAR 集成测试需要真实环境

---

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
所有架构决策彼此兼容，无冲突：
- Python 3.10+ + PyQt6 组合稳定
- TOML (用户配置) + JSON (工作流) 用途明确
- dataclass 与所有模块兼容
- QThread + QueuedConnection 确保线程安全
- subprocess + psutil 组合可靠

**Pattern Consistency:**
所有实现模式一致支持架构决策：
- PEP 8 命名贯穿所有模块
- BuildContext 状态传递规则统一
- ProcessError 错误类层次一致
- time.monotonic() + DEFAULT_TIMEOUT 超时模式一致
- logging + QtSignalHandler 日志模式一致

**Structure Alignment:**
项目结构完全支持所有架构决策：
- UI 层 (PyQt6 类) → src/ui/
- 业务层 (函数) → src/core/
- 工作流阶段 (函数模块) → src/stages/
- 集成 (函数模块) → src/integrations/
- 工具 (函数) → src/utils/

### Requirements Coverage Validation ✅

**Epic Coverage:**
所有 5 个 Epic 都有完整的架构支持：

| Epic | 架构支持 | 关键文件 |
|------|---------|---------|
| Epic 1: 项目配置管理 | ✅ 完整 | `core/config.py`, `ui/dialogs/` |
| Epic 2: 工作流执行 | ✅ 完整 | `core/workflow.py`, 5 个阶段 |
| Epic 3: 构建监控 | ✅ 完整 | `ui/widgets/`, 信号机制 |
| Epic 4: 错误处理 | ✅ 完整 | `utils/errors.py` |
| Epic 5: 环境验证 | ✅ 完整 | `integrations/env_detector.py` |

**Functional Requirements Coverage:**
全部 57 个 FR 都有架构支持：
- Epic 1: FR-001 至 FR-006 (6 个) ✅
- Epic 2: FR-010 至 FR-021 (12 个) ✅
- Epic 3: FR-022 至 FR-026 (5 个) ✅
- Epic 4: FR-027 至 FR-031 (5 个) ✅
- Epic 5: FR-032 至 FR-041 (10 个) ✅
- Phase 2 需求已预留扩展空间

**Non-Functional Requirements Coverage:**
所有关键 NFR 都有架构支持：

| NFR | 要求 | 架构支持 |
|-----|------|---------|
| NFR-P001 | 15-20 分钟构建 | 超时配置 + 后台线程 |
| NFR-P002 | <3 秒启动 | 轻量架构 |
| NFR-P003 | <500ms UI 响应 | QThread + signals |
| NFR-R001 | ≥98% 成功率 | 进程管理 + 错误处理 |
| NFR-R003 | 清晰错误提示 | ProcessError + suggestions |

### Implementation Readiness Validation ✅

**Decision Completeness:**
✅ 9 个核心架构决策已完整文档化
✅ 4 个 ADR 已创建
✅ 技术栈版本明确
✅ 派对模式修正已应用

**Structure Completeness:**
✅ 完整目录树已定义（包含 `src/__main__.py`）
✅ 组件边界已建立
✅ 集成点已映射
✅ 需求→文件映射完整

**Pattern Completeness:**
✅ 7 个高影响冲突点已识别并解决
✅ 5 大模式类别已定义
✅ 8 条强制规则已建立
✅ 完整代码示例已提供

### Gap Analysis Results

**Critical Gaps:** 无 ✅

**Important Gaps:**
| # | 缺口 | 解决方案 |
|---|------|---------|
| 1 | `src/__main__.py` 内容未定义 | 实施时添加: `from src.main import main; main()` |
| 2 | PyInstaller 配置详细内容 | 实施时细化 build.spec |
| 3 | 测试 Mock 策略 | 使用 pytest.mock，文档已标识 |

**Nice-to-Have Gaps:**
- 性能监控指标（Phase 2）
- 开发工具配置（Phase 2）
- CI/CD 配置（Phase 2）

### Validation Issues Addressed

**已解决的问题**（来自派对模式）：
1. ✅ time.monotonic() vs time.time() - 已修正
2. ✅ 统一错误基类 - 已添加
3. ✅ PyQt6 信号 QueuedConnection - 已明确

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] 项目上下文已分析
- [x] 规模和复杂度已评估
- [x] 技术约束已识别
- [x] 横切关注点已映射

**✅ Architectural Decisions**
- [x] 关键决策已文档化（9 个决策 + 4 个 ADR）
- [x] 技术栈已完全指定
- [x] 集成模式已定义
- [x] 性能考虑已处理

**✅ Implementation Patterns**
- [x] 命名约定已建立
- [x] 结构模式已定义
- [x] 通信模式已指定
- [x] 流程模式已文档化

**✅ Project Structure**
- [x] 完整目录结构已定义
- [x] 组件边界已建立
- [x] 集成点已映射
- [x] 需求→结构映射完整

### Architecture Readiness Assessment

**Overall Status:** ✅ **READY FOR IMPLEMENTATION**

**Confidence Level:** 高 (基于全面验证和派对模式审查)

**Key Strengths:**
- 清晰的模块边界和单向依赖流
- 针对桌面应用优化的架构模式
- 98% 可靠性目标的系统性保证
- 完整的错误处理和恢复机制
- AI Agent 友好的一致性规则

**Areas for Future Enhancement:**
- Phase 2: 高级工作流功能（阶段跳过、取消）
- Phase 2: 日志搜索和过滤
- Phase 2: 自动路径检测
- Phase 3: 性能监控和优化

### Implementation Handoff

**AI Agent Guidelines:**
1. 严格遵循所有架构决策
2. 始终使用实现模式
3. 尊重项目结构和边界
4. 遇到问题时参考此文档

**First Implementation Priority:**
1. 创建项目目录结构
2. 实现 `utils/errors.py`（错误基类）
3. 实现 `core/models.py`（数据模型）
4. 实现 `utils/process_mgr.py`（进程管理器）
5. 实现 `utils/logger.py`（日志框架）

**Estimated Module Implementation Order:**
```
Phase 1: Foundation (3-4 天)
├── dataclass models
├── error classes
└── logging framework

Phase 2: Core (5-8 天)
├── process manager
├── file operations
└── configuration

Phase 3: Integration (7-9 天)
├── MATLAB integration
├── IAR integration
└── workflow stages

Phase 4: UI (2-3 天)
├── main window
├── widgets
└── dialogs
```

---
