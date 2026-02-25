# MATLAB Engine for Python 安装指南

## 问题说明

运行 MBD_CICDKits 时出现以下错误：

```
No module named 'matlabengineforpython_abi3'
```

这表示目标电脑未安装 MATLAB Engine for Python。

---

## 安装步骤

### 前提条件

1. 已安装 MATLAB R2020a 或更高版本
2. 已安装 Python 3.8-3.11（需与 MATLAB 版本兼容）

### 方法一：使用 MATLAB 安装程序（推荐）

1. 打开 MATLAB
2. 在 MATLAB 命令窗口执行：
   ```matlab
   cd(fullfile(matlabroot, 'extern', 'engines', 'python'))
   system('python setup.py install')
   ```

### 方法二：手动安装

1. 打开命令提示符（管理员权限）

2. 进入 MATLAB 的 Python Engine 目录：
   ```cmd
   cd "D:\MATLAB\matlab2025a\extern\engines\python"
   ```
   （路径根据实际 MATLAB 安装位置调整）

3. 执行安装：
   ```cmd
   python setup.py install
   ```

4. 验证安装：
   ```cmd
   python -c "import matlab.engine; print('MATLAB Engine 安装成功')"
   ```

### 方法三：使用 pip（MATLAB R2022b+）

```cmd
pip install matlabengine
```

---

## 常见问题

### Q: 安装后仍然报错？

**A:** 检查 Python 版本与 MATLAB 版本兼容性：

| MATLAB 版本 | 支持 Python 版本 |
|-------------|-----------------|
| R2020a-R2021b | 3.7-3.9 |
| R2022a-R2023b | 3.8-3.11 |
| R2024a+ | 3.9-3.12 |

### Q: 提示权限不足？

**A:** 使用管理员权限运行命令提示符

### Q: 提示找不到 setup.py？

**A:** 确认 MATLAB 安装路径正确，检查 `extern/engines/python` 目录是否存在

---

## 重要说明

**MATLAB Engine for Python 无法打包进 EXE**

- MATLAB Engine 是一个需要与本地 MATLAB 安装绑定的库
- 它依赖于 MATLAB 的动态链接库
- 每台运行 MBD_CICDKits 的电脑都必须：
  1. 安装 MATLAB
  2. 安装 MATLAB Engine for Python

---

## 验证清单

在运行 MBD_CICDKits 前，请确认：

- [ ] MATLAB 已正确安装并可以正常启动
- [ ] Python 版本与 MATLAB 兼容
- [ ] MATLAB Engine for Python 已安装
- [ ] `import matlab.engine` 不报错
