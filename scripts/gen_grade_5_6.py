#!/usr/bin/env python3
"""补充小学5-6年级内容"""
import asyncio, aiohttp, json, os, edge_tts, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"
REQUEST_DELAY = 4.5

VOICE_MAP = {
    '一年级': 'zh-CN-XiaoxiaoNeural',
    '二年级': 'zh-CN-XiaoxiaoNeural',
    '三年级': 'zh-CN-XiaoxiaoNeural',
    '四年级': 'zh-CN-XiaoxiaoNeural',
    '五年级': 'zh-CN-XiaoxiaoNeural',
    '六年级': 'zh-CN-XiaoxiaoNeural',
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
    elif subject == 'chinese':
        icons = ['📖', '✏️', '🎨', '🎵']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "语文学习", font=font, fill='#2C3E50', anchor='mm')
    else:
        icons = ['📚', '🔬', '🌍', '🎨']
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

# 小学5-6年级知识点
TOPICS = [
    # 五年级数学
    ('五年级上', 'math', 'math_frac_1', '分数加减法', '异分母分数加减法'),
    ('五年级上', 'math', 'math_mult', '小数乘法', '小数乘法的计算方法'),
    ('五年级上', 'math', 'math_div', '小数除法', '小数除法的计算方法'),
    ('五年级上', 'math', 'math_area', '多边形面积', '平行四边形、三角形、梯形面积'),
    ('五年级上', 'math', 'math_equation', '简易方程', '用字母表示数、解方程'),
    ('五年级上', 'math', 'math_pos', '位置', '数对表示位置'),
    ('五年级上', 'math', 'math_prob', '可能性', '事件发生的可能性'),
    # 五年级语文
    ('五年级上', 'chinese', 'read_narr', '记叙文阅读', '抓住主要内容，体会思想感情'),
    ('五年级上', 'chinese', 'write_narr_5', '写一件小事', '内容具体，感情真实'),
    ('五年级上', 'chinese', 'poem_5', '古诗鉴赏', '理解诗意，体会情感'),
    ('五年级上', 'chinese', 'compose_5', '看图作文', '仔细观察图画，发挥想象'),
    # 六年级数学
    ('六年级上', 'math', 'math_frac_mul', '分数乘法', '分数乘整数、分数乘分数'),
    ('六年级上', 'math', 'math_frac_div', '分数除法', '分数除以整数、分数除以分数'),
    ('六年级上', 'math', 'math_ratio', '比和比例', '比的意义、比例的基本性质'),
    ('六年级上', 'math', 'math_percent', '百分数', '百分数的意义和读写'),
    ('六年级上', 'math', 'math_circle', '圆', '圆的周长和面积'),
    ('六年级上', 'math', 'math_cylinder', '圆柱与圆锥', '表面积和体积计算'),
    # 六年级语文
    ('六年级上', 'chinese', 'read_desc', '写景文章', '抓住特点，按顺序观察'),
    ('六年级上', 'chinese', 'write_obj', '写一种事物', '把特征写具体'),
    ('六年级上', 'chinese', 'poem_li', '古诗词背诵', '积累经典诗词'),
    ('六年级上', 'chinese', 'essay_6', '写读后感', '读懂原文，写出感受'),
    # 数学综合
    ('六年级上', 'math', 'math_stat', '统计图', '扇形统计图的认识和绘制'),
    ('六年级上', 'math', 'math_mix', '混合运算', '四则混合运算的顺序'),
]

async def generate_topic(grade, subject, topic_id, topic_name, focus, semaphore):
    async with semaphore:
        out_dir = Path(f"output/{subject}/{grade}/{topic_id}")
        out_dir.mkdir(parents=True, exist_ok=True)
        
        if (out_dir / f"{topic_id}.json").exists():
            return True
        
        print(f"📚 {grade}-{topic_name}", end=" ", flush=True)
        
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
        
        # 生成图片
        img = gen_pil_image(topic_id, grade, subject)
        img.save(out_dir / "image.png")
        
        # 生成音频
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
            "difficulty": 7 if grade.startswith("五年级") else 8,
            "created": "2026-09-17"
        }
        
        (out_dir / f"{topic_id}.json").write_text(json.dumps(content, ensure_ascii=False, indent=2))
        print("✅")
        return True

async def main():
    print(f"🚀 开始生成小学5-6年级内容... ({len(TOPICS)}个知识点)\n")
    
    semaphore = asyncio.Semaphore(1)
    results = await asyncio.gather(*[generate_topic(*t, semaphore) for t in TOPICS])
    
    completed = sum(1 for r in results if r)
    print(f"\n✅ 完成: {completed}/{len(TOPICS)}")

if __name__ == "__main__":
    asyncio.run(main())