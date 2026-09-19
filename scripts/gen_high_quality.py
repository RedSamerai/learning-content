#!/usr/bin/env python3
"""
高质量内容生成器 - 按新课标补全各年级缺失知识点
严格控制RPM≤20
"""
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
    "初中": "zh-CN-YunxiNeural",
    "七年级": "zh-CN-YunxiNeural",
    "八年级": "zh-CN-YunxiNeural",
    "九年级": "zh-CN-YunxiNeural"
}

def get_voice(grade):
    for key, voice in VOICE_MAP.items():
        if key in grade:
            return voice
    return "zh-CN-XiaoxiaoNeural"

async def call_agnes(prompt, max_tokens=800):
    """调用AGNES API，严格控制频率"""
    global last_request_time
    now = time.time()
    elapsed = now - last_request_time
    if elapsed < REQUEST_DELAY:
        await asyncio.sleep(REQUEST_DELAY - elapsed)
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "agnes-2.5-flash",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }
        try:
            async with session.post(
                "https://apihub.agnes-ai.com/v1/chat/completions",
                headers=headers, json=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    result = await resp.json()
                    return result['choices'][0]['message']['content']
                return None
        except Exception as e:
            print(f"    API错误: {e}")
            return None

def gen_image(topic_name, grade, subject):
    """生成主题图片"""
    from PIL import Image, ImageDraw, ImageFont
    
    w, h = 1024, 768
    img = Image.new('RGB', (w, h), color='#F5F7FA')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 48)
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
    except:
        title_font = ImageFont.load_default()
        font = title_font
    
    # 顶部标题栏
    draw.rectangle([50, 50, w-50, 150], fill='#2C3E50')
    draw.text((w//2, 85), f"{grade} · {topic_name}", font=title_font, fill='white', anchor='mm')
    
    # 科目颜色
    colors = {
        'math': '#FF6B6B', 'chinese': '#4ECDC4', 'english': '#45B7D1',
        'science': '#96CEB4', 'physics': '#DDA0DD', 'chemistry': '#98D8C8',
        'history': '#BB8FCE', 'geography': '#85C1E9', 'morality': '#FFEAA7'
    }
    color = colors.get(subject, '#BDC3C7')
    
    # 中心图案
    center_y = 450
    icons = {'math': '🔢', 'chinese': '📖', 'english': '🔤', 'science': '🔬',
             'morality': '❤️', 'physics': '⚡', 'chemistry': '🧪', 'biology': '🧬',
             'history': '📜', 'geography': '🌍'}
    icon = icons.get(subject, '📚')
    draw.text((w//2, center_y), icon, font=title_font, fill=color)
    
    # 装饰
    shapes = [(200, 300, 300, 400, '#FF6B6B'), (700, 300, 800, 400, '#4ECDC4'),
              (200, 550, 300, 650, '#45B7D1'), (700, 550, 800, 650, '#96CEB4')]
    for x1, y1, x2, y2, c in shapes:
        draw.rounded_rectangle([x1, y1, x2, y2], radius=20, fill=c)
    
    return img

async def generate_audio(text, output_path, voice):
    """生成音频"""
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+5%")
        await communicate.save(str(output_path))
        return True
    except Exception as e:
        print(f"      音频生成失败: {e}")
        return False

async def create_topic(topic, quality_check=True):
    """创建高质量知识点"""
    topic_id = topic['topic_id']
    name = topic['name']
    grade = topic['grade']
    subject = topic['subject']
    focus = topic['focus']
    
    dir_path = Path(f'output/{subject}/{grade}/{topic_id}')
    dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[{topic_id}] {name} ({grade})", end=" ", flush=True)
    
    # 1. 生成详细讲解
    explain_prompt = f"""你是{grade}的{subject}老师，请详细讲解'{name}'这个知识点。
要求：
1. 用通俗的语言解释概念（200-300字）
2. 至少举2个生活中的例子帮助理解
3. 给出核心公式/定理（如有）
4. 提醒常见错误和易错点
5. 给出记忆技巧（如有）
请用 markdown 格式输出。"""
    
    explanation = await call_agnes(explain_prompt)
    if not explanation:
        print("❌ 讲解生成失败")
        return False
    
    # 2. 生成练习题
    quiz_prompt = f"""为'{name}'（{grade}{subject}）设计4道选择题。
要求：
1. 题目情景化，不要空洞
2. 包含A/B/C/D四个选项
3. 标出正确答案
4. 每道题给出详细解析（为什么选这个，其他选项为什么错）
5. 难度：基础题2道，提高题2道
用 markdown 格式输出。"""
    
    quiz = await call_agnes(quiz_prompt)
    
    # 3. 创建JSON
    content = {
        "topic_id": topic_id,
        "name": name,
        "grade": grade,
        "subject": subject,
        "focus": focus,
        "explanation": explanation,
        "quiz": quiz or "",
        "image": "image.png",
        "audio": ["audio_concept.mp3", "audio_explanation.mp3"]
    }
    
    json_path = dir_path / f"{topic_id}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    # 4. 生成图片
    img = gen_image(name, grade, subject)
    img.save(dir_path / "image.png")
    
    # 5. 生成音频
    voice = get_voice(grade)
    audio_text = f"{name}。{explanation}"
    if quiz:
        audio_text += f"下面是练习题：{quiz[:500]}..."
    
    await generate_audio(audio_text, dir_path / "audio_concept.mp3", voice)
    await generate_audio(explanation, dir_path / "audio_explanation.mp3", voice)
    
    print("✅")
    return True

# ========== P0阶段：九年级（最紧急）==========
TOPICS_JIUNIANJI = [
    # 数学（应55个，现有8个，缺47个）
    {"topic_id": "math_j9_equation2", "name": "一元二次方程的解法", "grade": "九年级上", "subject": "math", "focus": "公式法与因式分解"},
    {"topic_id": "math_j9_discriminant", "name": "根的判别式", "grade": "九年级上", "subject": "math", "focus": "判断根的情况"},
    {"topic_id": "math_j9_vieta", "name": "根与系数的关系", "grade": "九年级上", "subject": "math", "focus": "韦达定理应用"},
    {"topic_id": "math_j9_quadratic_graph", "name": "二次函数的图像", "grade": "九年级上", "subject": "math", "focus": "抛物线性质"},
    {"topic_id": "math_j9_quadratic_vertex", "name": "二次函数最值", "grade": "九年级上", "subject": "math", "focus": "顶点与最值"},
    {"topic_id": "math_j9_quadratic_app", "name": "二次函数应用", "grade": "九年级上", "subject": "math", "focus": "实际问题建模"},
    {"topic_id": "math_j9_circle_angle", "name": "圆心角与圆周角", "grade": "九年级上", "subject": "math", "focus": "角度关系"},
    {"topic_id": "math_j9_circle_tangent", "name": "圆的切线", "grade": "九年级上", "subject": "math", "focus": "切线性质"},
    {"topic_id": "math_j9_rotation", "name": "图形的旋转", "grade": "九年级上", "subject": "math", "focus": "旋转性质与应用"},
    {"topic_id": "math_j9_probability", "name": "概率的计算", "grade": "九年级下", "subject": "math", "focus": "列举法求概率"},
    {"topic_id": "math_j9_similar", "name": "相似三角形的判定", "grade": "九年级下", "subject": "math", "focus": "三种判定方法"},
    {"topic_id": "math_j9_trig", "name": "锐角三角函数", "grade": "九年级下", "subject": "math", "focus": "sin cos tan"},
    {"topic_id": "math_j9_view", "name": "视图与投影", "grade": "九年级下", "subject": "math", "focus": "三视图绘制"},
    {"topic_id": "math_j9_inverse", "name": "反比例函数", "grade": "九年级下", "subject": "math", "focus": "图像与性质"},
    
    # 化学（应20+个，现有5个，缺15+）
    {"topic_id": "chem_j9_equation", "name": "化学方程式的书写", "grade": "九年级上", "subject": "chemistry", "focus": "配平方法"},
    {"topic_id": "chem_j9_calc", "name": "根据化学方程式计算", "grade": "九年级上", "subject": "chemistry", "focus": "质量关系"},
    {"topic_id": "chem_j9_solution", "name": "溶液的浓度", "grade": "九年级上", "subject": "chemistry", "focus": "溶质质量分数"},
    {"topic_id": "chem_j9_crystal", "name": "结晶方法", "grade": "九年级上", "subject": "chemistry", "focus": "蒸发与降温结晶"},
    {"topic_id": "chem_j9_acid_base", "name": "酸碱盐的通性", "grade": "九年级下", "subject": "chemistry", "focus": "化学性质总结"},
    {"topic_id": "chem_j9_material", "name": "金属材料", "grade": "九年级下", "subject": "chemistry", "focus": "合金与性质"},
    {"topic_id": "chem_j9_organic", "name": "有机物简介", "grade": "九年级下", "subject": "chemistry", "focus": "甲烷乙醇"},
    {"topic_id": "chem_j9_nutrition", "name": "化学与营养", "grade": "九年级下", "subject": "chemistry", "focus": "六大营养素"},
    
    # 物理（应20+个，现有4个，缺16+）
    {"topic_id": "phys_j9_ohm", "name": "欧姆定律", "grade": "九年级", "subject": "physics", "focus": "I=U/R"},
    {"topic_id": "phys_j9_power", "name": "电功率计算", "grade": "九年级", "subject": "physics", "focus": "P=UI"},
    {"topic_id": "phys_j9_heat", "name": "焦耳定律", "grade": "九年级", "subject": "physics", "focus": "电热计算"},
    {"topic_id": "phys_j9_electromagnet", "name": "电磁感应", "grade": "九年级", "subject": "physics", "focus": "发电机原理"},
    {"topic_id": "phys_j9_safety", "name": "安全用电", "grade": "九年级", "subject": "physics", "focus": "触电与防护"},
    
    # 语文（应50+个，现有3个，缺47+）
    {"topic_id": "chinese_j9_classical", "name": "文言文翻译技巧", "grade": "九年级", "subject": "chinese", "focus": "实词虚词积累"},
    {"topic_id": "chinese_j9_read", "name": "现代文阅读方法", "grade": "九年级", "subject": "chinese", "focus": "理解赏析技巧"},
    {"topic_id": "chinese_j9_argument", "name": "议论文写作", "grade": "九年级", "subject": "chinese", "focus": "论点论据论证"},
    {"topic_id": "chinese_j9_poem", "name": "古诗词鉴赏", "grade": "九年级", "subject": "chinese", "focus": "意象意境情感"},
    
    # 英语（应50+个，现有2个，缺48+）
    {"topic_id": "english_j9_tense", "name": "英语时态总结", "grade": "九年级", "subject": "english", "focus": "三大时态对比"},
    {"topic_id": "english_j9_clause", "name": "定语从句入门", "grade": "九年级", "subject": "english", "focus": "that which用法"},
    {"topic_id": "english_j9_reading", "name": "阅读理解策略", "grade": "九年级", "subject": "english", "focus": "寻读略读技巧"},
    {"topic_id": "english_j9_writing", "name": "书面表达技巧", "grade": "九年级", "subject": "english", "focus": "句式升级"},
    
    # 历史/地理（补充）
    {"topic_id": "history_j9_china", "name": "中国近现代史", "grade": "九年级", "subject": "history", "focus": "屈辱与抗争"},
    {"topic_id": "geography_j9_region", "name": "中国地理分区", "grade": "九年级", "subject": "geography", "focus": "四大区域特征"},
]

async def main():
    print("=" * 70)
    print("高质量内容生成 - P0阶段（九年级优先）")
    print(f"知识点数量: {len(TOPICS_JIUNIANJI)}个")
    print(f"预计时间: {len(TOPICS_JIUNIANJI) * REQUEST_DELAY * 3 / 60:.1f} 分钟")
    print("=" * 70)
    
    completed = 0
    failed = 0
    
    for i, topic in enumerate(TOPICS_JIUNIANJI):
        if (i + 1) % 5 == 0:
            print(f"\n进度: [{i+1}/{len(TOPICS_JIUNIANJI)}] 完成:{completed} 失败:{failed}\n")
        
        if await create_topic(topic):
            completed += 1
        else:
            failed += 1
        
        await asyncio.sleep(REQUEST_DELAY)
    
    print(f"\n{'='*70}")
    print(f"✅ 完成: {completed}")
    print(f"❌ 失败: {failed}")
    print(f"📊 总计: {len(TOPICS_JIUNIANJI)}")
    print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(main())