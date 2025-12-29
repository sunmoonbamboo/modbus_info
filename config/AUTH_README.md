# Gradio 鉴权配置说明

## 概述

本应用支持基于配置文件的简单鉴权功能，可以动态添加用户而无需重启应用。

## 配置文件

配置文件位置：`config/auth.json`

### 配置格式

```json
{
  "enabled": true,
  "users": {
    "用户名1": "密码1",
    "用户名2": "密码2"
  },
  "description": "鉴权配置文件 - 可以动态添加用户，无需重启应用"
}
```

### 配置说明

- **enabled**: `true` 启用鉴权，`false` 禁用鉴权
- **users**: 用户名和密码的键值对
- **description**: 配置说明（可选）

## 默认账号

默认配置了两个测试账号：

- 用户名: `admin`, 密码: `admin123`
- 用户名: `user1`, 密码: `password123`

⚠️ **安全提示**：在生产环境中，请务必修改默认密码！

## 如何使用

### 1. 启用鉴权

编辑 `config/auth.json`，将 `enabled` 设置为 `true`：

```json
{
  "enabled": true,
  "users": {
    "admin": "your_secure_password"
  }
}
```

### 2. 禁用鉴权

编辑 `config/auth.json`，将 `enabled` 设置为 `false`：

```json
{
  "enabled": false,
  "users": {}
}
```

### 3. 添加新用户

在 `users` 对象中添加新的用户名和密码：

```json
{
  "enabled": true,
  "users": {
    "admin": "admin123",
    "user1": "password123",
    "new_user": "new_password"  // 新增用户
  }
}
```

**重要**：添加新用户后**无需重启应用**，下次登录时会自动读取新配置。

### 4. 删除用户

从 `users` 对象中删除对应的用户名和密码即可：

```json
{
  "enabled": true,
  "users": {
    "admin": "admin123"
    // user1 已被删除
  }
}
```

### 5. 修改密码

直接修改对应用户的密码值：

```json
{
  "enabled": true,
  "users": {
    "admin": "new_secure_password"  // 密码已修改
  }
}
```

## 动态配置

本鉴权系统支持**动态重载配置**：

- 每次用户登录时，系统会自动重新读取 `config/auth.json`
- 修改配置文件后，下一次登录即可生效
- **无需重启应用**

## 工作原理

1. 用户访问应用时，Gradio会显示登录界面
2. 用户输入用户名和密码
3. 系统自动重新加载 `config/auth.json`（支持动态配置）
4. 验证用户凭证
5. 验证通过后进入应用

## 安全建议

1. **使用强密码**：密码应包含大小写字母、数字和特殊字符
2. **定期更换密码**：建议定期修改密码
3. **限制访问**：不要将配置文件提交到版本控制系统
4. **HTTPS部署**：生产环境建议使用HTTPS
5. **备份配置**：修改前备份配置文件

## 配置文件示例

### 示例1：单用户配置

```json
{
  "enabled": true,
  "users": {
    "admin": "SecurePassword123!"
  }
}
```

### 示例2：多用户配置

```json
{
  "enabled": true,
  "users": {
    "admin": "AdminPass123!",
    "developer": "DevPass456!",
    "viewer": "ViewPass789!"
  }
}
```

### 示例3：禁用鉴权

```json
{
  "enabled": false,
  "users": {}
}
```

## 故障排查

### 问题1：配置文件不存在

如果 `config/auth.json` 不存在，应用会自动禁用鉴权功能，并在日志中输出警告。

### 问题2：配置格式错误

如果配置文件格式错误（非有效JSON），应用会禁用鉴权功能，并在日志中输出错误信息。

### 问题3：无法登录

1. 检查配置文件中 `enabled` 是否为 `true`
2. 确认用户名和密码拼写正确（区分大小写）
3. 查看应用日志文件 `logs/gradio_app_*.log`

## 日志记录

鉴权相关的操作会记录在日志文件中：

- 配置加载状态
- 登录成功/失败记录
- 配置重载记录

日志文件位置：`logs/gradio_app_*.log`

---

📝 **注意**：本鉴权系统为基础鉴权功能，适用于内部使用或小规模部署。如需企业级安全方案，请考虑使用OAuth、LDAP等专业认证系统。

