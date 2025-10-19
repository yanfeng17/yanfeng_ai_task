# 图像编辑功能测试指南

## 测试准备

1. **上传测试图片**
   - 在 Home Assistant 中上传一张测试图片
   - 记录图片的 `media_content_id`

2. **配置图像编辑模型**
   ```
   设置 → 设备与服务 → Yanfeng AI Task → 配置
   图像模型：选择 Qwen/Qwen-Image-Edit
   ```

## 测试用例 1：基础图像编辑

```yaml
action: ai_task.generate_image
data:
  prompt: 将图片转换为卡通风格
  attachments:
    - media_content_id: media-source://image_upload/your_image_id
      mime_type: image/jpeg
  entity_id: ai_task.yanfeng_ai_task
```

### 预期结果
- 日志中应该看到：
  ```
  DEBUG: Found image attachment for editing: /config/media/upload_xxx
  DEBUG: Generated image URL from attachment: http://homeassistant.local:8123/media/local/xxx.jpg
  INFO: Extracted image URL from prompt: http://...
  DEBUG: Using image model: Qwen/Qwen-Image-Edit
  ```
- 返回编辑后的图像

## 测试用例 2：URL 提取测试

```yaml
action: ai_task.generate_image
data:
  prompt: 将这张图片 https://example.com/image.jpg 转为黑白风格
  entity_id: ai_task.yanfeng_ai_task
```

### 预期结果
- 应该从 prompt 中提取出 URL
- 日志显示：`INFO: Extracted image URL from prompt: https://example.com/image.jpg`

## 检查调试日志

启用详细日志：

```yaml
logger:
  default: info
  logs:
    custom_components.yanfeng_ai_task: debug
    custom_components.yanfeng_ai_task.ai_task: debug
```

查看日志：
```bash
tail -f /config/home-assistant.log | grep -E "(Generated image URL|image_url|Image API)"
```

## 可能的问题

### 问题 1：URL 无法访问
**症状**：ModelScope API 返回无法下载图片的错误

**排查**：
1. 在浏览器中直接访问生成的 URL，确认是否能下载图片
2. 检查 HA 的 `internal_url` 配置是否正确
3. 确认 HA 实例是否可从外网访问（ModelScope 服务器需要能访问这个 URL）

### 问题 2：路径转换失败
**症状**：日志显示 "Failed to generate HTTP URL from attachment path"

**排查**：
1. 检查 attachment.path 的实际值
2. 确认文件是否存在于 `/config/media/` 目录
3. 查看完整的错误堆栈

### 问题 3：ModelScope API 错误
**症状**：API 返回 500 或其他错误

**排查**：
1. 检查 API Key 是否有效
2. 确认模型名称是否正确
3. 查看 ModelScope API 返回的详细错误信息

## 成功标志

✅ 日志中看到 HTTP URL 成功生成
✅ ModelScope API 返回任务 ID
✅ 任务状态变为 SUCCEED
✅ 返回编辑后的图像 URL
✅ 图像数据成功下载并返回给用户

## 调试命令

```bash
# 查看所有图像相关日志
grep -i "image" /config/home-assistant.log | tail -50

# 查看 URL 生成过程
grep "Generated image URL" /config/home-assistant.log

# 查看 API 调用
grep "ModelScope Image API" /config/home-assistant.log
```
