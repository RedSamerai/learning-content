#!/usr/bin/env python3
"""修复缺失的音频和explanation"""
import asyncio, aiohttp, json, os, edge_tts, time
from pathlib import Path

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"
REQUEST_DELAY = 3.5

voice_map = {
    '一年级': 'zh-CN-XiaoxiaoNeural',
    '二年级': 'zh-CN-XiaoxiaoNeural',
    '三年级': 'zh-CN-XiaoxiaoNeural',
    '四年级': 'zh-CN-XiaoxiaoNeural',
    '五年级': 'zh-CN-XiaoxiaoNeural',
    '六年级': 'zh-CN-XiaoxiaoNeural',
}

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
            async with session.post(f"{AGNES_BASE_URL}/chat/completions", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    return (await resp.json())['choices'][0]['message']['content']
                return None
        except:
            return None

async def gen_audio(text, grade, voice):
    try:
        comm = edge_tts.Communicate(text, voice)
        audio_path = f"audio/temp_{int(time.time())}.mp3"
        await comm.save(audio_path)
        with open(audio_path, 'rb') as f:
            data = f.read()
        os.remove(audio_path)
        return data
    except:
        return None

async def fix_topic(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    topic_name = data.get('name', '')
    grade = data.get('grade', '')
    subject = data.get('subject', '')
    
    # 修复explanation
    if not data.get('explanation'):
        explanation = await call_agnes(f"为小学{grade}学生讲解'{topic_name}'，用简单易懂的语言，150字以内。")
        if explanation:
            data['explanation'] = explanation
    
    # 修复音频
    audio_path = Path(json_path).parent / 'audio_intro.mp3'
    if not audio_path.exists():
        voice = voice_map.get(grade, 'zh-CN-XiaoxiaoNeural')
        audio_text = f"{topic_name}。{data.get('explanation', '')[:100]}"
        audio_data = await gen_audio(audio_text, grade, voice)
        if audio_data:
            audio_path.write_bytes(audio_data)
            data['audio'] = ['audio_intro.mp3']
    
    # 保存
    with open(json_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return True

async def main():
    global last_request_time
    last_request_time = 0
    
    # 找出需要修复的文件
    issues = []
    for json_path in Path('output').rglob('*.json'):
        if json_path.parent.name in ['image', 'audio']:
            continue
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            topic_name = data.get('name', '')
            grade = data.get('grade', '')
            
            # 检查是否需要修复
            needs_fix = False
            if not data.get('explanation'):
                needs_fix = True
            audio_path = json_path.parent / 'audio_intro.mp3'
            if not audio_path.exists():
                needs_fix = True
            
            if needs_fix and '幼小衔接' not in grade and '幼儿园' not in grade:
                issues.append(json_path)
        except:
            pass
    
    print(f"🔧 需要修复: {len(issues)}个文件\n")
    
    for i, p in enumerate(issues):
        topic_name = json.load(open(p))['name']
        print(f"[{i+1}/{len(issues)}] 修复 {topic_name}...", end=" ", flush=True)
        await fix_topic(p)
        print("✅")
        await asyncio.sleep(0.5)
    
    print(f"\n✅ 修复完成: {len(issues)}个")

if __name__ == "__main__":
    asyncio.run(main())