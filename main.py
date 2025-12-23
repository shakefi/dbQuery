import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from connection_dialog import ConnectionDialog
from spatial_dialog import SpatialGeometryDialog
from database import DatabaseManager
from dbexport import DataExporter


class DBQueryApp:

    def __init__(self, root):
        self.root = root
        self.root.title("空间数据查询与导出工具")
        self.root.geometry("1000x700")
        
        # 初始化数据库管理器
        self.db_manager = DatabaseManager()
        
        # 创建菜单栏
        self.create_menu()
        
        # 使用PanedWindow实现可调整大小的布局
        self.main_paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧面板：表树形列表
        self.left_frame = ttk.LabelFrame(self.main_paned, text="数据库表")
        self.main_paned.add(self.left_frame, weight=1)

        # 表查询输入框框架
        search_frame = ttk.Frame(self.left_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="搜索表:").pack(side="left", padx=5)
        
        self.table_search_var = tk.StringVar()
        self.table_search_entry = ttk.Entry(search_frame, textvariable=self.table_search_var, width=15)
        self.table_search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.table_search_entry.bind("<KeyRelease>", self.filter_tables)
        
        # 清空搜索按钮
        clear_search_btn = ttk.Button(search_frame, text="×", width=3, command=self.clear_table_search)
        clear_search_btn.pack(side="left", padx=2)
        
        # 表树
        self.table_tree = ttk.Treeview(self.left_frame, show="tree")
        self.table_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 保存所有表数据用于过滤
        self.all_tables = []

        # 右侧面板（使用垂直分割）
        self.right_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.right_paned, weight=3)
        
        # 右上部分：查询条件
        self.query_frame = ttk.LabelFrame(self.right_paned, text="查询条件")
        self.right_paned.add(self.query_frame, weight=1)
        
        # 查询条件输入区（合并属性过滤和SQL查询）
        self.query_input_frame = ttk.LabelFrame(self.query_frame, text="查询条件")
        self.query_input_frame.pack(fill="x", padx=10, pady=5)
        
        # 查询模式选择（单选按钮）
        self.query_mode_var = tk.StringVar(value="WHERE")
        
        mode_frame = ttk.Frame(self.query_input_frame)
        mode_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Radiobutton(mode_frame, text="WHERE条件", variable=self.query_mode_var, 
                       value="WHERE", command=self.on_query_mode_change).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="完整SQL", variable=self.query_mode_var, 
                       value="SQL", command=self.on_query_mode_change).pack(side="left", padx=5)
        
        # 输入框（根据模式切换内容和提示）
        self.query_input = tk.Text(self.query_input_frame, height=4, wrap=tk.WORD)
        self.query_input.pack(fill="x", padx=5, pady=5)
        
        # 提示标签
        self.query_hint_label = ttk.Label(self.query_input_frame, text="", font=("Arial", 8))
        self.query_hint_label.pack(anchor="w", padx=5, pady=0)
        
        # 更新初始提示
        self.update_query_hint()
        
        # 空间过滤条件
        self.spatial_frame = ttk.LabelFrame(self.query_frame, text="空间过滤条件")
        self.spatial_frame.pack(fill="x", padx=10, pady=5)
        
        # 几何字段选择框架
        geom_field_frame = ttk.Frame(self.spatial_frame)
        geom_field_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(geom_field_frame, text="几何字段:").pack(side="left", padx=5)
        
        self.geom_field_var = tk.StringVar()
        self.geom_field_combo = ttk.Combobox(geom_field_frame, textvariable=self.geom_field_var, state="readonly", width=20)
        self.geom_field_combo.pack(side="left", padx=5)
        self.geom_field_combo.bind("<<ComboboxSelected>>", self.on_geom_field_select)
        
        # 按钮框架
        spatial_button_frame = ttk.Frame(self.spatial_frame)
        spatial_button_frame.pack(fill="x", padx=5, pady=5)
        
        # 空间文件选择按钮（使用更醒目的样式）
        self.spatial_button = ttk.Button(spatial_button_frame, 
                                       text="? 选择空间文件 (GeoJSON/Shapefile)", 
                                       command=self.load_spatial_file,
                                       style="Accent.TButton")
        self.spatial_button.pack(side="left", padx=5, pady=2)
        
        # 显示空间图形按钮
        self.show_spatial_button = ttk.Button(spatial_button_frame, 
                                            text="?? 显示", 
                                            command=self.show_spatial_geometry, 
                                            state="disabled",
                                            style="Accent.TButton")
        self.show_spatial_button.pack(side="left", padx=5, pady=2)
        
        self.spatial_label = ttk.Label(self.spatial_frame, text="未选择空间文件")
        self.spatial_label.pack(pady=5)
        
        # 查询按钮区域（优化布局和样式）
        query_button_frame = ttk.Frame(self.query_frame)
        query_button_frame.pack(fill="x", padx=10, pady=10)
        
        # 执行查询按钮（使用更醒目的样式，增加宽度）
        self.query_button = ttk.Button(query_button_frame, 
                                     text="? 执行查询", 
                                     command=self.execute_query,
                                     style="Success.TButton",
                                     width=20)
        self.query_button.pack(side="left", padx=5)
        
        # 添加说明标签（放在按钮右侧，确保可见）
        ttk.Label(query_button_frame, text="根据上方选择的模式执行查询", font=("Arial", 9, "italic")).pack(side="left", padx=10, fill="x", expand=True)
        
        # 配置按钮样式
        self.configure_button_styles()
        
        # 右下部分：查询结果
        self.result_frame = ttk.LabelFrame(self.right_paned, text="查询结果")
        self.right_paned.add(self.result_frame, weight=2)
        
        # 查询结果统计信息框架
        self.result_info_frame = ttk.Frame(self.result_frame)
        self.result_info_frame.pack(fill="x", padx=5, pady=5)
        
        self.result_info_label = ttk.Label(self.result_info_frame, text="暂无查询结果")
        self.result_info_label.pack(side="left", padx=5)
        
        # 导出按钮组放在统计信息行右侧，确保可见
        export_button_frame = ttk.Frame(self.result_info_frame)
        export_button_frame.pack(side="right", padx=5)
        
        # 导出Shapefile按钮
        self.export_shape_button = ttk.Button(export_button_frame, 
                                            text="?? 导出Shapefile", 
                                            command=self.export_to_shapefile,
                                            style="Accent.TButton")
        self.export_shape_button.pack(side="left", padx=2)
        
        # 导出GeoJSON按钮
        self.export_geojson_button = ttk.Button(export_button_frame, 
                                              text="? 导出GeoJSON", 
                                              command=self.export_to_geojson,
                                              style="Accent.TButton")
        self.export_geojson_button.pack(side="left", padx=2)
        
        # 导出Excel按钮
        self.export_button = ttk.Button(export_button_frame, 
                                      text="? 导出Excel", 
                                      command=self.export_to_excel,
                                      style="Accent.TButton")
        self.export_button.pack(side="left", padx=2)
        
        # 创建结果显示容器
        result_container = ttk.Frame(self.result_frame)
        result_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建滚动条
        self.result_scrollbar_y = ttk.Scrollbar(result_container, orient="vertical")
        self.result_scrollbar_x = ttk.Scrollbar(result_container, orient="horizontal")
        
        # 创建结果树并绑定滚动条
        self.result_tree = ttk.Treeview(
            result_container,
            height=15,
            yscrollcommand=self.result_scrollbar_y.set,
            xscrollcommand=self.result_scrollbar_x.set
        )
        
        # 配置滚动条命令
        self.result_scrollbar_y.config(command=self.result_tree.yview)
        self.result_scrollbar_x.config(command=self.result_tree.xview)
        
        # 布局：使用grid布局确保滚动条正确显示
        self.result_tree.grid(row=0, column=0, sticky="nsew")
        self.result_scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.result_scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # 配置容器的行列权重
        result_container.grid_rowconfigure(0, weight=1)
        result_container.grid_columnconfigure(0, weight=1)
        
        # 绑定右键菜单事件
        self.result_tree.bind("<Button-3>", self.show_copy_context_menu)  # 右键点击
        self.result_tree.bind("<<TreeviewSelect>>", self.on_result_select)  # 选中事件
        
        # 复制功能相关变量
        self.selected_column = None
        self.selected_row_data = None
        self.selected_cell_value = None
        
        # 状态栏
        self.status_bar = ttk.Label(root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初始化变量
        self.spatial_geom = None
        self.schema = None
        self.query_result = []  # 保存查询结果用于导出
        
        # 初始化数据导出器
        self.data_exporter = DataExporter(
            db_manager=self.db_manager,
            get_query_input=self.get_query_input_content,
            get_geom_field=self.get_current_geom_field,
            get_spatial_geom=self.get_current_spatial_geom
        )

    def create_menu(self):
        """创建菜单栏"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="连接...", command=self.show_connection_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

    def show_connection_dialog(self):
        """显示连接对话框"""
        dialog = ConnectionDialog(self.root)
        config = dialog.show()
        if config:
            self.connect_db(config)

    def connect_db(self, config):
        """连接数据库"""
        success, message = self.db_manager.connect(config)
        if success:
            # 更新状态
            self.status_bar.config(text=message)
            messagebox.showinfo("成功", "数据库连接成功！")
            # 获取表列表
            self.schema = config['schema']
            self.load_tables()
        else:
            messagebox.showerror("错误", message)
            self.status_bar.config(text="连接失败")

    def load_tables(self):
        """加载数据库表到树形控件"""
        # 清空现有表
        for item in self.table_tree.get_children():
            self.table_tree.delete(item)
        tables = self.db_manager.load_tables()
        # 保存所有表数据用于过滤
        self.all_tables = tables
        
        # 添加到树形控件
        for table_name, table_type in tables:
            self.table_tree.insert("", "end", text=table_name, values=(table_type,))
        
        # 绑定选择事件
        self.table_tree.bind("<<TreeviewSelect>>", self.on_table_select)

    def filter_tables(self, event=None):
        """根据输入的表名过滤树中的表"""
        search_text = self.table_search_var.get().strip().lower()
        
        # 清空当前显示的表
        for item in self.table_tree.get_children():
            self.table_tree.delete(item)
        
        # 如果搜索框为空，显示所有表
        if not search_text:
            for table_name, table_type in self.all_tables:
                self.table_tree.insert("", "end", text=table_name, values=(table_type,))
        else:
            # 根据搜索条件过滤表
            for table_name, table_type in self.all_tables:
                if search_text in table_name.lower():
                    self.table_tree.insert("", "end", text=table_name, values=(table_type,))
        
        # 更新状态栏显示过滤结果
        visible_count = len(self.table_tree.get_children())
        total_count = len(self.all_tables)
        if search_text:
            self.status_bar.config(text=f"搜索 '{search_text}': 显示 {visible_count}/{total_count} 个表")
        else:
            self.status_bar.config(text=f"共 {total_count} 个表")
    
    def clear_table_search(self):
        """清空表搜索框并显示所有表"""
        self.table_search_var.set("")
        self.filter_tables()

    def on_table_select(self, event):
        """当选择表时触发"""
        selection = self.table_tree.selection()
        if selection:
            item = self.table_tree.item(selection[0])
            table_name = item['text']
            self.db_manager.set_current_table(table_name)
            self.status_bar.config(text=f"已选择表: {table_name}")
            # 加载该表的几何字段
            self.load_geometry_fields(table_name)

    def load_geometry_fields(self, table_name):
        """加载指定表的几何字段"""
        geometry_columns = self.db_manager.get_geometry_columns(table_name)
        
        # 清空现有选项
        self.geom_field_combo['values'] = []
        self.geom_field_var.set("")
        
        if geometry_columns:
            # 设置几何字段选项
            self.geom_field_combo['values'] = geometry_columns
            # 默认选择第一个几何字段
            self.geom_field_var.set(geometry_columns[0])
            self.status_bar.config(text=f"已选择表: {table_name} | 找到 {len(geometry_columns)} 个几何字段")
        else:
            self.status_bar.config(text=f"已选择表: {table_name} | 未找到几何字段")

    def on_query_mode_change(self):
        """查询模式切换时更新提示"""
        self.update_query_hint()
        # 清空输入框
        self.query_input.delete("1.0", tk.END)

    def update_query_hint(self):
        """更新查询提示信息"""
        mode = self.query_mode_var.get()
        if mode == "WHERE":
            self.query_hint_label.config(text="示例: age > 25 AND name LIKE '张%'")
        else:
            self.query_hint_label.config(text="示例: SELECT * FROM table_name WHERE age > 25")

    def on_geom_field_select(self, event):
        """当选择几何字段时触发"""
        selected_field = self.geom_field_var.get()
        if selected_field:
            self.status_bar.config(text=f"已选择几何字段: {selected_field}")

    def load_spatial_file(self):
        """加载空间文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("GeoJSON", "*.geojson"), ("Shapefile", "*.shp"), ("所有文件", "*.*")]
        )
        if file_path:
            success, geometry, message = self.db_manager.load_spatial_file(file_path)
            
            if success:
                self.spatial_geom = geometry
                self.spatial_label.config(text=message)
                self.show_spatial_button.config(state="normal")  # 启用显示按钮
                messagebox.showinfo("成功", "空间文件加载成功！")
            else:
                messagebox.showerror("错误", message)

    def execute_query(self):
        """执行查询"""
        # 获取查询内容
        query_content = self.query_input.get("1.0", tk.END).strip()
        
        # 根据模式执行不同查询
        mode = self.query_mode_var.get()
        
        if mode == "WHERE":
            # WHERE条件模式：允许空条件查询全表或空间过滤
            geom_field = self.geom_field_var.get()
            
            # 如果查询条件为空，但有空间过滤条件，只执行空间查询
            if not query_content and self.spatial_geom:
                success, result = self.db_manager.execute_query("", self.spatial_geom, geom_field)
            # 如果查询条件为空，也没有空间过滤条件，查询全表
            elif not query_content and not self.spatial_geom:
                if not self.db_manager.current_table:
                    messagebox.showwarning("警告", "请先选择表！")
                    return
                # 执行全表查询
                success, result = self.db_manager.execute_query("", None, None)
            else:
                # 正常的WHERE条件查询（可能包含空间过滤）
                success, result = self.db_manager.execute_query(query_content, self.spatial_geom, geom_field)
        else:
            # 完整SQL模式：直接执行自定义SQL
            if not query_content:
                messagebox.showwarning("警告", "请输入自定义SQL查询！")
                return
            success, result = self.db_manager.execute_custom_sql(query_content)
        
        if success:
            self.display_query_result(result)
        else:
            messagebox.showerror("错误", result)
            self.result_info_label.config(text="查询失败")
            self.query_result = []  # 查询失败时清空结果

    def display_query_result(self, result):
        """显示查询结果（包含字段宽度自适应）"""
        columns = result['columns']
        data = result['data']
        row_count = result['row_count']
        
        # 保存查询结果用于导出
        self.query_result = data
        
        # 清空并填充结果树
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self.result_tree["columns"] = columns
        self.result_tree.heading("#0", text="序号")
        self.result_tree.column("#0", width=50, minwidth=50, stretch=False)
        
        # 获取当前选中的几何字段
        geom_field = self.geom_field_var.get()
        
        # 计算每列的最佳宽度
        column_widths = {}
        for col in columns:
            # 默认宽度
            max_width = 100
            # 计算列标题宽度
            title_width = len(col) * 8 + 20
            max_width = max(max_width, title_width)
            
            # 计算该列数据的最大宽度（检查前50行数据）
            for i, row in enumerate(data[:50]):
                if len(columns) == len(row):
                    cell_value = str(row[columns.index(col)])
                    cell_width = len(cell_value) * 8 + 20
                    max_width = max(max_width, cell_width)
            
            # 限制最大宽度
            max_width = min(max_width, 300)
            column_widths[col] = max_width
        
        # 设置列
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=column_widths[col], minwidth=100, stretch=False)
        
        # 准备显示数据：将几何字段转换为WKT格式
        display_data = []
        for row in data:
            display_row = []
            for i, col in enumerate(columns):
                value = row[i]
                # 如果是几何字段，转换为WKT格式
                if col == geom_field and value:
                    try:
                        # 尝试将几何对象转换为WKT
                        from shapely import wkt
                        if hasattr(value, 'wkt'):
                            display_row.append(value.wkt)
                        elif isinstance(value, str) and value.startswith('SRID='):
                            # 如果是PostGIS格式，提取WKT部分
                            wkt_str = value.split(';')[1] if ';' in value else value
                            display_row.append(wkt_str)
                        else:
                            display_row.append(str(value))
                    except:
                        display_row.append(str(value))
                else:
                    display_row.append(value)
            display_data.append(display_row)
        
        # 填充数据
        for i, row in enumerate(display_data):
            self.result_tree.insert("", "end", text=str(i+1), values=row)
        
        # 更新结果统计信息
        if row_count > 0:
            self.result_info_label.config(text=f"查询结果：共 {row_count} 条记录，显示 {len(data)} 条")
        else:
            self.result_info_label.config(text="查询结果：未找到匹配的记录")
        
        # 更新状态栏
        self.status_bar.config(text=f"查询完成，找到 {row_count} 条记录")

    def show_spatial_geometry(self):
        """显示空间几何图形对话框"""
        if not self.spatial_geom:
            messagebox.showerror("错误", "没有加载空间几何图形！")
            return
        
        dialog = SpatialGeometryDialog(self.root, self.spatial_geom)
        dialog.show()

    def configure_button_styles(self):
        """配置按钮样式，让按钮更醒目"""
        style = ttk.Style()
        
        # 配置Accent样式（用于空间文件按钮）
        style.configure("Accent.TButton",
                       background="#2196F3",
                       foreground="white",
                       font=("Arial", 10, "bold"),
                       padding=(10, 5))
        
        # 配置Success样式（用于执行查询按钮）
        style.configure("Success.TButton",
                       background="#4CAF50",
                       foreground="white",
                       font=("Arial", 11, "bold"),
                       padding=(15, 8))
        
        # 尝试设置按钮悬停效果（如果主题支持）
        try:
            style.map("Accent.TButton",
                     background=[("active", "#1976D2"), ("pressed", "#0D47A1")])
            style.map("Success.TButton",
                     background=[("active", "#45a049"), ("pressed", "#2d7a31")])
        except:
            pass
    
    def on_result_select(self, event):
        """当选择结果树中的项目时触发"""
        selection = self.result_tree.selection()
        if not selection:
            return
        
        # 获取选中的行数据
        item = self.result_tree.item(selection[0])
        row_values = item['values']
        self.selected_row_data = row_values
        
        # 获取列名
        columns = self.result_tree["columns"]
        
        # 获取鼠标位置对应的列（用于单元格复制）
        try:
            # 获取鼠标在Treeview中的位置
            x, y = event.x, event.y
            # 遍历列找到鼠标所在的列
            col_index = 0
            total_width = 50  # 序号列宽度
            for i, col in enumerate(columns):
                col_width = self.result_tree.column(col)['width']
                if x < total_width + col_width:
                    col_index = i
                    break
                total_width += col_width
            
            # 设置选中的列和单元格值
            if col_index < len(columns):
                self.selected_column = columns[col_index]
                self.selected_cell_value = str(row_values[col_index])
            else:
                self.selected_column = None
                self.selected_cell_value = None
        except:
            self.selected_column = None
            self.selected_cell_value = None

    def show_copy_context_menu(self, event):
        """显示复制功能的右键菜单"""
        if not self.result_tree.selection():
            return
        
        # 创建右键菜单
        menu = tk.Menu(self.root, tearoff=0)
        
        # 1. 复制整行
        menu.add_command(label="复制整行记录", command=self.copy_selected_row)
        
        # 2. 复制整行（JSON格式）
        menu.add_command(label="复制整行记录 (JSON格式)", command=self.copy_selected_row_json)
        
        # 3. 复制单元格
        if self.selected_cell_value:
            menu.add_command(label=f"复制单元格: {self.selected_cell_value[:50]}{'...' if len(self.selected_cell_value) > 50 else ''}", 
                           command=self.copy_selected_cell)
        
        # 4. 复制列（前500条记录的该列值）
        if self.selected_column:
            menu.add_command(label=f"复制列 '{self.selected_column}' (前500条)", 
                           command=self.copy_column_values)
        
        menu.add_separator()
        menu.add_command(label="取消", command=lambda: menu.destroy())
        
        # 显示菜单
        menu.tk_popup(event.x_root, event.y_root)

    def copy_selected_row(self):
        """复制选中的整行记录"""
        if not self.selected_row_data:
            messagebox.showwarning("警告", "请先选择一行记录！")
            return
        
        # 将行数据转换为字符串（用制表符分隔列，方便粘贴到Excel）
        row_text = "\t".join(str(v) if v is not None else "" for v in self.selected_row_data)
        
        # 复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(row_text)
        self.root.update()  # 确保剪贴板内容被保存
        
        self.status_bar.config(text=f"已复制整行记录（{len(self.selected_row_data)}列）")

    def copy_selected_cell(self):
        """复制选中的单元格"""
        if not self.selected_cell_value:
            messagebox.showwarning("警告", "请先选择一个单元格！")
            return
        
        # 复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(self.selected_cell_value)
        self.root.update()
        
        self.status_bar.config(text=f"已复制单元格: {self.selected_cell_value[:50]}{'...' if len(self.selected_cell_value) > 50 else ''}")

    def copy_column_values(self):
        """复制选中列的前500条记录的值"""
        if not self.selected_column:
            messagebox.showwarning("警告", "请先选择一列！")
            return
        
        if not self.query_result:
            messagebox.showwarning("警告", "没有查询结果！")
            return
        
        # 获取列索引
        columns = self.result_tree["columns"]
        try:
            col_index = list(columns).index(self.selected_column)
        except ValueError:
            messagebox.showerror("错误", "无法找到选中的列！")
            return
        
        # 提取该列的前500条记录的值
        column_values = []
        for i, row in enumerate(self.query_result[:500]):
            if col_index < len(row):
                value = row[col_index]
                column_values.append(str(value) if value is not None else "")
        
        if not column_values:
            messagebox.showwarning("警告", "该列没有数据！")
            return
        
        # 将值用换行符连接
        column_text = "\n".join(column_values)
        
        # 复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(column_text)
        self.root.update()
        
        self.status_bar.config(text=f"已复制列 '{self.selected_column}' 的 {len(column_values)} 条记录")

    def copy_selected_row_json(self):
        """复制选中的整行记录为JSON格式"""
        if not self.selected_row_data:
            messagebox.showwarning("警告", "请先选择一行记录！")
            return
        
        # 获取列名
        columns = self.result_tree["columns"]
        
        # 构建JSON对象
        json_data = {}
        for i, col in enumerate(columns):
            if i < len(self.selected_row_data):
                value = self.selected_row_data[i]
                # 处理特殊值类型
                if value is None:
                    json_data[col] = None
                elif isinstance(value, (int, float, bool)):
                    json_data[col] = value
                else:
                    json_data[col] = str(value)
        
        # 转换为JSON字符串（使用ensure_ascii=False支持中文）
        import json
        json_text = json.dumps(json_data, ensure_ascii=False, indent=2)
        
        # 复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(json_text)
        self.root.update()
        
        self.status_bar.config(text=f"已复制JSON格式（{len(columns)}个字段）")

    def get_query_input_content(self):
        """获取查询输入内容"""
        return self.query_input.get("1.0", tk.END).strip()
    
    def get_current_geom_field(self):
        """获取当前选中的几何字段"""
        return self.geom_field_var.get()
    
    def get_current_spatial_geom(self):
        """获取当前的空间几何"""
        return self.spatial_geom
    
    def export_to_excel(self):
        """导出为Excel的入口函数"""
        if not self.query_result:
            messagebox.showwarning("警告", "没有可导出的查询结果！")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            success, result = self.data_exporter.export_data(
                'excel', self.query_result, file_path,
                status_bar_callback=self.status_bar.config
            )
            
            if success:
                messagebox.showinfo("成功", result)
                self.status_bar.config(text=result.split('\n')[-1])
            else:
                messagebox.showerror("错误", result)
                self.status_bar.config(text="导出失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")
            self.status_bar.config(text="导出失败")
    
    def export_to_shapefile(self):
        """导出为Shapefile的入口函数"""
        if not self.query_result:
            messagebox.showwarning("警告", "没有可导出的查询结果！")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".shp",
            filetypes=[("Shapefile", "*.shp"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            success, result = self.data_exporter.export_data(
                'shapefile', self.query_result, file_path,
                status_bar_callback=self.status_bar.config
            )
            
            if success:
                messagebox.showinfo("成功", result)
                self.status_bar.config(text=result.split('\n')[-1])
            else:
                messagebox.showerror("错误", result)
                self.status_bar.config(text="导出失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")
            self.status_bar.config(text="导出失败")
    
    def export_to_geojson(self):
        """导出为GeoJSON的入口函数"""
        if not self.query_result:
            messagebox.showwarning("警告", "没有可导出的查询结果！")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".geojson",
            filetypes=[("GeoJSON", "*.geojson"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            success, result = self.data_exporter.export_data(
                'geojson', self.query_result, file_path,
                status_bar_callback=self.status_bar.config
            )
            
            if success:
                messagebox.showinfo("成功", result)
                self.status_bar.config(text=result.split('\n')[-1])
            else:
                messagebox.showerror("错误", result)
                self.status_bar.config(text="导出失败")
                
        except Exception as e:
            print(f"导出GeoJSON时发生错误: {e}")
            messagebox.showerror("错误", f"导出失败: {e}")
            self.status_bar.config(text="导出失败")
    
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo("关于", "空间数据查询与导出工具\n版本 1.0\n\n模块化版本")


if __name__ == "__main__":
    root = tk.Tk()
    app = DBQueryApp(root)
    root.mainloop()
