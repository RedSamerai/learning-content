#!/usr/bin/env python3
"""修复数数1-10图片"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_count_10_image():
    """生成数数1-10 - 确保显示所有10个数字"""
    img = Image.new('RGB', (1200, 150), color='white')
    draw = ImageDraw.Draw(img)
    
    # 使用更大的字体确保清晰
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except:
        font = ImageFont.load_default()
    
    # 水平排列10个数字，每个间隔均匀
    spacing = 110  # 每个数字的间距
    start_x = 50
    y = 20
    
    for i in range(1, 11):  # 1到10
        x = start_x + (i - 1) * spacing
        draw.text((x, y), str(i), fill='#333333', font=font)
    
    return img

def main():
    img = create_count_10_image()
    output_path = 'output/science/小班(3-4岁)/math_kg_count_10/image.png'
    img.save(output_path)
    print(f"✅ 已保存: {output_path}")
    print(f"   尺寸: {img.size}")
    
    # 验证：读取图片并显示宽度
    print(f"\n图片已生成，请检查是否包含1-10的所有数字")

if __name__ == '__main__':
    main()
