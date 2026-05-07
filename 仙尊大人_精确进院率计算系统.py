#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仙尊大人_精确进院率计算系统
根据药品在医院的实际出现情况计算精确的进院率
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class PreciseEntryRateCalculator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.results = {}
        self.hospital_counts = {
            '2021': {'一级': 0, '二级': 0, '三级': 0},
            '2022': {'一级': 0, '二级': 0, '三级': 0},
            '2023': {'一级': 0, '二级': 0, '三级': 0}
        }
        self.drug_hospital_data = {}  # 存储每个药品在各医院的使用情况
        
    def analyze_drug_hospital_distribution(self, df, year, level, sheet_name):
        """分析药品在医院的分布情况"""
        print(f"\n分析 {year}年{level}医院 药品分布...")
        
        # 获取医院名称列和药品名称列
        hospital_col = df.columns[0]  # 假设第一列是医院名称
        drug_col = '产品通用名'  # 药品名称列
        insurance_col = '是否医保用药'  # 医保状态列
        
        if drug_col not in df.columns:
            print(f"警告: 未找到药品名称列 {drug_col}")
            return
            
        # 统计每个药品在多少个医院出现
        drug_hospital_count = df.groupby(drug_col)[hospital_col].nunique().to_dict()
        
        # 统计总医院数
        total_hospitals = df[hospital_col].nunique()
        self.hospital_counts[year][level] = total_hospitals
        
        # 分析医保状态
        for drug_name, hospital_count in drug_hospital_count.items():
            # 获取该药品的医保状态
            drug_data = df[df[drug_col] == drug_name]
            insurance_status = 'Y' if (drug_data[insurance_col] == 'Y').any() else 'N'
            
            # 计算进院率
            entry_rate = (hospital_count / total_hospitals) * 100
            
            # 存储数据
            key = f"{year}_{level}"
            if key not in self.drug_hospital_data:
                self.drug_hospital_data[key] = {
                    'total_hospitals': total_hospitals,
                    'drugs': {},
                    'insurance_drugs': {},
                    'non_insurance_drugs': {}
                }
            
            self.drug_hospital_data[key]['drugs'][drug_name] = {
                'hospital_count': hospital_count,
                'entry_rate': entry_rate,
                'insurance_status': insurance_status
            }
            
            # 按医保状态分类
            if insurance_status == 'Y':
                self.drug_hospital_data[key]['insurance_drugs'][drug_name] = {
                    'hospital_count': hospital_count,
                    'entry_rate': entry_rate
                }
            else:
                self.drug_hospital_data[key]['non_insurance_drugs'][drug_name] = {
                    'hospital_count': hospital_count,
                    'entry_rate': entry_rate
                }
        
        print(f"  总医院数: {total_hospitals}")
        print(f"  药品种类数: {len(drug_hospital_count)}")
        print(f"  医保药品数: {len(self.drug_hospital_data[key]['insurance_drugs'])}")
        print(f"  非医保药品数: {len(self.drug_hospital_data[key]['non_insurance_drugs'])}")
    
    def calculate_average_entry_rates(self):
        """计算各类药品的平均进院率"""
        print(f"\n{'='*60}")
        print("计算平均进院率...")
        print(f"{'='*60}")
        
        for key, data in self.drug_hospital_data.items():
            year, level = key.split('_')
            print(f"\n{year}年{level}医院:")
            
            # 计算总创新药平均进院率（简单平均）
            all_drugs = data['drugs']
            if all_drugs:
                total_entry_rates = [drug_info['entry_rate'] for drug_info in all_drugs.values()]
                avg_total_entry_rate = np.mean(total_entry_rates)
                data['avg_total_entry_rate'] = avg_total_entry_rate
                print(f"  总创新药平均进院率: {avg_total_entry_rate:.2f}%")
            else:
                data['avg_total_entry_rate'] = 0.0
            
            # 计算医保创新药平均进院率
            insurance_drugs = data['insurance_drugs']
            if insurance_drugs:
                insurance_entry_rates = [drug_info['entry_rate'] for drug_info in insurance_drugs.values()]
                avg_insurance_entry_rate = np.mean(insurance_entry_rates)
                data['avg_insurance_entry_rate'] = avg_insurance_entry_rate
                print(f"  医保创新药平均进院率: {avg_insurance_entry_rate:.2f}%")
            else:
                data['avg_insurance_entry_rate'] = 0.0
            
            # 计算非医保创新药平均进院率
            non_insurance_drugs = data['non_insurance_drugs']
            if non_insurance_drugs:
                non_insurance_entry_rates = [drug_info['entry_rate'] for drug_info in non_insurance_drugs.values()]
                avg_non_insurance_entry_rate = np.mean(non_insurance_entry_rates)
                data['avg_non_insurance_entry_rate'] = avg_non_insurance_entry_rate
                print(f"  非医保创新药平均进院率: {avg_non_insurance_entry_rate:.2f}%")
            else:
                data['avg_non_insurance_entry_rate'] = 0.0
    
    def calculate_weighted_entry_rates(self):
        """计算不同年份不同医院级别的加权平均进院率"""
        print(f"\n{'='*60}")
        print("计算加权平均进院率...")
        print(f"{'='*60}")
        
        # 按级别计算加权平均
        level_weighted_rates = {}
        
        for level in ['一级', '二级', '三级']:
            print(f"\n{level}医院加权平均进院率:")
            
            # 收集该级别所有年份的数据
            level_data = []
            total_hospitals = 0
            
            for year in ['2021', '2022', '2023']:
                key = f"{year}_{level}"
                if key in self.drug_hospital_data:
                    data = self.drug_hospital_data[key]
                    hospital_count = data['total_hospitals']
                    total_hospitals += hospital_count
                    
                    level_data.append({
                        'year': year,
                        'hospital_count': hospital_count,
                        'avg_total_entry_rate': data.get('avg_total_entry_rate', 0),
                        'avg_insurance_entry_rate': data.get('avg_insurance_entry_rate', 0),
                        'avg_non_insurance_entry_rate': data.get('avg_non_insurance_entry_rate', 0)
                    })
            
            if level_data and total_hospitals > 0:
                # 计算加权平均
                weighted_total = sum(d['avg_total_entry_rate'] * d['hospital_count'] for d in level_data) / total_hospitals
                weighted_insurance = sum(d['avg_insurance_entry_rate'] * d['hospital_count'] for d in level_data) / total_hospitals
                weighted_non_insurance = sum(d['avg_non_insurance_entry_rate'] * d['hospital_count'] for d in level_data) / total_hospitals
                
                level_weighted_rates[level] = {
                    'weighted_total_entry_rate': weighted_total,
                    'weighted_insurance_entry_rate': weighted_insurance,
                    'weighted_non_insurance_entry_rate': weighted_non_insurance,
                    'total_hospitals': total_hospitals
                }
                
                print(f"  总创新药加权平均进院率: {weighted_total:.2f}%")
                print(f"  医保创新药加权平均进院率: {weighted_insurance:.2f}%")
                print(f"  非医保创新药加权平均进院率: {weighted_non_insurance:.2f}%")
                print(f"  总医院数: {total_hospitals}")
        
        return level_weighted_rates
    
    def run_analysis(self):
        """运行完整分析"""
        print("开始精确进院率计算...")
        print(f"文件路径: {self.file_path}")
        
        try:
            # 获取所有工作表名称
            xl_file = pd.ExcelFile(self.file_path)
            sheet_names = xl_file.sheet_names
            print(f"发现 {len(sheet_names)} 个工作表: {sheet_names}")
            
            # 分析每个工作表
            for sheet_name in sheet_names:
                if '综合汇总' in sheet_name:
                    continue
                    
                try:
                    df = pd.read_excel(self.file_path, sheet_name=sheet_name)
                    
                    # 提取年份和级别
                    year = None
                    level = None
                    
                    for y in ['2021', '2022', '2023']:
                        if y in sheet_name:
                            year = y
                            break
                    
                    if '一级' in sheet_name:
                        level = '一级'
                    elif '二级' in sheet_name:
                        level = '二级'
                    elif '三级' in sheet_name:
                        level = '三级'
                    
                    if year and level:
                        self.analyze_drug_hospital_distribution(df, year, level, sheet_name)
                    
                except Exception as e:
                    print(f"分析工作表 {sheet_name} 时出错: {str(e)}")
                    continue
            
            # 计算平均进院率
            self.calculate_average_entry_rates()
            
            # 计算加权平均进院率
            level_weighted_rates = self.calculate_weighted_entry_rates()
            
            # 保存结果
            self.save_results(level_weighted_rates)
            
        except Exception as e:
            print(f"分析过程中出错: {str(e)}")
    
    def save_results(self, level_weighted_rates):
        """保存分析结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"仙尊大人_精确进院率分析结果_{timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 详细药品进院率数据
                detail_data = []
                for key, data in self.drug_hospital_data.items():
                    year, level = key.split('_')
                    for drug_name, drug_info in data['drugs'].items():
                        detail_data.append({
                            '年份': year,
                            '医院级别': level,
                            '药品名称': drug_name,
                            '进院医院数': drug_info['hospital_count'],
                            '总医院数': data['total_hospitals'],
                            '进院率(%)': drug_info['entry_rate'],
                            '医保状态': drug_info['insurance_status']
                        })
                
                detail_df = pd.DataFrame(detail_data)
                detail_df.to_excel(writer, sheet_name='详细药品进院率', index=False)
                
                # 平均进院率汇总
                summary_data = []
                for key, data in self.drug_hospital_data.items():
                    year, level = key.split('_')
                    summary_data.append({
                        '年份': year,
                        '医院级别': level,
                        '总医院数': data['total_hospitals'],
                        '总药品数': len(data['drugs']),
                        '医保药品数': len(data['insurance_drugs']),
                        '非医保药品数': len(data['non_insurance_drugs']),
                        '总创新药平均进院率(%)': data.get('avg_total_entry_rate', 0),
                        '医保创新药平均进院率(%)': data.get('avg_insurance_entry_rate', 0),
                        '非医保创新药平均进院率(%)': data.get('avg_non_insurance_entry_rate', 0)
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='平均进院率汇总', index=False)
                
                # 加权平均进院率
                weighted_data = []
                for level, rates in level_weighted_rates.items():
                    weighted_data.append({
                        '医院级别': level,
                        '总医院数': rates['total_hospitals'],
                        '总创新药加权平均进院率(%)': rates['weighted_total_entry_rate'],
                        '医保创新药加权平均进院率(%)': rates['weighted_insurance_entry_rate'],
                        '非医保创新药加权平均进院率(%)': rates['weighted_non_insurance_entry_rate']
                    })
                
                weighted_df = pd.DataFrame(weighted_data)
                weighted_df.to_excel(writer, sheet_name='加权平均进院率', index=False)
            
            print(f"\n精确进院率分析结果已保存到: {output_file}")
            
        except Exception as e:
            print(f"保存结果时出错: {str(e)}")

def main():
    """主函数"""
    file_path = "仙尊大人_创新药医院数据完整匹配结果_10工作表版_20250908_144656.xlsx"
    
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        return
    
    # 创建分析器并运行分析
    calculator = PreciseEntryRateCalculator(file_path)
    calculator.run_analysis()

if __name__ == "__main__":
    main()
