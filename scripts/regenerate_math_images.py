#!/usr/bin/env python3
"""重新生成3张数学图片，确保数字正确"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_count_10_image():
    """生成数数1-10 - 确保每个数字正确显示"""
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 字体大小要足够大，确保数字清晰
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    # 绘制10个数字，居中排列
    spacing = 75
    start_x = 40
    for i in range(1, 11):
        x = start_x + (i - 1) * spacing * 8
        
        # 先画数字
        draw.text((x, 150), str(i), fill='#333333', font=font)
    
    # 标题
    title_font = ImageFont.truetype("arial.ttf", 40)
    draw.text((280, 30), "数数 1-10", fill='#FF6B6B', font=title_font)
    
    return img

def create_count_20_image():
    """生成数数1-20 - 两行排列，确保所有数字正确"""
    img = Image.new('RGB', (1200, 500), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except:
        font = ImageFont.load_default()
    
    # 第一行: 1-10
    row1_y = 80
    for i in range(1, 11):
        x = (i - 1) * 105 + 50
        # 画数字，不要背景框
        draw.text((x, row1_y), str(i), fill='#333333', font=font)
    
    # 第二行: 11-20
    row2_y = 260
    for i in range(11, 21):
        x = (i - 11) * 105 + 50
        draw.text((x, row2_y), str(i), fill='#333333', font=font)
    
    # 标题
    title_font = ImageFont.truetype("arial.ttf", 40)
    draw.text((450, 20), "数数 1-20", fill='#4ECDC4', font=title_font)
    
    return img

def create_shape_image():
    """生成几何图形 - 圆形、方形、三角形、椭圆形"""
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 定义4个形状的参数
    shapes = [
        {'type': 'circle', 'color': '#FF6B6B', 'label': '圆形', 'x': 150, 'y': 200, 'size': 80},
        {'type': 'square', 'color': '#4ECDC4', 'label': '方形', 'x': 350, 'y': 200, 'size': 80},
        {'type': 'triangle', 'color': '#FFE66D', 'label': '三角形', 'x': 550, 'y': 200, 'size': 90},
        {'type': 'ellipse', 'color': '#95E1D3', 'label': '椭圆形', 'x': 700, 'y': 200, 'size': 70}
    ]
    
    for shape in shapes:
        if shape['type'] == 'circle':
            # 圆形：ellipse需要4个坐标 (x1, y1, x2, y2)
            draw.ellipse([shape['x']-shape['size'], shape['y']-shape['size'], 
                         shape['x']+shape['size'], shape['y']+shape['size']], 
                        fill=shape['color'])
        elif shape['type'] == 'square':
            # 方形：rectangle
            draw.rectangle([shape['x']-shape['size'], shape['y']-shape['size'], 
                           shape['x']+shape['size'], shape['y']+shape['size']], 
                          fill=shape['color'])
        elif shape['type'] == 'triangle':
            # 三角形：polygon需要3个点
            points = [
                (shape['x'], shape['y'] - shape['size']),  # 顶部
                (shape['x'] - shape['size'], shape['y'] + shape['size']),  # 左下
                (shape['x'] + shape['size'], shape['y'] + shape['size'])   # 右下
            ]
            draw.polygon(points, fill=shape['color'])
        elif shape['type'] == 'ellipse':
            # 椭圆形：ellipse，宽高不同
            draw.ellipse([shape['x']-shape['size'], shape['y']-shape['size']//2, 
                         shape['x']+shape['size'], shape['y']+shape['size']//2], 
                        fill=shape['color'])
        
        # 绘制标签
        draw.text((shape['x'] - 30, shape['y'] + shape['size'] + 20), 
                 shape['label'], fill='#333333')
    
    # 标题
    title_font = ImageFont.truetype("arial.ttf", 40)
    draw.text((200, 30), "找找生活中的图形", fill='#333333', font=title_font)
    
    return img

def save_images():
    """保存所有图片"""
    # 确保目录存在
    os.makedirs('output/science/小班(3-4岁)', exist_ok=True)
    os.makedirs('output/science/中班(4-5岁)', exist_ok=True)
    
    print("🎨 重新生成数数1-10...")
    img1 = create_count_10_image()
    img1.save('output/science/小班(3-4岁)/math_kg_count_10/image.png')
    print(f"✅ 保存: output/science/小班(3-4岁)/math_kg_count_10/image.png")
    
    print("🎨 重新生成数数1-20...")
    img2 = create_count_20_image()
    img2.save('output/science/中班(4-5岁)/math_kg_count_20/image.png')
    print(f"✅ 保存: output/science/中班(4-5岁)/math_kg_count_20/image.png")
    
    print("🎨 重新生成几何图形...")
    img3 = create_shape_image()
    img3.save('output/science/小班(3-4岁)/math_kg_shape_find/image.png')
    print(f"✅ 保存: output/science/小班(3-4岁)/math_kg_shape_find/image.png")
    
    print("\n✅ 全部完成！请查看图片是否正确。")

if __name__ == '__main__':
    save_images()
