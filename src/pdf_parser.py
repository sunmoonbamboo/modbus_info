"""PDF解析模块 - 使用MinerU提取PDF内容为Markdown格式"""

import os
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
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        初始化PDF解析器
        
        Args:
            output_dir: 输出目录，默认为None时会自动生成
        """
        self.output_dir = output_dir
    
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
        
        logger.info(f"PDF解析完成，Markdown文件保存至: {md_file_path}")
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

