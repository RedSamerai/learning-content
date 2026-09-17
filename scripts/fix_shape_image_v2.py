#!/usr/bin/env python3
"""重新生成几何图形图片 - 确保没有多余元素"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_shape_image():
    """生成几何图形 - 只画4个基本形状和标签"""
    img = Image.new('RGB', (900, 450), color='white')
    draw = ImageDraw.Draw(img)
    
    # 定义4个形状的位置和颜色
    shapes = [
        {'type': 'circle', 'color': '#FF6B6B', 'label': '圆形', 'cx': 120, 'cy': 200, 'r': 60},
        {'type': 'square', 'color': '#4ECDC4', 'label': '方形', 'cx': 340, 'cy': 200, 'r': 60},
        {'type': 'triangle', 'color': '#FFE66D', 'label': '三角形', 'cx': 560, 'cy': 200, 'r': 70},
        {'type': 'ellipse', 'color': '#95E1D3', 'label': '椭圆形', 'cx': 780, 'cy': 200, 'r': 80}
    ]
    
    # 绘制每个形状
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
        
        # 在形状下方添加标签（不使用任何方框）
        label_font = ImageFont.truetype("arial.ttf", 32)
        draw.text((s['cx']-30, s['cy']+s['r']+25), s['label'], fill='#333333', font=label_font)
    
    # 添加标题
    title_font = ImageFont.truetype("arial.ttf", 36)
    draw.text((230, 30), "找找生活中的图形", fill='#333333', font=title_font)
    
    return img

def main():
    os.makedirs('output/science/小班(3-4岁)', exist_ok=True)
    
    print("🎨 重新生成几何图形图片...")
    img = create_shape_image()
    img.save('output/science/小班(3-4岁)/math_kg_shape_find/image.png')
    print(f"✅ 保存成功: {img.size}")
    print("\n图片内容:")
    print("- 白色背景")
    print("- 4个彩色几何图形（圆形、方形、三角形、椭圆形）")
    print("- 每个图形下方有中文标签")
    print("- 顶部有标题")
    print("- 没有任何方框或多余元素")

if __name__ == '__main__':
    main()
