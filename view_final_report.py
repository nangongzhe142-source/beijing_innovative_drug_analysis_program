#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看最终完整分析报告
"""

import pandas as pd
import os

def view_final_report():
    """查看最终分析报告文件"""
    
    # 查找最新的报告文件
    result_files = [f for f in os.listdir('.') if f.startswith('仙尊大人_完整医院药品分析报告_') and f.endswith('.xlsx')]
    
    if not result_files:
        print("未找到报告文件")
        return
    
    # 选择最新的文件
    latest_file = sorted(result_files)[-1]
    print(f"正在查看文件: {latest_file}")
    
    # 读取Excel文件的所有工作表
    excel_file = pd.ExcelFile(latest_file)
    sheet_names = excel_file.sheet_names
    
    print(f"\n📊 完整分析报告包含 {len(sheet_names)} 个工作表:")
    for i, sheet in enumerate(sheet_names, 1):
        print(f"  {i:2d}. {sheet}")
    
    print("\n" + "="*80)
    
    # 重点查看关键工作表
    key_sheets = ['数据概览', '销售金额前20名', '医保药_图1格式', '非医保药_图1格式']
    
    for sheet_name in key_sheets:
        if sheet_name in sheet_names:
            print(f"\n📋 工作表: {sheet_name}")
            print("-" * 60)
            
            try:
                df = pd.read_excel(latest_file, sheet_name=sheet_name)
                print(f"数据行数: {len(df)}")
                print(f"数据列数: {len(df.columns)}")
                
                if len(df) > 0:
                    print("列名:", list(df.columns))
                    
                    # 显示数据
                    if len(df) <= 15:
                        print("\n完整数据:")
                        print(df.to_string(index=False))
                    else:
                        print("\n前10行数据:")
                        print(df.head(10).to_string(index=False))
                
            except Exception as e:
                print(f"读取工作表失败: {str(e)}")
            
            print("\n" + "="*80)
    
    # 统计各类表格数量
    table1_count = len([s for s in sheet_names if '_图1格式' in s])
    table2_count = len([s for s in sheet_names if '_图2格式' in s])
    
    print(f"\n📈 报告统计:")
    print(f"  图1格式表格: {table1_count} 个")
    print(f"  图2格式表格: {table2_count} 个")
    print(f"  总工作表数: {len(sheet_names)} 个")
    
    # 显示所有工作表名称分类
    print(f"\n📋 工作表分类:")
    
    categories = {
        '基础数据': [s for s in sheet_names if s in ['数据概览', '销售金额前20名', '销售金额后20名', '进院率分析']],
        '医保药品分析': [s for s in sheet_names if s.startswith('医保药') and not s.startswith('医保创新') and not s.startswith('医保非创新')],
        '非医保药品分析': [s for s in sheet_names if s.startswith('非医保药') and not s.startswith('非医保创新') and not s.startswith('非医保非创新')],
        '创新药分析': [s for s in sheet_names if '创新药' in s],
        '非创新药分析': [s for s in sheet_names if '非创新药' in s]
    }
    
    for category, sheets in categories.items():
        if sheets:
            print(f"  {category}: {len(sheets)} 个")
            for sheet in sheets:
                print(f"    - {sheet}")

if __name__ == "__main__":
    view_final_report()
