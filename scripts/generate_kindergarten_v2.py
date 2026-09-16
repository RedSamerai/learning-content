#!/usr/bin/env python3
"""
继续生成幼儿园剩余内容（修复进度追踪）
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

class KindergartenGenerator:
    def __init__(self):
        self.progress = self.load_progress()
        self.stats = {"total": 0, "completed": 0, "failed": 0, "skipped": 0}
    
    def load_progress(self) -> dict:
        if os.path.exists("generation_progress.json"):
            with open("generation_progress.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"topics": {}, "created_at": datetime.now().isoformat()}
    
    def save_progress(self):
        self.progress["updated_at"] = datetime.now().isoformat()
        self.progress["stats"] = self.stats
        with open("generation_progress.json", 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def is_completed(self, topic_id: str) -> bool:
        # 检查是否有完整的输出文件
        topic_dir = Path("output") / topic_id
        json_file = Path(f"output/{topic_id}.json")
        
        # 尝试多种可能的路径
        for pattern in [
            "output/**/*.json",  # 通配符匹配
        ]:
            pass
        
        # 直接检查生成的JSON文件
        for subject in ["health", "language", "social", "science", "art"]:
            for age_group in ["小班(3-4岁)", "中班(4-5岁)", "大班(5-6岁)"]:
                test_path = f"output/{subject}/{age_group}/{topic_id}.json"
                if os.path.exists(test_path):
                    return True
        
        return False
    
    def mark_completed(self, topic_id: str):
        self.progress["topics"][topic_id] = {
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        }
        self.stats["completed"] += 1
        self.save_progress()
    
    def mark_failed(self, topic_id: str, error: str = ""):
        self.progress["topics"][topic_id] = {
            "status": "failed",
            "error": error,
            "failed_at": datetime.now().isoformat()
        }
        self.stats["failed"] += 1
        self.save_progress()
    
    def load_knowledge_graph(self) -> List[Dict]:
        with open("knowledge_graph.json", 'r', encoding='utf-8') as f:
            graph = json.load(f)
        
        topics = []
        for subject in graph["subjects"]:
            for area in subject.get("areas", []):
                for obj in area.get("objectives", []):
                    for topic in obj.get("topics", []):
                        topic["subject"] = subject["subject_id"]
                        topics.append(topic)
        
        self.stats["total"] = len(topics)
        return topics
    
    async def generate_text(self, topic: Dict) -> Optional[Dict]:
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
    
    async def generate_image(self, prompt: str, output_path: str) -> bool:
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
    
    async def generate_audio(self, text: str, output_path: str, age_group: str) -> bool:
        voice = VOICE_CONFIG.get(age_group, "zh-CN-XiaoyiNeural")
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"    TTS失败: {e}")
            return False
    
    async def qa_image(self, image_path: str, expected: str) -> Dict:
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
    
    async def process_topic(self, topic: Dict, index: int, total: int):
        topic_id = topic["topic_id"]
        name = topic["name"]
        subject = topic.get("subject", "unknown")
        age_group = topic.get("age_group", "未知")
        
        print(f"\n[{index}/{total}] {subject} - {name} ({age_group})")
        
        # 检查是否已完成（通过文件存在性）
        found = False
        for subj in ["health", "language", "social", "science", "art"]:
            for age in ["小班(3-4岁)", "中班(4-5岁)", "大班(5-6岁)"]:
                test_path = f"output/{subj}/{age}/{topic_id}.json"
                if os.path.exists(test_path):
                    found = True
                    break
            if found:
                break
        
        if found:
            print("  ⏭️ 已存在，跳过")
            self.stats["skipped"] += 1
            return
        
        # 生成文本
        print("  📝 生成文本...")
        content = await self.generate_text(topic)
        if not content:
            print("  ❌ 文本生成失败")
            self.mark_failed(topic_id, "文本生成失败")
            return
        
        # 生成图片
        print("  🎨 生成图片...")
        image_prompt = f"儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁白色背景，{name}的内容场景，适合幼儿认知，教育类插图"
        image_path = f"output/{subject}/{age_group}/{topic_id}/image.png"
        
        if await self.generate_image(image_prompt, image_path):
            qa_result = await self.qa_image(image_path, name)
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
        
        concept_ok = await self.generate_audio(content.get("concept", ""), audio_concept, age_group)
        explanation_ok = await self.generate_audio(content.get("explanation", ""), audio_explanation, age_group)
        
        if concept_ok:
            print(f"  ✅ 概念音频 ({os.path.getsize(audio_concept)} bytes)")
        if explanation_ok:
            print(f"  ✅ 讲解音频 ({os.path.getsize(audio_explanation)} bytes)")
        
        # 保存JSON
        output_file = f"output/{subject}/{age_group}/{topic_id}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "topic_id": topic_id,
                "name": name,
                "age_group": age_group,
                "subject": subject,
                "content": content,
                "created_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        print(f"  💾 已保存")
        self.mark_completed(topic_id)
    
    def show_progress(self):
        print("\n" + "=" * 60)
        print(f"📊 生成进度")
        print(f"   总计: {self.stats['total']} 个知识点")
        print(f"   ✅ 已完成: {self.stats['completed']}")
        print(f"   ❌ 失败: {self.stats['failed']}")
        print(f"   ⏭️ 跳过: {self.stats['skipped']}")
        if self.stats['total'] > 0:
            print(f"   📈 完成率: {(self.stats['completed']+self.stats['skipped'])/self.stats['total']*100:.1f}%")
        print("=" * 60)
    
    async def run(self):
        print("🚀 继续生成幼儿园内容（修复版）")
        print("=" * 60)
        
        topics = self.load_knowledge_graph()
        self.show_progress()
        
        for i, topic in enumerate(topics, 1):
            await self.process_topic(topic, i, len(topics))
        
        self.show_progress()
        print("\n✅ 全部完成！")


async def main():
    generator = KindergartenGenerator()
    await generator.run()


if __name__ == '__main__':
    asyncio.run(main())
