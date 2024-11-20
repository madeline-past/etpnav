import math

def quaternion_to_euler(q):
    """
    将四元数转换为欧拉角 (滚转, 俯仰, 偏航)，确保欧拉角在0到2pi的范围内。
    
    参数:
    q: 四元数，元组或列表 (w, x, y, z)
    
    返回:
    一个元组 (roll, pitch, yaw)，分别是绕X轴（滚转）、Y轴（俯仰）、Z轴（偏航）的旋转角度，单位是弧度
    """
    w, x, y, z = q
    
    # 计算滚转角 (Roll)
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    
    # 计算俯仰角 (Pitch)
    pitch = math.asin(2.0 * (w * y - z * x))
    
    # 计算偏航角 (Yaw)
    yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    
    # 将滚转角、俯仰角和偏航角限制在特定范围内
    roll = (roll + 2 * math.pi) % (2 * math.pi)  # 使roll在[0, 2pi]范围内
    yaw = (yaw + 2 * math.pi) % (2 * math.pi)  # 使yaw在[0, 2pi]范围内
    
    # 俯仰角应限制在[-pi/2, pi/2]范围内
    if pitch > math.pi / 2:
        pitch = math.pi / 2
    elif pitch < -math.pi / 2:
        pitch = -math.pi / 2
    
    return roll, pitch, yaw

# 示例: 四元数 (w, x, y, z)
q = (0.707, 0.0, 0.707, 0.0)

# 调用函数转换为欧拉角
roll, pitch, yaw = quaternion_to_euler(q)

# 输出结果（单位：弧度）
print("Roll: {:.3f} radians".format(roll))
print("Pitch: {:.3f} radians".format(pitch))
print("Yaw: {:.3f} radians".format(yaw))

# 如果需要角度单位，可以转换为度
roll_deg = math.degrees(roll)
pitch_deg = math.degrees(pitch)
yaw_deg = math.degrees(yaw)

print("\nRoll: {:.3f} degrees".format(roll_deg))
print("Pitch: {:.3f} degrees".format(pitch_deg))
print("Yaw: {:.3f} degrees".format(yaw_deg))
