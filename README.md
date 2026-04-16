# Crop_Model_Multi_Stages

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于生理过程的多物候期作物生长模拟模型，支持自定义基于积温量物候期数量和对应物候期的参数配置，适用于产量预测、气候变化影响评估和环控措施优化。

## 模型特点

- **多物候期支持**: 可配置任意数量的物候期，每个阶段独立设置参数
- **积温驱动**: 基于Growing Degree Days (GDD)的物候发育模型
- **光截获模拟**: Beer-Lambert定律计算冠层光截获
- **动态生物量分配**: 各物候期可配置不同的器官分配系数
- **胁迫响应**: 模拟水分和温度胁迫的影响
- **模块化设计**: 易于扩展和参数校准

## 核心方程

1. **积温计算**: $GDD = \max(0, T_{avg} - T_{base})$
2. **光截获**: $Q_{int} = Q_{total} \times (1 - e^{-k \times LAI})$
3. **生物量增长**: $\Delta W = RUE \times Q_{int} \times f(stress)$
4. **物候期判断**: 基于累计GDD自动判断当前物候期

## 快速开始

### 安装

```bash
git clone https://github.com/Weiyifan/Crop_Model_Multi_Stages.git
cd Crop_Model_Multi_Stages
pip install -e .
```

### 基础用法

```python
from crop_model_multi_stages import CropParameters, CropModel, generate_weather

# 1. 使用预定义作物参数 (玉米、小麦、水稻等)
params = CropParameters.maize()  # 6阶段物候期
print(f"作物: {params.crop_name}")
print(f"物候期数量: {len(params.phenology)}")
print(f"物候期列表: {params.phenology.get_stage_names()}")

# 2. 生成气象数据
weather = generate_weather(start_day=120, days=180)

# 3. 运行模拟
model = CropModel(params)
results = model.run(weather, verbose=True)

# 4. 查看结果
print(f"产量: {results['grain_yield']:.0f} g/m²")
print(f"生物量: {results['final_biomass']:.0f} g/m²")
print(f"收获指数: {results['harvest_index']:.2f}")

# 5. 查看物候期信息
for stage_name, info in results['stage_info'].items():
    print(f"{stage_name}: {info['days']}天 (GDD: {info['start_gdd']:.0f}-{info['end_gdd']:.0f})")
```

### 自定义物候期配置

```python
from crop_model_multi_stages import PhenologyStage, PhenologyConfig, CropParameters, CropModel

# 创建自定义5阶段物候期配置
phenology = PhenologyConfig([
    PhenologyStage(
        name="播种-出苗",
        gdd_threshold=0,
        partition_leaf=0.5, partition_stem=0.3,
        partition_root=0.2, partition_grain=0.0,
        lai_growth_rate=0.05
    ),
    PhenologyStage(
        name="营养生长期",
        gdd_threshold=100,
        partition_leaf=0.55, partition_stem=0.25,
        partition_root=0.20, partition_grain=0.0,
        lai_growth_rate=0.10
    ),
    PhenologyStage(
        name="开花期",
        gdd_threshold=600,
        partition_leaf=0.30, partition_stem=0.25,
        partition_root=0.15, partition_grain=0.30,
        lai_growth_rate=0.05
    ),
    PhenologyStage(
        name="灌浆期",
        gdd_threshold=1100,
        partition_leaf=0.15, partition_stem=0.15,
        partition_root=0.05, partition_grain=0.65,
        lai_growth_rate=0.02, height_growth=False
    ),
    PhenologyStage(
        name="成熟",
        gdd_threshold=1600,
        partition_leaf=0.0, partition_stem=0.0,
        partition_root=0.0, partition_grain=1.0,
        lai_growth_rate=0.0, senescence_start=True,
        height_growth=False
    )
])

# 创建作物参数
custom_params = CropParameters(
    crop_name="Custom Soybean",
    base_temp=10.0,
    max_lai=6.0,
    rue=3.0,
    phenology=phenology
)

# 运行模拟
model = CropModel(custom_params)
results = model.run(weather)
```

### 预定义作物物候期配置

| 作物 | 物候期数 | 基础温度 | RUE | Max LAI |
|------|---------|---------|-----|---------|
| 玉米 (Maize) | 6 | 8°C | 4.0 | 5.5 |
| 小麦 (Wheat) | 7 | 0°C | 3.2 | 6.0 |
| 水稻 (Rice) | 6 | 10°C | 2.8 | 7.0 |
| 大豆 (Soybean) | 5 | 10°C | 3.0 | 6.0 |

#### 玉米物候期配置详情 (6阶段)

```
1. 播种-出苗 (GDD: 0)
2. 苗期 (GDD: 80)
3. 拔节期 (GDD: 400)
4. 大喇叭口期 (GDD: 800)
5. 抽雄-开花 (GDD: 1200)
6. 灌浆-成熟 (GDD: 2000)
```

#### 小麦物候期配置详情 (7阶段)

```
1. 播种-出苗 (GDD: 0)
2. 分蘖期 (GDD: 150)
3. 越冬期 (GDD: 300)
4. 返青-拔节 (GDD: 500)
5. 抽穗期 (GDD: 800)
6. 开花-灌浆 (GDD: 1100)
7. 成熟 (GDD: 1600)
```

