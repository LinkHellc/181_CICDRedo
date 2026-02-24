"""
IAR集成模块
提供IAR Embedded Workbench编译功能
"""

import os
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path

from logging_config import get_logger

logger = get_logger()


class IARIntegration:
    """IAR集成类"""
    
    def __init__(self, iar_path: str):
        """初始化IAR集成"""
        self.iar_path = iar_path
        self.iar_build_exe = self._find_iar_build_executable()
        
    def _find_iar_build_executable(self) -> Optional[str]:
        """查找IAR编译工具"""
        # 尝试查找不同版本的IAR编译工具
        possible_paths = [
            os.path.join(self.iar_path, "IarBuild.exe"),
            os.path.join(self.iar_path, "common", "bin", "IarBuild.exe"),
            os.path.join(self.iar_path, "bin", "IarBuild.exe"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def is_available(self) -> bool:
        """检查IAR是否可用"""
        return self.iar_build_exe is not None and os.path.exists(self.iar_build_exe)
    
    def compile_project(self, project_file: str, configuration: str = "Debug",
                       target: str = "all") -> Dict[str, Any]:
        """编译IAR项目"""
        if not self.is_available():
            return {
                "success": False,
                "error_code": -1,
                "error_message": "IAR不可用",
                "error_category": "configuration_error",
                "project_file": project_file,
                "configuration": configuration
            }
        
        if not os.path.exists(project_file):
            return {
                "success": False,
                "error_code": -2,
                "error_message": f"项目文件不存在: {project_file}",
                "error_category": "file_not_found",
                "project_file": project_file,
                "configuration": configuration
            }
        
        try:
            # 构建IAR编译命令
            # 使用make而不是build，避免删除文件
            # make: 只编译修改过的文件
            # build: 编译所有文件（会删除旧文件）
            # rebuild: 清理并重新编译所有文件
            cmd = [
                self.iar_build_exe,
                project_file,
                configuration,
                "-" + target
            ]
            
            logger.info(f"执行IAR编译命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10分钟超时
                encoding='utf-8',
                errors='replace'
            )
            
            # IAR编译错误代码解释
            error_code_meaning = self._interpret_iar_returncode(result.returncode)
            
            # 分类编译错误
            error_output = result.stdout + result.stderr
            error_classification = self.classify_compilation_error(error_output)
            
            return {
                "success": result.returncode == 0,
                "error_code": result.returncode,
                "error_message": error_code_meaning,
                "error_category": error_classification["primary_error"]["category"] if error_classification["primary_error"] else "unknown_error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "project_file": project_file,
                "configuration": configuration,
                "error_classification": error_classification
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error_code": -3,
                "error_message": "编译超时（10分钟）",
                "error_category": "timeout_error",
                "project_file": project_file,
                "configuration": configuration
            }
        except Exception as e:
            return {
                "success": False,
                "error_code": -4,
                "error_message": f"编译执行异常: {str(e)}",
                "error_category": "execution_error",
                "project_file": project_file,
                "configuration": configuration
            }
    
    def _interpret_iar_returncode(self, returncode: int) -> str:
        """解释IAR编译返回代码"""
        error_codes = {
            0: "编译成功",
            1: "编译警告（有警告但编译成功）",
            2: "编译错误（存在编译错误）",
            3: "致命错误（无法继续编译）",
            4: "用户中止",
            5: "内部错误（IAR工具内部错误）",
            6: "内存不足",
            7: "磁盘空间不足",
            8: "配置错误",
            9: "链接错误",
            10: "文件访问错误"
        }
        
        if returncode in error_codes:
            return error_codes[returncode]
        elif returncode < 0:
            return f"系统错误代码: {returncode}"
        else:
            return f"未知错误代码: {returncode}"
    
    def build_project(self, project_file: str, configuration: str = "Debug") -> Dict[str, Any]:
        """构建IAR项目（编译+链接）"""
        return self.compile_project(project_file, configuration, "build")
    
    def rebuild_project(self, project_file: str, configuration: str = "Debug") -> Dict[str, Any]:
        """重新构建IAR项目"""
        return self.compile_project(project_file, configuration, "rebuild")
    
    def clean_project(self, project_file: str, configuration: str = "Debug") -> Dict[str, Any]:
        """清理IAR项目"""
        return self.compile_project(project_file, configuration, "clean")
    
    def get_project_info(self, project_file: str) -> Dict[str, Any]:
        """获取项目信息"""
        if not os.path.exists(project_file):
            return {"success": False, "error": "项目文件不存在"}
        
        try:
            # 这里可以解析IAR项目文件获取项目信息
            # 实际实现需要解析.ewp文件格式
            
            project_info = {
                "success": True,
                "project_file": project_file,
                "project_name": Path(project_file).stem,
                "configurations": ["Debug", "Release"],  # 示例配置
                "targets": ["all", "build", "rebuild", "clean"],
                "file_count": 0,  # 需要解析项目文件获取
                "last_build": None  # 需要解析项目文件获取
            }
            
            return project_info
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_project_template(self, project_name: str, output_dir: str,
                              template_type: str = "embedded") -> Dict[str, Any]:
        """创建IAR项目模板"""
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 项目文件路径
            project_file = os.path.join(output_dir, f"{project_name}.ewp")
            
            # 创建基本的IAR项目文件内容
            project_content = self._build_project_template(project_name, template_type)
            
            # 写入项目文件
            with open(project_file, 'w', encoding='utf-8') as f:
                f.write(project_content)
            
            # 创建基本的源文件
            self._create_source_files(project_name, output_dir, template_type)
            
            return {
                "success": True,
                "project_file": project_file,
                "output_dir": output_dir,
                "template_type": template_type
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _build_project_template(self, project_name: str, template_type: str) -> str:
        """构建IAR项目模板内容"""
        # 这是一个简化的IAR项目文件模板
        # 实际实现需要根据具体的IAR项目文件格式
        
        template = f"""<?xml version="1.0" encoding="UTF-8"?>
<project>
  <configuration>
    <name>IAR Embedded Workbench Project</name>
    <settings>
      <name>{project_name}</name>
      <archiveVersion>8.10</archiveVersion>
      <options>
        <option>
          <name>CCDebugInfo</name>
          <state>1</state>
        </option>
        <option>
          <name>CCLang</name>
          <state>c</state>
        </option>
      </options>
    </settings>
    <file>
      <name>main.c</name>
      <type>source</type>
    </file>
  </configuration>
</project>
"""
        return template
    
    def _create_source_files(self, project_name: str, output_dir: str, template_type: str):
        """创建源文件"""
        # 创建主源文件
        main_c_content = """#include <stdio.h>

int main(void) {
    printf("Hello from MBD CICD Kits!\\n");
    return 0;
}
"""
        
        main_c_path = os.path.join(output_dir, "main.c")
        with open(main_c_path, 'w', encoding='utf-8') as f:
            f.write(main_c_content)
    
    def get_version(self) -> Optional[str]:
        """获取IAR版本信息"""
        if not self.is_available():
            return None
        
        try:
            cmd = [self.iar_build_exe, "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            
        except Exception:
            pass
        
        return None
    
    def generate_hex_file(self, project_file: str, configuration: str = "Debug") -> Dict[str, Any]:
        """生成HEX烧录文件"""
        if not self.is_available():
            return {"success": False, "error": "IAR不可用"}
        
        if not os.path.exists(project_file):
            return {"success": False, "error": "项目文件不存在"}
        
        try:
            # 首先构建项目
            build_result = self.build_project(project_file, configuration)
            if not build_result["success"]:
                return build_result
            
            # 获取项目目录和名称
            project_dir = os.path.dirname(project_file)
            project_name = Path(project_file).stem
            
            # 预期的HEX文件路径
            exe_dir = os.path.join(project_dir, "Exe")
            hex_file = os.path.join(exe_dir, f"{project_name}.hex")
            
            # 创建Exe目录（如果不存在）
            os.makedirs(exe_dir, exist_ok=True)
            
            # 检查HEX文件是否已生成
            if os.path.exists(hex_file):
                # 验证HEX文件完整性
                validation_result = self._validate_hex_file(hex_file)
                return {
                    "success": True,
                    "hex_file": hex_file,
                    "hex_file_size": os.path.getsize(hex_file),
                    "validation": validation_result,
                    "project_file": project_file,
                    "configuration": configuration
                }
            else:
                return {
                    "success": False,
                    "error": "HEX文件未生成",
                    "project_file": project_file,
                    "configuration": configuration
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_hex_file(self, hex_file: str) -> Dict[str, Any]:
        """验证HEX文件完整性"""
        try:
            with open(hex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查HEX文件基本格式
            lines = content.strip().split('\n')
            
            if len(lines) == 0:
                return {"valid": False, "error": "空文件"}
            
            # 检查起始行
            if not lines[0].startswith(':'):
                return {"valid": False, "error": "无效的HEX格式"}
            
            # 检查结束行
            if not lines[-1].startswith(':00000001FF'):
                return {"valid": False, "error": "缺少文件结束标记"}
            
            # 验证每行的校验和
            for i, line in enumerate(lines):
                if line.startswith(':'):
                    if not self._validate_hex_line(line):
                        return {"valid": False, "error": f"第{i+1}行校验和错误"}
            
            return {
                "valid": True,
                "line_count": len(lines),
                "file_size": len(content),
                "hex_file": hex_file
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _validate_hex_line(self, line: str) -> bool:
        """验证HEX行校验和"""
        try:
            # 移除起始冒号
            data = line[1:]
            
            # 计算校验和
            byte_count = int(data[0:2], 16)
            address = int(data[2:6], 16)
            record_type = int(data[6:8], 16)
            
            # 数据部分
            data_bytes = []
            for i in range(0, byte_count * 2, 2):
                data_bytes.append(int(data[8+i:10+i], 16))
            
            # 读取校验和
            checksum = int(data[8+byte_count*2:10+byte_count*2], 16)
            
            # 计算校验和
            calculated_checksum = byte_count + (address >> 8) + (address & 0xFF) + record_type
            for byte in data_bytes:
                calculated_checksum += byte
            
            calculated_checksum = (~calculated_checksum + 1) & 0xFF
            
            return calculated_checksum == checksum
            
        except Exception:
            return False
    
    def resolve_dependencies(self, project_file: str) -> Dict[str, Any]:
        """解析编译依赖"""
        if not os.path.exists(project_file):
            return {"success": False, "error": "项目文件不存在"}
        
        try:
            dependencies = self._parse_project_dependencies(project_file)
            
            return {
                "success": True,
                "project_file": project_file,
                "dependencies": dependencies,
                "dependency_count": len(dependencies),
                "missing_dependencies": self._check_missing_dependencies(dependencies)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_project_dependencies(self, project_file: str) -> List[Dict[str, Any]]:
        """解析项目依赖"""
        dependencies = []
        project_dir = os.path.dirname(project_file)
        
        # 解析IAR项目文件获取依赖信息
        # 这里简化实现，实际需要解析.ewp文件
        
        # 常见的IAR项目依赖
        common_deps = [
            {
                "type": "source_file",
                "name": "main.c",
                "path": os.path.join(project_dir, "main.c"),
                "required": True
            },
            {
                "type": "header_file",
                "name": "header.h",
                "path": os.path.join(project_dir, "header.h"),
                "required": False
            },
            {
                "type": "library",
                "name": "runtime_library",
                "path": None,
                "required": True
            }
        ]
        
        # 检查文件是否存在
        for dep in common_deps:
            try:
                if dep["path"] and os.path.exists(dep["path"]):
                    dep["exists"] = True
                    dep["size"] = os.path.getsize(dep["path"])
                else:
                    dep["exists"] = False
                    dep["size"] = 0
            except OSError:
                # 如果无法访问文件，标记为不存在
                dep["exists"] = False
                dep["size"] = 0
            
            dependencies.append(dep)
        
        return dependencies
    
    def _check_missing_dependencies(self, dependencies: List[Dict[str, Any]]) -> List[str]:
        """检查缺失的依赖"""
        missing = []
        
        for dep in dependencies:
            if dep["required"] and not dep["exists"]:
                missing.append(dep["name"])
        
        return missing
    
    def classify_compilation_error(self, error_output: str) -> Dict[str, Any]:
        """分类编译错误"""
        error_categories = {
            "syntax_error": {
                "patterns": ["error[Pe", "syntax error", "expected"],
                "severity": "high",
                "description": "语法错误"
            },
            "linker_error": {
                "patterns": ["undefined reference", "unresolved external", "linker"],
                "severity": "high",
                "description": "链接错误"
            },
            "warning": {
                "patterns": ["warning", "Warning", "WARNING"],
                "severity": "low",
                "description": "编译警告"
            },
            "file_not_found": {
                "patterns": ["file not found", "cannot open file", "no such file"],
                "severity": "medium",
                "description": "文件未找到"
            },
            "configuration_error": {
                "patterns": ["configuration", "settings", "option"],
                "severity": "medium",
                "description": "配置错误"
            }
        }
        
        classified_errors = []
        
        # 按行分析错误输出
        lines = error_output.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for category, info in error_categories.items():
                for pattern in info["patterns"]:
                    if pattern.lower() in line.lower():
                        classified_errors.append({
                            "category": category,
                            "severity": info["severity"],
                            "description": info["description"],
                            "line": line,
                            "pattern": pattern
                        })
                        break
        
        # 如果没有匹配到任何分类，归类为未知错误
        if not classified_errors:
            classified_errors.append({
                "category": "unknown_error",
                "severity": "high",
                "description": "未知错误",
                "line": error_output[:100] if error_output else "",
                "pattern": ""
            })
        
        return {
            "error_count": len(classified_errors),
            "classified_errors": classified_errors,
            "primary_error": classified_errors[0] if classified_errors else None,
            "error_output": error_output
        }