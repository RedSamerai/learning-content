#!/usr/bin/env python3
"""生成所有缺失的音频 - 使用Edge TTS"""
import asyncio, aiohttp, json, time, os, edge_tts
from pathlib import Path

REQUEST_DELAY = 4.5
last_request_time = 0

def get_voice(grade):
    if '幼' in grade or '小' in grade or '班' in grade:
        return 'zh-CN-XiaoyiNeural'
    return 'zh-CN-XiaoxiaoNeural'

async def gen_audio(text, voice, output_path):
    """生成音频并保存到指定路径"""
    try:
        comm = edge_tts.Communicate(text, voice)
        await comm.save(str(output_path))
        return True
    except Exception as e:
        return False

async def fix_one(p):
    """修复单个知识点的音频"""
    global last_request_time
    
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        topic_name = data.get('name', '')
        grade = data.get('grade', data.get('age_group', ''))
        explanation = data.get('explanation', '')
        
        if not topic_name:
            return False
        
        voice = get_voice(grade)
        
        # 检查是否已有音频
        audio_files = []
        for af in data.get('audio', []):
            ap = p.parent / af
            if ap.exists() and ap.stat().st_size > 0:
                audio_files.append(af)
        
        if len(audio_files) >= 2:  # 已有足够音频
            return True
        
        # 生成缺失的音频
        audio_dir = p.parent / 'audio'
        audio_dir.mkdir(exist_ok=True)
        
        # 概念音频
        concept_path = audio_dir / 'audio_concept.mp3'
        if not concept_path.exists() or concept_path.stat().st_size == 0:
            success = await gen_audio(topic_name, voice, concept_path)
            if success:
                audio_files.append('audio_concept.mp3')
        
        # 等待避免限速
        now = time.time()
        elapsed = now - last_request_time
        if elapsed < REQUEST_DELAY:
            await asyncio.sleep(REQUEST_DELAY - elapsed)
        
        # 解释音频
        expl_path = audio_dir / 'audio_explanation.mp3'
        expl_text = explanation if explanation else topic_name
        if not expl_path.exists() or expl_path.stat().st_size == 0:
            success = await gen_audio(expl_text, voice, expl_path)
            if success:
                audio_files.append('audio_explanation.mp3')
        
        # 更新JSON
        data['audio'] = audio_files
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False

async def main():
    # 找出需要生成音频的文件
    tasks = []
    for p in Path('output').rglob('*.json'):
        if p.parent.name in ['image', 'audio']:
            continue
        
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            audio_count = 0
            for af in data.get('audio', []):
                ap = p.parent / af
                if ap.exists() and ap.stat().st_size > 0:
                    audio_count += 1
            
            # 如果音频不足2个，需要修复
            if audio_count < 2:
                tasks.append(p)
        except:
            pass
    
    print(f"🔊 需要生成音频: {len(tasks)}个文件\n")
    
    completed = 0
    for i, p in enumerate(tasks):
        topic_name = json.load(open(p, 'r', encoding='utf-8')).get('name', '')
        grade = json.load(open(p, 'r', encoding='utf-8')).get('grade', json.load(open(p, 'r', encoding='utf-8')).get('age_group', ''))
        
        if (i + 1) % 20 == 0:
            print(f"\n进度: [{i+1}/{len(tasks)}] 已完成 {completed} 个\n")
        
        print(f"[{i+1}/{len(tasks)}] {topic_name} ({grade})", end=" ", flush=True)
        if await fix_one(p):
            print("✅")
            completed += 1
        else:
            print("❌")
    
    print(f"\n✅ 完成: {completed}/{len(tasks)}")
    
    # 最终统计
    total_audio = len(list(Path('output').rglob('*.mp3')))
    print(f"总音频文件数: {total_audio}")

if __name__ == "__main__":
    asyncio.run(main())