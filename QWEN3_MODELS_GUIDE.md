# Qwen3 系列模型使用指南

## 📋 概述

Qwen3 和 QwQ 系列模型是支持"思考"（Reasoning）功能的特殊模型，类似于 OpenAI 的 o1 系列。这些模型在生成回答之前会先进行推理思考，因此需要特殊的参数配置。

## 🎯 支持的模型

### Qwen3 系列
- `Qwen/Qwen3-32B`
- `Qwen/Qwen3-72B`
- 其他包含 "Qwen3" 的模型

### QwQ 系列
- `Qwen/QwQ-32B-Preview`
- 其他包含 "QwQ" 的模型

## ⚙️ 技术细节

### 思考模式（Reasoning）

Qwen3/QwQ 模型支持两种输出模式：

1. **思考内容** (`reasoning_content`)：模型的内部推理过程
2. **最终答案** (`content`)：给用户的最终回答

### API 参数要求

根据 ModelScope API 的要求：

**流式调用** (`stream=True`)：
```python
extra_body = {
    "enable_thinking": True,  # 可选，默认 True
    "thinking_budget": 4096   # 可选，控制思考 token 数量
}
```

**非流式调用** (`stream=False`)：
```python
# 必须显式禁用思考功能
extra_body = {
    "enable_thinking": False
}
```

## 🔧 集成实现

### 自动处理

Yanfeng AI Task 集成已经自动处理了这些特殊参数：

**在 `helpers.py` 中**：
```python
# Handle special models that require extra parameters
# Qwen3 series models require enable_thinking parameter for non-streaming calls
if "Qwen3" in model or "QwQ" in model:
    if not stream:
        # For non-streaming calls, must disable thinking
        payload["enable_thinking"] = False
        LOGGER.debug("Added enable_thinking=False for Qwen3/QwQ model in non-streaming mode")
```

### 当前限制

由于 Home Assistant Conversation 集成**不支持流式输出**，所以：

- ✅ 可以使用 Qwen3/QwQ 模型获取最终答案
- ❌ 无法查看模型的思考过程（reasoning_content）
- ✅ 自动设置 `enable_thinking=False`

## 💡 使用方法

### 配置自定义模型

1. 进入 **设置 > 设备与服务**
2. 配置 **Yanfeng AI Task** 集成
3. 在 **Custom Chat Model** 字段输入：
   ```
   Qwen/Qwen3-32B
   ```
   或
   ```
   Qwen/QwQ-32B-Preview
   ```

### 预期行为

**用户输入**：
```
9.9和9.11谁大？
```

**模型处理**：
```
[内部思考过程 - 不可见]
比较两个数字：
9.9 = 9.90
9.11 = 9.11
因为 9.90 > 9.11，所以 9.9 更大
```

**最终输出**：
```
9.9 更大。
```

## 📊 对比：流式 vs 非流式

### 流式调用（需要额外开发支持）

**优点**：
- ✅ 可以看到完整的思考过程
- ✅ 更透明的推理链
- ✅ 适合需要解释推理的场景

**示例输出**：
```
[思考过程]
我需要比较 9.9 和 9.11...
将它们转换为相同的小数位数...
9.9 = 9.90
9.11 = 9.11
由于 90 > 11，所以 9.9 > 9.11

=== 最终答案 ===
9.9 更大。
```

### 非流式调用（当前实现）

**优点**：
- ✅ 与现有 HA 集成兼容
- ✅ 代码简单，无需流式处理
- ✅ 自动获取最终答案

**示例输出**：
```
9.9 更大。
```

## 🔍 调试信息

启用调试日志后，可以看到自动添加的参数：

```yaml
# configuration.yaml
logger:
  logs:
    custom_components.yanfeng_ai_task.helpers: debug
```

**日志输出**：
```
DEBUG (MainThread) [custom_components.yanfeng_ai_task.helpers]
Added enable_thinking=False for Qwen3/QwQ model in non-streaming mode

DEBUG (MainThread) [custom_components.yanfeng_ai_task.helpers]
Sending ModelScope request to https://api-inference.modelscope.cn/v1/chat/completions
with payload: {
  "model": "Qwen/Qwen3-32B",
  "messages": [...],
  "enable_thinking": false,
  ...
}
```

## ⚠️ 注意事项

### 1. Function Calling 支持

**Qwen3/QwQ 模型的 Function Calling 能力**：

