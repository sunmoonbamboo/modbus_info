"""主程序入口"""

import argparse
from pathlib import Path

from loguru import logger

from src.pipeline import ModbusPipeline
from src.config import config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="从Modbus协议PDF文件中提取关键点位信息并导出为CSV"
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        help="输入的PDF文件路径"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出的CSV文件路径（默认：data/output/{pdf_name}.csv）"
    )
    parser.add_argument(
        "-c", "--controller",
        type=str,
        default="default",
        help="控制器名称（默认：default）"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="输出目录（默认：data/output）"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="批量处理模式（pdf_path为目录）"
    )
    parser.add_argument(
        "--parse-pdf",
        action="store_true",
        help="重新解析PDF文件（默认使用已有的Markdown文件）"
    )
    
    args = parser.parse_args()
    
    # 配置日志
    logger.add(
        "logs/modbus_extract_{time}.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO"
    )
    
    try:
        # 验证配置
        config.validate()
        
        # 创建流程实例
        output_dir = Path(args.output_dir) if args.output_dir else config.OUTPUT_DIR
        pipeline = ModbusPipeline(
            output_dir=output_dir,
            controller_name=args.controller
        )
        
        if args.batch:
            # 批量处理模式
            pdf_dir = Path(args.pdf_path)
            if not pdf_dir.is_dir():
                raise ValueError(f"批量处理模式下，路径必须是目录: {pdf_dir}")
            
            pdf_files = list(pdf_dir.glob("*.pdf"))
            if not pdf_files:
                logger.warning(f"目录中没有找到PDF文件: {pdf_dir}")
                return
            
            logger.info(f"找到 {len(pdf_files)} 个PDF文件")
            pipeline.process_batch(pdf_files, output_dir, parse_pdf=args.parse_pdf)
        else:
            # 单文件处理模式
            pdf_path = Path(args.pdf_path)
            output_csv_path = Path(args.output) if args.output else None
            
            pipeline.process(pdf_path, output_csv_path, parse_pdf=args.parse_pdf)
        
        logger.info("程序执行完成！")
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        raise


if __name__ == "__main__":
    main()
