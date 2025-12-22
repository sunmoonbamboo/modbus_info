# 快速入门指南

本指南将帮助你在5分钟内开始使用Modbus协议信息提取工具。

## 前提条件

- ✅ Python 3.12+ 已安装
- ✅ 有可用的网络连接

## 第1步：安装uv并设置项目 (1分钟)

```powershell
# 安装uv
pip install uv

# 进入项目目录（如果还没有）
cd modbus_info

# 安装项目依赖
uv sync

# 单独安装 MinerU（PDF解析引擎）
uv pip install "mineru[core]"
```

## 第2步：配置API密钥 (2分钟)

```powershell
# 复制配置模板
copy config.example .env
```

然后：

1. 访问 https://openrouter.ai/keys
2. 创建或登录账户
3. 点击"Create Key"生成API密钥
4. 用记事本打开 `.env` 文件
5. 将 `your_api_key_here` 替换为你的API密钥
6. 保存文件

## 第3步：验证安装 (1分钟)

```powershell
uv run python verify_setup.py
```

如果看到 "🎉 恭喜！所有检查都通过了！"，说明安装成功！

## 第4步：处理你的第一个PDF (1分钟)

将你的Modbus协议PDF文件放入 `data/src/` 目录，然后运行：

```powershell
uv run python main.py data/src/你的文件.pdf
```

处理完成后，CSV文件将保存在 `data/output/` 目录下，文件名格式为：`20241216_160230.csv`（年月日_时分秒）。

## 示例输出

```
============================================================
开始处理 Modbus 协议文件: EK400模块螺杆式冷水（热泵）机Modbus客户通信协议-大金VRV.pdf
============================================================

[步骤 1/3] 读取已有的Markdown文件...
✓ 读取Markdown文件: EK400模块螺杆式冷水（热泵）机Modbus客户通信协议-大金VRV.md
✓ 文本长度: 12345 字符

[步骤 2/3] 使用AI提取点位信息...
✓ 成功提取 42 个点位

[步骤 3/3] 导出CSV文件...
✓ CSV文件已保存: data/output/20241216_160230.csv

============================================================
处理完成！
============================================================
```

## 常用命令

```powershell
# 使用已有的Markdown文件（快速模式，推荐）
uv run python main.py data/src/your_file.pdf

# 重新解析PDF（首次处理或PDF有更新时）
uv run python main.py data/src/your_file.pdf --parse-pdf

# 指定输出文件
uv run python main.py input.pdf -o output.csv

# 批量处理整个目录
uv run python main.py data/src/ --batch

# 自定义控制器名称（默认为 default）
uv run python main.py input.pdf -c ECR_01
# MeasuringPointName 会自动添加控制器前缀：ECR_01_温度, ECR_01_压力 等

# 查看帮助
uv run python main.py --help

# 运行测试
uv run pytest

# 运行示例代码
uv run python example.py
```

> **⚡ 性能提示**：默认使用已有的Markdown文件可以节省大量时间（约30秒），只在首次处理或PDF更新时使用 `--parse-pdf`。

## 输出文件说明

生成的CSV文件包含以下关键列：

| 列名 | 说明 | 示例 |
|------|------|------|
| MeasuringPointName | 测量点名称 | ECR_01_温度传感器 |
| ControllerName | 控制器名称 | ECR_01 |
| GroupName | 组名 | default |
| Address | Modbus地址 | 0X0001 |
| BitIndex | 位索引 | 0 |
| reverseBit | 字节转换 | 0 |
| ReadWrite | 读写权限 | ro/rw |

完整的字段列表请查看 `data/demo.csv`。

> **💡 提示**：
> - CSV文件使用UTF-8编码（带BOM），可以直接在Excel中打开，中文显示正常
> - MeasuringPointName 自动添加控制器前缀（格式：`{ControllerName}_{原始名称}`），便于区分不同设备

## 故障排除

### 问题：API调用失败

**原因**：API密钥未配置或无效

**解决**：
1. 检查 `.env` 文件中的API密钥
2. 确认API密钥有效且有配额
3. 检查网络连接

### 问题：找不到PDF文件

**原因**：文件路径不正确

**解决**：
1. 使用绝对路径或相对于项目根目录的路径
2. 确认文件扩展名为 `.pdf`
3. 检查文件是否真的存在

### 问题：导入错误

**原因**：依赖未正确安装

**解决**：
```powershell
# 重新安装依赖
uv sync

# 或使用pip
pip install -r requirements.txt
```

## 下一步

- 📖 阅读完整文档：[README.md](README.md)
- 🔧 查看示例代码：[example.py](example.py)
- 🧪 运行测试：`uv run pytest`
- 📝 自定义提示词：编辑 `modbus_extract.md`
- ⚙️ 修改字段映射：编辑 `dev_mapping.json`

## 获取帮助

- 查看 [常见问题](README.md#常见问题)
- 查看 [详细安装指南](INSTALL.md)
- 提交 Issue 报告问题

---

**祝使用愉快！** 🚀

