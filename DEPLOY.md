# 自动化部署说明

## 📁 文件说明

本目录包含自动化部署脚本，用于快速将代码部署到 Home Assistant OS：

- **`deploy.bat`** - Windows 批处理脚本
- **`deploy.sh`** - Linux/Mac Bash 脚本

## 🚀 使用方法

### Windows 用户

双击运行 `deploy.bat` 或在命令行执行：

```cmd
deploy.bat
```

### Linux/Mac 用户

首次使用需要添加执行权限：

```bash
chmod +x deploy.sh
```

然后运行：

```bash
./deploy.sh
```

## 🔄 部署流程

脚本会自动执行以下步骤：

1. **删除远程旧文件夹** - `rm -rf /config/custom_components/yanfeng_ai_task`
2. **上传新文件** - 使用 SCP 传输整个项目文件夹
3. **重启 Home Assistant** - 执行 `ha core restart`
4. **查看日志** - 等待 30 秒后显示最新的相关日志

## ⚙️ 前提条件

确保已完成以下配置：

1. **SSH 连接**：能够通过 SSH 连接到 HAOS
   ```bash
   ssh root@192.168.31.66
   ```

2. **SSH 指纹**：首次连接时已接受 SSH 指纹（输入 yes）

3. **网络连接**：本地电脑与 HAOS 在同一局域网（192.168.31.x）

## 📋 部署后检查

部署完成后，建议检查：

1. **查看完整日志**：
   ```bash
   ssh root@192.168.31.66 "tail -f /config/home-assistant.log"
   ```

2. **检查集成状态**：
   - 打开 HA Web UI: `http://192.168.31.66:8123`
   - 进入：设置 → 设备与服务 → Yanfeng AI Task

3. **测试意图识别**：
   - "打开卧室空调"
   - "把空调调到26度"
   - "关闭所有窗帘"

4. **查看意图识别日志**：
   ```bash
   ssh root@192.168.31.66 "tail -f /config/home-assistant.log | grep '第一层'"
   ```

   应该看到类似输出：
   ```
   ✅ 第一层成功: 意图识别匹配 - ClimateSetTemperature
   ```

## 🔧 故障排除

### 问题 1：SSH 连接失败

**症状**：`Connection refused` 或 `Connection timeout`

**解决方案**：
1. 确认 HAOS 的 Terminal & SSH add-on 已启动
2. 检查 SSH 端口（默认 22）
3. 测试连接：`ssh root@192.168.31.66`

### 问题 2：权限不足

**症状**：`Permission denied`

**解决方案**：
1. 检查 SSH 用户权限
2. 尝试使用 `homeassistant` 用户：`ssh homeassistant@192.168.31.66`

### 问题 3：SCP 上传失败

**症状**：文件传输中断

**解决方案**：
1. 检查网络连接
2. 检查 HAOS 磁盘空间：`ssh root@192.168.31.66 "df -h"`
3. 手动删除旧文件：`ssh root@192.168.31.66 "rm -rf /config/custom_components/yanfeng_ai_task"`

### 问题 4：重启后仍有错误

**症状**：`Migration handler not found` 或其他启动错误

**解决方案**：
1. 查看完整日志定位问题
2. 检查 `manifest.json` 的 `config_entry_version` 字段
3. 检查 Python 语法是否有错误

## 💡 使用技巧

1. **快速重新部署**：每次修改代码后直接运行脚本
2. **查看实时日志**：使用 `tail -f` 实时监控日志
3. **SSH 别名**：在 `~/.ssh/config` 中配置别名简化命令

   ```
   Host ha
       HostName 192.168.31.66
       User root
       Port 22
   ```

   之后可以使用：`ssh ha`

4. **免密登录**：配置 SSH 密钥避免每次输入密码

   ```bash
   ssh-keygen -t ed25519
   ssh-copy-id root@192.168.31.66
   ```

## 🎯 效率对比

- **手动部署**：3-5 分钟（打开浏览器 → 选择文件 → 上传 → 重启）
- **自动部署**：30 秒（一键运行脚本）

---

Created by Claude Code for Yanfeng AI Task Integration
