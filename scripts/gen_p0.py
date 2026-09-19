#!/usr/bin/env python3
"""按新课标补全知识点 - 分批生成"""
import asyncio, aiohttp, json, time
from pathlib import Path

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
REQUEST_DELAY = 4.5
last_request_time = 0

# P0阶段知识点清单（缺失严重的年级）
TOPICS_P0 = [
    # 九年级
    {"topic_id": "math_equation_1", "name": "一元二次方程的解法", "grade": "九年级上", "subject": "math", "focus": "公式法与因式分解"},
    {"topic_id": "math_equation_2", "name": "根的判别式", "grade": "九年级上", "subject": "math", "focus": "判断根的情况"},
    {"topic_id": "math_equation_3", "name": "根与系数的关系", "grade": "九年级上", "subject": "math", "focus": "韦达定理应用"},
    {"topic_id": "math_quadratic_func", "name": "二次函数的图像", "grade": "九年级上", "subject": "math", "focus": "抛物线性质"},
    {"topic_id": "math_quadratic_app", "name": "二次函数最值问题", "grade": "九年级上", "subject": "math", "focus": "实际应用"},
    {"topic_id": "math_circle", "name": "圆的性质", "grade": "九年级上", "subject": "math", "focus": "圆心角圆周角"},
    {"topic_id": "math_rotate", "name": "图形的旋转", "grade": "九年级上", "subject": "math", "focus": "旋转性质"},
    
    {"topic_id": "math_stats_prob", "name": "概率的计算", "grade": "九年级下", "subject": "math", "focus": "列举法求概率"},
    {"topic_id": "math_similar", "name": "相似三角形的判定", "grade": "九年级下", "subject": "math", "focus": "三种判定方法"},
    {"topic_id": "math_trig", "name": "锐角三角函数", "grade": "九年级下", "subject": "math", "focus": "sin cos tan"},
    {"topic_id": "math_view", "name": "视图与投影", "grade": "九年级下", "subject": "math", "focus": "三视图"},
    
    {"topic_id": "chem_equation", "name": "化学方程式", "grade": "九年级上", "subject": "chemistry", "focus": "书写与计算"},
    {"topic_id": "chem_calc", "name": "根据化学方程式计算", "grade": "九年级上", "subject": "chemistry", "focus": "质量守恒"},
    {"topic_id": "chem_solution", "name": "溶液的浓度", "grade": "九年级上", "subject": "chemistry", "focus": "溶质质量分数"},
    {"topic_id": "chem_crystal", "name": "结晶方法", "grade": "九年级上", "subject": "chemistry", "focus": "蒸发与降温"},
    
    {"topic_id": "chem_acid_base_salt", "name": "酸碱盐的性质", "grade": "九年级下", "subject": "chemistry", "focus": "通性与反应"},
    {"topic_id": "chem_material", "name": "化学与材料", "grade": "九年级下", "subject": "chemistry", "focus": "金属材料"},
    {"topic_id": "chem_organic", "name": "有机物简介", "grade": "九年级下", "subject": "chemistry", "focus": "甲烷酒精"},
    {"topic_id": "chem_life", "name": "化学与生活", "grade": "九年级下", "subject": "chemistry", "focus": "营养素"},
    
    {"topic_id": "phys_circuit", "name": "欧姆定律", "grade": "九年级", "subject": "physics", "focus": "电流电压电阻关系"},
    {"topic_id": "phys_power_calc", "name": "电功与电功率", "grade": "九年级", "subject": "physics", "focus": "计算与应用"},
    {"topic_id": "phys_electric_heat", "name": "焦耳定律", "grade": "九年级", "subject": "physics", "focus": "电热计算"},
    {"topic_id": "phys_electromagnet", "name": "电磁感应", "grade": "九年级", "subject": "physics", "focus": "发电机原理"},
    
    {"topic_id": "chinese_classical_read", "name": "文言文阅读方法", "grade": "九年级", "subject": "chinese", "focus": "实词虚词翻译"},
    {"topic_id": "chinese_modern_read", "name": "现代文阅读技巧", "grade": "九年级", "subject": "chinese", "focus": "理解赏析"},
    {"topic_id": "chinese_argument_write", "name": "议论文写作", "grade": "九年级", "subject": "chinese", "focus": "论点论据论证"},
    {"topic_id": "chinese_poem_appreciation", "name": "古诗词鉴赏", "grade": "九年级", "subject": "chinese", "focus": "意象意境情感"},
    
    {"topic_id": "english_tense_review", "name": "英语时态总结", "grade": "九年级", "subject": "english", "focus": "三大时态对比"},
    {"topic_id": "english_clause", "name": "定语从句入门", "grade": "九年级", "subject": "english", "focus": "that which用法"},
    {"topic_id": "english_reading_skill", "name": "阅读理解策略", "grade": "九年级", "subject": "english", "focus": "寻读略读技巧"},
    {"topic_id": "english_writing_tips", "name": "书面表达技巧", "grade": "九年级", "subject": "english", "focus": "句式升级"},
    
    {"topic_id": "history_china_ancient", "name": "中国古代史梳理", "grade": "九年级", "subject": "history", "focus": "朝代更替"},
    {"topic_id": "history_china_modern", "name": "中国近现代史", "grade": "九年级", "subject": "history", "focus": "屈辱与抗争"},
    {"topic_id": "geography_china_region", "name": "中国地理分区", "grade": "九年级", "subject": "geography", "focus": "四大区域"},
    
    # 小学空缺年级
    {"topic_id": "math_py3_sub_100", "name": "100以内退位减法", "grade": "二年级下", "subject": "math", "focus": "竖式计算"},
    {"topic_id": "math_py3_mul", "name": "乘法口诀应用", "grade": "二年级下", "subject": "math", "focus": "解决实际问题"},
    {"topic_id": "math_py3_div", "name": "表内除法", "grade": "二年级下", "subject": "math", "focus": "除法的意义"},
    {"topic_id": "math_py3_length", "name": "长度单位换算", "grade": "二年级下", "subject": "math", "focus": "米与厘米"},
    {"topic_id": "math_py3_symmetry", "name": "图形的对称", "grade": "二年级下", "subject": "math", "focus": "轴对称图形"},
    
    {"topic_id": "math_py4_pos", "name": "位置与方向", "grade": "四年级下", "subject": "math", "focus": "用数对确定位置"},
    {"topic_id": "math_py4_triangle", "name": "三角形的特性", "grade": "四年级下", "subject": "math", "focus": "分类与内角和"},
    {"topic_id": "math_py4_decimal", "name": "小数的意义", "grade": "四年级下", "subject": "math", "focus": "读写与性质"},
    {"topic_id": "math_py4_add", "name": "小数加减法", "grade": "四年级下", "subject": "math", "focus": "计算与应用"},
    {"topic_id": "math_py4_stat", "name": "平均数与条形图", "grade": "四年级下", "subject": "math", "focus": "数据分析"},
    
    {"topic_id": "math_py5_geo", "name": "长方体与正方体", "grade": "五年级下", "subject": "math", "focus": "表面积体积"},
    {"topic_id": "math_py5_factor", "name": "因数与倍数", "grade": "五年级下", "subject": "math", "focus": "整除特征"},
    {"topic_id": "math_py5_prime", "name": "质数与合数", "grade": "五年级下", "subject": "math", "focus": "判断方法"},
    {"topic_id": "math_py5_fraction", "name": "分数的意义", "grade": "五年级下", "subject": "math", "focus": "与除法关系"},
    {"topic_id": "math_py5_fraction_add", "name": "分数加减法", "grade": "五年级下", "subject": "math", "focus": "异分母计算"},
    {"topic_id": "math_py5_stars", "name": "找规律填数", "grade": "五年级下", "subject": "math", "focus": "数列规律"},
    
    {"topic_id": "math_py6_neg", "name": "负数的认识", "grade": "六年级下", "subject": "math", "focus": "正负数意义"},
    {"topic_id": "math_py6_percent", "name": "百分数的意义", "grade": "六年级下", "subject": "math", "focus": "与分数关系"},
    {"topic_id": "math_py6_cylinder", "name": "圆柱的认识", "grade": "六年级下", "subject": "math", "focus": "侧面展开图"},
    {"topic_id": "math_py6_cone", "name": "圆锥的认识", "grade": "六年级下", "subject": "math", "focus": "高与体积"},
    {"topic_id": "math_py6_ratio", "name": "比例的意义", "grade": "六年级下", "subject": "math", "focus": "解比例"},
    {"topic_id": "math_py6_map", "name": "比例尺", "grade": "六年级下", "subject": "math", "focus": "距离计算"},
    
    # 初中其他年级
    {"topic_id": "math_jun_rational", "name": "有理数的概念", "grade": "七年级上", "subject": "math", "focus": "正负数分类"},
    {"topic_id": "math_jun_numline", "name": "数轴与相反数", "grade": "七年级上", "subject": "math", "focus": "数形结合"},
    {"topic_id": "math_jun_abs", "name": "绝对值", "grade": "七年级上", "subject": "math", "focus": "几何意义"},
    {"topic_id": "math_jun_add", "name": "有理数加减法", "grade": "七年级上", "subject": "math", "focus": "运算法则"},
    {"topic_id": "math_jun_mul", "name": "有理数乘除法", "grade": "七年级上", "subject": "math", "focus": "符号法则"},
    
    {"topic_id": "math_jun_eq", "name": "一元一次方程", "grade": "七年级下", "subject": "math", "focus": "解法与应用"},
    {"topic_id": "math_jun_system", "name": "二元一次方程组", "grade": "七年级下", "subject": "math", "focus": "消元法"},
    {"topic_id": "math_jun_ineq", "name": "一元一次不等式", "grade": "七年级下", "subject": "math", "focus": "解集表示"},
    {"topic_id": "math_jun_coord", "name": "平面直角坐标系", "grade": "七年级下", "subject": "math", "focus": "点的坐标"},
    
    {"topic_id": "math_jun2_triangle", "name": "三角形的分类", "grade": "八年级上", "subject": "math", "focus": "按边按角分类"},
    {"topic_id": "math_jun2_congruent", "name": "全等三角形的判定", "grade": "八年级上", "subject": "math", "focus": "SSS SAS ASA"},
    {"topic_id": "math_jun2_axis", "name": "轴对称图形", "grade": "八年级上", "subject": "math", "focus": "性质与应用"},
    {"topic_id": "math_jun2_power", "name": "整式的乘除", "grade": "八年级上", "subject": "math", "focus": "公式应用"},
    {"topic_id": "math_jun2_frac", "name": "分式的运算", "grade": "八年级上", "subject": "math", "focus": "约分通分"},
    
    {"topic_id": "math_jun2_root", "name": "二次根式", "grade": "八年级下", "subject": "math", "focus": "化简与运算"},
    {"topic_id": "math_jun2_pythagoras", "name": "勾股定理", "grade": "八年级下", "subject": "math", "focus": "证明与应用"},
    {"topic_id": "math_jun2_parallelogram", "name": "平行四边形", "grade": "八年级下", "subject": "math", "focus": "性质判定"},
    {"topic_id": "math_jun2_linear", "name": "一次函数", "grade": "八年级下", "subject": "math", "focus": "图像与性质"},
    {"topic_id": "math_jun2_data", "name": "数据的分析", "grade": "八年级下", "subject": "math", "focus": "平均数中位数"},
]

