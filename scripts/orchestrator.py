#!/usr/bin/env python3
"""
内容生成编排器 - 协调所有Bot工作流
支持断点续传和进度追踪
"""

import asyncio
import aiohttp
import json
import os
import base64
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# API配置
AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

# 进度文件
PROGRESS_FILE = "generation_progress.json"

class ContentGenerator:
    """内容生成编排器"""
    
    def __init__(self):
        self.progress = self.load_progress()
        self.stats = {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "skipped": 0
        }
    
    def load_progress(self) -> dict:
        """加载进度"""
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"topics": {}, "created_at": datetime.now().isoformat()}
    
    def save_progress(self):
        """保存进度"""
        self.progress["updated_at"] = datetime.now().isoformat()
        self.progress["stats"] = self.stats
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def get_topic_status(self, topic_id: str) -> str:
        """获取知识点状态"""
        return self.progress["topics"].get(topic_id, {}).get("status", "pending")
    
    def mark_completed(self, topic_id: str):
        """标记已完成"""
        self.progress["topics"][topic_id] = {
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        }
        self.stats["completed"] += 1
    
    def mark_failed(self, topic_id: str, error: str = ""):
        """标记失败"""
        self.progress["topics"][topic_id] = {
            "status": "failed",
            "error": error,
            "failed_at": datetime.now().isoformat()
        }
        self.stats["failed"] += 1
    
    def mark_skipped(self, topic_id: str):
        """标记跳过"""
        self.progress["topics"][topic_id] = {
            "status": "skipped"
        }
        self.stats["skipped"] += 1
    
    def is_completed(self, topic_id: str) -> bool:
        """检查是否已完成"""
        return self.get_topic_status(topic_id) == "completed"
    
    def load_knowledge_graph(self) -> List[Dict]:
        """加载知识图谱"""
        with open("knowledge_graph.json", 'r', encoding='utf-8') as f:
            graph = json.load(f)
        
        topics = []
        for subject in graph["subjects"]:
            for area in subject.get("areas", []):
                for obj in area.get("objectives", []):
                    for topic in obj.get("topics", []):
                        topic["subject"] = subject["subject_id"]
                        topic["area"] = area["area_id"]
                        topics.append(topic)
        
        self.stats["total"] = len(topics)
        return topics
    
    async def generate_text(self, topic: Dict) -> Optional[Dict]:
        """生成文本内容"""
        subject = topic.get("subject", "unknown")
        name = topic["name"]
        age_group = topic.get("age_group", "未知")
        
        prompt = f"""请为{age_group}幼儿编写健康教育内容：
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
        """生成图片"""
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
    
    async def generate_audio(self, text: str, output_path: str, age_group: str = "") -> bool:
        """生成语音（根据年龄段选择音色）"""
        # 音色映射
        voice_map = {
            "小班": "zh-CN-XiaoyiNeural",
            "中班": "zh-CN-XiaoyiNeural",
            "大班": "zh-CN-XiaoyiNeural",
            "一年级": "zh-CN-XiaoxiaoNeural",
            "二年级": "zh-CN-XiaoxiaoNeural",
            "初中": "zh-CN-XiaoxiaoNeural",
        }
        
        # 根据年龄段选择音色
        voice = "zh-CN-XiaoyiNeural"  # 默认
        for key, v in voice_map.items():
            if key in age_group:
                voice = v
                break
        
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
        """质检图片"""
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
        """处理单个知识点"""
        topic_id = topic["topic_id"]
        name = topic["name"]
        subject = topic.get("subject", "unknown")
        age_group = topic.get("age_group", "未知")
        
        print(f"\n[{index}/{total}] {subject} - {name} ({age_group})")
        
        # 检查是否已完成
        if self.is_completed(topic_id):
            print("  ⏭️ 已生成，跳过")
            self.mark_skipped(topic_id)
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
        
        concept_ok = await self.generate_audio(content.get("concept", ""), audio_concept)
        explanation_ok = await self.generate_audio(content.get("explanation", ""), audio_explanation)
        
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
        self.save_progress()
    
    def show_progress(self):
        """显示进度"""
        completed = self.stats["completed"]
        failed = self.stats["failed"]
        total = self.stats["total"]
        
        print("\n" + "=" * 60)
        print(f"📊 生成进度")
        print(f"   总计: {total} 个知识点")
        print(f"   ✅ 已完成: {completed}")
        print(f"   ❌ 失败: {failed}")
        print(f"   ⏭️ 跳过: {self.stats['skipped']}")
        print(f"   📈 完成率: {completed/total*100:.1f}%" if total > 0 else "")
        print("=" * 60)
    
    async def run(self, subjects: List[str] = None, resume: bool = True):
        """运行生成"""
        print("🚀 开始批量生成幼儿园内容")
        print("=" * 60)
        
        # 加载知识图谱
        topics = self.load_knowledge_graph()
        
        # 过滤指定学科
        if subjects:
            topics = [t for t in topics if t.get("subject") in subjects]
        
        print(f"📋 待处理: {len(topics)} 个知识点")
        self.show_progress()
        
        # 处理每个知识点
        for i, topic in enumerate(topics, 1):
            await self.process_topic(topic, i, len(topics))
        
        self.show_progress()
        print("\n✅ 全部完成！")


async def main():
    generator = ContentGenerator()
    
    # 支持命令行参数
    import sys
    args = sys.argv[1:]
    
    if "--resume" in args:
        print("📂 从断点继续...")
    
    if "--subjects" in args:
        idx = args.index("--subjects")
        subjects = args[idx + 1:].split(",") if idx + 1 < len(args) else None
    else:
        subjects = None
    
    await generator.run(subjects=subjects)


if __name__ == '__main__':
    asyncio.run(main())
