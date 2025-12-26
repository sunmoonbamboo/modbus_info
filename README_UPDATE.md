# 🎉 新功能：MinerU官方API支持

## ✨ 更新概述

本次更新为 Modbus 协议信息提取工具新增了 **MinerU官方API解析模式**，让您无需本地GPU即可享受快速的PDF解析服务！

## 🚀 三种解析模式

现在支持三种PDF解析方式，您可以根据实际情况选择：

| 模式 | 说明 | 优点 | 适用场景 |
|------|------|------|----------|
| 🖥️ **本地Web API** | 本地启动MinerU服务 | 速度快、无限制 | 有GPU的本地环境 |
| ☁️ **MinerU官方API** | 使用官方云端服务 | 无需GPU、快速 | 无GPU或临时使用 |
| 💻 **本地直接解析** | 直接本地解析 | 无需额外服务 | 简单场景 |

## 🆕 新增文件

### 工具脚本
- `start_file_server.py` - HTTP文件服务器（为官方API提供文件访问）
- `test_official_api.py` - 官方API测试脚本

### 文档
- `docs/OFFICIAL_API_GUIDE.md` - 完整使用指南
- `config/README_API_CONFIG.md` - API配置说明
- `quick_start.md` - 快速启动指南
- `CHANGELOG_OFFICIAL_API.md` - 详细更新日志

## 📝 快速开始

### 1. 申请API Token
访问 https://mineru.net 申请免费的API Token

### 2. 配置环境变量
在项目根目录的 `.env` 文件中添加：

```bash
# MinerU官方API配置
MINERU_API_TOKEN=your_token_here
FILE_SERVER_URL=http://localhost:8080
```

### 3. 启动文件服务器
```bash
uv run python start_file_server.py
```

### 4. 启动应用
```bash
uv run python app.py
```

### 5. 在界面中使用
1. 上传PDF文件
2. 选择"MinerU官方API（云端解析，配置在.env）"模式
3. 点击"开始提取"

✅ **自动读取配置** - 无需手动输入Token和URL，系统会自动从 `.env` 文件读取！

## 🔧 主要修改

### 代码修改
- ✅ `src/pdf_parser.py` - 新增官方API解析方法
- ✅ `src/pipeline.py` - 支持新的解析模式
- ✅ `app.py` - 更新UI，添加官方API选项
- ✅ `src/config.py` - 新增API配置项

### 新增功能
- ✅ 官方API Token配置
- ✅ 文件服务器URL配置
- ✅ 任务创建和状态轮询
- ✅ ZIP结果下载和解压
- ✅ 完整的错误处理

## 💡 使用场景

### 场景1: 本地有GPU
**推荐**: 本地Web API
```bash
# 启动本地服务
uv run python -m mineru.server --host 0.0.0.0 --port 8000

# 在界面选择"本地Web API"
```

### 场景2: 没有GPU
**推荐**: MinerU官方API ⭐
```bash
# 启动文件服务器
uv run python start_file_server.py

# 在界面选择"MinerU官方API"
# 输入Token和文件服务器URL
```

### 场景3: 简单测试
**推荐**: 本地直接解析
```bash
# 直接在界面选择"本地直接解析"
# 无需额外配置
```

## 📊 API限制

- 📄 单文件大小: ≤ 200MB
- 📑 页数限制: ≤ 600页
- 🎁 每日免费额度: 2000页
- ⏰ 文件保存期: 30天

## ❓ 常见问题

### Q: 如何让外网访问文件服务器？

**方案1**: 使用ngrok
```bash
ngrok http 8080
# 使用ngrok提供的URL
```

**方案2**: 使用云存储
- 上传到阿里云OSS/腾讯云COS
- 获取公开访问URL

### Q: API Token在哪里配置？

**方式1**: 环境变量（推荐）
```bash
# .env文件
MINERU_API_TOKEN=your_token_here
```

**方式2**: 界面输入
- 直接在Gradio界面的输入框中输入

### Q: 文件服务器必须吗？

- 使用官方API时**必须**
- 官方API需要通过URL访问文件
- 可以使用本项目提供的服务器或云存储

## 📚 详细文档

- 📖 [完整使用指南](docs/OFFICIAL_API_GUIDE.md)
- ⚙️ [API配置说明](config/README_API_CONFIG.md)
- 🚀 [快速启动](quick_start.md)
- 📝 [更新日志](CHANGELOG_OFFICIAL_API.md)

## 🎯 测试

运行测试脚本验证功能：

```bash
uv run python test_official_api.py
```

## 🔗 相关链接

- [MinerU官网](https://mineru.net)
- [API文档](https://mineru.net/apiManage/docs)
- [GitHub](https://github.com/opendatalab/MinerU)

## 💬 反馈

如有问题或建议，欢迎反馈！

---

**更新日期**: 2025-12-26  
**版本**: v1.1.0  
**作者**: AI Assistant

