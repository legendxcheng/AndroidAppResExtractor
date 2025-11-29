#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量解包 organized 目录下的所有 ktx2 文件为 png 格式
"""

import os
import subprocess
import sys

def find_ktx2_files(root_dir):
    """递归查找所有 .ktx2 文件"""
    ktx2_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.ktx2'):
                full_path = os.path.join(dirpath, filename)
                ktx2_files.append(full_path)
    return ktx2_files

def extract_ktx2_to_png(ktx2_path):
    """将单个 ktx2 文件解包为 png"""
    # 生成输出路径：将 .ktx2 替换为 .png
    png_path = ktx2_path[:-5] + '.png'

    # 调用 ktx extract 命令
    cmd = ['ktx', 'extract', ktx2_path, png_path]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        # 返回结果
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'output_file': png_path
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'output_file': png_path
        }

def main():
    """主函数"""
    root_dir = 'organized'

    print(f"开始扫描 {root_dir} 目录...")

    # 查找所有 ktx2 文件
    ktx2_files = find_ktx2_files(root_dir)
    total_files = len(ktx2_files)

    print(f"找到 {total_files} 个 .ktx2 文件\n")

    if total_files == 0:
        print("未找到任何 .ktx2 文件")
        return

    # 统计信息
    success_count = 0
    failed_files = []

    # 批量处理
    for idx, ktx2_file in enumerate(ktx2_files, 1):
        print(f"[{idx}/{total_files}] 处理: {ktx2_file}")

        result = extract_ktx2_to_png(ktx2_file)

        if result['success']:
            success_count += 1
            print(f"  ✓ 成功生成: {result['output_file']}")
            # 如果有警告信息，也显示出来
            if result['stderr']:
                print(f"  ⚠ 警告: {result['stderr'][:100]}...")
        else:
            failed_files.append(ktx2_file)
            error_msg = result.get('error') or result.get('stderr', 'Unknown error')
            print(f"  ✗ 失败: {error_msg}")

        print()

    # 输出统计结果
    print("=" * 60)
    print(f"处理完成!")
    print(f"总计: {total_files} 个文件")
    print(f"成功: {success_count} 个")
    print(f"失败: {len(failed_files)} 个")

    if failed_files:
        print("\n失败的文件列表:")
        for f in failed_files:
            print(f"  - {f}")

if __name__ == '__main__':
    main()
