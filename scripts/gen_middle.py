#!/usr/bin/env python3
"""生成5-6年级和初中内容 - 低并发版本"""
import asyncio, aiohttp, json, os, edge_tts, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"
REQUEST_DELAY = 4.5  # 每分钟最多15次请求（4.5秒间隔）

VOICE_MAP = {
    '五年级': 'zh-CN-XiaoxiaoNeural',
    '六年级': 'zh-CN-XiaoxiaoNeural',
    '七年级': 'zh-CN-XiaoxiaoNeural',
    '八年级': 'zh-CN-XiaoxiaoNeural',
    '九年级': 'zh-CN-XiaoxiaoNeural',
}

last_request_time = 0

async def call_agnes(prompt, model="agnes-2.5-flash"):
    global last_request_time
    now = time.time()
    elapsed = now - last_request_time
    if elapsed < REQUEST_DELAY:
        await asyncio.sleep(REQUEST_DELAY - elapsed)
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
        data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 800}
        try:
            async with session.post(f"{AGNES_BASE_URL}/chat/completions", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    return (await resp.json())['choices'][0]['message']['content']
                elif resp.status == 429:
                    print(f"\n⚠️ 速率限制，等待20秒...")
                    await asyncio.sleep(20)
                    return await call_agnes(prompt, model)
                else:
                    print(f"\n❌ API错误: {resp.status}")
                    return None
        except Exception as e:
            print(f"\n❌ 请求失败: {e}")
            return None

async def gen_image(topic, grade):
    subject = 'chinese' if topic.startswith('hist') or topic.startswith('wen') or topic.startswith('poem') or topic.startswith('read') or topic.startswith('write') else 'math' if topic.startswith('math') else 'physics' if topic.startswith('phys') else 'chemistry' if topic.startswith('chem') else 'biology' if topic.startswith('bio') else 'history' if topic.startswith('hist') else 'geography' if topic.startswith('geo') else 'morality' if topic.startswith('mor') else 'english' if topic.startswith('eng') else 'general'
    
    prompts = {
        'chinese': f"初中语文{grade}课文插图，温馨明亮，适合青少年观看",
        'math': f"初中数学{grade}教材插图，简洁清晰的教学图示",
        'physics': f"初中物理{grade}实验插图，科学准确",
        'chemistry': f"初中化学{grade}实验插图，规范安全",
        'biology': f"初中生物{grade}插图，科学准确",
        'history': f"初中历史{grade}插图，历史场景还原",
        'geography': f"初中地理{grade}地图插图，清晰直观",
        'morality': f"初中道德与法治{grade}插图，积极向上",
        'english': f"初中英语{grade}插图，色彩明亮",
        'general': f"初中{grade}教材插图，教育性质"
    }
    prompt = prompts.get(subject, prompts['general'])
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "agnes-image-2.1-flash", "prompt": prompt, "size": "1024x768"}
        try:
            async with session.post(f"{AGNES_BASE_URL}/images/generations", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=90)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if 'data' in result and result['data']:
                        url = result['data'][0].get('url')
                        if url:
                            async with session.get(url) as img_resp:
                                return await img_resp.read()
        except:
            pass
    return None

