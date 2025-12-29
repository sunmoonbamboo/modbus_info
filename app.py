"""Gradio Web UI - Modbus协议信息提取工具"""

import gradio as gr
from pathlib import Path
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import argparse

from loguru import logger

from src.pipeline import ModbusPipeline
from src.config import config


class ModbusGradioApp:
    """Modbus协议提取的Gradio应用"""
    
    def __init__(self):
        """初始化应用"""
        # 确保必要的目录存在
        self.data_src_dir = Path("data/src")
        self.data_src_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载默认的配置
        self.default_dev_mapping = self._load_dev_mapping()
        self.default_point_metadata = self._load_point_metadata()
        
        # 加载新的多套配置（如果存在）
        self.dev_mapping_new = self._load_dev_mapping_new()
        self.available_device_types = list(self.dev_mapping_new.keys()) if self.dev_mapping_new else []
        
        logger.info("Gradio应用初始化完成")
        logger.info(f"可用设备类型: {self.available_device_types}")
    
    def _load_dev_mapping(self) -> Dict[str, str]:
        """
        从 config/dev_mapping.json 加载设备映射配置
        
        Returns:
            设备映射配置字典
        """
        try:
            mapping_file = Path("config/dev_mapping.json")
            if not mapping_file.exists():
                logger.warning(f"配置文件不存在: {mapping_file}")
                return self._get_fallback_dev_mapping()
            
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            
            logger.info(f"成功加载 {len(mapping)} 个设备映射配置")
            return mapping
            
        except Exception as e:
            logger.error(f"加载设备映射配置失败: {e}")
            return self._get_fallback_dev_mapping()
    
    def _load_dev_mapping_new(self) -> Dict[str, Dict[str, str]]:
        """
        从 config/dev_mapping_new.json 加载多套设备映射配置
        
        Returns:
            设备映射配置字典，格式: {"设备类型": {"描述": "编码", ...}, ...}
        """
        try:
            mapping_file = Path("config/dev_mapping_new.json")
            if not mapping_file.exists():
                logger.warning(f"多套配置文件不存在: {mapping_file}，将使用默认配置")
                return {}
            
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            
            # 验证格式是否正确（应该是嵌套字典）
            if not isinstance(mapping, dict):
                logger.error(f"配置文件格式错误，应该是字典类型")
                return {}
            
            # 统计配置数量
            total_points = sum(len(v) if isinstance(v, dict) else 0 for v in mapping.values())
            logger.info(f"成功加载多套配置: {len(mapping)} 个设备类型，共 {total_points} 个点位")
            
            return mapping
            
        except Exception as e:
            logger.error(f"加载多套设备映射配置失败: {e}")
            return {}
    
    def _get_fallback_dev_mapping(self) -> Dict[str, str]:
        """返回备用的默认设备映射配置"""
        return {
            "查询冷冻水进水温度采集": "SPcoolTwIn",
            "查询冷冻水出水温度采集": "SPcoolTwOut",
            "查询热水进水温度采集": "SPheatTwIn",
            "查询热水出水温度采集": "SPheatTwOut",
            "查询机组开关机采集": "STrunning",
            "机组开关设定(没有分别指定开机、关机时使用)": "TurnonOrOff",
            "机组开机设定(单独设定开机)": "Turnon",
            "机组关机设定(单独设定关机)": "Turnoff",
            "查询运行模式采集": "Mode",
            "热水温度设定点": "Setheatpoint",
            "冷水温度设定点": "Setcoolpoint",
            "出水温度设定点（没有指定冷水和热水时使用）": "ToutSet"
        }
    
    def _load_point_metadata(self) -> Dict[str, str]:
        """
        从 config/point_metadata.json 加载点位元数据配置
        
        Returns:
            点位元数据配置字典
        """
        try:
            metadata_file = Path("config/point_metadata.json")
            if not metadata_file.exists():
                logger.warning(f"配置文件不存在: {metadata_file}")
                return {}
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            logger.info(f"成功加载 {len(metadata)} 个点位元数据配置")
            return metadata
            
        except Exception as e:
            logger.error(f"加载点位元数据配置失败: {e}")
            return {}
    
    def upload_pdf(self, file) -> Tuple[str, str]:
        """
        处理PDF文件上传
        
        Args:
            file: Gradio上传的文件对象
            
        Returns:
            (状态消息, 文件路径)
        """
        if file is None:
            return "❌ 请选择一个文件", ""
        
        # 检查文件扩展名
        file_path = Path(file.name)
        if file_path.suffix.lower() != '.pdf':
            return f"❌ 只支持PDF格式的文件，当前文件格式: {file_path.suffix}", ""
        
        try:
            # 保存文件到 data/src 目录
            dest_path = self.data_src_dir / file_path.name
            shutil.copy2(file.name, dest_path)
            
            logger.info(f"文件已保存: {dest_path}")
            return f"✅ 文件上传成功: {file_path.name}\n文件已保存至: {dest_path}", str(dest_path)
            
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return f"❌ 文件上传失败: {str(e)}", ""
    
    def validate_inputs(
        self, 
        pdf_path: str, 
        controller_name: str,
        address_offset: int
    ) -> Optional[str]:
        """
        验证输入参数
        
        Args:
            pdf_path: PDF文件路径
            controller_name: 控制器名称
            address_offset: 地址偏移量
            
        Returns:
            错误信息，如果验证通过则返回None
        """
        if not pdf_path:
            return "❌ 请先上传PDF文件"
        
        if not Path(pdf_path).exists():
            return f"❌ 文件不存在: {pdf_path}"
        
        if not controller_name or not controller_name.strip():
            return "❌ 请输入控制器名称"
        
        if not (0 <= address_offset < 10):
            return f"❌ 地址偏移量必须在 [0, 10) 范围内，当前值: {address_offset}"
        
        return None
    
    def process_extraction(
        self,
        pdf_path: str,
        controller_name: str,
        address_offset: int,
        dev_mapping_config: str,
        metadata_config: str,
        parse_mode: str,
        api_url: str,
        progress=gr.Progress()
    ):
        """
        执行提取流程
        
        Args:
            pdf_path: PDF文件路径
            controller_name: 控制器名称
            address_offset: 地址偏移量
            dev_mapping_config: 设备映射配置（JSON字符串）
            metadata_config: 点位元数据配置（JSON字符串）
            parse_mode: 解析模式（local_api/official_api）
            api_url: Web API服务地址
            progress: Gradio进度条对象
            
        Yields:
            (状态信息, 结果DataFrame, CSV文件路径)
        """
        # 验证输入
        error_msg = self.validate_inputs(pdf_path, controller_name, address_offset)
        if error_msg:
            yield error_msg, None, None
            return
        
        try:
            # 解析配置
            try:
                dev_mapping_dict = json.loads(dev_mapping_config)
                logger.info(f"使用设备映射配置: {len(dev_mapping_dict)} 个点位")
            except Exception as e:
                yield f"❌ 设备映射配置格式错误: {str(e)}", None, None
                return
            
            try:
                metadata_dict = json.loads(metadata_config)
                logger.info(f"使用点位元数据配置: {len(metadata_dict)} 个字段")
            except Exception as e:
                yield f"❌ 点位元数据配置格式错误: {str(e)}", None, None
                return
            
            # 初始化进度
            progress(0, desc="正在初始化...")
            
            # 解析模式名称映射
            mode_names = {
                "local_api": "本地Web API",
                "official_api": "MinerU官方API"
            }
            mode_name = mode_names.get(parse_mode, parse_mode)
            yield f"🔄 正在初始化处理流程... (解析方式: {mode_name})\n", None, None
            
            # 如果使用官方API，从环境变量读取配置
            official_api_token = None
            file_server_url = None
            if parse_mode == "official_api":
                from src.config import config
                official_api_token = config.MINERU_API_TOKEN
                file_server_url = config.FILE_SERVER_URL
                
                # 检查是否配置了必要的参数
                if not official_api_token:
                    yield "❌ 错误: 未配置 MINERU_API_TOKEN\n请在 .env 文件中设置 MINERU_API_TOKEN=your_token_here", None, None
                    return
                
                if not file_server_url:
                    logger.warning("未配置 FILE_SERVER_URL，将使用本地文件路径（可能无法正常工作）")
                
                logger.info(f"使用官方API配置 - Token: {'已配置' if official_api_token else '未配置'}, 文件服务器: {file_server_url or '未配置'}")
            
            # 创建Pipeline实例（使用当前会话的配置，不写入文件）
            pipeline = ModbusPipeline(
                controller_name=controller_name,
                address_offset=address_offset,
                dev_mapping=dev_mapping_dict,
                point_metadata=metadata_dict,
                use_web_api=(parse_mode == "local_api"),
                api_url=api_url,
                parse_mode=parse_mode,
                official_api_token=official_api_token,
                file_server_url=file_server_url
            )
            
            pdf_file = Path(pdf_path)
            
            # 步骤1: 解析PDF
            progress(0.1, desc="正在解析PDF...")
            yield "🔄 [步骤 1/3] 正在解析PDF文件...\n", None, None
            
            # 查找已有的Markdown文件
            markdown_path = pipeline._find_existing_markdown(pdf_file)
            if markdown_path and markdown_path.exists():
                markdown_content = markdown_path.read_text(encoding='utf-8')
                status = f"✅ 读取已有的Markdown文件: {markdown_path.name}\n"
                status += f"📄 文本长度: {len(markdown_content)} 字符\n\n"
            else:
                markdown_content = pipeline.pdf_parser.parse(pdf_file)
                status = f"✅ PDF解析完成\n"
                status += f"📄 文本长度: {len(markdown_content)} 字符\n\n"
            
            yield status, None, None
            
            # 步骤2: AI提取
            progress(0.4, desc="正在使用AI提取点位信息...")
            yield status + "🔄 [步骤 2/3] 正在使用AI提取点位信息...\n", None, None
            
            data_points = pipeline.ai_extractor.extract(markdown_content)
            
            status += f"✅ 成功提取 {len(data_points)} 个点位信息\n\n"
            yield status, None, None
            
            # 步骤3: 导出CSV
            progress(0.7, desc="正在生成CSV文件...")
            yield status + "🔄 [步骤 3/3] 正在生成CSV文件...\n", None, None
            
            # 生成输出文件路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_csv_path = config.OUTPUT_DIR / f"{timestamp}.csv"
            
            pipeline.csv_exporter.export(data_points, output_csv_path)
            
            status += f"✅ CSV文件已保存: {output_csv_path}\n\n"
            status += "=" * 60 + "\n"
            status += "🎉 处理完成！\n"
            status += "=" * 60 + "\n"
            
            # 读取CSV为DataFrame用于显示
            df = pd.read_csv(output_csv_path)
            
            progress(1.0, desc="完成!")
            yield status, df, str(output_csv_path)
            
        except Exception as e:
            logger.error(f"提取失败: {e}", exc_info=True)
            error_msg = f"❌ 提取失败: {str(e)}\n\n详细信息请查看日志文件"
            yield error_msg, None, None
    
    def dict_to_json(self, data_dict: Dict[str, str]) -> str:
        """将字典转换为格式化的JSON字符串"""
        return json.dumps(data_dict, ensure_ascii=False, indent=2)
    
    def get_device_mapping(self, device_type: str) -> str:
        """
        根据设备类型获取对应的映射配置
        
        Args:
            device_type: 设备类型名称
            
        Returns:
            格式化的JSON字符串
        """
        if not device_type or device_type == "默认配置":
            # 使用默认配置
            return self.dict_to_json(self.default_dev_mapping)
        
        # 从多套配置中获取
        if device_type in self.dev_mapping_new:
            return self.dict_to_json(self.dev_mapping_new[device_type])
        
        # 如果找不到，返回默认配置
        logger.warning(f"未找到设备类型 '{device_type}' 的配置，使用默认配置")
        return self.dict_to_json(self.default_dev_mapping)
    
    def create_interface(self) -> gr.Blocks:
        """
        创建Gradio界面
        
        Returns:
            Gradio Blocks对象
        """
        with gr.Blocks(
            title="Modbus协议信息提取工具",
            theme=gr.themes.Soft()
        ) as interface:
            
            gr.Markdown("""
            # 📋 Modbus协议信息提取工具
            
            从PDF文档自动提取Modbus点位信息并导出为CSV格式 | 基于AI的智能识别
            """)
            
            # 存储上传文件的路径
            pdf_path_state = gr.State(value="")
            
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### 1️⃣ 上传协议文件")
                    
                    # PDF上传
                    pdf_upload = gr.File(
                        label="选择PDF文件",
                        file_types=[".pdf"],
                        type="filepath"
                    )
                    upload_status = gr.Textbox(
                        label="上传状态",
                        interactive=False,
                        lines=2
                    )
                    
                    gr.Markdown("### 2️⃣ 配置参数")
                    
                    with gr.Row():
                        # 控制器名称
                        controller_name = gr.Textbox(
                            label="控制器名称 *",
                            placeholder="请输入控制器名称（必填）",
                            value="default"
                        )
                        
                        # 地址偏移量
                        address_offset = gr.Number(
                            label="地址偏移量",
                            value=0,
                            minimum=0,
                            maximum=9,
                            step=1,
                            info="取值范围: [0, 10)"
                        )
                    
                    # PDF解析方式配置
                    gr.Markdown("### 3️⃣ PDF解析方式")
                    with gr.Row():
                        parse_mode = gr.Radio(
                            label="解析方式",
                            choices=[
                                ("MinerU官方API", "official_api"),
                                ("本地Web API（需启动本地服务）", "local_api")
                            ],
                            value="official_api",
                            info="选择PDF解析的方式"
                        )
                    
                    with gr.Accordion("⚙️ API配置", open=False):
                        gr.Markdown("""
                        **配置说明:**
                        - **本地Web API**: 需要在下方配置本地服务地址
                        - **MinerU官方API**: 自动从 `.env` 文件读取 `MINERU_API_TOKEN` 和 `FILE_SERVER_URL`
                        """)
                        
                        with gr.Row():
                            api_url = gr.Textbox(
                                label="本地Web API 地址",
                                value="http://127.0.0.1:8000",
                                placeholder="请输入本地Web API服务地址",
                                info="仅在使用本地Web API方式时有效"
                            )
                    
                    # 高级配置（可折叠）
                    gr.Markdown("### 4️⃣ 高级配置（可选）")
                    with gr.Accordion("⚙️ 点位映射与元数据配置", open=False):
                        gr.Markdown("💡 *修改仅在当前会话生效，不会保存到配置文件*")
                        
                        with gr.Tabs():
                            with gr.Tab("📝 点位映射 (dev_mapping)"):
                                gr.Markdown("*定义需要提取的点位。格式: {\"描述\": \"标准编码\"}*")
                                
                                # 设备类型选择器
                                with gr.Row():
                                    device_type_selector = gr.Dropdown(
                                        label="🏭 选择设备类型",
                                        choices=["默认配置"] + self.available_device_types,
                                        value="默认配置" if not self.available_device_types else self.available_device_types[0],
                                        info="选择要使用的设备配置方案",
                                        scale=3
                                    )
                                    refresh_config_btn = gr.Button(
                                        "🔄 刷新配置",
                                        size="sm",
                                        scale=1
                                    )
                                
                                # 设备映射配置编辑器
                                dev_mapping_config = gr.Code(
                                    label="",
                                    language="json",
                                    value=self.get_device_mapping(
                                        self.available_device_types[0] if self.available_device_types else "默认配置"
                                    ),
                                    lines=8
                                )
                            
                            with gr.Tab("🏷️ 元数据 (point_metadata)"):
                                gr.Markdown("*定义提取字段的含义。格式: {\"字段名\": \"字段说明\"}*")
                                # 点位元数据配置编辑器
                                metadata_config = gr.Code(
                                    label="",
                                    language="json",
                                    value=self.dict_to_json(self.default_point_metadata),
                                    lines=8
                                )
                    
                    # 提取按钮
                    extract_btn = gr.Button(
                        "🚀 开始提取",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=3):
                    gr.Markdown("### 📊 提取结果")
                    
                    # 使用Tabs组织提取过程和结果
                    with gr.Tabs():
                        with gr.Tab("📋 提取过程"):
                            # 提取过程显示
                            process_output = gr.Textbox(
                                label="",
                                lines=20,
                                max_lines=30,
                                interactive=False,
                                show_copy_button=True
                            )
                        
                        with gr.Tab("📊 数据预览"):
                            # 结果表格
                            result_table = gr.Dataframe(
                                label="",
                                wrap=True,
                                interactive=False
                            )
                    
                    # CSV文件路径（隐藏）
                    csv_path_state = gr.State(value="")
                    
                    # 下载按钮
                    download_btn = gr.DownloadButton(
                        label="📥 下载CSV文件",
                        visible=False,
                        size="lg"
                    )
            
            # 事件处理
            
            # 设备类型选择事件
            device_type_selector.change(
                fn=self.get_device_mapping,
                inputs=[device_type_selector],
                outputs=[dev_mapping_config]
            )
            
            # 刷新配置按钮事件
            refresh_config_btn.click(
                fn=self.get_device_mapping,
                inputs=[device_type_selector],
                outputs=[dev_mapping_config]
            )
            
            # 文件上传事件
            pdf_upload.upload(
                fn=self.upload_pdf,
                inputs=[pdf_upload],
                outputs=[upload_status, pdf_path_state]
            )
            
            # 提取按钮点击事件
            extract_btn.click(
                fn=self.process_extraction,
                inputs=[
                    pdf_path_state,
                    controller_name,
                    address_offset,
                    dev_mapping_config,
                    metadata_config,
                    parse_mode,
                    api_url
                ],
                outputs=[
                    process_output,
                    result_table,
                    csv_path_state
                ]
            ).then(
                # 提取完成后显示下载按钮
                fn=lambda csv_path: (gr.update(visible=csv_path is not None and csv_path != ""), csv_path),
                inputs=[csv_path_state],
                outputs=[download_btn, download_btn]
            )
            
            with gr.Accordion("📖 使用说明", open=False):
                gr.Markdown("""
                ### 快速开始
                
                1. **上传文件**: 选择Modbus协议的PDF文件（仅支持PDF格式）
                2. **配置参数**: 填写控制器名称（必填）和地址偏移量（可选）
                3. **选择解析方式**: 
                   - **本地Web API**: 需要先启动解析服务，速度更快
                   - **MinerU官方API**: 云端解析，自动从 `.env` 读取配置
                4. **配置API**: 根据选择的解析方式配置相应参数
                5. **开始提取**: 点击"🚀 开始提取"按钮
                6. **查看结果**: 在右侧的"提取过程"和"数据预览"标签页中查看结果
                7. **下载文件**: 提取完成后点击"📥 下载CSV文件"保存结果
                
                ### PDF解析方式详解
                
                - **本地Web API方式**（推荐）: 
                  - 需要先启动解析服务: `uv run python -m mineru.server --host 0.0.0.0 --port 8000`
                  - 解析速度更快，支持分布式部署
                  - 默认地址: http://127.0.0.1:8000
                  - 适合本地有GPU的情况
                
                - **MinerU官方API方式**（新增）: 
                  - 使用MinerU官方云端服务进行解析
                  - **配置方式**: 在项目根目录的 `.env` 文件中配置
                    ```bash
                    MINERU_API_TOKEN=your_token_here
                    FILE_SERVER_URL=http://localhost:8080
                    ```
                  - 需要先启动文件服务器: `uv run python start_file_server.py`
                  - 在 https://mineru.net 申请API Token
                  - 每天享有2000页免费额度
                  - 适合没有GPU或需要快速解析的情况
                  - ⚠️ 注意：配置完 `.env` 后需重启应用
                
                ### 高级配置（可选）
                
                - **设备类型选择**: 
                  - 支持多套预定义配置（冷机、空气源热泵等）
                  - 可以在下拉菜单中选择不同的设备类型
                  - 配置文件: `config/dev_mapping_new.json`
                
                - **点位映射（dev_mapping）**: 
                  - 定义需要从PDF中提取的点位
                  - 格式: `{"点位描述": "标准编码"}`
                  - 可以手动编辑或选择预定义配置
                
                - **元数据（point_metadata）**: 
                  - 定义提取字段的含义和说明
                  - 格式: `{"字段名": "字段说明"}`
                
                - ⚠️ **注意**: 配置修改仅在当前会话生效，不会保存到配置文件
                
                ### 系统流程
                
                1. 解析PDF文件为Markdown格式（Web API 或 本地）
                2. 使用AI模型（Gemini）提取点位信息
                3. 根据配置生成标准CSV文件
                
                ---
                💡 **提示**: 提取过程可能需要几分钟，请耐心等待...
                """)
        
        return interface
    
    def launch(self, **kwargs):
        """
        启动Gradio应用
        
        Args:
            **kwargs: 传递给gr.Blocks.launch()的参数
        """
        interface = self.create_interface()
        interface.launch(**kwargs)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Modbus协议信息提取工具 - Gradio Web界面")
    parser.add_argument(
        "--server-name",
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务器地址，默认为 0.0.0.0（监听所有网络接口）"
    )
    parser.add_argument(
        "--server-port",
        "--port",
        type=int,
        default=8860,
        help="服务器端口，默认为 8860"
    )
    args = parser.parse_args()
    
    # 配置日志
    logger.add(
        "logs/gradio_app_{time}.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO"
    )
    
    logger.info(f"启动服务器: {args.server_name}:{args.server_port}")
    
    # 创建并启动应用
    app = ModbusGradioApp()
    app.launch(
        server_name=args.server_name,
        server_port=args.server_port,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()

