import torch

def filter_minimum_distances(angle_idxes, distance_idxes):
    # 边界检查
    if len(angle_idxes) != len(distance_idxes):
        raise ValueError("angle_idxes and distance_idxes must have the same length")
    
    # 确保张量在 CPU 上，以便能进行 NumPy 样式操作
    angle_idxes_cpu = angle_idxes.cpu()
    distance_idxes_cpu = distance_idxes.cpu()
    
    # 计算 img_idxes
    img_idxes = 12 - ((angle_idxes_cpu + 5) // 10)
    img_idxes[img_idxes == 12] = 0

    # 字典用来存储每个 img_idx 与其最小的 angle_idx 和对应距离
    img_to_min_data_map = {}
    
    # 遍历每个 angle_idx, img_idx, 和 distance
    for angle_idx, img_idx, distance in zip(angle_idxes_cpu, img_idxes, distance_idxes_cpu):
        if img_idx.item() not in img_to_min_data_map:
            # 将 img_idx 初次映射到 angle_idx 和 distance
            img_to_min_data_map[img_idx.item()] = (angle_idx.item(), distance.item())
        else:
            # 如果当前距离小于已有的距离，更新该 img_idx 的映射
            _, current_min_distance = img_to_min_data_map[img_idx.item()]
            if distance.item() < current_min_distance:
                img_to_min_data_map[img_idx.item()] = (angle_idx.item(), distance.item())
    
    # 从字典中提取最终的 angle_idx 和 distance
    updated_angle_idxes = [data[0] for data in img_to_min_data_map.values()]
    updated_distance_idxes = [data[1] for data in img_to_min_data_map.values()]
    
    # 转换为 PyTorch 张量
    updated_angle_idxes_tensor = torch.tensor(updated_angle_idxes, device=angle_idxes.device)
    updated_distance_idxes_tensor = torch.tensor(updated_distance_idxes, device=distance_idxes.device)
    
    return updated_angle_idxes_tensor, updated_distance_idxes_tensor


def extract_waypoint_number(json_output, candidate_lengths):
    # 获取 'Action' 的值
    action_value = json_output.get('Action', '')
    
    # 如果 Action 是 'stop'，返回 candidate_lengths
    if action_value == "stop":
        return candidate_lengths - 1
    
    # 提取数字部分，如果 Action 以 "Waypoint_" 开头
    if action_value.startswith('Waypoint_'):
        try:
            number = int(action_value.split('_')[1])
            return number
        except (IndexError, ValueError):
            return None  # 如果提取数字失败，返回 None
    
    # 如果 'Action' 不符合预期格式，返回 None
    return None




# 示例使用
# angle_idxes_sample = torch.tensor([92, 106, 111, 116], device='cuda:0')
# distance_idxes_sample = torch.tensor([7, 2, 2, 4], device='cuda:0')

# updated_angle_idxes, updated_distance_idxes = filter_minimum_distances(angle_idxes_sample, distance_idxes_sample)
# print(updated_angle_idxes)
# print(updated_distance_idxes)



