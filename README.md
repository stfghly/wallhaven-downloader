# Wallhaven壁纸下载器

这是一个用于从Wallhaven网站批量下载壁纸的工具，支持GUI界面和命令行两种使用方式。

## 功能特点

- 支持下载latest、hot、toplist和random分类的壁纸
- 支持toplist时间段筛选（1天、3天、1周、1月、3月、6月、1年）
- 支持图片类型筛选（General、Anime、People）
- 支持图片纯度筛选（SFW、Sketchy、NSFW）
- 多线程下载，提高下载速度
- 自动跳过已下载的图片
- 支持GUI界面和命令行两种使用方式

## 使用方法

### GUI界面

1. 运行`Wallhaven下载器.exe`
2. 选择下载分类、页数、线程数等设置
3. 如果选择toplist分类，可以选择时间范围
4. 选择需要的图片类型和纯度
5. 设置保存位置
6. 点击「开始下载」按钮

### 命令行

```
Wallhaven命令行下载器.exe -c [分类] -p [页数] -d [保存目录] -t [线程数] -r [时间范围] --categories [分类代码] --purity [纯度代码]
```

参数说明：
- `-c, --category`: 要下载的分类 (默认: latest)，可选值：latest, hot, toplist, random
- `-p, --pages`: 要下载的页数 (默认: 1)
- `-d, --directory`: 图片保存位置 (默认: ./wallpapers)
- `-t, --threads`: 下载线程数 (默认: 3)
- `-r, --time-range`: Toplist时间范围 (默认: 1M)，可选值：1d, 3d, 1w, 1M, 3M, 6M, 1y
- `--categories`: 图片分类 (General,Anime,People，例如：100表示只看General)
- `--purity`: 图片纯度 (SFW,Sketchy,NSFW，例如：100表示只看SFW)

## 示例

```
# 下载toplist分类的壁纸，时间范围为1周，只下载General类型的SFW图片
Wallhaven命令行下载器.exe -c toplist -p 2 -r 1w --categories 100 --purity 100
```

## 编译方法

如果您想自己编译程序，请按照以下步骤操作：

1. 安装所需依赖：`pip install -r requirements.txt`
2. 运行打包脚本：`python build_exe.py`
3. 编译完成后，可执行文件将位于`dist`目录中

这是一个用于批量下载[wallhaven.cc](https://wallhaven.cc/)网站图片的Python脚本。

## 功能特点

- 支持下载不同分类的图片（latest、hot、toplist、random）
- 可以设置下载页数
- 可以自定义图片保存位置
- 多线程下载，提高下载速度
- 显示下载进度和统计信息

## 安装依赖

在使用此脚本前，请确保已安装以下Python库：

```
pip install requests beautifulsoup4
```

## 使用方法

### 基本用法

```
python wallhaven_downloader.py
```

这将使用默认设置下载最新(latest)分类的第1页图片，并保存到`./wallpapers`目录。

### 高级用法

```
python wallhaven_downloader.py -c hot -p 3 -d D:\wallpapers -t 8
```

参数说明：
- `-c, --category`: 要下载的分类，可选值：latest(最新)、hot(热门)、toplist(排行榜)、random(随机)，默认为latest
- `-p, --pages`: 要下载的页数，默认为1
- `-d, --directory`: 图片保存位置，默认为./wallpapers
- `-t, --threads`: 下载线程数，默认为5

## 示例

1. 下载热门分类的前2页图片：
   ```
   python wallhaven_downloader.py -c hot -p 2
   ```

2. 下载排行榜图片并保存到指定目录：
   ```
   python wallhaven_downloader.py -c toplist -d D:\我的壁纸
   ```

3. 使用10个线程下载随机图片：
   ```
   python wallhaven_downloader.py -c random -t 10
   ```

## 注意事项

- 请合理设置下载页数和线程数，避免对网站造成过大负担
- 下载的图片仅供个人使用，请尊重版权
- 如遇到网络问题，可能会导致部分图片下载失败