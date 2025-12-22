"""AI提取模块 - 使用Gemini API提取Modbus点位信息"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import json_repair
from loguru import logger
from openai import OpenAI

from src.config import config


class AIExtractor:
    """使用AI大模型提取Modbus点位信息"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        初始化AI提取器
        
        Args:
            api_key: API密钥，默认从配置读取
            model: 模型名称，默认从配置读取
            base_url: API基础URL，默认从配置读取
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        self.model = model or config.MODEL_NAME
        self.base_url = base_url or config.OPENAI_BASE_URL
        
        if not self.api_key:
            raise ValueError("API密钥未设置，请在.env文件中配置OPENAI_API_KEY")
        
        # 初始化OpenAI客户端（通过OpenRouter访问Gemini）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 加载设备映射配置
        self.dev_mapping = self._load_dev_mapping()
        
        # 加载提示词
        self.system_prompt = self._load_system_prompt()
    
    def _load_dev_mapping(self) -> Dict:
        """加载设备映射配置"""
        try:
            with open(config.DEV_MAPPING_FILE, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            logger.info(f"设备映射配置加载成功: {config.DEV_MAPPING_FILE}")
            return mapping
        except Exception as e:
            logger.error(f"加载设备映射配置失败: {e}")
            raise
    
    def _load_system_prompt(self) -> str:
        """加载系统提示词"""
        try:
            with open(config.EXTRACT_PROMPT_FILE, 'r', encoding='utf-8') as f:
                prompt = f.read().strip()
            logger.info(f"系统提示词加载成功: {config.EXTRACT_PROMPT_FILE}")
            return prompt
        except Exception as e:
            logger.error(f"加载系统提示词失败: {e}")
            raise
    
    def extract(
        self,
        markdown_content: str,
        temperature: float = 0.1,
        max_tokens: int = 8000
    ) -> List[Dict]:
        """
        从Markdown内容中提取Modbus点位信息
        
        Args:
            markdown_content: Markdown格式的协议内容
            temperature: 温度参数，控制输出随机性
            max_tokens: 最大token数
            
        Returns:
            提取的点位信息列表
        """
        logger.info("开始使用AI提取Modbus点位信息...")
        
        # 构建用户提示词
        user_prompt = self._build_user_prompt(markdown_content)
        
        try:
            # 调用API
            logger.info(f"调用模型: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 解析响应
            content = response.choices[0].message.content
            logger.info(f"模型响应长度: {len(content)} 字符")
            
            # 提取并解析JSON数据
            data_points = self._parse_response(content)
            logger.info(f"成功提取 {len(data_points)} 个点位信息")
            
            return data_points
            
        except Exception as e:
            logger.error(f"AI提取失败: {e}")
            raise
    
    def _build_user_prompt(self, markdown_content: str) -> str:
        """
        构建用户提示词
        
        Args:
            markdown_content: Markdown内容
            
        Returns:
            完整的用户提示词
        """
        # 构建数据描述
        data_description = "需要提取的数据字段说明：\n"
        for field_name, field_desc in self.dev_mapping.items():
            data_description += f"- {field_name}: {field_desc}\n"
        
        prompt = f"""{data_description}

请从以下Modbus协议文档中提取完整的点位信息，以JSON数组格式输出。每个点位包含上述所有字段。

协议文档内容：

{markdown_content}

请以JSON数组格式输出所有点位信息，格式如下：
```json
[
  {{
    "MeasuringPointName": "测量点名称",
    "thinking": "思考过程",
    "其它字段": "......"
  }},
  ...
]
```

注意：
1. 提取所有能找到的点位信息
2. 只输出JSON数组，不要有其他文字说明
"""
        return prompt
    
    def _parse_response(self, content: str) -> List[Dict]:
        """
        解析AI响应内容，使用 json_repair 处理格式不正确的 JSON
        
        Args:
            content: AI响应的文本内容
            
        Returns:
            解析后的点位信息列表
        """
        import re
        from json_repair import repair_json, loads
        
        # 尝试提取JSON代码块
        # 匹配 ```json ... ``` 或 ``` ... ```
        json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        if matches:
            json_str = matches[0].strip()
        else:
            # 如果没有代码块，尝试直接解析整个内容
            json_str = content.strip()
        
        try:
            # 首先尝试使用 json_repair 修复可能的 JSON 格式问题
            # repaired_json_str = repair_json(json_str)
            # data = json.loads(repaired_json_str)
            
            data = json_repair.loads(json_str)
            
            logger.debug("JSON 解析成功: \n" + json.dumps(data, ensure_ascii=False))
            
            # 确保返回的是列表
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                raise ValueError("返回的数据格式不正确，应该是JSON数组")
            
            return data
            
        except Exception as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"原始响应内容（前500字符）: {content[:500]}")
            logger.error(f"提取的JSON字符串（前500字符）: {json_str[:500]}")
            raise ValueError(f"AI响应的JSON格式无法解析: {e}")
    
    def extract_from_file(self, markdown_file: Path) -> List[Dict]:
        """
        从Markdown文件中提取点位信息
        
        Args:
            markdown_file: Markdown文件路径
            
        Returns:
            提取的点位信息列表
        """
        logger.info(f"从文件读取Markdown内容: {markdown_file}")
        markdown_content = markdown_file.read_text(encoding='utf-8')
        return self.extract(markdown_content)


def extract_modbus_points(markdown_content: str) -> List[Dict]:
    """
    便捷函数：从Markdown内容提取Modbus点位信息
    
    Args:
        markdown_content: Markdown内容
        
    Returns:
        点位信息列表
    """
    extractor = AIExtractor()
    return extractor.extract(markdown_content)

