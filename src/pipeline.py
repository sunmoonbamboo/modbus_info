"""主流程模块 - 协调整个处理流程"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from loguru import logger

from src.config import config
from src.pdf_parser import PDFParser
from src.ai_extractor import AIExtractor
from src.csv_exporter import CSVExporter


class ModbusPipeline:
    """Modbus协议信息提取流程"""
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        controller_name: str = "default"
    ):
        """
        初始化流程
        
        Args:
            output_dir: 输出目录，默认为配置中的输出目录
            controller_name: 控制器名称，默认为'default'
        """
        self.output_dir = output_dir or config.OUTPUT_DIR
        self.controller_name = controller_name
        
        # 初始化各个模块
        self.pdf_parser = PDFParser(output_dir=self.output_dir)
        self.ai_extractor = AIExtractor()
        self.csv_exporter = CSVExporter(controller_name=controller_name)
        
        logger.info("ModbusPipeline 初始化完成")
    
    def process(
        self,
        pdf_path: Path,
        output_csv_path: Optional[Path] = None,
        save_markdown: bool = True,
        parse_pdf: bool = False
    ) -> Path:
        """
        处理完整流程：PDF -> Markdown -> AI提取 -> CSV
        
        Args:
            pdf_path: 输入PDF文件路径
            output_csv_path: 输出CSV文件路径，默认为None时自动生成
            save_markdown: 是否保存中间的Markdown文件
            parse_pdf: 是否重新解析PDF（默认False，使用已有的Markdown文件）
            
        Returns:
            输出的CSV文件路径
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        logger.info("=" * 60)
        logger.info(f"开始处理 Modbus 协议文件: {pdf_path.name}")
        logger.info("=" * 60)
        
        # 步骤1: 获取Markdown内容
        if parse_pdf:
            # 重新解析PDF为Markdown
            logger.info("\n[步骤 1/3] 解析PDF文件...")
            markdown_content = self.pdf_parser.parse(pdf_path)
            logger.info(f"✓ PDF解析完成，文本长度: {len(markdown_content)} 字符")
        else:
            # 使用已有的Markdown文件
            logger.info("\n[步骤 1/3] 读取已有的Markdown文件...")
            markdown_path = self._find_existing_markdown(pdf_path)
            if markdown_path and markdown_path.exists():
                markdown_content = markdown_path.read_text(encoding='utf-8')
                logger.info(f"✓ 读取Markdown文件: {markdown_path.name}")
                logger.info(f"✓ 文本长度: {len(markdown_content)} 字符")
            else:
                logger.warning(f"⚠ 未找到已有的Markdown文件，将重新解析PDF")
                markdown_content = self.pdf_parser.parse(pdf_path)
                logger.info(f"✓ PDF解析完成，文本长度: {len(markdown_content)} 字符")
        
        # 步骤2: 使用AI提取点位信息
        logger.info("\n[步骤 2/3] 使用AI提取点位信息...")
        data_points = self.ai_extractor.extract(markdown_content)
        logger.info(f"✓ 成功提取 {len(data_points)} 个点位")
        
        # 步骤3: 导出为CSV
        logger.info("\n[步骤 3/3] 导出CSV文件...")
        if output_csv_path is None:
            # 使用时间戳生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_csv_path = self.output_dir / f"{timestamp}.csv"
        
        self.csv_exporter.export(data_points, output_csv_path)
        logger.info(f"✓ CSV文件已保存: {output_csv_path}")
        
        logger.info("\n" + "=" * 60)
        logger.info("处理完成！")
        logger.info("=" * 60)
        
        return output_csv_path
    
    def _find_existing_markdown(self, pdf_path: Path) -> Optional[Path]:
        """
        查找已存在的Markdown文件
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            Markdown文件路径，如果不存在则返回None
        """
        # 构造可能的Markdown文件路径
        # 格式1: data/output/{pdf_name}.md/{pdf_name}/auto/{pdf_name}.md
        pdf_stem = pdf_path.stem
        md_path1 = self.output_dir / f"{pdf_stem}.md" / pdf_stem / "auto" / f"{pdf_stem}.md"
        
        # 格式2: data/output/{pdf_name}/auto/{pdf_name}.md
        md_path2 = self.output_dir / pdf_stem / "auto" / f"{pdf_stem}.md"
        
        # 格式3: data/output/{pdf_name}.md
        md_path3 = self.output_dir / f"{pdf_stem}.md"
        
        # 按顺序检查
        for md_path in [md_path1, md_path2, md_path3]:
            if md_path.exists():
                return md_path
        
        return None
    
    def process_batch(
        self,
        pdf_paths: list[Path],
        output_dir: Optional[Path] = None,
        parse_pdf: bool = False
    ) -> list[Path]:
        """
        批量处理多个PDF文件
        
        Args:
            pdf_paths: PDF文件路径列表
            output_dir: 输出目录
            parse_pdf: 是否重新解析PDF
            
        Returns:
            生成的CSV文件路径列表
        """
        if output_dir:
            self.output_dir = output_dir
        
        results = []
        total = len(pdf_paths)
        
        logger.info(f"开始批量处理 {total} 个文件...")
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            try:
                logger.info(f"\n处理文件 {i}/{total}: {pdf_path.name}")
                csv_path = self.process(pdf_path, parse_pdf=parse_pdf)
                results.append(csv_path)
            except Exception as e:
                logger.error(f"处理文件 {pdf_path.name} 失败: {e}")
                continue
        
        logger.info(f"\n批量处理完成！成功: {len(results)}/{total}")
        return results


def process_pdf(
    pdf_path: Path,
    output_csv_path: Optional[Path] = None,
    controller_name: str = "default",
    parse_pdf: bool = False
) -> Path:
    """
    便捷函数：处理单个PDF文件
    
    Args:
        pdf_path: PDF文件路径
        output_csv_path: 输出CSV路径
        controller_name: 控制器名称，默认为'default'
        parse_pdf: 是否重新解析PDF
        
    Returns:
        输出的CSV文件路径
    """
    pipeline = ModbusPipeline(controller_name=controller_name)
    return pipeline.process(pdf_path, output_csv_path, parse_pdf=parse_pdf)

