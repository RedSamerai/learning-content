#!/usr/bin/env python3
"""生成高质量教科书式讲解内容"""
import asyncio, aiohttp, json, time, os
from pathlib import Path
import edge_tts

# 从环境变量读取Key，避免被系统截断
AGNES_API_KEY = os.environ.get('AGNES_API_KEY', '')
REQUEST_DELAY = 4  # 4秒间隔，确保≤15 RPM

async def generate_explanation(topic):
    """生成详细讲解内容"""
    prompt = f"""你是一个专业的K12教育内容专家。请为以下知识点生成详细的教科书式讲解内容。

知识点：{topic['topic']}
年级：{topic['grade']}
科目：{topic['subject']}

要求：
1. 像教科书正文一样详细讲解，不是提纲式
2. 包含：生活例子、概念解释、公式/定理、常见误区提醒
3. 内容要有深度，适合学生自学
4. 字数不少于500字
5. 用中文输出

请直接输出详细内容，不要加标题或说明。"""
    
    headers = {
        "Authorization": f"Bearer {AGNES_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "agnes-2.5-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://apihub.agnes-ai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
                else:
                    print(f"  ❌ API错误: {resp.status} {await resp.text()}")
                    return None
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return None

async def generate_audio(topic_id, topic_name, grade):
    """生成音频"""
    try:
        voice = "zh-CN-XiaoyiNeural" if grade in ["幼儿园", "幼小衔接"] else "zh-CN-YunxiNeural"
        communic = edge_tts.Communicate(topic_name, voice)
        audio_path = Path(f"output/{topic_id}.mp3")
        await communic.save(str(audio_path))
        return str(audio_path)
    except Exception as e:
        print(f"  ❌ 音频生成失败: {e}")
        return None

async def process_topic(topic):
    """处理单个知识点"""
    topic_id = topic["id"]
    # 清理文件名中的特殊字符 - 更彻底
    safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in topic_id)
    output_dir = Path(f"output/{topic['grade']}/{topic['subject']}/{safe_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = output_dir / f"{safe_id}.json"
    
    # 检查是否已存在
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if existing.get("explanation") and len(existing["explanation"]) > 500:
            return True
    
    print(f"\n📚 {topic['grade']} - {topic['subject']} - {topic['topic']}")
    
    # 生成讲解
    print("  📝 生成讲解...")
    explanation = await generate_explanation(topic)
    if not explanation:
        return False
    
    # 生成音频
    print("  🔊 生成音频...")
    audio_path = await generate_audio(safe_id, topic["topic"], topic["grade"])
    
    # 保存
    data = {
        "id": topic_id,
        "grade": topic["grade"],
        "level": topic.get("level", topic["grade"]),
        "subject": topic["subject"],
        "topic": topic["topic"],
        "explanation": explanation,
        "audio": audio_path or "",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ 完成 ({len(explanation)}字)")
    return True

async def main():
    # 加载知识点清单
    with open("knowledge_graph_complete.json", "r", encoding="utf-8") as f:
        topics = json.load(f)
    
    print(f"共 {len(topics)} 个知识点待生成")
    
    # 按年级排序
    grade_order = ["幼儿园", "幼小衔接", 
                   "一年级上", "一年级下", "二年级上", "二年级下",
                   "三年级上", "三年级下", "四年级上", "四年级下",
                   "五年级上", "五年级下", "六年级上", "六年级下",
                   "七年级上", "七年级下", "八年级上", "八年级下",
                   "九年级上", "九年级下"]
    
    topics.sort(key=lambda x: grade_order.index(x["grade"]) if x["grade"] in grade_order else 99)
    
    completed = 0
    for i, topic in enumerate(topics):
        success = await process_topic(topic)
        if success:
            completed += 1
        
        # 每50个保存一次进度
        if (i + 1) % 50 == 0:
            print(f"\n⏸ 进度: {completed}/{i+1}")
        
        # 控制RPM
        await asyncio.sleep(REQUEST_DELAY)
    
    print(f"\n🎉 完成! 成功: {completed}/{len(topics)}")

if __name__ == "__main__":
    asyncio.run(main())