#!/usr/bin/env python3
"""
生成美观的数学图片：AI生成背景 + 代码绘制数字
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_count_10_image():
    """生成数数1-10 - AI风格背景 + 正确数字"""
    # 创建白色背景
    img = Image.new('RGB', (1200, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # 添加一些装饰性元素（彩色圆点）
    colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#A8D8EA']
    for i in range(20):
        x = (i % 10) * 120 + 60
        y = 30 if i < 10 else 250
        color = colors[i % len(colors)]
        draw.ellipse([x-10, y-10, x+10, y+10], fill=color)
    
    # 绘制1-10的数字
    font = ImageFont.truetype("arial.ttf", 100)
    spacing = 110
    start_x = 60
    y = 100
    
    for i in range(1, 11):
        x = start_x + (i - 1) * spacing
        # 绘制数字阴影
        draw.text((x+3, y+3), str(i), fill='#CCCCCC', font=font)
        # 绘制数字主体
        draw.text((x, y), str(i), fill='#333333', font=font)
    
    return img

def create_count_20_image():
    """生成数数1-20 - 两行排列"""
    # 创建白色背景
    img = Image.new('RGB', (1400, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 添加装饰性元素
    colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3']
    for i in range(30):
        x = (i % 15) * 95 + 50
        y = 40 if i < 15 else 350
        color = colors[i % len(colors)]
        draw.ellipse([x-8, y-8, x+8, y+8], fill=color)
    
    # 第一行: 1-10
    font1 = ImageFont.truetype("arial.ttf", 80)
    row1_y = 80
    for i in range(1, 11):
        x = (i - 1) * 95 + 60
        draw.text((x, row1_y), str(i), fill='#333333', font=font1)
    
    # 第二行: 11-20
    for i in range(11, 21):
        x = (i - 11) * 95 + 60
        draw.text((x, 250), str(i), fill='#333333', font=font1)
    
    return img

def create_shape_image():
    """生成几何图形 - 带文字标签"""
    # 创建白色背景
    img = Image.new('RGB', (900, 500), color='white')
    draw = ImageDraw.Draw(img)
    
    # 定义4个形状
    shapes = [
        {'type': 'circle', 'color': '#FF6B6B', 'label': '圆形', 'cx': 130, 'cy': 220, 'r': 70},
        {'type': 'square', 'color': '#4ECDC4', 'label': '方形', 'cx': 350, 'cy': 220, 'r': 70},
        {'type': 'triangle', 'color': '#FFE66D', 'label': '三角形', 'cx': 570, 'cy': 220, 'r': 80},
        {'type': 'ellipse', 'color': '#95E1D3', 'label': '椭圆形', 'cx': 790, 'cy': 220, 'r': 90}
    ]
    
    # 绘制形状
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
        label_font = ImageFont.truetype("arial.ttf", 36)
        draw.text((s['cx']-35, s['cy']+s['r']+20), s['label'], fill='#333333', font=label_font)
    
    # 添加标题
    title_font = ImageFont.truetype("arial.ttf", 40)
    draw.text((250, 30), "找找生活中的图形", fill='#333333', font=title_font)
    
    return img

def main():
    # 保存目录
    os.makedirs('output/science/小班(3-4岁)', exist_ok=True)
    os.makedirs('output/science/中班(4-5岁)', exist_ok=True)
    
    print("🎨 生成数数1-10...")
    img1 = create_count_10_image()
    img1.save('output/science/小班(3-4岁)/math_kg_count_10/image.png')
    print(f"✅ 保存成功")
    
    print("🎨 生成数数1-20...")
    img2 = create_count_20_image()
    img2.save('output/science/中班(4-5岁)/math_kg_count_20/image.png')
    print(f"✅ 保存成功")
    
    print("🎨 生成几何图形...")
    img3 = create_shape_image()
    img3.save('output/science/小班(3-4岁)/math_kg_shape_find/image.png')
    print(f"✅ 保存成功")
    
    print("\n✅ 全部完成！")
    print("\n请查看图片效果：")
    print("- 数数1-10: 10个数字，有装饰圆点")
    print("- 数数1-20: 20个数字，两行排列，有装饰圆点")
    print("- 几何图形: 4个基本形状，带中文标签")

if __name__ == '__main__':
    main()
