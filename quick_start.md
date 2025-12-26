# 快速启动指南 - MinerU官方API模式

## 🚀 快速开始

### 步骤1: 申请API Token

访问 https://mineru.net 申请API Token

### 步骤2: 配置环境变量

编辑项目根目录的 `.env` 文件，添加：

```bash
# MinerU官方API Token
MINERU_API_TOKEN=your_token_here

# 文件服务器URL
FILE_SERVER_URL=http://localhost:8080
```

⚠️ **重要**: 配置完成后需要重启应用才能生效！

### 步骤3: 启动文件服务器

**终端1** - 启动文件服务器（用于提供PDF文件访问）：

```bash
uv run python start_file_server.py
```

### 步骤4: 启动Gradio应用

**终端2** - 启动Web界面：

```bash
uv run python app.py
```

### 步骤5: 使用界面

1. 打开浏览器访问: http://localhost:8860
2. 上传PDF文件
3. 选择解析方式: "MinerU官方API（云端解析，配置在.env）"
4. 点击"开始提取"

✅ **无需手动输入Token和URL** - 系统会自动从 `.env` 文件读取配置！

## 📝 三种解析模式对比

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **本地Web API** | 速度快，无需外网 | 需要GPU，需启动服务 | 有GPU的本地环境 |
| **MinerU官方API** ⭐ | 无需GPU，云端解析 | 需要网络，需要文件URL | 无GPU或快速解析 |
| **本地直接解析** | 无需额外服务 | 速度慢，需要GPU | 简单场景 |

## 🔧 常用命令

### 启动文件服务器（不同端口）
```bash
uv run python start_file_server.py --port 8080
```

### 测试官方API
```bash
uv run python test_official_api.py
```

### 查看日志
```bash
# Gradio应用日志
tail -f logs/gradio_app_*.log

# 测试日志
tail -f logs/test_official_api_*.log
```

## ❓ 常见问题

### 问题1: 文件服务器无法从外网访问

**解决方案A**: 使用ngrok
```bash
# 终端1
uv run python start_file_server.py --port 8080

# 终端2
ngrok http 8080
# 使用ngrok提供的URL作为文件服务器URL
```

**解决方案B**: 使用云存储
- 上传PDF到云存储（阿里云OSS、腾讯云COS等）
- 获取公开访问URL
- 直接在界面中使用该URL

### 问题2: API Token无效

1. 检查Token是否正确复制
2. 确认Token是否已过期
3. 重新申请Token

### 问题3: 解析超时

1. 检查网络连接
2. 文件可能过大，尝试分割
3. 使用本地解析模式

## 📚 更多文档

- [完整使用指南](docs/OFFICIAL_API_GUIDE.md)
- [API配置说明](config/README_API_CONFIG.md)
- [MinerU官方文档](https://mineru.net/doc/docs)

## 💡 提示

- 每天有2000页免费额度
- 文件大小限制200MB
- 页数限制600页
- 解析结果保存30天

