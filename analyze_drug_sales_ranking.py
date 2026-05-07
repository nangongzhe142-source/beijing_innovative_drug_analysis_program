#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仙尊大人的国谈药销售金额排名分析
自动识别销售金额和医院用量列，分析前十名和后十名药品
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def identify_columns(df):
    """自动识别销售金额和医院用量列"""
    columns = df.columns.tolist()
    
    # 识别销售金额列（包含"销售金额"的列）
    sales_amount_cols = [col for col in columns if '销售金额' in str(col)]
    
    # 识别医院用量列（包含"用量"的列）
    usage_cols = [col for col in columns if '用量' in str(col)]
    
    # 识别药品名称列（C列或包含"药品"的列）
    drug_name_col = None
    if '谈判药品' in columns:
        drug_name_col = '谈判药品'
    elif 'C' in columns:
        drug_name_col = 'C'
    else:
        # 寻找包含"药品"的列
        drug_cols = [col for col in columns if '药品' in str(col)]
        if drug_cols:
            drug_name_col = drug_cols[0]
    
    return sales_amount_cols, usage_cols, drug_name_col

def analyze_drug_sales_ranking():
    """分析国谈药销售金额排名"""
    
    filename = "国谈药统计分析结果.xlsx"
    
    try:
        # 读取Excel文件的所有工作表
        excel_file = pd.ExcelFile(filename)
        sheet_names = excel_file.sheet_names
        
        print(f"仙尊大人，正在分析文件: {filename}")
        print(f"发现 {len(sheet_names)} 个工作表:")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet}")
        
        # 分析前三个表格
        target_sheets = sheet_names[:3]
        print(f"\n正在分析前三个表格: {target_sheets}")
        
        all_drug_data = []
        
        for i, sheet_name in enumerate(target_sheets, 1):
            print(f"\n=== 分析表格 {i}: {sheet_name} ===")
            
            try:
                # 读取工作表
                df = pd.read_excel(filename, sheet_name=sheet_name)
                
                print(f"原始数据行数: {len(df)}")
                print(f"原始数据列数: {len(df.columns)}")
                
                # 自动识别列
                sales_cols, usage_cols, drug_col = identify_columns(df)
                
                print(f"识别到的销售金额列: {sales_cols}")
                print(f"识别到的医院用量列: {usage_cols}")
                print(f"识别到的药品名称列: {drug_col}")
                
                if not sales_cols or not drug_col:
                    print("⚠ 未找到必要的列，跳过此表格")
                    continue
                
                # 提取年份（从表格名称中）
                year = None
                if '2020' in sheet_name:
                    year = '2020年'
                elif '2021' in sheet_name:
                    year = '2021年'
                elif '2022' in sheet_name:
                    year = '2022年'
                
                # 处理每一行数据
                for idx, row in df.iterrows():
                    drug_name = str(row[drug_col]).strip()
                    if pd.isna(row[drug_col]) or drug_name == '' or drug_name == 'nan':
                        continue
                    
                    # 计算总销售金额
                    total_sales = 0
                    sales_detail = {}
                    for col in sales_cols:
                        value = pd.to_numeric(row[col], errors='coerce')
                        if pd.notna(value):
                            total_sales += value
                            # 提取医院级别
                            if '三级' in col:
                                sales_detail['三级医院销售金额'] = value
                            elif '二级' in col:
                                sales_detail['二级医院销售金额'] = value
                            elif '一级' in col:
                                sales_detail['一级医院销售金额'] = value
                    
                    # 计算总用量
                    total_usage = 0
                    usage_detail = {}
                    for col in usage_cols:
                        value = pd.to_numeric(row[col], errors='coerce')
                        if pd.notna(value):
                            total_usage += value
                            # 提取医院级别
                            if '三级' in col:
                                usage_detail['三级医院用量'] = value
                            elif '二级' in col:
                                usage_detail['二级医院用量'] = value
                            elif '一级' in col:
                                usage_detail['一级医院用量'] = value
                    
                    if total_sales > 0:  # 只记录有销售金额的药品
                        drug_data = {
                            'drug_name': drug_name,
                            'year': year,
                            'total_sales': total_sales,
                            'total_usage': total_usage,
                            **sales_detail,
                            **usage_detail
                        }
                        all_drug_data.append(drug_data)
                
                print(f"该表格有效药品数据: {len([d for d in all_drug_data if d['year'] == year])}")
                
            except Exception as e:
                print(f"处理表格 {sheet_name} 时出错: {str(e)}")
                continue
        
        if not all_drug_data:
            print("没有找到有效的药品数据")
            return
        
        # 转换为DataFrame进行分析
        df_all = pd.DataFrame(all_drug_data)
        
        # 按药品名称汇总（累加重复药品的销售额）
        print(f"\n=== 汇总分析 ===")
        print(f"总数据条数: {len(df_all)}")
        
        # 汇总每个药品的总销售金额和各年度明细
        drug_summary = {}
        
        for _, row in df_all.iterrows():
            drug_name = row['drug_name']
            year = row['year']
            
            if drug_name not in drug_summary:
                drug_summary[drug_name] = {
                    'total_sales': 0,
                    'total_usage': 0,
                    'years': {},
                    'hospital_levels': {
                        '三级医院销售金额': 0,
                        '二级医院销售金额': 0, 
                        '一级医院销售金额': 0,
                        '三级医院用量': 0,
                        '二级医院用量': 0,
                        '一级医院用量': 0
                    }
                }
            
            # 累加总销售金额和用量
            drug_summary[drug_name]['total_sales'] += row['total_sales']
            drug_summary[drug_name]['total_usage'] += row['total_usage']
            
            # 记录年度明细
            if year not in drug_summary[drug_name]['years']:
                drug_summary[drug_name]['years'][year] = {
                    'sales': 0,
                    'usage': 0
                }
            
            drug_summary[drug_name]['years'][year]['sales'] += row['total_sales']
            drug_summary[drug_name]['years'][year]['usage'] += row['total_usage']
            
            # 累加各级医院数据
            for level in drug_summary[drug_name]['hospital_levels']:
                if level in row and pd.notna(row[level]):
                    drug_summary[drug_name]['hospital_levels'][level] += row[level]
        
        # 转换为DataFrame并排序
        summary_data = []
        for drug_name, data in drug_summary.items():
            row_data = {
                'drug_name': drug_name,
                'total_sales': data['total_sales'],
                'total_usage': data['total_usage']
            }
            
            # 添加年度数据
            for year in ['2020年', '2021年', '2022年']:
                if year in data['years']:
                    row_data[f'{year}_销售金额'] = data['years'][year]['sales']
                    row_data[f'{year}_用量'] = data['years'][year]['usage']
                else:
                    row_data[f'{year}_销售金额'] = 0
                    row_data[f'{year}_用量'] = 0
            
            # 添加医院级别数据
            row_data.update(data['hospital_levels'])
            
            summary_data.append(row_data)
        
        summary_df = pd.DataFrame(summary_data)
        
        # 按总销售金额排序
        summary_df_sorted = summary_df.sort_values('total_sales', ascending=False)
        
        # 获取前十名和后十名
        top_10 = summary_df_sorted.head(10)
        bottom_10 = summary_df_sorted.tail(10)
        
        print(f"\n药品总数: {len(summary_df)}")
        print(f"前十名销售金额范围: {top_10['total_sales'].min():.2f} - {top_10['total_sales'].max():.2f}")
        print(f"后十名销售金额范围: {bottom_10['total_sales'].min():.2f} - {bottom_10['total_sales'].max():.2f}")
        
        # 保存结果
        save_ranking_results(top_10, bottom_10, summary_df_sorted)
        
        return top_10, bottom_10, summary_df_sorted
        
    except Exception as e:
        print(f"分析文件时出错: {str(e)}")
        return None, None, None

