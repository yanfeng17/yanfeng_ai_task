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
- ⚡ **三层智能处理** - 第一层快速意图识别（50-200ms）+ AI 理解 + 深度对话
- 🎚️ **响应模式配置** - 友好模式/静音模式/简单确认，个性化体验
- 📝 **AI 任务生成数据** - 生成文本、结构化 JSON 数据
- 🖼️ **图像生成** - 使用 ModelScope 图像模型生成图片
- 👁️ **图像识别** - 支持视觉模型识别图片内容
- 📊 **结构化输出** - 支持 JSON Schema 格式化响应
- 🔄 **多模态支持** - 文本 + 图像混合输入

## 🎯 支持的模型

### 内置预设模型

#### 文本对话模型
- **Qwen/Qwen2.5-72B-Instruct** ⭐ 推荐
  - 最强大的对话模型
  - 最佳 Function Calling 支持
  - 适合设备控制和复杂任务

- **Qwen/Qwen3-32B**
  - 支持推理（Reasoning）功能
  - 适合复杂逻辑推理任务
  - 查看 [QWEN3_MODELS_GUIDE.md](QWEN3_MODELS_GUIDE.md) 了解详情

#### 视觉语言模型
- **Qwen/Qwen3-VL-235B-A22B-Instruct** ⭐ 推荐
  - 最新视觉语言模型
  - 支持图像识别和理解
  - 支持多模态输入（文本 + 图像）
  - ⚠️ **注意**：VL 模型的 Function Calling 支持不如纯文本模型

#### 图像生成模型
- **Qwen/Qwen-Image** ⭐ 推荐
  - Qwen 官方图像生成模型
  - 中文提示词支持良好
  - 异步任务处理（自动轮询）

- **Qwen/Qwen-Image-Edit** ✨ 新增
  - 专业图像编辑模型
  - 支持本地图像编辑
  - 支持风格转换、场景改变、物体编辑等

### 自定义模型支持 🎨

除了内置预设模型，您还可以使用 **任何 ModelScope 平台支持的模型**：

**如何使用自定义模型**：
1. 进入配置界面：设置 → 设备与服务 → Yanfeng AI Task
2. 在 **"Custom Chat Model"** 或 **"Custom Image Model"** 字段输入完整的模型 ID
3. 例如：`Qwen/QwQ-32B-Preview`、`Qwen/Qwen2.5-14B-Instruct` 等

**注意事项**：
- ⚠️ 自定义模型需要在 ModelScope 平台支持 Chat Completions API
- ⚠️ 某些模型可能需要特殊参数（如 Qwen3/QwQ 系列）
- ⚠️ Function Calling 功能依赖模型支持
- 💡 推荐使用纯文本模型进行设备控制

