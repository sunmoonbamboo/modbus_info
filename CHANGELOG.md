# 更新日志

本文档记录项目的所有重要更改。

## [1.1.0] - 2025-12-23

### 新增功能

- ✨ **多设备类型配置支持**
  - 支持在UI中选择不同设备类型（冷机、空气源热泵等）
  - 新增 `config/dev_mapping_new.json` 配置文件
  - UI增加设备类型下拉选择器
  - 支持配置实时刷新

- 🌐 **Web API 解析方式**
  - 新增通过Web API解析PDF的功能
  - 支持本地解析和Web API两种方式
  - 默认使用Web API方式（更快）
  - 新增 `启动PDF解析服务.bat` 脚本
  - 详细的调试日志输出

### 改进

- 🎨 UI界面优化
  - 重新组织配置区域布局
  - 增加PDF解析方式选择
  - 改进配置面板的用户体验

- 📝 文档完善
  - 新增 `多设备配置说明.md`
  - 新增 `WEB_API_DEBUG.md`
  - 更新使用说明

### 修复

- 🐛 修复Web API响应解析问题
  - 支持多种响应格式（dict/list）
  - 兼容MinerU v2.6.8的响应格式
  - 增强错误处理和日志输出

## [0.1.0] - 2024-12-16

### 新增功能

- ✨ 初始版本发布
- 📄 PDF解析功能（基于MinerU）
- 🤖 AI提取功能（基于Gemini 2.0）
- 📊 CSV导出功能
- 🔄 批量处理支持
- ✅ 完整的单元测试和集成测试
- 📝 详细的文档和示例

### 核心模块

- `src/config.py`: 配置管理
- `src/pdf_parser.py`: PDF解析模块
- `src/ai_extractor.py`: AI提取模块
- `src/csv_exporter.py`: CSV导出模块
- `src/pipeline.py`: 主流程协调

### 命令行工具

- `main.py`: 主程序入口
- `example.py`: 使用示例
- `verify_setup.py`: 安装验证脚本

### 文档

- `README.md`: 项目说明
- `INSTALL.md`: 安装指南
- `QUICKSTART.md`: 快速入门
- `CHANGELOG.md`: 更新日志

### 测试

- 单元测试覆盖所有核心模块
- 集成测试支持真实PDF和API测试
- 测试标记支持（integration, slow）

### 配置文件

- `pyproject.toml`: 项目配置和依赖管理
- `requirements.txt`: 依赖列表
- `config.example`: 配置模板
- `dev_mapping.json`: 字段映射配置
- `modbus_extract.md`: AI提示词模板

---

## 版本说明

版本号格式：`主版本.次版本.修订号`

- **主版本**：不兼容的API更改
- **次版本**：向后兼容的功能新增
- **修订号**：向后兼容的问题修复

## 未来计划

### v0.2.0（计划中）

- [ ] 支持更多AI模型（Claude, GPT-4等）
- [ ] 增加图形界面
- [ ] 支持Excel输出格式
- [ ] 增加数据验证规则
- [ ] 提高提取准确率

### v0.3.0（计划中）

- [ ] 支持在线PDF解析
- [ ] 增加结果对比工具
- [ ] 支持自定义输出模板
- [ ] 添加Web API接口

## 贡献指南

如果你想为项目做出贡献：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 反馈

欢迎通过以下方式提供反馈：

- 提交 Issue 报告Bug
- 提交 Feature Request 建议新功能
- 提交 Pull Request 贡献代码

---

最后更新：2024-12-16

