# Home Assistant 自定义图标说明

## 图标使用方式

Home Assistant 集成可以通过以下几种方式显示图标：

### 方式1：使用 icons.json（当前使用）
当前项目已有 `icons.json` 文件，使用 Material Design Icons。

### 方式2：添加自定义 logo 图标

要使用你的自定义 logo，需要：

1. **创建 `www` 目录用于静态文件**
   ```
   /config/custom_components/yanfeng_ai_task/www/
   ```

2. **保存图标文件**
   - 建议格式：PNG（透明背景）或 SVG
   - 推荐尺寸：512x512 或 1024x1024
   - 文件名：`logo.png` 或 `icon.png`

3. **在集成中引用**
   通过 `manifest.json` 或实体属性设置图标

## 当前实现

你的集成已经在 `icons.json` 中配置了图标，使用 Material Design Icons。

## 添加自定义 logo 的步骤

### 步骤1：保存 logo 文件
将你的 logo 图片保存为：
- `/config/www/community/yanfeng_ai_task/logo.png`
- 或 `/config/custom_components/yanfeng_ai_task/logo.png`

### 步骤2：设置实体图标
在实体类中设置 `_attr_icon` 或 `_attr_entity_picture`：

```python
# 使用 entity_picture 显示自定义图片
_attr_entity_picture = "/local/community/yanfeng_ai_task/logo.png"

# 或继续使用 MDI 图标
_attr_icon = "mdi:robot"
```

### 步骤3：更新集成配置
确保在集成设置中能看到自定义图标。

## 推荐方案

对于你的科技感 logo，我建议：

1. **优化图片**：
   - 转换为 PNG 格式（透明背景）
   - 调整大小为 512x512 像素
   - 确保在深色和浅色主题下都清晰可见

2. **放置位置**：
   ```
   /config/www/yanfeng_ai_task/logo.png
   ```

3. **在代码中引用**：
   ```python
   _attr_entity_picture = "/local/yanfeng_ai_task/logo.png"
   ```

## 注意事项

- Home Assistant 的 `/config/www/` 目录会被映射到 `/local/` URL
- 图标文件不应该太大（建议 < 500KB）
- PNG 格式支持透明背景，在不同主题下显示效果更好
- SVG 格式文件更小，但可能需要额外配置

## 快速实现

我可以帮你：
1. 保存图片到正确位置
2. 更新实体代码以使用自定义图标
3. 测试显示效果

需要我现在帮你实现吗？
