# Modbus协议信息提取工具

从Modbus协议PDF文件中自动提取关键点位信息并导出为CSV格式。

## 功能特性

- 📄 **PDF解析**：支持两种解析方式
  - 🌐 MinerU官方API（云端解析，推荐）
  - 🖥️ 本地Web API（需要本地服务）
- 🤖 **AI提取**：通过OpenRouter使用Gemini 2.5 Pro模型智能提取Modbus点位信息
- 📊 **CSV导出**：标准化的CSV格式输出，方便导入其他系统
- 🔄 **批量处理**：支持批量处理多个PDF文件
- 🔐 **安全鉴权**：基于配置文件的用户认证，支持动态添加用户
- ✅ **完整测试**：包含单元测试和集成测试

## 快速开始

### 1. 环境准备

本项目使用 `uv` 管理Python环境：

```bash
# 安装uv（如果未安装）
pip install uv

# 安装项目依赖
uv sync
```

### 2. 配置PDF解析方式

项目支持两种PDF解析方式：

#### 方式1：MinerU官方API（推荐）

- 无需本地安装GPU或复杂环境
- 每天享有2000页免费额度
- 需要申请API Token：https://mineru.net

配置步骤：
1. 在 `.env` 文件中添加：
```
MINERU_API_TOKEN=your_token_here
FILE_SERVER_URL=http://localhost:8080
```

2. 启动文件服务器（用于让官方API访问本地文件）：
```bash
uv run python start_file_server.py
```

#### 方式2：本地Web API

- 需要本地GPU环境
- 需要单独安装MinerU并启动服务

配置步骤：
1. 安装MinerU：
```bash
uv pip install "mineru[core]"
```

2. 启动本地解析服务：
```bash
uv run python -m mineru.server --host 0.0.0.0 --port 8000
```

### 3. 配置API密钥

复制配置文件模板并填入你的 OpenRouter API 密钥：

```bash
copy config.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME="google/gemini-2.5-pro"
OPENAI_API_KEY=your_api_key_here

# PDF解析方式（可选）
MINERU_API_TOKEN=your_mineru_token_here  # 使用官方API时需要
FILE_SERVER_URL=http://localhost:8080     # 使用官方API时需要
```

> 获取OpenRouter API密钥：https://openrouter.ai/keys
> 获取MinerU API Token：https://mineru.net

### 4. 使用方法

#### 方式1：Web界面（推荐）

启动Gradio Web界面：

```bash
# 使用默认配置
uv run python app.py

# 或使用批处理文件
启动UI界面.bat

# 或指定端口
uv run python app.py --port 8860
```

然后在浏览器中访问：http://localhost:8860

**鉴权功能**：
- 默认用户：`admin` / `admin123`
- 配置文件：`config/auth.json`
- 支持动态添加用户，无需重启应用
- 详细说明：查看 [鉴权使用指南](AUTHENTICATION_GUIDE.md)

**用户管理工具**：

```bash
# 运行用户管理工具
uv run python manage_users.py

# 功能包括：
# - 查看所有用户
# - 添加/删除用户
# - 修改密码
# - 启用/禁用鉴权
```

#### 方式2：命令行

##### 单文件处理（使用已有的Markdown文件）

```bash
uv run python main.py data/src/your_modbus_protocol.pdf
# 输出文件将自动命名为：data/output/20241216_160230.csv（时间戳格式）
```

##### 重新解析PDF

```bash
uv run python main.py data/src/your_modbus_protocol.pdf --parse-pdf
```

##### 指定输出路径（自定义文件名）

```bash
uv run python main.py data/src/your_modbus_protocol.pdf -o output/my_result.csv
```

##### 批量处理

```bash
uv run python main.py data/src/ --batch
```

##### 自定义控制器名称

```bash
uv run python main.py data/src/your_modbus_protocol.pdf -c ECR_01
# CSV文件中的 ControllerName 列将被设置为 'ECR_01'
# MeasuringPointName 将自动添加前缀，例如：ECR_01_温度, ECR_01_压力
```

> **💡 提示**：默认情况下，程序会使用 `data/output/` 目录下已有的 Markdown 文件，避免重复解析PDF。如果需要重新解析，请添加 `--parse-pdf` 参数。

## 项目结构

