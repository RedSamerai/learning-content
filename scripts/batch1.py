#!/usr/bin/env python3
"""批量生成剩余知识点（分批执行）"""
import asyncio, aiohttp, json, os, edge_tts
from PIL import Image, ImageDraw
AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

# 第一批：小学数学核心内容
BATCH1 = [
    ("math", "一年级上", "math_py_compare", "比大小", "请为小学一年级学生编写比大小的教学内容：讲解大于号、小于号、等于号的用法和记忆方法，举例比较两个数的大小，生成3道练习题。"),
    ("math", "一年级上", "math_py_order", "数的顺序", "请编写数的顺序教学内容，教孩子理解数字排列顺序，如1在2前面，5在3后面等。"),
    ("math", "一年级上", "math_py_add_5", "5以内的加法", "请编写5以内加法的练习题和教学内容。"),
    ("math", "一年级上", "math_py_sub_5", "5以内的减法", "请编写5以内减法的练习题和教学内容。"),
    ("math", "一年级上", "math_py_add_10", "10以内的加法", "请编写10以内加法的练习题和教学内容。"),
    ("math", "一年级上", "math_py_sub_10", "10以内的减法", "请编写10以内减法的练习题和教学内容。"),
    ("math", "一年级上", "math_py_count_20", "数数1-20", "请编写数数1-20的教学内容。"),
    ("math", "一年级上", "math_py_write_20", "写数1-20", "请编写写数1-20的教学内容。"),
    ("math", "一年级上", "math_py_add_20_1", "9加几", "请编写9加几的进位加法教学内容。"),
    ("math", "一年级上", "math_py_add_20_2", "8、7、6加几", "请编写8、7、6加几的进位加法教学内容。"),
    ("math", "一年级上", "math_py_add_20_3", "5、4、3、2加几", "请编写5、4、3、2加几的进位加法教学内容。"),
    ("math", "一年级上", "math_py_shape_2", "认识正方体", "请编写认识正方体的教学内容。"),
    ("math", "一年级上", "math_py_shape_3", "认识圆柱", "请编写认识圆柱的教学内容。"),
    ("math", "一年级上", "math_py_shape_4", "认识球", "请编写认识球的教学内容。"),
    ("math", "一年级下", "math_py_flat_shape", "认识平面图形", "请编写认识平面图形（圆形、三角形、正方形、长方形）的教学内容。"),
    ("math", "一年级上", "math_py_clock_1", "认识整时", "请编写认识整时的教学内容，教孩子看钟面。"),
    ("math", "一年级上", "math_py_clock_2", "认识半时", "请编写认识半时的教学内容。"),
    ("math", "一年级下", "math_py_money_1", "认识元角分", "请编写认识元角分的教学内容。"),
]

async def gen(topic):
    subj, grade, tid, name, prompt = topic
    print(f"\n📚 {name}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{AGNES_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
                json={"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}) as r:
                if r.status == 200:
                    data = await r.json()
                    content = json.loads(data["choices"][0]["message"]["content"])
                else:
                    return False
            
            # 保存
            dir_path = f"output/{subj}/{grade}/{tid}"
            os.makedirs(dir_path, exist_ok=True)
            
            # 图片
            img = Image.new('RGB', (800, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((250, 80), name, fill='#333333')
            img.save(f"{dir_path}/image.png")
            
            # 音频
            concept = content.get('concept', name)
            exp = content.get('explanation', '')
            comm = edge_tts.Communicate(concept, 'zh-CN-XiaoxiaoNeural')
            await comm.save(f"{dir_path}/audio_concept.mp3")
            if exp:
                comm = edge_tts.Communicate(exp, 'zh-CN-XiaoxiaoNeural')
                await comm.save(f"{dir_path}/audio_explanation.mp3")
            
            # JSON
            with open(f"{dir_path}/{tid}.json", 'w', encoding='utf-8') as f:
                json.dump({"topic_id": tid, "name": name, "subject": subj, "grade": grade, "content": content}, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅")
            return True
    except Exception as e:
        print(f"   ❌ {e}")
        return False

async def main():
    print("🚀 开始生成第一批...\n")
    tasks = [gen(t) for t in BATCH1]
    results = await asyncio.gather(*tasks)
    completed = sum(1 for r in results if r)
    print(f"\n✅ 完成: {completed}/{len(BATCH1)}")

if __name__ == '__main__':
    asyncio.run(main())
