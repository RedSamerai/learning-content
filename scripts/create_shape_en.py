#!/usr/bin/env python3
"""生成几何图形图片 - 使用英文标签避免字体问题"""
from PIL import Image, ImageDraw
import os

# 创建图像
width, height = 900, 400
img = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(img)

# 定义形状位置 - 使用英文标签
shapes = [
    ('circle', '#FF6B6B', 'Circle', 120, 200, 60),
    ('square', '#4ECDC4', 'Square', 340, 200, 60),
    ('triangle', '#FFE66D', 'Triangle', 560, 200, 70),
    ('ellipse', '#95E1D3', 'Ellipse', 780, 200, 80)
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
    
    # 添加英文标签（使用默认字体）
    draw.text((cx-30, cy+size+20), label, fill='#333333')

# 添加标题（英文）
draw.text((250, 30), "Find Shapes in Life", fill='#333333')

# 保存
output_path = 'output/science/小班(3-4岁)/math_kg_shape_find/image.png'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
img.save(output_path)

print(f"✅ 已保存: {output_path}")
print(f"   尺寸: {img.size}")
print(f"   文件大小: {os.path.getsize(output_path)} bytes")
