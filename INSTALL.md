# 安装指南

本文档详细说明如何在Windows系统上安装和配置Modbus协议信息提取工具。

## 系统要求

- Windows 10/11
- Python 3.12 或更高版本
- 网络连接（用于下载依赖和调用API）

## 安装步骤

### 1. 安装Python

如果尚未安装Python 3.12+：

1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载并安装Python 3.12或更高版本
3. 安装时勾选"Add Python to PATH"

验证安装：

```powershell
python --version
```

应显示 Python 3.12.x 或更高版本。

### 2. 安装uv包管理器

```powershell
pip install uv
```

验证安装：

```powershell
uv --version
```

### 3. 克隆或下载项目

如果使用Git：

```powershell
git clone <repository-url>
cd modbus_info
```

或直接下载项目压缩包并解压。

### 4. 安装项目依赖

在项目根目录下运行：

```powershell
# 安装项目基础依赖
uv sync

# 如果需要安装开发依赖
uv sync --extra dev

# 单独安装 MinerU（PDF解析引擎）
uv pip install "mineru[core]"
```

这将自动创建虚拟环境并安装所有依赖。

> **📌 关于 MinerU**：
> 
> MinerU 需要单独安装，因为它的依赖比较复杂。使用官方推荐的安装方式：
> ```powershell
> uv pip install "mineru[core]"
> ```

### 5. 配置API密钥

1. 复制配置模板：

```powershell
copy config.example .env
```

2. 获取 OpenRouter API 密钥：
   - 访问 https://openrouter.ai/keys
   - 创建或登录账户
   - 生成新的API密钥

3. 编辑 `.env` 文件，填入你的API密钥：

```
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME="google/gemini-2.5-pro"
OPENAI_API_KEY=你的API密钥
```

### 6. 验证安装

运行测试以验证安装：

```powershell
uv run pytest -m "not integration" -v
```

如果所有测试通过，说明安装成功！

## 常见问题

### 问题1：uv安装失败

**解决方案**：使用pip直接安装依赖

```powershell
pip install -r requirements.txt
```

### 问题2：Python版本不匹配

**解决方案**：

1. 卸载旧版本Python
2. 安装Python 3.12+
3. 重新运行安装步骤

### 问题3：依赖安装失败

**解决方案**：

1. 确保网络连接正常
2. 尝试使用国内镜像：

```powershell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 问题4：magic-pdf安装失败

**解决方案**：

magic-pdf可能需要额外的系统依赖。如果安装失败：

1. 尝试单独安装：

```powershell
pip install magic-pdf[full]
```

2. 查看详细错误信息并根据提示安装缺失的系统库

### 问题5：权限错误

**解决方案**：

以管理员身份运行PowerShell：

1. 右键点击PowerShell
2. 选择"以管理员身份运行"
3. 重新执行安装命令

## 下一步

安装完成后，请参阅 [README.md](README.md) 了解使用方法。

快速开始：

```powershell
# 处理单个PDF文件
uv run python main.py data/src/your_file.pdf

# 查看帮助
uv run python main.py --help
```

## 获取帮助

如遇到问题：

1. 查看 [常见问题](#常见问题) 部分
2. 查看项目Issues
3. 提交新的Issue并附上详细错误信息

## 更新项目

更新到最新版本：

```powershell
git pull
uv sync
```

或重新下载并解压最新版本的压缩包。

