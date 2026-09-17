#!/usr/bin/env python3
"""补充生成缺失的初中知识点"""
import asyncio, aiohttp, json, os, edge_tts, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"
REQUEST_DELAY = 4.5

VOICE_MAP = {
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

# 缺失的知识点列表
MISSING_TOPICS = [
    # 数学
    ('math', '七年级上', 'math_equation_1', '一元一次方程', '解方程与实际问题'),
    ('math', '七年级上', 'math_equation_2', '二元一次方程组', '代入消元与加减消元'),
    ('math', '七年级上', 'math_inequality', '一元一次不等式', '不等式性质与解法'),
    ('math', '七年级上', 'math_stats_1', '数据的收集', '调查方法与图表'),
    ('math', '七年级下', 'math_triangle_1', '三角形性质', '内角和与外角'),
    ('math', '八年级上', 'math_triangle_2', '全等三角形', '判定定理与应用'),
    ('math', '八年级下', 'math_func_linear', '一次函数', '图像与性质'),
    ('math', '八年级下', 'math_stats_2', '数据分析', '平均数中位数众数'),
    # 语文
    ('chinese', '七年级上', 'hist_classical_1', '文言文字词', '常用文言实词虚词'),
    ('chinese', '七年级下', 'hist_modern_read', '说明文阅读', '说明方法与顺序'),
    ('chinese', '八年级上', 'hist_classical_2', '古诗文鉴赏', '诗词意象与情感'),
    ('chinese', '八年级下', 'hist_modern_write', '议论文阅读', '论点论据论证'),
    ('chinese', '九年级上', 'hist_classical_3', '文言文翻译', '直译与意译'),
    ('chinese', '九年级下', 'hist_modern_narr', '记叙文阅读', '叙事技巧与情感'),
    ('chinese', '五年级', 'write_narr_1', '记事作文', '六要素完整'),
    ('chinese', '六年级', 'write_narr_2', '写人作文', '人物描写方法'),
    ('chinese', '七年级', 'write_narr_3', '抒情散文', '借景抒情'),
    ('chinese', '八年级', 'write_argu_1', '论点提炼', '中心论点明确'),
    ('chinese', '九年级', 'write_argu_2', '论据选择', '典型论据运用'),
    # 英语
    ('english', '七年级上', 'eng_grammar_1', '一般现在时', 'be动词与实义动词'),
    ('english', '七年级下', 'eng_grammar_2', '现在进行时', 'be doing结构'),
    ('english', '八年级上', 'eng_grammar_3', '一般过去时', '动词过去式'),
    ('english', '八年级下', 'eng_grammar_4', '一般将来时', 'will/be going to'),
    ('english', '九年级', 'eng_grammar_5', '现在完成时', 'have/has done'),
    ('english', '七年级', 'eng_vocab_1', '七年级核心词汇', '课标1600词'),
    ('english', '八年级', 'eng_vocab_2', '八年级核心词汇', '课标2400词'),
    ('english', '九年级', 'eng_vocab_3', '中考核心词汇', '课标3000词'),
    # 物理
    ('physics', '八年级上', 'phys_mech_1', '运动的描述', '速度参照系'),
    ('physics', '八年级上', 'phys_opt_1', '光的传播', '直线传播与反射'),
    ('physics', '八年级下', 'phys_mech_2', '力与运动', '牛顿第一定律'),
    ('physics', '八年级下', 'phys_opt_2', '透镜成像', '凸透镜成像规律'),
    ('physics', '九年级', 'phys_energy_1', '功与功率', '计算与应用'),
    ('physics', '九年级', 'phys_energy_2', '电功率', '电路计算与安全用电'),
    # 化学
    ('chemistry', '九年级上', 'chem_basic_1', '物质的变化', '物理变化与化学变化'),
    ('chemistry', '九年级上', 'chem_basic_2', '空气与氧气', '空气成分与氧气性质'),
    ('chemistry', '九年级上', 'chem_basic_3', '水与溶液', '水的组成与溶液概念'),
    ('chemistry', '九年级下', 'chem_elem_1', '金属与金属矿物', '金属性质与冶炼'),
    ('chemistry', '九年级下', 'chem_elem_2', '酸与碱', '酸碱性质与中和反应'),
    # 生物
    ('biology', '七年级上', 'bio_cell_1', '细胞结构与功能', '动植物细胞对比'),
    ('biology', '七年级上', 'bio_cell_2', '细胞分裂分化', '细胞生命周期'),
    ('biology', '七年级上', 'bio_org_1', '绿色植物', '光合作用与呼吸作用'),
    ('biology', '七年级下', 'bio_org_2', '人体生理', '消化系统与循环系统'),
    # 历史
    ('history', '七年级上', 'hist_primitive_1', '早期人类', '元谋人北京人'),
    ('history', '七年级上', 'hist_dynasty_1', '夏商周', '早期国家与社会变革'),
    ('history', '七年级上', 'hist_dynasty_2', '秦汉统一', '秦统一与汉武帝'),
    ('history', '七年级下', 'hist_feudal_1', '三国两晋南北朝', '政权分立与民族交融'),
    ('history', '七年级下', 'hist_feudal_2', '隋唐盛世', '贞观之治与开元盛世'),
    ('history', '八年级上', 'hist_modern_1', '鸦片战争', '虎门销烟与南京条约'),
    ('history', '八年级上', 'hist_modern_2', '辛亥革命', '孙中山与共和'),
    ('history', '八年级下', 'hist_contemp_1', '新中国成立', '1949年建国'),
    ('history', '八年级下', 'hist_contemp_2', '改革开放', '十一届三中全会'),
    # 地理
    ('geography', '七年级上', 'geo_earth_1', '地球形状大小', '地球仪与经纬网'),
    ('geography', '七年级上', 'geo_earth_2', '地图阅读', '比例尺与图例'),
    ('geography', '七年级上', 'geo_climate_1', '天气与气候', '天气预报与气候类型'),
    ('geography', '八年级上', 'geo_china_1', '中国地形', '三大阶梯与主要地形'),
    ('geography', '八年级上', 'geo_china_2', '中国气候', '季风气候特征'),
    ('geography', '八年级上', 'geo_china_3', '中国河流', '长江黄河特征'),
    # 道德与法治
    ('morality', '七年级上', 'mor_law_1', '法律的特征', '法律与道德区别'),
    ('morality', '七年级下', 'mor_law_2', '未成年人保护', '四大保护体系'),
    ('morality', '八年级上', 'mor_const_1', '宪法是根本法', '宪法地位与作用'),
    ('morality', '八年级下', 'mor_const_2', '公民基本权利', '权利义务关系'),
]

async def generate_topic(subject, grade, topic_id, topic_name, focus, semaphore):
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
    print(f"🚀 开始补充生成缺失内容... ({len(MISSING_TOPICS)}个知识点)\n")
    
    semaphore = asyncio.Semaphore(2)
    results = await asyncio.gather(*[generate_topic(*t, semaphore) for t in MISSING_TOPICS])
    
    completed = sum(1 for r in results if r)
    print(f"\n✅ 完成: {completed}/{len(MISSING_TOPICS)}")

if __name__ == "__main__":
    asyncio.run(main())