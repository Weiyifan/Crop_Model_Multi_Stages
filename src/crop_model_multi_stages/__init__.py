"""
Crop_Model_Multi_Stages - 多物候期作物生长模拟模型

该模型实现了：
- 自定义多物候期配置
- 积温(GDD)驱动的物候发育
- Beer-Lambert光截获定律
- 动态生物量分配
- 环境胁迫响应（通过系数折算）
"""

__version__ = "1.0.0"
__author__ = "Wei Yifan"
__email__ = "silence.63@163.com"

from .phenology import PhenologyStage, PhenologyConfig
from .parameters import CropParameters
from .core import CropModel
from .weather import generate_weather, WeatherDataLoader

__all__ = [
    "PhenologyStage",
    "PhenologyConfig",
    "CropParameters",
    "CropModel",
    "generate_weather",
    "WeatherDataLoader"
]
