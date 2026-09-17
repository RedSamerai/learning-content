#!/usr/bin/env python3
"""批量生成缺失的音频"""
import asyncio, aiohttp, json, time, os, edge_tts
from pathlib import Path

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
REQUEST_DELAY = 4.5

last_request_time = 0

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
            async with session.post(f"https://apihub.agnes-ai.com/v1/chat/completions", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    return (await resp.json())['choices'][0]['message']['content']
                return None
        except:
            return None

def get_voice(grade):
    if '幼' in grade or '小' in grade or '班' in grade:
        return 'zh-CN-XiaoyiNeural'
    return 'zh-CN-XiaoxiaoNeural'

async def gen_audio(text, voice):
    try:
        comm = edge_tts.Communicate(text, voice)
        audio_path = f"audio/temp_{int(time.time())}.mp3"
        await comm.save(audio_path)
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        os.remove(audio_path)
        return audio_data
    except Exception as e:
        return None

async def fix_one(p):
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        topic_name = data.get('name', '')
        grade = data.get('grade', data.get('age_group', ''))
        
        if not topic_name:
            return False
        
        # 补充explanation
        if not data.get('explanation') or len(data.get('explanation', '')) < 10:
            prompt = f"为{grade}学生讲解'{topic_name}'。用简单易懂的语言，150字以内。"
            explanation = await call_agnes(prompt)
            if explanation:
                data['explanation'] = explanation
        
        # 生成音频
        voice = get_voice(grade)
        audio_dir = p.parent / 'audio'
        audio_dir.mkdir(exist_ok=True)
        
        # 概念音频
        audio_concept = audio_dir / 'audio_concept.mp3'
        if not audio_concept.exists() or audio_concept.stat().st_size == 0:
            audio_data = await gen_audio(topic_name, voice)
            if audio_data:
                audio_concept.write_bytes(audio_data)
        
        # 解释音频
        audio_explanation = audio_dir / 'audio_explanation.mp3'
        expl_text = data.get('explanation', topic_name)
        if not audio_explanation.exists() or audio_explanation.stat().st_size == 0:
            audio_data = await gen_audio(expl_text, voice)
            if audio_data:
                audio_explanation.write_bytes(audio_data)
        
        # 更新audio字段
        audio_files = []
        for af in audio_dir.glob("*.mp3"):
            if af.stat().st_size > 0:
                audio_files.append(af.name)
        data['audio'] = audio_files
        
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False

async def main():
    # 找出需要修复的文件
    tasks = []
    for p in Path('output').rglob('*.json'):
        if p.parent.name in ['image', 'audio']:
            continue
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            # 检查是否缺少音频或文本
            has_audio = False
            for af in data.get('audio', []):
                if (p.parent / af).exists() and (p.parent / af).stat().st_size > 0:
                    has_audio = True
                    break
            if not has_audio or not data.get('explanation') or len(data.get('explanation', '')) < 10:
                tasks.append(p)
        except:
            pass
    
    print(f"🔧 需要修复: {len(tasks)}个文件\n")
    
    semaphore = asyncio.Semaphore(1)
    completed = 0
    
    for i, p in enumerate(tasks):
        async with semaphore:
            topic_name = json.load(open(p, 'r', encoding='utf-8')).get('name', '')
            grade = json.load(open(p, 'r', encoding='utf-8')).get('grade', json.load(open(p, 'r', encoding='utf-8')).get('age_group', ''))
            print(f"[{i+1}/{len(tasks)}] {topic_name} ({grade})", end=" ", flush=True)
            if await fix_one(p):
                print("✅")
                completed += 1
            else:
                print("❌")
    
    print(f"\n✅ 完成: {completed}/{len(tasks)}")

if __name__ == "__main__":
    asyncio.run(main())