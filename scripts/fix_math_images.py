#!/usr/bin/env python3
"""重新生成3张有问题的图片 - 确保内容正确"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_count_10_image():
    """生成数数1-10 - 水平排列，清晰显示1-10"""
    img = Image.new('RGB', (1000, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except:
        font = ImageFont.load_default()
    
    # 水平排列10个数字
    spacing = 95
    start_x = 40
    y = 55
    
    for i in range(1, 11):
        x = start_x + (i - 1) * spacing
        draw.text((x, y), str(i), fill='#333333', font=font)
    
    return img

def create_count_20_image():
    """生成数数1-20 - 两行排列，清晰显示1-20"""
    img = Image.new('RGB', (1100, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 64)
    except:
        font = ImageFont.load_default()
    
    # 第一行: 1-10
    row1_y = 60
    for i in range(1, 11):
        x = (i - 1) * 100 + 50
        draw.text((x, row1_y), str(i), fill='#333333', font=font)
    
    # 第二行: 11-20
    row2_y = 180
    for i in range(11, 21):
        x = (i - 11) * 100 + 50
        draw.text((x, row2_y), str(i), fill='#333333', font=font)
    
    return img

def create_shape_image():
    """生成几何图形 - 只画4个基本形状"""
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 定义4个形状
    shapes = [
        {'type': 'circle', 'color': '#FF6B6B', 'label': '圆形', 'cx': 100, 'cy': 200, 'r': 60},
        {'type': 'square', 'color': '#4ECDC4', 'label': '方形', 'cx': 300, 'cy': 200, 'r': 60},
        {'type': 'triangle', 'color': '#FFE66D', 'label': '三角形', 'cx': 500, 'cy': 200, 'r': 65},
        {'type': 'ellipse', 'color': '#95E1D3', 'label': '椭圆', 'cx': 700, 'cy': 200, 'r': 70}
    ]
    
    for s in shapes:
        if s['type'] == 'circle':
            draw.ellipse([s['cx']-s['r'], s['cy']-s['r'], s['cx']+s['r'], s['cy']+s['r']], 
                        fill=s['color'])
        elif s['type'] == 'square':
            draw.rectangle([s['cx']-s['r'], s['cy']-s['r'], s['cx']+s['r'], s['cy']+s['r']], 
                          fill=s['color'])
        elif s['type'] == 'triangle':
            points = [
                (s['cx'], s['cy']-s['r']),
                (s['cx']-s['r'], s['cy']+s['r']),
                (s['cx']+s['r'], s['cy']+s['r'])
            ]
            draw.polygon(points, fill=s['color'])
        elif s['type'] == 'ellipse':
            draw.ellipse([s['cx']-s['r'], s['cy']-s['r']//2, s['cx']+s['r'], s['cy']+s['r']//2], 
                        fill=s['color'])
        
        # 添加标签
        draw.text((s['cx']-25, s['cy']+s['r']+15), s['label'], fill='#333333')
    
    return img

def main():
    # 保存目录
    os.makedirs('output/science/小班(3-4岁)', exist_ok=True)
    os.makedirs('output/science/中班(4-5岁)', exist_ok=True)
    
    # 生成图片
    print("🎨 生成数数1-10...")
    img1 = create_count_10_image()
    img1.save('output/science/小班(3-4岁)/math_kg_count_10/image.png')
    print(f"✅ 保存: {img1.size}")
    
    print("🎨 生成数数1-20...")
    img2 = create_count_20_image()
    img2.save('output/science/中班(4-5岁)/math_kg_count_20/image.png')
    print(f"✅ 保存: {img2.size}")
    
    print("🎨 生成几何图形...")
    img3 = create_shape_image()
    img3.save('output/science/小班(3-4岁)/math_kg_shape_find/image.png')
    print(f"✅ 保存: {img3.size}")
    
    print("\n✅ 全部完成！")

if __name__ == '__main__':
    main()
