#!/usr/bin/env python3
"""重新生成长方体图片 - 无黑框"""
from PIL import Image, ImageDraw

# 创建图像
img = Image.new('RGB', (900, 450), color='white')
draw = ImageDraw.Draw(img)

# 画三个立体长方体（用实色填充面，避免线条）
def draw_cuboid_fill(draw, cx, cy, w, h, d, colors):
    """绘制实心长方体"""
    # 前面（最大的面）
    draw.rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], fill=colors[0])
    # 顶面
    draw.polygon([(cx-w//2, cy-h//2), (cx-w//2+d//3, cy-h//2-d//2),
                  (cx+w//2+d//3, cy-h//2-d//2), (cx+w//2, cy-h//2)], fill=colors[1])
    # 右侧面
    draw.polygon([(cx+w//2, cy-h//2), (cx+w//2+d//3, cy-h//2-d//2),
                  (cx+w//2+d//3, cy+h//2-d//2), (cx+w//2, cy+h//2)], fill=colors[2])

# 定义颜色（每个面不同颜色避免黑框）
colors_list = [
    ['#FF6B6B', '#EE5A5A', '#DD4444'],  # 红色盒子
    ['#4ECDC4', '#3DBFB6', '#2CB0A7'],  # 青色书本
    ['#FFE66D', '#F5D74E', '#E8C830']   # 黄色砖块
]

positions = [
    (180, 250, 100, 80, 40),  # 盒子
    (450, 230, 80, 100, 35),  # 书本
    (700, 260, 70, 60, 30)    # 砖块
]

for i, (cx, cy, w, h, d) in enumerate(positions):
    draw_cuboid_fill(draw, cx, cy, w, h, d, colors_list[i])

# 添加标签（使用英文避免字体问题）
draw.text((150, 380), "Box", fill='#333333')
draw.text((420, 380), "Book", fill='#333333')
draw.text((670, 390), "Brick", fill='#333333')

# 标题
draw.text((280, 30), "Rectangular Prism (长方体)", fill='#333333')

# 保存
output_path = 'output/math/一年级/math_py1_shape_1/image.png'
img.save(output_path)
print(f"✅ 已保存: {output_path}")
print(f"   尺寸: {img.size}")
