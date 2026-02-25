# Sprint 变更提案

**提案日期：** 2026-02-25
**项目：** 181_CICDRedo (MBD_CICDKits)
**提案人：** link
**审批状态：** ✅ 已批准

---

## 1. 问题摘要

| 项目 | 内容 |
|------|------|
| **触发场景** | 在另一台电脑运行 PyInstaller 打包的 exe |
| **核心问题** | MATLAB Engine API for Python 在打包后无法正常工作 |
| **问题类型** | 技术限制 - 部署时发现 |
| **影响范围** | Story 2.5（MATLAB代码生成）、Story 2.9（A2L地址更新） |
| **发现时间** | 打包部署测试阶段 |

**问题陈述：**

> 在使用 PyInstaller 打包后，MATLAB Engine API 在目标机器上无法正常加载。经评估，决定**移除 MATLAB Engine 依赖**，将 A2L 处理功能（地址替换）改用纯 Python 实现。原有 MATLAB 代码生成功能保留接口暂不实现。

---

## 2. Epic 影响

| Epic | 状态 | 变更类型 | 具体内容 |
|------|------|---------|---------|
| **Epic 2** | done | 修改 | Story 2.5 改为预留接口，Story 2.9 改用 Python 实现 |
| **Epic 5** | backlog | 修改 | Story 5.1/5.2 移除 MATLAB Engine 检测 |
| Epic 1 | done | 无变更 | - |
| Epic 3 | in-progress | 无变更 | - |
| Epic 4 | backlog | 无变更 | - |

### Story 变更详情

**Story 2.5 - 执行 MATLAB 代码生成阶段**
- 原验收标准：使用 MATLAB Engine API 调用 genCode.m
- 新验收标准：预留接口，暂不实现（返回成功状态）

**Story 2.9 - 更新 A2L 文件变量地址**
- 原验收标准：通过 MATLAB Engine 执行 `rtw.asap2SetAddress()`
- 新验收标准：使用 Python 实现（基于原有 .m 脚本逻辑转换）
  - 解析 ELF 文件提取符号地址
  - 解析 A2L 文件结构
  - 更新 A2L 中的变量地址

**Story 5.1 - 启动时检测 MATLAB 安装**
- 原验收标准：检查 MATLAB 安装路径 + MATLAB Engine API
- 新验收标准：仅检查 MATLAB 安装路径（移除 Engine API 检测）

**Story 5.2 - 验证 MATLAB 版本兼容性**
- 原验收标准：检查 MATLAB 版本 + Engine API 版本
- 新验收标准：仅检查 MATLAB 版本（移除 Engine API 版本检测）

---

## 3. 文档调整需求

| 文档 | 变更类型 | 具体修改 |
|------|---------|---------|
| **PRD** | 修改 + 删除 | 修改 FR-012, FR-017；删除 NFR-I002, NFR-I003 |
| **Architecture** | 修改 | 移除 MATLAB Engine 集成；新增 Python A2L 模块 |
| **Epics** | 修改 | 更新 Story 2.5, 2.9, 5.1, 5.2 的验收标准 |
| **打包配置** | 修改 | 更新依赖：移除 matlab.engine，添加 pyelftools |

### PRD 具体修改

| 需求ID | 修改类型 | 内容 |
|--------|---------|------|
| FR-012 | 修改 | 系统预留 MATLAB 代码生成接口（暂不实现） |
| FR-017 | 修改 | 系统使用 Python 解析 ELF 文件更新 A2L 地址 |
| NFR-I002 | 删除 | 不再使用 MATLAB Engine API |
| NFR-I003 | 删除 | A2L 阶段不再启动 MATLAB 进程 |

### Architecture 具体修改

**移除：**
- MATLAB Engine API for Python 集成
- MATLAB 进程管理模块（A2L 阶段）

**新增：**
- Python A2L 地址替换模块（`a2l_address_updater.py`）
  - 解析 ELF 文件提取符号地址
  - 解析 A2L 文件结构
  - 更新 A2L 中的变量地址
- 依赖：pyelftools（解析 ELF）

---

## 4. 推荐方案

