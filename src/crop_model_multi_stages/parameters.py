"""
作物参数配置模块 - 集成多物候期系统
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .phenology import PhenologyConfig


@dataclass
class CropParameters:
    """
    作物参数配置类 - 支持多物候期
    
    包含作物基础生理参数和物候期配置
    
    Attributes:
        # 温度参数
        base_temp: 基础温度 (°C)，低于此温度不发育
        max_temp: 最高有效温度 (°C)，高于此温度按上限计算
        
        # 形态参数
        max_lai: 最大叶面积指数
        lai_growth_rate: 默认LAI增长速率 (可被各阶段覆盖)
        specific_leaf_area: 比叶面积 (m²/g)
        max_height: 最大株高 (cm)
        
        # 光合参数
        rue: 辐射利用效率 (g/MJ)
        light_extinction: 光 extinction coefficient
        
        # 物候期配置
        phenology: PhenologyConfig - 多物候期配置对象
        
        # 其他参数
        crop_name: 作物名称
        description: 描述信息
    """
    
    # 温度参数
    base_temp: float = 10.0
    max_temp: float = 35.0
    
    # 形态参数
    max_lai: float = 5.0
    lai_growth_rate: float = 0.08
    specific_leaf_area: float = 0.025
    max_height: float = 250.0
    
    # 光合参数
    rue: float = 3.0
    light_extinction: float = 0.6
    
    # 物候期配置
    phenology: PhenologyConfig = field(default_factory=PhenologyConfig)
    
    # 可选信息
    crop_name: str = "Generic Crop"
    description: str = ""
    
    def __post_init__(self):
        """验证参数有效性"""
        if self.base_temp >= self.max_temp:
            raise ValueError("base_temp must be less than max_temp")
        if self.max_lai <= 0:
            raise ValueError("max_lai must be positive")
        if self.rue <= 0:
            raise ValueError("rue must be positive")
    
    @property
    def mature_gdd(self) -> float:
        """获取成熟所需的总GDD"""
        return self.phenology.get_maturity_gdd()
    
    def get_stage_by_gdd(self, gdd: float):
        """根据GDD获取当前物候期"""
        return self.phenology.get_stage_by_gdd(gdd)
    
    @classmethod
    def maize(cls) -> "CropParameters":
        """预定义的玉米参数（6阶段物候期）"""
        return cls(
            crop_name="Maize",
            base_temp=8.0,
            max_temp=30.0,
            max_lai=5.5,
            lai_growth_rate=0.10,
            rue=4.0,
            light_extinction=0.65,
            max_height=280.0,
            phenology=PhenologyConfig.maize(),
            description="春玉米参数 - 6阶段物候期模型"
        )
    
    @classmethod
    def wheat(cls) -> "CropParameters":
        """预定义的冬小麦参数（7阶段物候期）"""
        return cls(
            crop_name="Wheat",
            base_temp=0.0,
            max_temp=30.0,
            max_lai=6.0,
            lai_growth_rate=0.09,
            rue=3.2,
            light_extinction=0.65,
            max_height=100.0,
            phenology=PhenologyConfig.wheat(),
            description="冬小麦参数 - 7阶段物候期模型"
        )
    
    @classmethod
    def rice(cls) -> "CropParameters":
        """预定义的水稻参数（6阶段物候期）"""
        return cls(
            crop_name="Rice",
            base_temp=10.0,
            max_temp=35.0,
            max_lai=7.0,
            lai_growth_rate=0.12,
            rue=2.8,
            light_extinction=0.55,
            max_height=110.0,
            phenology=PhenologyConfig.rice(),
            description="水稻参数 - 6阶段物候期模型"
        )
    
    @classmethod
    def soybean(cls) -> "CropParameters":
        """预定义的大豆参数（5阶段物候期）"""
        phenology = PhenologyConfig([
            # 使用 phenology.py 中定义的类
        ])
        # 动态导入避免循环引用
        from .phenology import PhenologyStage
        phenology = PhenologyConfig([
            PhenologyStage("播种-出苗", gdd_threshold=0,
                          partition_leaf=0.5, partition_stem=0.3,
                          partition_root=0.2, partition_grain=0.0),
            PhenologyStage("营养生长期", gdd_threshold=100,
                          partition_leaf=0.55, partition_stem=0.25,
                          partition_root=0.20, partition_grain=0.0,
                          lai_growth_rate=0.10),
            PhenologyStage("开花期", gdd_threshold=600,
                          partition_leaf=0.30, partition_stem=0.25,
                          partition_root=0.15, partition_grain=0.30,
                          lai_growth_rate=0.05),
            PhenologyStage("结荚期", gdd_threshold=1100,
                          partition_leaf=0.15, partition_stem=0.15,
                          partition_root=0.05, partition_grain=0.65,
                          lai_growth_rate=0.02, height_growth=False),
            PhenologyStage("成熟", gdd_threshold=1600,
                          partition_leaf=0.0, partition_stem=0.0,
                          partition_root=0.0, partition_grain=1.0,
                          lai_growth_rate=0.0, senescence_start=True,
                          height_growth=False)
        ])
        
        return cls(
            crop_name="Soybean",
            base_temp=10.0,
            max_temp=30.0,
            max_lai=6.0,
            lai_growth_rate=0.08,
            rue=3.0,
            light_extinction=0.60,
            max_height=80.0,
            phenology=phenology,
            description="大豆参数 - 5阶段物候期模型"
        )
