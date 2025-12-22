"""CSV导出模块 - 将提取的点位信息导出为CSV格式"""

import csv
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from src.config import config


class CSVExporter:
    """CSV导出器"""
    
    # CSV文件的标准列（从demo.csv获取）
    STANDARD_COLUMNS = [
        'MeasuringPointName', 'ControllerName', 'GroupName', 'UploadType', 
        'DeadZoneType', 'DeadZonePercent', 'DataType', 'ArrayIndex', 
        'EnableBit', 'BitIndex', 'reverseBit', 'Address', 'Decimal', 'Len', 
        'CodeType', 'ReadWrite', 'Unit', 'Description', 'Transform Type', 
        'MaxValue', 'MinValue', 'MaxScale', 'MinScale', 'Gain', 'Offset', 
        'startBit', 'endBit', 'Pt', 'Ct', 'Mapping_table', 'TransDecimal', 
        'bitMap', 'msecSample', 'storageLwTSDB', 'DataEndianReverse', 
        'ReadOffset', 'ReadLength', 'WriteOffset', 'WriteLength', 
        'DataParseMethod', 'BitId', 'pollCycle', 'EnableRequestCount', 
        'RequestCount', 'byteOrder'
    ]
    
    # 默认值映射（从demo.csv中观察到的模式）
    DEFAULT_VALUES = {
        'MeasuringPointName': '',  # 测量点名称（必需字段）
        'ControllerName': 'default',
        'GroupName': 'default',
        'UploadType': 'periodic',
        'DeadZoneType': '',
        'DeadZonePercent': '',
        'DataType': 'BIT',
        'ArrayIndex': '',
        'EnableBit': '',
        'BitIndex': '',
        'reverseBit': '0',
        'Address': '',  # Modbus地址（必需字段）
        'Decimal': '',
        'Len': '',
        'CodeType': '',
        'ReadWrite': 'ro',
        'Unit': '',
        'Description': '',
        'Transform Type': 'none',
        'MaxValue': '',
        'MinValue': '',
        'MaxScale': '',
        'MinScale': '',
        'Gain': '',
        'Offset': '',
        'startBit': '',
        'endBit': '',
        'Pt': '',
        'Ct': '',
        'Mapping_table': '',
        'TransDecimal': '0',
        'bitMap': '0',
        'msecSample': '0',
        'storageLwTSDB': '',
        'DataEndianReverse': '',
        'ReadOffset': '',
        'ReadLength': '',
        'WriteOffset': '',
        'WriteLength': '',
        'DataParseMethod': '',
        'BitId': '',
        'pollCycle': '0',
        'EnableRequestCount': '',
        'RequestCount': '',
        'byteOrder': ''
    }
    
    def __init__(self, controller_name: str = "default", address_offset: int = 0):
        """
        初始化CSV导出器
        
        Args:
            controller_name: 控制器名称，默认为'default'
            address_offset: 地址偏移量，默认为0，范围[0, 10)
        """
        self.controller_name = controller_name
        self.address_offset = address_offset
        self.default_values = self.DEFAULT_VALUES.copy()
        self.default_values['ControllerName'] = controller_name
    
    def export(
        self,
        data_points: List[Dict],
        output_path: Path,
        encoding: str = 'utf-8-sig'
    ) -> None:
        """
        导出点位信息到CSV文件
        
        Args:
            data_points: 点位信息列表
            output_path: 输出CSV文件路径
            encoding: 文件编码，默认为utf-8-sig（带BOM，Excel兼容）
        """
        if not data_points:
            logger.warning("没有数据可导出")
            return
        
        logger.info(f"开始导出 {len(data_points)} 个点位到CSV文件...")
        
        # 创建输出目录
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 标准化数据
        standardized_data = self._standardize_data(data_points)
        
        # 使用pandas导出
        df = pd.DataFrame(standardized_data)
        
        # 确保列顺序与标准列一致
        df = df.reindex(columns=self.STANDARD_COLUMNS, fill_value='')
        
        # 导出到CSV
        df.to_csv(output_path, index=False, encoding=encoding)
        
        logger.info(f"CSV文件导出成功: {output_path}")
        logger.info(f"导出数据行数: {len(df)}")
    
    def _standardize_data(self, data_points: List[Dict]) -> List[Dict]:
        """
        标准化数据，确保所有必需的列都存在
        
        Args:
            data_points: 原始点位信息列表
            
        Returns:
            标准化后的数据列表
        """
        standardized = []
        
        for point in data_points:
            
            if not point.get('exist', False):
                continue
            
            # 创建一个包含所有默认值的新记录
            record = self.default_values.copy()
            
            # 更新从AI提取的字段
            for key, value in point.items():
                if key in record:
                    # 确保值不是None
                    record[key] = value if value is not None else ''
            
            # 特殊处理：强制使用指定的值
            record['GroupName'] = 'default'
            record['ControllerName'] = self.controller_name  # 确保使用用户指定的控制器名称
            
            # 重新构造 MeasuringPointName: {ControllerName}_{原MeasuringPointName}
            original_name = record.get('MeasuringPointName', '')
            if original_name:
                record['MeasuringPointName'] = f"{self.controller_name}_{original_name}"
            
            # 如果BitIndex存在但为空字符串，根据需要设置默认值
            if record['BitIndex'] == '':
                record['BitIndex'] = ''
            
            # 格式化Address并应用偏移量
            if record.get('Address'):
                record['Address'] = self._format_address(record['Address'])
            
            standardized.append(record)
        
        return standardized
    
    def _format_address(self, address: str) -> str:
        """
        格式化地址并应用偏移量
        
        Args:
            address: 原始地址（如：3X0001, 4X0120）
            
        Returns:
            格式化并应用偏移后的地址
        """
        if not address:
            return ''
        
        address = str(address).strip()
        
        # 分离小数点部分（如：3X0000.0 -> address="3X0000", decimal_suffix=".0"）
        decimal_suffix = ''
        if '.' in address:
            parts = address.split('.', 1)
            address = parts[0]
            decimal_suffix = '.' + parts[1]
        
        # 解析地址格式：功能码 + 地址
        # 支持格式：3X0001, 4X0120
        import re
        
        # 匹配 Modbus 格式：3X0001, 4X0120
        modbus_pattern = r'^([0-9])X([0-9]+)$'
        match = re.match(modbus_pattern, address, re.IGNORECASE)
        
        if match:
            # Modbus 格式
            function_code = match.group(1)
            addr_str = match.group(2)
            
            try:
                # 转换为整数（十进制），应用偏移
                addr_int = int(addr_str)
                addr_int += self.address_offset
                
                # 格式化输出，保持原有位数，并拼接回小数部分
                addr_width = len(addr_str)
                return f"{function_code}X{addr_int:0{addr_width}d}{decimal_suffix}"
            except ValueError:
                return address + decimal_suffix
        
        # 无法解析的格式，返回原值
        return address + decimal_suffix
    
    def export_with_validation(
        self,
        data_points: List[Dict],
        output_path: Path,
        validate_required_fields: bool = True
    ) -> Dict[str, any]:
        """
        导出数据并进行验证
        
        Args:
            data_points: 点位信息列表
            output_path: 输出文件路径
            validate_required_fields: 是否验证必需字段
            
        Returns:
            导出结果信息
        """
        result = {
            'success': False,
            'exported_count': 0,
            'skipped_count': 0,
            'errors': []
        }
        
        if validate_required_fields:
            valid_points = []
            for i, point in enumerate(data_points):
                if self._validate_point(point):
                    valid_points.append(point)
                else:
                    result['skipped_count'] += 1
                    result['errors'].append(f"第 {i+1} 个点位缺少必需字段")
            
            data_points = valid_points
        
        try:
            self.export(data_points, output_path)
            result['success'] = True
            result['exported_count'] = len(data_points)
        except Exception as e:
            result['errors'].append(str(e))
            logger.error(f"导出失败: {e}")
        
        return result
    
    def _validate_point(self, point: Dict) -> bool:
        """
        验证点位数据是否包含必需字段
        
        Args:
            point: 点位数据
            
        Returns:
            是否有效
        """
        required_fields = ['MeasuringPointName', 'Address']
        
        for field in required_fields:
            if field not in point or not point[field]:
                logger.warning(f"点位缺少必需字段: {field}")
                return False
        
        return True


def export_to_csv(
    data_points: List[Dict],
    output_path: Path,
    controller_name: str = "default"
) -> None:
    """
    便捷函数：导出点位信息到CSV
    
    Args:
        data_points: 点位信息列表
        output_path: 输出文件路径
        controller_name: 控制器名称，默认为'default'
    """
    exporter = CSVExporter(controller_name=controller_name)
    exporter.export(data_points, output_path)

