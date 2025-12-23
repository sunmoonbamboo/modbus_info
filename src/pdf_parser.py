"""PDF解析模块 - 使用MinerU提取PDF内容为Markdown格式"""

import os
import requests
from pathlib import Path
from typing import Optional

from loguru import logger

from mineru.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2, prepare_env, read_fn
from mineru.data.data_reader_writer import FileBasedDataWriter
from mineru.backend.pipeline.pipeline_analyze import doc_analyze as pipeline_doc_analyze
from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_union_make
from mineru.backend.pipeline.model_json_to_middle_json import result_to_middle_json as pipeline_result_to_middle_json
from mineru.utils.enum_class import MakeMode


class PDFParser:
    """PDF解析器，使用MinerU将PDF转换为Markdown文本"""
    
    def __init__(self, output_dir: Optional[Path] = None, use_web_api: bool = True, api_url: str = "http://127.0.0.1:8000"):
        """
        初始化PDF解析器
        
        Args:
            output_dir: 输出目录，默认为None时会自动生成
            use_web_api: 是否使用Web API方式解析，默认为True
            api_url: Web API服务地址，默认为http://127.0.0.1:8000
        """
        self.output_dir = output_dir
        self.use_web_api = use_web_api
        self.api_url = api_url
    
    def parse(
        self,
        pdf_path: Path,
        lang: str = "ch",
        parse_method: str = "auto",
        formula_enable: bool = True,
        table_enable: bool = True,
    ) -> str:
        """
        解析PDF文件为Markdown文本
        
        Args:
            pdf_path: PDF文件路径
            lang: 语言，默认为'ch'（中文）
            parse_method: 解析方法，默认为'auto'
            formula_enable: 是否启用公式解析
            table_enable: 是否启用表格解析
            
        Returns:
            解析后的Markdown文本字符串
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        logger.info(f"开始解析PDF文件: {pdf_path}")
        
        # 根据配置选择解析方式
        if self.use_web_api:
            return self._parse_via_web_api(
                pdf_path=pdf_path,
                lang=lang,
                parse_method=parse_method,
                formula_enable=formula_enable,
                table_enable=table_enable
            )
        else:
            return self._parse_locally(
                pdf_path=pdf_path,
                lang=lang,
                parse_method=parse_method,
                formula_enable=formula_enable,
                table_enable=table_enable
            )
    
    def _parse_via_web_api(
        self,
        pdf_path: Path,
        lang: str = "ch",
        parse_method: str = "auto",
        formula_enable: bool = True,
        table_enable: bool = True,
    ) -> str:
        """
        通过Web API解析PDF文件为Markdown文本
        
        Args:
            pdf_path: PDF文件路径
            lang: 语言，默认为'ch'（中文）
            parse_method: 解析方法，默认为'auto'
            formula_enable: 是否启用公式解析
            table_enable: 是否启用表格解析
            
        Returns:
            解析后的Markdown文本字符串
        """
        logger.info(f"使用Web API方式解析PDF: {self.api_url}")
        
        try:
            # 设置输出目录
            if self.output_dir is None:
                self.output_dir = pdf_path.parent / "output"
            
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 准备请求参数
            url = f"{self.api_url}/file_parse"
            
            # 打开并上传文件
            with open(pdf_path, 'rb') as f:
                files = {
                    'files': (pdf_path.name, f, 'application/pdf')
                }
                
                # 构建表单数据
                data = {
                    'output_dir': str(self.output_dir),
                    'lang_list': [lang],  # API期望的是数组格式
                    'backend': 'pipeline',
                    'parse_method': parse_method,
                    'formula_enable': formula_enable,
                    'table_enable': table_enable,
                    'return_md': True,  # 返回markdown内容
                    'return_middle_json': False,
                    'return_model_output': False,
                    'return_content_list': False,
                    'return_images': False,
                    'response_format_zip': False
                }
                
                logger.info(f"发送请求到: {url}")
                logger.info(f"请求参数: {data}")
                
                # 发送POST请求
                response = requests.post(url, files=files, data=data, timeout=300)
                
                # 检查响应状态
                response.raise_for_status()
                
                logger.info(f"Web API HTTP状态码: {response.status_code}")
                logger.info(f"Web API响应头: {dict(response.headers)}")
                
                # 先获取原始响应文本（用于调试）
                response_text = response.text
                logger.info(f"Web API原始响应长度: {len(response_text)} 字符")
                logger.info(f"Web API原始响应前500字符: {response_text[:500]}")
                
                # 解析响应
                try:
                    result = response.json()
                    logger.info(f"Web API响应JSON解析成功")
                    logger.info(f"响应类型: {type(result)}")
                    
                    if isinstance(result, dict):
                        logger.info(f"响应字典的keys: {list(result.keys())}")
                        # 打印每个key的类型和值的长度/大小
                        for key, value in result.items():
                            if isinstance(value, str):
                                logger.info(f"  - {key}: {type(value).__name__} (长度: {len(value)})")
                            elif isinstance(value, (list, dict)):
                                logger.info(f"  - {key}: {type(value).__name__} (大小: {len(value)})")
                            else:
                                logger.info(f"  - {key}: {type(value).__name__} = {value}")
                    elif isinstance(result, list):
                        logger.info(f"响应是列表，长度: {len(result)}")
                        if len(result) > 0:
                            logger.info(f"第一个元素类型: {type(result[0])}")
                            if isinstance(result[0], dict):
                                logger.info(f"第一个元素的keys: {list(result[0].keys())}")
                except Exception as json_error:
                    logger.error(f"JSON解析失败: {json_error}")
                    logger.error(f"原始响应: {response_text[:1000]}")
                    raise ValueError(f"无法解析Web API响应的JSON: {json_error}")
                
                # 提取markdown内容
                md_content = None
                
                if isinstance(result, dict):
                    # 可能的返回格式: {"markdown": "...", ...} 或 {"results": [{"markdown": "..."}]}
                    logger.info("尝试从字典中提取markdown内容...")
                    
                    if 'markdown' in result:
                        md_content = result['markdown']
                        logger.info(f"找到 'markdown' 字段，长度: {len(md_content) if md_content else 0}")
                    elif 'md_content' in result:
                        md_content = result['md_content']
                        logger.info(f"找到 'md_content' 字段，长度: {len(md_content) if md_content else 0}")
                    elif 'results' in result:
                        logger.info(f"找到 'results' 字段，类型: {type(result['results'])}")
                        
                        # results 可能是字典或列表
                        if isinstance(result['results'], dict):
                            # results 是字典，key 是文件名
                            logger.info(f"results 是字典，keys: {list(result['results'].keys())}")
                            # 获取第一个文件的结果
                            if len(result['results']) > 0:
                                first_key = list(result['results'].keys())[0]
                                first_result = result['results'][first_key]
                                logger.info(f"使用文件: {first_key}")
                                logger.info(f"文件结果类型: {type(first_result)}")
                                if isinstance(first_result, dict):
                                    logger.info(f"文件结果的keys: {list(first_result.keys())}")
                                    md_content = first_result.get('markdown', '') or first_result.get('md_content', '')
                                    logger.info(f"从 results['{first_key}'] 提取，长度: {len(md_content) if md_content else 0}")
                                elif isinstance(first_result, str):
                                    md_content = first_result
                                    logger.info(f"文件结果直接是字符串，长度: {len(md_content)}")
                        
                        elif isinstance(result['results'], list) and len(result['results']) > 0:
                            # results 是列表（兼容旧格式）
                            first_result = result['results'][0]
                            logger.info(f"results[0] 类型: {type(first_result)}")
                            if isinstance(first_result, dict):
                                logger.info(f"results[0] 的keys: {list(first_result.keys())}")
                                md_content = first_result.get('markdown', '') or first_result.get('md_content', '')
                                logger.info(f"从 results[0] 提取，长度: {len(md_content) if md_content else 0}")
                    else:
                        # 尝试获取第一个包含内容的字段
                        logger.warning(f"未找到标准字段，尝试遍历所有字段...")
                        for key, value in result.items():
                            if isinstance(value, str) and len(value) > 100:
                                logger.info(f"尝试使用字段 '{key}' 作为markdown内容")
                                md_content = value
                                break
                        
                        if not md_content:
                            logger.warning(f"无法确定markdown字段，响应keys: {result.keys()}")
                            logger.warning(f"完整响应内容: {str(result)[:1000]}")
                            
                elif isinstance(result, list) and len(result) > 0:
                    # 如果返回的是列表
                    logger.info("尝试从列表中提取markdown内容...")
                    first_item = result[0]
                    if isinstance(first_item, dict):
                        logger.info(f"列表第一项的keys: {list(first_item.keys())}")
                        md_content = first_item.get('markdown', '') or first_item.get('md_content', '')
                        logger.info(f"从列表第一项提取，长度: {len(md_content) if md_content else 0}")
                    elif isinstance(first_item, str):
                        md_content = first_item
                        logger.info(f"列表第一项是字符串，长度: {len(md_content)}")
                else:
                    logger.error(f"无法解析API响应格式: {type(result)}")
                    logger.error(f"响应内容: {str(result)[:1000]}")
                
                if not md_content:
                    error_msg = "API返回的markdown内容为空或无法提取"
                    logger.error(error_msg)
                    logger.error(f"完整响应结构: {result}")
                    raise ValueError(error_msg)
                
                logger.info(f"✅ 成功提取markdown内容，长度: {len(md_content)} 字符")
                
                # 保存markdown文件
                file_name = pdf_path.stem
                md_file_path = self.output_dir / file_name / "auto" / f"{file_name}.md"
                md_file_path.parent.mkdir(parents=True, exist_ok=True)
                md_file_path.write_text(md_content, encoding='utf-8')
                
                logger.info(f"PDF解析完成（Web API），Markdown文件保存至: {md_file_path}")
                logger.info(f"Markdown文本长度: {len(md_content)} 字符")
                
                return md_content
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Web API请求失败: {e}")
            raise RuntimeError(f"Web API请求失败: {e}。请确认服务是否正常运行在 {self.api_url}")
        except Exception as e:
            logger.error(f"Web API解析失败: {e}")
            raise
    
    def _parse_locally(
        self,
        pdf_path: Path,
        lang: str = "ch",
        parse_method: str = "auto",
        formula_enable: bool = True,
        table_enable: bool = True,
    ) -> str:
        """
        本地解析PDF文件为Markdown文本
        
        Args:
            pdf_path: PDF文件路径
            lang: 语言，默认为'ch'（中文）
            parse_method: 解析方法，默认为'auto'
            formula_enable: 是否启用公式解析
            table_enable: 是否启用表格解析
            
        Returns:
            解析后的Markdown文本字符串
        """
        logger.info("使用本地方式解析PDF")
        
        # 读取PDF文件
        pdf_bytes = read_fn(pdf_path)
        file_name = pdf_path.stem
        
        # 设置输出目录
        if self.output_dir is None:
            self.output_dir = pdf_path.parent / "output"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 转换PDF字节
        new_pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes, 0, None)
        
        # 使用pipeline模式分析PDF
        logger.info("使用pipeline模式分析PDF内容...")
        infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = pipeline_doc_analyze(
            [new_pdf_bytes],
            [lang],
            parse_method=parse_method,
            formula_enable=formula_enable,
            table_enable=table_enable
        )
        
        # 处理第一个（也是唯一一个）PDF的结果
        model_list = infer_results[0]
        images_list = all_image_lists[0]
        pdf_doc = all_pdf_docs[0]
        _lang = lang_list[0]
        _ocr_enable = ocr_enabled_list[0]
        
        # 准备输出环境
        local_image_dir, local_md_dir = prepare_env(str(self.output_dir), file_name, parse_method)
        image_writer = FileBasedDataWriter(local_image_dir)
        
        # 转换为中间JSON格式
        logger.info("转换为中间格式...")
        middle_json = pipeline_result_to_middle_json(
            model_list, images_list, pdf_doc, image_writer,
            _lang, _ocr_enable, formula_enable
        )
        
        pdf_info = middle_json["pdf_info"]
        image_dir = str(os.path.basename(local_image_dir))
        
        # 生成Markdown内容
        logger.info("生成Markdown文本...")
        md_content_str = pipeline_union_make(pdf_info, MakeMode.MM_MD, image_dir)
        
        # 保存Markdown文件（可选）
        md_file_path = Path(local_md_dir) / f"{file_name}.md"
        md_writer = FileBasedDataWriter(local_md_dir)
        md_writer.write_string(f"{file_name}.md", md_content_str)
        
        logger.info(f"PDF解析完成（本地），Markdown文件保存至: {md_file_path}")
        logger.info(f"Markdown文本长度: {len(md_content_str)} 字符")
        
        return md_content_str
    
    def parse_to_file(
        self,
        pdf_path: Path,
        output_md_path: Optional[Path] = None,
        **kwargs
    ) -> Path:
        """
        解析PDF并保存Markdown到指定文件
        
        Args:
            pdf_path: PDF文件路径
            output_md_path: 输出Markdown文件路径，默认为None时自动生成
            **kwargs: 其他解析参数
            
        Returns:
            保存的Markdown文件路径
        """
        md_content = self.parse(pdf_path, **kwargs)
        
        if output_md_path is None:
            output_md_path = self.output_dir / f"{pdf_path.stem}.md"
        
        output_md_path.parent.mkdir(parents=True, exist_ok=True)
        output_md_path.write_text(md_content, encoding='utf-8')
        
        logger.info(f"Markdown文件已保存: {output_md_path}")
        return output_md_path


def parse_pdf_to_markdown(pdf_path: Path, output_dir: Optional[Path] = None) -> str:
    """
    便捷函数：解析PDF为Markdown文本
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
        
    Returns:
        解析后的Markdown文本
    """
    parser = PDFParser(output_dir=output_dir)
    return parser.parse(pdf_path)

