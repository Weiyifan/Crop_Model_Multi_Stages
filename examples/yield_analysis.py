"""
产量敏感性分析 - 测试不同参数对产量的影响
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import matplotlib.pyplot as plt
from simple_crop_model import CropParameters, OptimizedCropModel, generate_weather

def sensitivity_analysis():
    """分析RUE和Max LAI对产量的敏感性"""
    base_weather = generate_weather(start_day=120, days=180, seed=42)
    
    # 参数范围
    rue_values = np.linspace(2.5, 4.5, 9)
    lai_values = np.linspace(4.0, 7.0, 9)
    
    yields = np.zeros((len(rue_values), len(lai_values)))
    
    print("正在进行敏感性分析...")
    for i, rue in enumerate(rue_values):
        for j, max_lai in enumerate(lai_values):
            params = CropParameters(
                base_temp=8.0,
                flower_gdd=1200,
                mature_gdd=2400,
                max_lai=max_lai,
                rue=rue
            )
            model = OptimizedCropModel(params)
            results = model.run(base_weather)
            yields[i, j] = results['grain_yield'] / 100  # 转换为t/ha
    
    # 绘制热力图
    plt.figure(figsize=(10, 8))
    X, Y = np.meshgrid(lai_values, rue_values)
    contour = plt.contourf(X, Y, yields, levels=20, cmap='YlOrRd')
    plt.colorbar(contour, label='Grain Yield (t/ha)')
    plt.contour(X, Y, yields, levels=10, colors='black', alpha=0.3, linewidths=0.5)
    
    plt.xlabel('Maximum LAI')
    plt.ylabel('Radiation Use Efficiency (RUE, g/MJ)')
    plt.title('Yield Response to RUE and Maximum LAI')
    plt.grid(True, alpha=0.3)
    
    plt.savefig('sensitivity_analysis.png', dpi=150)
    print("敏感性分析图表已保存")
    plt.show()

if __name__ == "__main__":
    sensitivity_analysis()
