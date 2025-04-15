import PyInstaller.__main__
import os
import sys

# 确保当前目录是脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 打包GUI版本
PyInstaller.__main__.run([
    '--name=Wallhaven下载器',
    '--onefile',
    '--windowed',
    '--icon=NONE',  # 如果有图标文件，可以替换为实际的图标路径
    '--add-data=README.md;.',  # 添加额外文件
    '--clean',
    'wallhaven_gui.py'
])

# 打包命令行版本
PyInstaller.__main__.run([
    '--name=Wallhaven命令行下载器',
    '--onefile',
    '--console',
    '--icon=NONE',  # 如果有图标文件，可以替换为实际的图标路径
    '--add-data=README.md;.',  # 添加额外文件
    '--clean',
    'wallhaven_downloader.py'
])

print("\n打包完成！可执行文件位于 dist 目录中。")