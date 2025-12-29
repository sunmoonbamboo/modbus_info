# 鉴权功能快速开始

## 5分钟上手指南

### 步骤1：启动应用

```bash
# 启动Web界面
uv run python app.py
```

### 步骤2：登录

1. 浏览器访问：http://localhost:8860
2. 输入默认账号：
   - 用户名：`admin`
   - 密码：`admin123`
3. 点击登录

### 步骤3：修改默认密码（重要！）

```bash
# 运行用户管理工具
uv run python manage_users.py

# 选择：4. 修改密码
# 输入用户名：admin
# 输入新密码：your_secure_password
```

### 步骤4：添加新用户

方式1：使用管理工具（推荐）

```bash
uv run python manage_users.py
# 选择：2. 添加用户
```

方式2：直接编辑配置文件

编辑 `config/auth.json`：

```json
{
  "enabled": true,
  "users": {
    "admin": "new_password",
    "user1": "password123",
    "new_user": "another_password"
  }
}
```

保存后，下次登录时自动生效，**无需重启应用**！

---

## 常用操作

### 查看所有用户

```bash
uv run python manage_users.py
# 选择：1. 查看所有用户
```

### 删除用户

```bash
uv run python manage_users.py
# 选择：3. 删除用户
```

### 禁用鉴权

```bash
uv run python manage_users.py
# 选择：6. 禁用鉴权
```

或直接编辑 `config/auth.json`：

```json
{
  "enabled": false,
  "users": {}
}
```

### 启用鉴权

```bash
uv run python manage_users.py
# 选择：5. 启用鉴权
```

---

## 配置文件说明

### 位置

```
config/auth.json
```

### 格式

```json
{
  "enabled": true,           // 是否启用鉴权
  "users": {                 // 用户列表
    "username": "password"
  }
}
```

### 示例

```json
{
  "enabled": true,
  "users": {
    "admin": "SecurePass123!",
    "developer": "DevPass456!",
    "viewer": "ViewPass789!"
  },
  "description": "鉴权配置文件"
}
```

---

## 安全建议

### ✅ 推荐做法

1. **立即修改默认密码**
2. **使用强密码**：至少8位，包含大小写字母、数字和特殊字符
3. **定期更换密码**：建议每3-6个月更换一次
4. **限制用户数量**：只添加必要的用户
5. **启用HTTPS**：生产环境使用HTTPS

### ❌ 不推荐做法

1. 使用弱密码（如：123456、password）
2. 多人共享同一账号
3. 将配置文件提交到版本控制
4. 在公网暴露HTTP服务

---

## 故障排查

### 问题：无法登录

**检查清单：**
- [ ] 用户名和密码是否正确（区分大小写）
- [ ] `config/auth.json` 中 `enabled` 是否为 `true`
- [ ] 配置文件格式是否正确（有效的JSON）
- [ ] 查看日志：`logs/gradio_app_*.log`

### 问题：配置修改不生效

**解决方案：**
1. 确认配置文件已保存
2. 退出当前会话
3. 重新登录（配置会自动重新加载）

### 问题：忘记密码

**解决方案：**
直接编辑 `config/auth.json` 修改密码：

```json
{
  "enabled": true,
  "users": {
    "admin": "new_password_here"
  }
}
```

---

## 测试鉴权功能

运行测试脚本：

```bash
uv run python test_auth.py
```

测试内容：
- ✅ 配置加载
- ✅ 正确凭证验证
- ✅ 错误凭证拒绝
- ✅ 动态添加用户
- ✅ 禁用鉴权

---

## 进阶使用

### 脚本化管理

创建自定义脚本：

```python
import json
from pathlib import Path

def add_user(username, password):
    config_path = Path("config/auth.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['users'][username] = password
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"用户 {username} 已添加")

# 批量添加用户
users = {
    "user1": "pass1",
    "user2": "pass2",
    "user3": "pass3"
}

for username, password in users.items():
    add_user(username, password)
```

### 与其他系统集成

如需集成企业认证系统（LDAP、OAuth等），请参考：
- [Gradio官方文档](https://gradio.app/docs/)
- 使用反向代理（Nginx）配置认证
- 部署到支持SSO的平台

---

## 相关文档

- 📖 [完整鉴权指南](AUTHENTICATION_GUIDE.md)
- 📖 [配置说明](config/AUTH_README.md)
- 📖 [项目README](README.md)

---

## 获取帮助

如有问题：
1. 查看日志文件：`logs/gradio_app_*.log`
2. 运行测试脚本：`uv run python test_auth.py`
3. 查看详细文档：`AUTHENTICATION_GUIDE.md`

---

**🎉 恭喜！你已经掌握了鉴权功能的基本使用！**