| 维度 | 评估 |
|------|------|
| **选择方案** | 选项 1 - 直接调整 |
| **工作量** | 🟡 中等 |
| **风险级别** | 🟢 低 |
| **时间线影响** | 最小 - 不影响 MVP 交付 |

### 选择理由

1. **功能目标不变** - 仍然是 5 阶段自动化流程，只是实现方式改变
2. **有参考实现** - 原有 MATLAB 脚本可作为 Python 实现的参考
3. **架构简化** - 移除 MATLAB Engine 依赖实际上降低了部署复杂度
4. **修改范围可控** - 无需新增 Epic，仅修改现有 Stories
5. **长期收益** - 纯 Python 实现更易于打包、分发和维护

---

## 5. 行动计划

### 阶段 1: 架构文档更新
- [ ] 更新 Architecture.md - 移除 MATLAB Engine，新增 Python A2L 模块
- [ ] 更新依赖列表

### 阶段 2: Story 修改
- [ ] Story 2.5 - 修改验收标准为"预留接口"
- [ ] Story 2.9 - 修改验收标准为"Python 实现"
- [ ] Story 5.1 - 移除 MATLAB Engine 检测
- [ ] Story 5.2 - 移除 Engine API 版本检测

### 阶段 3: 代码实现
- [ ] 实现 Python A2L 地址替换模块（基于原有 .m 脚本）
- [ ] 添加 pyelftools 依赖
- [ ] 更新打包配置

### 阶段 4: 测试验证
- [ ] 验证 A2L 地址替换功能正确性
- [ ] 打包测试

---

## 6. 交接计划

### 变更范围分类

| 级别 | 本次分类 |
|------|---------|
| Minor | ✅ **开发团队直接实现** |

### 职责分配

| 角色 | 职责 | 具体任务 |
|------|------|---------|
| **Scrum Master** | 文档更新 | 更新 Architecture.md、Epics.md 中的 Story 验收标准 |
| **开发团队** | 代码实现 | 实现 Python A2L 地址替换模块，更新依赖配置 |
| **开发团队** | 测试验证 | 验证 A2L 功能正确性，打包测试 |

### 交付物清单

| 交付物 | 责任人 | 状态 |
|--------|--------|------|
| Architecture.md 更新 | Scrum Master | 待完成 |
| Story 2.5 验收标准修改 | Scrum Master | 待完成 |
| Story 2.9 验收标准修改 | Scrum Master | 待完成 |
| Story 5.1/5.2 验收标准修改 | Scrum Master | 待完成 |
| Python A2L 地址替换模块 | 开发团队 | 待完成 |
| pyelftools 依赖集成 | 开发团队 | 待完成 |
| 打包配置更新 | 开发团队 | 待完成 |
| 功能测试验证 | 开发团队 | 待完成 |

---

## 7. MVP 影响声明

| 项目 | 结论 |
|------|------|
| **MVP 是否受影响？** | ❌ **否** |
| **核心目标是否改变？** | ❌ 否 - 仍实现 5 阶段自动化 |
| **MVP 范围是否缩减？** | ❌ 否 |
| **交付时间线是否延迟？** | ❌ 否 - 工作量在可控范围内 |

---

## 8. 审批记录

| 日期 | 审批人 | 决定 | 备注 |
|------|--------|------|------|
| 2026-02-25 | link | ✅ 批准 | 直接调整方案 |

---

## 附录：sprint-status.yaml 更新

```yaml
# Epic 2: 工作流执行
# ⚠️ CHANGE-2026-02-25: 移除 MATLAB Engine 依赖，改用纯 Python 实现
2-5-execute-matlab-code-generation-phase: done  # 改为预留接口
2-9-update-a2l-file-variable-addresses: needs-revision  # 需要改用 Python 实现

# Epic 5: 环境验证与文件管理
# ⚠️ CHANGE-2026-02-25: 5-1/5-2 移除 MATLAB Engine 检测，仅保留 MATLAB 安装检测
5-1-startup-detect-matlab-installation: needs-revision  # 移除 Engine API 检测
5-2-validate-matlab-version-compatibility: needs-revision  # 移除 Engine API 版本检测
```
