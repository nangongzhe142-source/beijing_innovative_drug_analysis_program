#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仙尊大人专属谈判药品分析系统 - 完整实施计划
生成四组表格：所有谈判药、首谈药、续约药、创新药
"""

import pandas as pd
import os
from difflib import SequenceMatcher
import re

class NegotiatedDrugsAnalyzer:
    def __init__(self):
        self.negotiated_drugs = None
        self.hospital_data = {}
        self.hospital_counts = {}
        self.results = {}
        
    def analyze_negotiated_drugs_structure(self):
        """分析谈判药数据结构"""
        print("="*80)
        print("第一阶段：分析谈判药数据结构")
        print("="*80)
        
        file_path = "没有中药成分的谈判药.xlsx"
        
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return False
            
        try:
            df = pd.read_excel(file_path)
            print(f"✅ 成功读取谈判药数据: {df.shape}")
            print(f"列名: {list(df.columns)}")
            
            # 显示前几行数据以确认结构
            print("\n前5行数据预览:")
            print(df.head())
            
            # 分析各列内容
            if len(df.columns) > 0:
                print(f"\nA列内容样例: {df.iloc[:5, 0].tolist()}")
            if len(df.columns) > 2:
                print(f"C列内容样例: {df.iloc[:5, 2].tolist()}")
            if len(df.columns) > 5:
                print(f"F列内容样例: {df.iloc[:5, 5].tolist()}")
            if len(df.columns) > 6:
                print(f"G列内容样例: {df.iloc[:5, 6].tolist()}")
                
            # 检查谈判类别的唯一值
            if len(df.columns) > 5:
                negotiation_types = df.iloc[:, 5].dropna().unique()
                print(f"\n谈判类别(F列)唯一值: {negotiation_types}")
                
            # 检查创新药标识的唯一值  
            if len(df.columns) > 6:
                innovation_markers = df.iloc[:, 6].dropna().unique()
                print(f"创新药标识(G列)唯一值: {innovation_markers}")
                
            self.negotiated_drugs = df
            return True
            
        except Exception as e:
            print(f"❌ 读取谈判药数据失败: {e}")
            return False
    
    def analyze_hospital_data_structure(self):
        """分析医院数据结构"""
        print("\n" + "="*80)
        print("第二阶段：分析医院数据结构")
        print("="*80)
        
        hospital_files = []
        for year in [2021, 2022, 2023]:
            for category in ['委属', '市属', '其他三级']:
                filename = f"{year}年_{category}_医院数据.xlsx"
                if os.path.exists(filename):
                    hospital_files.append((year, category, filename))
                else:
                    print(f"⚠️ 文件不存在: {filename}")
        
        print(f"找到 {len(hospital_files)} 个医院数据文件")
        
        for year, category, filename in hospital_files:
            try:
                df = pd.read_excel(filename)
                print(f"\n📁 {filename}:")
                print(f"  数据形状: {df.shape}")
                print(f"  列名: {list(df.columns)}")
                
                # 识别销售制剂量列
                dosage_col = self.identify_dosage_column(df.columns)
                print(f"  销售制剂量列: {dosage_col}")
                
                # 识别销售金额列
                amount_col = self.identify_amount_column(df.columns)
                print(f"  销售金额列: {amount_col}")
                
                # 统计医院数量
                if len(df.columns) > 0:
                    hospital_count = df.iloc[:, 0].nunique()
                    print(f"  医院数量: {hospital_count}")
                    
                    # 保存医院数量统计
                    if year not in self.hospital_counts:
                        self.hospital_counts[year] = {}
                    self.hospital_counts[year][category] = hospital_count
                
                # 保存数据结构信息
                self.hospital_data[f"{year}_{category}"] = {
                    'filename': filename,
                    'data': df,
                    'dosage_col': dosage_col,
                    'amount_col': amount_col,
                    'hospital_col': df.columns[0] if len(df.columns) > 0 else None,
                    'drug_col': df.columns[7] if len(df.columns) > 7 else None  # H列
                }
                
            except Exception as e:
                print(f"❌ 读取 {filename} 失败: {e}")
        
        # 显示医院数量统计
        print(f"\n医院数量统计:")
        for year, categories in self.hospital_counts.items():
            print(f"  {year}年:")
            for category, count in categories.items():
                print(f"    {category}: {count}家")
    
    def identify_dosage_column(self, columns):
        """识别销售制剂量列"""
        keywords = ['制剂量', '用量', '数量', '销售制剂量', '销售数量']
        
        for col in columns:
            col_str = str(col).lower()
            for keyword in keywords:
                if keyword in col_str:
                    return col
        
        # 如果没找到，返回可能的列
        for col in columns:
            if '量' in str(col):
                return col
                
        return None
    
    def identify_amount_column(self, columns):
        """识别销售金额列"""
        keywords = ['销售金额', '金额', '收入', '销售额']
        
        for col in columns:
            col_str = str(col).lower()
            for keyword in keywords:
                if keyword in col_str:
                    return col
        
        # 如果没找到，返回可能的列
        for col in columns:
            if '金额' in str(col) or '收入' in str(col):
                return col
                
        return None
    
    def match_drug_names(self, hospital_drug_name, negotiated_drug_name):
        """药品名称匹配算法"""
        if pd.isna(hospital_drug_name) or pd.isna(negotiated_drug_name):
            return 0
            
        # 标准化处理
        def normalize_name(name):
            name = str(name).strip()
            # 去除括号内容
            name = re.sub(r'[（(].*?[）)]', '', name)
            # 去除多余空格
            name = re.sub(r'\s+', '', name)
            return name.lower()
        
        norm_hospital = normalize_name(hospital_drug_name)
        norm_negotiated = normalize_name(negotiated_drug_name)
        
        # 精确匹配
        if norm_hospital == norm_negotiated:
            return 1.0
            
        # 相似度匹配
        similarity = SequenceMatcher(None, norm_hospital, norm_negotiated).ratio()
        return similarity
    
    def generate_implementation_plan(self):
        """生成详细实施计划"""
        print("\n" + "="*80)
        print("详细实施计划")
        print("="*80)
        
        plan = """
