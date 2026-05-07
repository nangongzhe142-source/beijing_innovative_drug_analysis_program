#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2021年、2022年、2023年各级别医院品规数和品类数分析脚本（修正版）
正确处理不同年份的数据结构差异
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
rcParams['axes.unicode_minus'] = False

def analyze_year_data(year, files_config):
    """分析指定年份的医院品规数和品类数"""
    
    print(f"\n{'='*60}")
    print(f"仙尊大人，开始分析{year}年各级别医院品规数和品类数...")
    print(f"{'='*60}")
    
    results = {}
    detailed_results = {}
    
    for level, file_path in files_config.items():
        print(f"\n正在分析{year}年{level}数据...")
        
        try:
            # 根据文件类型读取
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                # CSV文件，自动检测编码
                encodings = ['utf-8', 'gbk', 'gb18030', 'gb2312']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        print(f"成功使用{encoding}编码读取文件")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    print(f"无法读取{file_path}，尝试所有编码都失败")
                    continue
                    
            print(f"{year}年{level}数据形状: {df.shape}")
            
            # 根据年份确定列名
            hospital_col = df.columns[0]  # A列 - 医院名称
            
            if year == '2021年':
                # 2021年：O列是标化通用名，Y列是是否医保用药
                drug_col = df.columns[14]  # O列 - 标化通用名
                insurance_col = df.columns[24]  # Y列 - 是否医保用药
            else:
                # 2022年、2023年：H列是产品通用名，Y列是是否医保用药
                drug_col = df.columns[7]   # H列 - 产品通用名
                insurance_col = df.columns[24]  # Y列 - 是否医保用药
            
            print(f"\n{year}年{level} - 医院列: {hospital_col}")
            print(f"{year}年{level} - 药品列: {drug_col}")
            print(f"{year}年{level} - 医保列: {insurance_col}")
            
            # 显示医保列的唯一值
            print(f"\n{year}年{level}医保列唯一值:")
            print(df[insurance_col].value_counts(dropna=False))
            
            # 只去除医院名称和药品名称为空的记录
            clean_df = df[[hospital_col, drug_col, insurance_col]].dropna(subset=[hospital_col, drug_col])
            print(f"{year}年{level}清理后数据形状: {clean_df.shape}")
            
            if len(clean_df) > 0:
                # 分析每个医院的数据
                hospital_stats = []
                
                for hospital in clean_df[hospital_col].unique():
                    hospital_data = clean_df[clean_df[hospital_col] == hospital]
                    
                    # 总品规数（总记录数）
                    total_specs = len(hospital_data)
                    
                    # 总品类数（药品名称不重复数量）
                    total_categories = hospital_data[drug_col].nunique()
                    
                    # 医保药数据
                    insurance_data = hospital_data[hospital_data[insurance_col] == 'Y']
                    insurance_specs = len(insurance_data)  # 医保药品规数
                    insurance_categories = insurance_data[drug_col].nunique()  # 医保药品类数
                    
                    # 非医保药数据
                    if year == '2021年':
                        # 2021年：NaN值表示非医保药
                        non_insurance_data = hospital_data[hospital_data[insurance_col].isna()]
                    else:
                        # 2022年、2023年：N值表示非医保药
                        non_insurance_data = hospital_data[hospital_data[insurance_col] == 'N']
                    
                    non_insurance_specs = len(non_insurance_data)  # 非医保药品规数
                    non_insurance_categories = non_insurance_data[drug_col].nunique()  # 非医保药品类数
                    
                    hospital_stats.append({
                        '医院名称': hospital,
                        '总品规数': total_specs,
                        '总品类数': total_categories,
                        '医保药品规数': insurance_specs,
                        '医保药品类数': insurance_categories,
                        '非医保药品规数': non_insurance_specs,
                        '非医保药品类数': non_insurance_categories,
                        '医保药品规占比': insurance_specs / total_specs * 100 if total_specs > 0 else 0,
                        '医保药品类占比': insurance_categories / total_categories * 100 if total_categories > 0 else 0
                    })
                
                # 转换为DataFrame
                hospital_stats_df = pd.DataFrame(hospital_stats)
                hospital_stats_df = hospital_stats_df.sort_values('总品规数', ascending=False)
                
                print(f"\n{year}年{level}医院数量: {len(hospital_stats_df)}")
                print(f"{year}年{level}统计结果:")
                print(f"  平均总品规数: {hospital_stats_df['总品规数'].mean():.2f}")
                print(f"  平均总品类数: {hospital_stats_df['总品类数'].mean():.2f}")
                print(f"  平均医保药品规数: {hospital_stats_df['医保药品规数'].mean():.2f}")
                print(f"  平均医保药品类数: {hospital_stats_df['医保药品类数'].mean():.2f}")
                print(f"  平均非医保药品规数: {hospital_stats_df['非医保药品规数'].mean():.2f}")
                print(f"  平均非医保药品类数: {hospital_stats_df['非医保药品类数'].mean():.2f}")
                print(f"  平均医保药品规占比: {hospital_stats_df['医保药品规占比'].mean():.2f}%")
                print(f"  平均医保药品类占比: {hospital_stats_df['医保药品类占比'].mean():.2f}%")
                
                # 显示前10名医院
                print(f"\n{year}年{level}总品规数前10名医院:")
                print(hospital_stats_df[['医院名称', '总品规数', '总品类数', '医保药品规数', '医保药品类数', '非医保药品规数', '非医保药品类数']].head(10).to_string(index=False))
                
                # 保存结果
                results[level] = {
                    '医院数量': len(hospital_stats_df),
                    '平均总品规数': hospital_stats_df['总品规数'].mean(),
                    '平均总品类数': hospital_stats_df['总品类数'].mean(),
                    '平均医保药品规数': hospital_stats_df['医保药品规数'].mean(),
                    '平均医保药品类数': hospital_stats_df['医保药品类数'].mean(),
                    '平均非医保药品规数': hospital_stats_df['非医保药品规数'].mean(),
                    '平均非医保药品类数': hospital_stats_df['非医保药品类数'].mean(),
                    '平均医保药品规占比': hospital_stats_df['医保药品规占比'].mean(),
                    '平均医保药品类占比': hospital_stats_df['医保药品类占比'].mean(),
                    '中位数总品规数': hospital_stats_df['总品规数'].median(),
                    '中位数总品类数': hospital_stats_df['总品类数'].median(),
                    '最大总品规数': hospital_stats_df['总品规数'].max(),
                    '最小总品规数': hospital_stats_df['总品规数'].min(),
                    '最大总品类数': hospital_stats_df['总品类数'].max(),
                    '最小总品类数': hospital_stats_df['总品类数'].min()
                }
                
                detailed_results[level] = hospital_stats_df
                
            else:
                print(f"警告：{year}年{level}清理后无有效数据")
                
        except Exception as e:
            print(f"读取{year}年{level}数据时出错: {e}")
            continue
    
    return results, detailed_results

