import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from data_preprocessor import DataPreprocessor
from hospital_classifier_step2 import HospitalClassifier
from drug_matcher import DrugMatcher

class DataAggregatorFinal:
    """最终版数据聚合计算器 - 修正数据丢失问题"""
    
    def __init__(self, preprocessor: DataPreprocessor, classifier: HospitalClassifier, matcher: DrugMatcher):
        self.preprocessor = preprocessor
        self.classifier = classifier
        self.matcher = matcher
        self.aggregated_results = {}
        
        # 医院总数将根据实际数据动态计算
        self.hospital_totals = {}
    
    def calculate_actual_hospital_totals(self, year: int) -> Dict[str, int]:
        """计算指定年份的实际医院总数"""
        if year not in self.preprocessor.hospital_data:
            return {}
        
        df = self.preprocessor.hospital_data[year]
        
        # 统计各类医院的实际数量
        hospital_counts = df.groupby('医院分类')['机构名称'].nunique().to_dict()
        
        # 确保所有类别都存在
        totals = {
            '委属医院': hospital_counts.get('委属医院', 0),
            '市属医院': hospital_counts.get('市属医院', 0),
            '其他医院': hospital_counts.get('其他医院', 0)
        }
        
        # 计算总计
        totals['三级医院总计'] = sum(totals.values())
        
        print(f"{year}年实际医院总数统计:")
        for category, count in totals.items():
            print(f"  {category}: {count}家")
        
        return totals
    
    def clean_and_aggregate_data(self, year: int) -> Dict[str, pd.DataFrame]:
        """清理数据并聚合"""
        print(f"正在清理并聚合{year}年数据...")
        
        if year not in self.matcher.matched_data:
            print(f"错误: {year}年匹配数据不存在")
            return {}
        
        df = self.matcher.matched_data[year].copy()
        print(f"原始匹配数据: {len(df)}条记录")
        print(f"原始总金额: {df['销售金额_标准'].sum()/100000000:.4f}亿元")
        print(f"原始总用量: {df['销售制剂量_标准'].sum()/100000000:.4f}亿")
        
        # 获取实际医院总数
        hospital_totals = self.calculate_actual_hospital_totals(year)
        self.hospital_totals[year] = hospital_totals
        
        # 清理"是否创新药"字段，将NaN替换为"非创新药"
        df['是否创新药_清理'] = df['是否创新药'].fillna('非创新药')
        
        print(f"清理后创新药分布:")
        print(df['是否创新药_清理'].value_counts())
        
        # 按医院分类直接聚合，不按药品类别分组
        results = {}
        
        # 1. 所有谈判药 - 按医院分类聚合
        all_drugs_agg = df.groupby('医院分类').agg({
            '销售金额_标准': 'sum',
            '销售制剂量_标准': 'sum',
            '机构名称': 'nunique',
            '标准化药品名': 'nunique'
        }).reset_index()
        
        all_drugs_agg['谈判类别'] = '所有谈判药'
        all_drugs_agg['是否创新药'] = '所有'
        results['所有谈判药'] = all_drugs_agg
        
        # 2. 首谈药 - 按医院分类聚合
        first_drugs = df[df['谈判类别'] == '首谈']
        if len(first_drugs) > 0:
            first_drugs_agg = first_drugs.groupby('医院分类').agg({
                '销售金额_标准': 'sum',
                '销售制剂量_标准': 'sum',
                '机构名称': 'nunique',
                '标准化药品名': 'nunique'
            }).reset_index()
            first_drugs_agg['谈判类别'] = '首谈药'
            first_drugs_agg['是否创新药'] = '所有'
            results['首谈药'] = first_drugs_agg
        else:
            results['首谈药'] = pd.DataFrame()
        
        # 3. 续约药 - 按医院分类聚合
        renewal_drugs = df[df['谈判类别'] == '续约']
        if len(renewal_drugs) > 0:
            renewal_drugs_agg = renewal_drugs.groupby('医院分类').agg({
                '销售金额_标准': 'sum',
                '销售制剂量_标准': 'sum',
                '机构名称': 'nunique',
                '标准化药品名': 'nunique'
            }).reset_index()
            renewal_drugs_agg['谈判类别'] = '续约药'
            renewal_drugs_agg['是否创新药'] = '所有'
            results['续约药'] = renewal_drugs_agg
        else:
            results['续约药'] = pd.DataFrame()
        
        # 4. 创新药 - 按医院分类聚合
        innovation_drugs = df[df['是否创新药_清理'] == '创新药']
        if len(innovation_drugs) > 0:
            innovation_drugs_agg = innovation_drugs.groupby('医院分类').agg({
                '销售金额_标准': 'sum',
                '销售制剂量_标准': 'sum',
                '机构名称': 'nunique',
                '标准化药品名': 'nunique'
            }).reset_index()
            innovation_drugs_agg['谈判类别'] = '创新药'
            innovation_drugs_agg['是否创新药'] = '创新药'
            results['创新药'] = innovation_drugs_agg
        else:
            results['创新药'] = pd.DataFrame()
        
        # 为所有结果添加标准列名和计算进院率
        for category, result_df in results.items():
            if len(result_df) > 0:
                result_df.rename(columns={
                    '销售金额_标准': '销售金额',
                    '销售制剂量_标准': '医院用量',
                    '机构名称': '进院医院数',
                    '标准化药品名': '药品种类数'
                }, inplace=True)
                
                # 添加医院总数和计算进院率
                result_df['医院总数'] = result_df['医院分类'].map(hospital_totals)
                result_df['平均进院率'] = (result_df['进院医院数'] / result_df['医院总数'] * 100).round(2)
                
                # 转换单位
                if category == '创新药':
                    # 创新药使用万元单位
                    result_df['销售金额_万元'] = (result_df['销售金额'] / 10000).round(2)
                    result_df['医院用量_万'] = (result_df['医院用量'] / 10000).round(2)
                else:
                    # 其他使用亿元单位
                    result_df['销售金额_亿元'] = (result_df['销售金额'] / 100000000).round(4)
                    result_df['医院用量_亿'] = (result_df['医院用量'] / 100000000).round(4)
                
                print(f"{category}: {len(result_df)}行数据, 总金额{result_df['销售金额'].sum()/100000000:.4f}亿元")
        
        return results
    
    def aggregate_all_years(self) -> Dict[int, Dict[str, pd.DataFrame]]:
        """聚合所有年份的数据"""
        print("正在聚合所有年份数据...")
        
        all_results = {}
        
        for year in [2021, 2022, 2023]:
            if year in self.matcher.matched_data:
                year_results = self.clean_and_aggregate_data(year)
                all_results[year] = year_results
                
                print(f"{year}年聚合完成:")
                for category, df in year_results.items():
                    if len(df) > 0:
                        total_amount = df['销售金额'].sum()
                        print(f"  {category}: {len(df)}行数据, 总金额{total_amount/100000000:.4f}亿元")
        
        self.aggregated_results = all_results
        return all_results
    
    def get_summary_statistics(self):
        """获取汇总统计"""
        print("\n=== 最终版数据聚合汇总统计 ===")
        
        # 计算三年总计
        category_totals = {}
        
        for year, year_data in self.aggregated_results.items():
            print(f"\n{year}年:")
            print(f"  医院总数统计: {self.hospital_totals[year]}")
            
            for category, df in year_data.items():
                if len(df) > 0:
                    total_amount = df['销售金额'].sum()
                    total_volume = df['医院用量'].sum()
                    
                    if category not in category_totals:
                        category_totals[category] = {'amount': 0, 'volume': 0}
                    
                    category_totals[category]['amount'] += total_amount
                    category_totals[category]['volume'] += total_volume
                    
                    if category == '创新药':
                        print(f"  {category}: {len(df)}行, 销售金额{total_amount/10000:.2f}万元, 用量{total_volume/10000:.2f}万")
                    else:
                        print(f"  {category}: {len(df)}行, 销售金额{total_amount/100000000:.4f}亿元, 用量{total_volume/100000000:.4f}亿")
        
        print("\n=== 三年总计统计 ===")
        for category, totals in category_totals.items():
            total_amount = totals['amount']
            total_volume = totals['volume']
            
            if category == '创新药':
                print(f"{category}: 销售金额{total_amount/10000:.2f}万元, 用量{total_volume/10000:.2f}万")
            else:
                print(f"{category}: 销售金额{total_amount/100000000:.4f}亿元, 用量{total_volume/100000000:.4f}亿")

if __name__ == "__main__":
    # 测试最终版数据聚合
    preprocessor = DataPreprocessor()
    
    # 加载数据
    preprocessor.load_hospital_classification()
    preprocessor.load_negotiated_drugs()
    
    for year in [2021, 2022, 2023]:
        preprocessor.load_hospital_data(year)
    
    # 创建分类器
    classifier = HospitalClassifier(preprocessor)
    classifier.create_hospital_mapping()
    
    for year in [2021, 2022, 2023]:
        classified_df = classifier.classify_hospitals_in_data(year)
        preprocessor.hospital_data[year] = classified_df
    
    # 创建匹配器
    matcher = DrugMatcher(preprocessor, classifier)
    for year in [2021, 2022, 2023]:
        matcher.match_negotiated_drugs(year)
    
    # 创建最终版聚合器
    aggregator = DataAggregatorFinal(preprocessor, classifier, matcher)
    results = aggregator.aggregate_all_years()
    
    # 显示统计
    aggregator.get_summary_statistics()
    
    print("\n最终版数据聚合计算完成！")
