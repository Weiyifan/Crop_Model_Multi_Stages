# Crop_Model_Multi_Stages

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于生理过程的多物候期作物生长模拟模型，支持任意数量的物候期自定义配置，适用于产量预测、气候变化影响评估和农艺措施优化。

## 模型特点

- **多物候期支持**: 可定义任意数量的物候期，每个物候期有独立参数
- **物候期平滑过渡**: 支持物候期之间的线性插值过渡
- **积温驱动**: 基于Growing Degree Days (GDD)的物候发育模型
- **光截获模拟**: Beer-Lambert定律计算冠层光截获
- **动态生物量分配**: 按物候期动态分配同化物到叶、茎、根、籽粒
- **胁迫响应**: 模拟水分、氮素和温度胁迫的影响
- **源库关系**: 高级模型支持源库平衡模拟
- **模块化设计**: 易于扩展和参数校准

## 核心方程

1. **积温计算**: $GDD = \max(0, T_{avg} - T_{base})$
2. **光截获**: $Q_{int} = Q_{total} \times (1 - e^{-k \times LAI})$
3. **生物量增长**: $\Delta W = RUE \times Q_{int} \times f(stress) \times rue\_factor$
4. **生物量分配**: 按物候期动态分配至各器官，支持阶段间插值

## 快速开始

### 安装

```bash
git clone https://github.com/Weiyifan/Crop_Model_Multi_Stages.git
cd Crop_Model_Multi_Stages
pip install -e .
```

### 基础用法

```python
from Crop_Model_Multi_Stages import CropParameters, SimpleCropModel, generate_weather

# 1. 使用预定义作物参数 (玉米、小麦、水稻)
params = CropParameters.maize()

# 2. 生成气象数据
weather = generate_weather(start_day=120, days=150)

# 3. 运行模拟
model = SimpleCropModel(params)
results = model.run(weather)

# 4. 查看结果
print(f"产量: {results['grain_yield']:.0f} g/m²")
print(f"生物量: {results['final_biomass']:.0f} g/m²")
print(f"收获指数: {results['harvest_index']:.2f}")
print(f"物候期转换次数: {len(results['stage_transitions'])}")
```

### 自定义多物候期

```python
from Crop_Model_Multi_Stages import CropParameters, PhenologyStage

# 定义6个物候期的玉米模型
stages = [
    PhenologyStage(
        name="播种-出苗",
        gdd_threshold=0,
        partition_leaf=0.70, partition_stem=0.20, 
        partition_root=0.10, partition_grain=0.00,
        lai_growth_rate=0.15, height_growth_rate=0.2
    ),
    PhenologyStage(
        name="苗期",
        gdd_threshold=100,
        partition_leaf=0.60, partition_stem=0.25,
        partition_root=0.15, partition_grain=0.00,
        lai_growth_rate=0.12, height_growth_rate=0.8
    ),
    PhenologyStage(
        name="拔节期",
        gdd_threshold=500,
        partition_leaf=0.40, partition_stem=0.35,
        partition_root=0.20, partition_grain=0.05,
        lai_growth_rate=0.15, height_growth_rate=1.5,
        rue_factor=1.1  # 提高10%的RUE
    ),
    PhenologyStage(
        name="抽雄开花期",
        gdd_threshold=900,
        partition_leaf=0.20, partition_stem=0.30,
        partition_root=0.15, partition_grain=0.35,
        lai_growth_rate=0.05, height_growth_rate=0.3,
        rue_factor=1.2  # 提高20%的RUE
    ),
    PhenologyStage(
        name="灌浆期",
        gdd_threshold=1300,
        partition_leaf=0.05, partition_stem=0.15,
        partition_root=0.10, partition_grain=0.70,
        lai_growth_rate=0.0, senescence_rate=0.015,
        rue_factor=1.1
    ),
    PhenologyStage(
        name="成熟期",
        gdd_threshold=1800,
        partition_leaf=0.00, partition_stem=0.00,
        partition_root=0.00, partition_grain=1.00,
        lai_growth_rate=0.0, senescence_rate=0.03,
        rue_factor=0.8
    )
]

# 创建作物参数
params = CropParameters(
    crop_name="Custom Maize",
    base_temp=8.0,
    max_gdd=1800,
    max_lai=5.5,
    rue_base=4.0,
    phenology_stages=stages
)
```

