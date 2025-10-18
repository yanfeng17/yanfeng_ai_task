# 自定义模型功能文档

## 📋 功能概述

Yanfeng AI Task 集成现在支持**自定义模型**功能，允许用户输入任意 ModelScope 平台上的模型名称，不受预定义模型列表的限制。

## ✨ 新增功能

### 1. 自定义聊天模型 (Custom Chat Model)

用户可以输入任意支持对话的模型名称，例如：
- `Qwen/Qwen2.5-110B-Instruct`
- `Qwen/Qwen2-72B-Instruct-AWQ`
- `Qwen/QwQ-32B-Preview`
- ModelScope 平台上的任何其他对话模型

### 2. 自定义图像模型 (Custom Image Model)

用户可以输入任意支持图像生成的模型名称，例如：
- `AI-ModelScope/flux-dev`
- `AI-ModelScope/sd3-medium`
- `damo/image-generation-v1`
- ModelScope 平台上的任何其他图像生成模型

## 🎯 使用方法

### 方法 1：通过 Home Assistant 界面配置

#### 初始配置时

1. 进入 **设置 > 设备与服务**
2. 点击 **添加集成**，搜索并选择 **Yanfeng AI Task**
3. 输入 API Key
4. 在 **Chat Model** 下拉菜单中选择一个预定义模型（作为备用）
5. 在 **Custom Chat Model** 文本框中输入您想使用的自定义模型名称
   - 例如：`Qwen/QwQ-32B-Preview`
6. （可选）在 **Custom Image Model** 文本框中输入自定义图像模型
7. 点击提交

#### 修改现有配置

1. 进入 **设置 > 设备与服务**
2. 找到 **Yanfeng AI Task** 集成
3. 点击子配置项（如 **Yanfeng AI Conversation** 或 **Yanfeng AI Task**）
4. 点击 **配置** 或 **选项**
5. 在表单中找到 **Custom Chat Model** 或 **Custom Image Model** 字段
6. 输入自定义模型名称
7. 点击提交

### 方法 2：直接编辑配置文件（不推荐）

编辑 `config/.storage/core.config_entries` 文件（需要重启）：

```json
{
  "subentries": {
    "xxx": {
      "data": {
        "chat_model": "Qwen/Qwen2.5-72B-Instruct",
        "custom_chat_model": "Qwen/QwQ-32B-Preview",
        "image_model": "Qwen/Qwen-Image",
        "custom_image_model": "AI-ModelScope/flux-dev"
      }
    }
  }
}
```

## ⚙️ 优先级规则

系统使用以下优先级选择模型：

```
自定义模型 (custom_chat_model/custom_image_model)
    ↓ 如果为空或未填写
预定义模型 (chat_model/image_model)
    ↓ 如果为空或未配置
默认推荐模型 (RECOMMENDED_CHAT_MODEL/RECOMMENDED_IMAGE_MODEL)
```

### 示例

**配置场景 1：**
```
Chat Model (下拉): Qwen/Qwen2.5-72B-Instruct
Custom Chat Model: [空]
→ 实际使用: Qwen/Qwen2.5-72B-Instruct
```

**配置场景 2：**
```
Chat Model (下拉): Qwen/Qwen2.5-32B-Instruct
Custom Chat Model: Qwen/QwQ-32B-Preview
→ 实际使用: Qwen/QwQ-32B-Preview (自定义优先)
```

**配置场景 3：**
```
Chat Model (下拉): [默认值]
Custom Chat Model: AI-ModelScope/my-custom-model
→ 实际使用: AI-ModelScope/my-custom-model
```

## 💡 使用场景

### 1. 测试新发布的模型

当 ModelScope 发布新模型时，无需等待集成更新，直接输入模型名称即可使用：

```
Custom Chat Model: Qwen/Qwen3-72B-Instruct
```

### 2. 使用特殊优化的模型

使用针对特定任务优化的模型：

```
Custom Chat Model: Qwen/Qwen2.5-Math-72B-Instruct  # 数学推理专用
```

