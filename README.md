<p align="center">
  <img src="logo.png" alt="岩风 AI Task" width="300"/>
</p>

<h1 align="center">Yanfeng AI Task</h1>

<p align="center">
  <strong>基于 ModelScope 的 Home Assistant AI 集成</strong>
</p>

<p align="center">
  <a href="https://github.com/custom-components/hacs">
    <img src="https://img.shields.io/badge/HACS-Custom-orange.svg" alt="HACS Custom">
  </a>
  <img src="https://img.shields.io/badge/Home%20Assistant-2024.10+-blue.svg" alt="Home Assistant">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/ModelScope-API-green.svg" alt="ModelScope">
</p>

---

## ✨ 功能特性

- 🤖 **对话代理** - 支持中文和多语言自然语言对话
- 📝 **AI 任务生成数据** - 生成文本、结构化 JSON 数据
- 🖼️ **图像生成** - 使用 ModelScope 图像模型生成图片
- 👁️ **图像识别** - 支持视觉模型识别图片内容
- 📊 **结构化输出** - 支持 JSON Schema 格式化响应
- 🔄 **多模态支持** - 文本 + 图像混合输入

## 🎯 支持的模型

### 文本模型
- **Qwen/Qwen2.5-72B-Instruct** - 最强大的对话模型（推荐）
- **Qwen/Qwen2.5-32B-Instruct** - 高性能平衡模型
- **Qwen/Qwen2.5-14B-Instruct** - 中等规模模型
- **Qwen/Qwen2.5-7B-Instruct** - 快速响应模型

### 视觉模型
- **Qwen/Qwen3-VL-235B-A22B-Instruct** - 最新视觉语言模型（推荐）
- **Qwen/Qwen2-VL-72B-Instruct** - 高性能视觉模型

### 图像生成模型
- **Qwen/Qwen-Image** - Qwen 图像生成（推荐）
- **stable-diffusion-v1-5** - Stable Diffusion 1.5
- **stable-diffusion-xl-base-1-0** - SDXL 基础模型

## 📦 安装

### 方法1：通过 HACS（推荐）

1. 打开 HACS
2. 点击右上角菜单，选择 **"自定义存储库"**
3. 添加此存储库 URL: https://github.com/yanfeng17/yanfeng_ai_task
4. 搜索 **"Yanfeng AI Task"**
5. 点击 **安装**
6. 重启 Home Assistant

### 方法2：手动安装

1. 下载最新版本
2. 解压到 `custom_components/yanfeng_ai_task/`
3. 重启 Home Assistant

## ⚙️ 配置

### 第一步：获取 ModelScope API Key

