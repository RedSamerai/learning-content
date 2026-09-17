#!/usr/bin/env python3
"""重新生成3张严重幻觉的图片（简化prompt）"""
import asyncio
import aiohttp
import os

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

# 3张严重幻觉的图片 - 使用最简单明确的prompt
topics_to_fix = [
    {
        'id': 'math_kg_count_10',
        'name': '数数1-10',
        'age': '小班(3-4岁)',
        'subject': 'science',
        # 简化：只画数字1-10，不要求数量对应，避免幻觉
        'prompt': '''简单的儿童教育数字卡片，纯白色背景，只显示阿拉伯数字1到10，
每个数字单独占据一个圆角矩形框，数字用粗体红色或蓝色，
大字体，居中对齐，无任何其他元素、无动物、无水果、无装饰物，
风格：极简、清晰、教学卡片风格'''
    },
    {
        'id': 'math_kg_count_20',
        'name': '数数1-20',
        'age': '中班(4-5岁)',
        'subject': 'science',
        # 简化：只画数字1-20，两行排列
        'prompt': '''简单的儿童教育数字卡片，纯白色背景，只显示阿拉伯数字1到20，
两行排列，每行10个数字，每个数字单独占据一个圆角矩形框，
数字用粗体蓝色，大字体，居中对齐，无任何其他元素，
风格：极简、清晰、教学卡片风格'''
    },
    {
        'id': 'math_kg_shape_find',
        'name': '找找生活中的图形',
        'age': '小班(3-4岁)',
        'subject': 'science',
        # 简化：只画基本几何图形，不用生活物品避免复杂场景
        'prompt': '''儿童教育几何图形卡片，纯白色背景，只显示四个基本形状：
- 红色圆形（实心）
- 蓝色正方形（实心）
- 黄色三角形（实心）
- 绿色椭圆形（实心）
四个形状分开排列，中等大小，居中对齐，无任何其他元素、无文字说明，
风格：扁平化、简洁、教学卡片'''
    }
]

async def fix_image(topic):
    print(f"\n🎨 重新生成: {topic['name']}")
    
    async with aiohttp.ClientSession() as session:
        # 调用图片生成API
        async with session.post(
            f"{AGNES_BASE_URL}/images/generations",
            headers={
                "Authorization": f"Bearer {AGNES_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "agnes-image-2.1-flash",
                "prompt": topic['prompt'],
                "size": "512x512",
                "n": 1
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['data'][0].get('url', '')
                
                if image_url:
                    # 下载图片
                    async with session.get(image_url) as img_response:
                        if img_response.status == 200:
                            img_data = await img_response.read()
                            
                            # 保存文件
                            img_path = f"output/{topic['subject']}/{topic['age']}/{topic['id']}/image.png"
                            os.makedirs(os.path.dirname(img_path), exist_ok=True)
                            
                            with open(img_path, 'wb') as f:
                                f.write(img_data)
                            
                            print(f"✅ {topic['name']}: {len(img_data)} bytes")
                            return True
                        else:
                            print(f"❌ 下载失败: {img_response.status}")
                            return False
            else:
                print(f"❌ API错误: {response.status}")
                return False

async def main():
    print("🔧 重新生成3张严重幻觉的图片...")
    
    for topic in topics_to_fix:
        await fix_image(topic)
    
    print("\n✅ 全部完成！")

if __name__ == '__main__':
    asyncio.run(main())
