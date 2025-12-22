# Modbus协议信息提取工具

从Modbus协议PDF文件中自动提取关键点位信息并导出为CSV格式。

## 功能特性

- 📄 **PDF解析**：使用MinerU自动解析PDF文档，支持复杂的表格和格式
- 🤖 **AI提取**：通过OpenRouter使用Gemini 2.5 Pro模型智能提取Modbus点位信息
- 📊 **CSV导出**：标准化的CSV格式输出，方便导入其他系统
- 🔄 **批量处理**：支持批量处理多个PDF文件
- ✅ **完整测试**：包含单元测试和集成测试

## 快速开始

### 1. 环境准备

本项目使用 `uv` 管理Python环境：

```bash
# 安装uv（如果未安装）
pip install uv

# 安装项目依赖
uv sync

# 单独安装 MinerU（PDF解析引擎）
uv pip install "mineru[core]"
```

### 2. 配置API密钥

复制配置文件模板并填入你的 OpenRouter API 密钥：

```bash
copy config.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME="google/gemini-2.5-pro"
OPENAI_API_KEY=your_api_key_here
```

> 获取API密钥：https://openrouter.ai/keys

### 3. 使用方法

#### 单文件处理（使用已有的Markdown文件）

```bash
uv run python main.py data/src/your_modbus_protocol.pdf
# 输出文件将自动命名为：data/output/20241216_160230.csv（时间戳格式）
```

#### 重新解析PDF

```bash
uv run python main.py data/src/your_modbus_protocol.pdf --parse-pdf
```

#### 指定输出路径（自定义文件名）

```bash
uv run python main.py data/src/your_modbus_protocol.pdf -o output/my_result.csv
```

#### 批量处理

```bash
uv run python main.py data/src/ --batch
```

#### 自定义控制器名称

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

- `mineru[core]`: PDF解析（需要单独安装）
- `openai`: API客户端（兼容Gemini）
- `pandas`: 数据处理
- `loguru`: 日志记录
- `python-dotenv`: 环境变量管理

## 常见问题

### 1. API调用失败

确保：
- OpenRouter API密钥正确配置在 `.env` 文件中
- 网络连接正常
- OpenRouter账户有足够的额度

### 2. PDF解析失败

确保：
- PDF文件格式正常，未加密
- 文件路径正确
- 有足够的磁盘空间存储临时文件

### 3. 测试失败

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

