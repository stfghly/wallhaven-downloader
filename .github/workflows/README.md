# GitHub Actions 自动构建说明

本项目使用 GitHub Actions 自动构建 Wallhaven 壁纸下载器的 Windows 可执行文件。

## 工作流程说明

在 `build.yml` 文件中配置了自动构建流程，主要功能如下：

1. 触发条件：
   - 当推送代码到 main 或 master 分支时
   - 当创建针对 main 或 master 分支的 Pull Request 时

2. 构建环境：
   - 使用 Windows 最新版本作为构建环境
   - 使用 Python 3.10

3. 构建步骤：
   - 检出代码
   - 安装依赖项（requests, beautifulsoup4, PyInstaller）
   - 运行 build_exe.py 脚本构建可执行文件
   - 将构建好的 GUI 版本和命令行版本作为构建产物上传

## 构建产物

每次成功构建后，可以在 GitHub Actions 的构建详情页面下载以下文件：

- `wallhaven-downloader-gui`：图形界面版本的壁纸下载器
- `wallhaven-downloader-cli`：命令行版本的壁纸下载器

## 如何获取构建产物

1. 在 GitHub 仓库页面，点击 "Actions" 标签
2. 选择最新的成功构建
3. 在构建详情页面底部的 "Artifacts" 部分，可以下载构建好的可执行文件