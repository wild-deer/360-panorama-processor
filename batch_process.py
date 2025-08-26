import cv2
import numpy as np
import math
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from pathlib import Path
import argparse

def equirectangular_to_perspective(img, fov, theta, phi, out_size, flip_vertical=False):
    """
    从 equirectangular 全景图生成一个透视图
    img: 输入 equirectangular (H×W×3)，比例 2:1
    fov: 视场角（度）
    theta: 水平方向旋转角度（度，0=前方，正数向右）
    phi: 垂直方向旋转角度（度，0=水平，正数向上）
    out_size: 输出图像大小 (w,h)
    flip_vertical: 是否垂直翻转图像（用于处理倒置拍摄的全景图）
    """
    h, w = img.shape[:2]
    
    # 如果需要进行垂直翻转，先翻转输入图像
    if flip_vertical:
        img = cv2.flip(img, 0)  # 0表示垂直翻转
    
    fov_rad = math.radians(fov)
    w_out, h_out = out_size

    # 构建透视相机坐标
    x = np.linspace(-math.tan(fov_rad/2), math.tan(fov_rad/2), w_out)
    y = np.linspace(-math.tan(fov_rad/2), math.tan(fov_rad/2), h_out)
    x, y = np.meshgrid(x, -y)  # 注意 y 反向

    z = np.ones_like(x)
    xyz = np.stack([x, y, z], axis=-1)
    xyz = xyz / np.linalg.norm(xyz, axis=-1, keepdims=True)

    # 旋转矩阵（先绕 Y=theta，再绕 X=phi）
    def rot_matrix(axis, angle):
        a = math.radians(angle)
        if axis == 'y':
            return np.array([[ math.cos(a), 0, math.sin(a)],
                             [0, 1, 0],
                             [-math.sin(a), 0, math.cos(a)]])
        if axis == 'x':
            return np.array([[1, 0, 0],
                             [0, math.cos(a), -math.sin(a)],
                             [0, math.sin(a), math.cos(a)]])
    R = rot_matrix('y', theta) @ rot_matrix('x', phi)

    xyz = xyz @ R.T

    # 转换到经纬度
    lon = np.arctan2(xyz[...,0], xyz[...,2])
    lat = np.arcsin(np.clip(xyz[...,1], -1, 1))

    # 映射到图像坐标
    u = (lon / math.pi + 1) * 0.5 * w
    v = (0.5 - lat / math.pi) * h

    map_x = u.astype(np.float32)
    map_y = v.astype(np.float32)

    persp = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LANCZOS4,
                      borderMode=cv2.BORDER_WRAP)
    return persp


