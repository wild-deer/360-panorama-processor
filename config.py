#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - 可以在这里修改默认参数
"""

# 默认处理参数
DEFAULT_CONFIG = {
    # 视场角（度）
    'fov': 90,
    
    # 重叠比例（0-1）
    'overlap': 0.2,
    
    # 输出图片尺寸 (宽度, 高度)
    'output_size': (1024, 1024),
    
    # 默认线程数
    'default_threads': 4,
    
    # 支持的图片格式
    'supported_formats': {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'},
    
    # 输出图片质量（0-100，仅对jpg格式有效）
    'jpeg_quality': 95,
    
    # 是否显示处理进度
    'show_progress': True,
    
    # 是否在处理完成后显示统计信息
    'show_stats': True,
    
    # 输出文件命名格式
    'output_filename_format': '{base_name}_view_{view_index:03d}.jpg',
    
    # 是否创建处理日志
    'create_log': True,
    
    # 日志文件路径
    'log_file': 'processing_log.txt',
    
    # 角度排除设置 - 用于排除拍摄人所在的角度范围
    'exclude_angle_ranges': [],  # 格式: [(start_angle1, end_angle1), (start_angle2, end_angle2), ...]
    
    # 是否启用角度排除功能
    'enable_angle_exclusion': False
}

# 性能优化建议配置
PERFORMANCE_CONFIGS = {
    'fast': {
        'fov': 90,
        'overlap': 0.1,
        'output_size': (512, 512),
        'jpeg_quality': 85,
        'exclude_angle_ranges': [(150, 210)],  # 排除拍摄人后方180度范围
        'enable_angle_exclusion': True
    },
    'balanced': {
        'fov': 90,
        'overlap': 0.2,
        'output_size': (1024, 1024),
        'jpeg_quality': 95,
        'exclude_angle_ranges': [(150, 210)],  # 排除拍摄人后方180度范围
        'enable_angle_exclusion': True
    },
    'high_quality': {
        'fov': 60,
        'overlap': 0.3,
        'output_size': (2048, 2048),
        'jpeg_quality': 100,
        'exclude_angle_ranges': [(150, 210)],  # 排除拍摄人后方180度范围
        'enable_angle_exclusion': True
    }
}

# 线程数建议（根据CPU核心数）
THREAD_RECOMMENDATIONS = {
    2: [2, 3],
    4: [4, 6],
    8: [6, 8],
    16: [8, 12],
    32: [12, 16]
}

def get_recommended_threads():
    """获取推荐的线程数"""
    import os
    try:
        # 获取CPU核心数
        cpu_count = os.cpu_count()
        if cpu_count is None:
            return DEFAULT_CONFIG['default_threads']
        
        # 根据核心数推荐线程数
        for cores, thread_range in sorted(THREAD_RECOMMENDATIONS.items()):
            if cpu_count <= cores:
                return thread_range[0]  # 返回推荐范围的最小值
        
        # 如果核心数超过32，使用16个线程
        return 16
        
    except:
        return DEFAULT_CONFIG['default_threads']

def get_performance_config(profile='balanced'):
    """获取性能配置"""
    if profile in PERFORMANCE_CONFIGS:
        return PERFORMANCE_CONFIGS[profile]
    else:
        return PERFORMANCE_CONFIGS['balanced']


def validate_angle_ranges(angle_ranges):
    """
    验证角度范围的有效性
    angle_ranges: 角度范围列表，格式: [(start1, end1), (start2, end2), ...]
    返回: (是否有效, 错误信息)
    """
    if not angle_ranges:
        return True, ""
    
    for i, (start, end) in enumerate(angle_ranges):
        # 检查角度值是否在有效范围内
        if not (0 <= start <= 360 and 0 <= end <= 360):
            return False, f"角度范围 {i+1}: 角度值必须在0-360度之间"
        
        # 检查起始角度是否小于结束角度
        if start >= end:
            return False, f"角度范围 {i+1}: 起始角度必须小于结束角度"
    
    return True, ""


def normalize_angle(angle):
    """将角度标准化到0-360度范围"""
    return angle % 360


def is_angle_excluded(angle, exclude_ranges):
    """
    检查指定角度是否在排除范围内
    angle: 要检查的角度（度）
    exclude_ranges: 排除角度范围列表
    返回: 是否应该排除
    """
    if not exclude_ranges:
        return False
    
    normalized_angle = normalize_angle(angle)
    
    for start, end in exclude_ranges:
        # 处理跨越0度的情况
        if start > end:  # 例如 (350, 10)
            if normalized_angle >= start or normalized_angle <= end:
                return True
        else:  # 正常情况，例如 (150, 210)
            if start <= normalized_angle <= end:
                return True
    
    return False


def print_config_info():
    """打印配置信息"""
    print("=== 当前配置信息 ===")
    print(f"默认视场角: {DEFAULT_CONFIG['fov']}°")
    print(f"默认重叠比例: {DEFAULT_CONFIG['overlap']*100:.1f}%")
    print(f"默认输出尺寸: {DEFAULT_CONFIG['output_size'][0]}x{DEFAULT_CONFIG['output_size'][1]}")
    print(f"默认线程数: {DEFAULT_CONFIG['default_threads']}")
    print(f"推荐线程数: {get_recommended_threads()}")
    print(f"支持的图片格式: {', '.join(DEFAULT_CONFIG['supported_formats'])}")
    print(f"角度排除功能: {'启用' if DEFAULT_CONFIG['enable_angle_exclusion'] else '禁用'}")
    if DEFAULT_CONFIG['exclude_angle_ranges']:
        print(f"排除角度范围: {DEFAULT_CONFIG['exclude_angle_ranges']}")
    print("\n性能配置选项:")
    for profile, config in PERFORMANCE_CONFIGS.items():
        print(f"  {profile}: FOV={config['fov']}°, 重叠={config['overlap']*100:.1f}%, 尺寸={config['output_size'][0]}x{config['output_size'][1]}")
        if config.get('enable_angle_exclusion'):
            print(f"    排除角度: {config.get('exclude_angle_ranges', [])}")
    print("=" * 30)

if __name__ == "__main__":
    print_config_info()
