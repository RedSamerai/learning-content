#!/usr/bin/env python3
"""生成小学2-6年级核心知识点"""
import asyncio, aiohttp, json, os, edge_tts
from PIL import Image, ImageDraw, ImageFont
import numpy as np

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

VOICE_MAP = {
    '一年级': 'zh-CN-XiaoxiaoNeural',
    '二年级': 'zh-CN-XiaoxiaoNeural',
    '三年级': 'zh-CN-XiaoxiaoNeural',
    '四年级': 'zh-CN-XiaoxiaoNeural',
    '五年级': 'zh-CN-XiaoxiaoNeural',
    '六年级': 'zh-CN-XiaoxiaoNeural',
}

async def call_agnes(prompt, model="agnes-2.5-flash"):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
        data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 800}
        async with session.post(f"{AGNES_BASE_URL}/chat/completions", headers=headers, json=data) as resp:
            if resp.status == 200:
                return (await resp.json())['choices'][0]['message']['content']
            return None

async def gen_image(topic, grade):
    prompts = {
        'math': f"小学数学{grade}教材插图风格，简洁清晰的教学图示，教育性质，无文字标注",
        'chinese': f"小学语文{grade}课文插图，温馨明亮，适合儿童观看",
        'science': f"小学科学{grade}实验插图，清晰展示科学现象，教育用途",
        'morality': f"小学道德与法治{grade}插图，积极向上，色彩柔和"
    }
    subject = 'chinese' if topic.startswith('py') or topic.startswith('zi') or topic.startswith('wen') or topic.startswith('poem') or topic.startswith('read') else 'math' if topic.startswith('math') else 'science' if topic.startswith('sci') else 'morality'
    prompt = prompts.get(subject, prompts['math'])
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "agnes-image-2.1-flash", "prompt": prompt, "size": "1024x768"}
        async with session.post(f"{AGNES_BASE_URL}/images/generations", headers=headers, json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                if 'data' in result and result['data']:
                    url = result['data'][0].get('url')
                    if url:
                        async with session.get(url) as img_resp:
                            content = await img_resp.read()
                            return content
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
    
    draw.rectangle([50, 50, w-50, 150], fill='#2C3E50', outline=None)
    draw.text((w//2, 85), f"小学{grade} · {topic}", font=title_font, fill='white', anchor='mm')
    
    if 'math' in topic.lower() or topic.startswith('math'):
        shapes = [('circle', '#FF6B6B'), ('rect', '#4ECDC4'), ('triangle', '#45B7D1')]
        positions = [(200, 350), (512, 350), (824, 350)]
        for i, ((shape, color), (x, y)) in enumerate(zip(shapes, positions)):
            if shape == 'circle':
                draw.ellipse([x-80, y-80, x+80, y+80], fill=color, outline=None)
            elif shape == 'rect':
                draw.rectangle([x-80, y-80, x+80, y+80], fill=color, outline=None)
            elif shape == 'triangle':
                draw.polygon([(x, y-80), (x-80, y+80), (x+80, y+80)], fill=color)
        draw.text((w//2, 550), "图形认知", font=font, fill='#2C3E50', anchor='mm')
    elif topic.startswith('py'):
        pinyins = ['ā', 'á', 'ǎ', 'à', 'ō', 'ó', 'ǒ', 'ò']
        for i, p in enumerate(pinyins):
            x = 150 + (i % 4) * 220
            y = 250 + (i // 4) * 180
            draw.ellipse([x, y, x+160, y+160], fill=colors[i % len(colors)], outline=None)
            draw.text((x+80, y+80), p, font=title_font, fill='white', anchor='mm')
        draw.text((w//2, 650), "拼音学习", font=font, fill='#2C3E50', anchor='mm')
    elif topic.startswith('sci'):
        elements = ['🌱', '💧', '☀️', '🌍']
        for i, e in enumerate(elements):
            x = 200 + i * 200
            draw.text((x, 300), e, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "科学探索", font=font, fill='#2C3E50', anchor='mm')
    else:
        icons = ['👨‍👩‍👧', '🏫', '🤝', '❤️']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "品德培养", font=font, fill='#2C3E50', anchor='mm')
    
    return img

async def gen_audio(topic_name, grade, voice):
    try:
        now = edge_tts.Communicate(topic_name, voice)
        audio_path = f"audio/intro.mp3"
        await now.save(audio_path)
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        os.remove(audio_path)
        return audio_data
    except:
        return None

async def generate_topic(topic_id, topic_name, grade, subject, focus):
    out_dir = Path(f"output/{subject}/{grade}/{topic_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if (out_dir / f"{topic_id}.json").exists():
        return True
    
    explanation = await call_agnes(
        f"为小学{grade}学生讲解'{topic_name}'，{focus}。用简单易懂的语言，200字以内。",
        "agnes-2.5-flash"
    )
    
    quiz = await call_agnes(
        f"出2道小学{grade}数学选择题，关于'{topic_name}'，格式：题目、选项A/B/C、正确答案。",
        "agnes-2.5-flash"
    ) if subject == 'math' else None
    
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
        "audio": ["audio_intro.mp3"],
        "tags": [subject, grade],
        "difficulty": min(1 + int(grade[0]) if grade[0].isdigit() else 1, 6),
        "created": "2026-09-17"
    }
    
    (out_dir / f"{topic_id}.json").write_text(json.dumps(content, ensure_ascii=False, indent=2))
    print(f"   ✅ {topic_name}")
    return True

async def main():
    with open('knowledge_graph_k12_full.json', 'r') as f:
        g = json.load(f)
    
    tasks = []
    for s in g['subjects']:
        subj = s['subject_id'].strip()
        for a in s.get('areas', []):
            for o in a.get('objectives', []):
                for t in o.get('topics', []):
                    grade = t.get('grade', '')
                    if '幼小衔接' in grade or '幼儿园' in grade or '小班' in grade or '中班' in grade or '大班' in grade:
                        continue
                    tasks.append((t['topic_id'], t['name'], grade, subj, t.get('focus', '')))
    
    print(f"🚀 开始生成小学内容... ({len(tasks)}个知识点)\n")
    
    results = await asyncio.gather(*[generate_topic(*t) for t in tasks])
    completed = sum(1 for r in results if r)
    print(f"\n✅ 完成: {completed}/{len(tasks)}")

if __name__ == "__main__":
    from pathlib import Path
    asyncio.run(main())