def gen_pil_image(topic, grade, subject):
    w, h = 1024, 768
    img = Image.new('RGB', (w, h), color='#F5F7FA')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
        title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 48)
    except:
        font = ImageFont.load_default()
        title_font = font
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    draw.rectangle([50, 50, w-50, 150], fill='#2C3E50')
    draw.text((w//2, 85), f"{grade} · {topic}", font=title_font, fill='white', anchor='mm')
    
    if subject == 'math':
        shapes = [('circle', '#FF6B6B'), ('rect', '#4ECDC4'), ('triangle', '#45B7D1')]
        positions = [(200, 350), (512, 350), (824, 350)]
        for i, ((shape, color), (x, y)) in enumerate(zip(shapes, positions)):
            if shape == 'circle':
                draw.ellipse([x-80, y-80, x+80, y+80], fill=color)
            elif shape == 'rect':
                draw.rectangle([x-80, y-80, x+80, y+80], fill=color)
            elif shape == 'triangle':
                draw.polygon([(x, y-80), (x-80, y+80), (x+80, y+80)], fill=color)
        draw.text((w//2, 550), "数学学习", font=font, fill='#2C3E50', anchor='mm')
    elif subject in ['history', 'geography']:
        icons = ['📜', '🗺️', '🏛️', '⚔️']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "历史文化", font=font, fill='#2C3E50', anchor='mm')
    elif subject in ['physics', 'chemistry', 'biology']:
        icons = ['⚡', '🧪', '🧬', '🔬']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "科学探索", font=font, fill='#2C3E50', anchor='mm')
    else:
        icons = ['📖', '✏️', '🎨', '🎵']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "学习内容", font=font, fill='#2C3E50', anchor='mm')
    
    return img

async def gen_audio(topic_name, grade, voice):
    try:
        comm = edge_tts.Communicate(topic_name, voice)
        audio_path = f"audio/temp_{int(time.time())}.mp3"
        await comm.save(audio_path)
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        os.remove(audio_path)
        return audio_data
    except:
        return None

async def generate_topic(topic_id, topic_name, grade, subject, focus, semaphore):
    async with semaphore:
        out_dir = Path(f"output/{subject}/{grade}/{topic_id}")
        out_dir.mkdir(parents=True, exist_ok=True)
        
        if (out_dir / f"{topic_id}.json").exists():
            return True
        
        print(f"📚 {topic_name} ({grade})", end=" ", flush=True)
        
        explanation = await call_agnes(
            f"为{grade}学生讲解'{topic_name}'，{focus}。用简单易懂的语言，200字以内。",
            "agnes-2.5-flash"
        )
        
        if subject == 'math':
            quiz = await call_agnes(
                f"出2道{grade}数学选择题，关于'{topic_name}'。",
                "agnes-2.5-flash"
            )
        else:
            quiz = None
        
        image_content = await gen_image(topic_id, grade)
        if not image_content:
            img = gen_pil_image(topic_id, grade, subject)
            img.save(out_dir / "image.png")
        else:
            (out_dir / "image.png").write_bytes(image_content)
        
        voice = VOICE_MAP.get(grade, 'zh-CN-XiaoxiaoNeural')
        audio_data = await gen_audio(topic_name, grade, voice)
        if audio_data:
            (out_dir / "audio_intro.mp3").write_bytes(audio_data)
        
        content = {
            "topic_id": topic_id,
            "name": topic_name,
            "grade": grade,
            "subject": subject,
            "focus": focus,
            "explanation": explanation or "",
            "quiz": quiz or "",
            "image": "image.png",
            "audio": ["audio_intro.mp3"] if audio_data else [],
            "tags": [subject, grade],
            "difficulty": min(1 + int(grade[0]) if grade[0].isdigit() else 1, 9),
            "created": "2026-09-17"
        }
        
        (out_dir / f"{topic_id}.json").write_text(json.dumps(content, ensure_ascii=False, indent=2))
        print("✅")
        return True

async def main():
    with open('knowledge_graph_middle.json', 'r') as f:
        g = json.load(f)
    
    tasks = []
    for s in g['subjects']:
        subj = s['subject_id']
        for a in s.get('areas', []):
            for o in a.get('objectives', []):
                for t in o.get('topics', []):
                    grade = t.get('grade', '')
                    if any(g in grade for g in ['幼儿园', '小班', '中班', '大班', '幼小衔接']):
                        continue
                    tasks.append((t['topic_id'], t['name'], grade, subj, t.get('focus', '')))
    
    print(f"🚀 开始生成5-6年级和初中内容... ({len(tasks)}个知识点)")
    print(f"⏱️ 预计时间: {len(tasks) * 4.5 / 60:.1f} 分钟\n")
    
    semaphore = asyncio.Semaphore(2)
    results = await asyncio.gather(*[generate_topic(*t, semaphore) for t in tasks])
    
    completed = sum(1 for r in results if r)
    print(f"\n✅ 完成: {completed}/{len(tasks)}")

if __name__ == "__main__":
    asyncio.run(main())