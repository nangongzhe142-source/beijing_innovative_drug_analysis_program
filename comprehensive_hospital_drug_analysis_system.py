#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仙尊大人的完整多维度医院药品数据分析系统
整合医院数据、医院分类、创新药匹配的综合分析
"""

import pandas as pd
import numpy as np
import os
import chardet
from pathlib import Path
import warnings
import json
from datetime import datetime
warnings.filterwarnings('ignore')

class ComprehensiveHospitalDrugAnalyzer:
    def __init__(self):
        self.data_years = ['2021年', '2022年', '2023年']
        self.hospital_levels = {
            '一级': ['基层', '_1', '1.csv', '1.xlsx'],
            '二级': ['_2', '2.csv', '2.xlsx'],
            '三级': ['_3', '3.csv', '3.xlsx']
        }
        
        # 数据存储
        self.all_hospital_data = []
        self.hospital_classification = {}
        self.innovative_drugs = set()
        self.analysis_results = {}
        
        # 文件路径
        self.hospital_list_file = "北京医院完整名单_20250623_084503.csv"
        self.innovative_drugs_file = "最终_纯化学创新药名单.xlsx"
        
        print("仙尊大人，综合分析系统初始化完成！")
    
    def detect_encoding(self, file_path):
        """检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                
            # 常见编码映射
            encoding_map = {
                'GB2312': 'gb18030',
                'GBK': 'gb18030', 
                'gb2312': 'gb18030',
                'gbk': 'gb18030'
            }
            
            return encoding_map.get(encoding, encoding or 'utf-8')
        except:
            return 'utf-8'
    
    def load_hospital_classification(self):
        """加载医院分类数据"""
        print("\n=== 第一步：加载医院分类数据 ===")
        
        try:
            # 尝试不同编码读取CSV文件
            encodings = ['gb18030', 'gbk', 'utf-8', 'gb2312']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(self.hospital_list_file, encoding=encoding)
                    print(f"成功使用编码 {encoding} 读取医院分类文件")
                    break
                except:
                    continue
            
            if df is None:
                print("⚠ 无法读取医院分类文件，将使用默认分类")
                return False
            
            print(f"医院分类数据形状: {df.shape}")
            print(f"列名: {list(df.columns)}")
            
            # 处理医院分类
            if len(df.columns) >= 2:
                hospital_col = df.columns[1]  # B列：医院名称
                
                # 前11个是委属医院，后22个是市属医院
                for idx, row in df.iterrows():
                    hospital_name = str(row[hospital_col]).strip()
                    if hospital_name and hospital_name != 'nan':
                        if idx < 11:  # 前11个
                            self.hospital_classification[hospital_name] = '委属医院'
                        elif idx < 33:  # 后22个
                            self.hospital_classification[hospital_name] = '市属医院'
                        else:
                            self.hospital_classification[hospital_name] = '其他三级医院'
                
                print(f"成功加载医院分类: 委属医院 {sum(1 for v in self.hospital_classification.values() if v == '委属医院')} 家")
                print(f"                市属医院 {sum(1 for v in self.hospital_classification.values() if v == '市属医院')} 家")
                print(f"                其他三级医院 {sum(1 for v in self.hospital_classification.values() if v == '其他三级医院')} 家")
                
                return True
            else:
                print("⚠ 医院分类文件格式不正确")
                return False
                
        except Exception as e:
            print(f"加载医院分类时出错: {str(e)}")
            return False
    
    def load_innovative_drugs(self):
        """加载创新药名单"""
        print("\n=== 第二步：加载创新药名单 ===")

        try:
            df = pd.read_excel(self.innovative_drugs_file)
            print(f"创新药数据形状: {df.shape}")
            print(f"列名: {list(df.columns)}")

            # 查找药品名称列（通常是第二列"药品名称"）
            drug_col = None
            for col in df.columns:
                if '药品名称' in str(col) or '名称' in str(col):
                    drug_col = col
                    break

            if drug_col is None and len(df.columns) > 1:
                drug_col = df.columns[1]  # 默认使用第二列

            if drug_col is not None:
                drugs = df[drug_col].dropna().astype(str).str.strip()
                # 过滤掉明显不是药品名称的数据
                drugs = drugs[drugs.str.len() > 2]  # 长度大于2
                drugs = drugs[~drugs.str.isdigit()]  # 不是纯数字
                self.innovative_drugs = set(drugs)

                print(f"使用列: {drug_col}")
                print(f"成功加载创新药 {len(self.innovative_drugs)} 种")
                print(f"创新药示例: {list(self.innovative_drugs)[:5]}")

                return True
            else:
                print("⚠ 未找到药品名称列")
                return False

        except Exception as e:
            print(f"加载创新药名单时出错: {str(e)}")
            return False
    
    def identify_hospital_level(self, filename):
        """识别医院级别"""
        filename_lower = filename.lower()
        
        if '基层' in filename:
            return '一级'
        elif filename_lower.endswith('_1.csv') or filename_lower.endswith('1.csv'):
            return '一级'
        elif filename_lower.endswith('_2.csv') or filename_lower.endswith('2.csv'):
            return '二级'
        elif filename_lower.endswith('_3.csv') or filename_lower.endswith('3.csv'):
            return '三级'
        elif '一级' in filename:
            return '一级'
        elif '二级' in filename:
            return '二级'
        elif '三级' in filename:
            return '三级'
        else:
            return '未知'
    
    def load_hospital_data(self):
        """加载所有医院数据"""
        print("\n=== 第三步：加载医院数据 ===")
        
        total_records = 0
        
        for year in self.data_years:
            year_path = Path(year)
            if not year_path.exists():
                print(f"警告: 年份文件夹 {year} 不存在")
                continue
                
            print(f"\n处理 {year} 数据:")
            files = list(year_path.glob('*'))
            
            for file_path in files:
                if file_path.is_file() and (file_path.suffix in ['.csv', '.xlsx']):
                    hospital_level = self.identify_hospital_level(file_path.name)
                    
                    if hospital_level != '未知':
                        print(f"  读取: {file_path.name} ({hospital_level})")
                        
                        try:
                            # 读取文件
                            if file_path.suffix == '.xlsx':
                                df = pd.read_excel(str(file_path))
                            else:
                                encoding = self.detect_encoding(str(file_path))
                                df = pd.read_csv(str(file_path), encoding=encoding)
                            
                            # 添加元数据
                            df['年份'] = year
                            df['医院级别'] = hospital_level
                            df['文件名'] = file_path.name
                            
                            self.all_hospital_data.append(df)
                            total_records += len(df)
                            
                            print(f"    成功加载 {len(df)} 条记录")
                            
                        except Exception as e:
                            print(f"    读取失败: {str(e)}")
        
        print(f"\n总计加载 {len(self.all_hospital_data)} 个文件，{total_records:,} 条记录")
        return len(self.all_hospital_data) > 0
    
    def standardize_data_columns(self):
        """标准化数据列名"""
        print("\n=== 第四步：标准化数据列名 ===")

        for i, df in enumerate(self.all_hospital_data):
            print(f"处理文件 {i+1}: {df['文件名'].iloc[0]}")

            # 显示原始列名
            original_cols = list(df.columns)
            print(f"  原始列名: {original_cols[:10]}...")

            # 标准化列名映射 - 避免重复映射
            column_mapping = {}
            mapped_targets = set()

            # 查找关键列
            for idx, col in enumerate(df.columns):
                col_str = str(col).strip()

                # A列：医院名称 (只映射第一个匹配的)
                if 'hospital_name' not in mapped_targets and (idx == 0 or ('机构' in col_str and '名称' in col_str)):
                    column_mapping[col] = 'hospital_name'
                    mapped_targets.add('hospital_name')

                # H列：药品名称 (第8列，索引7，或包含"通用名")
                elif 'drug_name' not in mapped_targets and (idx == 7 or ('通用名' in col_str and '产品' in col_str)):
                    column_mapping[col] = 'drug_name'
                    mapped_targets.add('drug_name')

                # I、J、K列：销售金额和销售制剂量
                elif 'sales_amount' not in mapped_targets and '销售金额' in col_str:
                    column_mapping[col] = 'sales_amount'
                    mapped_targets.add('sales_amount')
                elif 'sales_volume' not in mapped_targets and ('销售制剂量' in col_str or ('销售' in col_str and ('制剂量' in col_str or '包装量' in col_str))):
                    column_mapping[col] = 'sales_volume'
                    mapped_targets.add('sales_volume')

                # Y列：医保标识
                elif 'insurance_status' not in mapped_targets and ('医保' in col_str or idx == 24):
                    column_mapping[col] = 'insurance_status'
                    mapped_targets.add('insurance_status')

            # 应用列名映射
            if column_mapping:
                df.rename(columns=column_mapping, inplace=True)

            print(f"  映射关系: {column_mapping}")
            print(f"  标准化后关键列: {[col for col in df.columns if col in ['hospital_name', 'drug_name', 'sales_amount', 'sales_volume', 'insurance_status']]}")
    
    def process_insurance_status(self):
        """处理医保状态"""
        print("\n=== 第五步：处理医保状态 ===")
        
        for i, df in enumerate(self.all_hospital_data):
            if 'insurance_status' in df.columns:
                # 标准化医保状态
                df['is_insurance'] = df['insurance_status'].apply(
                    lambda x: '医保药' if str(x).upper() == 'Y' else '非医保药'
                )
                
                # 统计分布
                insurance_counts = df['is_insurance'].value_counts()
                print(f"文件 {i+1} 医保状态分布: {dict(insurance_counts)}")
    
    def match_hospital_classification(self):
        """匹配医院分类"""
        print("\n=== 第六步：匹配医院分类 ===")
        
        for i, df in enumerate(self.all_hospital_data):
            if 'hospital_name' in df.columns:
                # 匹配医院属性
                df['hospital_type'] = df['hospital_name'].apply(
                    lambda x: self.hospital_classification.get(str(x).strip(), '其他医院')
                )
                
                # 统计匹配结果
                type_counts = df['hospital_type'].value_counts()
                print(f"文件 {i+1} 医院类型分布: {dict(type_counts)}")
    
    def match_innovative_drugs(self):
        """匹配创新药"""
        print("\n=== 第七步：匹配创新药 ===")
        
        for i, df in enumerate(self.all_hospital_data):
            if 'drug_name' in df.columns:
                # 匹配创新药
                df['is_innovative'] = df['drug_name'].apply(
                    lambda x: '创新药' if str(x).strip() in self.innovative_drugs else '非创新药'
                )
                
                # 统计匹配结果
                innovative_counts = df['is_innovative'].value_counts()
                print(f"文件 {i+1} 创新药分布: {dict(innovative_counts)}")

    def calculate_basic_statistics(self):
        """计算基础统计数据"""
        print("\n=== 第八步：计算基础统计 ===")

        # 合并所有数据
        combined_df = pd.concat(self.all_hospital_data, ignore_index=True)

        # 转换数值列
        for col in ['sales_amount', 'sales_volume']:
            if col in combined_df.columns:
                combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0)

        # 基础统计
        total_records = len(combined_df)
        total_hospitals = combined_df['hospital_name'].nunique() if 'hospital_name' in combined_df.columns else 0
        total_drugs = combined_df['drug_name'].nunique() if 'drug_name' in combined_df.columns else 0

        # 医保药品统计
        if 'is_insurance' in combined_df.columns:
            insurance_stats = combined_df.groupby('is_insurance').agg({
                'sales_amount': 'sum',
                'sales_volume': 'sum',
                'drug_name': 'nunique'
            }).round(2)

            print("医保药品统计:")
            print(insurance_stats)

        # 创新药统计
        if 'is_innovative' in combined_df.columns:
            innovative_stats = combined_df.groupby('is_innovative').agg({
                'sales_amount': 'sum',
                'sales_volume': 'sum',
                'drug_name': 'nunique'
            }).round(2)

            print("\n创新药统计:")
            print(innovative_stats)

        # 年度统计
        yearly_stats = combined_df.groupby('年份').agg({
            'sales_amount': 'sum',
            'sales_volume': 'sum',
            'drug_name': 'nunique',
            'hospital_name': 'nunique'
        }).round(2)

        print("\n年度统计:")
        print(yearly_stats)

        # 医院级别统计
        level_stats = combined_df.groupby('医院级别').agg({
            'sales_amount': 'sum',
            'sales_volume': 'sum',
            'drug_name': 'nunique',
            'hospital_name': 'nunique'
        }).round(2)

        print("\n医院级别统计:")
        print(level_stats)

        # 保存基础统计结果
        self.analysis_results['basic_stats'] = {
            'total_records': total_records,
            'total_hospitals': total_hospitals,
            'total_drugs': total_drugs,
            'insurance_stats': insurance_stats.to_dict() if 'is_insurance' in combined_df.columns else {},
            'innovative_stats': innovative_stats.to_dict() if 'is_innovative' in combined_df.columns else {},
            'yearly_stats': yearly_stats.to_dict(),
            'level_stats': level_stats.to_dict()
        }

        return combined_df

    def calculate_top_drugs(self, combined_df):
        """计算TOP20药品"""
        print("\n=== 第九步：计算TOP20药品 ===")

        if 'sales_amount' not in combined_df.columns or 'drug_name' not in combined_df.columns:
            print("⚠ 缺少必要的列，跳过TOP药品计算")
            return

        # 只统计医保药的销售金额
        if 'is_insurance' in combined_df.columns:
            insurance_drugs = combined_df[combined_df['is_insurance'] == '医保药']
        else:
            insurance_drugs = combined_df

        # 按药品名称汇总三年销售金额
        drug_totals = insurance_drugs.groupby('drug_name').agg({
            'sales_amount': 'sum',
            'sales_volume': 'sum'
        }).reset_index()

        # 排序获取前20后20
        drug_totals_sorted = drug_totals.sort_values('sales_amount', ascending=False)

        top_20 = drug_totals_sorted.head(20)
        bottom_20 = drug_totals_sorted.tail(20)

        print(f"销售金额前20名药品:")
        for i, (_, row) in enumerate(top_20.iterrows(), 1):
            print(f"{i:2d}. {row['drug_name']}: {row['sales_amount']:,.2f}元")

        print(f"\n销售金额后20名药品:")
        for i, (_, row) in enumerate(bottom_20.iterrows(), 1):
            print(f"{i:2d}. {row['drug_name']}: {row['sales_amount']:,.2f}元")

        # 保存TOP药品结果
        self.analysis_results['top_drugs'] = {
            'top_20': top_20.to_dict('records'),
            'bottom_20': bottom_20.to_dict('records')
        }

        return top_20, bottom_20

