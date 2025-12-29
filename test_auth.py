"""测试鉴权功能"""

import json
import sys
from pathlib import Path
from app import ModbusGradioApp

# 设置Windows控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_auth():
    """测试鉴权功能"""
    print("=" * 60)
    print("测试Gradio鉴权功能")
    print("=" * 60)
    
    # 创建应用实例
    app = ModbusGradioApp()
    
    # 测试1: 检查配置加载
    print("\n[测试1] 检查鉴权配置加载")
    print(f"鉴权状态: {'启用' if app.auth_config.get('enabled') else '禁用'}")
    print(f"用户数量: {len(app.auth_config.get('users', {}))}")
    print(f"用户列表: {list(app.auth_config.get('users', {}).keys())}")
    
    # 测试2: 测试正确的凭证
    print("\n[测试2] 测试正确的凭证")
    test_cases = [
        ("admin", "admin123", True),
        ("user1", "password123", True),
        ("admin", "wrong_password", False),
        ("nonexistent", "password", False),
    ]
    
    for username, password, expected in test_cases:
        result = app._validate_credentials(username, password)
        status = "✅ 通过" if result == expected else "❌ 失败"
        print(f"{status} - 用户: {username}, 密码: {password}, 预期: {expected}, 实际: {result}")
    
    # 测试3: 测试动态添加用户
    print("\n[测试3] 测试动态添加用户")
    auth_config_path = Path("config/auth.json")
    
    # 读取当前配置
    with open(auth_config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 添加新用户
    config['users']['test_user'] = 'test_password'
    
    # 写入配置文件
    with open(auth_config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("已添加新用户: test_user")
    
    # 测试新用户（应该自动重载配置）
    result = app._validate_credentials("test_user", "test_password")
    print(f"{'✅ 通过' if result else '❌ 失败'} - 新用户登录测试: {result}")
    
    # 清理：删除测试用户
    with open(auth_config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if 'test_user' in config['users']:
        del config['users']['test_user']
        with open(auth_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("已清理测试用户")
    
    # 测试4: 测试禁用鉴权
    print("\n[测试4] 测试禁用鉴权")
    with open(auth_config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    original_enabled = config['enabled']
    config['enabled'] = False
    
    with open(auth_config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # 任意凭证都应该通过
    result = app._validate_credentials("any_user", "any_password")
    print(f"{'✅ 通过' if result else '❌ 失败'} - 禁用鉴权后，任意凭证应该通过: {result}")
    
    # 恢复原始配置
    config['enabled'] = original_enabled
    with open(auth_config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("已恢复原始配置")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    print("\n💡 提示:")
    print("1. 配置文件位置: config/auth.json")
    print("2. 默认用户: admin / admin123")
    print("3. 修改配置后无需重启应用")
    print("4. 查看详细说明: config/AUTH_README.md")


if __name__ == "__main__":
    test_auth()

