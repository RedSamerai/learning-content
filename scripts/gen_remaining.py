#!/usr/bin/env python3
import asyncio, aiohttp, json, os, edge_tts
AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

# 待生成的知识点
TOPICS = [
    ("chinese", "幼小衔接", "py_pin du", "拼音拼读练习", "请为幼小衔接学生编写拼音拼读练习教学内容：要求用简单语言讲解拼读规则，举例说明，生成3道练习题。输出JSON：{\"concept\":\"...\",\"explanation\":\"...\",\"questions\":[{\"question\":\"...\",\"options\":[\"A...\",\"B...\",\"C...\",\"D...\"],\"answer\":\"A\",\"explanation\":\"...\"}]}"),
    ("chinese", "幼小衔接", "py_char_100", "认识100个常用字", "请为幼小衔接学生编写认识100个常用字的教学内容：介绍如何识记汉字，举例常用字，生成练习题。"),
    ("chinese", "幼小衔接", "py_char_name", "认识自己的名字", "请编写认识自己名字的教学内容，教孩子读写自己的名字，理解名字的含义。"),
    ("chinese", "幼小衔接", "py_write_heaven", "写天和地", "请编写写'天'和'地'的教学内容，教孩子认识笔画顺序，练习书写。"),
    ("chinese", "幼小衔接", "py_write_human", "写人和大", "请编写写'人'和'大'的教学内容，教孩子认识笔画顺序，练习书写。"),
    ("chinese", "一年级上", "py_look_talk_1", "看图说一句话", "请编写看图说一句话的教学内容，教孩子观察图片并用一句话表达。"),
    ("chinese", "一年级上", "py_read_lesson1", "朗读课文秋天", "请编写朗读课文《秋天》的教学内容，介绍课文内容和朗读技巧。"),
    ("math", "一年级上", "math_py_count_10", "数数1-10", "请为小学一年级学生编写数数1-10的教学内容：用简单语言讲解如何从1数到10，举例生活场景，生成3道练习题。"),
    ("math", "一年级上", "math_py_compare", "比大小", "请为小学一年级学生编写比大小的教学内容：讲解大于号小于号的用法，举例比较两个数的大小。"),
    ("math", "一年级上", "math_py_order", "数的顺序", "请编写数的顺序教学内容，教孩子理解数字的排列顺序。"),
    ("math", "一年级上", "math_py_add_5", "5以内的加法", "请编写5以内加法的练习题。"),
    ("math", "一年级上", "math_py_sub_5", "5以内的减法", "请编写5以内减法的练习题。"),
    ("math", "一年级上", "math_py_add_10", "10以内的加法", "请编写10以内加法的练习题。"),
    ("math", "一年级上", "math_py_sub_10", "10以内的减法", "请编写10以内减法的练习题。"),
    ("math", "一年级上", "math_py_count_20", "数数1-20", "请编写数数1-20的教学内容。"),
    ("math", "一年级上", "math_py_write_20", "写数1-20", "请编写写数1-20的教学内容。"),
    ("math", "一年级上", "math_py_add_20_1", "9加几", "请编写9加几的进位加法教学内容。"),
    ("math", "一年级上", "math_py_add_20_2", "8、7、6加几", "请编写8、7、6加几的进位加法教学内容。"),
    ("math", "一年级上", "math_py_add_20_3", "5、4、3、2加几", "请编写5、4、3、2加几的进位加法教学内容。"),
    ("math", "一年级上", "math_py_shape_1", "认识长方体", "请编写认识长方体的教学内容，介绍长方体的特征。"),
    ("math", "一年级上", "math_py_shape_2", "认识正方体", "请编写认识正方体的教学内容。"),
    ("math", "一年级上", "math_py_shape_3", "认识圆柱", "请编写认识圆柱的教学内容。"),
    ("math", "一年级上", "math_py_shape_4", "认识球", "请编写认识球的教学内容。"),
    ("math", "一年级下", "math_py_flat_shape", "认识平面图形", "请编写认识平面图形（圆形、三角形、正方形、长方形）的教学内容。"),
    ("math", "一年级上", "math_py_clock_1", "认识整时", "请编写认识整时的教学内容，教孩子看钟面。"),
    ("math", "一年级上", "math_py_clock_2", "认识半时", "请编写认识半时的教学内容。"),
    ("math", "一年级下", "math_py_money_1", "认识元角分", "请编写认识元角分的教学内容。"),
    ("science", "一年级上", "sci_py_plant_1", "观察校园里的植物", "请编写观察校园植物的教学内容。"),
    ("science", "一年级上", "sci_py_animal_1", "认识常见的动物", "请编写认识常见动物的教学内容。"),
    ("science", "二年级上", "sci_py_plant_need", "植物生长需要什么", "请编写植物生长需要的教学内容。"),
    ("science", "一年级上", "sci_py_water_1", "水的特征", "请编写水的特征的教学内容。"),
    ("science", "一年级上", "sci_py_air_1", "空气的特点", "请编写空气特点的教学内容。"),
    ("science", "二年级上", "sci_py_hard_soft", "软硬比较", "请编写软硬比较的教学内容。"),
    ("science", "二年级上", "sci_py_float_sink", "浮与沉", "请编写浮与沉的教学内容。"),
    ("science", "一年级上", "sci_py_weather_1", "认识天气", "请编写认识天气的教学内容。"),
    ("science", "一年级下", "sci_py_season_1", "四季的变化", "请编写四季变化的教学内容。"),
    ("morality", "一年级上", "mor_py_good habit_1", "早睡早起", "请编写早睡早起习惯的培养教学内容。"),
    ("morality", "一年级上", "mor_py_clean_1", "讲卫生勤洗手", "请编写讲卫生勤洗手的教学内容。"),
]

async def gen(topic):
    subj, grade, tid, name, prompt = topic
    print(f"\n📚 {name} ({grade})")
    try:
        async with aiohttp.ClientSession() as session:
            # 生成文本
            async with session.post(f"{AGNES_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
                json={"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}) as r:
                if r.status == 200:
                    data = await r.json()
                    content = json.loads(data["choices"][0]["message"]["content"])
                else:
                    print(f"   ❌ API错误 {r.status}")
                    return False
            
            # 生成图片（简单文字图）
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (1000, 250), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((300, 100), name, fill='#333333')
            
            # 保存
            dir_path = f"output/{subj}/{grade}/{tid}"
            os.makedirs(dir_path, exist_ok=True)
            img.save(f"{dir_path}/image.png")
            
            # 生成音频
            concept = content.get('concept', name)
            exp = content.get('explanation', '')
            
            comm = edge_tts.Communicate(concept, 'zh-CN-XiaoxiaoNeural')
            await comm.save(f"{dir_path}/audio_concept.mp3")
            if exp:
                comm = edge_tts.Communicate(exp, 'zh-CN-XiaoxiaoNeural')
                await comm.save(f"{dir_path}/audio_explanation.mp3")
            
            # 保存JSON
            with open(f"{dir_path}/{tid}.json", 'w', encoding='utf-8') as f:
                json.dump({"topic_id": tid, "name": name, "subject": subj, "grade": grade, "content": content}, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ 完成")
            return True
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False

async def main():
    print("🚀 开始生成剩余知识点...\n")
    completed = 0
    for topic in TOPICS:
        if await gen(topic):
            completed += 1
    print(f"\n{'='*50}")
    print(f"✅ 完成: {completed}/{len(TOPICS)}")

if __name__ == '__main__':
    asyncio.run(main())