## PhenologyStage 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | str | 物候期名称 |
| `gdd_threshold` | float | 进入该阶段的GDD阈值 |
| `partition_leaf` | float | 叶片分配系数 (0-1) |
| `partition_stem` | float | 茎秆分配系数 (0-1) |
| `partition_root` | float | 根系分配系数 (0-1) |
| `partition_grain` | float | 籽粒分配系数 (0-1) |
| `lai_growth_rate` | float | LAI增长速率 |
| `max_lai_factor` | float | 最大LAI比例 (0-1) |
| `height_growth` | bool | 是否增长株高 |
| `senescence_start` | bool | 是否开始衰老 |

## 加载人工设定天气数据

本文档介绍如何使用 `WeatherDataLoader` 从 CSV 文件或 DataFrame 加载人工设定的天气数据。

### 数据格式要求

#### 必需字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `day` | int | 年积日（一年中的第几天） |
| `tmin` | float | 每日最低温度（°C） |
| `tmax` | float | 每日最高温度（°C） |
| `solar_rad` | float | 太阳辐射（MJ/m²） |

#### 可选字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `rain` | float | 降雨量，用于计算水分胁迫系数 |

### 加载实际天气使用方法

```python
from crop_model_multi_stages import WeatherDataLoader, CropModel, CropParameters

# 从 CSV 文件加载
weather = WeatherDataLoader.from_csv('weather_data.csv')

# 从 DataFrame 加载
import pandas as pd
df = pd.DataFrame({
    'day': range(1, 31),
    'tmin': [5 + i*0.1 for i in range(30)],
    'tmax': [15 + i*0.2 for i in range(30)],
    'solar_rad': [10 + 5*(i%7)/7 for i in range(30)],
    'rain': [2.0 if i % 5 == 0 else 0.0 for i in range(30)]
})
weather = WeatherDataLoader.from_dataframe(df)

# 运行模拟
crop = CropModel(CropParameters.maize())
results = crop.run(weather)
```

### 自定义列名

```python
weather = WeatherDataLoader.from_csv(
    'weather_data.csv',
    day_col='doy',
    tmin_col='temp_min',
    tmax_col='temp_max',
    rad_col='radiation',
    rain_col='precipitation'
)
```

## 项目结构

```
Crop_Model_Multi_Stages/
├── src/crop_model_multi_stages/  # 核心源码
│   ├── __init__.py              # 包初始化
│   ├── phenology.py             # 多物候期配置
│   ├── parameters.py            # 作物参数
│   ├── core.py                  # 模型核心
│   ├── weather.py               # 气象工具
│   └── utils.py                 # 辅助函数
├── examples/                     # 使用示例
│   ├── basic_usage.py           # 基础示例
│   ├── multi_stage_demo.py      # 多物候期演示
│   ├── maize_simulation.py      # 玉米多场景对比
│   └── custom_phenology.py      # 自定义物候期示例
├── tests/                        # 单元测试
└── docs/                         # 文档
```

## 示例场景

### 1. 不同物候期配置产量对比
运行 `examples/multi_stage_demo.py` 查看不同物候期数量配置对产量的影响。

### 2. 不同播期产量比较
运行 `examples/maize_simulation.py` 查看不同播期对玉米产量和发育的影响。

### 3. 自定义物候期
运行 `examples/custom_phenology.py` 学习如何创建和使用自定义物候期配置。

## 从单物候期版本迁移

如果之前使用 `Zero_to_One_CropModel` (单物候期版本)，迁移步骤如下：

### API 变化

| 旧版本 | 新版本 | 说明 |
|--------|--------|------|
| `SimpleCropModel` | `CropModel` | 统一使用 CropModel |
| `OptimizedCropModel` | `CropModel` | 功能已合并 |
| `CropParameters(flower_gdd=...)` | `PhenologyConfig([...])` | 使用物候期配置对象 |
| `params.flower_gdd` | `params.phenology.get_stage_by_name(...)` | 通过物候期名称访问 |

### 迁移示例

```python
# 旧版本 (单物候期)
from simple_crop_model import CropParameters, SimpleCropModel

params = CropParameters(
    crop_name="Maize",
    flower_gdd=1200,
    mature_gdd=2400,
    partition_leaf=[0.45, 0.15, 0.0],
    partition_grain=[0.0, 0.50, 1.0]
)

# 新版本 (多物候期)
from crop_model_multi_stages import CropParameters, CropModel

# 方式1: 使用预定义配置
params = CropParameters.maize()  # 6阶段物候期

# 方式2: 自定义物候期配置
from crop_model_multi_stages import PhenologyConfig, PhenologyStage

phenology = PhenologyConfig([
    PhenologyStage("营养期", gdd_threshold=0, ...),
    PhenologyStage("开花期", gdd_threshold=1200, ...),
    PhenologyStage("成熟期", gdd_threshold=2400, ...)
])

params = CropParameters(
    crop_name="Maize",
    phenology=phenology
)

model = CropModel(params)
```

## 引用

如果你在工作中使用了本模型，请引用：

```plain
@software{crop_model_multi_stages,
  author = {Weiyifan},
  title = {Crop_Model_Multi_Stages: A Multi-Stage Phenology Crop Growth Simulation Model},
  year = {2026},
  url = {https://github.com/Weiyifan/Crop_Model_Multi_Stages}
}
```

## 许可证

MIT License - 详见 LICENSE 文件