### 3. 使用量化模型以节省成本

使用 AWQ/GPTQ 等量化版本模型：

```
Custom Chat Model: Qwen/Qwen2-72B-Instruct-AWQ
```

### 4. 使用社区微调模型

使用社区在 ModelScope 上分享的微调模型：

```
Custom Chat Model: username/custom-finetuned-model
```

## 🔍 调试和验证

### 查看当前使用的模型

启用调试日志后，可以在日志中看到实际使用的模型：

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.yanfeng_ai_task: debug
    custom_components.yanfeng_ai_task.entity: debug
    custom_components.yanfeng_ai_task.ai_task: debug
```

**日志示例**：

```
DEBUG (MainThread) [custom_components.yanfeng_ai_task.entity] Using custom chat model: Qwen/QwQ-32B-Preview
```

或

```
DEBUG (MainThread) [custom_components.yanfeng_ai_task.entity] Using predefined chat model: Qwen/Qwen2.5-72B-Instruct
```

### 验证模型名称是否正确

1. **访问 ModelScope 平台**：https://modelscope.cn/models
2. **搜索模型**：输入模型名称
3. **复制完整路径**：格式通常为 `组织名/模型名`
4. **粘贴到配置中**

## 📝 配置示例

### 示例 1：使用 QwQ 推理模型

```
Chat Model: Qwen/Qwen2.5-72B-Instruct
Custom Chat Model: Qwen/QwQ-32B-Preview
Temperature: 0.3
Max Tokens: 4096
```

**用途**：适合需要复杂推理和思考过程的任务。

### 示例 2：使用数学专用模型

```
Chat Model: Qwen/Qwen2.5-72B-Instruct
Custom Chat Model: Qwen/Qwen2.5-Math-72B-Instruct
Temperature: 0.2
Max Tokens: 2048
```

**用途**：处理数学计算、方程求解等数学相关任务。

### 示例 3：使用自定义图像模型

```
Image Model: Qwen/Qwen-Image
Custom Image Model: AI-ModelScope/flux-dev
```

**用途**：使用更先进的图像生成模型。

## ⚠️ 注意事项

### 1. 模型兼容性

**重要**：不是所有模型都支持所有功能。

#### 对话模型要求

- ✅ **必须支持 OpenAI Chat Completions 格式**
- ✅ **推荐使用纯文本模型**（支持 Function Calling）
- ❌ **避免使用 VL（视觉语言）模型进行纯文本对话**

**推荐用于设备控制的模型**：
```
✅ Qwen/Qwen2.5-72B-Instruct
✅ Qwen/Qwen2.5-32B-Instruct
✅ Qwen/QwQ-32B-Preview
❌ Qwen/Qwen3-VL-235B-A22B-Instruct (不适合 Function Calling)
```

#### 图像模型要求

- ✅ **必须支持文本到图像生成**
- ✅ **支持 OpenAI Images API 格式**（或兼容格式）
- ⚠️ **部分模型可能需要额外的输入图像**

### 2. API 调用成本

不同模型的调用成本可能不同：
- 大型模型（如 110B）：成本较高，速度较慢
- 中型模型（如 32B-72B）：性能与成本平衡
- 小型模型（如 7B-14B）：成本较低，速度较快

请根据实际需求选择合适的模型。

### 3. 模型可用性

- ModelScope 平台上的模型可能随时下线或更名
- 建议定期检查模型是否仍然可用
- 保留预定义模型作为备用

### 4. 输入验证

- 自定义模型名称会去除首尾空格
- 如果自定义模型为空字符串，将使用预定义模型
- 模型名称格式通常为 `组织名/模型名`

### 5. 错误处理

如果自定义模型不存在或不可用：
- ModelScope API 将返回错误
- 日志中会记录详细的错误信息
- 建议切换回预定义模型或联系 ModelScope 支持

## 🔧 代码实现细节

### entity.py (对话模型)

```python
# Priority: custom_chat_model > chat_model > default
custom_model = self._get_option(CONF_CUSTOM_CHAT_MODEL)
if custom_model and custom_model.strip():
    model = custom_model.strip()
    LOGGER.debug("Using custom chat model: %s", model)
