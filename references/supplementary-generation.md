# 补充知识点生成规范

当需要扩展学习内容时，按此流程操作。

## 触发场景
- 调研发现某年龄段内容缺失
- 家长热门需求未覆盖（如情商、安全教育、专注力训练）
- 用户要求补充特定科目

## 流程

### 1. 规划知识点清单
在 `knowledge_graph_supplementary.json` 中添加新条目：
```json
{
  "topic_id": "kg_math_num_1",
  "name": "数数1-10",
  "age_group": "幼儿园(3-4岁)",
  "subject": "数学",
  "focus": "正确点数"
}
```

**命名规范**：
- 幼儿园：`kg_{subject}_{num}`
- 幼小衔接：`prep_{subject}_{num}`
- 小学：`py{年级}{上/下}_{subject}_{num}`
- 初中：`junior_{subject}_{num}`

**排序规则**：按年龄组顺序排列（幼儿园→幼小衔接→小学低年级→小学高年级→初中）

### 2. 生成内容
```bash
python scripts/gen_supplementary.py
```

脚本会自动：
- 按年龄排序生成
- 调用AGNES API生成文本说明
- 使用PIL生成图片
- 每请求间隔4.5秒避免超限

### 3. 补全音频
```bash
python scripts/generate_audio.py
```

使用edge-tts本地生成，音色按年龄段自动选择。

### 4. 验证
```bash
python scripts/final_check.py
```

## 注意事项

1. **RPM限制**：AGNES API 20 RPM，批量生成必须加延迟
2. **图片风格**：幼儿园用PIL绘制简单图形，避免AI幻觉
3. **文本长度**：explanation应150字以内，适合朗读
4. **音频格式**：统一MP3，采样率22050Hz

## 常见问题

**Q: 音频生成太慢？**
A: 使用edge-tts而非AGNES API，本地生成无限制

**Q: 图片质量差？**
A: 数学/几何类用PIL代码生成，AI生成用于复杂场景

**Q: 知识点重复？**
A: 先检查output目录，确认是否已存在同名目录