# MinerU官方API使用指南

本指南介绍如何使用MinerU官方API进行PDF解析。

## 目录

1. [功能介绍](#功能介绍)
2. [准备工作](#准备工作)
3. [配置方法](#配置方法)
4. [使用步骤](#使用步骤)
5. [常见问题](#常见问题)
6. [API限制](#api限制)

## 功能介绍

MinerU官方API是一个云端PDF解析服务，具有以下特点：

- ✅ **无需本地GPU**: 在云端进行解析，无需本地GPU资源
- ✅ **快速解析**: 云端高性能服务器，解析速度快
- ✅ **免费额度**: 每天享有2000页免费解析额度
- ✅ **支持多种格式**: 支持PDF、Word、PowerPoint、图片等格式
- ⚠️ **需要网络**: 需要稳定的网络连接
- ⚠️ **文件URL**: 需要提供可访问的文件URL

## 准备工作

### 1. 申请API Token

1. 访问 [MinerU官网](https://mineru.net)
2. 注册/登录账号
3. 进入API管理页面
4. 申请API Token

### 2. 准备文件服务器

由于官方API需要通过URL访问文件，您需要：

**选项A: 使用本项目提供的简单文件服务器**

```bash
# 启动文件服务器
uv run python start_file_server.py

# 或指定端口和目录
uv run python start_file_server.py --port 8080 --directory data/src
```

**选项B: 使用Python内置HTTP服务器**

```bash
cd data/src
python -m http.server 8080
```

**选项C: 使用云存储服务**

将PDF文件上传到云存储（如阿里云OSS、腾讯云COS等），获取公开访问URL。

**选项D: 使用临时文件分享**

使用文件分享服务（如transfer.sh、wetransfer等）获取临时URL。

### 3. 确保文件可访问

测试文件URL是否可访问：

```bash
# 在浏览器中访问
http://localhost:8080/your_file.pdf

# 或使用curl测试
curl -I http://localhost:8080/your_file.pdf
```

## 配置方法

### 在 .env 文件中配置（推荐且必需）

在项目根目录的 `.env` 文件中添加：

```bash
# MinerU官方API Token（必需）
MINERU_API_TOKEN=your_api_token_here

# 文件服务器URL（必需）
FILE_SERVER_URL=http://localhost:8080
```

⚠️ **重要说明**:
- 配置完成后需要**重启Gradio应用**才能生效
- Token和文件服务器URL会自动从环境变量读取
- **无需在界面中手动输入**，简化了使用流程

## 使用步骤

### 通过Gradio界面使用

1. **启动文件服务器**（如果使用本地文件）

```bash
uv run python start_file_server.py
```

2. **启动Gradio应用**

```bash
uv run python app.py
```

3. **在界面中操作**

   a. 上传PDF文件
   
   b. 配置参数：
      - 控制器名称: 输入控制器名称
      - 地址偏移量: 设置偏移量（0-9）
   
   c. 选择解析方式：
      - 选择 "MinerU官方API（云端解析，配置在.env）"
   
   d. 点击"🚀 开始提取"
   
   ✅ **自动配置**: Token和文件服务器URL会自动从 `.env` 文件读取，无需手动输入！

4. **等待解析完成**

   - 系统会自动从 `.env` 读取Token和文件服务器URL
   - 创建解析任务
   - 轮询任务状态
   - 下载并解压结果
   - 提取点位信息
   - 生成CSV文件

5. **下载结果**

   点击"📥 下载CSV文件"保存结果

### 通过命令行测试

```bash
# 运行测试脚本
uv run python test_official_api.py

# 按提示选择测试模式
```

## 常见问题

### Q1: 提示"API返回401错误"

**原因**: API Token无效或已过期

**解决方法**:
1. 检查Token是否正确复制
2. 确认Token是否已过期
3. 重新申请Token

### Q2: 提示"无法访问文件URL"

**原因**: 文件服务器未启动或URL配置错误

**解决方法**:
1. 确认文件服务器正在运行
2. 在浏览器中测试URL是否可访问
3. 检查防火墙设置
4. 如果使用localhost，确保MinerU API能访问（可能需要使用公网IP）

### Q3: 解析超时

**原因**: 文件过大或网络不稳定

**解决方法**:
1. 检查网络连接
2. 尝试分割PDF文件
3. 压缩PDF文件大小
4. 增加等待时间

### Q4: 文件服务器外网无法访问

**原因**: 使用了localhost或内网IP

**解决方法**:
1. 修改 `.env` 文件中的 `FILE_SERVER_URL`
2. 使用公网IP或域名
3. 配置端口转发
4. 使用云存储服务
5. 使用内网穿透工具（如ngrok）

示例（使用ngrok）:
```bash
# 启动文件服务器
uv run python start_file_server.py --port 8080

# 在另一个终端启动ngrok
ngrok http 8080

# 将ngrok提供的URL配置到 .env 文件
FILE_SERVER_URL=https://xxxx-xx-xx-xx-xx.ngrok.io

# 重启Gradio应用
uv run python app.py
```

### Q5: 提示"ZIP文件中未找到Markdown文件"

**原因**: 解析结果格式异常

**解决方法**:
1. 检查PDF文件是否损坏
2. 尝试使用其他解析方式
3. 查看日志文件获取详细错误信息

## API限制

### 文件限制

- 单个文件大小: ≤ 200MB
- 页数: ≤ 600页
- 支持格式: PDF, DOC, DOCX, PPT, PPTX, PNG, JPG, JPEG

### 调用限制

- 每天免费额度: 2000页
- 提交任务: 300次/分钟
- 查询结果: 1000次/分钟

### 文件保存期限

- 解析结果保存30天
- 建议及时下载保存

## 技术细节

### 工作流程

1. **上传PDF**: 用户上传PDF文件到本地
2. **启动服务器**: 通过HTTP服务器提供文件访问
3. **创建任务**: 向MinerU API发送解析请求（包含文件URL）
4. **轮询状态**: 定期查询任务状态（pending → running → done/failed）
5. **下载结果**: 任务完成后下载ZIP文件
6. **解压提取**: 从ZIP中提取Markdown文件
7. **AI处理**: 使用AI提取点位信息
8. **导出CSV**: 生成最终的CSV文件

### API端点

- 创建任务: `POST https://mineru.net/api/v4/extract/task`
- 查询状态: `GET https://mineru.net/api/v4/extract/task/{task_id}`

### 请求示例

**创建任务**:
```json
{
  "url": "http://your-server.com/file.pdf",
  "model_version": "vlm"
}
```

**响应示例**:
```json
{
  "data": {
    "task_id": "xxx-xxx-xxx"
  }
}
```

**查询状态**:
```json
{
  "data": {
    "state": "done",
    "full_zip_url": "https://download-url.com/result.zip"
  }
}
```

## 相关链接

- [MinerU官网](https://mineru.net)
- [API文档](https://mineru.net/apiManage/docs)
- [使用限制说明](https://mineru.net/doc/docs/limit)
- [GitHub仓库](https://github.com/opendatalab/MinerU)

## 更新日志

- 2025-12-26: 初始版本，支持MinerU官方API解析

