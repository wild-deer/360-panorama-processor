# 🌐 全景图片批量处理程序

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

> 🚀 **一个高性能的多线程全景图片批量处理工具**  
> 专为全景摄影师、VR内容创作者和房地产展示设计

---

## ✨ 功能特点

| 功能 | 描述 | 状态 |
|------|------|------|
| 🔄 **批量处理** | 支持文件夹批量处理全景图片 | ✅ |
| ⚡ **多线程加速** | 利用多核CPU提升处理速度 | ✅ |
| 🎯 **参数可配置** | 视场角、重叠比例、输出尺寸等 | ✅ |
| 🖼️ **多格式支持** | JPG, PNG, BMP, TIFF等 | ✅ |
| 🚫 **角度排除** | 排除指定角度范围，减少干扰 | ✅ |
| 🔄 **垂直翻转** | 处理倒置拍摄的全景图 | ✅ |
| 📐 **俯仰角度** | 支持向上/向下视角调整 | ✅ |

---

## 🚀 快速开始

### 📋 系统要求

- **Python**: 3.6+
- **依赖库**: OpenCV, NumPy
- **操作系统**: Windows, macOS, Linux

### 🔧 安装依赖

```bash
# 方式1: 直接安装
pip install opencv-python numpy

# 方式2: 使用requirements.txt
pip install -r requirements.txt
```

### 🎯 基本用法

```bash
# 最简单的用法
python batch_process.py 输入文件夹 输出文件夹

# 使用默认参数（当前目录）
python batch_process.py
```

---

## ⚙️ 高级配置

### 🔧 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `输入文件夹` | 路径 | 当前目录 | 包含全景图片的文件夹 |
| `输出文件夹` | 路径 | `output_views` | 处理结果输出位置 |
| `--fov` | 整数 | 90 | 视场角（度） |
| `--overlap` | 浮点数 | 0.2 | 重叠比例（0-1） |
| `--size` | 整数 整数 | 1024 1024 | 输出图片尺寸 |
| `--threads` | 整数 | 4 | 处理线程数 |
| `--pitch-angle` | 整数 | 0 | 俯仰角度（度） |
| `--exclude-angles` | 整数 整数 | - | 排除的角度范围 |
| `--enable-exclusion` | 标志 | False | 启用角度排除 |
| `--flip-vertical` | 标志 | False | 启用垂直翻转 |

### 🎨 使用示例

<details>
<summary><b>🔍 基础处理示例</b></summary>

```bash
# 处理指定文件夹，使用8个线程
python batch_process.py ./panorama_images ./output --threads 8

# 自定义视场角和重叠比例
python batch_process.py ./input ./output --fov 60 --overlap 0.3 --threads 6
```

</details>

<details>
<summary><b>🚫 角度排除示例</b></summary>

```bash
# 排除150-210度范围的图片（拍摄人后方区域）
python batch_process.py ./input ./output --exclude-angles 150 210 --enable-exclusion

# 排除多个角度范围
python batch_process.py ./input ./output \
    --exclude-angles 150 210 \
    --exclude-angles 270 330 \
    --enable-exclusion
```

</details>

<details>
<summary><b>🔄 垂直翻转示例</b></summary>

```bash
# 启用垂直翻转，处理倒置拍摄的全景图
python batch_process.py ./input ./output --flip-vertical

# 组合使用：翻转 + 俯仰角度 + 角度排除
python batch_process.py ./input ./output \
    --flip-vertical \
    --pitch-angle -10 \
    --exclude-angles 150 210 \
    --enable-exclusion
```

</details>

---

## 🔄 垂直翻转功能详解

### 📖 功能说明

垂直翻转功能专门用于处理倒置拍摄的全景图。当全景相机倒置拍摄时，生成的图片上下颠倒，直接处理会导致视角错误。

### 🎯 使用场景

- **📷 倒置拍摄**: 相机倒置安装拍摄的全景图
- **🎬 特殊角度**: 需要从特定角度拍摄的全景图  
- **🔧 设备限制**: 由于设备安装限制必须倒置拍摄的情况

