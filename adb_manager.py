"""
ADB管理模块 - 封装ADB操作
提供设备连接、命令执行、文件拉取等功能
"""

import subprocess
import os
from config import ADB_PATH, DEVICE_ADDRESS


class ADBManager:
    """ADB管理器类"""

    def __init__(self):
        self.adb_path = ADB_PATH
        self.device_address = DEVICE_ADDRESS
        self._connected = False

    def connect(self):
        """
        连接ADB设备
        :return: (bool, str) 成功标志和消息
        """
        try:
            # 执行连接命令
            result = self._run_adb_command(["connect", self.device_address])

            # 检查连接结果
            if "connected" in result.lower() or "already connected" in result.lower():
                self._connected = True
                return True, f"连接成功: {self.device_address}"
            else:
                return False, f"连接失败: {result}"
        except Exception as e:
            return False, f"连接异常: {str(e)}"

    def disconnect(self):
        """
        断开ADB连接
        :return: (bool, str) 成功标志和消息
        """
        try:
            result = self._run_adb_command(["disconnect", self.device_address])
            self._connected = False
            return True, f"已断开连接: {result}"
        except Exception as e:
            return False, f"断开连接异常: {str(e)}"

    def is_connected(self):
        """
        检查设备连接状态
        :return: bool 是否已连接
        """
        try:
            result = self._run_adb_command(["devices"])
            # 检查设备列表中是否包含当前设备
            return self.device_address in result and "device" in result
        except:
            return False

    def run_command(self, cmd):
        """
        在设备上执行shell命令
        :param cmd: shell命令字符串或列表
        :return: (bool, str) 成功标志和命令输出
        """
        try:
            if isinstance(cmd, str):
                # 对于访问受保护路径的命令，使用su提权
                if any(path in cmd for path in ['/data/app/', '/data/data/', '/data/user/']):
                    # 整个su命令作为一个shell参数
                    full_cmd = f"su -c '{cmd}'"
                    shell_cmd = ["shell", full_cmd]
                else:
                    shell_cmd = ["shell", cmd]
            else:
                shell_cmd = ["shell"] + cmd

            result = self._run_adb_command(shell_cmd)
            return True, result
        except Exception as e:
            return False, f"命令执行失败: {str(e)}"

    def pull(self, remote_path, local_path):
        """
        从设备拉取文件或目录
        :param remote_path: 设备上的路径
        :param local_path: 本地保存路径
        :return: (bool, str) 成功标志和消息
        """
        try:
            # 确保本地目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # 检查是否是受保护路径（需要root权限）
            is_protected = any(p in remote_path for p in ['/data/app/', '/data/data/', '/data/user/'])

            if is_protected:
                # 使用临时目录中转
                import time
                temp_name = f"adb_temp_{int(time.time())}"
                temp_path = f"/sdcard/{temp_name}"

                # 1. 用su复制到临时目录
                self.run_command(f"rm -rf {temp_path}")  # 清理可能存在的旧文件
                self.run_command(f"cp -r {remote_path} {temp_path}")

                # 2. 拉取临时目录
                result = self._run_adb_command(["pull", temp_path, local_path])

                # 3. 清理临时文件
                self.run_command(f"rm -rf {temp_path}")

                # 检查结果
                if "pulled" in result.lower() or "file pulled" in result.lower():
                    return True, f"拉取成功: {remote_path} -> {local_path}"
                else:
                    return False, f"拉取失败: {result}"
            else:
                # 直接拉取
                result = self._run_adb_command(["pull", remote_path, local_path])

                # 检查是否成功
                if "pulled" in result.lower() or "file pulled" in result.lower():
                    return True, f"拉取成功: {remote_path} -> {local_path}"
                elif "does not exist" in result.lower() or "no such file" in result.lower():
                    return False, f"路径不存在: {remote_path}"
                else:
                    return False, f"拉取失败: {result}"
        except Exception as e:
            return False, f"拉取异常: {str(e)}"

    def find_app_path(self, package_name):
        """
        查找应用在 /data/app/ 中的实际路径
        支持 Android 11+ 新格式: /data/app/~~xxx==/{包名}-xxx==/
        以及旧格式: /data/app/{包名}-xxx/
        :param package_name: 应用包名
        :return: (bool, str) 成功标志和实际路径
        """
        try:
            # 构造find命令
            cmd_str = f'find /data/app/ -maxdepth 2 -type d -name "{package_name}*" 2>/dev/null'
            # 整个su命令作为一个shell参数
            full_cmd = f"su -c '{cmd_str}'"
            shell_cmd = ["shell", full_cmd]

            result = self._run_adb_command(shell_cmd)

            if result.strip():
                # 取第一个匹配的路径
                paths = result.strip().split('\n')
                actual_path = paths[0].strip()
                return True, actual_path
            else:
                return False, f"未找到应用: {package_name}"
        except Exception as e:
            return False, f"查找路径异常: {str(e)}"

    def path_exists(self, remote_path):
        """
        检查设备上的路径是否存在
        :param remote_path: 设备路径
        :return: bool 是否存在
        """
        try:
            # 根据路径类型选择命令
            if any(p in remote_path for p in ['/data/app/', '/data/data/', '/data/user/']):
                # 受保护路径，使用su
                cmd_str = f'ls {remote_path} 2>/dev/null'
                full_cmd = f"su -c '{cmd_str}'"
                result = self._run_adb_command(["shell", full_cmd])
            else:
                # 普通路径
                result = self._run_adb_command(["shell", f"ls {remote_path} 2>/dev/null"])

            return result.strip() != ""
        except:
            return False

    def _run_adb_command(self, args):
        """
        执行ADB命令的内部方法
        :param args: 命令参数列表
        :return: str 命令输出
        """
        # 需要指定设备的命令（除了 connect/disconnect/devices）
        needs_device = args and args[0] not in ['connect', 'disconnect', 'devices']

        # 构建命令：adb [-s 设备] 命令
        if needs_device and self._connected:
            cmd = [self.adb_path, '-s', self.device_address] + args
        else:
            cmd = [self.adb_path] + args

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        # 返回标准输出或标准错误
        output = result.stdout if result.stdout else result.stderr
        return output.strip()
