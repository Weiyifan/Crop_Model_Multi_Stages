"""
多物候期对比演示 - 展示不同物候期数量配置的效果
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import matplotlib.pyplot as plt
from crop_model_multi_stages import (
    PhenologyStage, PhenologyConfig, CropParameters, 
    CropModel, generate_weather
)

def create_3stage_config():
    """创建3阶段物候期配置"""
    return PhenologyConfig([
        PhenologyStage("营养期", gdd_threshold=0,
                      partition_leaf=0.55, partition_stem=0.25,
                      partition_root=0.20, partition_grain=0.0,
                      lai_growth_rate=0.10),
        PhenologyStage("生殖期", gdd_threshold=800,
                      partition_leaf=0.30, partition_stem=0.20,
                      partition_root=0.0, partition_grain=0.50,
                      lai_growth_rate=0.03),
        PhenologyStage("成熟期", gdd_threshold=1600,
                      partition_leaf=0.0, partition_stem=0.0,
                      partition_root=0.0, partition_grain=1.0,
                      senescence_start=True)
    ])

def create_5stage_config():
    """创建5阶段物候期配置"""
    return PhenologyConfig([
        PhenologyStage("播种-出苗", gdd_threshold=0,
                      partition_leaf=0.50, partition_stem=0.30,
                      partition_root=0.20, partition_grain=0.0),
        PhenologyStage("苗期", gdd_threshold=100,
                      partition_leaf=0.55, partition_stem=0.25,
                      partition_root=0.20, partition_grain=0.0,
                      lai_growth_rate=0.12),
        PhenologyStage("快速生长期", gdd_threshold=500,
                      partition_leaf=0.50, partition_stem=0.30,
                      partition_root=0.20, partition_grain=0.0,
                      lai_growth_rate=0.10),
        PhenologyStage("开花-灌浆", gdd_threshold=1000,
                      partition_leaf=0.20, partition_stem=0.20,
                      partition_root=0.0, partition_grain=0.60,
                      lai_growth_rate=0.02),
        PhenologyStage("成熟", gdd_threshold=1800,
                      partition_leaf=0.0, partition_stem=0.0,
                      partition_root=0.0, partition_grain=1.0,
                      senescence_start=True)
    ])

def run_simulation(phenology_config, name):
    """运行单个模拟"""
    weather = generate_weather(start_day=120, days=180, base_temp=20, seed=42)
    
    params = CropParameters(
        crop_name=name,
        base_temp=10.0,
        max_lai=6.0,
        rue=3.5,
        phenology=phenology_config
    )
    
    model = CropModel(params)
    results = model.run(weather)
    
    return {
        'name': name,
        'stages': len(phenology_config),
        'results': results
    }

def plot_comparison(results_list):
    """绘制不同配置的对比"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(results_list)))
    
    # 1. LAI动态对比
    ax = axes[0, 0]
    for i, res in enumerate(results_list):
        df = res['results']['daily_data']
        ax.plot([d['day'] for d in df], [d['lai'] for d in df],
                label=f"{res['name']} ({res['stages']}阶段)", 
                color=colors[i], linewidth=2)
    ax.set_xlabel('Day of Year')
    ax.set_ylabel('LAI')
    ax.set_title('LAI Dynamics Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. 生物量积累对比
    ax = axes[0, 1]
    for i, res in enumerate(results_list):
        df = res['results']['daily_data']
        ax.plot([d['day'] for d in df], [d['total_biomass'] for d in df],
                label=f"{res['name']}", color=colors[i], linewidth=2)
        ax.plot([d['day'] for d in df], [d['grain'] for d in df],
                linestyle='--', color=colors[i], alpha=0.7)
    ax.set_xlabel('Day of Year')
    ax.set_ylabel('Biomass (g/m²)')
    ax.set_title('Biomass Accumulation')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. 物候期阶段对比
    ax = axes[1, 0]
    for i, res in enumerate(results_list):
        df = res['results']['daily_data']
        ax.plot([d['day'] for d in df], [d['stage_index'] for d in df],
                label=f"{res['name']}", color=colors[i], linewidth=2)
    ax.set_xlabel('Day of Year')
    ax.set_ylabel('Stage Index')
    ax.set_title('Phenological Stage Progression')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. 产量对比
    ax = axes[1, 1]
    names = [f"{r['name']}\n({r['stages']}阶段)" for r in results_list]
    yields = [r['results']['grain_yield']/100 for r in results_list]
    biomass = [r['results']['final_biomass']/100 for r in results_list]
    
    x = np.arange(len(names))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, yields, width, label='Grain Yield', color='gold')
    bars2 = ax.bar(x + width/2, biomass, width, label='Total Biomass', color='forestgreen', alpha=0.7)
    
    ax.set_ylabel('Yield/Biomass (t/ha)')
    ax.set_title('Final Yield and Biomass Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('multi_stage_comparison.png', dpi=150, bbox_inches='tight')
    print("对比图已保存为 multi_stage_comparison.png")
    plt.show()

def main():
    print("=== 多物候期配置对比演示 ===\n")
    
    # 创建不同的物候期配置
    configs = [
        (create_3stage_config(), "Simple 3-Stage"),
        (create_5stage_config(), "Detailed 5-Stage"),
    ]
    
    # 添加预定义的玉米配置
    from crop_model_multi_stages import CropParameters
    maize_params = CropParameters.maize()
    configs.append((maize_params.phenology, "Maize 6-Stage"))
    
    # 运行所有模拟
    results = []
    for phenology, name in configs:
        print(f"运行 {name} 模拟...")
        result = run_simulation(phenology, name)
        results.append(result)
    
    # 打印结果摘要
    print("\n=== 结果摘要 ===")
    print(f"{'Configuration':<20} {'Stages':>8} {'Yield(t/ha)':>12} {'Biomass(t/ha)':>14} {'HI':>8}")
    print("-" * 70)
    for res in results:
        r = res['results']
        print(f"{res['name']:<20} {res['stages']:>8} "
              f"{r['grain_yield']/100:>12.2f} "
              f"{r['final_biomass']/100:>14.2f} "
              f"{r['harvest_index']:>8.2f}")
    
    # 绘制对比图
    plot_comparison(results)

if __name__ == "__main__":
    main()
