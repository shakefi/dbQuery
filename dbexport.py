# -*- coding: utf-8 -*-
"""
Database Export Module - Fixed Version
Handles data export to Excel, Shapefile, GeoJSON formats
"""

import pandas as pd
import geopandas as gpd
from shapely import wkt


class DataExporter:
    """Data exporter class for various formats"""
    
    def __init__(self, db_manager, get_query_input, get_geom_field, get_spatial_geom):
        """
        Initialize exporter
        
        Args:
            db_manager: Database manager instance
            get_query_input: Function to get query input
            get_geom_field: Function to get geometry field
            get_spatial_geom: Function to get spatial geometry
        """
        self.db_manager = db_manager
        self.get_query_input = get_query_input
        self.get_geom_field = get_geom_field
        self.get_spatial_geom = get_spatial_geom
    
    def export_to_excel(self, query_result, status_bar_callback=None):
        """Export to Excel, convert geometry field to WKT format"""
        if not query_result:
            return False, "No query results to export!"
        
        # Get current geometry field
        geom_field = self.get_geom_field()
        if not geom_field:
            return False, "Please select geometry field first!"
        
        # Get current table info
        current_table = self.db_manager.current_table
        if not current_table:
            return False, "Please select table first!"
        
        try:
            # Re-execute query with WKT conversion
            query_content = self.get_query_input()
            geom_field = self.get_geom_field()
            
            # Execute query with WKT conversion
            success, result = self.db_manager.execute_query(
                filter_condition=query_content if query_content else None,
                spatial_geom=self.get_spatial_geom(),
                geometry_column=geom_field,
                convert_wkt=True  # Enable WKT conversion
            )
            
            if not success:
                return False, result
            
            # Get new query result (with WKT field)
            columns = result['columns']
            data = result['data']
            
            # Find WKT column name
            wkt_column_name = f"{geom_field}_wkt"
            if wkt_column_name not in columns:
                return False, f"WKT conversion result column not found: {wkt_column_name}"
            
            # Simplified export logic: create DataFrame, replace geometry column with WKT
            df = pd.DataFrame(data, columns=columns)
            
            # Replace geometry column with WKT values
            df[geom_field] = df[wkt_column_name]
            
            # Drop WKT column
            df.drop(columns=[wkt_column_name], inplace=True)
            
            if status_bar_callback:
                status_bar_callback(text=f"Exporting Excel, {len(data)} records...")
            
            return True, df
            
        except Exception as e:
            return False, f"Export failed: {e}"
    
    def export_to_shapefile(self, query_result, status_bar_callback=None):
        """Export to Shapefile format"""
        if not query_result:
            return False, "No query results to export!"
        
        # Get current geometry field
        geom_field = self.get_geom_field()
        if not geom_field:
            return False, "Please select geometry field first!"
        
        # Get current table info
        current_table = self.db_manager.current_table
        if not current_table:
            return False, "Please select table first!"
        
        try:
            # Re-execute query with WKT conversion
            query_content = self.get_query_input()
            geom_field = self.get_geom_field()
            
            # Execute query with WKT conversion
            success, result = self.db_manager.execute_query(
                filter_condition=query_content if query_content else None,
                spatial_geom=self.get_spatial_geom(),
                geometry_column=geom_field,
                convert_wkt=True  # Enable WKT conversion
            )
            
            if not success:
                return False, result
            
            # Get new query result (with WKT field)
            columns = result['columns']
            data = result['data']
            
            # Find WKT column name
            wkt_column_name = f"{geom_field}_wkt"
            if wkt_column_name not in columns:
                return False, f"WKT conversion result column not found: {wkt_column_name}"
            
            if status_bar_callback:
                status_bar_callback(text="Preparing Shapefile data...")
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # Convert WKT strings to geometry objects
            geometries = []
            for wkt_value in df[wkt_column_name]:
                if wkt_value:
                    try:
                        geometry = wkt.loads(wkt_value)
                        geometries.append(geometry)
                    except Exception as e:
                        print(f"WKT parsing error: {e}, WKT value: {wkt_value}")
                        geometries.append(None)
                else:
                    geometries.append(None)
            
            # Drop WKT and original geometry columns, keep other columns
            drop_columns = [wkt_column_name, geom_field]
            existing_drop_columns = [col for col in drop_columns if col in df.columns]
            if existing_drop_columns:
                df.drop(columns=existing_drop_columns, inplace=True)
            
            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame(df, geometry=geometries)
            
            return True, gdf
            
        except Exception as e:
            return False, f"Shapefile export failed: {e}"
    
    def export_to_geojson(self, query_result, status_bar_callback=None):
        """Export to GeoJSON format"""
        if not query_result:
            return False, "No query results to export!"
        
        # Get current geometry field
        geom_field = self.get_geom_field()
        if not geom_field:
            return False, "Please select geometry field first!"
        
        # Get current table info
        current_table = self.db_manager.current_table
        if not current_table:
            return False, "Please select table first!"
        
        try:
            # Re-execute query with WKT conversion
            query_content = self.get_query_input()
            geom_field = self.get_geom_field()
            
            # Execute query with WKT conversion
            success, result = self.db_manager.execute_query(
                filter_condition=query_content if query_content else None,
                spatial_geom=self.get_spatial_geom(),
                geometry_column=geom_field,
                convert_wkt=True  # Enable WKT conversion
            )
            
            if not success:
                return False, result
            
            # Get new query result (with WKT field)
            columns = result['columns']
            data = result['data']
            
            # Find WKT column name
            wkt_column_name = f"{geom_field}_wkt"
            if wkt_column_name not in columns:
                return False, f"WKT conversion result column not found: {wkt_column_name}"
            
            if status_bar_callback:
                status_bar_callback(text="Preparing GeoJSON data...")
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # Convert WKT strings to geometry objects
            geometries = []
            for wkt_value in df[wkt_column_name]:
                if wkt_value:
                    try:
                        geometry = wkt.loads(wkt_value)
                        geometries.append(geometry)
                    except Exception as e:
                        print(f"WKT parsing error: {e}, WKT value: {wkt_value}")
                        geometries.append(None)
                else:
                    geometries.append(None)
            
            # Drop WKT and original geometry columns, keep other columns
            drop_columns = [wkt_column_name, geom_field]
            existing_drop_columns = [col for col in drop_columns if col in df.columns]
            if existing_drop_columns:
                df.drop(columns=existing_drop_columns, inplace=True)
            
            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame(df, geometry=geometries)
            
            # Ensure geometry column name is correct
            gdf.rename_geometry(geom_field, inplace=True)
            
            return True, gdf
            
        except Exception as e:
            print(f"GeoJSON export error: {e}")
            return False, f"GeoJSON export failed: {e}"
    
    def export_data(self, export_type, query_result, file_path, status_bar_callback=None):
        """
        General export function
        
        Args:
            export_type: Export type ('excel', 'shapefile', 'geojson')
            query_result: Query result data
            file_path: Save file path
            status_bar_callback: Status bar update callback
        
        Returns:
            tuple: (success, message)
        """
        if export_type == 'excel':
            success, result = self.export_to_excel(query_result, status_bar_callback)
            if success:
                try:
                    result.to_excel(file_path, index=False)
                    return True, f"Excel export successful!\nFile saved to: {file_path}\nExported {len(result)} records"
                except Exception as e:
                    return False, f"Excel file save failed: {e}"
            else:
                return False, result
        
        elif export_type == 'shapefile':
            success, result = self.export_to_shapefile(query_result, status_bar_callback)
            if success:
                try:
                    result.to_file(file_path, encoding='utf-8')
                    return True, f"Shapefile export successful!\nFile saved to: {file_path}\nExported {len(result)} records"
                except Exception as e:
                    return False, f"Shapefile file save failed: {e}"
            else:
                return False, result
        
        elif export_type == 'geojson':
            success, result = self.export_to_geojson(query_result, status_bar_callback)
            if success:
                try:
                    result.to_file(file_path, driver='GeoJSON', encoding='utf-8')
                    return True, f"GeoJSON export successful!\nFile saved to: {file_path}\nExported {len(result)} records"
                except Exception as e:
                    return False, f"GeoJSON file save failed: {e}"
            else:
                return False, result
        
        else:
            return False, f"Unsupported export type: {export_type}"
