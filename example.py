"""使用示例"""

from pathlib import Path
from loguru import logger

from src.pipeline import ModbusPipeline
from src.config import config


def example_single_file():
    """示例1：处理单个PDF文件"""
    logger.info("=" * 60)
    logger.info("示例1：处理单个PDF文件")
    logger.info("=" * 60)
    
    # 指定PDF文件路径
    pdf_path = config.SRC_DIR / "EK400模块螺杆式冷水（热泵）机Modbus客户通信协议-大金VRV.pdf"
    
    if not pdf_path.exists():
        logger.warning(f"示例PDF文件不存在: {pdf_path}")
        logger.info("请将PDF文件放入 data/src/ 目录")
        return
    
    # 创建流程实例
    pipeline = ModbusPipeline()
    
    # 处理文件
    output_csv = pipeline.process(pdf_path)
    
    logger.info(f"\n✓ 处理完成！输出文件: {output_csv}")


def example_custom_output():
    """示例2：自定义输出路径"""
    logger.info("\n" + "=" * 60)
    logger.info("示例2：自定义输出路径")
    logger.info("=" * 60)
    
    pdf_path = config.SRC_DIR / "EK400模块螺杆式冷水（热泵）机Modbus客户通信协议-大金VRV.pdf"
    
    if not pdf_path.exists():
        logger.warning(f"示例PDF文件不存在: {pdf_path}")
        return
    
    # 指定输出路径
    output_path = Path("custom_output/my_result.csv")
    
    pipeline = ModbusPipeline()
    pipeline.process(pdf_path, output_csv_path=output_path)
    
    logger.info(f"\n✓ 文件已保存到自定义路径: {output_path}")


def example_batch_processing():
    """示例3：批量处理"""
    logger.info("\n" + "=" * 60)
    logger.info("示例3：批量处理多个PDF文件")
    logger.info("=" * 60)
    
    # 获取所有PDF文件
    pdf_files = list(config.SRC_DIR.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"没有找到PDF文件: {config.SRC_DIR}")
        logger.info("请将PDF文件放入 data/src/ 目录")
        return
    
    logger.info(f"找到 {len(pdf_files)} 个PDF文件")
    
    # 批量处理
    pipeline = ModbusPipeline()
    results = pipeline.process_batch(pdf_files)
    
    logger.info(f"\n✓ 批量处理完成！成功处理 {len(results)} 个文件")


def example_custom_controller():
    """示例4：自定义控制器名称"""
    logger.info("\n" + "=" * 60)
    logger.info("示例4：自定义控制器名称")
    logger.info("=" * 60)
    
    pdf_path = config.SRC_DIR / "EK400模块螺杆式冷水（热泵）机Modbus客户通信协议-大金VRV.pdf"
    
    if not pdf_path.exists():
        logger.warning(f"示例PDF文件不存在: {pdf_path}")
        return
    
    # 使用自定义控制器名称（默认为 default）
    pipeline = ModbusPipeline(controller_name="my_controller")
    output_csv = pipeline.process(pdf_path)
    
    logger.info(f"\n✓ 处理完成！CSV中的ControllerName已设置为: my_controller")


def example_step_by_step():
    """示例5：分步处理（更细粒度的控制）"""
    logger.info("\n" + "=" * 60)
    logger.info("示例5：分步处理")
    logger.info("=" * 60)
    
    from src.pdf_parser import PDFParser
    from src.ai_extractor import AIExtractor
    from src.csv_exporter import CSVExporter
    
    pdf_path = config.SRC_DIR / "EK400模块螺杆式冷水（热泵）机Modbus客户通信协议-大金VRV.pdf"
    
    if not pdf_path.exists():
        logger.warning(f"示例PDF文件不存在: {pdf_path}")
        return
    
    # 步骤1：解析PDF
    logger.info("\n步骤1：解析PDF...")
    parser = PDFParser()
    markdown_content = parser.parse(pdf_path)
    logger.info(f"✓ PDF解析完成，文本长度: {len(markdown_content)} 字符")
    
    # 步骤2：提取点位信息
    logger.info("\n步骤2：AI提取点位信息...")
    extractor = AIExtractor()
    data_points = extractor.extract(markdown_content)
    logger.info(f"✓ 提取了 {len(data_points)} 个点位")
    
    # 步骤3：导出CSV
    logger.info("\n步骤3：导出CSV...")
    exporter = CSVExporter()
    output_path = config.OUTPUT_DIR / f"{pdf_path.stem}_manual.csv"
    exporter.export(data_points, output_path)
    logger.info(f"✓ CSV已保存: {output_path}")


def main():
    """运行所有示例"""
    try:
        # 验证配置
        config.validate()
        
        # 运行示例
        # 注意：某些示例需要真实的PDF文件和API密钥
        
        # 运行单个示例
        example_single_file()
        
        # 取消注释以运行其他示例
        # example_custom_output()
        # example_batch_processing()
        # example_custom_controller()
        # example_step_by_step()
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}")
        logger.info("\n提示：")
        logger.info("1. 确保已配置 .env 文件并填入 OpenRouter API 密钥")
        logger.info("2. 确保 data/src/ 目录下有PDF文件")
        logger.info("3. 确保已安装所有依赖: uv sync")
        logger.info("4. 确保 OpenRouter 账户有足够额度")


if __name__ == "__main__":
    main()