```
modbus_info/
├── src/                      # 源代码
│   ├── config.py            # 配置管理
│   ├── pdf_parser.py        # PDF解析模块
│   ├── ai_extractor.py      # AI提取模块
│   ├── csv_exporter.py      # CSV导出模块
│   └── pipeline.py          # 主流程
├── tests/                    # 测试代码
│   ├── test_pdf_parser.py   
│   ├── test_ai_extractor.py 
│   ├── test_csv_exporter.py 
│   ├── test_pipeline.py     
│   └── test_config.py       
├── data/                     # 数据目录
│   ├── src/                 # 输入PDF文件
│   ├── output/              # 输出CSV文件
│   └── demo.csv             # CSV格式示例
├── main.py                   # 程序入口
├── dev_mapping.json          # 字段映射配置
├── modbus_extract.md         # AI提示词模板
├── pyproject.toml           # 项目配置
└── README.md                # 项目说明
```

## 配置说明

### dev_mapping.json

定义需要从PDF中提取的字段信息：

```json
{
    "MeasuringPointName": "测量点名称",
    "GroupName": "组名,固定为default",
    "Address": "数据的起始地址",
    "BitIndex": "数据的位索引,用于确定数据在字节中的位置",
    "reverseBit": "是否需要高低字节转换,0-否,1-是"
}
```

### modbus_extract.md

包含AI提取时使用的系统提示词，可根据需要自定义。

## 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_pdf_parser.py

# 运行测试并查看覆盖率
uv run pytest --cov=src

# 跳过集成测试（不需要API密钥）
uv run pytest -m "not integration"

# 测试鉴权功能
uv run python test_auth.py
```

## 输出格式

输出的CSV文件包含以下主要字段：

- `MeasuringPointName`: 测量点名称（格式：`{ControllerName}_{原始名称}`）
- `ControllerName`: 控制器名称（通过 `-c` 参数指定）
- `GroupName`: 组名（固定为 default）
- `Address`: Modbus地址
- `BitIndex`: 位索引
- `reverseBit`: 是否需要字节转换
- `ReadWrite`: 读写权限（ro/rw）
- 以及其他40+个标准字段

完整字段列表请参考 `data/demo.csv`。

> **📝 编码说明**：CSV文件使用 UTF-8 with BOM 编码，可在 Excel 中直接打开并正确显示中文。

> **🏷️ 命名规则**：MeasuringPointName 自动添加控制器前缀，便于区分不同设备的点位。例如：`ECR_01_温度`、`PLC_02_压力`。

## 工作流程

1. **获取Markdown**：
   - 默认：使用 `data/output/` 下已有的Markdown文件（快速）
   - 可选：使用 `--parse-pdf` 重新解析PDF（首次或更新时）
2. **信息提取**：通过OpenRouter调用Gemini 2.5 Pro从Markdown文本中提取点位信息
3. **格式转换**：将提取的信息标准化并转换为CSV格式
4. **文件输出**：保存到指定路径或默认输出目录

> **性能优化**：程序默认跳过PDF解析步骤，直接使用已有的Markdown文件，这可以节省约30秒的处理时间。

## 依赖项

主要依赖：

- `requests`: HTTP客户端（用于调用PDF解析API）
- `openai`: API客户端（兼容Gemini）
- `pandas`: 数据处理
- `loguru`: 日志记录
- `python-dotenv`: 环境变量管理
- `gradio`: Web UI界面

> 注意：不再需要本地安装完整的 MinerU，除非使用本地Web API方式

## 常见问题

### 1. 鉴权相关

**Q: 如何启用/禁用鉴权？**  
A: 编辑 `config/auth.json`，设置 `"enabled": true` 或 `false`

**Q: 忘记密码怎么办？**  
A: 直接编辑 `config/auth.json` 修改密码，或使用 `manage_users.py` 工具

**Q: 如何添加新用户？**  
A: 运行 `uv run python manage_users.py` 使用交互式工具，或直接编辑 `config/auth.json`

**Q: 修改配置后需要重启吗？**  
A: 不需要！配置会在下次登录时自动重新加载

详细说明请查看：[鉴权使用指南](AUTHENTICATION_GUIDE.md)

### 2. API调用失败

确保：
- OpenRouter API密钥正确配置在 `.env` 文件中
- 网络连接正常
- OpenRouter账户有足够的额度

### 3. PDF解析失败

确保：
- PDF文件格式正常，未加密
- 文件路径正确
- 有足够的磁盘空间存储临时文件

### 4. 测试失败

某些集成测试需要：
- 配置 `.env` 文件
- `data/src/` 目录下有测试PDF文件

可以使用 `-m "not integration"` 跳过集成测试。

## 开发指南

### 添加新功能

1. 在 `src/` 目录下创建新模块
2. 在 `tests/` 目录下添加对应测试
3. 更新文档

### 代码风格

本项目遵循 PEP 8 规范，建议使用以下工具：

```bash
# 代码格式化
black src/ tests/

# 代码检查
ruff check src/ tests/
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过Issue联系。

