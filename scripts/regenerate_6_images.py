#!/usr/bin/env python3
"""重新生成6张有问题的图片（修复幻觉）"""
import asyncio
import aiohttp
import os

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

# 6张需要重新生成的图片 - 使用精确prompt避免幻觉
topics_to_regenerate = [
    {
        'id': 'math_kg_count_10',
        'name': '数数1-10',
        'age': '小班(3-4岁)',
        'subject': 'science',
        # 明确数字1-10，每个数字配对应数量的物体
        'prompt': '''儿童教育插画，显示数字1到10，每个数字旁边有对应数量的简单物体：
- 数字1旁边1个苹果
- 数字2旁边2个圆形
- 数字3旁边3个星星
- 数字4旁边4个方块
- 数字5旁边5个圆点
- 数字6旁边6个小动物
- 数字7旁边7个花朵
- 数字8旁边8个气球
- 数字9旁边9个水果
- 数字10旁边10个糖果
风格：扁平化设计，简洁白色背景，色彩鲜艳，适合幼儿认知，大字体数字，每行显示5个数字'''
    },
    {
        'id': 'math_kg_count_20',
        'name': '数数1-20',
        'age': '中班(4-5岁)',
        'subject': 'science',
        'prompt': '''儿童教育插画，显示数字1到20，每个数字旁边有对应数量的简单物体：
数字1-20依次排列，每行10个，每个数字用彩色气泡框住，旁边配对应数量的小圆点（简化表示）
风格：扁平化设计，简洁白色背景，数字清晰易读，色彩柔和，适合幼儿学习'''
    },
    {
        'id': 'math_kg_shape_find',
        'name': '找找生活中的图形',
        'age': '小班(3-4岁)',
        'subject': 'science',
        'prompt': '''儿童教育插画，展示生活中的常见图形：
- 圆形：太阳、钟表、盘子
- 方形：窗户、书本、盒子
- 三角形：屋顶、路标、 slice of pizza
- 椭圆形：鸡蛋、橄榄球
每类图形展示一个生活物品，白色背景，简洁卡通风格，颜色鲜明，每个图形标注中文名称'''
    },
    {
        'id': 'sci_kg_animal',
        'name': '动物的家',
        'age': '大班(5-6岁)',
        'subject': 'science',
        'prompt': '''儿童教育插画，展示不同动物的家：
- 小鸟在鸟窝里（树上）
- 兔子在兔洞里（草地）
- 鱼在水里（鱼缸或池塘）
- 蜜蜂在蜂巢里（花丛中）
画面温馨，风格可爱，白色背景，色彩柔和，每个动物配对应的栖息地'''
    },
    {
        'id': 'health_kg_express_emotion',
        'name': '表达自己情绪',
        'age': '中班(4-5岁)',
        'subject': 'health',
        'prompt': '''儿童教育插画，展示四种基本情绪：
- 开心：孩子笑脸，黄色调
- 生气：孩子皱眉，红色调
- 难过：孩子掉眼泪，蓝色调
- 害怕：孩子缩着，紫色调
四个表情分开排列，白色背景，简洁卡通风格，表情夸张但友好，适合幼儿理解'''
    },
    {
        'id': 'art_kg_draw',
        'name': '涂鸦画画',
        'age': '小班(3-4岁)',
        'subject': 'art',
        'prompt': '''儿童教育插画，展示简单的涂鸦画画场景：
- 一个孩子拿着蜡笔在画纸上画画
- 画纸上有简单的线条和色块（红色、蓝色、黄色）
- 旁边放着彩色蜡笔
风格：手绘质感，不规则线条，童趣，温暖色调，白色背景'''
    }
]

async def regenerate_image(topic):
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
    print("🔧 重新生成6张有问题的图片...")
    
    for topic in topics_to_regenerate:
        await regenerate_image(topic)
    
    print("\n✅ 全部完成！")

if __name__ == '__main__':
    asyncio.run(main())
