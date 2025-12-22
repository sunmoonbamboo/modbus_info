# Gradio UI 实现说明

## 文件结构

```
modbus_info/
├── app.py                    # 主 Gradio 应用程序
├── run_ui.py                 # 快捷启动脚本
├── 启动UI界面.bat            # Windows 批处理启动文件
├── UI_README.md              # UI 使用说明文档
├── GRADIO_IMPLEMENTATION.md  # 本文件 - 实现说明
├── requirements.txt          # 已添加 gradio>=4.0.0
├── pyproject.toml            # 已添加 gradio>=4.0.0
└── ...
```

## 实现的功能

### 1. PDF 文件上传 ✅

```python
# 组件定义
pdf_upload = gr.File(
    label="选择PDF文件",
    file_types=[".pdf"],
    type="filepath"
)

# 上传处理
def upload_pdf(file):
    # 1. 验证文件格式（只接受 PDF）
    if file_path.suffix.lower() != '.pdf':
        return "错误提示"
    
    # 2. 保存到 data/src 目录
    dest_path = self.data_src_dir / file_path.name
    shutil.copy2(file.name, dest_path)
    
    # 3. 返回成功消息和文件路径
    return status_message, file_path
```

### 2. 控制器名称输入 ✅

```python
controller_name = gr.Textbox(
    label="控制器名称 *",
    placeholder="请输入控制器名称（必填）",
    value="default"
)
```

### 3. 地址偏移量输入 ✅

```python
address_offset = gr.Number(
    label="地址偏移量",
    value=0,
    minimum=0,
    maximum=9,
    step=1,
    info="取值范围: [0, 10)"
)
```

### 4. 点位信息配置 ✅

```python
# 从 config/modbus_extract.md 加载默认配置
def _load_default_points(self):
    # 解析格式：-- 查询冷冻水进水温度采集: SPcoolTwIn
    points = {}
    for line in content.split('\n'):
        if line.startswith('--'):
            desc, code = line[2:].split(':', 1)
            points[desc.strip()] = code.strip()
    return points

# JSON 编辑器
points_config = gr.Code(
    label="点位信息配置（JSON格式）",
    language="json",
    value=self.points_dict_to_json(self.default_points),
    lines=15
)
```

### 5. 提取按钮和流程 ✅

```python
extract_btn = gr.Button("🚀 开始提取", variant="primary")

def process_extraction(self, pdf_path, controller_name, address_offset, points_config):
    # 1. 验证输入
    # 2. 解析点位配置（JSON）
    # 3. 更新设备映射配置
    # 4. 执行 Pipeline
    #    - 步骤1: 解析 PDF
    #    - 步骤2: AI 提取
    #    - 步骤3: 导出 CSV
    # 5. 返回结果
```

### 6. 流式显示提取过程 ✅

使用 Python Generator（yield）实现流式输出：

```python
def process_extraction(self, ..., progress=gr.Progress()):
    # 步骤1
    progress(0.1, desc="正在解析PDF...")
    yield "🔄 [步骤 1/3] 正在解析PDF文件...\n", None, None
    
    # 步骤2
    progress(0.4, desc="正在使用AI提取...")
    yield status + "🔄 [步骤 2/3] AI提取中...\n", None, None
    
    # 步骤3
    progress(0.7, desc="正在生成CSV...")
    yield status + "🔄 [步骤 3/3] 生成CSV...\n", None, None
    
    # 完成
    progress(1.0, desc="完成!")
    yield final_status, dataframe, csv_path
```

### 7. 表格显示结果 ✅

```python
result_table = gr.Dataframe(
    label="提取的点位信息",
    wrap=True,
    interactive=False
)

# 读取 CSV 为 DataFrame
df = pd.read_csv(output_csv_path)
yield status, df, csv_path
```

### 8. 下载按钮 ✅

```python
download_btn = gr.DownloadButton(
    label="📥 下载CSV文件",
    visible=False  # 初始隐藏，提取完成后显示
)

# 提取完成后显示下载按钮
extract_btn.click(...).then(
    fn=lambda csv_path: (
        gr.update(visible=csv_path is not None),
        csv_path
    ),
    inputs=[csv_path_state],
    outputs=[download_btn, download_btn]
)
```

## 核心类：ModbusGradioApp

```python
class ModbusGradioApp:
    def __init__(self):
        # 创建必要目录
        # 加载默认点位配置
        
    def _load_default_points(self):
        # 从 config/modbus_extract.md 读取
        
    def upload_pdf(self, file):
        # 处理 PDF 上传
        
    def validate_inputs(self, ...):
        # 验证输入参数
        
    def process_extraction(self, ...):
        # 执行提取流程（流式输出）
        
    def _update_dev_mapping(self, points_dict):
        # 更新设备映射配置
        
    def create_interface(self):
        # 创建 Gradio 界面
        
    def launch(self, **kwargs):
        # 启动应用
```

## 界面布局

