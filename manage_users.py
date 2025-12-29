"""用户管理工具 - 方便管理鉴权用户"""

import json
import sys
from pathlib import Path
from typing import Dict

# 设置Windows控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class UserManager:
    """用户管理器"""
    
    def __init__(self, config_path: str = "config/auth.json"):
        """初始化用户管理器"""
        self.config_path = Path(config_path)
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """确保配置文件存在"""
        if not self.config_path.exists():
            print(f"⚠️  配置文件不存在，创建默认配置: {self.config_path}")
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            default_config = {
                "enabled": True,
                "users": {
                    "admin": "admin123"
                },
                "description": "鉴权配置文件 - 可以动态添加用户，无需重启应用"
            }
            self._save_config(default_config)
    
    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
            return {"enabled": True, "users": {}}
    
    def _save_config(self, config: Dict):
        """保存配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    
    def list_users(self):
        """列出所有用户"""
        config = self._load_config()
        users = config.get("users", {})
        enabled = config.get("enabled", False)
        
        print("\n" + "=" * 60)
        print("📋 用户列表")
        print("=" * 60)
        print(f"鉴权状态: {'✅ 启用' if enabled else '❌ 禁用'}")
        print(f"用户数量: {len(users)}")
        print("-" * 60)
        
        if users:
            print(f"{'序号':<6} {'用户名':<20} {'密码':<30}")
            print("-" * 60)
            for idx, (username, password) in enumerate(users.items(), 1):
                # 隐藏部分密码
                masked_password = password[:2] + "*" * (len(password) - 2) if len(password) > 2 else "**"
                print(f"{idx:<6} {username:<20} {masked_password:<30}")
        else:
            print("暂无用户")
        
        print("=" * 60 + "\n")
    
    def add_user(self, username: str, password: str):
        """添加用户"""
        config = self._load_config()
        
        if username in config.get("users", {}):
            print(f"⚠️  用户 '{username}' 已存在，是否覆盖？(y/n): ", end="")
            choice = input().strip().lower()
            if choice != 'y':
                print("❌ 操作已取消")
                return
        
        config.setdefault("users", {})[username] = password
        self._save_config(config)
        print(f"✅ 用户 '{username}' 添加成功")
    
    def remove_user(self, username: str):
        """删除用户"""
        config = self._load_config()
        users = config.get("users", {})
        
        if username not in users:
            print(f"❌ 用户 '{username}' 不存在")
            return
        
        del users[username]
        self._save_config(config)
        print(f"✅ 用户 '{username}' 已删除")
    
    def change_password(self, username: str, new_password: str):
        """修改密码"""
        config = self._load_config()
        users = config.get("users", {})
        
        if username not in users:
            print(f"❌ 用户 '{username}' 不存在")
            return
        
        users[username] = new_password
        self._save_config(config)
        print(f"✅ 用户 '{username}' 的密码已修改")
    
    def enable_auth(self):
        """启用鉴权"""
        config = self._load_config()
        config["enabled"] = True
        self._save_config(config)
        print("✅ 鉴权已启用")
    
    def disable_auth(self):
        """禁用鉴权"""
        config = self._load_config()
        config["enabled"] = False
        self._save_config(config)
        print("⚠️  鉴权已禁用")
    
    def show_status(self):
        """显示鉴权状态"""
        config = self._load_config()
        enabled = config.get("enabled", False)
        users_count = len(config.get("users", {}))
        
        print("\n" + "=" * 60)
        print("📊 鉴权状态")
        print("=" * 60)
        print(f"配置文件: {self.config_path}")
        print(f"鉴权状态: {'✅ 启用' if enabled else '❌ 禁用'}")
        print(f"用户数量: {users_count}")
        print("=" * 60 + "\n")


def print_menu():
    """打印菜单"""
    print("\n" + "=" * 60)
    print("🔐 Modbus应用 - 用户管理工具")
    print("=" * 60)
    print("1. 查看所有用户")
    print("2. 添加用户")
    print("3. 删除用户")
    print("4. 修改密码")
    print("5. 启用鉴权")
    print("6. 禁用鉴权")
    print("7. 查看鉴权状态")
    print("0. 退出")
    print("=" * 60)


def main():
    """主函数"""
    manager = UserManager()
    
    while True:
        print_menu()
        choice = input("\n请选择操作 (0-7): ").strip()
        
        if choice == "1":
            manager.list_users()
        
        elif choice == "2":
            username = input("请输入用户名: ").strip()
            if not username:
                print("❌ 用户名不能为空")
                continue
            
            password = input("请输入密码: ").strip()
            if not password:
                print("❌ 密码不能为空")
                continue
            
            manager.add_user(username, password)
        
        elif choice == "3":
            manager.list_users()
            username = input("请输入要删除的用户名: ").strip()
            if not username:
                print("❌ 用户名不能为空")
                continue
            
            confirm = input(f"确认删除用户 '{username}'? (y/n): ").strip().lower()
            if confirm == 'y':
                manager.remove_user(username)
            else:
                print("❌ 操作已取消")
        
        elif choice == "4":
            manager.list_users()
            username = input("请输入用户名: ").strip()
            if not username:
                print("❌ 用户名不能为空")
                continue
            
            new_password = input("请输入新密码: ").strip()
            if not new_password:
                print("❌ 密码不能为空")
                continue
            
            manager.change_password(username, new_password)
        
        elif choice == "5":
            manager.enable_auth()
        
        elif choice == "6":
            confirm = input("确认禁用鉴权? (y/n): ").strip().lower()
            if confirm == 'y':
                manager.disable_auth()
            else:
                print("❌ 操作已取消")
        
        elif choice == "7":
            manager.show_status()
        
        elif choice == "0":
            print("\n👋 再见！")
            break
        
        else:
            print("❌ 无效的选择，请重新输入")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