def create_three_year_comparison(results_2021, results_2022, results_2023):
    """创建三年对比分析"""
    
    print(f"\n{'='*80}")
    print(f"仙尊大人，2021年、2022年、2023年各级别医院品规数品类数三年对比分析")
    print(f"{'='*80}")
    
    # 创建对比表格
    comparison_data = []
    
    # 获取所有级别
    all_levels = set(results_2021.keys()) | set(results_2022.keys()) | set(results_2023.keys())
    
    for level in sorted(all_levels):
        row = [level]
        
        # 2021年数据
        if level in results_2021:
            row.extend([
                results_2021[level]['医院数量'],
                f"{results_2021[level]['平均总品规数']:.2f}",
                f"{results_2021[level]['平均总品类数']:.2f}",
                f"{results_2021[level]['平均医保药品规占比']:.2f}%"
            ])
        else:
            row.extend(['N/A', 'N/A', 'N/A', 'N/A'])
        
        # 2022年数据
        if level in results_2022:
            row.extend([
                results_2022[level]['医院数量'],
                f"{results_2022[level]['平均总品规数']:.2f}",
                f"{results_2022[level]['平均总品类数']:.2f}",
                f"{results_2022[level]['平均医保药品规占比']:.2f}%"
            ])
        else:
            row.extend(['N/A', 'N/A', 'N/A', 'N/A'])
        
        # 2023年数据
        if level in results_2023:
            row.extend([
                results_2023[level]['医院数量'],
                f"{results_2023[level]['平均总品规数']:.2f}",
                f"{results_2023[level]['平均总品类数']:.2f}",
                f"{results_2023[level]['平均医保药品规占比']:.2f}%"
            ])
        else:
            row.extend(['N/A', 'N/A', 'N/A', 'N/A'])
        
        comparison_data.append(row)
    
    comparison_df = pd.DataFrame(comparison_data, columns=[
        '医院级别',
        '2021年医院数', '2021年平均品规数', '2021年平均品类数', '2021年医保药占比',
        '2022年医院数', '2022年平均品规数', '2022年平均品类数', '2022年医保药占比',
        '2023年医院数', '2023年平均品规数', '2023年平均品类数', '2023年医保药占比'
    ])
    
    print(f"\n📊 2021年-2023年三年对比分析表:")
    print(comparison_df.to_string(index=False))
    
    return comparison_df

