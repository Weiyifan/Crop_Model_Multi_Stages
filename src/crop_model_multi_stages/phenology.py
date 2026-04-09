"""
物候期配置模块 - 支持自定义多物候期
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class PhenologyStage:
    """
    单个物候期配置
    
    Attributes:
        name: 物候期名称 (如 "播种", "出苗", "开花", "成熟")
        gdd_threshold: 进入该阶段所需的累计积温 (GDD)
        duration_days: 预计持续天数 (可选，用于参考)
        
        # 生物量分配系数 (该阶段内)
        partition_leaf: 叶片分配系数 (0-1)
        partition_stem: 茎秆分配系数 (0-1)
        partition_root: 根系分配系数 (0-1)
        partition_grain: 籽粒分配系数 (0-1)
        
        # LAI 增长参数
        lai_growth_rate: LAI增长速率系数
        max_lai_factor: 相对最大LAI的比例 (0-1)
        
        # 其他物候特性
        height_growth: 株高是否增长 (bool)
        senescence_start: 是否开始衰老 (bool)
    """
    name: str
    gdd_threshold: float
    duration_days: Optional[int] = None
    
    # 生物量分配系数
    partition_leaf: float = 0.5
    partition_stem: float = 0.3
    partition_root: float = 0.2
    partition_grain: float = 0.0
    
    # LAI 参数
    lai_growth_rate: float = 0.08
    max_lai_factor: float = 1.0
    
    # 其他特性
    height_growth: bool = True
    senescence_start: bool = False
    
    def __post_init__(self):
        """验证参数有效性"""
        total_partition = (self.partition_leaf + self.partition_stem + 
                          self.partition_root + self.partition_grain)
        if not (0.99 <= total_partition <= 1.01):
            raise ValueError(
                f"物候期 '{self.name}' 的分配系数总和必须等于1.0，"
                f"当前为 {total_partition}"
            )
        
        for name, value in [
            ('partition_leaf', self.partition_leaf),
            ('partition_stem', self.partition_stem),
            ('partition_root', self.partition_root),
            ('partition_grain', self.partition_grain)
        ]:
            if not (0 <= value <= 1):
                raise ValueError(f"{name} 必须在 0-1 之间，当前为 {value}")
    
    def get_partition_coefficients(self) -> Dict[str, float]:
        """获取生物量分配系数字典"""
        return {
            'leaf': self.partition_leaf,
            'stem': self.partition_stem,
            'root': self.partition_root,
            'grain': self.partition_grain
        }


@dataclass
class PhenologyConfig:
    """
    多物候期配置管理器
    
    支持自定义物候期数量和参数，按GDD阈值排序
    
    Example:
        # 创建3阶段配置 (播种→开花→成熟)
        config = PhenologyConfig([
            PhenologyStage("营养生长期", gdd_threshold=0, 
                          partition_leaf=0.6, partition_stem=0.3, 
                          partition_root=0.1, partition_grain=0.0),
            PhenologyStage("开花期", gdd_threshold=800,
                          partition_leaf=0.3, partition_stem=0.3,
                          partition_root=0.1, partition_grain=0.3),
            PhenologyStage("成熟期", gdd_threshold=1600,
                          partition_leaf=0.0, partition_stem=0.0,
                          partition_root=0.0, partition_grain=1.0,
                          senescence_start=True)
        ])
        
        # 获取当前阶段
        current_stage = config.get_stage_by_gdd(850)  # 返回开花期
    """
    stages: List[PhenologyStage] = field(default_factory=list)
    
    def __post_init__(self):
        """验证并排序物候期"""
        if not self.stages:
            # 默认创建4阶段配置
            self.stages = self._default_stages()
        
        # 按 GDD 阈值排序
        self.stages.sort(key=lambda s: s.gdd_threshold)
        
        # 验证GDD阈值递增
        for i in range(1, len(self.stages)):
            if self.stages[i].gdd_threshold <= self.stages[i-1].gdd_threshold:
                raise ValueError(
                    f"物候期 '{self.stages[i].name}' 的GDD阈值 "
                    f"({self.stages[i].gdd_threshold}) 必须大于 "
                    f"'{self.stages[i-1].name}' 的阈值 "
                    f"({self.stages[i-1].gdd_threshold})"
                )
    
    @staticmethod
    def _default_stages() -> List[PhenologyStage]:
        """创建默认4阶段配置"""
        return [
            PhenologyStage(
                name="播种-出苗",
                gdd_threshold=0,
                partition_leaf=0.5,
                partition_stem=0.3,
                partition_root=0.2,
                partition_grain=0.0,
                lai_growth_rate=0.05,
                height_growth=True
            ),
            PhenologyStage(
                name="营养生长",
                gdd_threshold=100,
                partition_leaf=0.5,
                partition_stem=0.3,
                partition_root=0.2,
                partition_grain=0.0,
                lai_growth_rate=0.08,
                max_lai_factor=0.8,
                height_growth=True
            ),
            PhenologyStage(
                name="生殖生长",
                gdd_threshold=800,
                partition_leaf=0.3,
                partition_stem=0.2,
                partition_root=0.0,
                partition_grain=0.5,
                lai_growth_rate=0.02,
                max_lai_factor=1.0,
                height_growth=False
            ),
            PhenologyStage(
                name="成熟",
                gdd_threshold=1600,
                partition_leaf=0.0,
                partition_stem=0.0,
                partition_root=0.0,
                partition_grain=1.0,
                lai_growth_rate=0.0,
                max_lai_factor=0.3,
                height_growth=False,
                senescence_start=True
            )
        ]
    
    def get_stage_by_gdd(self, gdd: float) -> PhenologyStage:
        """
        根据累计GDD获取当前物候期
        
        Args:
            gdd: 累计生长度日
            
        Returns:
            当前物候期配置
        """
        current_stage = self.stages[0]
        for stage in self.stages:
            if gdd >= stage.gdd_threshold:
                current_stage = stage
            else:
                break
        return current_stage
    
    def get_stage_index(self, gdd: float) -> int:
        """获取当前物候期的索引"""
        for i, stage in enumerate(self.stages):
            if gdd < stage.gdd_threshold:
                return max(0, i - 1)
        return len(self.stages) - 1
    
    def get_stage_by_name(self, name: str) -> Optional[PhenologyStage]:
        """根据名称获取物候期"""
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None
    
    def get_stage_names(self) -> List[str]:
        """获取所有物候期名称列表"""
        return [stage.name for stage in self.stages]
    
    def get_maturity_gdd(self) -> float:
        """获取成熟所需的总GDD"""
        return self.stages[-1].gdd_threshold
    
    def add_stage(self, stage: PhenologyStage):
        """添加新的物候期（会自动重新排序）"""
        self.stages.append(stage)
        self.stages.sort(key=lambda s: s.gdd_threshold)
        self.__post_init__()  # 重新验证
    
    def remove_stage(self, name: str):
        """移除指定名称的物候期"""
        self.stages = [s for s in self.stages if s.name != name]
        if not self.stages:
            raise ValueError("至少需要保留一个物候期")
    
    def __len__(self) -> int:
        return len(self.stages)
    
    def __iter__(self):
        return iter(self.stages)
    
    @classmethod
    def maize(cls) -> "PhenologyConfig":
        """预定义的玉米物候期配置（6阶段）"""
        return cls([
            PhenologyStage("播种-出苗", gdd_threshold=0,
                          partition_leaf=0.5, partition_stem=0.3,
                          partition_root=0.2, partition_grain=0.0,
                          lai_growth_rate=0.05),
            PhenologyStage("苗期", gdd_threshold=80,
                          partition_leaf=0.55, partition_stem=0.25,
                          partition_root=0.20, partition_grain=0.0,
                          lai_growth_rate=0.10),
            PhenologyStage("拔节期", gdd_threshold=400,
                          partition_leaf=0.50, partition_stem=0.30,
                          partition_root=0.20, partition_grain=0.0,
                          lai_growth_rate=0.12),
            PhenologyStage("大喇叭口期", gdd_threshold=800,
                          partition_leaf=0.40, partition_stem=0.35,
                          partition_root=0.15, partition_grain=0.10,
                          lai_growth_rate=0.08),
            PhenologyStage("抽雄-开花", gdd_threshold=1200,
                          partition_leaf=0.20, partition_stem=0.20,
                          partition_root=0.05, partition_grain=0.55,
                          lai_growth_rate=0.03, height_growth=False),
            PhenologyStage("灌浆-成熟", gdd_threshold=2000,
                          partition_leaf=0.0, partition_stem=0.0,
                          partition_root=0.0, partition_grain=1.0,
                          lai_growth_rate=0.0, senescence_start=True,
                          height_growth=False)
        ])
    
    @classmethod
    def wheat(cls) -> "PhenologyConfig":
        """预定义的冬小麦物候期配置（7阶段）"""
        return cls([
            PhenologyStage("播种-出苗", gdd_threshold=0,
                          partition_leaf=0.4, partition_stem=0.3,
                          partition_root=0.3, partition_grain=0.0),
            PhenologyStage("分蘖期", gdd_threshold=150,
                          partition_leaf=0.5, partition_stem=0.25,
                          partition_root=0.25, partition_grain=0.0,
                          lai_growth_rate=0.10),
            PhenologyStage("越冬期", gdd_threshold=300,
                          partition_leaf=0.3, partition_stem=0.3,
                          partition_root=0.4, partition_grain=0.0,
                          lai_growth_rate=0.01),
            PhenologyStage("返青-拔节", gdd_threshold=500,
                          partition_leaf=0.55, partition_stem=0.25,
                          partition_root=0.20, partition_grain=0.0,
                          lai_growth_rate=0.12),
            PhenologyStage("抽穗期", gdd_threshold=800,
                          partition_leaf=0.40, partition_stem=0.30,
                          partition_root=0.10, partition_grain=0.20,
                          lai_growth_rate=0.05),
            PhenologyStage("开花-灌浆", gdd_threshold=1100,
                          partition_leaf=0.20, partition_stem=0.20,
                          partition_root=0.05, partition_grain=0.55,
                          lai_growth_rate=0.02, height_growth=False),
            PhenologyStage("成熟", gdd_threshold=1600,
                          partition_leaf=0.0, partition_stem=0.0,
                          partition_root=0.0, partition_grain=1.0,
                          lai_growth_rate=0.0, senescence_start=True,
                          height_growth=False)
        ])
    
    @classmethod
    def rice(cls) -> "PhenologyConfig":
        """预定义的水稻物候期配置（6阶段）"""
        return cls([
            PhenologyStage("播种-出苗", gdd_threshold=0,
                          partition_leaf=0.45, partition_stem=0.30,
                          partition_root=0.25, partition_grain=0.0),
            PhenologyStage("分蘖期", gdd_threshold=100,
                          partition_leaf=0.50, partition_stem=0.25,
                          partition_root=0.25, partition_grain=0.0,
                          lai_growth_rate=0.12),
            PhenologyStage("拔节期", gdd_threshold=400,
                          partition_leaf=0.45, partition_stem=0.30,
                          partition_root=0.25, partition_grain=0.0,
                          lai_growth_rate=0.10),
            PhenologyStage("孕穗期", gdd_threshold=700,
                          partition_leaf=0.35, partition_stem=0.30,
                          partition_root=0.15, partition_grain=0.20,
                          lai_growth_rate=0.06),
            PhenologyStage("抽穗-开花", gdd_threshold=900,
                          partition_leaf=0.20, partition_stem=0.20,
                          partition_root=0.05, partition_grain=0.55,
                          lai_growth_rate=0.02, height_growth=False),
            PhenologyStage("灌浆-成熟", gdd_threshold=1800,
                          partition_leaf=0.0, partition_stem=0.0,
                          partition_root=0.0, partition_grain=1.0,
                          lai_growth_rate=0.0, senescence_start=True,
                          height_growth=False)
        ])
