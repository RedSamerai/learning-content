#!/usr/bin/env python3
"""批量补全音频 - 针对所有缺失音频的知识点"""
import asyncio, aiohttp, json, time
from pathlib import Path
import edge_tts

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
REQUEST_DELAY = 4.5
last_request_time = 0

# 音色配置
VOICE_MAP = {
    "幼儿园": "zh-CN-XiaoyiNeural",
    "幼小衔接": "zh-CN-XiaoyiNeural",
    "一年级": "zh-CN-XiaoxiaoNeural",
    "二年级": "zh-CN-XiaoxiaoNeural",
    "三年级": "zh-CN-XiaoxiaoNeural",
    "四年级": "zh-CN-XiaoxiaoNeural",
    "五年级": "zh-CN-XiaoxiaoNeural",
    "六年级": "zh-CN-XiaoxiaoNeural",
    "初中": "zh-CN-YunxiNeural"
}

def get_voice(age_group):
    for key, voice in VOICE_MAP.items():
        if key in age_group:
            return voice
    return "zh-CN-XiaoxiaoNeural"

async def call_agnes(prompt):
    global last_request_time
    now = time.time()
    elapsed = now - last_request_time
    if elapsed < REQUEST_DELAY:
        await asyncio.sleep(REQUEST_DELAY - elapsed)
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 400}
        try:
            async with session.post("https://apihub.agnes-ai.com/v1/chat/completions", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    return (await resp.json())['choices'][0]['message']['content']
                return None
        except:
            return None

async def generate_audio(text, output_path, voice):
    """使用Edge-TTS生成音频"""
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"      音频生成失败: {e}")
        return False

async def fix_missing_audio():
    """修复缺失音频的知识点"""
    tasks = []
    
    # 找出所有缺失音频的知识点
    for p in Path('output').rglob('*.json'):
        if p.parent.name in ['image', 'audio']:
            continue
        
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            audio_path = p.parent / 'audio.mp3'
            
            if not audio_path.exists() or audio_path.stat().st_size == 0:
                # 获取文本
                text = data.get('explanation', '')
                if text:
                    age_group = data.get('age_group', data.get('grade', ''))
                    voice = get_voice(age_group)
                    tasks.append((p, text, voice, audio_path))
        except:
            pass
    
    print(f"🎵 需要补全音频: {len(tasks)}个知识点\n")
    
    completed = 0
    for i, (json_path, text, voice, audio_path) in enumerate(tasks):
        topic_name = json.load(open(json_path, 'r', encoding='utf-8')).get('name', '')
        age_group = json.load(open(json_path, 'r', encoding='utf-8')).get('age_group', json.load(open(json_path, 'r', encoding='utf-8')).get('grade', ''))
        
        if (i + 1) % 10 == 0:
            print(f"\n进度: [{i+1}/{len(tasks)}] 已完成 {completed} 个\n")
        
        print(f"[{i+1}/{len(tasks)}] {topic_name} ({age_group})", end=" ", flush=True)
        
        # 拼接完整文本
        full_text = f"{topic_name}。{text}"
        
        if await generate_audio(full_text, audio_path, voice):
            print("✅")
            completed += 1
        else:
            print("❌")
        
        await asyncio.sleep(REQUEST_DELAY)
    
    print(f"\n✅ 完成: {completed}/{len(tasks)}")

if __name__ == "__main__":
    asyncio.run(fix_missing_audio())