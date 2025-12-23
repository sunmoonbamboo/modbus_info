"""安装验证脚本"""

import sys
from pathlib import Path
from loguru import logger


def check_python_version():
    """检查Python版本"""
    logger.info("检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 12:
        logger.info(f"✓ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        logger.error(f"✗ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        logger.error("  需要Python 3.12或更高版本")
        return False


def check_dependencies():
    """检查依赖包"""
    logger.info("\n检查依赖包...")
    
    required_packages = {
        'magic_pdf': 'magic-pdf',
        'loguru': 'loguru',
        'openai': 'openai',
        'dotenv': 'python-dotenv',
        'pandas': 'pandas',
    }
    
    all_ok = True
    for module_name, package_name in required_packages.items():
        try:
            if module_name == 'magic_pdf':
                import mineru
                logger.info(f"✓ {package_name} 已安装")
            elif module_name == 'dotenv':
                from dotenv import load_dotenv
                logger.info(f"✓ {package_name} 已安装")
            else:
                __import__(module_name)
                logger.info(f"✓ {package_name} 已安装")
        except ImportError:
            logger.error(f"✗ {package_name} 未安装")
            all_ok = False
    
    return all_ok


def check_project_structure():
    """检查项目结构"""
    logger.info("\n检查项目结构...")
    
    required_paths = {
        'src': '源代码目录',
        'tests': '测试目录',
        'data': '数据目录',
        'data/src': 'PDF输入目录',
        'dev_mapping.json': '字段映射配置',
        'modbus_extract.md': '提示词文件',
        'main.py': '主程序',
        'pyproject.toml': '项目配置',
    }
    
    all_ok = True
    for path_str, desc in required_paths.items():
        path = Path(path_str)
        if path.exists():
            logger.info(f"✓ {desc}: {path}")
        else:
            logger.error(f"✗ {desc} 不存在: {path}")
            all_ok = False
    
    return all_ok


def check_config_file():
    """检查配置文件"""
    logger.info("\n检查配置文件...")
    
    env_file = Path(".env")
    config_example = Path("config.example")
    
    if env_file.exists():
        logger.info(f"✓ 配置文件存在: {env_file}")
        
        # 检查是否配置了API密钥
        content = env_file.read_text()
        if "your_api_key_here" in content or "GEMINI_API_KEY=" not in content:
            logger.warning("⚠ 警告: API密钥可能未正确配置")
            logger.info("  请编辑 .env 文件并填入你的Gemini API密钥")
            return False
        else:
            logger.info("✓ API密钥已配置")
            return True
    else:
        logger.warning(f"⚠ 配置文件不存在: {env_file}")
        if config_example.exists():
            logger.info(f"  请复制 {config_example} 为 {env_file} 并配置API密钥")
        return False


def check_test_data():
    """检查测试数据"""
    logger.info("\n检查测试数据...")
    
    src_dir = Path("data/src")
    if not src_dir.exists():
        logger.warning("⚠ 测试数据目录不存在")
        return False
    
    pdf_files = list(src_dir.glob("*.pdf"))
    if pdf_files:
        logger.info(f"✓ 找到 {len(pdf_files)} 个PDF文件")
        for pdf in pdf_files:
            logger.info(f"  - {pdf.name}")
        return True
    else:
        logger.warning("⚠ 没有找到PDF文件")
        logger.info("  如需测试，请将PDF文件放入 data/src/ 目录")
        return False


def run_basic_tests():
    """运行基本测试"""
    logger.info("\n运行基本测试...")
    
    try:
        # 测试导入核心模块
        logger.info("测试导入核心模块...")
        from src.config import config
        from src.pdf_parser import PDFParser
        from src.ai_extractor import AIExtractor
        from src.csv_exporter import CSVExporter
        from src.pipeline import ModbusPipeline
        
        logger.info("✓ 所有核心模块导入成功")
        
        # 测试配置
        logger.info("\n测试配置加载...")
        assert config.PROJECT_ROOT.exists()
        assert config.POINT_METADATA_FILE.exists()
        logger.info("✓ 配置加载成功")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 测试失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("Modbus协议信息提取工具 - 安装验证")
    logger.info("=" * 60)
    
    results = {
        "Python版本": check_python_version(),
        "依赖包": check_dependencies(),
        "项目结构": check_project_structure(),
        "配置文件": check_config_file(),
        "测试数据": check_test_data(),
        "基本测试": run_basic_tests(),
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("验证结果汇总")
    logger.info("=" * 60)
    
    for check_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        logger.info(f"{check_name}: {status}")
    
    all_passed = all(results.values())
    
    logger.info("\n" + "=" * 60)
    if all_passed:
        logger.info("🎉 恭喜！所有检查都通过了！")
        logger.info("\n下一步：")
        logger.info("1. 将PDF文件放入 data/src/ 目录")
        logger.info("2. 运行: uv run python main.py data/src/your_file.pdf")
        logger.info("3. 查看输出文件: data/output/your_file.csv")
    else:
        logger.warning("⚠ 部分检查未通过，请根据上述提示进行修复")
        logger.info("\n常见解决方案：")
        logger.info("1. 运行 'uv sync' 安装依赖")
        logger.info("2. 复制 config.example 为 .env 并配置API密钥")
        logger.info("3. 查看 INSTALL.md 获取详细安装说明")
    
    logger.info("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

