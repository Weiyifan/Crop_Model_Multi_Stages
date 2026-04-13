"""
基础使用示例 - 展示CropModel的基本功能和多物候期特性
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crop_model_multi_stages import CropParameters, CropModel, generate_weather
from crop_model_multi_stages.utils import print_summary

def main():
    print("=== 多物候期作物模型 - 基础使用示例 ===\n")
    
    # 1. 创建作物参数 (使用预定义的玉米参数 - 6阶段物候期)
    params = CropParameters.maize()
    print(f"作物: {params.crop_name}")
    print(f"基础温度: {params.base_temp}°C")
    print(f"物候期数量: {len(params.phenology)}")
    print(f"物候期列表: {params.phenology.get_stage_names()}")
    print()
    
    # 2. 生成气象数据 (模拟夏季180天)
    weather = generate_weather(start_day=120, days=180, base_temp=20)
    print(f"生成气象数据: {len(weather)} 天")
    print()
    
    # 3. 初始化模型
    model = CropModel(params)
    
    # 4. 运行模拟 (verbose=True 显示物候期转换)
    print("运行模拟...")
    results = model.run(weather, verbose=True)
    print()
    
    # 5. 输出结果
    print_summary(results)
    
    # 6. 打印物候期详细信息
    print("\n=== 物候期详细信息 ===")
    for stage_name, info in results['stage_info'].items():
        print(f"{stage_name}:")
        print(f"  天数: {info['days']} 天")
        print(f"  GDD范围: {info['start_gdd']:.0f} - {info['end_gdd']:.0f}")
        print()
    
    # 7. 保存详细数据到CSV
    import pandas as pd
    df = pd.DataFrame(results['daily_data'])
    df.to_csv('simulation_output.csv', index=False)
    print("详细数据已保存到 simulation_output.csv")

if __name__ == "__main__":
    main()
