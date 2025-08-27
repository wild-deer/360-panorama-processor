#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 提供简单的用户界面来启动批量处理
"""

import os
import sys
from pathlib import Path
from batch_process import batch_process_images
from config import DEFAULT_CONFIG, get_recommended_threads, get_performance_config

def get_user_input():
    """获取用户输入"""
    print("=== 全景图片批量处理 - 快速启动 ===\n")
    
    # 获取输入文件夹
    while True:
        input_folder = input("请输入全景图片文件夹路径 (或按回车使用当前目录): ").strip()
        if not input_folder:
            input_folder = "."
        
        if os.path.exists(input_folder):
            break
        else:
            print(f"错误：文件夹 '{input_folder}' 不存在，请重新输入")
    
    # 获取输出文件夹
    while True:
        output_folder = input("请输入输出文件夹路径 (或按回车使用 'batch_output'): ").strip()
        if not output_folder:
            output_folder = "batch_output"
        
        # 检查输出文件夹是否可写
        try:
            os.makedirs(output_folder, exist_ok=True)
            break
        except:
            print(f"错误：无法创建输出文件夹 '{output_folder}'，请重新输入")
    
    # 选择性能配置
    print("\n请选择性能配置:")
    print("1. 快速模式 (512x512, 低质量)")
    print("2. 平衡模式 (1024x1024, 标准质量) [推荐]")
    print("3. 高质量模式 (2048x2048, 高质量)")
    
    while True:
        try:
            choice = input("请选择 (1-3，默认2): ").strip()
            if not choice:
                choice = "2"
            
            if choice in ["1", "2", "3"]:
                profiles = ["fast", "balanced", "high_quality"]
                profile = profiles[int(choice) - 1]
                break
            else:
                print("请输入 1、2 或 3")
        except:
            print("输入无效，请重新输入")
    
    # 询问是否启用角度排除功能
    print("\n角度排除功能 - 用于排除拍摄人所在的角度范围:")
    print("通常拍摄人站在图片后方（约180度位置），可以排除该区域")
    
    while True:
        enable_exclusion = input("是否启用角度排除功能？(y/n，默认y): ").strip().lower()
        if not enable_exclusion:
            enable_exclusion = "y"
        
        if enable_exclusion in ["y", "yes"]:
            enable_exclusion = True
            break
        elif enable_exclusion in ["n", "no"]:
            enable_exclusion = False
            break
        else:
            print("请输入 y 或 n")
    
    # 如果启用角度排除，获取排除范围
    exclude_angle_ranges = []
    if enable_exclusion:
        print("\n请设置要排除的角度范围:")
        print("角度说明: 0度=前方，90度=右方，180度=后方，270度=左方")
        print("建议排除范围: 150-210度（拍摄人后方区域）")
        
        while True:
            try:
                start_angle = input("请输入起始角度 (0-360，默认150): ").strip()
                if not start_angle:
                    start_angle = 150
                else:
                    start_angle = float(start_angle)
                
                if 0 <= start_angle <= 360:
                    break
                else:
                    print("角度必须在0-360度之间")
            except ValueError:
                print("请输入有效的数字")
        
        while True:
            try:
                end_angle = input("请输入结束角度 (0-360，默认210): ").strip()
                if not end_angle:
                    end_angle = 210
                else:
                    end_angle = float(end_angle)
                
                if 0 <= end_angle <= 360:
                    if end_angle > start_angle:
                        break
                    else:
                        print("结束角度必须大于起始角度")
                else:
                    print("角度必须在0-360度之间")
            except ValueError:
                print("请输入有效的数字")
        
        exclude_angle_ranges = [(start_angle, end_angle)]
        
        # 询问是否添加更多排除范围
        while True:
            add_more = input("是否添加更多排除范围？(y/n，默认n): ").strip().lower()
            if not add_more:
                add_more = "n"
            
            if add_more in ["n", "no"]:
                break
            elif add_more in ["y", "yes"]:
                # 这里可以扩展为添加多个范围，暂时只支持一个
                print("当前版本暂只支持一个排除范围，将在后续版本中支持多个范围")
                break
            else:
                print("请输入 y 或 n")
    
    # 获取俯仰角度
    print("\n俯仰角度设置 - 用于调整视角的上下方向:")
    print("正值向上看，负值向下看，0度为水平视角")
    while True:
        try:
            pitch_input = input("请输入俯仰角度 (-90到90度，默认0): ").strip()
            if not pitch_input:
                pitch_angle = 0
            else:
                pitch_angle = float(pitch_input)
            
            if -90 <= pitch_angle <= 90:
                break
            else:
                print("俯仰角度必须在-90到90度之间")
        except ValueError:
            print("请输入有效的数字")
    
    # 询问是否启用垂直翻转功能
    print("\n垂直翻转功能 - 用于处理倒置拍摄的全景图:")
    print("如果全景图是倒置拍摄的，启用此功能可以自动翻转")
    
    while True:
        flip_vertical = input("是否启用垂直翻转功能？(y/n，默认n): ").strip().lower()
        if not flip_vertical:
            flip_vertical = "n"
        
        if flip_vertical in ["y", "yes"]:
            flip_vertical = True
            break
        elif flip_vertical in ["n", "no"]:
            flip_vertical = False
            break
        else:
            print("请输入 y 或 n")
    
    # 获取线程数
    recommended = get_recommended_threads()
    while True:
        try:
            threads_input = input(f"请输入线程数 (推荐: {recommended}, 默认: {recommended}): ").strip()
            if not threads_input:
                threads = recommended
            else:
                threads = int(threads_input)
            
            if threads > 0:
                break
            else:
                print("线程数必须大于0")
        except ValueError:
            print("请输入有效的数字")
    
    return input_folder, output_folder, profile, threads, exclude_angle_ranges, enable_exclusion, pitch_angle, flip_vertical

def main():
    """主函数"""
    try:
        # 获取用户输入
        input_folder, output_folder, profile, threads, exclude_angle_ranges, enable_exclusion, pitch_angle, flip_vertical = get_user_input()
        
        # 获取性能配置
        perf_config = get_performance_config(profile)
        
        print(f"\n=== 处理参数 ===")
        print(f"输入文件夹: {input_folder}")
        print(f"输出文件夹: {output_folder}")
        print(f"性能模式: {profile}")
        print(f"视场角: {perf_config['fov']}°")
        print(f"重叠比例: {perf_config['overlap']*100:.1f}%")
        print(f"输出尺寸: {perf_config['output_size'][0]}x{perf_config['output_size'][1]}")
        print(f"线程数: {threads}")
        print(f"俯仰角度: {pitch_angle}°")
        if flip_vertical:
            print(f"垂直翻转: 启用")
        else:
            print(f"垂直翻转: 禁用")
        if enable_exclusion and exclude_angle_ranges:
            print(f"角度排除: 启用，排除范围: {exclude_angle_ranges}")
        else:
            print(f"角度排除: 禁用")
        print("=" * 30)
        
        # 确认开始处理
        confirm = input("\n确认开始处理？(y/n，默认y): ").strip().lower()
        if confirm in ['n', 'no']:
            print("已取消处理")
            return
        
        print("\n开始批量处理...")
        
        # 调用批量处理函数
        batch_process_images(
            input_folder=input_folder,
            output_base_dir=output_folder,
            fov=perf_config['fov'],
            overlap=perf_config['overlap'],
            out_size=perf_config['output_size'],
            max_workers=threads,
            exclude_angle_ranges=exclude_angle_ranges,
            enable_angle_exclusion=enable_exclusion,
            pitch_angle=pitch_angle,
            flip_vertical=flip_vertical
        )
        
        print(f"\n处理完成！结果保存在: {output_folder}")
        
    except KeyboardInterrupt:
        print("\n\n用户中断了程序")
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
