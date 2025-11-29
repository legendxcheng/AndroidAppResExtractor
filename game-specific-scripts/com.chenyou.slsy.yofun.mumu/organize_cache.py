#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存文件组织脚本
根据cacheList.json中的URL映射，将缓存文件复制到organized目录下的相对路径中
"""

import json
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse, unquote

def extract_relative_path(url):
    """
    从URL中提取相对路径

    示例:
    输入: https://cdn.lth5.zeda6.com/zhengba3_res/anim/player/player_9999_0_0.plist?version=xxx
    输出: anim/player/player_9999_0_0.plist
    """
    # 解析URL
    parsed = urlparse(url)

    # 获取路径部分（移除查询参数）
    path = unquote(parsed.path)

    # 移除基础路径 "/zhengba3_res/"
    if path.startswith('/zhengba3_res/'):
        path = path[len('/zhengba3_res/'):]
    elif path.startswith('zhengba3_res/'):
        path = path[len('zhengba3_res/'):]

    return path

def organize_cache_files(cache_list_path, output_dir):
    """
    组织缓存文件

    Args:
        cache_list_path: cacheList.json文件路径
        output_dir: 输出目录（organized）
    """
    # 统计信息
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'missing': 0,
        'errors': []
    }

    # 读取cacheList.json
    try:
        with open(cache_list_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
    except Exception as e:
        print(f"错误: 无法读取 {cache_list_path}: {e}")
        return stats

    files_mapping = cache_data.get('files', {})
    stats['total'] = len(files_mapping)

    print(f"开始处理 {stats['total']} 个文件...")
    print("-" * 60)

    # 遍历所有文件映射
    for url, file_info in files_mapping.items():
        local_filename = file_info.get('url')

        if not local_filename:
            stats['failed'] += 1
            stats['errors'].append(f"URL无本地文件映射: {url}")
            continue

        # 提取相对路径
        try:
            relative_path = extract_relative_path(url)
        except Exception as e:
            stats['failed'] += 1
            stats['errors'].append(f"URL解析失败 {url}: {e}")
            continue

        # 源文件路径
        source_file = Path(local_filename)

        # 检查源文件是否存在
        if not source_file.exists():
            stats['missing'] += 1
            stats['errors'].append(f"源文件不存在: {local_filename}")
            continue

        # 目标文件路径
        target_file = Path(output_dir) / relative_path

        # 创建目标目录
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            stats['failed'] += 1
            stats['errors'].append(f"创建目录失败 {target_file.parent}: {e}")
            continue

        # 复制文件
        try:
            shutil.copy2(source_file, target_file)
            stats['success'] += 1
            print(f"✓ {local_filename} -> {relative_path}")
        except Exception as e:
            stats['failed'] += 1
            stats['errors'].append(f"复制文件失败 {local_filename} -> {target_file}: {e}")
            print(f"✗ {local_filename} -> {relative_path} (失败)")

    return stats

def print_summary(stats):
    """打印统计摘要"""
    print("\n" + "=" * 60)
    print("处理完成!")
    print("=" * 60)
    print(f"总文件数:   {stats['total']}")
    print(f"成功复制:   {stats['success']}")
    print(f"源文件缺失: {stats['missing']}")
    print(f"失败:       {stats['failed']}")

    if stats['errors']:
        print("\n错误详情:")
        print("-" * 60)
        for error in stats['errors'][:10]:  # 只显示前10个错误
            print(f"  - {error}")
        if len(stats['errors']) > 10:
            print(f"  ... 还有 {len(stats['errors']) - 10} 个错误")

def main():
    """主函数"""
    script_dir = Path(__file__).parent
    cache_list_path = script_dir / 'cacheList.json'
    output_dir = script_dir / 'organized'

    print("缓存文件组织脚本")
    print("=" * 60)
    print(f"配置文件: {cache_list_path}")
    print(f"输出目录: {output_dir}")
    print("=" * 60)
    print()

    # 执行组织
    stats = organize_cache_files(cache_list_path, output_dir)

    # 打印摘要
    print_summary(stats)

if __name__ == '__main__':
    main()
