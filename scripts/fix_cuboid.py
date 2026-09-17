#!/usr/bin/env python3
"""生成正确的长方体图片"""
from PIL import Image, ImageDraw
import os

def draw_cuboid(draw, x, y, size, color):
    """画一个长方体（线框图）"""
    # 前面的面
    draw.rectangle([x, y, x+size, y+size], outline=color, width=2)
    # 后面的面（偏移）
    offset = size // 3
    draw.rectangle([x+offset, y-offset, x+size+offset, y+size-offset], outline=color, width=2)
    # 连接边
    draw.line([(x, y), (x+offset, y-offset)], fill=color, width=2)
    draw.line([(x+size, y), (x+size+offset, y-offset)], fill=color, width=2)
    draw.line([(x, y+size), (x+offset, y+size-offset)], fill=color, width=2)
    draw.line([(x+size, y+size), (x+size+offset, y+size-offset)], fill=color, width=2)

img = Image.new('RGB', (800, 400), color='white')
draw = ImageDraw.Draw(img)

# 画三个长方体
draw_cuboid(draw, 150, 120, 120, '#FF6B6B')  # 红色盒子
draw_cuboid(draw, 380, 100, 100, '#4ECDC4')  # 青色书本
draw_cuboid(draw, 580, 130, 90, '#FFE66D')   # 黄色砖块

# 添加标签
draw.text((170, 280), "盒子", fill='#333333')
draw.text((400, 250), "书本", fill='#333333')
draw.text((600, 270), "砖块", fill='#333333')

# 标题
draw.text((250, 30), "长方体像这些物品", fill='#333333')

output_path = 'output/math/一年级/math_py1_shape_1/image.png'
img.save(output_path)
print(f"✅ 已保存: {output_path}")
