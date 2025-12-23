"""测试Web API解析功能"""

from pathlib import Path
from src.pdf_parser import PDFParser
from loguru import logger

def test_web_api_parse():
    """测试Web API解析PDF"""
    
    # 配置日志
    logger.add("logs/test_{time}.log", rotation="10 MB")
    
    # 选择一个测试PDF文件
    test_pdf = Path("data/src/11.pdf")
    
    if not test_pdf.exists():
        print(f"❌ 测试文件不存在: {test_pdf}")
        print("请确保 data/src/ 目录下有PDF文件")
        return
    
    print("=" * 60)
    print("测试Web API解析功能")
    print("=" * 60)
    
    # 测试Web API方式
    print("\n1️⃣ 测试Web API方式...")
    try:
        parser_web = PDFParser(use_web_api=True, api_url="http://127.0.0.1:8000")
        md_content_web = parser_web.parse(test_pdf)
        print(f"✅ Web API解析成功")
        print(f"   内容长度: {len(md_content_web)} 字符")
    except Exception as e:
        print(f"❌ Web API解析失败: {e}")
        print(f"   请确保Web API服务正在运行: uv run python -m mineru.server --host 0.0.0.0 --port 8000")
    
    # 测试本地方式
    print("\n2️⃣ 测试本地方式...")
    try:
        parser_local = PDFParser(use_web_api=False)
        md_content_local = parser_local.parse(test_pdf)
        print(f"✅ 本地解析成功")
        print(f"   内容长度: {len(md_content_local)} 字符")
    except Exception as e:
        print(f"❌ 本地解析失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_web_api_parse()

