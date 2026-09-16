#!/usr/bin/env python3
"""
继续生成幼儿园剩余知识点
"""

import asyncio
import aiohttp
import json
import os
import base64
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

VOICE_CONFIG = {
    "小班": "zh-CN-XiaoyiNeural",
    "中班": "zh-CN-XiaoyiNeural",
    "大班": "zh-CN-XiaoyiNeural",
}

async def generate_text(topic: Dict) -> Optional[Dict]:
    subject = topic.get("subject", "unknown")
    name = topic["name"]
    age_group = topic.get("age_group", "未知")
    
    prompt = f"""请为{age_group}幼儿编写教育内容：
题目：{name}
要求：
1. 用简单易懂的语言讲解
2. 举例要贴近幼儿生活
3. 语言生动活泼，适合朗读
4. 生成3道选择题（附答案）
5. 控制在200字以内

输出JSON格式：
{{
  "concept": "一句话概念",
  "explanation": "详细讲解(100字内)",
  "practice_questions": [
    {{"question": "...", "options": ["A...","B...","C...","D..."], "answer": "A", "explanation": "..."}}
  ]
}}"""
    
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
            return None

async def generate_image(prompt: str, output_path: str) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/images/generations",
            headers={
                "Authorization": f"Bearer {AGNES_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "agnes-image-2.1-flash",
                "prompt": prompt,
                "size": "512x512",
                "n": 1
            }
        ) as response:
            if response.status != 200:
                return False
            
            data = await response.json()
            image_url = data['data'][0].get('url', '')
            
            if not image_url:
                return False
            
            async with session.get(image_url) as img_response:
                if img_response.status == 200:
                    content = await img_response.read()
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(content)
                    return True
            return False

async def generate_audio(text: str, output_path: str, voice: str) -> bool:
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"    TTS失败: {e}")
        return False

async def qa_image(image_path: str, expected: str) -> Dict:
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    prompt = f"""请审核这张教育插图：期望：{expected}
输出JSON：{{"passed": true/false, "score": 0-100, "issues": []}}"""
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {AGNES_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "agnes-3.0-flash",
                "messages": [{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                ]}],
                "response_format": {"type": "json_object"}
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                return json.loads(data["choices"][0]["message"]["content"])
            return {"passed": False, "score": 0, "issues": ["API错误"]}

async def process_topic(topic: Dict, index: int, total: int):
    topic_id = topic["topic_id"]
    name = topic["name"]
    subject = topic.get("subject", "unknown")
    age_group = topic.get("age_group", "未知")
    voice = VOICE_CONFIG.get(age_group, "zh-CN-XiaoyiNeural")
    
    print(f"\n[{index}/{total}] {subject} - {name} ({age_group})")
    
    # 检查是否已完成
    json_path = f"output/{subject}/{age_group}/{topic_id}.json"
    if os.path.exists(json_path):
        print("  ⏭️ 已存在，跳过")
        return True
    
    # 生成文本
    print("  📝 生成文本...")
    content = await generate_text(topic)
    if not content:
        print("  ❌ 文本生成失败")
        return False
    
    # 生成图片
    print("  🎨 生成图片...")
    image_prompt = f"儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁白色背景，{name}的内容场景，适合幼儿认知，教育类插图"
    image_path = f"output/{subject}/{age_group}/{topic_id}/image.png"
    
    if await generate_image(image_prompt, image_path):
        qa_result = await qa_image(image_path, name)
        if qa_result["passed"]:
            print(f"  ✅ 图片通过质检 (分数:{qa_result['score']})")
        else:
            print(f"  ⚠️ 图片需人工审核: {qa_result.get('issues', [])}")
    else:
        print("  ⚠️ 图片生成失败")
    
    # 生成语音
    print("  🔊 生成语音...")
    audio_concept = f"output/{subject}/{age_group}/{topic_id}/audio_concept.mp3"
    audio_explanation = f"output/{subject}/{age_group}/{topic_id}/audio_explanation.mp3"
    
    concept_ok = await generate_audio(content.get("concept", ""), audio_concept, voice)
    explanation_ok = await generate_audio(content.get("explanation", ""), audio_explanation, voice)
    
    if concept_ok:
        print(f"  ✅ 概念音频 ({os.path.getsize(audio_concept)} bytes)")
    if explanation_ok:
        print(f"  ✅ 讲解音频 ({os.path.getsize(audio_explanation)} bytes)")
    
    # 保存JSON
    os.makedirs(f"output/{subject}/{age_group}", exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "topic_id": topic_id,
            "name": name,
            "age_group": age_group,
            "subject": subject,
            "content": content,
            "created_at": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"  💾 已保存")
    return True

async def main():
    # 加载知识图谱
    with open('knowledge_graph.json', 'r', encoding='utf-8') as f:
        graph = json.load(f)
    
    # 收集所有幼儿园知识点
    all_topics = []
    for subject in graph['subjects']:
        for area in subject.get('areas', []):
            for obj in area.get('objectives', []):
                for topic in obj.get('topics', []):
                    if 'kg' in topic.get('topic_id', ''):
                        topic['subject'] = subject['subject_id']
                        all_topics.append(topic)
    
    print(f"🚀 继续生成幼儿园内容")
    print(f"总知识点: {len(all_topics)}\n")
    
    completed = 0
    for i, topic in enumerate(all_topics, 1):
        if await process_topic(topic, i, len(all_topics)):
            completed += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 完成: {completed}/{len(all_topics)}")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())