### ⚙️ 工作原理

启用垂直翻转功能后，程序会：

1. 🔄 在生成透视图之前，先将输入的全景图进行垂直翻转
2. 🎯 翻转后的图片按照正常的坐标系统进行处理
3. ✨ 生成的透视图具有正确的视角方向

### ⚠️ 注意事项

> **💡 提示**: 翻转功能会增加少量处理时间，建议在处理前确认图片确实需要翻转

---

## 🚫 角度排除功能详解

### 🧭 角度说明

| 角度 | 方向 | 说明 |
|------|------|------|
| **0°** | 🧭 前方 | 图片正前方 |
| **90°** | ➡️ 右方 | 图片右侧 |
| **180°** | 🧭 后方 | 图片后方（通常是拍摄人站立的位置） |
| **270°** | ⬅️ 左方 | 图片左侧 |

### 🎯 推荐设置

| 场景 | 角度范围 | 说明 |
|------|----------|------|
| **👤 拍摄人后方** | 150° - 210° | 排除拍摄人及其周围区域 |
| **👈 拍摄人左侧** | 270° - 330° | 排除左侧区域 |
| **👉 拍摄人右侧** | 30° - 90° | 排除右侧区域 |

### 🎬 使用场景

- **🏖️ 旅游摄影**: 排除拍摄人及其装备
- **🏠 房地产展示**: 排除拍摄设备和人员
- **🌅 景观摄影**: 排除不必要的干扰元素
- **🥽 VR内容制作**: 提高沉浸式体验质量

---

## 📁 输出结构

程序会为每张输入图片创建一个独立的输出文件夹：

```
输出文件夹/
├── 📸 图片1名称/
│   ├── 图片1名称_view_000.jpg
│   ├── 图片1名称_view_001.jpg
│   └── ...
├── 📸 图片2名称/
│   ├── 图片2名称_view_000.jpg
│   ├── 图片2名称_view_001.jpg
│   └── ...
└── ...
```

> **⚠️ 注意**: 启用角度排除功能后，某些视角的图片会被跳过，因此输出图片的编号可能不连续。

---

## ⚡ 性能优化建议

### 🖥️ 线程数设置

| CPU核心数 | 推荐线程数 | 说明 |
|-----------|------------|------|
| **4核** | 4-6 | 避免过度线程切换 |
| **8核** | 6-8 | 平衡性能和资源利用 |
| **16核** | 8-12 | 充分利用多核优势 |

### 🎯 其他优化策略

- **📏 输出尺寸**: 较小的输出尺寸可以显著提高处理速度
- **🔄 重叠比例**: 较小的重叠比例可以减少生成的图片数量
- **🚫 角度排除**: 启用角度排除功能可以减少生成的图片数量，提高处理速度

---

## 🛠️ 工具和测试

### 🚀 快速启动

使用交互式界面快速配置参数：

```bash
python quick_start.py
```

### 🧪 功能测试

```bash
# 测试角度排除功能
python test_angle_exclusion.py

# 测试垂直翻转功能
python test_flip.py

# 测试批量处理
python test_batch.py
```

---

## ⚠️ 重要注意事项

> **🔴 关键要求**: 输入图片必须是全景图片（equirectangular格式）

| 注意事项 | 说明 |
|----------|------|
| **📁 文件夹创建** | 程序会自动创建输出文件夹 |
| **💾 磁盘空间** | 处理大量图片时，确保有足够的磁盘空间 |
| **🧪 参数测试** | 建议先用少量图片测试参数设置 |
| **📐 角度范围** | 角度范围必须在0-360度之间，起始角度必须小于结束角度 |
| **🔄 功能组合** | 角度排除功能会减少生成的图片数量，但提高整体质量 |

---

## 📚 相关文档

- [📖 项目说明](项目说明.md)
- [🔄 垂直翻转功能说明](垂直翻转功能说明.md)
- [📁 部署指南](deploy/360-panorama-processor/README.md)

---

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

---

<div align="center">

**🌟 如果这个项目对您有帮助，请给它一个Star！**

</div>
