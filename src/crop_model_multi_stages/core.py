"""
多物候期作物生长模型核心模块
"""

import numpy as np
from typing import List, Dict, Optional
from .parameters import CropParameters


class CropModel:
    """
    多物候期作物生长模型
    
    基于积温驱动的物候发育，支持自定义物候期数量和参数
    结合Beer-Lambert光截获定律和动态生物量分配
    
    Example:
        >>> from crop_model_multi_stages import CropParameters, CropModel, generate_weather
        >>> params = CropParameters.maize()  # 6阶段物候期
        >>> model = CropModel(params)
        >>> weather = generate_weather(days=150)
        >>> results = model.run(weather)
    """
    
    def __init__(self, params: Optional[CropParameters] = None):
        self.params = params or CropParameters()
        self.reset()
    
    def reset(self):
        """重置模型状态到初始值"""
        self.day = 0
        self.gdd = 0.0  # Growing Degree Days累计
        self.biomass_total = 0.0
        self.biomass_leaf = 0.0
        self.biomass_stem = 0.0
        self.biomass_root = 0.0
        self.biomass_grain = 0.0
        self.lai = 0.0  # Leaf Area Index
        self.height = 5.0  # 株高 cm
        self.stage_name = ""
        self.stage_index = 0
        self.current_stage = None
        self.daily_data: List[Dict] = []
        
        # 初始化物候期
        self._update_current_stage()
    
    def _update_current_stage(self):
        """更新当前物候期状态"""
        self.current_stage = self.params.get_stage_by_gdd(self.gdd)
        self.stage_name = self.current_stage.name
        self.stage_index = self.params.phenology.get_stage_index(self.gdd)
    
    def calculate_gdd(self, tmin: float, tmax: float) -> float:
        """
        计算每日生长度日 (GDD)
        
        GDD = max(0, min(Tavg, Tmax_limit) - Tbase)
        
        Args:
            tmin: 日最低温度 (°C)
            tmax: 日最高温度 (°C)
            
        Returns:
            当日GDD值
        """
        tavg = (tmin + tmax) / 2
        tavg = min(tavg, self.params.max_temp)
        return max(0.0, tavg - self.params.base_temp)
    
    def calculate_photosynthesis(self, solar_rad: float) -> float:
        """
        计算日同化量 (基于Monteith方程)
        
        使用Beer-Lambert定律计算光截获:
        Q_intercepted = Q_total * (1 - exp(-k * LAI))
        
        生物量增长:
        ΔW = RUE * Q_intercepted
        
        Args:
            solar_rad: 日总辐射 (MJ/m²/day)
            
        Returns:
            潜在生物量增长 (g/m²/day)
        """
        intercepted_rad = solar_rad * (
            1 - np.exp(-self.params.light_extinction * self.lai)
        )
        return self.params.rue * intercepted_rad
    
    def update_lai(self, daily_growth: float = 0):
        """
        更新叶面积指数
        
        根据当前物候期特性更新LAI
        """
        if not self.current_stage:
            return
        
        # 基于物候期配置计算LAI增长
        if self.day == 1:
            self.lai = 0.1
        else:
            # 使用当前阶段的LAI增长速率和最大LAI因子
            growth_rate = self.current_stage.lai_growth_rate
            max_lai_stage = self.params.max_lai * self.current_stage.max_lai_factor
            
            if self.current_stage.senescence_start:
                # 衰老期 - LAI下降
                senescence_rate = 0.02
                self.lai *= (1 - senescence_rate)
            elif self.lai < max_lai_stage:
                # 增长期 - 逻辑斯蒂增长
                if self.lai > 0:
                    growth_factor = (1 - self.lai / max_lai_stage) * growth_rate
                    self.lai += self.lai * growth_factor + 0.001 * daily_growth
                else:
                    self.lai = 0.1
            
            # 根据叶片生物量修正LAI
            if self.biomass_leaf > 0 and self.params.specific_leaf_area > 0:
                lai_from_biomass = self.biomass_leaf * self.params.specific_leaf_area
                # 平滑过渡
                self.lai = 0.7 * self.lai + 0.3 * lai_from_biomass
            
            # 边界限制
            self.lai = max(0.1, min(self.lai, self.params.max_lai))
    
    def update_height(self, water_stress: float = 1.0):
        """
        更新株高
        
        基于当前物候期特性更新株高
        """
        if not self.current_stage:
            return
        
        if self.current_stage.height_growth and self.height < self.params.max_height:
            # 株高增长
            growth_rate = 0.5 * np.sqrt(water_stress)
            self.height += growth_rate
            self.height = min(self.height, self.params.max_height)
    
    def step(self, tmin: float, tmax: float, solar_rad: float,
             water_stress: float = 1.0, nitrogen_stress: float = 1.0,
             **kwargs) -> Dict:
        """
        执行单步模拟 (一天)
        
        Args:
            tmin: 最低温度 (°C)
            tmax: 最高温度 (°C)
            solar_rad: 太阳辐射 (MJ/m²)
            water_stress: 水分胁迫因子 (0-1)
            nitrogen_stress: 氮素胁迫因子 (0-1)
            
        Returns:
            当日状态字典
        """
        self.day += 1
        
        # 1. 计算积温
        daily_gdd = self.calculate_gdd(tmin, tmax)
        self.gdd += daily_gdd
        
        # 2. 更新物候期
        prev_stage = self.stage_name
        self._update_current_stage()
        
        # 检测物候期转换
        stage_changed = (prev_stage != self.stage_name and prev_stage != "")
        
        # 3. 光合作用
        potential_biomass = self.calculate_photosynthesis(solar_rad)
        
        # 4. 胁迫计算
        stress_factor = min(water_stress, nitrogen_stress)
        
        # 温度胁迫 (高温抑制光合)
        if tmax > 35:
            heat_stress = max(0, 1 - (tmax - 35) * 0.05)
            stress_factor *= heat_stress
        
        actual_biomass = potential_biomass * stress_factor
        
        # 5. 生物量分配 (使用当前物候期的分配系数)
        partition = self.current_stage.get_partition_coefficients()
        
        self.biomass_leaf += actual_biomass * partition['leaf']
        self.biomass_stem += actual_biomass * partition['stem']
        self.biomass_root += actual_biomass * partition['root']
        self.biomass_grain += actual_biomass * partition['grain']
        
        # 衰老导致的叶片损失
        if self.current_stage.senescence_start and self.biomass_leaf > 0:
            senescence_loss = self.biomass_leaf * 0.01
            self.biomass_leaf -= senescence_loss
        
        self.biomass_total = (
            self.biomass_leaf + self.biomass_stem + 
            self.biomass_root + self.biomass_grain
        )
        
        # 6. 更新LAI
        self.update_lai(actual_biomass)
        
        # 7. 更新株高
        self.update_height(water_stress)
        
        # 记录数据
        daily_record = {
            'day': self.day,
            'doy': kwargs.get('doy', self.day),
            'gdd': self.gdd,
            'stage': self.stage_name,
            'stage_index': self.stage_index,
            'stage_changed': stage_changed,
            'lai': self.lai,
            'height': self.height,
            'total_biomass': self.biomass_total,
            'leaf': self.biomass_leaf,
            'stem': self.biomass_stem,
            'root': self.biomass_root,
            'grain': self.biomass_grain,
            'daily_growth': actual_biomass,
            'stress': stress_factor,
            'water_stress': water_stress,
            'nitrogen_stress': nitrogen_stress,
        }
        self.daily_data.append(daily_record)
        return daily_record
    
    def run(self, weather_data: List[Dict], verbose: bool = False) -> Dict:
        """
        运行完整生育期模拟
        
        Args:
            weather_data: 气象数据列表
            verbose: 是否打印进度信息
            
        Returns:
            包含最终生物量、产量、逐日数据的字典
        """
        self.reset()
        
        for i, weather in enumerate(weather_data):
            result = self.step(
                tmin=weather['tmin'],
                tmax=weather['tmax'],
                solar_rad=weather['solar_rad'],
                water_stress=weather.get('water_stress', 1.0),
                nitrogen_stress=weather.get('nitrogen_stress', 1.0),
                doy=weather.get('day', i+1)
            )
            
            # 打印物候期转换信息
            if verbose and result['stage_changed']:
                print(f"第{self.day}天: 进入 {self.stage_name} 阶段 (GDD={self.gdd:.1f})")
            
            # 检查成熟
            if self.gdd >= self.params.mature_gdd:
                if verbose:
                    print(f"作物于第{self.day}天成熟 (GDD={self.gdd:.1f})")
                break
        
        return self._compile_results()
    
    def _compile_results(self) -> Dict:
        """编译最终输出结果"""
        if not self.daily_data:
            raise RuntimeError("模型尚未运行，请先调用run()")
        
        # 统计物候期信息
        stage_info = {}
        for data in self.daily_data:
            stage = data['stage']
            if stage not in stage_info:
                stage_info[stage] = {
                    'start_day': data['day'],
                    'start_gdd': data['gdd'],
                    'days': 0
                }
            stage_info[stage]['end_day'] = data['day']
            stage_info[stage]['end_gdd'] = data['gdd']
            stage_info[stage]['days'] += 1
        
        return {
            'crop_name': self.params.crop_name,
            'stage_count': len(self.params.phenology),
            'stages': self.params.phenology.get_stage_names(),
            'stage_info': stage_info,
            'final_biomass': self.biomass_total,
            'grain_yield': self.biomass_grain,
            'harvest_index': self.biomass_grain / self.biomass_total if self.biomass_total > 0 else 0,
            'max_lai': max([d['lai'] for d in self.daily_data]),
            'maturity_day': self.day,
            'total_gdd': self.gdd,
            'daily_data': self.daily_data
        }
    
    def get_stage_transitions(self) -> List[Dict]:
        """获取物候期转换事件列表"""
        transitions = []
        prev_stage = None
        
        for data in self.daily_data:
            if data['stage_changed'] and prev_stage is not None:
                transitions.append({
                    'day': data['day'],
                    'from_stage': prev_stage,
                    'to_stage': data['stage'],
                    'gdd': data['gdd']
                })
            prev_stage = data['stage']
        
        return transitions


# 为了向后兼容，保留别名
SimpleCropModel = CropModel
OptimizedCropModel = CropModel
