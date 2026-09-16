#!/usr/bin/env python3
"""
测试：使用AGNES生成单个知识点
"""

import asyncio
import aiohttp
import json
import os

# 使用用户提供的API Key
AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

async def generate_single_topic():
    """生成单个知识点"""
    
    # 测试数据：认识数字1-3
    topic_data = {
        "id": "math_kg_number_123",
        "name": "认识数字1-3",
        "subject": "math",
        "grade": "kindergarten",
        "age_group": "kindergarten",
        "objectives": [
            "能识别数字1、2、3",
            "能将数字与数量对应",
            "能按顺序读出1-3"
        ]
    }
    
    prompt = f"""
你是幼儿园数学老师。请为以下知识点生成教学内容：

知识点: {topic_data['name']}
年级: {topic_data['grade']}
教学目标: {', '.join(topic_data['objectives'])}

请用儿童友好的语言，生成以下内容（输出JSON格式）：
{{
  "concept": "概念解释（100字以内，生动有趣）",
  "explanation": "详细讲解（200字以内，循序渐进）",
  "examples": [
    {{"number": 1, "text": "1个苹果", "description": "简短说明"}},
    {{"number": 2, "text": "2只小鸟", "description": "简短说明"}},
    {{"number": 3, "text": "3朵花", "description": "简短说明"}}
  ],
  "common_mistakes": ["常见错误1", "常见错误2"],
  "tips": ["学习技巧1"]
}}

要求：
- 用简单短句，每句不超过15个字
- 多用比喻和故事
- 加入拟人化元素
- 避免抽象概念
"""
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {AGNES_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "agnes-2.5-flash",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "temperature": 0.7
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = json.loads(data["choices"][0]["message"]["content"])
                return content
            else:
                error_text = await response.text()
                raise Exception(f"API Error {response.status}: {error_text}")

async def generate_practice_questions(topic_name: str, count: int = 3):
    """生成练习题"""
    
    prompt = f"""
你是幼儿园数学老师。请为"{topic_name}"生成{count}道选择题。

输出JSON格式：
{{
  "practice": [
    {{
      "type": "multiple_choice",
      "question": "题目内容",
      "options": ["选项A", "选项B", "选项C", "选项D"],
      "answer": "正确选项",
      "explanation": "为什么选这个答案"
    }}
  ]
}}

要求：
- 题目简单明了
- 选项要有干扰性但不过难
- 解释要鼓励性语言
"""
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {AGNES_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "agnes-2.5-flash",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                return json.loads(data["choices"][0]["message"]["content"])
            else:
                error_text = await response.text()
                raise Exception(f"API Error {response.status}: {error_text}")

async def main():
    print("🚀 开始生成知识点...")
    print("=" * 50)
    
    try:
        # 1. 生成内容
        print("\n📝 Step 1: 生成教学内容...")
        content = await generate_single_topic()
        print("✅ 内容生成成功！")
        
        # 2. 生成练习题
        print("\n📝 Step 2: 生成练习题...")
        practice_data = await generate_practice_questions("认识数字1-3", 3)
        print("✅ 练习题生成成功！")
        
        # 3. 合并完整知识点
        full_topic = {
            "id": "math_kg_number_123",
            "version": "1.0.0",
            "created_at": "2026-09-16",
            
            "metadata": {
                "subject": "math",
                "grade_level": "kindergarten",
                "chapter": "数字认知",
                "topic": "认识数字1-3"
            },
            
            "age_appropriate": {
                "min_age": 3,
                "max_age": 6,
                "cognitive_level": "concrete",
                "learning_style": "visual_auditory"
            },
            
            "content": content,
            "practice": practice_data["practice"],
            
            "accessibility": {
                "audio_required": True,
                "voice": "zh-CN-XiaoxiaoNeural"
            },
            
            "estimated_time_minutes": 10
        }
        
        print("\n" + "=" * 50)
        print("📦 完整知识点JSON：")
        print("=" * 50)
        print(json.dumps(full_topic, ensure_ascii=False, indent=2))
        
        # 保存到文件
        output_path = "test_output/generated_topic.json"
        import os
        os.makedirs("test_output", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(full_topic, f, ensure_ascii=False, indent=2)
        print(f"\n💾 已保存到: {output_path}")
        
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
