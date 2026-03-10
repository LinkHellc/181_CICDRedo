# MBD-CICDKits 使用手册

## 1. 项目概述

**MBD_CICDKits** 是一款用于 Simulink 模型开发的 CI/CD 自动化工具，实现从模型生成代码到最终软件烧录文件和标定文件生成的全流程自动化。

### 核心价值

- **自动化流程**：将手动操作自动化，减少人工错误
- **模块化设计**：支持完整流程和单步执行两种模式
- **可视化界面**：PyQt6 图形界面，操作直观简便

### 技术栈

| 组件 | 技术 |
|------|------|
| 开发语言 | Python 3.10+ |
| UI 框架 | PyQt6 |
| 代码生成 | MATLAB (Simulink Coder) |
| 编译工具 | IAR Embedded Workbench |
| ELF 解析 | pyelftools |

---

## 2. 系统要求

### 2.1 硬件要求

- **处理器**：Intel Core i5 或同等性能处理器
- **内存**：建议 8GB 及以上
- **硬盘空间**：至少 2GB 可用空间

### 2.2 软件要求

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.10 或更高 | 必需 |
| MATLAB | R2020a 或更高 | 用于代码生成（可选） |
| IAR | 9.x 或更高 | 用于编译工程 |
| 操作系统 | Windows 10/11 | 当前仅支持 Windows |

### 2.3 Python 依赖

```bash
# 核心依赖
PyQt6>=6.6.0
tomli>=2.0.0          # Python 3.10 需要
tomli-w>=1.0.0        # TOML 文件写入
pyelftools>=0.31      # ELF 文件解析
```

---

## 3. 快速开始

### 3.1 安装步骤

#### 步骤 1：克隆项目

```bash
git clone <repository-url>
cd 181_CICDRedo
```

#### 步骤 2：安装依赖

```bash
pip install -r requirements.txt
```

#### 步骤 3：启动应用

```bash
python run_ui.py
```

### 3.2 命令行选项

```bash
python run_ui.py          # 默认深色主题
python run_ui.py --light  # 浅色主题
python run_ui.py --dark   # 深色主题
```

---

## 4. 核心流程说明

MBD_CICDKits 包含 5 个核心处理阶段：

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. 项目配置     │ -> │  2. 代码生成     │ -> │  3. 文件处理     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  5. 文件打包     │ <- │  4. A2L处理      │ <- │    (继续)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 4.1 各阶段说明

| 阶段 | 说明 | 输入 | 输出 |
|------|------|------|------|
| **项目配置** | 配置路径参数 | 用户输入 | 配置文件 (.toml) |
| **MATLAB代码生成** | 调用 Simulink 生成代码 | Simulink 模型 | C/H 代码文件 |
| **文件处理** | 处理 Cal.c，排除接口文件 | 生成的代码 | 处理后的代码 |
| **IAR编译** | 编译 IAR 工程 | 处理后的代码 | ELF/HEX 文件 |
| **A2L处理** | 更新变量地址 | ELF + A2L 模板 | 最终 A2L 文件 |
| **文件打包** | 归集最终产物 | HEX + A2L | 打包文件夹 |

---

## 5. 配置说明

### 5.1 配置文件格式

配置文件采用 TOML 格式，存储在 `configs/projects/` 目录下：

```toml
name = "项目名称"

# 路径配置
simulink_path = "D:/MATLAB/Project/E0Y_TMS"
matlab_code_path = "D:/IDE/E0Y/600-CICD/02_genHex/M7/src/TmsApp_APP"
a2l_path = "D:/MATLAB/Project/E0Y_TMS/22_A2L/TmsApp.a2l"
target_path = "D:/IDE/E0Y/600-CICD/05_finObj"
iar_project_path = "D:/IDE/E0Y/600-CICD/02_genHex/Neusar_CYT4BF.eww"
a2l_tool_path = "D:/IDE/E0Y/600-CICD/04_genA2L"

# MATLAB 配置
matlab_reuse_existing = true    # 复用已打开的 MATLAB
matlab_close_after_build = true # 构建后关闭 MATLAB
matlab_timeout = 60             # 超时时间（秒）
matlab_memory_limit = "2GB"     # 内存限制

# 自定义参数（可选）
[custom_params]
```

### 5.2 配置项说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `name` | 项目名称 | `"E0Y"` |
| `simulink_path` | Simulink 工程目录 | `"D:/MATLAB/Project/E0Y_TMS"` |
| `matlab_code_path` | MATLAB 代码存放路径 | `"D:/IDE/E0Y/.../TmsApp_APP"` |
| `a2l_path` | A2L 模板文件路径 | `"D:/MATLAB/Project/.../TmsApp.a2l"` |
| `target_path` | 最终输出目录 | `"D:/IDE/E0Y/.../05_finObj"` |
| `iar_project_path` | IAR 工程文件路径 | `"D:/IDE/E0Y/.../Neusar_CYT4BF.eww"` |
| `a2l_tool_path` | A2L 工具目录 | `"D:/IDE/E0Y/.../04_genA2L"` |

---

## 6. 使用指南

### 6.1 创建新项目