def main():
    """主函数"""
    print("仙尊大人，开始执行完整的多维度医院药品数据分析...")

    analyzer = ComprehensiveHospitalDrugAnalyzer()

    # 执行分析步骤
    steps = [
        ("加载医院分类数据", analyzer.load_hospital_classification),
        ("加载创新药名单", analyzer.load_innovative_drugs),
        ("加载医院数据", analyzer.load_hospital_data),
        ("标准化数据列名", analyzer.standardize_data_columns),
        ("处理医保状态", analyzer.process_insurance_status),
        ("匹配医院分类", analyzer.match_hospital_classification),
        ("匹配创新药", analyzer.match_innovative_drugs),
    ]

    combined_df = None

    for step_name, step_func in steps:
        print(f"\n{'='*60}")
        print(f"执行步骤: {step_name}")
        print(f"{'='*60}")

        try:
            result = step_func()
            if result is False:
                print(f"⚠ 步骤 {step_name} 执行失败，但继续执行后续步骤")
        except Exception as e:
            print(f"❌ 步骤 {step_name} 执行出错: {str(e)}")
            continue

    # 执行分析步骤
    try:
        print(f"\n{'='*60}")
        print("执行步骤: 计算基础统计")
        print(f"{'='*60}")
        combined_df = analyzer.calculate_basic_statistics()

        print(f"\n{'='*60}")
        print("执行步骤: 计算TOP20药品")
        print(f"{'='*60}")
        analyzer.calculate_top_drugs(combined_df)

    except Exception as e:
        print(f"❌ 分析步骤执行出错: {str(e)}")

    # 保存分析结果
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"仙尊大人_完整医院药品分析结果_{timestamp}.json"

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(analyzer.analysis_results, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n📋 分析结果已保存到: {results_file}")

    except Exception as e:
        print(f"❌ 保存结果时出错: {str(e)}")

    print(f"\n🎉 仙尊大人，数据预处理完成！")
    print(f"📊 已加载 {len(analyzer.all_hospital_data)} 个数据文件")
    print(f"🏥 医院分类: {len(analyzer.hospital_classification)} 家医院")
    print(f"💊 创新药: {len(analyzer.innovative_drugs)} 种药品")

    if combined_df is not None:
        print(f"📈 总记录数: {len(combined_df):,} 条")
        print(f"🏥 医院总数: {combined_df['hospital_name'].nunique() if 'hospital_name' in combined_df.columns else 0} 家")
        print(f"💊 药品总数: {combined_df['drug_name'].nunique() if 'drug_name' in combined_df.columns else 0} 种")

if __name__ == "__main__":
    main()