**参考资源**：
- [ModelScope 模型库](https://modelscope.cn/models)
- [Qwen3 模型使用指南](QWEN3_MODELS_GUIDE.md)
- [自定义模型功能说明](CUSTOM_MODEL_FEATURE.md)

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

## 🎯 三层智能处理机制

Yanfeng AI Task 采用创新的三层处理架构，结合快速响应和深度理解：

### 第一层：快速意图识别（50-200ms）⚡

**特点**：
- 基于关键词匹配的快速检测
- 不调用 LLM，极速响应
- 适合简单的设备控制命令

**支持的命令**：
```
✅ "打开客厅灯"          → 50-200ms 快速执行
✅ "关闭卧室空调"        → 50-200ms 快速执行
✅ "请帮我开启风扇"      → 50-200ms 快速执行
✅ "把台灯打开"          → 50-200ms 快速执行
```

**工作原理**：
1. 检测控制关键词（打开、关闭、启动、停止等）
2. 提取设备名称（通过 friendly_name、entity_id、alias 匹配）
3. 直接调用 Home Assistant 服务
4. 根据配置返回响应

### 第二/三层：AI 理解与深度对话（1-3秒）🤖

**特点**：
- 使用 LLM 进行语义理解
- 支持复杂任务和工具调用
- 智能上下文对话

**支持的场景**：
```
⚡ "把空调调到26度"       → AI 理解 + 工具调用
⚡ "关闭所有窗帘"         → AI 理解 + 批量操作
⚡ "我感觉有点热"         → AI 理解意图 + 建议
⚡ "今天天气怎么样"       → 深度对话
```

### 响应模式配置 🎚️

根据个人喜好选择第一层的响应方式：

#### 1️⃣ 友好模式（推荐）
```
用户："帮我关闭台灯"
系统："已关闭台灯"（有 friendly_name 时）
      或 *提示音*（无 friendly_name 时）
```

**特点**：
- 智能判断，有名称时说话，无名称时静音
- 用户体验好，反馈清晰
- **默认模式** ✅

#### 2️⃣ 静音模式
```
用户："帮我关闭台灯"
系统：*提示音*（无语音）
```

**特点**：
- 完全模仿 HAOS 内置意图
- 极简主义，只播放音效
- 适合追求极致简洁的用户

#### 3️⃣ 简单确认
```
用户："帮我关闭台灯"
系统："完成"
```

**特点**：
- 简短明确的文字反馈
- 不依赖设备名称
- 快速确认操作成功

### 性能对比

| 处理层级 | 响应时间 | 适用场景 | 是否调用 LLM |
|---------|---------|---------|------------|
| **第一层** | 50-200ms | 简单设备控制 | ❌ 否 |
| **第二/三层** | 1-3秒 | 复杂任务、对话 | ✅ 是 |

**效率提升**：
- 简单命令响应速度提升 **5-15倍**
- 减少 LLM API 调用，降低成本
- 保持复杂任务的完整 AI 能力

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

#### 3.1 基础文生图

```yaml
action: ai_task.generate_image
data:
  prompt: 一只可爱的小猫在花园里玩耍
  entity_id: ai_task.yanfeng_ai_task
```

#### 3.2 本地图像编辑（新功能） ✨

支持上传本地图像进行图像编辑：

**使用 Qwen-Image 模型（推荐文生图）**：
```yaml
action: ai_task.generate_image
data:
  prompt: 一只可爱的小猫在花园里玩耍
  entity_id: ai_task.yanfeng_ai_task
```

**使用 Qwen-Image-Edit 进行图像编辑**：
```yaml
action: ai_task.generate_image
data:
  prompt: 将图片转换为吉卜力工作室风格
  attachments:
    - media_content_id: media-source://image_upload/your_image_id
      mime_type: image/jpeg
  entity_id: ai_task.yanfeng_ai_task
```

**如何选择模型**：
1. **文生图**（从无到有）：使用 `Qwen/Qwen-Image`
2. **图像编辑**：使用 `Qwen/Qwen-Image-Edit` ⭐ 推荐

**在配置界面中选择模型**：
```
设置 → 设备与服务 → Yanfeng AI Task → 配置 → 图像模型
```
然后选择或输入相应的模型 ID

**工作原理**：
1. 自动上传本地图像到 ModelScope 服务
2. 获得公开 URL
3. 使用选定的编辑模型进行处理
4. 返回编辑后的图像

**支持的编辑操作**：
- 风格转换（吉卜力风格、油画风格、卡通风格等）
- 场景改变（室内改户外、白天改夜晚等）
- 物体编辑（添加或移除物体）
- 属性修改（改变颜色、材质、表情等）
- 文字添加
- 图像增强（清晰度、色彩等）

**例子**：
```yaml
# 转换风格
prompt: "将此图片转换为水彩画风格"

# 改变场景
prompt: "把这个室内场景改为户外春天环境"

# 修改属性
prompt: "把这个人的头发改成蓝色"

# 添加元素
prompt: "给图片中的人物添加一顶帽子"

# 物体移除
prompt: "移除图片中背景的电线杆"
```

**注意**：
- 首次使用时会自动上传文件到 ModelScope（可能需要几秒钟）
- 需要确保 Home Assistant 能访问图像文件
- 支持的图像格式：JPEG、PNG、WEBP
- 编辑模型需要输入图像，不能用于纯文生图

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

### 基础配置

| 选项 | 描述 | 默认值 | 范围 |
|------|------|--------|------|
| API Key | ModelScope API Token | 必填 | - |
| 对话模型 | 用于对话的模型 | Qwen/Qwen2.5-72B-Instruct | 见支持的模型 |
| 温度 | 控制回答的随机性 | 0.7 | 0.0 - 2.0 |
| Top P | 核采样参数 | 0.9 | 0.0 - 1.0 |
| 最大令牌数 | 单次回答的最大长度 | 2048 | 1 - 8192 |
| 提示词 | 系统提示词 | 中文优化提示词 | 自定义文本 |

### 响应模式配置（第一层快速响应）

| 模式 | 描述 | 适用场景 |
|------|------|---------|
| **友好模式**（默认）| 有 friendly_name 时说话，否则静音 | 推荐给大多数用户 |
| **静音模式** | 总是静音，只播放提示音 | 追求极简体验 |
| **简单确认** | 总是返回"完成" | 需要明确反馈 |

**配置位置**：
```
设置 → 设备与服务 → Yanfeng AI Task → 配置 → 响应模式
```

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

### 问题5：第一层意图识别不工作
**症状**：简单命令也很慢（>1秒）
**解决方案**：
- 检查命令是否包含控制关键词（打开、关闭等）
- 查看日志确认是否匹配到第一层
- 确认设备的 `friendly_name` 是否正确
- 尝试使用更简单的命令格式

**日志示例**：
```
# 成功匹配第一层
DEBUG: 🔍 Layer 1: Detected potential service call: 打开客厅灯
INFO: ✅ Layer 1: Service call matched - executing light.turn_on
DEBUG: Layer 1: Executed successfully in <200ms

# 未匹配第一层，转到 AI 处理
DEBUG: ⚠️ Layer 1: Not a service call, proceeding to Layer 2/3 (AI processing)
```

### 问题6：响应模式配置不生效
**症状**：修改响应模式后无变化
**解决方案**：
- 重启 Home Assistant
- 检查配置是否保存成功
- 查看日志确认使用的模式
- 清除浏览器缓存

### 问题7：图像生成/编辑失败 ⚠️（新增）
**症状**：收到错误 "Error generating image: ModelScope Image API error: 500"
**原因**：本地图像文件需要先上传到 ModelScope API
**解决方案**：
- 确保使用支持图像编辑的模型（如 Qwen/Qwen-Image）
- 检查图像文件格式是否支持（JPEG、PNG、WEBP）
- 检查 ModelScope API 是否正常工作
- 查看日志中是否看到 "Uploaded local file to ModelScope" 消息

**日志示例（成功）**：
```
DEBUG: Uploaded local file to ModelScope, using URL: https://...
DEBUG: Submitting ModelScope image task to v1/images/generations
```

**日志示例（失败）**：
```
ERROR: Failed to upload local image file: [error message]
ERROR: ModelScope Image API error: 500
```

### 问题8：图像上传缓慢
**症状**：图像编辑请求需要很长时间
**原因**：首次上传文件到 ModelScope 服务需要时间
**解决方案**：
- 这是正常的，首次上传通常需要 2-5 秒
- 缩小图像尺寸以加快上传速度
- 确保网络连接稳定

### 启用调试日志

在 `configuration.yaml` 中添加：

```yaml
logger:
  default: info
  logs:
    custom_components.yanfeng_ai_task: debug
    custom_components.yanfeng_ai_task.conversation: debug  # 第一层调试
    homeassistant.components.conversation: debug
    homeassistant.components.ai_task: debug
```

重启后查看日志：
```bash
tail -f /config/home-assistant.log | grep yanfeng
```

## 📊 性能优化

### 利用三层处理机制

**最佳实践**：
```
# ✅ 推荐：简单明确的命令（第一层处理）
"打开客厅灯"          → 50-200ms
"关闭卧室空调"        → 50-200ms

# ⚡ 可优化：可以简化的命令
"帮我把客厅的那个灯打开" → 可简化为 "打开客厅灯"
"能不能关一下空调"      → 可简化为 "关闭空调"

# 🤖 适合 AI：需要理解的命令
"我有点热"            → AI 理解意图
"晚安"                → AI 执行晚安场景
```

**优化建议**：
1. 为设备设置清晰的 `friendly_name`（如"客厅灯"而非"light_1"）
2. 使用简单直接的命令格式
3. 复杂任务交给 AI 处理，不强求第一层匹配

### 选择合适的模型

**根据任务类型选择**：
- **设备控制与对话**: Qwen/Qwen2.5-72B-Instruct ⭐ (最佳 Function Calling)
- **复杂推理任务**: Qwen/Qwen3-32B（支持思考模式）
- **视觉任务**: Qwen/Qwen3-VL-235B-A22B-Instruct

**自定义模型示例**：
- `Qwen/Qwen2.5-32B-Instruct` - 中等规模，性能平衡
- `Qwen/Qwen2.5-14B-Instruct` - 较小规模，响应快
- `Qwen/Qwen2.5-7B-Instruct` - 最小规模，极速响应
- `Qwen/QwQ-32B-Preview` - 推理增强模型

**注意**：使用自定义模型时，请在配置界面的 "Custom Chat Model" 字段输入完整的模型 ID。

### 调整参数
- **降低 temperature** (0.3-0.5): 更准确、一致的回答
- **提高 temperature** (0.8-1.0): 更创造性的回答
- **减少 max_tokens**: 更快的响应速度

### 响应模式选择
- **家庭用户**: 友好模式（默认）- 清晰友好
- **极简主义**: 静音模式 - 快速简洁
- **移动端**: 简单确认 - 明确反馈

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
- [智谱AI集成](https://github.com/knoop7/zhipuai) - 三层架构设计灵感来源

## 📞 联系作者或打赏感谢
<p align="center">
  <img src="https://github.com/user-attachments/assets/c1c5a7c8-1643-4ec8-a5a6-f76da3b90fc2" width="250">
  <img src="https://github.com/user-attachments/assets/873ff78e-b04e-4f89-9bb8-fa5fccadc775" width="250">
  <img src="https://github.com/user-attachments/assets/a3d7534a-77b8-407a-a559-1d9699cb23bc" width="250">
</p>

<p align="center">
  Made with ❤️ by Yanfeng | Powered by ModelScope
</p>