🎯 实施步骤详解：

1️⃣ 数据预处理阶段
   ✅ 读取谈判药数据，确认A/C/F/G列内容
   ✅ 读取9个医院数据文件，智能识别销售制剂量和销售金额列
   ✅ 统计各年份各类别医院数量
   
2️⃣ 药品匹配阶段  
   🔄 使用三级匹配策略：
      - 精确匹配（优先级最高）
      - 标准化匹配（去除括号、空格）
      - 模糊匹配（相似度>90%）
   
3️⃣ 数据聚合阶段
   📊 按年份、医院类别、药品类型聚合数据
   📈 计算进院率：进院医院数/该类别医院总数
   💰 汇总销售金额和制剂量
   
4️⃣ 表格生成阶段
   📋 生成四个表格：
      - 所有谈判药（亿为单位）
      - 首谈药（亿为单位）  
      - 续约药（亿为单位）
      - 创新药（万为单位）

🚨 需要确认的关键问题：

❓ 谈判类别F列的具体值格式？
❓ 创新药G列的标识方式？
❓ 原始数据的金额和制剂量单位？
❓ 进院率计算是否包含零销售记录？
❓ 同一医院同一药品多条记录如何处理？

💡 建议的解决方案：

1. 先运行数据结构分析，确认各列内容格式
2. 根据实际数据调整匹配算法参数
3. 设置数据验证检查点，确保结果准确性
4. 生成详细的匹配报告，便于人工核查

🎯 预期输出：

📊 四个标准化表格，包含：
   - 年份、医院类型
   - 医院用量（按指定单位）
   - 占三级公立医院比(%)
   - 销售金额（按指定单位）
   - 占三级公立医院比(%)
        """
        
        print(plan)
        
        return plan

def main():
    """主函数 - 执行完整的实施计划"""
    analyzer = NegotiatedDrugsAnalyzer()
    
    print("🌟 仙尊大人，开始执行谈判药品分析实施计划")
    
    # 第一阶段：分析数据结构
    if not analyzer.analyze_negotiated_drugs_structure():
        print("❌ 谈判药数据分析失败，无法继续")
        return
    
    # 第二阶段：分析医院数据
    analyzer.analyze_hospital_data_structure()
    
    # 第三阶段：生成实施计划
    analyzer.generate_implementation_plan()
    
    print("\n🎊 仙尊大人，实施计划分析完成！")
    print("请确认上述关键问题后，我将开始正式实施数据处理。")

if __name__ == "__main__":
    main()
