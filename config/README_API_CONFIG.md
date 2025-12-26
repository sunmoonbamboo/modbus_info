# API 配置说明

## MinerU官方API配置

如果您想使用MinerU官方API进行PDF解析，需要进行以下配置：

### 1. 申请API Token

访问 [MinerU官网](https://mineru.net) 申请API Token。

### 2. 配置环境变量（必需）

在项目根目录的 `.env` 文件中添加以下配置：

```bash
# MinerU官方API Token（必需）
MINERU_API_TOKEN=your_mineru_api_token_here

# 文件服务器URL（必需）
# 如果您有自己的文件服务器，配置此项
# 官方API需要通过URL访问PDF文件
FILE_SERVER_URL=http://localhost:8080
```

⚠️ **重要提示**:
- 这两个配置项是**必需**的
- 配置完成后需要**重启Gradio应用**才能生效
- Token和URL会自动从环境变量读取，**无需在界面中手动输入**

### 3. 使用方式

#### 配置好环境变量后

1. 启动文件服务器（如果使用本地文件）：
```bash
uv run python start_file_server.py
```

2. 启动Gradio应用：
```bash
uv run python app.py
```

3. 在界面中：
   - 选择解析方式: "MinerU官方API（云端解析，配置在.env）"
   - 上传PDF文件
   - 点击"开始提取"
   - ✅ 系统会自动读取配置，无需手动输入！

### 4. 文件服务器说明

**重要**: MinerU官方API需要通过URL访问PDF文件，而不是直接上传文件。

有以下几种方式：

#### 方式1: 使用简单的HTTP文件服务器

在项目目录下运行：

```bash
# Python内置HTTP服务器
cd data/src
python -m http.server 8080
```

然后在界面中配置：
- 文件服务器URL: `http://localhost:8080`

#### 方式2: 使用云存储服务

将PDF文件上传到云存储（如阿里云OSS、腾讯云COS等），获取公开访问URL。

#### 方式3: 使用临时文件分享服务

使用文件分享服务（如transfer.sh）获取临时URL。

### 5. API使用限制

- 单个文件大小不超过 200MB
- 页数不超过 600 页
- 每天享有 2000 页的最高优先级解析额度
- 提交任务接口：每分钟 300 次
- 获取结果接口：每分钟 1000 次

### 6. 支持的文件格式

- PDF (.pdf)
- Word (.doc, .docx)
- PowerPoint (.ppt, .pptx)
- 图片 (.png, .jpg, .jpeg)

## 本地Web API配置

如果使用本地Web API模式，需要先启动MinerU服务：

```bash
uv run python -m mineru.server --host 0.0.0.0 --port 8000
```

然后在界面中配置：
- 本地Web API地址: `http://127.0.0.1:8000`

## 本地直接解析

本地直接解析模式无需额外配置，但需要：
- GPU支持
- 已安装MinerU及其依赖

## 故障排查

### 问题1: "API返回401错误"
- 检查API Token是否正确
- 确认Token是否已过期

### 问题2: "无法访问文件URL"
- 确认文件服务器是否正常运行
- 确认URL是否可以从外网访问（如果使用官方API）
- 尝试在浏览器中直接访问URL测试

### 问题3: "解析超时"
- 检查网络连接
- 文件可能过大，尝试分割或压缩
- 增加max_wait_time参数

## 更多信息

- [MinerU官方文档](https://mineru.net/doc/docs)
- [API文档](https://mineru.net/apiManage/docs)

