# 调试日志配置指南

## 方法 1: 通过 configuration.yaml 配置（推荐）

1. 编辑 Home Assistant 的 `configuration.yaml` 文件
2. 添加以下配置：

```yaml
logger:
  default: info
  logs:
    custom_components.yanfeng_ai_task: debug
    homeassistant.components.conversation: debug
    homeassistant.helpers.intent: debug
```

3. 保存后重启 Home Assistant
4. 查看日志：设置 → 系统 → 日志

---

## 方法 2: 通过开发者工具临时启用（无需重启）

1. 进入 **开发者工具 → 服务**
2. 选择服务：`logger.set_level`
3. 服务数据填写：

```yaml
custom_components.yanfeng_ai_task: debug
homeassistant.components.conversation: debug
homeassistant.helpers.intent: debug
```

4. 点击 **调用服务**
5. 立即生效，但重启后失效

---

## 关键日志搜索关键词

启用 DEBUG 后，在日志中搜索以下关键词：

1. **`yanfeng`** - 集成相关的所有日志
2. **`注册意图处理器`** - 意图注册流程
3. **`Set up conversation entities`** - 对话实体创建
4. **`CONF_LLM_HASS_API`** - API 控制配置
5. **`ConversationEntityFeature.CONTROL`** - 控制功能注册
6. **`处理用户输入`** - 实际对话处理

---

## 预期的正常日志示例

```
[custom_components.yanfeng_ai_task] API connection test successful
[custom_components.yanfeng_ai_task] 注册意图处理器...
[custom_components.yanfeng_ai_task.intents] Registering intent: ClimateSetTemperature
[custom_components.yanfeng_ai_task.intents] Registering intent: ClimateSetMode
...
[custom_components.yanfeng_ai_task] 意图处理器注册完成
[custom_components.yanfeng_ai_task.conversation] Set up conversation entities
[custom_components.yanfeng_ai_task.conversation] 处理用户输入: 打开卧室空调
```

---

## 如果没有看到 yanfeng 日志

可能的原因：

1. **集成根本没加载** - 检查集成状态是否为"已加载"
2. **没有创建子条目** - Subentry-Only 架构必须先创建子条目
3. **日志被过滤** - 确认日志级别设置正确
4. **启动时出错** - 查看 Home Assistant 启动日志（重启后的前 100 行）
