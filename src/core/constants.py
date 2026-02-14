"""Core constants for MBD_CICDKits.

This module defines core constants used across the application.
"""

# 默认超时值（秒）
DEFAULT_TIMEOUT = 300

# 各阶段专用超时值（秒）- Story 2.5, Story 2.8
STAGE_TIMEOUTS = {
    "matlab_gen": 1800,  # MATLAB 代码生成: 30 分钟
    "file_process": 60,  # 代码文件处理: 1 分钟
    "iar_compile": 1200,  # IAR 工程编译: 20 分钟 (Story 2.8 - 更新为1200秒)
    "a2l_process": 120,  # A2L 文件处理: 2 分钟
    "package": 30,       # 最终文件打包: 30 秒
}

# 获取阶段超时值的辅助函数
def get_stage_timeout(stage_name: str) -> int:
    """获取指定阶段的超时值

    Args:
        stage_name: 阶段名称

    Returns:
        超时时间（秒），如果阶段未定义则返回 DEFAULT_TIMEOUT
    """
    return STAGE_TIMEOUTS.get(stage_name, DEFAULT_TIMEOUT)

# 工作流阶段执行顺序 (Story 2.4)
# 必须与 workflow.py 中的 STAGE_ORDER 保持一致
WORKFLOW_STAGE_ORDER = [
    "matlab_gen",
    "file_process",
    "iar_compile",
    "a2l_process",
    "package"
]

# 阶段显示名称映射
STAGE_DISPLAY_NAMES = {
    "matlab_gen": "MATLAB 代码生成",
    "file_process": "代码文件处理",
    "iar_compile": "IAR 工程编译",
    "a2l_process": "A2L 文件处理",
    "package": "最终文件打包"
}

# =============================================================================
# Story 2.13: MATLAB 进程配置常量
# =============================================================================

# MATLAB 进程配置 (Story 2.13 - 任务 5.1-5.5)
MATLAB_START_TIMEOUT = 60          # MATLAB 启动超时（秒）
MATLAB_CONNECT_TIMEOUT = 10        # 连接超时（秒）
MATLAB_MEMORY_LIMIT = "2GB"       # 内存限制
MATLAB_MIN_VERSION = "R2020a"      # 最低支持版本

# 默认启动选项
MATLAB_DEFAULT_OPTIONS = [
    "-nojvm",        # 禁用 JVM（可选，减少内存占用）
    "-nodesktop",    # 无桌面模式
    "-nosplash",     # 无启动画面
]

# MATLAB 进程名称
MATLAB_PROCESS_NAMES = ["MATLAB.exe", "matlab.exe"]
