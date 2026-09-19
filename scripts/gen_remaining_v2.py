#!/usr/bin/env python3
"""继续生成小学+初中其他年级内容"""
import asyncio, aiohttp, json, time
from pathlib import Path
import edge_tts

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
REQUEST_DELAY = 4.0
VOICE_MAP = {
    "幼儿园": "zh-CN-XiaoyiNeural",
    "幼小衔接": "zh-CN-XiaoyiNeural",
    "一年级": "zh-CN-XiaoxiaoNeural",
    "二年级": "zh-CN-XiaoxiaoNeural",
    "三年级": "zh-CN-XiaoxiaoNeural",
    "四年级": "zh-CN-XiaoxiaoNeural",
    "五年级": "zh-CN-XiaoxiaoNeural",
    "六年级": "zh-CN-XiaoxiaoNeural",
    "七年级": "zh-CN-YunxiNeural",
    "八年级": "zh-CN-YunxiNeural",
    "九年级": "zh-CN-YunxiNeural"
}

def get_voice(grade):
    for k, v in VOICE_MAP.items():
        if k in grade:
            return v
    return "zh-CN-XiaoxiaoNeural"

async def call_api(prompt):
    headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 800}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("https://apihub.agnes-ai.com/v1/chat/completions", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result['choices'][0]['message']['content']
                return None
        except Exception as e:
            print(f"    API错误: {e}")
            return None

async def generate_audio(text, audio_path, voice):
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(audio_path))
        return True
    except:
        return False

async def process_topic(topic_path, subject, grade):
    json_path = topic_path / f"{topic_path.name}.json"
    if not json_path.exists():
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        topic_name = data.get("name", topic_path.name)
        print(f"  {topic_name} ({grade})...", end=" ", flush=True)
        
        # 生成详细讲解
        prompt = f"""你是{grade}的{subject}老师，请详细讲解'{topic_name}'。
要求：用通俗易懂的语言，200-400字，包含生活例子和核心要点。只返回讲解内容。"""
        
        explanation = await call_api(prompt)
        if explanation and len(explanation) > 100:
            data["explanation"] = explanation
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 生成音频
            voice = get_voice(grade)
            audio_path = topic_path / "audio.mp3"
            await generate_audio(explanation[:500], audio_path, voice)
            
            print("✅")
            return True
        else:
            print("❌ 内容过短")
            return False
    except Exception as e:
        print(f"❌ {e}")
        return False

async def main():
    subjects = ["math", "chinese", "english", "physics", "chemistry", "biology", "history", "geography", "morality", "science", "art", "health", "social", "language"]
    grades = [
        "一年级上", "一年级下", "二年级上", "二年级下",
        "三年级上", "三年级下", "四年级上", "四年级下",
        "五年级上", "五年级下", "六年级上", "六年级下",
        "七年级上", "七年级下", "八年级上", "八年级下", "九年级上", "九年级下",
        "幼儿园(3-4岁)", "幼儿园(4-5岁)", "幼儿园(5-6岁)", "幼小衔接"
    ]
    
    topics = []
    for p in Path("output").rglob("*"):
        if p.is_dir() and p.name not in ["image", "audio"]:
            parts = str(p.relative_to("output")).split("/")
            if len(parts) >= 4 and parts[0] in subjects and parts[1] in grades:
                json_path = p / f"{p.name}.json"
                if json_path.exists():
                    topics.append((p, parts[0], parts[1]))
    
    print(f"找到 {len(topics)} 个知识点待处理\n")
    
    completed = 0
    for i, (topic_path, subject, grade) in enumerate(topics):
        print(f"[{i+1}/{len(topics)}]", end=" ")
        if await process_topic(topic_path, subject, grade):
            completed += 1
        
        await asyncio.sleep(REQUEST_DELAY)
        
        if (i+1) % 20 == 0:
            print(f"\n进度: {i+1}/{len(topics)}, 完成: {completed}\n")
    
    print(f"\n{'='*60}")
    print(f"✅ 完成: {completed}/{len(topics)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
