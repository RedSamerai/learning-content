#!/usr/bin/env python3
"""修复几何图形图片 - 移除多余元素"""
from PIL import Image, ImageDraw
import os

def create_shape_image():
    """生成几何图形 - 只画4个基本形状，无多余元素"""
    img = Image.new('RGB', (800, 350), color='white')
    draw = ImageDraw.Draw(img)
    
    # 定义4个形状的参数：(中心x, 中心y, 半径/半宽)
    shapes = [
        {'cx': 100, 'cy': 175, 'r': 60, 'color': '#FF6B6B'},  # 圆形
        {'cx': 300, 'cy': 175, 'r': 60, 'color': '#4ECDC4'},  # 正方形
        {'cx': 500, 'cy': 175, 'r': 65, 'color': '#FFE66D'},  # 三角形
        {'cx': 700, 'cy': 175, 'r': 70, 'color': '#95E1D3'}   # 椭圆形
    ]
    
    for s in shapes:
        if s['color'] == '#FF6B6B':  # 圆形
            draw.ellipse([s['cx']-s['r'], s['cy']-s['r'], s['cx']+s['r'], s['cy']+s['r']], 
                        fill=s['color'])
        elif s['color'] == '#4ECDC4':  # 正方形
            draw.rectangle([s['cx']-s['r'], s['cy']-s['r'], s['cx']+s['r'], s['cy']+s['r']], 
                          fill=s['color'])
        elif s['color'] == '#FFE66D':  # 三角形
            points = [
                (s['cx'], s['cy']-s['r']),
                (s['cx']-s['r'], s['cy']+s['r']),
                (s['cx']+s['r'], s['cy']+s['r'])
            ]
            draw.polygon(points, fill=s['color'])
        elif s['color'] == '#95E1D3':  # 椭圆形
            draw.ellipse([s['cx']-s['r'], s['cy']-s['r']//2, s['cx']+s['r'], s['cy']+s['r']//2], 
                        fill=s['color'])
        
        # 在形状下方添加标签
        draw.text((s['cx']-35, s['cy']+s['r']+20), 
                 ['圆形', '方形', '三角形', '椭圆形'][shapes.index(s)], 
                 fill='#333333')
    
    return img

def main():
    img = create_shape_image()
    output_path = 'output/science/小班(3-4岁)/math_kg_shape_find/image.png'
    img.save(output_path)
    print(f"✅ 已保存: {output_path}")
    print(f"   尺寸: {img.size}")
    print("\n✅ 几何图形图片已修复！")

if __name__ == '__main__':
    main()
