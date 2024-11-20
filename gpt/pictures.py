import os
import numpy as np
import math
import json
import torch
from io import BytesIO
from PIL import Image
import base64
import glob

def save_tensor_as_images(tensor_dict, save_dir='logs/running_log', name='clockwise'):
    """
    将字典中的张量（假设包含一个 RGB 张量）转换为图像并保存到指定目录。
    
    参数：
    - tensor_dict (dict): 包含张量数据的字典，假设键是 'rgb'，值是一个形状为 [12, H, W, C] 的张量。
    - save_dir (str): 存储图像的目录路径，默认是 'logs/running_log'。
    - name (str): 用于生成图像文件名前缀的名字，默认是 'clockwise'。
    """
    # 获取 RGB 张量
    rgb_batch = tensor_dict.get('rgb')
    
    if rgb_batch is None:
        raise ValueError("字典中没有找到键 'rgb'。")
    
    # 确保张量是 [N, H, W, C] 形状
    if len(rgb_batch.shape) != 4 or rgb_batch.shape[-1] != 3:
        raise ValueError(f"输入张量的形状不符合要求，应该是 [N, H, W, 3]，实际是 {rgb_batch.shape}。")
    
    # 确保保存路径存在并创建
    os.makedirs(save_dir, exist_ok=True)
    
    # 将张量转为图像并保存
    for i in range(rgb_batch.shape[0]):
        # 提取单张图像，并确保格式为 [H, W, C]（因为 RGB 需要这种格式）
        img_array = rgb_batch[i].cpu().numpy()
        img_array = (img_array - img_array.min()) / (img_array.max() - img_array.min())  # 归一化到 [0, 1]
        img_array = (img_array * 255).astype(np.uint8)  # 转为 8 位图像

        # 转为 PIL 图像对象
        img = Image.fromarray(img_array)

        # 保存图像，文件名可以用索引来区分
        img.save(os.path.join(save_dir, f'{name}_image_{i}.png'))

    print(f"Images have been saved to {save_dir}")


def delete_png_images_in_directory(directory='logs/running_log'):
    """
    删除指定目录中所有后缀为 .png 的文件。
    
    参数：
    - directory (str): 要处理的目录路径，默认是 'logs/running_log'。
    """
    
    # 构建匹配所有 .png 文件的路径模式
    pattern = os.path.join(directory, '*.png')
    
    # 使用 glob 查找所有匹配的文件
    files = glob.glob(pattern)
    
    # 遍历文件列表并删除每个文件
    for file_path in files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

# 调用函数来删除.png文件
#delete_png_images_in_directory()



def process_batch_data(obs_view12_counterclockwise, img_idxes):
    """
    根据索引筛选图片和角度，并转换为 JSON 可用格式（图片直接编码为 Base64）。
    
    参数:
    - obs_view12_counterclockwise: dict，包含键 'rgb' 的数据 (torch.Size: [12, 224, 224, 3])。
    - img_idxes: array，指定要筛选的图片索引 (如 [3, 1, 0])。
    
    返回:
    - cand_inputs: list，包含格式化后的图片 Base64 编码和角度数据。
    """
    # 筛选出指定索引的图片
    selected_images = obs_view12_counterclockwise['rgb'][img_idxes]

    # 根据索引计算对应角度（直接乘以 30）
    angles_deg = img_idxes * 30
    print(angles_deg)

    # 构建 JSON 格式化的候选输入
    cand_inputs = []
    for image_array, angle in zip(selected_images, angles_deg):
        # 将图像从 tensor 转换为 numpy 并缩放到 [0, 255]
        image_array = (image_array.cpu().numpy() * 255).astype(np.uint8)
        
        # 转换 numpy array 为 PIL 图像
        image = Image.fromarray(image_array)
        
        # 将图像编码为 Base64 字符串
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # 添加到候选列表
        cand_inputs.append({
            "image": img_str,  # Base64 编码的图像数据
            "angle": angle  # 直接使用计算的角度
        })

    return cand_inputs

# 示例数据
# obs_view12_counterclockwise = {
#     "rgb": torch.randn(12, 224, 224, 3)  # 假设是随机数据
# }
# img_idxes = np.array([3, 1, 0])

# 调用函数处理数据
# cand_inputs = process_batch_data(obs_view12_counterclockwise, img_idxes)

# 转为 JSON 格式
# cand_inputs_json = json.dumps(cand_inputs, indent=4)
# print(cand_inputs_json)