1. 访问 [ModelScope](https://modelscope.cn/my/myaccesstoken)
2. 注册并登录账户
3. 创建 **API Token**
4. 确保账户有足够的额度，魔搭平台每天有2000点额度可以免费使用
<img width="1426" height="269" alt="img_v3_02r1_ff29e809-fba0-49de-8600-f3755c286a9g" src="https://github.com/user-attachments/assets/e2bc939c-2dcb-49df-ac20-090c2b53ac25" />


### 第二步：添加集成

1. 进入 Home Assistant **设置 > 设备与服务**
2. 点击 **"添加集成"**
3. 搜索 **"Yanfeng AI Task"**
4. 输入 **ModelScope API Key**
5. 选择模型和参数：
   - **对话模型**: Qwen/Qwen2.5-72B-Instruct（推荐）
   - **温度**: 0.7
   - **Max Tokens**: 2048
6. 完成配置

## 🚀 使用示例

### 1. 对话代理

在 **设置 > 语音助手** 中选择 **"Yanfeng AI Task"** 作为对话代理：

```
你: 你好
AI: 你好！有什么可以帮助你的吗？
```

### 2. AI Task 生成文本

```yaml
action: ai_task.generate_data
data:
  instructions: 写一首关于春天的诗
  entity_id: ai_task.yanfeng_ai_task
response_variable: poem
```

### 3. 图像生成

```yaml
action: ai_task.generate_image
data:
  prompt: 一只可爱的小猫在花园里玩耍
  entity_id: ai_task.yanfeng_ai_task
```

### 4. 图像识别

```yaml
action: ai_task.generate_data
data:
  instructions: 描述这张图片中的内容
  attachments:
    media_content_id: media-source://camera/camera.video
    media_content_type: image/jpeg
  entity_id: ai_task.yanfeng_ai_task
response_variable: description
```

### 5. 结构化输出

```yaml
action: ai_task.generate_data
data:
  instructions: 分析人物特征
  attachments:
    media_content_id: media-source://camera/camera.video
  structure:
    name:
      description: 人物名称
    age:
      description: 估计年龄
    clothing:
      description: 服装描述
  entity_id: ai_task.yanfeng_ai_task
response_variable: analysis
```

**返回示例**：
```json
{
  "name": "未知",
  "age": "约25岁",
  "clothing": "蓝色T恤和牛仔裤"
}
```

### 6. 在自动化中使用

```yaml
automation:
  - alias: "门铃识别来访者"
    trigger:
      platform: state
      entity_id: binary_sensor.doorbell
      to: "on"
    action:
      - action: ai_task.generate_data
        data:
          instructions: 描述门口的人物特征
          attachments:
            media_content_id: media-source://camera/doorbell
            media_content_type: image/jpeg
          structure:
            description:
              description: 人物描述
            count:
              description: 人数
          entity_id: ai_task.yanfeng_ai_task
        response_variable: visitor_info
      - action: notify.mobile_app
        data:
          message: "有访客：{{ visitor_info.data.description }}"
```

## 📋 配置选项

| 选项 | 描述 | 默认值 | 范围 |
|------|------|--------|------|
| API Key | ModelScope API Token | 必填 | - |
| 对话模型 | 用于对话的模型 | Qwen/Qwen2.5-72B-Instruct | 见支持的模型 |
| 温度 | 控制回答的随机性 | 0.7 | 0.0 - 2.0 |
| Top P | 核采样参数 | 0.9 | 0.0 - 1.0 |
| 最大令牌数 | 单次回答的最大长度 | 2048 | 1 - 8192 |
| 提示词 | 系统提示词 | "You are a helpful assistant." | 自定义文本 |

## 🔧 高级功能

### 多模态输入

支持文本 + 图像混合输入，适用于：
- 图像描述
- 视觉问答
- 场景理解
- 物体识别

### 结构化输出

使用 `structure` 参数定义 JSON Schema，模型会返回符合格式的结构化数据：

```yaml
structure:
  field_name:
    description: 字段描述
    selector:
      text: null
```

### 流式响应

部分模型支持流式响应（逐字返回），提供更好的用户体验。

## 🐛 故障排除

### 问题1：API Key 无效
**症状**：无法连接到 ModelScope API
**解决方案**：
- 检查 API Key 是否正确
- 确认账户状态正常
- 验证 API 额度是否充足

### 问题2：对话无响应
**症状**：发送消息后没有回复
**解决方案**：
- 检查网络连接
- 查看日志中的错误信息
- 确认选择的模型可用

### 问题3：图像识别不工作
**症状**：无法识别图像内容
**解决方案**：
- 确认使用支持视觉的模型
- 检查图像附件路径是否正确
- 查看日志确认图像已添加

### 问题4：结构化输出格式错误
**症状**：返回的不是 JSON 格式
**解决方案**：
- 检查 `structure` 参数定义是否正确
- 使用更详细的字段描述
- 尝试使用更强大的模型

### 启用调试日志

在 `configuration.yaml` 中添加：

```yaml
logger:
  default: info
  logs:
    custom_components.yanfeng_ai_task: debug
    homeassistant.components.conversation: debug
    homeassistant.components.ai_task: debug
```

重启后查看日志：
```bash
tail -f /config/home-assistant.log | grep yanfeng
```

## 📊 性能优化

### 选择合适的模型
- **快速响应**: Qwen2.5-7B-Instruct
- **平衡**: Qwen2.5-32B-Instruct
- **最佳质量**: Qwen2.5-72B-Instruct
- **视觉任务**: Qwen3-VL-235B-A22B-Instruct

### 调整参数
- **降低 temperature** (0.3-0.5): 更准确、一致的回答
- **提高 temperature** (0.8-1.0): 更创造性的回答
- **减少 max_tokens**: 更快的响应速度

## 📚 更多资源

- [Home Assistant 官方文档](https://www.home-assistant.io/)
- [ModelScope 平台](https://modelscope.cn/)
- [Qwen 模型文档](https://github.com/QwenLM)

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Home Assistant](https://www.home-assistant.io/) - 智能家居平台
- [ModelScope](https://modelscope.cn/) - AI 模型服务
- [Qwen Team](https://github.com/QwenLM) - 强大的语言模型

## 📞 联系作者或打赏感谢
<p align="center">
  <img src="https://github.com/user-attachments/assets/c1c5a7c8-1643-4ec8-a5a6-f76da3b90fc2" width="250">
  <img src="https://github.com/user-attachments/assets/873ff78e-b04e-4f89-9bb8-fa5fccadc775" width="250">
  <img src="https://github.com/user-attachments/assets/a3d7534a-77b8-407a-a559-1d9699cb23bc" width="250">
</p>

<p align="center">
  Made with ❤️ by Yanfeng | Powered by ModelScope
</p>
