import os
import subprocess

# 打开小学数学示例文件夹
path = os.path.abspath('output/math/一年级')
subprocess.run(["explorer", path], check=False)
