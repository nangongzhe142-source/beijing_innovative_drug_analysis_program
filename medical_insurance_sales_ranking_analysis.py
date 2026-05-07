#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仙尊大人的医保药品销售金额排名分析系统
处理2021-2023年三年医院数据，分析医保药品销售金额前十后十名
特殊处理：医保状态变化的药品只计算医保药年份的数据
"""

import pandas as pd
import numpy as np
import os
import chardet
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class MedicalInsuranceSalesRankingAnalyzer:
    def __init__(self):
        self.data_years = ['2021年', '2022年', '2023年']
        self.hospital_levels = {
            '一级': ['基层', '_1', '1.csv', '1.xlsx'],
            '二级': ['_2', '2.csv', '2.xlsx'],
            '三级': ['_3', '3.csv', '3.xlsx']
        }
        self.all_data = []
        self.medical_insurance_data = None
        self.drug_status_changes = []
        
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
    
    def identify_hospital_level(self, filename):
        """识别医院级别"""
        filename_lower = filename.lower()
        
        if '基层' in filename:
            return '一级'
        elif filename_lower.endswith('_1.csv') or filename_lower.endswith('1.csv') or filename_lower.endswith('_1.xlsx') or filename_lower.endswith('1.xlsx'):
            return '一级'
        elif filename_lower.endswith('_2.csv') or filename_lower.endswith('2.csv') or filename_lower.endswith('_2.xlsx') or filename_lower.endswith('2.xlsx'):
            return '二级'
        elif filename_lower.endswith('_3.csv') or filename_lower.endswith('3.csv') or filename_lower.endswith('_3.xlsx') or filename_lower.endswith('3.xlsx'):
            return '三级'
        elif '一级' in filename:
            return '一级'
        elif '二级' in filename:
            return '二级'
        elif '三级' in filename:
            return '三级'
        else:
            return '未知'
    
    def identify_sales_columns(self, df):
        """智能识别销售金额和销售制剂量列"""
        sales_amount_col = None
        sales_volume_col = None
        
        # 直接查找包含关键词的列名
        for col in df.columns:
            col_name = str(col)
            if '销售金额' in col_name:
                sales_amount_col = col
            elif '销售制剂量' in col_name or '销售包装量' in col_name:
                sales_volume_col = col
        
        return sales_amount_col, sales_volume_col
    
    def process_insurance_status(self, value):
        """处理医保状态"""
        if pd.isna(value) or value == '' or str(value).upper() == 'N':
            return '非医保药'
        elif str(value).upper() == 'Y':
            return '医保药'
        else:
            return '非医保药'
    
    def read_file_data(self, file_path, year, hospital_level):
        """读取单个文件数据"""
        print(f"正在读取: {file_path} (年份: {year}, 级别: {hospital_level})")
        
        try:
            # 根据文件扩展名选择读取方式
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                # CSV文件需要检测编码
                encoding = self.detect_encoding(file_path)
                df = pd.read_csv(file_path, encoding=encoding)
            
            print(f"  - 原始数据行数: {len(df)}")
            
            # 检查必要列是否存在
            hospital_name_col = '机构名称'  # A列对应
            drug_name_col = '产品通用名'    # H列对应
            insurance_col = '是否医保用药'   # Y列对应
            
            if hospital_name_col not in df.columns or drug_name_col not in df.columns:
                print(f"  ⚠ 缺少必要列: {hospital_name_col} 或 {drug_name_col}")
                return None
            
            # 识别销售金额和销售制剂量列
            sales_amount_col, sales_volume_col = self.identify_sales_columns(df)
            
            if not sales_amount_col:
                print("  ⚠ 未找到销售金额列")
                return None
            
            print(f"  - 销售金额列: {sales_amount_col}")
            print(f"  - 销售制剂量列: {sales_volume_col}")
            print(f"  - 医保标识列: {insurance_col}")
            
            # 标准化列名和数据处理
            df_processed = df.copy()
            df_processed['hospital_name'] = df_processed[hospital_name_col]
            df_processed['drug_name'] = df_processed[drug_name_col]
            df_processed['sales_amount'] = pd.to_numeric(df_processed[sales_amount_col], errors='coerce').fillna(0)
            
            if sales_volume_col:
                df_processed['sales_volume'] = pd.to_numeric(df_processed[sales_volume_col], errors='coerce').fillna(0)
            else:
                df_processed['sales_volume'] = 0
            
            # 处理医保状态
            if insurance_col in df_processed.columns:
                df_processed['insurance_status'] = df_processed[insurance_col].apply(self.process_insurance_status)
            else:
                print(f"  ⚠ 未找到医保标识列，默认为非医保药")
                df_processed['insurance_status'] = '非医保药'
            
            # 添加年份和医院级别信息
            df_processed['year'] = year
            df_processed['hospital_level'] = hospital_level
            
            # 统计医保药分布
            insurance_counts = df_processed['insurance_status'].value_counts()
            print(f"  - 医保药分布: {dict(insurance_counts)}")
            
            return df_processed
            
        except Exception as e:
            print(f"读取文件失败 {file_path}: {str(e)}")
            return None
    
    def load_all_hospital_data(self):
        """加载所有医院数据"""
        print("开始加载医院数据...")
        
        for year in self.data_years:
            year_path = Path(year)
            if not year_path.exists():
                print(f"警告: 年份文件夹 {year} 不存在")
                continue
                
            # 获取该年份文件夹下的所有文件
            files = list(year_path.glob('*'))
            print(f"\n{year} 文件夹包含文件:")
            for f in files:
                print(f"  - {f.name}")
            
            # 处理每个文件
            for file_path in files:
                if file_path.is_file():
                    hospital_level = self.identify_hospital_level(file_path.name)
                    
                    if hospital_level != '未知':
                        df = self.read_file_data(str(file_path), year, hospital_level)
                        if df is not None:
                            self.all_data.append(df)
                    else:
                        print(f"无法识别医院级别: {file_path.name}")
        
        print(f"\n成功加载 {len(self.all_data)} 个文件")
        return len(self.all_data) > 0
    
    def extract_medical_insurance_data(self):
        """提取医保药数据并检测状态变化"""
        print("\n=== 提取医保药数据 ===")
        
        if not self.all_data:
            print("❌ 没有数据可处理")
            return False
        
        # 合并所有数据
        combined_df = pd.concat(self.all_data, ignore_index=True)
        print(f"合并后总数据行数: {len(combined_df):,}")
        
        # 统计医保药分布
        insurance_distribution = combined_df['insurance_status'].value_counts()
        print(f"医保药分布: {dict(insurance_distribution)}")
        
        # 只保留医保药数据
        self.medical_insurance_data = combined_df[combined_df['insurance_status'] == '医保药'].copy()
        print(f"医保药数据行数: {len(self.medical_insurance_data):,}")
        print(f"医保药种类数: {self.medical_insurance_data['drug_name'].nunique()}")
        
        # 检测医保状态变化的药品
        self.detect_insurance_status_changes(combined_df)
        
        return len(self.medical_insurance_data) > 0

    def detect_insurance_status_changes(self, combined_df):
        """检测医保状态变化的药品"""
        print("\n=== 检测医保状态变化 ===")

        # 按药品名称和年份统计医保状态
        drug_year_status = combined_df.groupby(['drug_name', 'year'])['insurance_status'].first().reset_index()

        # 按药品名称统计各年份的医保状态
        drug_status_pivot = drug_year_status.pivot(index='drug_name', columns='year', values='insurance_status')

        # 检测状态变化的药品
        status_changes = []

        for drug_name in drug_status_pivot.index:
            statuses = []
            for year in self.data_years:
                if year in drug_status_pivot.columns:
                    status = drug_status_pivot.loc[drug_name, year]
                    if pd.notna(status):
                        statuses.append(f"{year}:{status}")

            # 如果同一药品在不同年份有不同的医保状态，记录为状态变化
            unique_statuses = set([s.split(':')[1] for s in statuses])
            if len(unique_statuses) > 1:
                status_changes.append({
                    'drug_name': drug_name,
                    'status_by_year': ', '.join(statuses),
                    'has_medical_insurance': '医保药' in unique_statuses
                })

        self.drug_status_changes = status_changes
        print(f"发现医保状态变化的药品: {len(status_changes)} 种")

        if len(status_changes) > 0:
            print("前5个状态变化药品示例:")
            for i, change in enumerate(status_changes[:5], 1):
                print(f"  {i}. {change['drug_name']}: {change['status_by_year']}")

    def calculate_sales_ranking_with_special_rules(self):
        """计算销售金额排名（特殊规则：医保状态变化的药品只计算医保药年份）"""
        print("\n=== 计算销售金额排名（特殊规则处理）===")

        if self.medical_insurance_data is None or len(self.medical_insurance_data) == 0:
            print("❌ 没有医保药数据")
            return None, None

        # 获取所有数据（包括非医保药，用于状态变化检测）
        combined_df = pd.concat(self.all_data, ignore_index=True)

        # 创建药品-年份-医保状态映射
        drug_year_insurance = {}
        for _, row in combined_df.iterrows():
            key = (row['drug_name'], row['year'])
            drug_year_insurance[key] = row['insurance_status']

        # 按药品名称分组，应用特殊规则计算三年总和
        drug_totals = []

        for drug_name in self.medical_insurance_data['drug_name'].unique():
            total_sales_amount = 0
            total_sales_volume = 0
            yearly_details = {}

            for year in self.data_years:
                # 检查该药品在该年份的医保状态
                key = (drug_name, year)
                if key in drug_year_insurance and drug_year_insurance[key] == '医保药':
                    # 只有当该年份为医保药时，才计入统计
                    year_data = self.medical_insurance_data[
                        (self.medical_insurance_data['drug_name'] == drug_name) &
                        (self.medical_insurance_data['year'] == year)
                    ]

                    if len(year_data) > 0:
                        year_sales_amount = year_data['sales_amount'].sum()
                        year_sales_volume = year_data['sales_volume'].sum()

                        total_sales_amount += year_sales_amount
                        total_sales_volume += year_sales_volume

                        yearly_details[year] = {
                            'sales_amount': year_sales_amount,
                            'sales_volume': year_sales_volume
                        }
                    else:
                        yearly_details[year] = {
                            'sales_amount': 0,
                            'sales_volume': 0
                        }
                else:
                    # 该年份不是医保药，不计入统计
                    yearly_details[year] = {
                        'sales_amount': 0,
                        'sales_volume': 0
                    }

            if total_sales_amount > 0:  # 只保留有销售金额的药品
                drug_totals.append({
                    'drug_name': drug_name,
                    'total_sales_amount': total_sales_amount,
                    'total_sales_volume': total_sales_volume,
                    'yearly_details': yearly_details
                })

        print(f"应用特殊规则后，有销售金额的医保药数量: {len(drug_totals)}")

        # 排序获取前十后十
        drug_totals_sorted = sorted(drug_totals, key=lambda x: x['total_sales_amount'], reverse=True)

        top_10 = drug_totals_sorted[:10]
        bottom_10 = drug_totals_sorted[-10:] if len(drug_totals_sorted) >= 10 else drug_totals_sorted

        print("医保药销售金额前十名:")
        for i, drug in enumerate(top_10, 1):
            print(f"{i}. {drug['drug_name']}: {drug['total_sales_amount']:,.2f}元")

        print("\n医保药销售金额后十名（仅正数）:")
        for i, drug in enumerate(bottom_10, 1):
            rank = len(drug_totals_sorted) - len(bottom_10) + i
            print(f"{rank}. {drug['drug_name']}: {drug['total_sales_amount']:,.2f}元")

        return top_10, bottom_10

    def generate_detailed_ranking_tables(self, top_10, bottom_10):
        """生成详细的排名表格（包含年度明细）"""
        print("\n=== 生成详细排名表格 ===")

        if not top_10 or not bottom_10:
            print("❌ 没有排名数据")
            return None, None

        # 生成前十名详细表格
        top_details = []
        for i, drug in enumerate(top_10, 1):
            detail = {
                '排名': i,
                '药品名称': drug['drug_name'],
                '三年总销售金额': drug['total_sales_amount'],
                '三年总销售制剂量': drug['total_sales_volume']
            }

            # 添加年度明细
            for year in self.data_years:
                if year in drug['yearly_details']:
                    detail[f'{year}销售金额'] = drug['yearly_details'][year]['sales_amount']
                    detail[f'{year}销售制剂量'] = drug['yearly_details'][year]['sales_volume']
                else:
                    detail[f'{year}销售金额'] = 0
                    detail[f'{year}销售制剂量'] = 0

            top_details.append(detail)

        # 生成后十名详细表格
        bottom_details = []
        for i, drug in enumerate(bottom_10, 1):
            rank = len(bottom_10) - len(bottom_10) + i  # 实际排名
            detail = {
                '排名': rank,
                '药品名称': drug['drug_name'],
                '三年总销售金额': drug['total_sales_amount'],
                '三年总销售制剂量': drug['total_sales_volume']
            }

            # 添加年度明细
            for year in self.data_years:
                if year in drug['yearly_details']:
                    detail[f'{year}销售金额'] = drug['yearly_details'][year]['sales_amount']
                    detail[f'{year}销售制剂量'] = drug['yearly_details'][year]['sales_volume']
                else:
                    detail[f'{year}销售金额'] = 0
                    detail[f'{year}销售制剂量'] = 0

            bottom_details.append(detail)

        top_df = pd.DataFrame(top_details)
        bottom_df = pd.DataFrame(bottom_details)

        print(f"前十名表格生成完成，包含 {len(top_df)} 行")
        print(f"后十名表格生成完成，包含 {len(bottom_df)} 行")

        return top_df, bottom_df

    def save_results_to_excel(self, top_df, bottom_df):
        """保存结果到Excel文件"""
        print("\n=== 保存结果到Excel ===")

        filename = f"医保药品销售金额排名分析结果_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 1. 数据概览
            overview_data = []
            total_records = 0
            medical_insurance_records = 0

            for i, df in enumerate(self.all_data):
                records = len(df)
                medical_records = len(df[df['insurance_status'] == '医保药'])
                total_records += records
                medical_insurance_records += medical_records

                overview_data.append({
                    '年份': df['year'].iloc[0],
                    '医院级别': df['hospital_level'].iloc[0],
                    '总数据条数': records,
                    '医保药数据条数': medical_records,
                    '非医保药数据条数': records - medical_records,
                    '医院数量': df['hospital_name'].nunique(),
                    '药品种类': df['drug_name'].nunique(),
                    '医保药种类': df[df['insurance_status'] == '医保药']['drug_name'].nunique()
                })

            overview_df = pd.DataFrame(overview_data)
            overview_df.to_excel(writer, sheet_name='数据概览', index=False)

            # 2. 医保药销售金额前十名
            if top_df is not None and len(top_df) > 0:
                top_df.to_excel(writer, sheet_name='医保药销售金额前十名', index=False)

            # 3. 医保药销售金额后十名
            if bottom_df is not None and len(bottom_df) > 0:
                bottom_df.to_excel(writer, sheet_name='医保药销售金额后十名', index=False)

            # 4. 医保药完整排名（如果数据不太大）
            if self.medical_insurance_data is not None:
                # 生成完整排名
                complete_ranking = self.medical_insurance_data.groupby('drug_name').agg({
                    'sales_amount': 'sum',
                    'sales_volume': 'sum'
                }).reset_index()

                complete_ranking = complete_ranking[complete_ranking['sales_amount'] > 0]
                complete_ranking = complete_ranking.sort_values('sales_amount', ascending=False)
                complete_ranking['排名'] = range(1, len(complete_ranking) + 1)
                complete_ranking.columns = ['药品名称', '三年总销售金额', '三年总销售制剂量', '排名']
                complete_ranking = complete_ranking[['排名', '药品名称', '三年总销售金额', '三年总销售制剂量']]

                # 如果数据量不太大，保存完整排名
                if len(complete_ranking) <= 1000:
                    complete_ranking.to_excel(writer, sheet_name='医保药完整排名', index=False)

            # 5. 医保状态变化药品
            if self.drug_status_changes:
                status_changes_df = pd.DataFrame(self.drug_status_changes)
                status_changes_df.to_excel(writer, sheet_name='医保状态变化药品', index=False)

            # 6. 统计摘要
            summary_data = {
                '统计项目': [
                    '总数据条数',
                    '医保药数据条数',
                    '非医保药数据条数',
                    '医保药种类数',
                    '有销售金额的医保药种类数',
                    '医保状态变化药品数',
                    '前十名总销售金额',
                    '后十名总销售金额',
                    '医保药平均销售金额'
                ],
                '数值': [
                    total_records,
                    medical_insurance_records,
                    total_records - medical_insurance_records,
                    self.medical_insurance_data['drug_name'].nunique() if self.medical_insurance_data is not None else 0,
                    len(complete_ranking) if 'complete_ranking' in locals() else 0,
                    len(self.drug_status_changes),
                    f"{top_df['三年总销售金额'].sum():,.2f}元" if top_df is not None and len(top_df) > 0 else "N/A",
                    f"{bottom_df['三年总销售金额'].sum():,.2f}元" if bottom_df is not None and len(bottom_df) > 0 else "N/A",
                    f"{complete_ranking['三年总销售金额'].mean():,.2f}元" if 'complete_ranking' in locals() else "N/A"
                ]
            }

            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='统计摘要', index=False)

        print(f"结果已保存到: {filename}")
        return filename

def main():
    """主函数"""
    print("仙尊大人，开始处理医保药品销售金额排名分析...")

    analyzer = MedicalInsuranceSalesRankingAnalyzer()

    # 第一步：加载所有数据
    print("\n" + "="*60)
    print("第一步：加载医院数据")
    print("="*60)

    if not analyzer.load_all_hospital_data():
        print("❌ 数据加载失败，请检查文件结构")
        return

    print("✓ 所有文件加载成功")

    # 第二步：提取医保药数据
    print("\n" + "="*60)
    print("第二步：提取医保药数据并检测状态变化")
    print("="*60)

    if not analyzer.extract_medical_insurance_data():
        print("❌ 医保药数据提取失败")
        return

    # 第三步：计算销售金额排名（特殊规则）
    print("\n" + "="*60)
    print("第三步：计算销售金额排名（特殊规则处理）")
    print("="*60)

    top_10, bottom_10 = analyzer.calculate_sales_ranking_with_special_rules()

    if not top_10 or not bottom_10:
        print("❌ 销售金额排名计算失败")
        return

    # 第四步：生成详细排名表格
    print("\n" + "="*60)
    print("第四步：生成详细排名表格")
    print("="*60)

    top_df, bottom_df = analyzer.generate_detailed_ranking_tables(top_10, bottom_10)

    if top_df is None or bottom_df is None:
        print("❌ 详细表格生成失败")
        return

    # 第五步：保存结果
    print("\n" + "="*60)
    print("第五步：保存分析结果")
    print("="*60)

    filename = analyzer.save_results_to_excel(top_df, bottom_df)

    # 最终总结
    print("\n" + "="*60)
    print("🎉 仙尊大人，医保药品销售金额排名分析完成！")
    print("="*60)
    print(f"📊 结果文件: {filename}")
    print("📈 包含内容:")
    print("  - 数据概览（9个文件的基本统计）")
    print("  - 医保药销售金额前十名（含年度明细）")
    print("  - 医保药销售金额后十名（含年度明细）")
    print("  - 医保药完整排名（如果数据量适中）")
    print("  - 医保状态变化药品清单")
    print("  - 统计摘要")

    print(f"\n🎯 关键指标:")
    if len(top_df) > 0:
        print(f"  - 前十名总销售金额: {top_df['三年总销售金额'].sum():,.2f}元")
        print(f"  - 销售金额冠军: {top_df.iloc[0]['药品名称']} ({top_df.iloc[0]['三年总销售金额']:,.2f}元)")

    if len(bottom_df) > 0:
        print(f"  - 后十名总销售金额: {bottom_df['三年总销售金额'].sum():,.2f}元")

    print(f"  - 医保状态变化药品: {len(analyzer.drug_status_changes)} 种")

    print(f"\n📋 特殊处理说明:")
    print(f"  - 医保状态变化的药品只计算医保药年份的销售数据")
    print(f"  - 年度明细包含销售金额和销售制剂量")
    print(f"  - 排除销售金额为0或负数的药品")

if __name__ == "__main__":
    main()
