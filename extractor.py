"""
资源提取模块 - 核心提取逻辑
从Android设备提取应用资源到本地
"""

import os
from adb_manager import ADBManager
from config import EXPORT_DIR, PATHS, EXPORT_SUBDIRS


class ResourceExtractor:
    """资源提取器类"""

    def __init__(self, adb_manager):
        """
        初始化提取器
        :param adb_manager: ADBManager实例
        """
        self.adb = adb_manager
        self.export_dir = EXPORT_DIR

    def extract_package(self, package_name):
        """
        提取指定包名的所有资源
        :param package_name: 应用包名
        :return: (bool, dict) 成功标志和提取结果详情
        """
        print(f"\n开始提取应用资源: {package_name}")
        print("=" * 60)

        # 创建导出目录
        pkg_export_dir = os.path.join(self.export_dir, package_name)
        os.makedirs(pkg_export_dir, exist_ok=True)

        # 提取结果统计
        results = {
            "package": package_name,
            "export_dir": pkg_export_dir,
            "app": {"success": False, "message": ""},
            "data": {"success": False, "message": ""},
            "sdcard_data": {"success": False, "message": ""},
            "obb": {"success": False, "message": ""}
        }

        # 1. 提取APK及lib (需要特殊处理路径)
        print("\n[1/4] 提取APK及lib...")
        results["app"] = self._extract_app_data(package_name, pkg_export_dir)

        # 2. 提取私有数据
        print("\n[2/4] 提取私有数据...")
        results["data"] = self._extract_private_data(package_name, pkg_export_dir)

        # 3. 提取外部存储数据
        print("\n[3/4] 提取外部存储数据...")
        results["sdcard_data"] = self._extract_sdcard_data(package_name, pkg_export_dir)

        # 4. 提取OBB数据包
        print("\n[4/4] 提取OBB数据包...")
        results["obb"] = self._extract_obb(package_name, pkg_export_dir)

        # 统计成功数量
        success_count = sum(1 for v in results.values() if isinstance(v, dict) and v.get("success"))
        total_count = 4

        print("\n" + "=" * 60)
        print(f"提取完成: {success_count}/{total_count} 项成功")
        print(f"导出位置: {pkg_export_dir}")

        return success_count > 0, results

    def _extract_app_data(self, package_name, export_dir):
        """
        提取APK及lib (/data/app/{包名}-xxx/)
        :param package_name: 包名
        :param export_dir: 导出根目录
        :return: dict 提取结果
        """
        # 查找实际路径
        success, app_path = self.adb.find_app_path(package_name)

        if not success:
            return {"success": False, "message": f"未找到应用: {package_name}"}

        # 设置本地保存路径
        local_path = os.path.join(export_dir, EXPORT_SUBDIRS["app"])

        # 拉取文件
        success, message = self.adb.pull(app_path, local_path)

        if success:
            return {"success": True, "message": f"成功: {app_path}"}
        else:
            return {"success": False, "message": message}

    def _extract_private_data(self, package_name, export_dir):
        """
        提取私有数据 (/data/data/{包名}/)
        :param package_name: 包名
        :param export_dir: 导出根目录
        :return: dict 提取结果
        """
        remote_path = PATHS["data"].format(pkg=package_name)
        local_path = os.path.join(export_dir, EXPORT_SUBDIRS["data"])

        # 检查路径是否存在
        if not self.adb.path_exists(remote_path):
            return {"success": False, "message": f"路径不存在: {remote_path}"}

        # 拉取文件
        success, message = self.adb.pull(remote_path, local_path)

        if success:
            return {"success": True, "message": f"成功: {remote_path}"}
        else:
            return {"success": False, "message": message}

    def _extract_sdcard_data(self, package_name, export_dir):
        """
        提取外部存储数据 (/storage/emulated/0/Android/data/{包名}/)
        :param package_name: 包名
        :param export_dir: 导出根目录
        :return: dict 提取结果
        """
        remote_path = PATHS["sdcard_data"].format(pkg=package_name)
        local_path = os.path.join(export_dir, EXPORT_SUBDIRS["sdcard_data"])

        # 检查路径是否存在
        if not self.adb.path_exists(remote_path):
            return {"success": False, "message": f"路径不存在: {remote_path}"}

        # 拉取文件
        success, message = self.adb.pull(remote_path, local_path)

        if success:
            return {"success": True, "message": f"成功: {remote_path}"}
        else:
            return {"success": False, "message": message}

    def _extract_obb(self, package_name, export_dir):
        """
        提取OBB数据包 (/storage/emulated/0/Android/obb/{包名}/)
        :param package_name: 包名
        :param export_dir: 导出根目录
        :return: dict 提取结果
        """
        remote_path = PATHS["obb"].format(pkg=package_name)
        local_path = os.path.join(export_dir, EXPORT_SUBDIRS["obb"])

        # 检查路径是否存在
        if not self.adb.path_exists(remote_path):
            return {"success": False, "message": f"路径不存在: {remote_path}"}

        # 拉取文件
        success, message = self.adb.pull(remote_path, local_path)

        if success:
            return {"success": True, "message": f"成功: {remote_path}"}
        else:
            return {"success": False, "message": message}
