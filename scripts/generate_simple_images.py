#!/usr/bin/env python3
"""
直接生成简单的数字卡片和几何图形图片（避免AI幻觉）
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_count_10_image():
    """生成数数1-10的图片 - 纯数字卡片"""
    img = Image.new('RGB', (1024, 512), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体，如果没有则使用默认
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # 绘制10个数字，每个一行
    for i in range(1, 11):
        y = (i - 1) * 45 + 30
        # 绘制圆角矩形背景
        draw.rounded_rectangle([50, y, 250, y + 40], radius=10, fill='#FFE4B5', outline='#FF8C00', width=2)
        # 绘制数字
        draw.text((120, y + 5), str(i), fill='#333333', font=font)
    
    # 标题
    title_font = ImageFont.truetype("arial.ttf", 36)
    draw.text((350, 20), "数数 1-10", fill='#333333', font=title_font)
    
    return img

def create_count_20_image():
    """生成数数1-20的图片 - 两行数字"""
    img = Image.new('RGB', (1024, 512), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    # 第一行: 1-10
    for i in range(1, 11):
        x = (i - 1) * 95 + 30
        y = 50
        draw.rounded_rectangle([x, y, x + 80, y + 70], radius=8, fill='#E0FFE0', outline='#32CD32', width=2)
        draw.text((x + 25, y + 15), str(i), fill='#333333', font=font)
    
    # 第二行: 11-20
    for i in range(11, 21):
        x = (i - 11) * 95 + 30
        y = 150
        draw.rounded_rectangle([x, y, x + 80, y + 70], radius=8, fill='#E0E0FF', outline='#4169E1', width=2)
        draw.text((x + 15, y + 15), str(i), fill='#333333', font=font)
    
    return img

def create_shape_image():
    """生成几何图形图片 - 基本形状"""
    img = Image.new('RGB', (1024, 512), color='white')
    draw = ImageDraw.Draw(img)
    
    # 定义形状信息：(类型, 颜色, 标签)
    shapes = [
        ('circle', '#FF6B6B', '圆形'),
        ('square', '#4ECDC4', '方形'),
        ('triangle', '#FFE66D', '三角形'),
        ('ellipse', '#95E1D3', '椭圆形')
    ]
    
    # 每个形状的绘制函数
    shape_funcs = {
        'circle': lambda d, x, y, size: d.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill='#FF6B6B'),
        'square': lambda d, x, y, size: d.rectangle([x-size//2, y-size//2, x+size//2, y+size//2], fill='#4ECDC4'),
        'triangle': lambda d, x, y, size: d.polygon([(x, y-size//2), (x-size//2, y+size//2), (x+size//2, y+size//2)], fill='#FFE66D'),
        'ellipse': lambda d, x, y, size: d.ellipse([x-size, y-size//3, x+size, y+size//3], fill='#95E1D3')
    }
    
    # 绘制4个形状
    spacing = 220
    start_x = 150
    for i, (shape_type, color, label) in enumerate(shapes):
        x = start_x + i * spacing
        y = 200
        
        # 绘制形状
        shape_funcs[shape_type](draw, x, y, 120)
        
        # 绘制标签
        draw.text((x - 30, y + 80), label, fill='#333333')
    
    return img

def save_images():
    """保存所有图片"""
    # 确保目录存在
    os.makedirs('output/science/小班(3-4岁)', exist_ok=True)
    os.makedirs('output/science/中班(4-5岁)', exist_ok=True)
    
    # 生成并保存图片
    print("🎨 生成数数1-10...")
    img1 = create_count_10_image()
    img1.save('output/science/小班(3-4岁)/math_kg_count_10/image.png')
    print(f"✅ 保存: output/science/小班(3-4岁)/math_kg_count_10/image.png")
    
    print("🎨 生成数数1-20...")
    img2 = create_count_20_image()
    img2.save('output/science/中班(4-5岁)/math_kg_count_20/image.png')
    print(f"✅ 保存: output/science/中班(4-5岁)/math_kg_count_20/image.png")
    
    print("🎨 生成几何图形...")
    img3 = create_shape_image()
    img3.save('output/science/小班(3-4岁)/math_kg_shape_find/image.png')
    print(f"✅ 保存: output/science/小班(3-4岁)/math_kg_shape_find/image.png")
    
    print("\n✅ 全部完成！")

if __name__ == '__main__':
    save_images()
