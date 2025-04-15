import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from wallhaven_downloader import WallhavenDownloader

class WallhavenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallhaven壁纸下载器")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("TFrame", background="#f0f0f0")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建设置区域
        self.create_settings_frame()
        
        # 创建日志区域
        self.create_log_frame()
        
        # 创建按钮区域
        self.create_button_frame()
        
        # 下载状态变量
        self.is_downloading = False
        self.download_thread = None
        
        # 进度变量
        self.total_images = 0
        self.downloaded_images = 0
        self.failed_images = 0
        
    def create_settings_frame(self):
        # 设置区域框架
        settings_frame = ttk.LabelFrame(self.main_frame, text="下载设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        # 分类选择
        ttk.Label(settings_frame, text="分类:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(value="latest")
        self.category_combo = ttk.Combobox(settings_frame, textvariable=self.category_var, width=15)
        self.category_combo['values'] = ('latest', 'hot', 'toplist', 'random')
        self.category_combo['state'] = 'readonly'
        self.category_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.category_combo.bind("<<ComboboxSelected>>", self.on_category_change)
        
        # 页数设置
        ttk.Label(settings_frame, text="页数:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(10, 0))
        self.pages_var = tk.IntVar(value=1)
        pages_spinbox = ttk.Spinbox(settings_frame, from_=1, to=100, textvariable=self.pages_var, width=5)
        pages_spinbox.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 线程数设置
        ttk.Label(settings_frame, text="线程数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.threads_var = tk.IntVar(value=3)
        threads_spinbox = ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.threads_var, width=5)
        threads_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 时间范围设置（仅在toplist分类下可用）
        ttk.Label(settings_frame, text="时间范围:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(10, 0))
        self.time_range_var = tk.StringVar(value="1M")
        self.time_range_combo = ttk.Combobox(settings_frame, textvariable=self.time_range_var, width=10, state="disabled")
        self.time_range_combo['values'] = ('1d', '3d', '1w', '1M', '3M', '6M', '1y')
        self.time_range_combo['state'] = 'readonly'
        self.time_range_combo.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 图片类型设置
        ttk.Label(settings_frame, text="图片类型:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # 使用Frame来包含复选框
        categories_frame = ttk.Frame(settings_frame)
        categories_frame.grid(row=3, column=1, columnspan=3, sticky=tk.W, pady=5)
        
        # 创建复选框变量
        self.general_var = tk.BooleanVar(value=True)
        self.anime_var = tk.BooleanVar(value=True)
        self.people_var = tk.BooleanVar(value=True)
        
        # 创建复选框
        ttk.Checkbutton(categories_frame, text="General", variable=self.general_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(categories_frame, text="Anime", variable=self.anime_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(categories_frame, text="People", variable=self.people_var).pack(side=tk.LEFT, padx=5)
        
        # 图片纯度设置
        ttk.Label(settings_frame, text="图片纯度:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # 使用Frame来包含复选框
        purity_frame = ttk.Frame(settings_frame)
        purity_frame.grid(row=4, column=1, columnspan=3, sticky=tk.W, pady=5)
        
        # 创建复选框变量
        self.sfw_var = tk.BooleanVar(value=True)
        self.sketchy_var = tk.BooleanVar(value=False)
        self.nsfw_var = tk.BooleanVar(value=False)
        
        # 创建复选框
        ttk.Checkbutton(purity_frame, text="SFW", variable=self.sfw_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(purity_frame, text="Sketchy", variable=self.sketchy_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(purity_frame, text="NSFW", variable=self.nsfw_var).pack(side=tk.LEFT, padx=5)
        
        # 保存目录设置
        ttk.Label(settings_frame, text="保存位置:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.save_dir_var = tk.StringVar(value="./wallpapers")
        save_dir_entry = ttk.Entry(settings_frame, textvariable=self.save_dir_var, width=40)
        save_dir_entry.grid(row=5, column=1, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        
        browse_button = ttk.Button(settings_frame, text="浏览...", command=self.browse_directory)
        browse_button.grid(row=5, column=4, sticky=tk.W, padx=5, pady=5)
    
    def on_category_change(self, event):
        """当分类选择改变时调用"""
        if self.category_var.get() == "toplist":
            self.time_range_combo.config(state="readonly")
        else:
            self.time_range_combo.config(state="disabled")
        
    def create_log_frame(self):
        # 日志区域框架
        log_frame = ttk.LabelFrame(self.main_frame, text="下载日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建日志文本框和滚动条
        self.log_text = tk.Text(log_frame, height=10, width=70, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 设置日志文本框只读
        self.log_text.config(state=tk.DISABLED)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W, pady=2)
        
    def create_button_frame(self):
        # 按钮区域框架
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 开始下载按钮
        self.start_button = ttk.Button(button_frame, text="开始下载", command=self.start_download)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 停止下载按钮
        self.stop_button = ttk.Button(button_frame, text="停止下载", command=self.stop_download, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 打开下载文件夹按钮
        self.open_folder_button = ttk.Button(button_frame, text="打开下载文件夹", command=self.open_download_folder)
        self.open_folder_button.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        exit_button = ttk.Button(button_frame, text="退出", command=self.root.destroy)
        exit_button.pack(side=tk.RIGHT, padx=5)
        
    def browse_directory(self):
        """打开文件夹选择对话框"""
        directory = filedialog.askdirectory(initialdir=os.path.abspath(self.save_dir_var.get()))
        if directory:
            self.save_dir_var.set(directory)
    
    def log_message(self, message):
        """向日志区域添加消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_progress(self, downloaded, total):
        """更新进度条和状态"""
        if total > 0:
            progress = (downloaded / total) * 100
            self.progress_var.set(progress)
            self.status_var.set(f"已下载: {downloaded}/{total} ({progress:.1f}%)")
        else:
            self.progress_var.set(0)
            self.status_var.set("就绪")
    
    def start_download(self):
        """开始下载过程"""
        if self.is_downloading:
            return
        
        # 获取设置
        category = self.category_var.get()
        pages = self.pages_var.get()
        threads = self.threads_var.get()
        save_dir = self.save_dir_var.get()
        
        # 验证设置
        if pages < 1:
            messagebox.showerror("错误", "页数必须大于0")
            return
        
        if threads < 1:
            messagebox.showerror("错误", "线程数必须大于0")
            return
        
        # 更新UI状态
        self.is_downloading = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 清空日志
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # 重置进度
        self.total_images = 0
        self.downloaded_images = 0
        self.failed_images = 0
        self.update_progress(0, 0)
        
        # 创建并启动下载线程
        self.download_thread = threading.Thread(target=self.download_task, args=(category, pages, threads, save_dir))
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def download_task(self, category, pages, threads, save_dir):
        """下载任务线程"""
        try:
            # 创建自定义的下载器类，重写输出方法
            class GUIWallhavenDownloader(WallhavenDownloader):
                def __init__(self, gui, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.gui = gui
                
                def get_image_urls(self, page):
                    self.gui.log_message(f"正在获取第{page}页的图片链接...")
                    return super().get_image_urls(page)
                
                def download_image(self, image_url, max_retries=3):
                    result = super().download_image(image_url, max_retries)
                    if result:
                        self.gui.downloaded_images += 1
                    else:
                        self.gui.failed_images += 1
                    
                    self.gui.update_progress(self.gui.downloaded_images, self.gui.total_images)
                    return result
            
            # 获取分类和纯度设置
            categories = ''
            categories += '1' if self.general_var.get() else '0'
            categories += '1' if self.anime_var.get() else '0'
            categories += '1' if self.people_var.get() else '0'
            
            purity = ''
            purity += '1' if self.sfw_var.get() else '0'
            purity += '1' if self.sketchy_var.get() else '0'
            purity += '1' if self.nsfw_var.get() else '0'
            
            # 确保至少选择了一个分类和纯度
            if categories == '000':
                self.log_message("错误：至少需要选择一种图片类型！")
                return
            
            if purity == '000':
                self.log_message("错误：至少需要选择一种图片纯度！")
                return
            
            # 获取时间范围
            time_range = self.time_range_var.get()
            
            # 创建下载器实例
            downloader = GUIWallhavenDownloader(
                gui=self,
                save_dir=save_dir,
                category=category,
                pages=pages,
                threads=threads,
                time_range=time_range,
                categories=categories,
                purity=purity
            )
            
            # 记录开始时间
            start_time = time.time()
            self.log_message(f"开始从Wallhaven下载{category}分类的图片，共{pages}页")
            self.log_message(f"图片将保存到: {save_dir}")
            
            # 获取所有页面的图片URL
            all_image_urls = []
            for page in range(1, pages + 1):
                if not self.is_downloading:  # 检查是否被停止
                    break
                
                page_urls = downloader.get_image_urls(page)
                all_image_urls.extend(page_urls)
                self.log_message(f"第{page}页找到{len(page_urls)}张图片")
            
            self.total_images = len(all_image_urls)
            self.log_message(f"总共找到{self.total_images}张图片，开始下载...")
            
            # 使用线程池下载图片
            if self.is_downloading and self.total_images > 0:
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    results = list(executor.map(downloader.download_image, all_image_urls))
                
                # 计算结果
                successful_downloads = sum(results)
                elapsed_time = time.time() - start_time
                
                self.log_message("\n下载完成!")
                self.log_message(f"总图片数: {self.total_images}")
                self.log_message(f"成功下载: {successful_downloads}")
                self.log_message(f"失败: {self.total_images - successful_downloads}")
                self.log_message(f"耗时: {elapsed_time:.2f}秒")
            
        except Exception as e:
            self.log_message(f"发生错误: {str(e)}")
        finally:
            # 恢复UI状态
            self.is_downloading = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def stop_download(self):
        """停止下载过程"""
        if not self.is_downloading:
            return
        
        self.log_message("正在停止下载...")
        self.is_downloading = False
        
        # 等待线程结束
        if self.download_thread and self.download_thread.is_alive():
            self.download_thread.join(0.1)  # 非阻塞等待
    
    def open_download_folder(self):
        """打开下载文件夹"""
        save_dir = os.path.abspath(self.save_dir_var.get())
        if os.path.exists(save_dir):
            # 使用系统默认的文件管理器打开文件夹
            import subprocess
            subprocess.Popen(f'explorer "{save_dir}"')
        else:
            messagebox.showerror("错误", f"文件夹不存在: {save_dir}")

def main():
    root = tk.Tk()
    app = WallhavenGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()