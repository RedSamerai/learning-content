#!/usr/bin/env python3
"""
测试：使用AGNES生成配图
"""

import asyncio
import aiohttp
import json
import os
import base64

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

async def generate_image(prompt: str, output_path: str):
    """调用AGNES图片生成API"""
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/images/generations",
            headers={
                "Authorization": f"Bearer {AGNES_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "agnes-image-2.1-flash",
                "prompt": prompt,
                "size": "1024x1024",
                "n": 1
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                # 保存base64图片
                image_data = data['data'][0]['b64_json']
                
                output_dir = os.path.dirname(output_path)
                os.makedirs(output_dir, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(image_data))
                
                print(f"✅ 图片已保存: {output_path}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ 生成失败: {error_text}")
                return False

async def main():
    print("🎨 开始生成示例图片...")
    print("=" * 50)
    
    # 为幼儿园数学"认识数字1-3"生成配图
    images = [
        ("1个红苹果", "examples/1-apple.png"),
        ("2只小鸟在树枝上", "examples/2-birds.png"),
        ("3朵花在阳光下", "examples/3-flowers.png"),
        ("数字1、2、3的卡通形象", "examples/numbers-123.png")
    ]
    
    for desc, filename in images:
        print(f"\n生成: {desc}")
        prompt = f"儿童插画风格，色彩鲜艳可爱，{desc}，简洁背景，教育类插图，适合幼儿认知"
        await generate_image(prompt, f"test_output/{filename}")
    
    print("\n" + "=" * 50)
    print("🎉 图片生成完成！")
    print(f"📁 保存位置: D:\\WorkBuddy\\learning-app-research\\learning-content\\test_output\\")

if __name__ == '__main__':
    asyncio.run(main())
