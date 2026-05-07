#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仙尊大人的创新药销售分析系统
分析2021-2023年医院数据，匹配创新药名单，统计销售金额
"""

import pandas as pd
import numpy as np
import os
import chardet
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class InnovativeDrugAnalyzer:
    def __init__(self):
        self.data_years = ['2021年', '2022年', '2023年']
        self.hospital_levels = {
            '一级': ['基层', '_1', '1.csv', '1.xlsx'],
            '二级': ['_2', '2.csv', '2.xlsx'],
            '三级': ['_3', '3.csv', '3.xlsx']
        }
        self.all_data = []
        self.innovative_drugs_list = []
        self.matched_data = []
        
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
    
    def load_innovative_drugs_list(self):
        """加载创新药名单"""
        try:
            df = pd.read_excel('创新药名单.xlsx')
            print(f"创新药名单文件列名: {list(df.columns)}")
            
            if 'B' in df.columns:
                drug_column = 'B'
            elif len(df.columns) >= 2:
                drug_column = df.columns[1]  # 第二列（B列）
            else:
                print("❌ 无法找到B列或第二列")
                return False
            
            # 提取B列的创新药名单
            self.innovative_drugs_list = df[drug_column].dropna().astype(str).tolist()
            print(f"✓ 成功加载 {len(self.innovative_drugs_list)} 个创新药")
            print(f"创新药示例: {self.innovative_drugs_list[:5]}")
            
            return True
            
        except Exception as e:
            print(f"❌ 加载创新药名单失败: {str(e)}")
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
    
    def identify_sales_columns(self, df):
        """智能识别销售金额和销售制剂量列"""
        sales_amount_col = None
        sales_volume_col = None

        # 直接按列名查找
        for col in df.columns:
            col_name = str(col)
            if '销售金额' in col_name and not sales_amount_col:
                sales_amount_col = col
            elif '销售制剂量' in col_name and not sales_volume_col:
                sales_volume_col = col
            elif '销售包装量' in col_name and not sales_volume_col:  # 2022年数据用的是销售包装量
                sales_volume_col = col

        return sales_amount_col, sales_volume_col
    
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
            print(f"  - 列名: {list(df.columns)[:10]}...")  # 只显示前10个列名
            
            # 检查必要列是否存在（使用实际的中文列名）
            hospital_name_col = '机构名称'  # A列对应
            drug_name_col = '产品通用名'    # H列对应

            if hospital_name_col not in df.columns or drug_name_col not in df.columns:
                print(f"  ⚠ 缺少{hospital_name_col}列或{drug_name_col}列")
                return None
            
            # 识别销售金额和销售制剂量列
            sales_amount_col, sales_volume_col = self.identify_sales_columns(df)
            
            if not sales_amount_col:
                print("  ⚠ 未找到销售金额列")
                return None
            
            print(f"  - 销售金额列: {sales_amount_col}")
            print(f"  - 销售制剂量列: {sales_volume_col}")
            
            # 重命名关键列
            rename_map = {
                hospital_name_col: 'hospital_name',
                drug_name_col: 'drug_name',
                sales_amount_col: 'sales_amount'
            }
            
            if sales_volume_col:
                rename_map[sales_volume_col] = 'sales_volume'
            
            df = df.rename(columns=rename_map)
            
            # 添加年份和医院级别信息
            df['年份'] = year
            df['医院级别'] = hospital_level
            
            # 转换数值列
            df['sales_amount'] = pd.to_numeric(df['sales_amount'], errors='coerce').fillna(0)
            if 'sales_volume' in df.columns:
                df['sales_volume'] = pd.to_numeric(df['sales_volume'], errors='coerce').fillna(0)
            
            return df
            
        except Exception as e:
            print(f"读取文件失败 {file_path}: {str(e)}")
            return None
    
    def load_all_data(self):
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

    def match_innovative_drugs(self):
        """匹配创新药数据"""
        print("\n开始匹配创新药数据...")

        if not self.all_data:
            print("❌ 没有医院数据可匹配")
            return False

        if not self.innovative_drugs_list:
            print("❌ 没有创新药名单可匹配")
            return False

        # 合并所有医院数据
        combined_df = pd.concat(self.all_data, ignore_index=True)
        print(f"合并后总数据行数: {len(combined_df)}")

        # 匹配创新药
        matched_rows = []

        for idx, row in combined_df.iterrows():
            drug_name = str(row['drug_name']).strip()

            # 检查是否为创新药（精确匹配或包含匹配）
            is_innovative = False
            matched_innovative_name = None

            for innovative_drug in self.innovative_drugs_list:
                innovative_drug = str(innovative_drug).strip()

                # 精确匹配
                if drug_name == innovative_drug:
                    is_innovative = True
                    matched_innovative_name = innovative_drug
                    break

                # 包含匹配（创新药名称包含在医院药品名称中）
                elif innovative_drug in drug_name:
                    is_innovative = True
                    matched_innovative_name = innovative_drug
                    break

                # 反向包含匹配（医院药品名称包含在创新药名称中）
                elif drug_name in innovative_drug:
                    is_innovative = True
                    matched_innovative_name = innovative_drug
                    break

            if is_innovative:
                row_copy = row.copy()
                row_copy['matched_innovative_drug'] = matched_innovative_name
                matched_rows.append(row_copy)

        if matched_rows:
            self.matched_data = pd.DataFrame(matched_rows)
            print(f"✓ 成功匹配 {len(self.matched_data)} 条创新药数据")

            # 统计匹配的创新药种类
            unique_innovative_drugs = self.matched_data['matched_innovative_drug'].nunique()
            print(f"✓ 匹配到 {unique_innovative_drugs} 种不同的创新药")

            return True
        else:
            print("❌ 没有匹配到任何创新药数据")
            return False

    def calculate_top_drugs(self):
        """计算销售金额前十后十"""
        print("\n计算创新药销售金额排名...")

        if self.matched_data.empty:
            print("❌ 没有匹配的创新药数据")
            return None, None

        # 按创新药名称汇总销售金额
        drug_totals = self.matched_data.groupby('matched_innovative_drug').agg({
            'sales_amount': 'sum',
            'sales_volume': 'sum' if 'sales_volume' in self.matched_data.columns else lambda x: 0
        }).reset_index()

        # 筛选销售金额大于0的药品（后十名需要为正数）
        drug_totals = drug_totals[drug_totals['sales_amount'] > 0]

        if len(drug_totals) == 0:
            print("❌ 没有销售金额大于0的创新药")
            return None, None

        # 排序
        drug_totals_sorted = drug_totals.sort_values('sales_amount', ascending=False)

        # 前十名
        top_10 = drug_totals_sorted.head(10)

        # 后十名（销售金额最小但大于0的）
        bottom_10 = drug_totals_sorted.tail(10)

        print(f"销售金额前十名创新药:")
        for i, (_, row) in enumerate(top_10.iterrows(), 1):
            print(f"{i}. {row['matched_innovative_drug']}: {row['sales_amount']:,.2f}元")

        print(f"\n销售金额后十名创新药:")
        for i, (_, row) in enumerate(bottom_10.iterrows(), 1):
            print(f"{i}. {row['matched_innovative_drug']}: {row['sales_amount']:,.2f}元")

        return top_10, bottom_10

    def get_yearly_drug_details(self, top_10, bottom_10):
        """获取前十后十药品的年度详细数据"""
        print("\n生成年度详细数据...")

        # 合并前十后十药品名单
        target_drugs = set()
        if top_10 is not None:
            target_drugs.update(top_10['matched_innovative_drug'].tolist())
        if bottom_10 is not None:
            target_drugs.update(bottom_10['matched_innovative_drug'].tolist())

        if not target_drugs:
            return None, None

        # 筛选目标药品数据
        target_data = self.matched_data[self.matched_data['matched_innovative_drug'].isin(target_drugs)]

        # 按药品和年份汇总
        yearly_details = target_data.groupby(['matched_innovative_drug', '年份']).agg({
            'sales_amount': 'sum',
            'sales_volume': 'sum' if 'sales_volume' in target_data.columns else lambda x: 0
        }).reset_index()

        # 转换为透视表格式
        yearly_pivot = yearly_details.pivot(index='matched_innovative_drug',
                                          columns='年份',
                                          values='sales_amount').fillna(0)

        # 添加总计列
        yearly_pivot['总计'] = yearly_pivot.sum(axis=1)

        # 分离前十和后十的详细数据
        top_10_details = None
        bottom_10_details = None

        if top_10 is not None:
            top_10_drugs = top_10['matched_innovative_drug'].tolist()
            top_10_details = yearly_pivot[yearly_pivot.index.isin(top_10_drugs)]

        if bottom_10 is not None:
            bottom_10_drugs = bottom_10['matched_innovative_drug'].tolist()
            bottom_10_details = yearly_pivot[yearly_pivot.index.isin(bottom_10_drugs)]

        return top_10_details, bottom_10_details

    def get_yearly_innovative_drugs_list(self):
        """统计每年有销售数据的创新药名单"""
        print("\n统计每年创新药名单...")

        if self.matched_data.empty:
            print("❌ 没有匹配的创新药数据")
            return {}

        # 筛选有销售数据的记录（销售金额或销售制剂量大于0）
        has_sales_data = self.matched_data[
            (self.matched_data['sales_amount'] > 0) |
            (self.matched_data.get('sales_volume', 0) > 0)
        ]

        results = {}

        # 按年份统计
        for year in ['2021年', '2022年', '2023年']:
            year_data = has_sales_data[has_sales_data['年份'] == year]
            unique_drugs = year_data['matched_innovative_drug'].unique().tolist()

            results[year] = {
                'drugs': unique_drugs,
                'count': len(unique_drugs)
            }

            print(f"{year}: {len(unique_drugs)} 种创新药有销售数据")

        # 三年总和不重复
        all_drugs = set()
        for year_data in results.values():
            all_drugs.update(year_data['drugs'])

        results['三年总和'] = {
            'drugs': sorted(list(all_drugs)),
            'count': len(all_drugs)
        }

        print(f"三年总和: {len(all_drugs)} 种不重复创新药有销售数据")

        return results

    def save_results_to_excel(self, top_10, bottom_10, top_10_details, bottom_10_details, yearly_drugs):
        """保存结果到Excel文件"""
        print("\n保存结果到Excel...")

        filename = f"创新药销售分析结果_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 1. 前十名汇总
            if top_10 is not None:
                top_10_display = top_10.copy()
                top_10_display['排名'] = range(1, len(top_10_display) + 1)
                top_10_display = top_10_display[['排名', 'matched_innovative_drug', 'sales_amount', 'sales_volume']]
                top_10_display.columns = ['排名', '创新药名称', '总销售金额', '总销售制剂量']
                top_10_display.to_excel(writer, sheet_name='销售金额前十名', index=False)

            # 2. 后十名汇总
            if bottom_10 is not None:
                bottom_10_display = bottom_10.copy()
                bottom_10_display['排名'] = range(1, len(bottom_10_display) + 1)
                bottom_10_display = bottom_10_display[['排名', 'matched_innovative_drug', 'sales_amount', 'sales_volume']]
                bottom_10_display.columns = ['排名', '创新药名称', '总销售金额', '总销售制剂量']
                bottom_10_display.to_excel(writer, sheet_name='销售金额后十名', index=False)

            # 3. 前十名年度详细数据
            if top_10_details is not None:
                top_10_details_copy = top_10_details.copy()
                top_10_details_copy.index.name = '创新药名称'
                top_10_details_copy.to_excel(writer, sheet_name='前十名年度明细')

            # 4. 后十名年度详细数据
            if bottom_10_details is not None:
                bottom_10_details_copy = bottom_10_details.copy()
                bottom_10_details_copy.index.name = '创新药名称'
                bottom_10_details_copy.to_excel(writer, sheet_name='后十名年度明细')

            # 5. 各年度创新药名单
            if yearly_drugs:
                for year, data in yearly_drugs.items():
                    if year != '三年总和':
                        year_df = pd.DataFrame({
                            '创新药名称': data['drugs']
                        })
                        year_df.to_excel(writer, sheet_name=f'{year}创新药名单', index=False)

                # 三年总和
                if '三年总和' in yearly_drugs:
                    total_df = pd.DataFrame({
                        '创新药名称': yearly_drugs['三年总和']['drugs']
                    })
                    total_df.to_excel(writer, sheet_name='三年总和创新药名单', index=False)

            # 6. 统计摘要
            summary_data = []

            if yearly_drugs:
                for year, data in yearly_drugs.items():
                    summary_data.append({
                        '统计项目': f'{year}创新药数量',
                        '数值': data['count']
                    })

            if top_10 is not None:
                summary_data.append({
                    '统计项目': '前十名总销售金额',
                    '数值': top_10['sales_amount'].sum()
                })

            if bottom_10 is not None:
                summary_data.append({
                    '统计项目': '后十名总销售金额',
                    '数值': bottom_10['sales_amount'].sum()
                })

            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='统计摘要', index=False)

        print(f"✓ 结果已保存到: {filename}")
        return filename

def main():
    """主函数"""
    print("仙尊大人，开始分析创新药销售数据...")

    analyzer = InnovativeDrugAnalyzer()

    # 第一步：加载创新药名单
    if not analyzer.load_innovative_drugs_list():
        print("❌ 加载创新药名单失败，程序退出")
        return

    # 第二步：加载医院数据
    if not analyzer.load_all_data():
        print("❌ 加载医院数据失败，程序退出")
        return

    # 第三步：匹配创新药数据
    if not analyzer.match_innovative_drugs():
        print("❌ 匹配创新药数据失败，程序退出")
        return

    # 第四步：计算前十后十
    top_10, bottom_10 = analyzer.calculate_top_drugs()

    # 第五步：获取年度详细数据
    top_10_details, bottom_10_details = analyzer.get_yearly_drug_details(top_10, bottom_10)

    # 第六步：统计年度创新药名单
    yearly_drugs = analyzer.get_yearly_innovative_drugs_list()

    # 第七步：保存结果
    filename = analyzer.save_results_to_excel(top_10, bottom_10, top_10_details, bottom_10_details, yearly_drugs)

    print(f"\n🎉 仙尊大人，创新药销售分析完成！")
    print(f"📊 结果文件: {filename}")
    print("📈 包含内容:")
    print("  - 销售金额前十名/后十名")
    print("  - 前十名/后十名年度明细")
    print("  - 各年度创新药名单")
    print("  - 三年总和创新药名单")
    print("  - 统计摘要")

if __name__ == "__main__":
    main()
