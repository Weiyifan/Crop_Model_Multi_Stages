import numpy as np
from typing import List, Dict, Optional
import pandas as pd


def generate_weather(start_day: int = 1, days: int = 150,
                    base_temp: float = 15.0, temp_amp: float = 10.0,
                    base_rad: float = 20.0, rad_var: float = 5.0,
                    rain_prob: float = 0.3, seed: int = 42) -> List[Dict]:
    """
    生成简化的天气数据用于模拟测试
    
    Args:
        start_day: 起始年积日
        days: 模拟天数
        base_temp: 基础温度 (°C)
        temp_amp: 温度振幅 (°C)
        base_rad: 基础辐射 (MJ/m²)
        rad_var: 辐射变异
        rain_prob: 降雨概率
        seed: 随机种子
        
    Returns:
        每日气象数据字典列表
    """
    np.random.seed(seed)
    weather = []
    
    for d in range(start_day, start_day + days):
        # 季节性温度变化 + 随机波动
        seasonal_temp = base_temp + 10 * np.sin(2 * np.pi * d / 365 - np.pi/2)
        tmax = seasonal_temp + temp_amp/2 + np.random.normal(0, 2)
        tmin = seasonal_temp - temp_amp/2 + np.random.normal(0, 2)
        
        # 辐射 (受云量影响)
        cloud = np.random.random()
        solar_rad = max(5, base_rad + rad_var * np.sin(2 * np.pi * d / 365) - 15 * cloud)
        
        # 水分胁迫 (随机干旱事件)
        water_stress = 1.0
        if np.random.random() < rain_prob:
            # 降雨，无胁迫
            water_stress = 1.0
        elif np.random.random() < 0.1:  # 10%概率干旱
            water_stress = np.random.uniform(0.6, 0.9)
        
        weather.append({
            'day': d,
            'tmin': tmin,
            'tmax': tmax,
            'solar_rad': solar_rad,
            'water_stress': water_stress,
            'nitrogen_stress': 1.0
        })
    
    return weather


class WeatherDataLoader:
    """气象数据加载器，支持CSV和DataFrame"""
    
    @staticmethod
    def from_dataframe(df: pd.DataFrame, 
                      day_col: str = 'day',
                      tmin_col: str = 'tmin',
                      tmax_col: str = 'tmax',
                      rad_col: str = 'solar_rad',
                      rain_col: Optional[str] = None) -> List[Dict]:
        """
        从DataFrame加载天气数据
        
        Args:
            df: 包含气象数据的DataFrame
            day_col: 日期列名
            tmin_col: 最低温度列名
            tmax_col: 最高温度列名
            rad_col: 辐射列名
            rain_col: 降雨列名 (可选，用于计算水分胁迫)
            
        Returns:
            标准格式的气象数据列表
        """
        required_cols = [day_col, tmin_col, tmax_col, rad_col]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        weather = []
        for _, row in df.iterrows():
            water_stress = 1.0
            if rain_col and row[rain_col] > 0:
                # 简单的水分胁迫计算：无雨时降低
                pass  # 保持1.0
            elif rain_col and row[rain_col] == 0:
                water_stress = 0.9  # 轻度胁迫
                
            weather.append({
                'day': int(row[day_col]),
                'tmin': float(row[tmin_col]),
                'tmax': float(row[tmax_col]),
                'solar_rad': float(row[rad_col]),
                'water_stress': water_stress,
                'nitrogen_stress': 1.0
            })
        
        return weather
    
    @staticmethod
    def from_csv(filepath: str, **kwargs) -> List[Dict]:
        """从CSV文件加载"""
        df = pd.read_csv(filepath)
        return WeatherDataLoader.from_dataframe(df, **kwargs)
