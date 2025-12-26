"""测试MinerU官方API解析功能"""

import os
from pathlib import Path
from src.pdf_parser import PDFParser
from loguru import logger

# 配置日志
logger.add("logs/test_official_api_{time}.log", rotation="10 MB")


def test_official_api_parsing():
    """测试官方API解析功能"""
    
    # 从环境变量读取配置
    api_token = os.getenv("MINERU_API_TOKEN", "")
    file_server_url = os.getenv("FILE_SERVER_URL", "")
    
    if not api_token:
        logger.warning("未设置MINERU_API_TOKEN环境变量，请在.env文件中配置")
        logger.info("测试将使用手动输入的Token（如果有）")
        api_token = input("请输入您的MinerU API Token（按Enter跳过）: ").strip()
        if not api_token:
            logger.error("未提供API Token，无法测试")
            return
    
    if not file_server_url:
        logger.warning("未设置FILE_SERVER_URL环境变量")
        file_server_url = input("请输入文件服务器URL（按Enter跳过）: ").strip()
    
    # 选择测试PDF文件
    test_pdf_dir = Path("data/src")
    if not test_pdf_dir.exists():
        logger.error(f"测试目录不存在: {test_pdf_dir}")
        return
    
    pdf_files = list(test_pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"未找到测试PDF文件: {test_pdf_dir}")
        return
    
    logger.info(f"找到 {len(pdf_files)} 个PDF文件:")
    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"  {i}. {pdf_file.name}")
    
    # 使用第一个PDF文件进行测试
    test_pdf = pdf_files[0]
    logger.info(f"使用测试文件: {test_pdf.name}")
    
    # 如果有文件服务器URL，构造完整URL
    if file_server_url:
        # 假设文件已经在服务器上
        pdf_url = f"{file_server_url}/{test_pdf.name}"
        logger.info(f"文件URL: {pdf_url}")
    else:
        logger.warning("未提供文件服务器URL，将使用本地路径")
        logger.warning("注意：官方API需要可访问的URL，本地路径可能无法工作")
        pdf_url = str(test_pdf)
    
    try:
        # 创建解析器实例
        logger.info("=" * 60)
        logger.info("开始测试MinerU官方API解析")
        logger.info("=" * 60)
        
        parser = PDFParser(
            output_dir=Path("data/output"),
            parse_mode="official_api",
            official_api_token=api_token,
            file_server_url=file_server_url
        )
        
        # 执行解析
        logger.info("正在解析PDF...")
        markdown_content = parser.parse(test_pdf)
        
        logger.info("=" * 60)
        logger.info("✅ 解析成功！")
        logger.info("=" * 60)
        logger.info(f"Markdown内容长度: {len(markdown_content)} 字符")
        logger.info(f"前500字符预览:\n{markdown_content[:500]}")
        
        # 保存测试结果
        output_file = Path("data/output") / f"test_official_api_{test_pdf.stem}.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(markdown_content, encoding='utf-8')
        logger.info(f"测试结果已保存至: {output_file}")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)
        return
    
    logger.info("\n测试完成！")


def test_local_api_parsing():
    """测试本地Web API解析功能（对比测试）"""
    
    logger.info("\n" + "=" * 60)
    logger.info("开始测试本地Web API解析（对比）")
    logger.info("=" * 60)
    
    test_pdf_dir = Path("data/src")
    pdf_files = list(test_pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.error(f"未找到测试PDF文件: {test_pdf_dir}")
        return
    
    test_pdf = pdf_files[0]
    
    try:
        parser = PDFParser(
            output_dir=Path("data/output"),
            parse_mode="local_api",
            api_url="http://127.0.0.1:8000"
        )
        
        logger.info("正在解析PDF...")
        markdown_content = parser.parse(test_pdf)
        
        logger.info("=" * 60)
        logger.info("✅ 本地API解析成功！")
        logger.info("=" * 60)
        logger.info(f"Markdown内容长度: {len(markdown_content)} 字符")
        
    except Exception as e:
        logger.error(f"❌ 本地API测试失败: {e}")
        logger.info("提示: 请确保本地Web API服务正在运行")
        logger.info("启动命令: uv run python -m mineru.server --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    print("=" * 60)
    print("MinerU官方API解析功能测试")
    print("=" * 60)
    print()
    print("请选择测试模式:")
    print("1. 测试官方API解析")
    print("2. 测试本地Web API解析（对比）")
    print("3. 同时测试两种模式")
    print()
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        test_official_api_parsing()
    elif choice == "2":
        test_local_api_parsing()
    elif choice == "3":
        test_official_api_parsing()
        test_local_api_parsing()
    else:
        print("无效的选择")

