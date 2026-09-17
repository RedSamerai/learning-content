import os
import subprocess

# 定义要打开的文件夹路径
folders = [
    "output/science/小班(3-4岁)",
    "output/science/中班(4-5岁)"
]

for folder in folders:
    abs_path = os.path.abspath(folder)
    # Windows上用explorer打开
    subprocess.run(["explorer", abs_path], check=False)