def generate_views_for_image(input_path, output_dir, fov=90, overlap=0.2, out_size=(1024,1024), 
                            exclude_angle_ranges=None, enable_angle_exclusion=False, pitch_angle=0, flip_vertical=False):
    """
    为单张图片生成多个透视图
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        img = cv2.imread(input_path)
        
        if img is None:
            print(f"错误：无法读取图片 {input_path}")
            return False
            
        h, w = img.shape[:2]

        # 计算步进角度（比如 fov=90, overlap=0.2 → step=72）
        step = fov * (1 - overlap)
        n_views = int(math.ceil(360 / step))

        print(f"处理 {os.path.basename(input_path)}: 生成 {n_views} 张图，每张 FOV={fov}°，重叠={overlap*100:.1f}%，俯仰角={pitch_angle}°")
        if flip_vertical:
            print(f"启用垂直翻转功能（用于处理倒置拍摄的全景图）")
        
        if enable_angle_exclusion and exclude_angle_ranges:
            print(f"启用角度排除功能，排除范围: {exclude_angle_ranges}")

        generated_count = 0
        excluded_count = 0
        
        for i in range(n_views):
            theta = i * step  # 水平角
            phi = pitch_angle  # 垂直方向俯仰角
            
            # 检查是否应该排除这个角度
            if enable_angle_exclusion and exclude_angle_ranges:
                from config import is_angle_excluded
                if is_angle_excluded(theta, exclude_angle_ranges):
                    excluded_count += 1
                    continue
            
            out = equirectangular_to_perspective(img, fov, theta, phi, out_size, flip_vertical)
            
            # 生成输出文件名
            base_name = Path(input_path).stem
            output_filename = f"{base_name}_view_{generated_count:03d}.jpg"
            output_path = os.path.join(output_dir, output_filename)
            
            cv2.imwrite(output_path, out)
            generated_count += 1
            
        if enable_angle_exclusion and exclude_angle_ranges:
            print(f"完成处理 {os.path.basename(input_path)}: 生成 {generated_count} 张图，排除 {excluded_count} 张")
        else:
            print(f"完成处理 {os.path.basename(input_path)}: 生成 {generated_count} 张图")
        return True
        
    except Exception as e:
        print(f"处理 {input_path} 时出错: {str(e)}")
        return False


def process_single_image(args):
    """
    单张图片处理函数，用于多线程调用
    """
    input_path, output_base_dir, fov, overlap, out_size, exclude_angle_ranges, enable_angle_exclusion, pitch_angle, flip_vertical = args
    
    # 为每张图片创建独立的输出目录
    base_name = Path(input_path).stem
    output_dir = os.path.join(output_base_dir, base_name)
    
    return generate_views_for_image(input_path, output_dir, fov, overlap, out_size, 
                                  exclude_angle_ranges, enable_angle_exclusion, pitch_angle, flip_vertical)


def batch_process_images(input_folder, output_base_dir, fov=90, overlap=0.2, out_size=(1024,1024), 
                        max_workers=4, exclude_angle_ranges=None, enable_angle_exclusion=False, pitch_angle=0, flip_vertical=False):
    """
    批量处理文件夹中的全景图片，使用多线程
    """
    # 支持的图片格式
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # 获取所有图片文件
    input_path = Path(input_folder)
    if not input_path.exists():
        print(f"错误：输入文件夹 {input_folder} 不存在")
        return
    
    image_files = []
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_formats:
            image_files.append(str(file_path))
    
    if not image_files:
        print(f"在文件夹 {input_folder} 中没有找到支持的图片文件")
        return
    
    print(f"找到 {len(image_files)} 张图片，开始批量处理...")
    print(f"使用 {max_workers} 个线程进行处理")
    
    if enable_angle_exclusion and exclude_angle_ranges:
        print(f"角度排除功能已启用，排除范围: {exclude_angle_ranges}")
    
    print(f"俯仰角度设置为: {pitch_angle}°")
    
    if flip_vertical:
        print(f"垂直翻转功能已启用（用于处理倒置拍摄的全景图）")
    
    # 创建输出基础目录
    os.makedirs(output_base_dir, exist_ok=True)
    
    # 准备多线程参数
    thread_args = [(img_path, output_base_dir, fov, overlap, out_size, exclude_angle_ranges, enable_angle_exclusion, pitch_angle, flip_vertical) 
                   for img_path in image_files]
    
    # 使用线程池执行
    start_time = time.time()
    successful_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_path = {executor.submit(process_single_image, args): args[0] 
                         for args in thread_args}
        
        # 处理完成的任务
        for future in as_completed(future_to_path):
            img_path = future_to_path[future]
            try:
                result = future.result()
                if result:
                    successful_count += 1
            except Exception as e:
                print(f"处理 {img_path} 时发生异常: {str(e)}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n批量处理完成！")
    print(f"成功处理: {successful_count}/{len(image_files)} 张图片")
    print(f"总耗时: {total_time:.2f} 秒")
    print(f"平均每张图片: {total_time/len(image_files):.2f} 秒")
    print(f"输出目录: {output_base_dir}")
    
    if enable_angle_exclusion and exclude_angle_ranges:
        print(f"注意：已排除角度范围 {exclude_angle_ranges} 内的图片，以减少拍摄人的影响")
    
    if flip_vertical:
        print(f"注意：已启用垂直翻转功能，适用于倒置拍摄的全景图")


def main():
    parser = argparse.ArgumentParser(description='多线程批量处理全景图片')
    parser.add_argument('input_folder', help='输入文件夹路径')
    parser.add_argument('output_folder', help='输出文件夹路径')
    parser.add_argument('--fov', type=int, default=90, help='视场角（度），默认90')
    parser.add_argument('--overlap', type=float, default=0.2, help='重叠比例（0-1），默认0.2')
    parser.add_argument('--size', type=int, nargs=2, default=[1024, 1024], 
                       metavar=('WIDTH', 'HEIGHT'), help='输出图片尺寸，默认1024x1024')
    parser.add_argument('--threads', type=int, default=4, help='线程数，默认4')
    parser.add_argument('--pitch-angle', type=float, default=0, 
                       help='俯仰角度（度），正值向上，负值向下，默认0（水平）')
    parser.add_argument('--exclude-angles', type=float, nargs=2, action='append',
                       metavar=('START', 'END'), help='排除的角度范围，格式: START END，可多次使用')
    parser.add_argument('--enable-exclusion', action='store_true', 
                       help='启用角度排除功能')
    parser.add_argument('--flip-vertical', action='store_true', 
                       help='启用垂直翻转功能（用于处理倒置拍摄的全景图）')
    
    args = parser.parse_args()
    
    # 验证参数
    if not os.path.exists(args.input_folder):
        print(f"错误：输入文件夹 {args.input_folder} 不存在")
        return
    
    if args.overlap < 0 or args.overlap >= 1:
        print("错误：重叠比例必须在0到1之间")
        return
    
    if args.threads < 1:
        print("错误：线程数必须大于0")
        return
    
    # 验证俯仰角度参数
    if args.pitch_angle < -90 or args.pitch_angle > 90:
        print("错误：俯仰角度必须在-90到90度之间")
        return
    
    # 验证角度排除参数
    exclude_angle_ranges = []
    enable_angle_exclusion = args.enable_exclusion
    
    if args.exclude_angles:
        from config import validate_angle_ranges
        is_valid, error_msg = validate_angle_ranges(args.exclude_angles)
        if not is_valid:
            print(f"错误：{error_msg}")
            return
        exclude_angle_ranges = args.exclude_angles
        enable_angle_exclusion = True
    
    print("=== 全景图片批量处理程序 ===")
    print(f"输入文件夹: {args.input_folder}")
    print(f"输出文件夹: {args.output_folder}")
    print(f"视场角: {args.fov}°")
    print(f"重叠比例: {args.overlap*100:.1f}%")
    print(f"输出尺寸: {args.size[0]}x{args.size[1]}")
    print(f"线程数: {args.threads}")
    print(f"俯仰角度: {args.pitch_angle}°")
    if enable_angle_exclusion and exclude_angle_ranges:
        print(f"角度排除: 启用，排除范围: {exclude_angle_ranges}")
    else:
        print(f"角度排除: 禁用")
    if args.flip_vertical:
        print(f"垂直翻转: 启用")
    else:
        print(f"垂直翻转: 禁用")
    print("=" * 40)
    
    # 开始批量处理
    batch_process_images(
        input_folder=args.input_folder,
        output_base_dir=args.output_folder,
        fov=args.fov,
        overlap=args.overlap,
        out_size=tuple(args.size),
        max_workers=args.threads,
        exclude_angle_ranges=exclude_angle_ranges,
        enable_angle_exclusion=enable_angle_exclusion,
        pitch_angle=args.pitch_angle,
        flip_vertical=args.flip_vertical
    )


if __name__ == "__main__":
    # 如果没有命令行参数，使用默认值进行测试
    import sys
    if len(sys.argv) == 1:
        print("使用默认参数进行测试...")
        # 使用当前目录下的图片进行测试
        current_dir = "./inputs"
        output_dir = "batch_output"
        
        # 查找当前目录下的图片文件
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        image_files = []
        for file_path in Path(current_dir).iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                image_files.append(str(file_path))
        
        if image_files:
            print(f"找到测试图片: {image_files}")
            print("使用角度排除功能进行测试，排除拍摄人后方180度范围...")
            batch_process_images(
                input_folder=current_dir,
                output_base_dir=output_dir,
                fov=75,
                overlap=0.50,
                out_size=(1024, 1024),
                max_workers=6,
                exclude_angle_ranges=[(150,210)],  # 排除拍摄人后方180度范围
                enable_angle_exclusion=True,
                pitch_angle=0,  # 水平视角
                flip_vertical=False # 禁用垂直翻转

            )
        else:
            print("当前目录下没有找到图片文件，请使用命令行参数指定输入文件夹")
            print("使用示例: python batch_process.py input_folder output_folder --threads 8")
            print("角度排除示例: python batch_process.py input_folder output_folder --exclude-angles 150 210 --enable-exclusion")
            print("俯仰角度示例: python batch_process.py input_folder output_folder --pitch-angle 15")
            print("组合使用示例: python batch_process.py input_folder output_folder --pitch-angle -10 --exclude-angles 150 210 --enable-exclusion")
            print("垂直翻转示例: python batch_process.py input_folder output_folder --flip-vertical")
    else:
        main()