else:
    model = self._get_option(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL)
    LOGGER.debug("Using predefined chat model: %s", model)
```

### ai_task.py (图像模型)

```python
# Priority: custom_image_model > image_model > default
custom_image_model = self._get_option(CONF_CUSTOM_IMAGE_MODEL)
if custom_image_model and custom_image_model.strip():
    image_model = custom_image_model.strip()
    LOGGER.debug("Using custom image model: %s", image_model)
else:
    image_model = self._get_option(CONF_IMAGE_MODEL, RECOMMENDED_IMAGE_MODEL)
    LOGGER.debug("Using predefined image model: %s", image_model)
```

## 📊 常见问题 (FAQ)

### Q1: 自定义模型和预定义模型可以同时配置吗？

**A**: 可以。预定义模型会作为备用，当自定义模型字段为空时使用。

### Q2: 如何清除自定义模型配置？

**A**: 在配置界面将 Custom Chat Model 或 Custom Image Model 字段清空，然后提交即可。

### Q3: 自定义模型是否支持所有功能？

**A**: 这取决于模型本身的能力：
- **对话功能**：所有 Chat Completions 兼容的模型都支持
- **Function Calling**：仅支持纯文本对话模型（非 VL 模型）
- **图像生成**：仅支持图像生成模型

### Q4: 可以使用其他平台的模型吗？

**A**: 不可以。本集成仅支持 ModelScope 平台上的模型。如果需要使用其他平台（如 OpenAI、Anthropic 等），请使用对应的集成。

### Q5: 自定义模型会保存在哪里？

**A**: 自定义模型配置保存在 Home Assistant 的配置条目中（`.storage/core.config_entries`），与其他配置一起持久化存储。

### Q6: 重启后自定义模型配置会丢失吗？

**A**: 不会。自定义模型配置会持久保存，重启后仍然有效。

## 🎓 最佳实践

### 1. 渐进式测试

首次使用自定义模型时：
1. 先在测试环境中验证
2. 确认模型可用后再应用到生产环境
3. 监控日志确保没有错误

### 2. 保留备用模型

始终在下拉菜单中选择一个可靠的预定义模型作为备用：
```
Chat Model: Qwen/Qwen2.5-72B-Instruct (备用)
Custom Chat Model: Qwen/QwQ-32B-Preview (主用)
```

### 3. 文档记录

为每个自定义模型配置添加注释（在配置说明或文档中）：
```
配置项: Yanfeng AI Conversation
自定义模型: Qwen/QwQ-32B-Preview
用途: 复杂推理任务，需要思考链
配置时间: 2025-01-17
```

### 4. 性能监控

使用自定义模型后，监控以下指标：
- 响应时间
- 错误率
- API 调用成本
- 输出质量

### 5. 定期更新

定期检查 ModelScope 平台的模型更新：
- 新模型发布
- 模型优化版本
- 废弃通知

## 🔄 版本历史

- **v2.0.1 (2025-01-17)**：添加自定义模型功能
  - 支持自定义聊天模型
  - 支持自定义图像模型
  - 优先级：自定义 > 预定义 > 默认

---

## 📚 相关文档

- [FUNCTION_CALLING_IMPLEMENTATION.md](./FUNCTION_CALLING_IMPLEMENTATION.md) - Function Calling 功能文档
- [SYSTEM_PROMPT.md](./SYSTEM_PROMPT.md) - 系统提示词指南
- [CLAUDE.md](./CLAUDE.md) - 项目开发指南

---

**提示**：自定义模型功能为您提供了最大的灵活性，让您可以充分利用 ModelScope 平台上不断更新的模型资源！

**最后更新**：2025-01-17
**版本**：v2.0.1
**状态**：✅ 已完成并就绪
