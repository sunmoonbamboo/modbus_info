# Web API 调试指南

## 问题排查步骤

### 1. 检查 Web API 服务是否正常运行

首先确保 MinerU 的 Web API 服务已启动：

```bash
# 使用批处理脚本启动（推荐）
启动PDF解析服务.bat

# 或者手动启动
uv run python -m mineru.server --host 0.0.0.0 --port 8000
```

服务启动后，你应该能看到类似这样的输出：
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. 测试 API 是否可访问

在浏览器中访问：
- API 文档: http://127.0.0.1:8000/docs
- 健康检查: http://127.0.0.1:8000/health (如果有的话)

### 3. 查看详细日志

现在系统会输出非常详细的调试信息，包括：

#### Web API 请求日志
```
INFO     | src.pdf_parser:_parse_via_web_api:99 - 使用Web API方式解析PDF: http://127.0.0.1:8000
INFO     | src.pdf_parser:_parse_via_web_api:133 - 发送请求到: http://127.0.0.1:8000/file_parse
INFO     | src.pdf_parser:_parse_via_web_api:134 - 请求参数: {...}
```

#### HTTP 响应日志
```
INFO     | src.pdf_parser:_parse_via_web_api:XXX - Web API HTTP状态码: 200
INFO     | src.pdf_parser:_parse_via_web_api:XXX - Web API响应头: {...}
INFO     | src.pdf_parser:_parse_via_web_api:XXX - Web API原始响应长度: XXX 字符
INFO     | src.pdf_parser:_parse_via_web_api:XXX - Web API原始响应前500字符: ...
```

#### JSON 结构日志
```
INFO     | src.pdf_parser:_parse_via_web_api:XXX - Web API响应JSON解析成功
INFO     | src.pdf_parser:_parse_via_web_api:XXX - 响应类型: <class 'dict'>
INFO     | src.pdf_parser:_parse_via_web_api:XXX - 响应字典的keys: ['key1', 'key2', ...]
INFO     | src.pdf_parser:_parse_via_web_api:XXX -   - markdown: str (长度: XXXX)
```

#### Markdown 提取日志
```
INFO     | src.pdf_parser:_parse_via_web_api:XXX - 尝试从字典中提取markdown内容...
INFO     | src.pdf_parser:_parse_via_web_api:XXX - 找到 'markdown' 字段，长度: XXXX
INFO     | src.pdf_parser:_parse_via_web_api:XXX - ✅ 成功提取markdown内容，长度: XXXX 字符
```

### 4. 常见错误及解决方法

#### 错误: "Web API请求失败: Connection refused"
**原因**: Web API 服务未启动
**解决**: 运行 `启动PDF解析服务.bat`

#### 错误: "Web API请求失败: Timeout"
**原因**: PDF 文件太大或服务器负载过高
**解决**: 
- 增加超时时间（当前为300秒）
- 使用更小的PDF文件测试
- 检查服务器资源使用情况

#### 错误: "API返回的markdown内容为空或无法提取"
**原因**: API 响应格式与预期不符
**解决**: 
1. 查看日志中的 "Web API原始响应前500字符"
2. 查看 "响应字典的keys" 确认返回的字段名
3. 如果字段名不同，需要修改 `src/pdf_parser.py` 中的提取逻辑

### 5. 手动测试 API

你可以使用 `curl` 或 `Postman` 手动测试 API：

```bash
# 使用 curl 测试
curl -X POST "http://127.0.0.1:8000/file_parse" \
  -F "files=@data/src/test.pdf" \
  -F "return_md=true" \
  -F "backend=pipeline"
```

或者使用 Python 测试：

```python
import requests

url = "http://127.0.0.1:8000/file_parse"
files = {'files': open('data/src/test.pdf', 'rb')}
data = {
    'return_md': True,
    'backend': 'pipeline'
}

response = requests.post(url, files=files, data=data)
print(f"状态码: {response.status_code}")
print(f"响应keys: {response.json().keys()}")
```

### 6. 使用测试脚本

运行测试脚本进行诊断：

```bash
uv run python test_web_api.py
```

这个脚本会：
1. 测试 Web API 方式解析
2. 测试本地方式解析
3. 输出详细的错误信息

## 日志文件位置

- Gradio UI 日志: `logs/gradio_app_*.log`
- 测试日志: `logs/test_*.log`
- Pipeline 日志: `logs/*.log`

## API 响应格式说明

根据实际测试，MinerU Web API 的响应格式是：

### 实际格式（MinerU v2.6.8）
```json
{
  "backend": "pipeline",
  "version": "2.6.8",
  "results": {
    "文件名（不含扩展名）": {
      "md_content": "这里是markdown内容..."
    }
  }
}
```

**关键点**：
- `results` 是一个**字典**（不是列表）
- 字典的 key 是文件名（不含 `.pdf` 扩展名）
- 字典的 value 包含 `md_content` 字段（不是 `markdown`）

### 兼容的其他格式

代码也支持以下格式以保证兼容性：

#### 格式 1: 直接返回字段
```json
{
  "markdown": "...",
  "status": "success"
}
```

#### 格式 2: results 是列表
```json
{
  "results": [
    {
      "markdown": "...",
      "filename": "test.pdf"
    }
  ]
}
```

#### 格式 3: 使用不同的字段名
```json
{
  "md_content": "...",
  "pages": 10
}
```

当前代码已经支持所有这些格式。

## 需要帮助？

如果以上步骤都无法解决问题，请：
1. 收集完整的日志输出
2. 记录 API 的原始响应内容
3. 检查 MinerU 版本是否最新
4. 查看 MinerU 的官方文档: https://github.com/opendatalab/MinerU