def get_voice(grade):
    if "幼儿园" in grade or "幼小衔接" in grade:
        return "zh-CN-XiaoyiNeural"
    elif "九年级" in grade or "初中" in grade:
        return "zh-CN-YunxiNeural"
    return "zh-CN-XiaoxiaoNeural"

async def call_agnes(prompt):
    global last_request_time
    now = time.time()
    elapsed = now - last_request_time
    if elapsed < REQUEST_DELAY:
        await asyncio.sleep(REQUEST_DELAY - elapsed)
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 600}
        try:
            async with session.post("https://apihub.agnes-ai.com/v1/chat/completions", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    return (await resp.json())['choices'][0]['message']['content']
                return None
        except:
            return None

async def gen_image(topic_name, grade, subject):
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
    
    draw.rectangle([50, 50, w-50, 150], fill='#2C3E50')
    draw.text((w//2, 85), f"{grade} · {topic_name}", font=title_font, fill='white', anchor='mm')
    
    colors = {'math': '#FF6B6B', 'chinese': '#4ECDC4', 'english': '#45B7D1', 
              'science': '#96CEB4', 'physics': '#DDA0DD', 'chemistry': '#98D8C8',
              'history': '#BB8FCE', 'geography': '#85C1E9', 'morality': '#FFEAA7'}
    color = colors.get(subject, '#BDC3C7')
    draw.ellipse([350, 300, 674, 624], fill=color)
    draw.text((w//2, 550), subject, font=font, fill='#2C3E50', anchor='mm')
    return img

async def create_topic(topic):
    topic_id = topic['topic_id']
    name = topic['name']
    grade = topic['grade']
    subject = topic['subject']
    focus = topic['focus']
    
    dir_path = Path(f'output/{subject}/{grade}/{topic_id}')
    dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[{topic_id}] {name} ({grade})", end=" ", flush=True)
    
    # 生成explanation
    prompt = f"为{grade}学生详细讲解'{name}'，{focus}。用通俗易懂的语言，200字左右，要有具体例子帮助理解。"
    explanation = await call_agnes(prompt)
    if not explanation:
        print("❌ 生成失败")
        return False
    
    # 生成练习题
    q_prompt = f"为'{name}'设计4道选择题，适合{grade}学生。每道题包含题目、选项A/B/C/D、正确答案和详细解析。格式清晰。"
    quiz = await call_agnes(q_prompt)
    
    # 创建JSON
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
    
    # 生成图片
    img = gen_image(name, grade, subject)
    (dir_path / "image.png").write_bytes(img.tobytes())
    # 简化：用PIL保存
    from PIL import Image as PILImage
    img.save(dir_path / "image.png")
    
    print("✅")
    return True

async def main():
    print(f"📚 P0阶段补全计划: {len(TOPICS_P0)}个知识点\n")
    print(f"⏱️ 预计时间: {len(TOPICS_P0) * REQUEST_DELAY / 60:.1f} 分钟\n")
    
    completed = 0
    for i, topic in enumerate(TOPICS_P0):
        if (i + 1) % 10 == 0:
            print(f"\n进度: [{i+1}/{len(TOPICS_P0)}] 已完成 {completed} 个\n")
        
        if await create_topic(topic):
            completed += 1
        
        await asyncio.sleep(REQUEST_DELAY)
    
    print(f"\n{'='*50}")
    print(f"✅ 完成: {completed}/{len(TOPICS_P0)}")

if __name__ == "__main__":
    asyncio.run(main())