def main():
    """主函数"""
    
    # 2021年文件配置
    files_2021 = {
        '三级医院': '2021年/三级药品使用数据.xlsx',
        '二级医院': '2021年/二级药品使用数据.xlsx', 
        '一级医院': '2021年/使用数据（基层）.xlsx'
    }
    
    # 2022年文件配置
    files_2022 = {
        '三级医院': '2022年/RPT_DRUG_USE_2022_BIG-北京市-三级.csv',
        '二级医院': '2022年/RPT_DRUG_USE_2022_BIG-北京市-二级.csv',
        '一级医院': '2022年/RPT_DRUG_USE_2022_BIG-北京市-基层.csv'
    }
    
    # 2023年文件配置
    files_2023 = {
        '一级医院': '2023年/RPT_DRUG_USE_2023_BIG_北京_1.csv',
        '二级医院': '2023年/RPT_DRUG_USE_2023_BIG_北京_2.csv',
        '三级医院': '2023年/RPT_DRUG_USE_2023_BIG_北京_3.csv'
    }
    
    # 分析各年数据
    results_2021, detailed_2021 = analyze_year_data('2021年', files_2021)
    results_2022, detailed_2022 = analyze_year_data('2022年', files_2022)
    results_2023, detailed_2023 = analyze_year_data('2023年', files_2023)
    
    # 创建三年对比分析
    if results_2021 and results_2022 and results_2023:
        comparison_df = create_three_year_comparison(results_2021, results_2022, results_2023)
        
        # 保存结果到Excel
        try:
            with pd.ExcelWriter('2021-2023年各级别医院品规数品类数三年对比分析结果.xlsx', engine='openpyxl') as writer:
                comparison_df.to_excel(writer, sheet_name='三年对比分析汇总', index=False)
                
                # 保存各年详细数据
                for level, detail_df in detailed_2021.items():
                    detail_df.to_excel(writer, sheet_name=f'2021年{level}详细数据', index=False)
                
                for level, detail_df in detailed_2022.items():
                    detail_df.to_excel(writer, sheet_name=f'2022年{level}详细数据', index=False)
                
                for level, detail_df in detailed_2023.items():
                    detail_df.to_excel(writer, sheet_name=f'2023年{level}详细数据', index=False)
            
            print(f"\n✅ 三年对比分析结果已保存到 '2021-2023年各级别医院品规数品类数三年对比分析结果.xlsx'")
            
        except Exception as e:
            print(f"\n❌ 保存Excel文件时出错: {e}")
        
        # 生成总结报告
        print(f"\n🎯 三年发展趋势:")
        
        common_levels = set(results_2021.keys()) & set(results_2022.keys()) & set(results_2023.keys())
        for level in sorted(common_levels):
            specs_2021 = results_2021[level]['平均总品规数']
            specs_2022 = results_2022[level]['平均总品规数']
            specs_2023 = results_2023[level]['平均总品规数']
            
            change_21_22 = specs_2022 - specs_2021
            change_22_23 = specs_2023 - specs_2022
            change_21_23 = specs_2023 - specs_2021
            
            print(f"- {level}:")
            print(f"  2021年: {specs_2021:.1f} → 2022年: {specs_2022:.1f} → 2023年: {specs_2023:.1f}")
            print(f"  2021-2022变化: {change_21_22:+.1f}  2022-2023变化: {change_22_23:+.1f}  三年总变化: {change_21_23:+.1f}")
    
    print("\n📋 三年对比分析完成！所有结果已保存。")

if __name__ == "__main__":
    main()
