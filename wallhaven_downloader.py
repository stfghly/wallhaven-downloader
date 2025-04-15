import os
import requests
import argparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import random

class WallhavenDownloader:
    def __init__(self, save_dir, category='latest', pages=1, threads=3, time_range='1M', purity='100', categories='111'):
        self.base_url = 'https://wallhaven.cc'
        self.save_dir = save_dir
        self.category = category
        self.pages = pages
        self.threads = threads
        self.time_range = time_range  # 时间范围：1d, 3d, 1w, 1M, 3M, 6M, 1y
        self.purity = purity  # 纯度：100=SFW, 010=Sketchy, 001=NSFW
        self.categories = categories  # 分类：100=General, 010=Anime, 001=People
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 确保保存目录存在
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def get_image_urls(self, page):
        """获取指定页面的所有图片URL"""
        # 构建URL，添加筛选参数
        url = f"{self.base_url}/{self.category}?page={page}"
        
        # 如果是toplist分类，添加时间范围参数
        if self.category == 'toplist':
            url += f"&sorting=toplist&topRange={self.time_range}"
        
        # 添加分类和纯度筛选
        url += f"&categories={self.categories}&purity={self.purity}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有图片预览元素
            preview_elements = soup.select('figure.thumb a.preview')
            image_urls = [elem.get('href') for elem in preview_elements if elem.get('href')]
            
            return image_urls
        except requests.exceptions.RequestException as e:
            print(f"获取第{page}页图片列表失败: {e}")
            return []
    
    def download_image(self, image_url, max_retries=3):
        """下载单张图片，支持重试"""
        retries = 0
        while retries < max_retries:
            try:
                # 随机延迟，避免请求过于频繁
                time.sleep(random.uniform(1.0, 3.0))
                
                # 获取图片详情页
                response = requests.get(image_url, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 找到原始图片链接
                img_element = soup.select_one('#wallpaper')
                if not img_element or not img_element.get('src'):
                    print(f"无法在{image_url}找到图片链接")
                    return False
                
                img_url = img_element.get('src')
                img_id = os.path.basename(image_url)
                
                # 确定文件扩展名
                file_ext = os.path.splitext(img_url)[1]
                if not file_ext:
                    file_ext = '.jpg'  # 默认扩展名
                
                # 检查文件是否已存在
                file_path = os.path.join(self.save_dir, f"{img_id}{file_ext}")
                if os.path.exists(file_path):
                    print(f"文件已存在，跳过: {img_id}{file_ext}")
                    return True
                
                # 下载图片
                img_response = requests.get(img_url, headers=self.headers, stream=True)
                img_response.raise_for_status()
                
                # 保存图片
                with open(file_path, 'wb') as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"已下载: {img_id}{file_ext}")
                return True
                
            except requests.exceptions.HTTPError as e:
                if "429" in str(e):  # Too Many Requests
                    retries += 1
                    wait_time = 5 * retries  # 递增等待时间
                    print(f"请求过于频繁，等待{wait_time}秒后重试 ({retries}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    print(f"下载图片{image_url}失败: {e}")
                    return False
            except Exception as e:
                print(f"下载图片{image_url}失败: {e}")
                return False
        
        print(f"达到最大重试次数，下载失败: {image_url}")
        return False
    
    def start_download(self):
        """开始下载过程"""
        print(f"开始从Wallhaven下载{self.category}分类的图片，共{self.pages}页")
        print(f"图片将保存到: {self.save_dir}")
        
        total_images = 0
        successful_downloads = 0
        
        start_time = time.time()
        
        # 获取所有页面的图片URL
        all_image_urls = []
        for page in range(1, self.pages + 1):
            print(f"正在获取第{page}页的图片链接...")
            page_urls = self.get_image_urls(page)
            all_image_urls.extend(page_urls)
            print(f"第{page}页找到{len(page_urls)}张图片")
        
        total_images = len(all_image_urls)
        print(f"总共找到{total_images}张图片，开始下载...")
        
        # 使用线程池下载图片
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            results = list(executor.map(self.download_image, all_image_urls))
        
        successful_downloads = sum(results)
        elapsed_time = time.time() - start_time
        
        print("\n下载完成!")
        print(f"总图片数: {total_images}")
        print(f"成功下载: {successful_downloads}")
        print(f"失败: {total_images - successful_downloads}")
        print(f"耗时: {elapsed_time:.2f}秒")

def main():
    parser = argparse.ArgumentParser(description='Wallhaven图片批量下载器')
    parser.add_argument('-c', '--category', default='latest', 
                        choices=['latest', 'hot', 'toplist', 'random'],
                        help='要下载的分类 (默认: latest)')
    parser.add_argument('-p', '--pages', type=int, default=1,
                        help='要下载的页数 (默认: 1)')
    parser.add_argument('-d', '--directory', default='./wallpapers',
                        help='图片保存位置 (默认: ./wallpapers)')
    parser.add_argument('-t', '--threads', type=int, default=3,
                        help='下载线程数 (默认: 3)')
    parser.add_argument('-r', '--time-range', default='1M',
                        choices=['1d', '3d', '1w', '1M', '3M', '6M', '1y'],
                        help='Toplist时间范围 (默认: 1M)')
    parser.add_argument('--categories', default='111',
                        help='图片分类 (General,Anime,People，例如：100表示只看General)')
    parser.add_argument('--purity', default='100',
                        help='图片纯度 (SFW,Sketchy,NSFW，例如：100表示只看SFW)')
    
    args = parser.parse_args()
    
    # 创建下载器并开始下载
    downloader = WallhavenDownloader(
        save_dir=args.directory,
        category=args.category,
        pages=args.pages,
        threads=args.threads,
        time_range=args.time_range,
        categories=args.categories,
        purity=args.purity
    )
    
    downloader.start_download()

if __name__ == '__main__':
    main()