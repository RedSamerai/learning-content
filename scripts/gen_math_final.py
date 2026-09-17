#!/usr/bin/env python3
"""一次性生成所有数学图片 - 确保排版正确"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_count_10():
    """数数1-10 - 一行10个数字，均匀分布"""
    width, height = 1200, 250
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 字体
    font = ImageFont.truetype("arial.ttf", 80)
    
    # 10个数字，均匀分布
    spacing = width // 10
    for i in range(1, 11):
        x = (i - 1) * spacing + 30
        y = 70
        # 阴影效果
        draw.text((x+2, y+2), str(i), fill='#AAAAAA', font=font)
        # 主数字
        draw.text((x, y), str(i), fill='#333333', font=font)
    
    # 标题
    title_font = ImageFont.truetype("arial.ttf", 36)
    draw.text((450, 10), "Count 1-10", fill='#666666', font=title_font)
    
    return img

def create_count_20():
    """数数1-20 - 两行各10个，均匀分布"""
    width, height = 1300, 350
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 字体
    font = ImageFont.truetype("arial.ttf", 72)
    
    # 第一行: 1-10
    row1_spacing = width // 11
    for i in range(1, 11):
        x = (i - 1) * row1_spacing + 50
        y = 60
        draw.text((x, y), str(i), fill='#333333', font=font)
    
    # 第二行: 11-20
    for i in range(11, 21):
        x = (i - 11) * row1_spacing + 50
        y = 200
        draw.text((x, y), str(i), fill='#333333', font=font)
    
    # 标题
    title_font = ImageFont.truetype("arial.ttf", 36)
    draw.text((500, 10), "Count 1-20", fill='#666666', font=title_font)
    
    return img

def create_shapes():
    """几何图形 - 一行4个，均匀分布"""
    width, height = 900, 400
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 定义4个形状
    shapes = [
        ('circle', '#FF6B6B', 'Circle', 110, 200, 70),
        ('square', '#4ECDC4', 'Square', 330, 200, 70),
        ('triangle', '#FFE66D', 'Triangle', 550, 200, 80),
        ('ellipse', '#95E1D3', 'Ellipse', 770, 200, 90)
    ]
    
    # 绘制每个形状
    for shape_type, color, label, cx, cy, size in shapes:
        if shape_type == 'circle':
            draw.ellipse([cx-size, cy-size, cx+size, cy+size], fill=color)
        elif shape_type == 'square':
            draw.rectangle([cx-size, cy-size, cx+size, cy+size], fill=color)
        elif shape_type == 'triangle':
            points = [(cx, cy-size), (cx-size, cy+size), (cx+size, cy+size)]
            draw.polygon(points, fill=color)
        elif shape_type == 'ellipse':
            draw.ellipse([cx-size, cy-size//2, cx+size, cy+size//2], fill=color)
        
        # 标签
        draw.text((cx-30, cy+size+30), label, fill='#333333')
    
    # 标题
    draw.text((300, 30), "Find Shapes", fill='#666666')
    
    return img

def main():
    # 保存路径
    paths = [
        ('output/science/小班(3-4岁)/math_kg_count_10/image.png', create_count_10()),
        ('output/science/中班(4-5岁)/math_kg_count_20/image.png', create_count_20()),
        ('output/science/小班(3-4岁)/math_kg_shape_find/image.png', create_shapes())
    ]
    
    for path, img in paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
        print(f"✅ {path} - {img.size}")
    
    print("\n✅ 全部完成！")

if __name__ == '__main__':
    main()
