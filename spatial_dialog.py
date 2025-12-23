import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import descartes
from shapely.geometry import shape as shapely_shape
from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon

class SpatialGeometryDialog:
    """空间几何图形显示对话框"""

    def __init__(self, parent, geometry):
        self.parent = parent
        self.geometry = geometry
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("空间几何图形查看器")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        """创建对话框控件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="空间几何图形详情", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # 使用Notebook创建标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=10)

        # 图形展示标签页
        plot_frame = ttk.Frame(notebook)
        notebook.add(plot_frame, text="图形展示")

        # 创建matplotlib图形
        self.create_plot(plot_frame)

        # WKT坐标标签页
        wkt_frame = ttk.Frame(notebook)
        notebook.add(wkt_frame, text="WKT坐标")

        self.create_wkt_display(wkt_frame)

        # 几何信息标签页
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="几何信息")

        self.create_info_display(info_frame)

        # 关闭按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        ttk.Button(button_frame, text="关闭", command=self.dialog.destroy).pack(side="right", padx=5)

    def create_plot(self, parent):
        """创建matplotlib图形"""
        try:
            # 创建图形
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)

            # 绘制几何图形
            if hasattr(self.geometry, '__geo_interface__'):
                shapely_geom = shapely_shape(self.geometry.__geo_interface__)
                # 根据几何类型选择合适的绘制方法
                geom_type = shapely_geom.geom_type
                
                if geom_type in ('Polygon', 'MultiPolygon'):
                    # 使用descartes.PolygonPatch绘制多边形
                    patch = descartes.PolygonPatch(shapely_geom, alpha=0.5, edgecolor='blue', facecolor='lightblue')
                    ax.add_patch(patch)
                elif geom_type in ('LineString', 'MultiLineString'):
                    # 绘制线
                    if geom_type == 'LineString':
                        x, y = shapely_geom.xy
                        ax.plot(x, y, 'b-', linewidth=2)
                    else:  # MultiLineString
                        for line in shapely_geom.geoms:
                            x, y = line.xy
                            ax.plot(x, y, 'b-', linewidth=2)
                elif geom_type in ('Point', 'MultiPoint'):
                    # 绘制点
                    if geom_type == 'Point':
                        x, y = shapely_geom.xy
                        ax.plot(x, y, 'bo', markersize=8)
                    else:  # MultiPoint
                        for point in shapely_geom.geoms:
                            x, y = point.xy
                            ax.plot(x, y, 'bo', markersize=8)
                else:
                    # 其他几何类型，显示信息
                    ax.text(0.5, 0.5, f"几何类型 '{geom_type}' 暂不支持图形展示", 
                           horizontalalignment='center', verticalalignment='center',
                           transform=ax.transAxes, fontsize=12)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    return

                # 设置图形范围
                bounds = shapely_geom.bounds
                ax.set_xlim(bounds[0] - 0.1, bounds[2] + 0.1)
                ax.set_ylim(bounds[1] - 0.1, bounds[3] + 0.1)
                ax.set_aspect('equal', adjustable='datalim')

                # 添加标题和标签
                ax.set_title("空间几何图形")
                ax.set_xlabel("经度/X")
                ax.set_ylabel("纬度/Y")
                ax.grid(True, alpha=0.3)
            else:
                # 如果无法绘制，显示错误信息
                ax.text(0.5, 0.5, "无法绘制此类型的几何图形", 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)

            # 将图形嵌入到tkinter中
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        except Exception as e:
            # 如果绘图失败，显示错误信息
            error_label = ttk.Label(parent, text=f"绘图失败: {str(e)}", foreground="red")
            error_label.pack(fill="both", expand=True, padx=20, pady=20)

    def create_wkt_display(self, parent):
        """创建WKT坐标显示"""
        # 获取WKT字符串
        try:
            wkt_text = self.geometry.wkt
        except:
            wkt_text = "无法获取WKT坐标"

        # 创建文本框架
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 添加标签
        ttk.Label(text_frame, text="WKT (Well-Known Text) 坐标:").pack(anchor="w", pady=(0, 5))

        # 创建文本区域
        text_widget = tk.Text(text_frame, wrap="word", height=15)
        text_widget.pack(fill="both", expand=True, side="left")

        # 添加滚动条
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.configure(yscrollcommand=scrollbar.set)

        # 插入WKT文本
        text_widget.insert("1.0", wkt_text)
        text_widget.configure(state="disabled")  # 设置为只读

    def create_info_display(self, parent):
        """创建几何信息显示"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            # 获取几何信息
            geom_type = self.geometry.geom_type
            area = self.geometry.area
            length = self.geometry.length
            bounds = self.geometry.bounds

            # 创建信息文本
            info_text = f"""几何类型: {geom_type}

面积: {area:.6f}

长度/周长: {length:.6f}

边界框:

  最小X: {bounds[0]:.6f}

  最小Y: {bounds[1]:.6f}

  最大X: {bounds[2]:.6f}

  最大Y: {bounds[3]:.6f}

坐标数量: {len(self.geometry.coords) if hasattr(self.geometry, 'coords') else 'N/A'}

"""

            # 显示信息
            text_widget = tk.Text(info_frame, wrap="word", height=10)
            text_widget.pack(fill="both", expand=True, side="left")

            # 添加滚动条
            scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=text_widget.yview)
            scrollbar.pack(side="right", fill="y")
            text_widget.configure(yscrollcommand=scrollbar.set)

            text_widget.insert("1.0", info_text)
            text_widget.configure(state="disabled")

        except Exception as e:
            error_label = ttk.Label(info_frame, text=f"获取几何信息失败: {str(e)}", foreground="red")
            error_label.pack(fill="both", expand=True)

    def show(self):
        """显示对话框"""
        self.dialog.wait_window()