def save_ranking_results(top_10, bottom_10, all_data):
    """保存排名结果到Excel文件"""
    
    output_filename = f"国谈药销售金额排名分析_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
        # 1. 前十名
        top_10.to_excel(writer, sheet_name='销售金额前十名', index=False)
        
        # 2. 后十名  
        bottom_10.to_excel(writer, sheet_name='销售金额后十名', index=False)
        
        # 3. 完整排名
        all_data.to_excel(writer, sheet_name='完整排名', index=False)
    
    print(f"\n📋 排名结果已保存到: {output_filename}")
    return output_filename

def main():
    """主函数"""
    print("仙尊大人，开始分析国谈药销售金额排名...")
    
    top_10, bottom_10, all_data = analyze_drug_sales_ranking()
    
    if top_10 is not None and bottom_10 is not None:
        print(f"\n🎉 分析完成！")
        print(f"📊 前十名药品:")
        for i, row in top_10.iterrows():
            print(f"  {list(top_10.index).index(i)+1}. {row['drug_name']}: {row['total_sales']:,.2f}元")
        
        print(f"\n📊 后十名药品:")
        for i, row in bottom_10.iterrows():
            print(f"  {len(all_data)-9+list(bottom_10.index).index(i)}. {row['drug_name']}: {row['total_sales']:,.2f}元")
    else:
        print("❌ 分析失败，请检查文件格式")

if __name__ == "__main__":
    main()
