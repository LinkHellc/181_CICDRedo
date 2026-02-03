# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

MBD_CICDKits 是一个用于Simulink模型开发的CI/CD自动化工具，实现从模型生成代码到最终软件烧录文件和标定文件生成的全流程自动化。

## 核心流程

该项目的主要流程分为5个阶段：

### 1. 项目配置阶段
- 配置Simulink工程目录
- 配置MATLAB代码存放路径
- 配置A2L保存路径和目标文件路径

### 2. MATLAB代码集成阶段
- 调用MATLAB生成Simulink模型代码（使用 `genCode.m`）
- 代码生成到 `./20_Code` 目录
- 缓存文件生成到 `./21_Cache` 目录
- 提取所有 `.c` 和 `.h` 文件（排除 `Rte_TmsApp.h`）
- 对标定量的 `Cal.c` 文件添加特定内存区域定义前后缀代码
- 移动代码到MATLAB代码存放目录（每次移动前清空）
- 处理A2L文件并移动到A2L文件存放目录

### 3. IAR工程编译阶段
- 配置IAR工程路径（默认：`E:\liuyan\600-CICD\02_genHex\Neusar_CYT4BF.eww`）
- 自动替换MATLAB代码到IAR工程（`M7\src\TmsApp_APP`）
- 执行IAR编译生成ELF文件（`CYT4BF_M7_Master.elf`）
- 执行 `HexMerge.bat` 生成HEX文件

### 4. A2L文件处理阶段
- 使用MATLAB命令更新A2L文件变量地址：
  ```matlab
  rtw.asap2SetAddress('tmsAPP[_年_月_日_时_分].a2l', 'CYT4BF_M7_Master.elf')
  ```
- 替换XCP头文件内容（使用 `奇瑞热管理XCP头文件.txt`）
- 最终文件命名为 `tmsAPP_upAdress[_年_月_日_时_分].a2l`

### 5. 最终文件归纳阶段
- 创建时间戳文件夹 `MBD_CICD_Obj_[_年_月_日_时_分]`
- 归集HEX文件和A2L文件

## 关键文件说明

### MATLAB工具文件
- `00_用户输入需求与材料/genCode.m` - Simulink模型代码生成工具
  - 使用 `Simulink.fileGenControl` 管理编译文件夹
  - 生成代码到 `20-Code` 目录
  - 自动打包生成的代码为ZIP文件
  - 支持回溯级数配置（默认回溯1级）

- `00_用户输入需求与材料/A2LTool.m` - A2L文件处理工具
  - 用于清理A2L文件中的XCP IF_DATA标记

- `00_用户输入需求与材料/奇瑞热管理XCP头文件.txt` - XCP协议头文件模板
  - 包含完整的XCP 1.2协议定义
  - 用于A2L文件头部替换

### 需求文档
- `00_用户输入需求与材料/MBD_CICDKits需求.md` - 详细的需求规格说明书

## 系统功能要求

1. **模块化设计** - 每个分步骤实现为独立的程序模块
2. **运行模式** - 支持完整流程自动运行和独立运行特定模块
3. **部署要求** - 第一阶段本地环境部署，预留服务器部署扩展空间

## 技术栈

- **Python** - 主要开发语言（负责流程控制和工具调用）
- **MATLAB** - 代码生成和A2L处理
- **IAR** - 嵌入式代码编译
- **Simulink** - 模型开发环境

## 文件命名规范

- 时间戳格式：`_年_月_日_时_分`（例如：`_2025_02_02_15_43`）
- A2L文件：`tmsAPP[_时间戳].a2l` → `tmsAPP_upAdress[_时间戳].a2l`
- HEX文件：`VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB_[时间戳：_20251210_V99_11_43].hex`
- 目标文件夹：`MBD_CICD_Obj_[_时间戳]`

## 代码处理规则

### 必须排除的文件
- `Rte_TmsApp.h`（接口文件）

### Cal.c文件处理
在头文件引用下方添加前缀：
```c
#define ASW_ATECH_START_SEC_CALIB
#include "Xcp_MemMap.h"
```

在文件末尾添加后缀：
```c
#define ASW_ATECH_STOP_SEC_CALIB
#include "Xcp_MemMap.h"
#ifdef __cplusplus
}
#endif
```

## 开发状态

**当前阶段**：需求定义阶段，尚未开始代码实现

**待实现**：
- Python主程序框架
- UI界面
- 各功能模块实现
- 配置管理系统