## PhenologyStage 参数说明

每个物候期可以配置以下参数：

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `name` | str | 必填 | 物候期名称 |
| `gdd_threshold` | float | 必填 | 进入该阶段所需GDD |
| `partition_leaf` | float | 0.5 | 叶分配系数 (0-1) |
| `partition_stem` | float | 0.3 | 茎分配系数 (0-1) |
| `partition_root` | float | 0.2 | 根分配系数 (0-1) |
| `partition_grain` | float | 0.0 | 籽粒分配系数 (0-1) |
| `lai_growth_rate` | float | 0.08 | LAI增长速率 |
| `rue_factor` | float | 1.0 | RUE乘数 |
| `height_growth_rate` | float | 0.5 | 株高增长速率 (cm/day) |
| `senescence_rate` | float | 0.0 | 叶片衰老速率 |
| `stress_factor` | float | 1.0 | 胁迫响应因子 |
| `custom_params` | dict | {} | 自定义参数字典 |

**注意**: 四个分配系数之和必须等于1.0

## 预定义作物参数

| 作物 | 物候期数 | 基础温度 | 成熟GDD | RUE | Max LAI |
|------|----------|----------|---------|-----|---------|
| 玉米 | 6 | 8°C | 1800 | 4.0 | 5.5 |
| 小麦 | 7 | 0°C | 1300 | 3.2 | 6.0 |
| 水稻 | 6 | 10°C | 1400 | 2.8 | 7.0 |

### 玉米物候期详细配置

| 物候期 | GDD阈值 | 叶分配 | 茎分配 | 根分配 | 籽粒分配 | RUE因子 |
|--------|---------|--------|--------|--------|----------|---------|
| 播种-出苗 | 0 | 0.70 | 0.20 | 0.10 | 0.00 | 1.0 |
| 苗期 | 100 | 0.60 | 0.25 | 0.15 | 0.00 | 1.0 |
| 拔节期 | 500 | 0.40 | 0.35 | 0.20 | 0.05 | 1.1 |
| 抽雄开花期 | 900 | 0.20 | 0.30 | 0.15 | 0.35 | 1.2 |
| 灌浆期 | 1300 | 0.05 | 0.15 | 0.10 | 0.70 | 1.1 |
| 成熟期 | 1800 | 0.00 | 0.00 | 0.00 | 1.00 | 0.8 |

## 项目结构

```plain
Crop_Model_Multi_Stages/
├── src/simple_crop_model/  # 核心源码
│   ├── __init__.py        # 包初始化
│   ├── core.py            # 模型类 (SimpleCropModel, AdvancedCropModel)
│   ├── parameters.py      # 作物参数和物候期定义
│   ├── weather.py         # 气象工具
│   └── utils.py           # 辅助函数
├── examples/              # 使用示例
│   ├── basic_usage.py     # 基础示例
│   ├── custom_stages.py   # 自定义物候期示例
│   └── multi_crop_comparison.py  # 多作物对比
├── tests/                 # 单元测试
└── docs/                  # 文档
```

## 高级功能

### 使用AdvancedCropModel

```python
from Crop_Model_Multi_Stages import AdvancedCropModel

# 高级模型支持源库关系和更多输出变量
config = {
    'output_variables': [
        'day', 'gdd', 'stage_name', 'lai', 'height',
        'total_biomass', 'grain', 'source_strength', 'sink_strength'
    ]
}

model = AdvancedCropModel(params, config=config)
results = model.run(weather)

# 查看源库关系
print(f"平均源强度: {results['avg_source_strength']:.2f}")
print(f"平均库强度: {results['avg_sink_strength']:.2f}")
```

