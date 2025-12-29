# Gradio应用鉴权功能使用指南

## 功能概述

本应用已集成基于Gradio的简单鉴权功能，支持：

✅ **基于配置文件的用户管理**  
✅ **动态添加/删除用户，无需重启应用**  
✅ **启用/禁用鉴权开关**  
✅ **安全的登录验证**  

---

## 快速开始

### 1. 启用鉴权

编辑 `config/auth.json` 文件：

```json
{
  "enabled": true,
  "users": {
    "admin": "admin123",
    "user1": "password123"
  }
}
```

### 2. 启动应用

```bash
# 使用默认配置启动
uv run python app.py

# 或使用批处理文件
启动UI界面.bat

# 或指定端口
uv run python app.py --port 8860
```

### 3. 登录

访问应用时会看到登录界面，输入用户名和密码即可登录。

---

## 配置文件详解

### 配置文件位置

```
config/auth.json
```

### 配置结构

```json
{
  "enabled": true,              // 是否启用鉴权（true/false）
  "users": {                    // 用户列表
    "用户名1": "密码1",
    "用户名2": "密码2"
  },
  "description": "说明文字"     // 可选的说明
}
```

### 默认账号

应用预配置了两个测试账号：

| 用户名 | 密码 |
|--------|------|
| admin  | admin123 |
| user1  | password123 |

⚠️ **重要**：生产环境请务必修改默认密码！

---

## 用户管理

### 添加新用户

1. 打开 `config/auth.json`
2. 在 `users` 对象中添加新用户：

```json
{
  "enabled": true,
  "users": {
    "admin": "admin123",
    "user1": "password123",
    "new_user": "secure_password"  // 新增用户
  }
}
```

3. 保存文件
4. **无需重启应用**，下次登录时自动生效

### 删除用户

从 `users` 对象中删除对应的用户即可：

```json
{
  "enabled": true,
  "users": {
    "admin": "admin123"
    // user1 已被删除
  }
}
```

### 修改密码

直接修改对应用户的密码值：

```json
{
  "enabled": true,
  "users": {
    "admin": "new_secure_password_123!"  // 密码已修改
  }
}
```

### 禁用鉴权

将 `enabled` 设置为 `false`：

```json
{
  "enabled": false,
  "users": {}
}
```

---

## 动态配置特性

### 工作原理

- 每次用户登录时，系统会**自动重新读取** `config/auth.json`
- 配置修改后**立即生效**，无需重启应用
- 支持在应用运行期间动态添加/删除用户

### 使用场景

1. **临时授权**：快速添加临时用户，使用后删除
2. **密码重置**：直接修改配置文件重置密码
3. **批量管理**：通过脚本批量管理用户
4. **零停机**：在不中断服务的情况下管理用户

---

## 测试鉴权功能

运行测试脚本验证鉴权功能：

```bash
uv run python test_auth.py
```

测试内容包括：
- ✅ 配置文件加载
- ✅ 正确凭证验证
- ✅ 错误凭证拒绝
- ✅ 动态添加用户
- ✅ 禁用鉴权

---

## 安全建议

### 1. 密码强度

❌ 弱密码示例：
```
123456
password
admin
```

✅ 强密码示例：
```
Admin@2025!Secure
MyP@ssw0rd#2025
Secure!Pass123$
```

### 2. 定期更换密码

建议每3-6个月更换一次密码。

### 3. 配置文件安全

```bash
# 不要将配置文件提交到版本控制
echo "config/auth.json" >> .gitignore

# 限制文件访问权限（Linux/Mac）
chmod 600 config/auth.json
```

### 4. 使用HTTPS

生产环境建议使用反向代理（如Nginx）配置HTTPS：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. 日志监控

定期检查登录日志：

```bash
# 查看最近的登录记录
tail -f logs/gradio_app_*.log | grep "登录"
```

---

## 故障排查

### 问题1：无法登录

**症状**：输入正确的用户名密码仍然无法登录

**解决方案**：
1. 检查 `config/auth.json` 中 `enabled` 是否为 `true`
2. 确认用户名和密码拼写正确（区分大小写）
3. 检查配置文件格式是否正确（有效的JSON）
4. 查看日志文件：`logs/gradio_app_*.log`

### 问题2：配置文件不存在

**症状**：应用启动时提示配置文件不存在

**解决方案**：
```bash
# 创建配置文件
cat > config/auth.json << EOF
{
  "enabled": true,
  "users": {
    "admin": "admin123"
  }
}
EOF
```

### 问题3：配置修改不生效

**症状**：修改配置后仍使用旧配置

