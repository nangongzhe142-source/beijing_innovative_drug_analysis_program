#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创新药按治疗领域和是否谈判药分类统计
"""

import pandas as pd
import os
from datetime import datetime

def read_innovative_drug_list():
    """读取创新药名单文件"""
    file_path = r'创新药名单_去重去中药版_最终完整版_含国产进口信息_标记有数据_含谈判药_修复模糊匹配.xlsx'
    
    print(f"正在读取文件: {file_path}")
    df = pd.read_excel(file_path)
    
    print(f"文件总行数: {len(df)}")
    print(f"列名: {df.columns.tolist()}")
    
    # 获取B列（药品名称）、E列（治疗领域）、K列（是否谈判药）
    # 列索引：B=1, E=4, K=10
    drug_name_col = df.columns[1]  # B列
    treatment_area_col = df.columns[4]  # E列
    negotiation_col = df.columns[10]  # K列
    
    print(f"\nB列（药品名称）: {drug_name_col}")
    print(f"E列（治疗领域）: {treatment_area_col}")
    print(f"K列（是否谈判药）: {negotiation_col}")
    
    # 创建药品信息字典
    drug_info = {}
    for idx, row in df.iterrows():
        drug_name = str(row[drug_name_col]).strip() if pd.notna(row[drug_name_col]) else ''
        treatment_area = str(row[treatment_area_col]).strip() if pd.notna(row[treatment_area_col]) else ''
        is_negotiation = str(row[negotiation_col]).strip() if pd.notna(row[negotiation_col]) else ''
        
        if drug_name:
            drug_info[drug_name] = {
                'treatment_area': treatment_area,
                'is_negotiation': is_negotiation
            }
    
    print(f"\n成功读取 {len(drug_info)} 个药品信息")
    print(f"前5个药品示例:")
    for i, (drug, info) in enumerate(list(drug_info.items())[:5]):
        print(f"  {i+1}. {drug}: 治疗领域={info['treatment_area']}, 是否谈判药={info['is_negotiation']}")
    
    return drug_info, drug_name_col, treatment_area_col, negotiation_col

def read_hospital_data():
    """读取医院数据文件的所有工作表"""
    file_path = r'仙尊大人_创新药医院数据完整匹配结果_10工作表版_20250908_144656.xlsx'
    
    print(f"\n正在读取文件: {file_path}")
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    
    print(f"工作表数量: {len(sheet_names)}")
    print(f"工作表列表: {sheet_names}")
    
    all_data = []
    data_sheet_count = 0  # 实际数据工作表计数器
    
    for i, sheet_name in enumerate(sheet_names):
        # 跳过非数据工作表（如"综合汇总"）
        if '汇总' in sheet_name or '综合' in sheet_name:
            print(f"\n跳过非数据工作表: {sheet_name}")
            continue
            
        print(f"\n处理工作表 {i+1}/{len(sheet_names)}: {sheet_name}")
        df_sheet = pd.read_excel(file_path, sheet_name=sheet_name)
        
        print(f"  行数: {len(df_sheet)}")
        print(f"  列数: {len(df_sheet.columns)}")
        
        # 检查是否有足够的列
        if len(df_sheet.columns) < 15:
            print(f"  警告: 工作表列数不足，跳过")
            continue
        
        # 获取关键列：O列（药品通用名，索引14）、I列（销售金额，索引8）
        try:
            generic_name_col = df_sheet.columns[14]  # O列
            amount_col = df_sheet.columns[8]  # I列
            
            # 根据实际数据工作表位置确定销售制剂量列
            # 前3个数据工作表用J列（索引9），后3个数据工作表用K列（索引10）
            if data_sheet_count < 3:  # 前3个数据工作表
                if len(df_sheet.columns) > 9:
                    usage_col = df_sheet.columns[9]  # J列（索引9）
                else:
                    print(f"  警告: 工作表列数不足，跳过")
                    continue
            else:  # 后3个数据工作表及之后
                if len(df_sheet.columns) > 10:
                    usage_col = df_sheet.columns[10]  # K列（索引10）
                else:
                    print(f"  警告: 工作表列数不足，跳过")
                    continue
            
            print(f"  O列（药品通用名）: {generic_name_col}")
            print(f"  I列（销售金额）: {amount_col}")
            print(f"  销售制剂量列: {usage_col} (索引{df_sheet.columns.get_loc(usage_col)})")
            
            # 选择需要的列
            df_selected = df_sheet[[generic_name_col, amount_col, usage_col]].copy()
            df_selected.columns = ['药品通用名', '销售金额', '销售制剂量']
            df_selected['工作表'] = sheet_name
            df_selected['工作表索引'] = data_sheet_count
            
            # 清理数据：去除空值
            df_selected = df_selected.dropna(subset=['药品通用名'])
            
            # 转换数值列为数值类型
            df_selected['销售金额'] = pd.to_numeric(df_selected['销售金额'], errors='coerce').fillna(0)
            df_selected['销售制剂量'] = pd.to_numeric(df_selected['销售制剂量'], errors='coerce').fillna(0)
            
            all_data.append(df_selected)
            data_sheet_count += 1  # 增加数据工作表计数
            print(f"  有效数据行数: {len(df_selected)}")
            
        except Exception as e:
            print(f"  错误处理工作表 {sheet_name}: {e}")
            continue
    
    if not all_data:
        raise ValueError("没有成功读取任何数据工作表")
    
    # 合并所有数据
    df_all = pd.concat(all_data, ignore_index=True)
    print(f"\n合并后总数据行数: {len(df_all)}")
    
    return df_all

def match_drugs(drug_info, hospital_df):
    """匹配药品名称"""
    print("\n开始匹配药品名称...")
    
    matched_data = []
    unmatched_count = 0
    
    for idx, row in hospital_df.iterrows():
        generic_name = str(row['药品通用名']).strip()
        
        # 查找匹配的创新药名称（后者完全属于前者）
        matched_drug = None
        matched_info = None
        
        for drug_name, info in drug_info.items():
            if generic_name in drug_name:  # 后者（generic_name）完全属于前者（drug_name）
                matched_drug = drug_name
                matched_info = info
                break
        
        if matched_drug:
            matched_data.append({
                '药品通用名': generic_name,
                '匹配的创新药名称': matched_drug,
                '治疗领域': matched_info['treatment_area'],
                '是否谈判药': matched_info['is_negotiation'],
                '销售金额': row['销售金额'],
                '销售制剂量': row['销售制剂量'],
                '工作表': row['工作表']
            })
        else:
            unmatched_count += 1
    
    print(f"匹配成功: {len(matched_data)} 条")
    print(f"未匹配: {unmatched_count} 条")
    
    matched_df = pd.DataFrame(matched_data)
    return matched_df

def calculate_statistics(matched_df):
    """计算统计结果"""
    print("\n开始计算统计结果...")
    
    # 创建结果列表
    results = []
    
    # 获取所有治疗领域
    treatment_areas = sorted(matched_df['治疗领域'].dropna().unique())
    print(f"治疗领域数量: {len(treatment_areas)}")
    print(f"治疗领域列表: {treatment_areas}")
    
    # 按治疗领域和是否谈判药分组统计
    for treatment_area in treatment_areas:
        # 筛选该治疗领域的数据
        area_data = matched_df[matched_df['治疗领域'] == treatment_area]
        
        # 1. 是谈判药的数据
        negotiation_data = area_data[area_data['是否谈判药'].str.contains('是', na=False)]
        negotiation_amount = negotiation_data['销售金额'].sum()
        negotiation_usage = negotiation_data['销售制剂量'].sum()
        # 统计不重复的药品数量
        negotiation_drug_count = negotiation_data['匹配的创新药名称'].nunique()
        
        results.append({
            '治疗领域': treatment_area,
            '分类': '是谈判药',
            '销售金额': negotiation_amount,
            '销售制剂量': negotiation_usage,
            '记录数': len(negotiation_data),
            '药品数量': negotiation_drug_count
        })
        
        # 2. 所有药品的数据（包括谈判药和非谈判药）
        all_amount = area_data['销售金额'].sum()
        all_usage = area_data['销售制剂量'].sum()
        # 统计不重复的药品数量
        all_drug_count = area_data['匹配的创新药名称'].nunique()
        
        results.append({
            '治疗领域': treatment_area,
            '分类': '所有药品',
            '销售金额': all_amount,
            '销售制剂量': all_usage,
            '记录数': len(area_data),
            '药品数量': all_drug_count
        })
    
    # 转换为DataFrame
    result_df = pd.DataFrame(results)
    
    # 计算各维度总计
    # 1. 按治疗领域总计（等于该治疗领域的"所有药品"值，因为"所有药品"已包含全部）
    treatment_totals = []
    for treatment_area in treatment_areas:
        area_all_drugs = result_df[(result_df['治疗领域'] == treatment_area) & 
                                   (result_df['分类'] == '所有药品')]
        if len(area_all_drugs) > 0:
            treatment_totals.append({
                '治疗领域': treatment_area,
                '分类': '该治疗领域总计',
                '销售金额': area_all_drugs.iloc[0]['销售金额'],
                '销售制剂量': area_all_drugs.iloc[0]['销售制剂量'],
                '记录数': area_all_drugs.iloc[0]['记录数'],
                '药品数量': area_all_drugs.iloc[0]['药品数量']
            })
    
    treatment_totals_df = pd.DataFrame(treatment_totals)
    
    # 2. 按分类总计（是谈判药 vs 所有药品）
    negotiation_total = result_df[result_df['分类'] == '是谈判药'].agg({
        '销售金额': 'sum',
        '销售制剂量': 'sum',
        '记录数': 'sum'
    })
    # 单独计算谈判药的不重复药品数量
    negotiation_drug_count = matched_df[matched_df['是否谈判药'].str.contains('是', na=False)]['匹配的创新药名称'].nunique()
    
    all_drugs_total = result_df[result_df['分类'] == '所有药品'].agg({
        '销售金额': 'sum',
        '销售制剂量': 'sum',
        '记录数': 'sum'
    })
    # 单独计算所有药品的不重复药品数量
    all_drugs_drug_count = matched_df['匹配的创新药名称'].nunique()
    
    category_totals = pd.DataFrame([
        {
            '治疗领域': '全部治疗领域',
            '分类': '是谈判药总计',
            '销售金额': negotiation_total['销售金额'],
            '销售制剂量': negotiation_total['销售制剂量'],
            '记录数': int(negotiation_total['记录数']),
            '药品数量': negotiation_drug_count
        },
        {
            '治疗领域': '全部治疗领域',
            '分类': '所有药品总计',
            '销售金额': all_drugs_total['销售金额'],
            '销售制剂量': all_drugs_total['销售制剂量'],
            '记录数': int(all_drugs_total['记录数']),
            '药品数量': all_drugs_drug_count
        }
    ])
    
    # 3. 全局总计
    global_total = pd.DataFrame([{
        '治疗领域': '全部治疗领域',
        '分类': '全部总计',
        '销售金额': matched_df['销售金额'].sum(),
        '销售制剂量': matched_df['销售制剂量'].sum(),
        '记录数': len(matched_df),
        '药品数量': matched_df['匹配的创新药名称'].nunique()
    }])
    
    # 合并所有结果：先基础数据，再治疗领域总计，再分类总计，最后全局总计
    final_results = pd.concat([
        result_df,
        treatment_totals_df,
        category_totals,
        global_total
    ], ignore_index=True)
    
    return final_results

def main():
    """主函数"""
    print("=" * 80)
    print("创新药按治疗领域和是否谈判药分类统计")
    print("=" * 80)
    
    try:
        # 1. 读取创新药名单
        drug_info, drug_name_col, treatment_area_col, negotiation_col = read_innovative_drug_list()
        
        # 2. 读取医院数据
        hospital_df = read_hospital_data()
        
        # 3. 匹配药品
        matched_df = match_drugs(drug_info, hospital_df)
        
        # 4. 计算统计结果
        result_df = calculate_statistics(matched_df)
        
        # 5. 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'创新药治疗领域谈判药统计分析结果_{timestamp}.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 保存统计结果
            result_df.to_excel(writer, sheet_name='统计结果', index=False)
            
            # 保存匹配详情
            matched_df.to_excel(writer, sheet_name='匹配详情', index=False)
        
        print(f"\n结果已保存到: {output_file}")
        print(f"\n统计结果预览:")
        print(result_df.head(20).to_string())
        
        print(f"\n总计信息:")
        print(f"  总销售金额: {matched_df['销售金额'].sum():,.2f}")
        print(f"  总销售制剂量: {matched_df['销售制剂量'].sum():,.2f}")
        print(f"  总记录数: {len(matched_df)}")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

