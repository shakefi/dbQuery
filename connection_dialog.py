import tkinter as tk
from tkinter import ttk
import json
import os

class ConnectionDialog:
    """数据库连接配置对话框"""

    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("数据库连接配置")
        self.dialog.geometry("400x320")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self.result = None
        self.config_file = "db_config.json"
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill="both", expand=True)

        # 从配置文件读取连接信息
        config = self.load_config()

        # 数据库地址
        ttk.Label(frame, text="数据库地址:").grid(row=0, column=0, sticky="w", pady=5)
        self.host_entry = ttk.Entry(frame, width=30)
        self.host_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        self.host_entry.insert(0, config.get('host', ''))

        # 数据库名
        ttk.Label(frame, text="数据库名:").grid(row=1, column=0, sticky="w", pady=5)
        self.database_entry = ttk.Entry(frame, width=30)
        self.database_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        self.database_entry.insert(0, config.get('database', ''))

        # Schema名
        ttk.Label(frame, text="Schema名:").grid(row=2, column=0, sticky="w", pady=5)
        self.schema_entry = ttk.Entry(frame, width=30)
        self.schema_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        self.schema_entry.insert(0, config.get('schema', ''))

        # 用户名
        ttk.Label(frame, text="用户名:").grid(row=3, column=0, sticky="w", pady=5)
        self.user_entry = ttk.Entry(frame, width=30)
        self.user_entry.grid(row=3, column=1, pady=5, padx=(10, 0))
        self.user_entry.insert(0, config.get('user', ''))

        # 密码
        ttk.Label(frame, text="密码:").grid(row=4, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(frame, width=30)
        self.password_entry.grid(row=4, column=1, pady=5, padx=(10, 0))
        self.password_entry.insert(0, config.get('password', ''))

        # 端口
        ttk.Label(frame, text="端口:").grid(row=5, column=0, sticky="w", pady=5)
        self.port_entry = ttk.Entry(frame, width=30)
        self.port_entry.grid(row=5, column=1, pady=5, padx=(10, 0))
        self.port_entry.insert(0, config.get('port', ''))

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="连接", command=self.on_connect).pack(side="left", padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side="left", padx=10)

    def load_config(self):
        """从配置文件读取数据库连接信息"""
        config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"读取配置文件失败: {e}")
        return config

    def save_config(self, config):
        """保存配置到配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def on_connect(self):
        """连接按钮点击事件"""
        # 获取当前输入的配置
        config = {
            'host': self.host_entry.get(),
            'database': self.database_entry.get(),
            'schema': self.schema_entry.get(),
            'user': self.user_entry.get(),
            'password': self.password_entry.get(),
            'port': self.port_entry.get()
        }
        
        # 保存配置到文件
        self.save_config(config)
        
        # 设置返回结果
        self.result = config
        self.dialog.destroy()

    def on_cancel(self):
        self.result = None
        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result
