# MBD_CICDKits 自动化工具需求规格说明书

## 1. 项目概述

设计一套用于Simulink模型开发的代码集成部署自动化工具（MBD_CICDKits），实现从模型生成代码到最终软件烧录文件和标定文件生成的全流程自动化。
全部功能使用python程序直接或者调用已有工具链（m脚本、bat程序）完成，并实现UI界面进行交互。

## 2. 详细流程需求


### 2.1 项目配置阶段
- 用户在界面设置Simulink工程目录和MAtlab代码报错路径、A2L保存路径、目标文件路径：

### 2.2 MATLAB代码集成阶段
  -（预留，先不做）加载simlink工程，使用python调用matlab进行代码生成，
  -生成代码配置在工程目录的.\20_Code，缓存文件生成在.\21_Cache
 - 代码提取策略：提取20-Codej目录下所有.c和.h文件
  - 文件排除规则：必须排除接口文件Rte_TmsApp.h
- 对标定量的Cal.c文件进行处理，添加特定内存区域定义的前后缀代码：
  - 前缀内容（放置在原有头文件引用下方）：
    ```c
    #define ASW_ATECH_START_SEC_CALIB
    #include "Xcp_MemMap.h"
    ```
  - 后缀内容（放置在文件末尾）：
    ```c
    #define ASW_ATECH_STOP_SEC_CALIB
    #include "Xcp_MemMap.h"
    #ifdef __cplusplus

    }
    #endif
    ```
- .c.h代码移动到“Matlab代码存放”E:\liuyan\600-CICD\01_genA(可配置)，每次移动前清空文件夹
 - A2L文件修改：当前工程生成的空A2L文件，并进行文件处理，处理文件命名：格式为'tmsAPP[_年_月_日_时_分].a2l'，移动到A2L文件存放：E:\liuyan\600-CICD\04_genA2L(可配置)

### 2.3 IAR工程编译阶段

- IAR工程路径配置：支持配置更新工程路径，默认为E:\liuyan\600-CICD\02_genHex\Neusar_CYT4BF.eww
- 模型文件替换：自动替换Matlab代码存放文件夹下代码到工程中的模型文件E:\liuyan\600-CICD\02_genHex\M7\src\TmsApp_APP，移动前清空目标文件夹，移动后原Matlab代码存放文件夹也清空
- 编译集成控制：实现对IAR编译过程的自动化控制
- 输出产物：
  - ELF文件：生成路径为E:\liuyan\600-CICD\02_genHex\M7\Debug\Exe\CYT4BF_M7_Master.elf，移动到A2L文件存放：E:\liuyan\600-CICD\04_genA2L(可配置)，用于后续A2L文件地址更新
 执行脚本E:\liuyan\600-CICD\02_genHex\HexMerge_REEV\HexMerge.bat生成HEX文件
-生成在E:\liuyan\600-CICD\02_genHex\HexMerge_REEV（项目路径下\HexMerge_REEV），移动到E:\liuyan\600-CICD\05_finObj（目标文件文件夹）

### 2.4 A2L文件处理阶段

- 地址更新：通过执行以下MATLAB命令实现A2L文件变量地址更新：
  ```matlab
  rtw.asap2SetAddress( 'tmsAPP[_年_月_日_时_分].a2l' , 'CYT4BF_M7_Master.elf' )
  ```
- 文件生成路径：更新后的A2L文件生成至E:\\liuyan\\600-CICD\\04_genHex目录
- 头文件替换：将该目录下"奇瑞热管理XCP头文件.txt"的完整内容替换到A2L文件前部，直至"    /begin MOD_COMMON  \"Mod Common Comment Here\""行
- 最终命名：处理完成的文件命名为'tmsAPP_upAdress[_年_月_日_时_分].a2l'

### 2.5 最终文件归纳阶段

- 目标文件夹创建：在E:\\liuyan\\600-CICD\\05_finObj目录下创建新文件夹，命名格式为"MBD_CICD_Obj_[_年_月_日_时_分]"
- 文件归集：将以下最终目标文件移动至上述新建文件夹：
  - HEX文件：VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB_【时间：_20251210_V99_11_43】.hex
  - A2L文件：tmsAPP_upAdress[_年_月_日_时_分].a2l

## 3. 系统功能要求

### 3.1 模块化设计

- 每个分步骤需实现为独立的程序模块
- 设计总程序集成调度模块，实现各步骤的有序执行

### 3.2 运行模式

- 支持完整流程自动运行
- 支持选择独立运行某个特定功能模块

### 3.3 部署要求

- 第一阶段：实现本地环境部署
- 架构设计：预留后续服务器部署所需的扩展空间和接口

## 4. 交付物

- MBD_CICDKits自动化工具软件包
- 工具使用说明书
- 各模块详细设计文档
- 测试报告及验证结果
