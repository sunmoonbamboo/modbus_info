"""配置管理模块"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """配置类"""
    
    # API配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "google/gemini-2.5-pro")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    
    # 项目路径
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    OUTPUT_DIR = DATA_DIR / "output"
    SRC_DIR = DATA_DIR / "src"
    
    # 配置文件路径
    DEV_MAPPING_FILE = PROJECT_ROOT / "config" / "dev_mapping.json"
    EXTRACT_PROMPT_FILE = PROJECT_ROOT / "config" / "modbus_extract.md"
    DEMO_CSV_FILE = DATA_DIR / "demo.csv"
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 未设置，请在 .env 文件中配置")
        
        if not cls.DEV_MAPPING_FILE.exists():
            raise FileNotFoundError(f"设备映射文件不存在: {cls.DEV_MAPPING_FILE}")
        
        if not cls.EXTRACT_PROMPT_FILE.exists():
            raise FileNotFoundError(f"提示词文件不存在: {cls.EXTRACT_PROMPT_FILE}")
        
        return True


# 创建配置实例
config = Config()

