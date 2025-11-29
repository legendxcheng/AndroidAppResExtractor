"""
Android应用资源提取器 - 主程序
通过ADB从Android设备提取应用资源文件
"""

import sys
from adb_manager import ADBManager
from extractor import ResourceExtractor


def print_banner():
    """打印程序横幅"""
    print("\n" + "=" * 60)
    print(" Android应用资源提取器 v1.0")
    print(" Android App Resource Extractor")
    print("=" * 60)


def print_results(results):
    """
    打印提取结果详情
    :param results: 提取结果字典
    """
    print("\n详细结果:")
    print("-" * 60)

    items = [
        ("APK及lib", "app"),
        ("私有数据", "data"),
        ("外部存储", "sdcard_data"),
        ("OBB数据包", "obb")
    ]

    for name, key in items:
        result = results[key]
        status = "✓ 成功" if result["success"] else "✗ 失败"
        print(f"{name:12s} {status:8s} | {result['message']}")


def main():
    """主程序入口"""
    print_banner()

    # 初始化ADB管理器
    adb = ADBManager()

    # 连接设备
    print("\n正在连接ADB设备...")
    success, message = adb.connect()
    print(message)

    if not success:
        print("\n错误: 无法连接到设备，请检查:")
        print("  1. MuMu模拟器是否已启动")
        print("  2. ADB路径是否正确 (当前: ./adb.exe)")
        print("  3. 设备地址是否正确 (当前: 127.0.0.1:7555)")
        sys.exit(1)

    # 验证连接状态
    if not adb.is_connected():
        print("警告: 设备连接状态异常")
        sys.exit(1)

    print("设备连接成功！\n")

    # 创建资源提取器
    extractor = ResourceExtractor(adb)

    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 命令行模式：直接提取指定包名
        package_name = sys.argv[1]
        print(f"命令行模式: 提取包 {package_name}\n")

        try:
            success, results = extractor.extract_package(package_name)
            print_results(results)

            if success:
                print(f"\n导出目录: {results['export_dir']}")
            else:
                print("\n警告: 所有提取操作均失败，请检查包名是否正确")
        except Exception as e:
            print(f"\n错误: {str(e)}")

        adb.disconnect()
        return

    # 交互模式：循环输入
    while True:
        print("\n" + "-" * 60)
        package_name = input("请输入应用包名 (输入 'q' 退出): ").strip()

        if package_name.lower() == 'q':
            print("\n感谢使用，再见！")
            adb.disconnect()
            break

        if not package_name:
            print("错误: 包名不能为空")
            continue

        # 执行提取
        try:
            success, results = extractor.extract_package(package_name)

            # 显示详细结果
            print_results(results)

            if success:
                print(f"\n导出目录: {results['export_dir']}")
            else:
                print("\n警告: 所有提取操作均失败，请检查包名是否正确")

        except KeyboardInterrupt:
            print("\n\n操作已取消")
            continue
        except Exception as e:
            print(f"\n错误: {str(e)}")
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
        sys.exit(0)