⚠️ **重要**：Qwen3/QwQ 模型主要用于推理任务，对 Function Calling 的支持可能不如 Qwen2.5 系列完善。

**推荐配置**：
- **设备控制和工具调用**：使用 `Qwen/Qwen2.5-72B-Instruct`
- **复杂推理任务**：使用 `Qwen/Qwen3-32B` 或 `Qwen/QwQ-32B-Preview`

### 2. 响应时间

Qwen3/QwQ 模型由于需要内部推理，响应时间可能比普通模型长：

- **普通模型**：1-2 秒
- **Qwen3/QwQ**：2-5 秒（取决于问题复杂度）

### 3. Token 消耗

虽然用户看不到思考过程，但模型内部仍在消耗 token 进行推理：

- **思考 token**：根据问题复杂度，可能消耗额外的 token
- **输出 token**：最终答案的 token

这意味着 API 调用成本可能高于普通模型。

### 4. 适用场景

**推荐使用 Qwen3/QwQ 的场景**：
- ✅ 复杂的数学问题
- ✅ 逻辑推理任务
- ✅ 需要多步骤思考的问题
- ✅ 代码调试和分析

**不推荐使用的场景**：
- ❌ 简单的设备控制（"打开灯"）
- ❌ 快速查询（"温度多少"）
- ❌ 需要调用 HA 工具的任务

## 🎓 最佳实践

### 1. 多配置策略

创建两个不同的 Conversation 子配置：

**配置 1：设备控制**
```
名称: AI 设备助手
Custom Chat Model: Qwen/Qwen2.5-72B-Instruct
LLM Hass API: Assist (启用)
用途: 设备控制、状态查询
```

**配置 2：推理助手**
```
名称: AI 推理助手
Custom Chat Model: Qwen/QwQ-32B-Preview
LLM Hass API: (不启用)
用途: 数学计算、逻辑推理
```

### 2. 根据任务选择模型

**自动化脚本示例**：
```yaml
alias: "智能助手路由"
trigger:
  - platform: conversation
    command:
      - "计算*"
      - "推理*"
      - "解决*"
action:
  - service: conversation.process
    data:
      agent_id: conversation.ai_reasoning_agent  # 使用推理模型
      text: "{{ trigger.text }}"
```

### 3. 监控性能

定期检查以下指标：
- 平均响应时间
- Token 消耗量
- API 调用成本
- 用户满意度

## 🚀 未来改进

### 计划支持的功能

1. **流式输出支持**
   - 实时显示思考过程
   - 更好的用户体验
   - 需要 HA Conversation 集成支持

2. **思考预算控制**
   - 允许用户设置 `thinking_budget` 参数
   - 控制推理 token 消耗

3. **选择性思考**
   - 根据问题类型自动决定是否启用思考
   - 简单问题快速响应，复杂问题深度思考

## 📚 参考资料

### ModelScope 文档
- [Qwen3 模型文档](https://modelscope.cn/models/Qwen/Qwen3-32B)
- [QwQ 模型文档](https://modelscope.cn/models/Qwen/QwQ-32B-Preview)

### 相关集成文档
- [CUSTOM_MODEL_FEATURE.md](./CUSTOM_MODEL_FEATURE.md) - 自定义模型功能
- [FUNCTION_CALLING_IMPLEMENTATION.md](./FUNCTION_CALLING_IMPLEMENTATION.md) - Function Calling 实现

## 🔧 故障排除

### 错误：parameter.enable_thinking must be set to false

**原因**：使用了 Qwen3/QwQ 模型，但没有正确设置参数

**解决方案**：
- ✅ 使用最新版本的集成（已自动处理）
- ✅ 确认日志中有 "Added enable_thinking=False" 信息
- ✅ 重启 Home Assistant 确保代码更新生效

### 错误：模型响应慢或超时

**原因**：Qwen3/QwQ 模型推理时间较长

**解决方案**：
- ⚙️ 增加超时时间（在 `const.py` 中修改 `TIMEOUT_SECONDS`）
- 💡 对简单任务使用 Qwen2.5 系列模型
- 🔍 检查网络连接

### 工具调用失败

**原因**：Qwen3/QwQ 模型对 Function Calling 的支持不完善

**解决方案**：
- 🔄 切换回 `Qwen/Qwen2.5-72B-Instruct`
- 📝 为推理任务和工具调用创建不同的配置

---

**最后更新**：2025-01-17
**版本**：v2.0.1
**状态**：✅ 已实现并测试