1. 启动应用后，点击 **"新建项目"**
2. 填写项目配置信息：
   - 项目名称
   - 各路径配置
   - MATLAB 相关选项
3. 点击 **"保存"** 完成创建

### 6.2 执行工作流

#### 完整流程模式

1. 选择已配置的项目
2. 点击 **"执行完整工作流"**
3. 等待各阶段依次执行完成

#### 单步执行模式

1. 选择项目
2. 选择需要执行的阶段：
   - MATLAB 代码生成
   - 代码文件处理
   - IAR 工程编译
   - A2L 文件处理
   - 最终文件打包
3. 点击 **"执行选中阶段"**

### 6.3 监控执行进度

- **进度面板**：显示当前执行阶段和进度百分比
- **日志面板**：实时显示执行日志
- **状态指示**：显示各阶段的执行状态（待执行/执行中/成功/失败）

### 6.4 取消执行

如需中断执行：
1. 点击 **"取消执行"** 按钮
2. 确认取消操作
3. 系统将安全停止当前阶段

---

## 7. 输出文件说明

### 7.1 文件命名规则

| 文件类型 | 命名格式 | 示例 |
|----------|----------|------|
| A2L 模板 | `tmsAPP[_年_月_日_时_分].a2l` | `tmsAPP_2026_02_27_15_43.a2l` |
| A2L 最终 | `tmsAPP_upAdress[_年_月_日_时_分].a2l` | `tmsAPP_upAdress_2026_02_27_15_43.a2l` |
| HEX 文件 | `VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB_[时间戳].hex` | `VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB_20260227_V99_15_43.hex` |
| 输出文件夹 | `MBD_CICD_Obj_[_年_月_日_时_分]` | `MBD_CICD_Obj_2026_02_27_15_43` |

### 7.2 最终输出结构

```
05_finObj/
└── MBD_CICD_Obj_2026_02_27_15_43/
    ├── VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB_20260227_V99_15_43.hex
    └── tmsAPP_upAdress_2026_02_27_15_43.a2l
```

---

## 8. 常见问题

### 8.1 环境相关问题

**Q: 提示 "PyQt6 未安装"？**

A: 请执行以下命令安装依赖：
```bash
pip install -r requirements.txt
```

**Q: IAR 编译失败？**

A: 请检查：
1. IAR 工程路径是否正确配置
2. IAR 编译器是否正确安装
3. 项目路径是否包含中文字符（建议使用英文路径）

### 8.2 MATLAB 相关问题

**Q: MATLAB 代码生成超时？**

A: 可以尝试：
1. 增加 `matlab_timeout` 配置值
2. 检查 Simulink 模型是否有错误
3. 确认 MATLAB 版本兼容性（R2020a+）

### 8.3 A2L 处理问题

**Q: A2L 地址更新失败？**

A: 请确认：
1. ELF 文件已正确生成
2. A2L 模板文件存在且格式正确
3. `a2l_tool_path` 路径配置正确

### 8.4 文件处理问题

**Q: Cal.c 文件处理不生效？**

A: 请检查：
1. Cal.c 文件是否存在于生成的代码中
2. 文件编码是否为 UTF-8
3. 内存区域定义代码是否正确插入

---

## 9. 目录结构

```
181_CICDRedo/
├── run_ui.py                    # 应用启动入口
├── requirements.txt             # Python 依赖
├── CLAUDE.md                    # 项目说明
├── MBD-CICDKits使用手册.md      # 本文档
│
├── src/                         # 源代码
│   ├── core/                    # 核心模块
│   ├── ui/                      # UI 界面
│   ├── stages/                  # 工作流阶段
│   ├── integrations/            # 集成接口
│   └── utils/                   # 工具函数
│
├── configs/                     # 配置文件
│   └── projects/                # 项目配置
│       ├── E0Y.toml
│       └── test_project.toml
│
├── tests/                       # 测试代码
│   ├── unit/                    # 单元测试
│   └── integration/             # 集成测试
│
└── 00_用户输入需求与材料/        # 原始需求文档
```

---

## 10. 故障排查

### 10.1 启用调试日志

如需详细日志，可在启动时设置环境变量：

```bash
set DEBUG=1
python run_ui.py
```

### 10.2 重置配置

如配置出现问题，可删除 `configs/projects/` 目录下对应的配置文件，重新创建项目。

### 10.3 清理缓存

如遇到缓存问题，可删除以下目录：
- `20_Code/` - 生成的代码缓存
- `21_Cache/` - MATLAB 缓存

---

## 11. 技术支持

如有问题或建议，请通过以下方式联系：

- **项目仓库**：[待填写]
- **问题反馈**：[待填写]
- **文档更新**：2026-02-27

---

## 附录：文件排除规则

### 必须排除的文件

- `Rte_TmsApp.h` - 接口文件，不应被复制

### Cal.c 文件处理规则

**前缀**（添加在原有头文件引用下方）：
```c
#define ASW_ATECH_START_SEC_CALIB
#include "Xcp_MemMap.h"
```

**后缀**（添加在文件末尾）：
```c
#define ASW_ATECH_STOP_SEC_CALIB
#include "Xcp_MemMap.h"
#ifdef __cplusplus
}
#endif
```

---

*本文档最后更新：2026-02-27*
