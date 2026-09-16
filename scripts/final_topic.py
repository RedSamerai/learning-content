#!/usr/bin/env python3
"""生成最后一个知识点"""
import asyncio
import aiohttp
import json
import os
import base64
from datetime import datetime

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

async def main():
    print("🎨 生成最后一个知识点: 捏泥工作品")
    
    # 生成文本
    print("📝 生成文本...")
    prompt = """请为大班(5-6岁)幼儿编写教育内容：
题目：捏泥工作品
要求：
1. 用简单易懂的语言讲解
2. 举例要贴近幼儿生活
3. 语言生动活泼，适合朗读
4. 生成3道选择题（附答案）
5. 控制在200字以内

输出JSON格式：
{"concept": "一句话概念", "explanation": "详细讲解(100字内)", "practice_questions": [{"question": "...", "options": ["A...","B...","C...","D..."], "answer": "A", "explanation": "..."}]}"""
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
            json={"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = json.loads(data["choices"][0]["message"]["content"])
            else:
                print(f"❌ API错误: {response.status}")
                return
    
    print(f"✅ 文本生成完成")
    
    # 生成图片
    print("🎨 生成图片...")
    image_prompt = "儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁白色背景，小朋友正在捏泥人做手工，适合幼儿认知，教育类插图"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/images/generations",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
            json={"model": "agnes-image-2.1-flash", "prompt": image_prompt, "size": "512x512", "n": 1}
        ) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['data'][0].get('url', '')
                async with session.get(image_url) as img_response:
                    if img_response.status == 200:
                        with open("output/art/大班(5-6岁)/art_kg_clay/image.png", 'wb') as f:
                            f.write(await img_response.read())
                        print("✅ 图片生成完成")
    
    # 生成音频
    print("🔊 生成音频...")
    import edge_tts
    voice = "zh-CN-XiaoyiNeural"
    
    concept_path = "output/art/大班(5-6岁)/art_kg_clay/audio_concept.mp3"
    explanation_path = "output/art/大班(5-6岁)/art_kg_clay/audio_explanation.mp3"
    
    os.makedirs("output/art/大班(5-6岁)/art_kg_clay", exist_ok=True)
    
    communicate = edge_tts.Communicate(content.get("concept", ""), voice)
    await communicate.save(concept_path)
    print(f"✅ 概念音频 ({os.path.getsize(concept_path)} bytes)")
    
    communicate = edge_tts.Communicate(content.get("explanation", ""), voice)
    await communicate.save(explanation_path)
    print(f"✅ 讲解音频 ({os.path.getsize(explanation_path)} bytes)")
    
    # 保存JSON
    with open("output/art/大班(5-6岁)/art_kg_clay.json", 'w', encoding='utf-8') as f:
        json.dump({
            "topic_id": "art_kg_clay",
            "name": "捏泥工作品",
            "age_group": "大班(5-6岁)",
            "subject": "art",
            "content": content,
            "created_at": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print("💾 已保存")
    print("\n✅ 全部完成！")

if __name__ == '__main__':
    asyncio.run(main())
