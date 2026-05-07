import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def analyze_treatment_areas():
    """
    分析有数据的创新药.xlsx中不同治疗领域的药品数量分布
    """
    try:
        # 读取有数据的创新药.xlsx文件
        df = pd.read_excel('c:\\偷偷用用AI\\有数据的创新药.xlsx')
        print(f"文件行数: {len(df)}")
        print(f"列名: {df.columns.tolist()}")
        
        # 显示前几行数据
        print(f"\n前5行数据:")
        print(df.head())
        
        # 分析治疗领域分布
        if '治疗领域' in df.columns:
            treatment_area_col = '治疗领域'
        else:
            # 查找包含"治疗"或"领域"的列
            treatment_area_col = None
            for col in df.columns:
                if '治疗' in str(col) or '领域' in str(col):
                    treatment_area_col = col
                    break
            
            if treatment_area_col is None:
                # 如果没找到，使用第三列（通常是治疗领域）
                treatment_area_col = df.columns[2] if len(df.columns) > 2 else df.columns[-1]
        
        print(f"\n使用治疗领域列: {treatment_area_col}")
        
        # 统计各治疗领域的药品数量
        treatment_counts = df[treatment_area_col].value_counts()
        
        print(f"\n=== 不同治疗领域药品数量统计 ===")
        print(f"总药品数量: {len(df)}")
        print(f"治疗领域种类: {len(treatment_counts)}")
        print("-" * 50)
        
        for i, (area, count) in enumerate(treatment_counts.items(), 1):
            percentage = (count / len(df)) * 100
            print(f"{i:2d}. {area:<20} {count:3d}个 ({percentage:5.1f}%)")
        
        # 显示每个治疗领域的具体药品
        print(f"\n=== 各治疗领域具体药品列表 ===")
        
        for area, count in treatment_counts.items():
            print(f"\n【{area}】({count}个):")
            area_drugs = df[df[treatment_area_col] == area]['药品名称'].tolist()
            for j, drug in enumerate(area_drugs, 1):
                print(f"  {j:2d}. {drug}")
        
        # 创建统计表
        summary_data = []
        for i, (area, count) in enumerate(treatment_counts.items(), 1):
            percentage = (count / len(df)) * 100
            summary_data.append({
                '排名': i,
                '治疗领域': area,
                '药品数量': count,
                '占比(%)': f"{percentage:.1f}%"
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        # 保存结果
        with pd.ExcelWriter('c:\\偷偷用用AI\\有数据创新药治疗领域分布分析.xlsx') as writer:
            summary_df.to_excel(writer, sheet_name='治疗领域统计', index=False)
            
            # 为每个治疗领域创建详细列表
            for area in treatment_counts.index[:10]:  # 只为前10个治疗领域创建详细表
                area_df = df[df[treatment_area_col] == area][['获批年份', '药品名称', treatment_area_col]]
                safe_area_name = area.replace('/', '_').replace('\\', '_')[:20]  # 处理特殊字符和长度
                area_df.to_excel(writer, sheet_name=f'{safe_area_name}', index=False)
        
        print(f"\n结果已保存到: 有数据创新药治疗领域分布分析.xlsx")
        
        return treatment_counts, summary_df
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    treatment_counts, summary_df = analyze_treatment_areas()



































