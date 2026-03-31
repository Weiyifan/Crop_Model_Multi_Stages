"""
自定义物候期示例 - 展示如何定义多个物候期
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Crop_Model_Multi_Stages import (
    PhenologyStage, CropParameters, SimpleCropModel,
    generate_weather, print_summary, compare_scenarios
)


def create_custom_maize():
    """创建自定义玉米模型 (8个精细物候期)"""
    stages = [
        PhenologyStage(
            name="播种期",
            gdd_threshold=0,
            partition_leaf=0.80, partition_stem=0.15,
            partition_root=0.05, partition_grain=0.00,
            lai_growth_rate=0.05, height_growth_rate=0.1,
            rue_factor=0.8
        ),
        PhenologyStage(
            name="出苗期",
            gdd_threshold=80,
            partition_leaf=0.70, partition_stem=0.20,
            partition_root=0.10, partition_grain=0.00,
            lai_growth_rate=0.12, height_growth_rate=0.5,
            rue_factor=0.9
        ),
        PhenologyStage(
            name="三叶期",
            gdd_threshold=200,
            partition_leaf=0.65, partition_stem=0.20,
            partition_root=0.15, partition_grain=0.00,
            lai_growth_rate=0.15, height_growth_rate=0.8,
            rue_factor=1.0
        ),
        PhenologyStage(
            name="拔节期",
            gdd_threshold=450,
            partition_leaf=0.50, partition_stem=0.30,
            partition_root=0.15, partition_grain=0.05,
            lai_growth_rate=0.18, height_growth_rate=1.5,
            rue_factor=1.1
        ),
        PhenologyStage(
            name="大喇叭口期",
            gdd_threshold=750,
            partition_leaf=0.35, partition_stem=0.35,
            partition_root=0.15, partition_grain=0.15,
            lai_growth_rate=0.10, height_growth_rate=0.8,
            rue_factor=1.2
        ),
        PhenologyStage(
            name="抽雄吐丝期",
            gdd_threshold=1000,
            partition_leaf=0.20, partition_stem=0.25,
            partition_root=0.15, partition_grain=0.40,
            lai_growth_rate=0.05, height_growth_rate=0.2,
            rue_factor=1.25
        ),
        PhenologyStage(
            name="灌浆期",
            gdd_threshold=1400,
            partition_leaf=0.05, partition_stem=0.15,
            partition_root=0.10, partition_grain=0.70,
            lai_growth_rate=0.0, height_growth_rate=0.0,
            senescence_rate=0.015, rue_factor=1.15
        ),
        PhenologyStage(
            name="完熟期",
            gdd_threshold=1800,
            partition_leaf=0.00, partition_stem=0.00,
            partition_root=0.00, partition_grain=1.00,
            lai_growth_rate=0.0, height_growth_rate=0.0,
            senescence_rate=0.03, rue_factor=0.7
        )
    ]
    
    return CropParameters(
        crop_name="精细玉米模型",
        base_temp=8.0,
        max_gdd=1800,
        max_lai=6.0,
        rue_base=4.0,
        light_extinction=0.65,
        phenology_stages=stages,
        description="8个物候期的精细玉米模型"
    )


def create_fast_growing_crop():
    """创建快速生长作物 (4个简单物候期)"""
    stages = [
        PhenologyStage(
            name="幼苗期",
            gdd_threshold=0,
            partition_leaf=0.60, partition_stem=0.30,
            partition_root=0.10, partition_grain=0.00,
            lai_growth_rate=0.15, height_growth_rate=1.0
        ),
        PhenologyStage(
            name="快速生长期",
            gdd_threshold=300,
            partition_leaf=0.40, partition_stem=0.40,
            partition_root=0.15, partition_grain=0.05,
            lai_growth_rate=0.20, height_growth_rate=2.0,
            rue_factor=1.1
        ),
        PhenologyStage(
            name="开花结实期",
            gdd_threshold=600,
            partition_leaf=0.15, partition_stem=0.20,
            partition_root=0.10, partition_grain=0.55,
            lai_growth_rate=0.05, height_growth_rate=0.3,
            rue_factor=1.2
        ),
        PhenologyStage(
            name="成熟期",
            gdd_threshold=900,
            partition_leaf=0.00, partition_stem=0.00,
            partition_root=0.00, partition_grain=1.00,
            lai_growth_rate=0.0, senescence_rate=0.02,
            rue_factor=0.8
        )
    ]
    
    return CropParameters(
        crop_name="速生作物",
        base_temp=12.0,
        max_gdd=900,
        max_lai=5.0,
        rue_base=3.5,
        phenology_stages=stages,
        description="4个物候期的速生作物"
    )


def main():
    print("="*70)
    print("自定义物候期示例")
    print("="*70)
    
    # 生成气象数据
    print("\n生成气象数据...")
    weather = generate_weather(start_day=120, days=200, seed=42)
    
    # 场景1: 精细玉米模型 (8阶段)
    print("\n" + "="*70)
    print("场景1: 精细玉米模型 (8个物候期)")
    print("="*70)
    
    params1 = create_custom_maize()
    print(f"\n作物: {params1.crop_name}")
    print(f"物候期数量: {len(params1.phenology_stages)}")
    print("\n物候期配置:")
    for i, stage in enumerate(params1.phenology_stages, 1):
        print(f"  {i}. {stage.name:12s} (GDD≥{stage.gdd_threshold:4.0f}) "
              f"叶{stage.partition_leaf:.2f} 籽{stage.partition_grain:.2f} "
              f"RUE×{stage.rue_factor:.2f}")
    
    model1 = SimpleCropModel(params1)
    results1 = model1.run(weather, verbose=False)
    print_summary(results1)
    
    # 场景2: 速生作物 (4阶段)
    print("\n" + "="*70)
    print("场景2: 速生作物 (4个物候期)")
    print("="*70)
    
    params2 = create_fast_growing_crop()
    print(f"\n作物: {params2.crop_name}")
    print(f"物候期数量: {len(params2.phenology_stages)}")
    print("\n物候期配置:")
    for i, stage in enumerate(params2.phenology_stages, 1):
        print(f"  {i}. {stage.name:12s} (GDD≥{stage.gdd_threshold:4.0f}) "
              f"叶{stage.partition_leaf:.2f} 籽{stage.partition_grain:.2f}")
    
    model2 = SimpleCropModel(params2)
    results2 = model2.run(weather, verbose=False)
    print_summary(results2)
    
    # 对比两个场景
    print("\n" + "="*70)
    print("场景对比")
    print("="*70)
    compare_scenarios(
        [results1, results2],
        ["精细玉米(8阶段)", "速生作物(4阶段)"]
    )


if __name__ == "__main__":
    main()
