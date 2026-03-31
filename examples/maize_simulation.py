"""
起始：玉米产量模拟 - 对比不同播期的影响
复现用户原始代码中的完整分析流程
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import matplotlib.pyplot as plt
from Crop_Model_Multi_Stages import CropParameters, OptimizedCropModel, generate_weather
import pandas as pd

def run_scenario(start_doy, scenario_name):
    """运行单场景模拟"""
    weather = generate_weather(
        start_day=start_doy, 
        days=180, 
        base_temp=18, 
        temp_amp=8,
        seed=start_doy  # 不同播期不同天气
    )
    
    model = OptimizedCropModel(CropParameters.maize())
    results = model.run(weather)
    
    return {
        'scenario': scenario_name,
        'start_doy': start_doy,
        'yield': results['grain_yield'],
        'biomass': results['final_biomass'],
        'maturity_day': results['maturity_day'],
        'max_lai': results['max_lai'],
        'daily_data': pd.DataFrame(results['daily_data'])
    }

def plot_comparison(scenarios):
    """绘制多场景对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(scenarios)))
    
    # 1. LAI动态
    ax = axes[0, 0]
    for i, sc in enumerate(scenarios):
        df = sc['daily_data']
        ax.plot(df['day'] - sc['start_doy'], df['lai'], 
                label=sc['scenario'], color=colors[i], linewidth=2)
    ax.set_xlabel('Days after sowing')
    ax.set_ylabel('Leaf Area Index')
    ax.set_title('LAI Dynamics')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. 生物量积累
    ax = axes[0, 1]
    for i, sc in enumerate(scenarios):
        df = sc['daily_data']
        ax.plot(df['day'] - sc['start_doy'], df['total_biomass'], 
                label=sc['scenario'], color=colors[i], linewidth=2)
        ax.plot(df['day'] - sc['start_doy'], df['grain'], 
                linestyle='--', color=colors[i], alpha=0.7)
    ax.set_xlabel('Days after sowing')
    ax.set_ylabel('Biomass (g/m²)')
    ax.set_title('Biomass Accumulation')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. 发育阶段
    ax = axes[1, 0]
    stage_map = {"播种-出苗": 0, "营养生长": 1, "生殖生长": 2, "成熟": 3}
    for i, sc in enumerate(scenarios):
        df = sc['daily_data']
        stages = [stage_map.get(s, -1) for s in df['stage']]
        ax.plot(df['day'] - sc['start_doy'], stages, 
                label=sc['scenario'], color=colors[i], linewidth=2)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(['Emergence', 'Vegetative', 'Reproductive', 'Mature'])
    ax.set_xlabel('Days after sowing')
    ax.set_title('Phenological Stages')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. 产量对比条形图
    ax = axes[1, 1]
    yields = [sc['yield']/100 for sc in scenarios]  # 转换为t/ha
    names = [sc['scenario'] for sc in scenarios]
    bars = ax.bar(names, yields, color=colors)
    ax.set_ylabel('Grain Yield (t/ha)')
    ax.set_title('Final Yield Comparison')
    
    # 在柱子上添加数值
    for bar, y in zip(bars, yields):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{y:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('maize_comparison.png', dpi=150, bbox_inches='tight')
    print("图表已保存为 maize_comparison.png")
    plt.show()

def main():
    print("=== 玉米不同播期模拟 ===\n")
    
    # 定义3个场景
    scenarios = [
        run_scenario(110, "Early Sowing (Apr 20)"),
        run_scenario(130, "Normal Sowing (May 10)"),
        run_scenario(150, "Late Sowing (May 30)")
    ]
    
    # 打印结果表格
    print(f"{'Scenario':<20} {'Yield(t/ha)':>12} {'Biomass(t/ha)':>14} {'Days':>6}")
    print("-" * 60)
    for sc in scenarios:
        print(f"{sc['scenario']:<20} {sc['yield']/100:>12.2f} "
              f"{sc['biomass']/100:>14.2f} {sc['maturity_day']:>6}")
    
    # 可视化
    plot_comparison(scenarios)

if __name__ == "__main__":
    main()
