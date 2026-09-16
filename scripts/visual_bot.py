#!/usr/bin/env python3
"""
VisualBot - 视觉设计Bot
使用 AGNES-image-2.1-flash 生成配图
"""

import asyncio
import aiohttp
import os
from pathlib import Path

AGNES_API_KEY = os.getenv("AGNES_API_KEY", "你的AGNES_API_KEY")
AGNES_BASE_URL = "https://api.agnes.ai/v1"

class VisualBot:
    """视觉设计Bot - 生成配图"""
    
    def __init__(self):
        self.api_key = AGNES_API_KEY
        self.base_url = AGNES_BASE_URL
    
    async def generate_image(self, prompt: str, output_path: str, age_group: str = 'kindergarten'):
        """生成单张图片"""
        
        # 年龄适配的图像风格
        style_prompts = {
            'kindergarten': '儿童插画风格，色彩鲜艳，卡通可爱，线条简洁',
            'grade1': '儿童插画风格，色彩明亮，温馨可爱',
            'grade2': '儿童插画风格，清晰明了',
            'grade3-6': '教育插图风格，简洁专业',
            'middle_school': '科学插图风格，准确清晰'
        }
        
        style = style_prompts.get(age_group, style_prompts['kindergarten'])
        full_prompt = f"{prompt}, {style}, high quality, educational"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "agnes-image-2.1-flash",
                    "prompt": full_prompt,
                    "size": "1024x1024",
                    "n": 1
                }
            ) as response:
                data = await response.json()
                
                # 保存图片
                image_url = data['data'][0]['url']
                await self._download_image(image_url, output_path)
                
                return output_path
    
    async def _download_image(self, url: str, path: str):
        """下载图片"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    Path(path).parent.mkdir(parents=True, exist_ok=True)
                    with open(path, 'wb') as f:
                        f.write(content)

async def main():
    """测试：生成"1个苹果"的图片"""
    bot = VisualBot()
    await bot.generate_image(
        "一个红色的苹果",
        "examples/1-apple.png",
        'kindergarten'
    )
    print("✅ 图片已生成！")

if __name__ == '__main__':
    asyncio.run(main())
