"""
基础用法示例 - 展示SimpleCropModel的基本功能 (支持多物候期)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Crop_Model_Multi_Stages import CropParameters, SimpleCropModel, generate_weather
from Crop_Model_Multi_Stages.utils import print_summary

def main():
    # 1. 创建作物参数 (使用预定义的玉米参数 - 包含6个物候期)
    params = CropParameters.maize()
    print(f"作物: {params.crop_name}")
    print(f"基础温度: {params.base_temp}°C")
    print(f"物候期数量: {len(params.phenology_stages)}")
    print("\n物候期列表:")
    for i, stage in enumerate(params.phenology_stages, 1):
        print(f"  {i}. {stage.name} (GDD≥{stage.gdd_threshold})")
    
    # 2. 生成气象数据 (模拟夏季150天)
    print("\n生成气象数据...")
    weather = generate_weather(start_day=120, days=150, base_temp=20)
    
    # 3. 初始化模型
    model = SimpleCropModel(params)
    
    # 4. 运行模拟
    print("\n运行模拟...")
    results = model.run(weather, verbose=True)
    
    # 5. 输出结果
    print_summary(results)
    
    # 6. 显示物候期转换
    print("\n物候期转换记录:")
    for trans in results['stage_transitions']:
        print(f"  Day {trans['day']}: {trans['from_stage']} → {trans['to_stage']} "
              f"(GDD={trans['gdd']:.0f})")
    
    # 7. 保存详细数据到CSV (可选)
    try:
        import pandas as pd
        df = pd.DataFrame(results['daily_data'])
        df.to_csv('simulation_output.csv', index=False)
        print("\n详细数据已保存到 simulation_output.csv")
    except ImportError:
        print("\n(安装pandas后可导出CSV详细数据)")

if __name__ == "__main__":
    main()
