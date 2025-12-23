import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("PyInstaller已安装")
        return True
    except ImportError:
        print("正在安装PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller安装完成")
            return True
        except Exception as e:
            print(f"PyInstaller安装失败: {e}")
            return False

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('connection_dialog.py', '.'), ('database.py', '.'), ('spatial_dialog.py', '.')],
    hiddenimports=['email','tkinter', 'urllib','tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'psycopg2', 'pandas', 'geopandas', 'shapely', 'matplotlib', 'matplotlib.backends.backend_tkagg', 'descartes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    #excludes=['unittest', 'http',  'xml', 'pydoc'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DBQueryTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('build.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("已创建build.spec文件")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 检查main.py是否存在
    if not os.path.exists('main.py'):
        print("错误: main.py文件不存在!")
        return False
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return False
    
    # 创建spec文件
    create_spec_file()
    
    # 使用PyInstaller构建
    try:
        # 使用spec文件构建
        subprocess.run([
            sys.executable, '-m', 'PyInstaller', 
            '--clean',  # 清理之前的构建
            'build.spec'
        ], check=True)
        
        print("构建成功!")
        print("可执行文件位置: dist/DBQueryTool.exe")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    print("数据库查询工具可执行文件构建脚本")
    print("=" * 40)
    
    success = build_executable()
    
    if success:
        print("\n构建完成! 可执行文件位于 dist/DBQueryTool.exe")
    else:
        print("\n构建失败，请检查错误信息")