```
┌─────────────────────────────────────────────────────────────────┐
│                   📋 Modbus协议信息提取工具                      │
├──────────────────────────────┬──────────────────────────────────┤
│  左侧：输入区 (Column)        │  右侧：输出区 (Column)            │
│  ┌────────────────────────┐  │  ┌────────────────────────────┐  │
│  │ 1️⃣ 上传协议文件        │  │  │ 📊 提取结果                │  │
│  │  └─ PDF上传            │  │  │  ├─ 提取过程 (Textbox)     │  │
│  │  └─ 上传状态           │  │  │  ├─ 结果表格 (Dataframe)   │  │
│  ├────────────────────────┤  │  │  └─ 下载按钮              │  │
│  │ 2️⃣ 配置参数            │  │  └────────────────────────────┘  │
│  │  ├─ 控制器名称 *       │  │                                   │
│  │  └─ 地址偏移量         │  │                                   │
│  ├────────────────────────┤  │                                   │
│  │ 3️⃣ 配置点位信息        │  │                                   │
│  │  └─ JSON编辑器         │  │                                   │
│  │     (15行代码编辑器)    │  │                                   │
│  ├────────────────────────┤  │                                   │
│  │ 🚀 开始提取 (Button)   │  │                                   │
│  └────────────────────────┘  │                                   │
└──────────────────────────────┴──────────────────────────────────┘
│                         使用说明                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 事件流程

```
1. 用户上传 PDF
   ↓
   upload_pdf() → 验证格式 → 保存到 data/src → 更新状态
   ↓
2. 用户配置参数
   - 控制器名称
   - 地址偏移量
   - 点位配置 (JSON)
   ↓
3. 点击"开始提取"
   ↓
   process_extraction()
   ├─ 验证输入
   ├─ 解析点位配置
   ├─ 更新设备映射
   └─ 执行 Pipeline
      ├─ [步骤1] 解析PDF → yield 进度
      ├─ [步骤2] AI提取  → yield 进度
      └─ [步骤3] 导出CSV → yield 进度
   ↓
4. 显示结果
   - 提取过程文本
   - 结果表格
   - 下载按钮
   ↓
5. 用户下载 CSV
```

## 关键技术点

### 1. 流式输出

使用 Python Generator（yield）配合 Gradio 的自动流式处理：

```python
def process_extraction(self, ...):
    yield "步骤1开始", None, None
    # ... 执行步骤1 ...
    yield "步骤1完成", None, None
    
    yield "步骤2开始", None, None
    # ... 执行步骤2 ...
    yield "步骤2完成", None, None
```

### 2. 状态管理

使用 `gr.State` 保存跨组件的状态：

```python
pdf_path_state = gr.State(value="")      # PDF文件路径
csv_path_state = gr.State(value="")      # 生成的CSV文件路径
```

### 3. 动态显示下载按钮

使用 `.then()` 链式调用在提取完成后显示下载按钮：

```python
extract_btn.click(
    fn=process_extraction,
    inputs=[...],
    outputs=[process_output, result_table, csv_path_state]
).then(
    fn=lambda csv_path: (
        gr.update(visible=csv_path is not None),
        csv_path
    ),
    inputs=[csv_path_state],
    outputs=[download_btn, download_btn]
)
```

### 4. JSON 配置编辑

使用 `gr.Code` 组件提供语法高亮的 JSON 编辑器：

```python
points_config = gr.Code(
    label="点位信息配置（JSON格式）",
    language="json",
    value=json.dumps(default_points, ensure_ascii=False, indent=2),
    lines=15
)
```

### 5. 集成现有 Pipeline

直接使用现有的 `ModbusPipeline` 类：

```python
pipeline = ModbusPipeline(
    controller_name=controller_name,
    address_offset=address_offset
)

# 执行处理流程
data_points = pipeline.ai_extractor.extract(markdown_content)
pipeline.csv_exporter.export(data_points, output_csv_path)
```

## 启动方式

### 方式 1：双击批处理文件
```
启动UI界面.bat
```

### 方式 2：命令行
```powershell
# 使用 uv
uv run python app.py

# 或
uv run python run_ui.py
```

### 方式 3：直接 Python
```powershell
python app.py
```

## 配置项

应用启动参数（在 `app.py` 的 `main()` 函数中）：

```python
app.launch(
    server_name="0.0.0.0",    # 监听所有网络接口
    server_port=7860,          # 端口号
    share=False,               # 不创建公网分享链接
    show_error=True            # 显示详细错误信息
)
```

可根据需要修改这些参数。

## 依赖包

新增依赖：
- `gradio>=4.0.0` - Web UI 框架

已更新：
- `requirements.txt`
- `pyproject.toml`

## 日志

应用运行日志保存在：
```
logs/gradio_app_{time}.log
```

包括：
- 文件上传记录
- 处理流程日志
- 错误信息
- API 调用记录

## 安全注意事项

1. **文件上传大小限制**：Gradio 默认有文件大小限制，大文件可能需要调整配置
2. **API 密钥保护**：确保 `.env` 文件不要提交到版本控制
3. **网络访问**：默认监听 `0.0.0.0`，生产环境建议修改为 `127.0.0.1`
4. **文件存储**：上传的文件存储在 `data/src`，定期清理避免占用过多空间

## 扩展建议

未来可以考虑的改进：

1. **批量处理**：支持一次上传多个 PDF 文件
2. **历史记录**：保存和查看历史提取记录
3. **模板管理**：保存和加载不同的点位配置模板
4. **可视化**：添加点位分布的图表展示
5. **用户认证**：添加登录功能保护应用
6. **进度持久化**：长时间处理时保存进度，避免刷新丢失

