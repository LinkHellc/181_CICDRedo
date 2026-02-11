"""Core constants for MBD_CICDKits.

This module defines core constants used across the application.
"""

# 默认超时值（秒）
DEFAULT_TIMEOUT = 300

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
