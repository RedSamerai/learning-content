#!/usr/bin/env python3
"""生成小学数学一年级示例内容"""
import asyncio
import aiohttp
import json
import os
import edge_tts
from PIL import Image, ImageDraw, ImageFont

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

# 示例知识点
SAMPLE_TOPICS = [
    {
        "topic_id": "math_py1_count_10",
        "name": "数数1-10",
        "subject": "math",
        "grade": "一年级",
        "prompt": """请为小学一年级学生编写数学教学内容：
题目：数数1-10
要求：
1. 用简单易懂的语言讲解如何数数
2. 举例要贴近生活（如苹果、铅笔等）
3. 生成3道练习题（附答案）
4. 控制在150字以内

输出JSON：{"concept": "一句话概念", "explanation": "详细讲解", "questions": [{"q": "...", "options": ["A...","B...","C..."], "answer": "A"}]}"""
    },
    {
        "topic_id": "math_py1_add_5",
        "name": "5以内的加法",
        "subject": "math",
        "grade": "一年级",
        "prompt": """请为小学一年级学生编写数学教学内容：
题目：5以内的加法
要求：
1. 讲解加法的概念（合并、增加）
2. 用实物举例（如3个苹果加2个苹果）
3. 生成3道练习题（附答案）
4. 控制在150字以内

输出JSON：{"concept": "一句话概念", "explanation": "详细讲解", "questions": [...]}"""
    },
    {
        "topic_id": "math_py1_shape_1",
        "name": "认识长方体",
        "subject": "math",
        "grade": "一年级",
        "prompt": """请为小学一年级学生编写数学教学内容：
题目：认识长方体
要求：
1. 解释什么是长方体（有6个面，相对的面相同）
2. 举例生活中的长方体（如盒子、书本、冰箱）
3. 生成3道练习题（附答案）
4. 控制在150字以内

输出JSON：{"concept": "一句话概念", "explanation": "详细讲解", "questions": [...]}"""
    }
]

async def generate_text(topic):
    """生成文本内容"""
    print(f"📝 生成文本: {topic['name']}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "agnes-2.5-flash",
                "messages": [{"role": "user", "content": topic['prompt']}],
                "response_format": {"type": "json_object"}
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = json.loads(data["choices"][0]["message"]["content"])
                print(f"✅ 文本生成完成")
                return content
            else:
                print(f"❌ API错误: {response.status}")
                return None

async def generate_image(topic):
    """生成图片"""
    print(f"🎨 生成图片: {topic['name']}")
    
    # 根据主题生成不同的prompt
    image_prompts = {
        "math_py1_count_10": "儿童教育插画，显示数字1到10，每个数字旁边有对应数量的彩色物体，如苹果、星星等，扁平化风格，白色背景，色彩鲜艳",
        "math_py1_add_5": "儿童教育插画，展示加法概念：左边3个红色苹果，右边2个绿色苹果，中间加号，总共5个苹果，简洁明了",
        "math_py1_shape_1": "儿童教育插画，展示长方体形状：一个打开的盒子，旁边的书本、砖块等日常物品也是长方体形状，标注'长方体'"
    }
    
    prompt = image_prompts.get(topic['topic_id'], f"儿童教育插画，主题：{topic['name']}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/images/generations",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
            json={"model": "agnes-image-2.1-flash", "prompt": prompt, "size": "1024x512", "n": 1}
        ) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['data'][0].get('url', '')
                if image_url:
                    async with session.get(image_url) as img_response:
                        if img_response.status == 200:
                            img_data = await img_response.read()
                            return img_data
            return None

async def generate_audio(topic_id, concept, explanation, voice="zh-CN-XiaoxiaoNeural"):
    """生成音频"""
    print(f"🔊 生成音频")
    
    # 概念音频
    concept_path = f"output/math/一年级/{topic_id}/audio_concept.mp3"
    os.makedirs(os.path.dirname(concept_path), exist_ok=True)
    
    communicate = edge_tts.Communicate(concept, voice)
    await communicate.save(concept_path)
    print(f"✅ 概念音频 ({os.path.getsize(concept_path)} bytes)")
    
    # 讲解音频
    explanation_path = f"output/math/一年级/{topic_id}/audio_explanation.mp3"
    communicate = edge_tts.Communicate(explanation, voice)
    await communicate.save(explanation_path)
    print(f"✅ 讲解音频 ({os.path.getsize(explanation_path)} bytes)")

def create_math_image(topic_id):
    """创建简单的数学图片（避免AI幻觉）"""
    img = Image.new('RGB', (1200, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    font = ImageFont.truetype("arial.ttf", 80)
    
    if topic_id == "math_py1_count_10":
        # 显示1-10
        for i in range(1, 11):
            x = (i - 1) * 105 + 50
            draw.text((x, 80), str(i), fill='#333333', font=font)
    elif topic_id == "math_py1_add_5":
        # 显示加法：3+2=5
        draw.text((400, 80), "3 + 2 = 5", fill='#FF6B6B', font=font)
    elif topic_id == "math_py1_shape_1":
        # 显示长方体文字说明
        draw.text((200, 80), "长方体：有6个面", fill='#333333', font=font)
        draw.text((200, 180), "就像盒子、书本", fill='#666666', font=font)
    
    return img

async def main():
    print("🚀 开始生成小学数学一年级示例内容\n")
    
    for topic in SAMPLE_TOPICS:
        print(f"\n{'='*50}")
        print(f"📚 知识点: {topic['name']}")
        print(f"{'='*50}")
        
        # 生成文本
        content = await generate_text(topic)
        if not content:
            continue
        
        # 生成图片
        img = create_math_image(topic['topic_id'])
        img_path = f"output/math/一年级/{topic['topic_id']}/image.png"
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        img.save(img_path)
        print(f"✅ 图片已保存: {img_path}")
        
        # 生成音频
        await generate_audio(topic['topic_id'], content.get('concept', ''), content.get('explanation', ''))
        
        # 保存JSON
        output_json = {
            "topic_id": topic['topic_id'],
            "name": topic['name'],
            "subject": topic['subject'],
            "grade": topic['grade'],
            "content": content,
            "created_at": asyncio.get_event_loop().time()
        }
        
        with open(f"output/math/一年级/{topic['topic_id']}.json", 'w', encoding='utf-8') as f:
            json.dump(output_json, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON已保存")
    
    print("\n" + "="*50)
    print("✅ 全部完成！")
    print("="*50)
    print(f"\n示例内容已保存到: output/math/一年级/")
    print("包含3个知识点：")
    print("  1. 数数1-10")
    print("  2. 5以内的加法")
    print("  3. 认识长方体")

if __name__ == '__main__':
    asyncio.run(main())
