import json
from typing import Dict, List, Any


def save_results(results: Dict, filepath: str):
    """保存模拟结果到JSON"""
    # 处理numpy类型
    def convert(obj):
        if hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        return obj
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(convert(results), f, indent=2, ensure_ascii=False)


def print_summary(results: Dict):
    """打印模拟结果摘要"""
    print("=" * 60)
    print(f"作物: {results.get('crop_name', 'Unknown')}")
    print("=" * 60)
    print(f"总生物量: {results['final_biomass']:.0f} g/m² "
          f"({results['final_biomass']/100:.2f} t/ha)")
    print(f"籽粒产量: {results['grain_yield']:.0f} g/m² "
          f"({results['grain_yield']/100:.2f} t/ha)")
    print(f"收获指数: {results['harvest_index']*100:.1f}%")
    print(f"最大叶面积指数: {results['max_lai']:.2f}")
    print(f"生育期长度: {results['maturity_day']} 天")
    print(f"累计积温: {results['total_gdd']:.0f} °C·day")
    print("=" * 60)


def get_stage_transitions(daily_data: List[Dict]) -> List[tuple]:
    """获取生育期转换节点"""
    transitions = []
    if not daily_data:
        return transitions
        
    prev_stage = daily_data[0]['stage']
    for i, data in enumerate(daily_data):
        if data['stage'] != prev_stage:
            transitions.append((data['day'], prev_stage, data['stage']))
            prev_stage = data['stage']
    return transitions