### 获取物候期统计信息

```python
from Crop_Model_Multi_Stages import get_stage_statistics

stats = get_stage_statistics(results['daily_data'])
for stage_name, stage_info in stats.items():
    print(f"{stage_name}: {stage_info['duration_days']} 天, "
          f"平均LAI: {stage_info['avg_lai']:.2f}")
```

### 导出结果

```python
from Crop_Model_Multi_Stages import export_to_csv, save_results

# 导出逐日数据到CSV
export_to_csv(results, "simulation_results.csv")

# 保存完整结果到JSON
save_results(results, "simulation_results.json")
```

### 验证参数

```python
from Crop_Model_Multi_Stages import validate_parameters

errors = validate_parameters(params)
if errors:
    print("参数验证失败:")
    for error in errors:
        print(f"  - {error}")
else:
    print("参数验证通过!")
```

## 示例场景

### 1. 比较不同物候期配置的产量

```python
# 定义两个不同的物候期配置
stages_v1 = [...]  # 标准配置
stages_v2 = [...]  # 延长灌浆期

params1 = CropParameters(phenology_stages=stages_v1)
params2 = CropParameters(phenology_stages=stages_v2)

results1 = SimpleCropModel(params1).run(weather)
results2 = SimpleCropModel(params2).run(weather)

from Crop_Model_Multi_Stages import compare_scenarios
compare_scenarios([results1, results2], ["标准", "延长灌浆"])
```

### 2. 分析物候期转换时间

```python
results = model.run(weather, verbose=True)

# 查看物候期转换
for trans in results['stage_transitions']:
    print(f"Day {trans['day']}: {trans['from_stage']} → {trans['to_stage']}")
```

## API参考

### CropParameters

```python
class CropParameters:
    def __init__(
        self,
        base_temp: float = 10.0,          # 基础温度
        max_temp: float = 35.0,          # 最高有效温度
        max_gdd: float = 2000.0,         # 最大积温
        max_lai: float = 5.0,            # 最大LAI
        specific_leaf_area: float = 0.025,
        rue_base: float = 3.0,           # 基础RUE
        light_extinction: float = 0.6,
        phenology_stages: List[PhenologyStage] = None,
        crop_name: str = "Generic Crop"
    )
    
    # 类方法
    @classmethod
    def maize(cls) -> "CropParameters"     # 预定义玉米参数
    @classmethod
    def wheat(cls) -> "CropParameters"    # 预定义小麦参数
    @classmethod
    def rice(cls) -> "CropParameters"     # 预定义水稻参数
    
    # 实例方法
    def get_stage_by_gdd(self, gdd: float) -> PhenologyStage
    def get_stage_index(self, gdd: float) -> int
    def get_stage_progress(self, gdd: float) -> float
```

### Crop_Model_Multi_Stages

```python
class SimpleCropModel:
    def __init__(self, params: CropParameters = None)
    
    def step(self, tmin: float, tmax: float, solar_rad: float,
             water_stress: float = 1.0, nitrogen_stress: float = 1.0,
             **kwargs) -> Dict
             
    def run(self, weather_data: List[Dict], 
            verbose: bool = False) -> Dict
```

## 引用

如果你在工作中使用了本模型，请引用：

```plain
@software{Crop_Model_Multi_Stages,
  author = {Weiyifan},
  title = {Crop_Model_Multi_Stages: A Multi-Phenology Crop Growth Simulation Model},
  year = {2026},
  url = {https://github.com/Weiyifan/Crop_Model_Multi_Stages}
}
```

## 更新日志

### v0.2.0 (2026)
- 新增多物候期支持
- 物候期间平滑过渡
- 新增 PhenologyStage 类
- 新增 AdvancedCropModel 类
- 更新预定义作物参数

### v0.1.0
- 基础作物模型
- GDD驱动物候发育
- Beer-Lambert光截获

## 许可证

MIT License - 详见 LICENSE 文件
