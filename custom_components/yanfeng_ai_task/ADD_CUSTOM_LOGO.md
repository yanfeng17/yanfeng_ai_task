# 🎨 添加自定义 Logo 到 Yanfeng AI Task

## 已完成的修改 ✅

代码已更新，现在支持显示你的自定义"岩风"logo！

## 📋 需要你完成的步骤

### 步骤1：准备图片文件

你需要优化你的 logo 图片：

**推荐规格**：
- 格式：PNG（支持透明背景）
- 尺寸：512x512 像素（或 1024x1024）
- 文件大小：< 500KB
- 背景：透明或适配深色主题

**图片处理建议**：
1. 使用图片编辑工具（如 Photoshop、GIMP）
2. 裁剪为正方形
3. 调整大小到 512x512
4. 导出为 PNG 格式
5. 确保文字和边框清晰可见

### 步骤2：上传到 Home Assistant

#### 方法A：使用文件编辑器（推荐）

1. 在 Home Assistant 中，进入：
   - 设置 > 加载项 > File Editor
   - 或使用 SSH 访问

2. 创建目录结构：
   ```
   /config/www/yanfeng_ai_task/
   ```

3. 上传你的 logo 图片，命名为：
   ```
   /config/www/yanfeng_ai_task/logo.png
   ```

#### 方法B：使用 SSH/SFTP

```bash
# SSH 到 Home Assistant
ssh root@homeassistant.local

# 创建目录
mkdir -p /config/www/yanfeng_ai_task

# 上传文件（使用 SFTP 或 scp）
scp logo.png root@homeassistant.local:/config/www/yanfeng_ai_task/
```

### 步骤3：重启集成

1. 进入 Home Assistant：
   - 设置 > 设备与服务
   - 找到 "Yanfeng AI Task"
   - 点击"重新加载"或重启 Home Assistant

2. 或重启 Home Assistant：
   ```bash
   ha core restart
   ```

## 📂 文件路径说明

```
/config/
└── www/                          # Home Assistant 静态文件目录
    └── yanfeng_ai_task/         # 你的集成目录
        └── logo.png             # 你的 logo 文件
```

**URL 映射**：
- 文件路径：`/config/www/yanfeng_ai_task/logo.png`
- 访问 URL：`/local/yanfeng_ai_task/logo.png`
- 代码引用：`self._attr_entity_picture = "/local/yanfeng_ai_task/logo.png"`

## ✅ 验证图标显示

重启后，检查以下位置：

### 1. 实体卡片
- 打开 Home Assistant 仪表板
- 查看 `ai_task.yanfeng_ai_task` 实体
- 应该显示你的自定义 logo

### 2. 设备页面
- 设置 > 设备与服务 > 设备
- 找到 "Yanfeng AI Task"
- 应该显示你的 logo

### 3. 集成页面
- 设置 > 设备与服务
- "Yanfeng AI Task" 集成卡片

## 🎨 显示效果

你的"岩风"logo 将显示在：
- ✅ 所有实体卡片上
- ✅ 对话代理选择界面
- ✅ AI Task 实体
- ✅ 设备信息页面

## 🔧 代码修改说明

### entity.py 修改（已完成）

```python
class YanfengAIBaseEntity:
    def __init__(self, entry, subentry=None):
        # ... 其他初始化代码 ...

        # 设置自定义 logo
        self._attr_entity_picture = "/local/yanfeng_ai_task/logo.png"
```

这个设置会应用到所有继承自 `YanfengAIBaseEntity` 的实体，包括：
- `YanfengAIConversationEntity` (对话代理)
- `YanfengAITaskEntity` (AI Task)

## 📝 备选方案

如果你不想使用 entity_picture，也可以继续使用 Material Design Icons：

### 保持使用 MDI 图标

如果你想移除自定义图片，只需删除这行代码：
```python
# 删除或注释掉
# self._attr_entity_picture = "/local/yanfeng_ai_task/logo.png"
```

集成会自动使用 `icons.json` 中定义的 MDI 图标。

### 当前 icons.json 配置

```json
{
  "entity": {
    "conversation": {
      "agent": {
        "default": "mdi:robot"
      }
    }
  }
}
```

## 🎯 推荐的图片优化工具

### 在线工具
- **TinyPNG** (https://tinypng.com/) - 压缩 PNG
- **Squoosh** (https://squoosh.app/) - 图片优化
- **Remove.bg** (https://remove.bg/) - 移除背景

### 本地工具
- **GIMP** (免费) - 图片编辑
- **Photoshop** - 专业编辑
- **Inkscape** (免费) - 矢量图编辑（如果你有 SVG）

## 💡 提示

1. **测试不同主题**：在深色和浅色主题下都检查 logo 显示效果
2. **文件权限**：确保 logo.png 文件可被 Home Assistant 读取
3. **缓存清除**：如果更新图片后没变化，尝试清除浏览器缓存（Ctrl+F5）
4. **文件大小**：保持图片文件小于 500KB 以提高加载速度

## 🐛 故障排除

### 问题1：图片不显示
**检查**：
- 文件路径是否正确：`/config/www/yanfeng_ai_task/logo.png`
- 文件名是否正确（区分大小写）
- 文件权限是否正确
- 重启 Home Assistant

### 问题2：显示默认图标
**检查**：
- 代码是否正确更新
- 集成是否已重新加载
- 浏览器缓存是否已清除

### 问题3：图片显示模糊
**解决**：
- 使用更高分辨率的图片（1024x1024）
- 确保是 PNG 格式，不是 JPG
- 检查原图质量

## 📊 完成清单

- [x] 代码已更新（entity.py）
- [ ] 优化 logo 图片（512x512 PNG）
- [ ] 上传到 `/config/www/yanfeng_ai_task/logo.png`
- [ ] 重启 Home Assistant
- [ ] 验证显示效果

---

**状态**: 代码已更新 ✅
**下一步**: 上传 logo 图片到 Home Assistant
**预期效果**: 你的科技感"岩风"logo 将显示在所有实体上

完成这些步骤后，你的集成将拥有独特的品牌标识！🎨✨
