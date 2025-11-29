"""
配置文件 - Android资源提取器
定义ADB路径、连接参数、提取路径常量
"""

import os

# ADB配置
ADB_PATH = os.path.join(os.path.dirname(__file__), "adb.exe")
DEVICE_ADDRESS = "127.0.0.1:7555"

# 导出目录
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "export")

# Android资源路径模板
# {pkg} 将被替换为实际包名
PATHS = {
    "app": "/data/app/{pkg}*/",
    "data": "/data/data/{pkg}/",
    "sdcard_data": "/storage/emulated/0/Android/data/{pkg}/",
    "obb": "/storage/emulated/0/Android/obb/{pkg}/"
}

# 导出子目录名称
EXPORT_SUBDIRS = {
    "app": "app",
    "data": "data",
    "sdcard_data": "sdcard_data",
    "obb": "obb"
}
