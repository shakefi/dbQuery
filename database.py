import psycopg2
import pandas as pd
import geopandas as gpd
from tkinter import messagebox

class DatabaseManager:
    """数据库管理器类，处理所有数据库相关操作"""

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.current_table = None
        self.query_result = None
        self.schema = None

    def connect(self, config):
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(
                host=config['host'],
                database=config['database'],
                user=config['user'],
                password=config['password'],
                port=config['port']
            )
            self.cursor = self.conn.cursor()
            self.schema = config['schema']
            return True, f"已连接到 {config['host']}/{config['database']}"
        except Exception as e:
            return False, f"连接数据库失败: {e}"

    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.conn = None
        self.cursor = None
        self.current_table = None
        self.query_result = None

    def load_tables(self):
        """加载数据库表列表"""
        if not self.cursor:
            return []
        try:
            self.cursor.execute(f"""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = '{self.schema}'
                ORDER BY table_name;
            """)
            tables = self.cursor.fetchall()
            return tables
        except Exception as e:
            messagebox.showerror("错误", f"加载表列表失败: {e}")
            return []

    def set_current_table(self, table_name):
        """设置当前选中的表"""
        self.current_table = f"{self.schema}.{table_name}"

    def execute_query(self, filter_condition=None, spatial_geom=None, geometry_column=None, convert_wkt=False):
        """执行查询
        
        Args:
            filter_condition: WHERE条件
            spatial_geom: 空间几何对象
            geometry_column: 几何字段名
            convert_wkt: 是否将几何字段转换为WKT格式（用于导出Excel）
        """
        if not self.current_table:
            return False, "请先选择表！"
        if not self.cursor:
            return False, "请先连接数据库！"
        try:
            # 构建查询
            if convert_wkt and geometry_column:
                # 导出Excel时，将几何字段转换为WKT
                query = f"SELECT *, ST_AsText({geometry_column}) as {geometry_column}_wkt FROM {self.current_table}"
            else:
                query = f"SELECT * FROM {self.current_table}"
            
            conditions = []
            if filter_condition:
                conditions.append(filter_condition)
            if spatial_geom and geometry_column:
                # 使用用户选择的几何字段进行空间查询
                conditions.append(f"ST_Intersects({geometry_column}, ST_GeomFromText('{spatial_geom.wkt}'))")
            elif spatial_geom:
                # 如果没有选择几何字段，使用默认的local_geometry字段
                conditions.append(f"ST_Intersects(local_geometry, ST_GeomFromText('{spatial_geom.wkt}'))")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # 执行查询
            self.cursor.execute(query)
            self.query_result = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            return True, {
                'columns': columns,
                'data': self.query_result,
                'row_count': len(self.query_result)
            }
        except Exception as e:
            return False, f"查询失败: {e}"

    def export_to_excel(self, file_path):
        """导出查询结果为Excel文件"""
        if not self.query_result:
            return False, "没有查询结果可导出！"
        
        try:
            columns = [desc[0] for desc in self.cursor.description]
            df = pd.DataFrame(self.query_result, columns=columns)
            df.to_excel(file_path, index=False)
            return True, f"导出成功！\n文件保存到: {file_path}"
        except Exception as e:
            return False, f"导出失败: {e}"

    def load_spatial_file(self, file_path):
        """加载空间文件"""
        try:
            gdf = gpd.read_file(file_path)
            if len(gdf) > 0:
                return True, gdf.geometry.iloc[0], f"已加载: {file_path.split('/')[-1]}"
            else:
                return False, None, "空间文件为空！"
        except Exception as e:
            return False, None, f"加载空间文件失败: {e}"

    def get_table_info(self, table_name):
        """获取表的详细信息"""
        if not self.cursor:
            return None
        
        try:
            # 获取表结构信息
            self.cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            columns = self.cursor.fetchall()
            
            # 获取表行数
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = self.cursor.fetchone()[0]
            
            return {
                'columns': columns,
                'row_count': row_count
            }
        except Exception as e:
            return None

    def get_geometry_columns(self, table_name):
        """获取表中的几何字段列表"""
        if not self.cursor:
            return []
        
        try:
            # 方法1: 查询PostGIS的geometry_columns视图（最可靠）
            self.cursor.execute(f"""
                SELECT f_geometry_column 
                FROM geometry_columns 
                WHERE f_table_name = '{table_name}'
                AND f_table_schema = '{self.schema}';
            """)
            geometry_columns = [row[0] for row in self.cursor.fetchall()]
            if geometry_columns:
                return geometry_columns
            
            # 方法2: 查询geography_columns视图
            try:
                self.cursor.execute(f"""
                    SELECT f_geography_column 
                    FROM geography_columns 
                    WHERE f_table_name = '{table_name}'
                    AND f_table_schema = '{self.schema}';
                """)
                geography_columns = [row[0] for row in self.cursor.fetchall()]
                if geography_columns:
                    return geography_columns
            except:
                pass
            
            # 方法3: 检查所有USER-DEFINED类型的字段
            self.cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns
                WHERE table_name = '{table_name}' 
                AND data_type = 'USER-DEFINED'
                ORDER BY ordinal_position;
            """)
            user_defined_columns = [row[0] for row in self.cursor.fetchall()]
            
            # 对USER-DEFINED字段进行几何类型验证
            geometry_columns = []
            for column in user_defined_columns:
                try:
                    # 尝试检查是否为几何类型
                    self.cursor.execute(f"""
                        SELECT ST_GeometryType({column}) 
                        FROM {self.schema}.{table_name} 
                        WHERE {column} IS NOT NULL 
                        LIMIT 1;
                    """)
                    geom_type = self.cursor.fetchone()
                    if geom_type and geom_type[0]:
                        geometry_columns.append(column)
                except:
                    # 如果ST_GeometryType失败，尝试其他方法
                    try:
                        # 检查字段值是否可以转换为几何类型
                        self.cursor.execute(f"""
                            SELECT {column}::geometry 
                            FROM {self.schema}.{table_name} 
                            WHERE {column} IS NOT NULL 
                            LIMIT 1;
                        """)
                        result = self.cursor.fetchone()
                        if result:
                            geometry_columns.append(column)
                    except:
                        continue
            
            return geometry_columns
        except Exception as e:
            return []

    def execute_custom_sql(self, sql):
        """执行自定义SQL查询"""
        if not self.cursor:
            return False, "请先连接数据库！"
        
        try:
            # 执行自定义SQL
            self.cursor.execute(sql)
            
            # 获取结果
            self.query_result = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            return True, {
                'columns': columns,
                'data': self.query_result,
                'row_count': len(self.query_result)
            }
        except Exception as e:
            return False, f"SQL执行失败: {e}"
