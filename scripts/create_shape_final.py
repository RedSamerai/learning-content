#!/usr/bin/env python3
"""重新生成几何图形 - 确保没有任何多余元素"""
from PIL import Image, ImageDraw, ImageFont
import os

def main():
    # 创建图像 - 更大的画布
    width, height = 1000, 500
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 字体
    title_font = ImageFont.truetype("arial.ttf", 40)
    label_font = ImageFont.truetype("arial.ttf", 36)
    
    # 定义4个形状的参数 - 每个都有明确的中心坐标和大小
    shapes = [
        {'name': 'circle', 'color': '#FF6B6B', 'label': '圆形', 'cx': 150, 'cy': 220, 'size': 70},
        {'name': 'square', 'color': '#4ECDC4', 'label': '方形', 'cx': 400, 'cy': 220, 'size': 70},
        {'name': 'triangle', 'color': '#FFE66D', 'label': '三角形', 'cx': 650, 'cy': 220, 'size': 80},
        {'name': 'ellipse', 'color': '#95E1D3', 'label': '椭圆形', 'cx': 850, 'cy': 220, 'size': 80}
    ]
    
    # 绘制每个形状
    for shape in shapes:
        sx = shape['cx']
        sy = shape['cy']
        s = shape['size']
        
        if shape['name'] == 'circle':
            # 圆形：使用ellipse，确保是正圆
            draw.ellipse([sx-s, sy-s, sx+s, sy+s], fill=shape['color'])
        
        elif shape['name'] == 'square':
            # 正方形：使用rectangle
            draw.rectangle([sx-s, sy-s, sx+s, sy+s], fill=shape['color'])
        
        elif shape['name'] == 'triangle':
            # 三角形：三个顶点
            points = [
                (sx, sy-s),           # 顶部
                (sx-s, sy+s),         # 左下
                (sx+s, sy+s)          # 右下
            ]
            draw.polygon(points, fill=shape['color'])
        
        elif shape['name'] == 'ellipse':
            # 椭圆形：横向椭圆
            draw.ellipse([sx-s, sy-s//2, sx+s, sy+s//2], fill=shape['color'])
        
        # 在形状正下方添加标签（不使用任何方框）
        label_x = sx - 35
        label_y = sy + s + 30
        draw.text((label_x, label_y), shape['label'], fill='#333333', font=label_font)
    
    # 添加标题
    title_text = "找找生活中的图形"
    title_width = len(title_text) * 20
    draw.text(((width-title_width)//2, 30), title_text, fill='#333333', font=title_font)
    
    # 保存
    output_path = 'output/science/小班(3-4岁)/math_kg_shape_find/image.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    
    print(f"✅ 已保存: {output_path}")
    print(f"   尺寸: {img.size}")
    print(f"   文件大小: {os.path.getsize(output_path)} bytes")
    print("\n图片内容:")
    print("- 白色背景")
    print("- 4个彩色几何图形：圆形、方形、三角形、椭圆形")
    print("- 每个图形下方有中文标签")
    print("- 顶部有标题")
    print("- 没有任何方框或多余元素")

if __name__ == '__main__':
    main()