**原因**：配置在每次登录时重新加载，需要重新登录

**解决方案**：
1. 退出当前会话
2. 重新登录
3. 新配置会自动加载

### 问题4：JSON格式错误

**症状**：应用启动失败或鉴权被禁用

**解决方案**：
```bash
# 验证JSON格式
python -m json.tool config/auth.json

# 或使用在线工具
# https://jsonlint.com/
```

---

## 高级用法

### 1. 脚本化用户管理

创建用户管理脚本：

```python
import json
from pathlib import Path

def add_user(username, password):
    """添加用户"""
    config_path = Path("config/auth.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['users'][username] = password
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"用户 {username} 已添加")

def remove_user(username):
    """删除用户"""
    config_path = Path("config/auth.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if username in config['users']:
        del config['users'][username]
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"用户 {username} 已删除")
    else:
        print(f"用户 {username} 不存在")

# 使用示例
add_user("new_user", "secure_password")
remove_user("old_user")
```

### 2. 批量导入用户

```python
import json
from pathlib import Path

users_to_add = {
    "user1": "password1",
    "user2": "password2",
    "user3": "password3"
}

config_path = Path("config/auth.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

config['users'].update(users_to_add)

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f"已添加 {len(users_to_add)} 个用户")
```

### 3. 密码加密（可选增强）

如需更高安全性，可以使用密码哈希：

```python
import hashlib
import json
from pathlib import Path

def hash_password(password):
    """对密码进行SHA256哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

# 创建加密密码的用户
config_path = Path("config/auth.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

config['users']['secure_user'] = hash_password('my_secure_password')

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
```

注意：如使用密码哈希，需要同时修改 `app.py` 中的验证逻辑。

---

## 命令行参数

启动应用时可以指定端口和地址：

```bash
# 指定端口
uv run python app.py --port 8860

# 指定监听地址
uv run python app.py --host 0.0.0.0

# 同时指定
uv run python app.py --host 0.0.0.0 --port 8860
```

---

## 相关文件

- `config/auth.json` - 鉴权配置文件
- `config/AUTH_README.md` - 详细配置说明
- `test_auth.py` - 鉴权功能测试脚本
- `app.py` - 主应用文件（包含鉴权逻辑）

---

## 技术实现

### 核心方法

```python
def _validate_credentials(self, username: str, password: str) -> bool:
    """验证用户凭证"""
    # 每次验证时重新加载配置（支持动态配置）
    self._reload_auth_config()
    
    # 如果鉴权未启用，直接通过
    if not self.auth_config.get("enabled", False):
        return True
    
    # 验证用户名和密码
    users = self.auth_config.get("users", {})
    if username in users and users[username] == password:
        logger.info(f"用户登录成功: {username}")
        return True
    
    logger.warning(f"用户登录失败: {username}")
    return False
```

### Gradio集成

```python
def launch(self, **kwargs):
    """启动应用"""
    interface = self.create_interface()
    
    # 如果启用了鉴权，添加auth参数
    if self.auth_config.get("enabled", False):
        kwargs["auth"] = self._validate_credentials
        kwargs["auth_message"] = "请输入用户名和密码进行登录"
    
    interface.launch(**kwargs)
```

---

## 常见问题

### Q1: 忘记密码怎么办？

**A**: 直接编辑 `config/auth.json` 文件修改密码，无需重启应用。

### Q2: 可以设置多个管理员吗？

**A**: 可以，在 `users` 中添加多个用户即可，所有用户权限相同。

### Q3: 支持角色权限吗？

**A**: 当前版本不支持角色权限，所有登录用户权限相同。如需角色权限，建议使用企业级认证系统。

### Q4: 配置文件可以放在其他位置吗？

**A**: 可以，修改 `app.py` 中的 `self.auth_config_path` 路径即可。

### Q5: 如何集成LDAP/OAuth？

**A**: 当前版本为简单鉴权，如需企业级认证，建议：
- 使用反向代理（Nginx）配置认证
- 集成OAuth 2.0
- 使用LDAP认证
- 部署到支持SSO的平台

---

## 更新日志

### v1.0 (2025-12-29)

- ✅ 实现基于配置文件的鉴权
- ✅ 支持动态添加/删除用户
- ✅ 支持启用/禁用鉴权
- ✅ 添加登录日志记录
- ✅ 提供测试脚本

---

## 联系支持

如有问题或建议，请查看：
- 项目文档：`README.md`
- 配置说明：`config/AUTH_README.md`
- 测试脚本：`test_auth.py`

---

📝 **注意**：本鉴权系统适用于内部使用或小规模部署。生产环境建议使用企业级认证方案。

