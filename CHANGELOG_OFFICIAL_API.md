# 更新日志 - MinerU官方API支持

## 版本信息

- **更新日期**: 2025-12-26
- **功能**: 新增MinerU官方API解析模式
- **版本**: v1.1.0

## 📋 更新内容

### 1. 核心功能

#### 新增解析模式
- ✅ 本地Web API（原有功能）
- ✅ 本地直接解析（原有功能）
- 🆕 **MinerU官方API**（新增）

### 2. 文件修改

#### 2.1 `src/pdf_parser.py`

**新增功能**:
- 添加 `parse_mode` 参数支持三种解析模式
- 新增 `_parse_via_official_api()` 方法实现官方API解析
- 新增 `_extract_markdown_from_zip()` 方法处理ZIP结果
- 支持官方API Token和文件服务器URL配置

**主要变更**:
```python
# 新增参数
def __init__(
    self,
    parse_mode: str = "local_api",  # 新增
    official_api_token: Optional[str] = None,  # 新增
    file_server_url: Optional[str] = None  # 新增
)
```

**工作流程**:
1. 构造文件URL
2. 创建解析任务（POST请求）
3. 轮询任务状态（GET请求）
4. 下载ZIP结果
5. 解压提取Markdown
6. 保存到本地

#### 2.2 `src/pipeline.py`

**新增功能**:
- 支持传递解析模式参数
- 支持官方API相关配置

**主要变更**:
```python
def __init__(
    self,
    parse_mode: str = "local_api",  # 新增
    official_api_token: Optional[str] = None,  # 新增
    file_server_url: Optional[str] = None  # 新增
)
```

#### 2.3 `app.py`

**UI改进**:
- 将原有的二选一改为三选一的Radio选项
- 新增API配置折叠面板
- 添加官方API Token输入框（密码类型）
- 添加文件服务器URL输入框
- 更新使用说明文档

**主要变更**:
```python
# 新增UI组件
parse_mode = gr.Radio(
    choices=[
        ("本地Web API", "local_api"),
        ("MinerU官方API", "official_api"),  # 新增
        ("本地直接解析", "local")
    ]
)
official_api_token = gr.Textbox(type="password")  # 新增
file_server_url = gr.Textbox()  # 新增
```

#### 2.4 `src/config.py`

**新增配置**:
```python
# MinerU官方API配置
MINERU_API_TOKEN = os.getenv("MINERU_API_TOKEN", "")
FILE_SERVER_URL = os.getenv("FILE_SERVER_URL", "")
```

### 3. 新增文件

#### 3.1 工具脚本

- **`start_file_server.py`**: HTTP文件服务器
  - 提供PDF文件的HTTP访问
  - 支持CORS跨域
  - 可配置端口和目录

- **`test_official_api.py`**: 测试脚本
  - 测试官方API解析功能
  - 对比测试本地API
  - 支持交互式配置

#### 3.2 文档

- **`docs/OFFICIAL_API_GUIDE.md`**: 完整使用指南
  - 功能介绍
  - 准备工作
  - 配置方法
  - 使用步骤
  - 常见问题
  - API限制

- **`config/README_API_CONFIG.md`**: API配置说明
  - 环境变量配置
  - Token申请方法
  - 文件服务器配置
  - 故障排查

- **`quick_start.md`**: 快速启动指南
  - 快速开始步骤
  - 三种模式对比
  - 常用命令
  - 常见问题

## 🎯 使用方式

### 方式1: 通过Gradio界面（推荐）

```bash
# 终端1: 启动文件服务器
uv run python start_file_server.py

# 终端2: 启动Gradio应用
uv run python app.py
```

在界面中：
1. 选择"MinerU官方API"
2. 输入API Token
3. 输入文件服务器URL（如 http://localhost:8080）
4. 上传PDF并开始提取

### 方式2: 通过代码调用

```python
from pathlib import Path
from src.pdf_parser import PDFParser

# 创建解析器
parser = PDFParser(
    parse_mode="official_api",
    official_api_token="your_token_here",
    file_server_url="http://localhost:8080"
)

# 解析PDF
markdown = parser.parse(Path("data/src/your_file.pdf"))
```

## 📊 功能对比

| 特性 | 本地Web API | 官方API | 本地直接解析 |
|------|-------------|---------|--------------|
| 需要GPU | ✅ 是 | ❌ 否 | ✅ 是 |
| 需要网络 | ❌ 否 | ✅ 是 | ❌ 否 |
| 解析速度 | ⚡ 快 | ⚡ 快 | 🐌 慢 |
| 需要服务 | ✅ 是 | ❌ 否 | ❌ 否 |
| 文件限制 | ❌ 无 | ✅ 200MB | ❌ 无 |
| 使用限制 | ❌ 无 | ✅ 2000页/天 | ❌ 无 |
| 适用场景 | 本地GPU | 无GPU/快速 | 简单场景 |

## 🔧 配置要求

### 官方API模式

**必需**:
- MinerU API Token
- 稳定的网络连接
- 可访问的文件URL

**可选**:
- 文件服务器（或使用云存储）
- 环境变量配置

### 文件服务器选项

1. **本项目提供的服务器**（推荐）
   ```bash
   uv run python start_file_server.py
   ```

2. **Python内置服务器**
   ```bash
   python -m http.server 8080
   ```

3. **云存储服务**
   - 阿里云OSS
   - 腾讯云COS
   - AWS S3等

4. **内网穿透**
   ```bash
   ngrok http 8080
   ```

## ⚠️ 注意事项

### 1. 文件访问
- 官方API需要通过URL访问文件
- 确保文件URL可从外网访问
- 本地文件需要通过HTTP服务器提供

### 2. API限制
- 单文件≤200MB
- 页数≤600页
- 每天2000页免费额度
- 文件保存30天

### 3. 安全性
- API Token是敏感信息，不要泄露
- 建议使用环境变量存储
- 文件服务器注意访问控制

### 4. 网络要求
- 需要稳定的网络连接
- 上传和下载可能需要时间
- 建议使用有线网络

## 🐛 故障排查

### 问题1: "API返回401错误"
- 检查Token是否正确
- 确认Token是否过期

### 问题2: "无法访问文件URL"
- 确认文件服务器运行中
- 测试URL是否可访问
- 检查防火墙设置

### 问题3: "解析超时"
- 检查网络连接
- 文件可能过大
- 尝试分割文件

### 问题4: "ZIP文件解析失败"
- 检查PDF文件是否损坏
- 查看详细日志
- 尝试其他解析方式

## 📝 后续计划

- [ ] 支持批量文件上传到云存储
- [ ] 添加解析进度实时显示
- [ ] 支持更多文件格式
- [ ] 优化错误处理和重试机制
- [ ] 添加解析结果缓存

## 🔗 相关链接

- [MinerU官网](https://mineru.net)
- [API文档](https://mineru.net/apiManage/docs)
- [GitHub仓库](https://github.com/opendatalab/MinerU)

## 📞 支持

如有问题，请：
1. 查看文档: `docs/OFFICIAL_API_GUIDE.md`
2. 运行测试: `uv run python test_official_api.py`
3. 查看日志: `logs/`目录

## 🎉 总结

本次更新新增了MinerU官方API支持，为没有GPU的用户提供了云端解析方案。通过简单的配置，即可享受快速、便捷的PDF解析服务。

**主要优势**:
- 无需本地GPU
- 解析速度快
- 配置简单
- 免费额度充足

**适用场景**:
- 没有GPU的开发环境
- 需要快速解析的场景
- 临时使用的情况
- 移动办公环境

