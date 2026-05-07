import pandas as pd
import numpy as np
import re
import os
from pathlib import Path
import warnings
import gc
from typing import Dict, List, Tuple
warnings.filterwarnings('ignore')

class BigDataPharmaceuticalAnalyzer:
    def __init__(self):
        self.negotiated_drugs = None
        self.hospital_data_summary = {}
        self.matched_results = {}
        self.hospital_totals = {}
        self.chunk_size = 10000  # 分批处理大小
        
    def detect_encoding(self, file_path: str) -> str:
        """智能检测文件编码"""
        encodings = ['gb18030', 'gbk', 'utf-8', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)  # 读取前1024字符测试
                return encoding
            except:
                continue
        return 'utf-8'  # 默认编码
    
    def load_negotiated_drugs(self, file_path='没有中药成分的谈判药.xlsx'):
        """加载谈判药数据"""
        print("=== 第一步：加载谈判药数据 ===")
        try:
            self.negotiated_drugs = pd.read_excel(file_path)
            print(f"✓ 成功加载谈判药数据：{len(self.negotiated_drugs)}条记录")
            
            # 确认关键列
            print("✓ 关键列确认：")
            print(f"  A列(年份): {self.negotiated_drugs.columns[0]}")
            print(f"  B列(药品名称): {self.negotiated_drugs.columns[1]}")
            print(f"  E列(谈判类别): {self.negotiated_drugs.columns[4]}")
            print(f"  F列(创新药): {self.negotiated_drugs.columns[5]}")
            
            # 建立药品名称索引以提高匹配效率
            self.drug_index = {}
            for _, row in self.negotiated_drugs.iterrows():
                year = row[self.negotiated_drugs.columns[0]]
                drug_name = row[self.negotiated_drugs.columns[1]]
                negotiation_type = row[self.negotiated_drugs.columns[4]]
                is_innovative = row[self.negotiated_drugs.columns[5]]
                
                if year not in self.drug_index:
                    self.drug_index[year] = {}
                
                self.drug_index[year][drug_name] = {
                    'negotiation_type': negotiation_type,
                    'is_innovative': is_innovative
                }
            
            print(f"✓ 建立药品索引完成，覆盖{len(self.drug_index)}个年份")
            return True
            
        except Exception as e:
            print(f"✗ 加载谈判药数据失败：{e}")
            return False
    
    def identify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """智能识别列结构"""
        column_mapping = {
            'hospital_col': None,
            'drug_col': None,
            'amount_col': None,
            'volume_col': None
        }
        
        # A列：医院名称
        if len(df.columns) > 0:
            column_mapping['hospital_col'] = df.columns[0]
        
        # H列：药品名称
        if len(df.columns) > 7:
            column_mapping['drug_col'] = df.columns[7]
        
        # 智能识别销售金额和销售制剂量列
        for col in df.columns:
            col_str = str(col).lower()
            if '销售金额' in col_str and column_mapping['amount_col'] is None:
                column_mapping['amount_col'] = col
            elif '销售制剂量' in col_str and column_mapping['volume_col'] is None:
                column_mapping['volume_col'] = col
        
        return column_mapping
    
    def enhanced_drug_matching(self, hospital_drug_name: str, negotiated_drug_name: str) -> bool:
        """增强药品名称匹配"""
        if pd.isna(hospital_drug_name) or pd.isna(negotiated_drug_name):
            return False
            
        hospital_drug_name = str(hospital_drug_name).strip()
        negotiated_drug_name = str(negotiated_drug_name).strip()
        
        if not hospital_drug_name or not negotiated_drug_name:
            return False
        
        # 精确匹配
        if hospital_drug_name == negotiated_drug_name:
            return True
        
        # 检查非汉字字符，启用增强匹配
        has_non_chinese = bool(re.search(r'[^\u4e00-\u9fff]', hospital_drug_name))
        
        if has_non_chinese:
            # 提取核心药品名
            hospital_core = re.sub(r'[\[\]()（）].*?[\[\]()（）]', '', hospital_drug_name)
            hospital_core = re.sub(r'[^\u4e00-\u9fff]', '', hospital_core)
            
            negotiated_core = re.sub(r'[\[\]()（）].*?[\[\]()（）]', '', negotiated_drug_name)
            negotiated_core = re.sub(r'[^\u4e00-\u9fff]', '', negotiated_core)
            
            if len(hospital_core) > 2 and len(negotiated_core) > 2:
                if hospital_core in negotiated_core or negotiated_core in hospital_core:
                    return True
        
        return False
    
    def process_hospital_file(self, file_path: str, year: str, level: str) -> Dict:
        """处理单个医院数据文件"""
        print(f"  处理{year}年{level}级医院数据...")
        
        try:
            # 根据文件类型选择读取方式
            if file_path.endswith('.xlsx'):
                # Excel文件
                df = pd.read_excel(file_path)
            else:
                # CSV文件，检测编码
                encoding = self.detect_encoding(file_path)
                df = pd.read_csv(file_path, encoding=encoding)
            
            print(f"    原始数据：{len(df)}条记录")
            
            # 识别列结构
            column_mapping = self.identify_columns(df)
            
            if not all(column_mapping.values()):
                print(f"    ✗ 列识别失败：{column_mapping}")
                return {'matched_count': 0, 'hospital_count': 0}
            
            # 统计医院总数
            hospital_count = df[column_mapping['hospital_col']].nunique()
            
            # 年份映射：谈判药年份 → 医院数据年份
            negotiated_year_map = {
                '2021': 2020,
                '2022': 2021, 
                '2023': 2022
            }
            
            negotiated_year = negotiated_year_map.get(year)
            if negotiated_year not in self.drug_index:
                print(f"    ✗ 未找到{negotiated_year}年谈判药数据")
                return {'matched_count': 0, 'hospital_count': hospital_count}
            
            # 分批处理匹配
            matched_records = []
            year_drug_index = self.drug_index[negotiated_year]
            
            # 分批处理以节省内存
            for chunk_start in range(0, len(df), self.chunk_size):
                chunk_end = min(chunk_start + self.chunk_size, len(df))
                chunk_df = df.iloc[chunk_start:chunk_end]
                
                for _, row in chunk_df.iterrows():
                    hospital_drug = row[column_mapping['drug_col']]
                    
                    # 快速精确匹配
                    if hospital_drug in year_drug_index:
                        drug_info = year_drug_index[hospital_drug]
                        matched_record = {
                            'year': year,
                            'level': level,
                            'hospital': row[column_mapping['hospital_col']],
                            'drug_name': hospital_drug,
                            'amount': row[column_mapping['amount_col']],
                            'volume': row[column_mapping['volume_col']],
                            'negotiation_type': drug_info['negotiation_type'],
                            'is_innovative': drug_info['is_innovative']
                        }
                        matched_records.append(matched_record)
                    else:
                        # 增强匹配
                        for negotiated_drug, drug_info in year_drug_index.items():
                            if self.enhanced_drug_matching(hospital_drug, negotiated_drug):
                                matched_record = {
                                    'year': year,
                                    'level': level,
                                    'hospital': row[column_mapping['hospital_col']],
                                    'drug_name': hospital_drug,
                                    'amount': row[column_mapping['amount_col']],
                                    'volume': row[column_mapping['volume_col']],
                                    'negotiation_type': drug_info['negotiation_type'],
                                    'is_innovative': drug_info['is_innovative']
                                }
                                matched_records.append(matched_record)
                                break
                
                # 清理内存
                del chunk_df
                gc.collect()
            
            print(f"    ✓ 匹配成功：{len(matched_records)}条记录")
            
            return {
                'matched_records': matched_records,
                'matched_count': len(matched_records),
                'hospital_count': hospital_count
            }
            
        except Exception as e:
            print(f"    ✗ 处理失败：{e}")
            return {'matched_count': 0, 'hospital_count': 0}
    
    def process_all_hospital_data(self):
        """处理所有医院数据"""
        print("\n=== 第二步：处理医院数据（110万条记录）===")
        
        # 文件映射
        file_mappings = {
            '2021': {
                '三级': '2021年/三级药品使用数据.xlsx',
                '二级': '2021年/二级药品使用数据.xlsx',
                '一级': '2021年/使用数据（基层）.xlsx'
            },
            '2022': {
                '三级': '2022年/RPT_DRUG_USE_2022_BIG-北京市-三级.csv',
                '二级': '2022年/RPT_DRUG_USE_2022_BIG-北京市-二级.csv',
                '一级': '2022年/RPT_DRUG_USE_2022_BIG-北京市-基层.csv'
            },
            '2023': {
                '三级': '2023年/RPT_DRUG_USE_2023_BIG_北京_3.csv',
                '二级': '2023年/RPT_DRUG_USE_2023_BIG_北京_2.csv',
                '一级': '2023年/RPT_DRUG_USE_2023_BIG_北京_1.csv'
            }
        }
        
        all_matched_records = []
        total_matched = 0
        
        for year, level_files in file_mappings.items():
            print(f"\n处理{year}年数据：")
            
            for level, file_path in level_files.items():
                if os.path.exists(file_path):
                    result = self.process_hospital_file(file_path, year, level)
                    
                    if 'matched_records' in result:
                        all_matched_records.extend(result['matched_records'])
                    
                    total_matched += result['matched_count']
                    self.hospital_totals[f"{year}_{level}"] = result['hospital_count']
                else:
                    print(f"  ✗ 文件不存在：{file_path}")
        
        # 转换为DataFrame
        self.matched_data = pd.DataFrame(all_matched_records)
        print(f"\n✓ 总计匹配成功：{total_matched}条记录")
        print(f"✓ 医院总数统计：{self.hospital_totals}")
        
        return total_matched > 0
    
    def generate_summary_tables(self):
        """生成汇总表格 - 按医院级别分组格式，正确计算占比"""
        print("\n=== 第三步：生成汇总表格 ===")

        if self.matched_data.empty:
            print("✗ 没有匹配数据")
            return {}

        # 四个类别的数据
        categories = {
            '所有谈判药': self.matched_data,
            '首谈药': self.matched_data[self.matched_data['negotiation_type'] == '首谈'],
            '续约药': self.matched_data[self.matched_data['negotiation_type'] == '续约'],
            '创新药': self.matched_data[self.matched_data['is_innovative'] == '创新药']
        }

        # 计算总谈判药的基准数据（用于占比计算）
        all_negotiated_data = categories['所有谈判药']
        total_negotiated_volume = all_negotiated_data['volume'].sum()
        total_negotiated_amount = all_negotiated_data['amount'].sum()

        print(f"✓ 总谈判药基准数据：用量{total_negotiated_volume:.0f}，金额{total_negotiated_amount:.0f}")

        results = {}

        for category_name, category_data in categories.items():
            print(f"\n生成{category_name}表格...")

            table_data = []

            # 按医院级别分组，每个级别下有各年份数据
            for level in ['一级', '二级', '三级']:
                level_data = category_data[category_data['level'] == level]

                # 添加级别行（第一行显示级别名称）
                first_row_for_level = True
                level_total_volume = 0
                level_total_amount = 0
                level_total_hospitals = 0
                level_all_hospitals = 0

                # 各年份数据
                for year in ['2021', '2022', '2023']:
                    year_level_data = level_data[level_data['year'] == year]

                    if len(year_level_data) > 0:
                        total_volume = year_level_data['volume'].sum()
                        total_amount = year_level_data['amount'].sum()
                        hospital_count = year_level_data['hospital'].nunique()
                        total_hospitals = self.hospital_totals.get(f"{year}_{level}", 1)
                        entry_rate = (hospital_count / total_hospitals * 100) if total_hospitals > 0 else 0
                    else:
                        total_volume = total_amount = hospital_count = entry_rate = 0
                        total_hospitals = self.hospital_totals.get(f"{year}_{level}", 1)

                    # 累计级别总计
                    level_total_volume += total_volume
                    level_total_amount += total_amount
                    level_total_hospitals += hospital_count
                    level_all_hospitals += total_hospitals

                    # 计算占比（该类别/总谈判药）
                    volume_ratio = (total_volume / total_negotiated_volume * 100) if total_negotiated_volume > 0 else 0
                    amount_ratio = (total_amount / total_negotiated_amount * 100) if total_negotiated_amount > 0 else 0

                    # 单位转换
                    if category_name == '创新药':
                        volume_unit = total_volume / 10000
                        amount_unit = total_amount / 10000
                    else:
                        volume_unit = total_volume / 100000000
                        amount_unit = total_amount / 100000000

                    table_row = {
                        '医院级别': level if first_row_for_level else '',
                        '年份': year,
                        '医院用量(万)' if category_name == '创新药' else '医院用量(亿)': round(volume_unit, 2),
                        '占该级药品比(%)': round(volume_ratio, 2),
                        '销售金额(万)' if category_name == '创新药' else '销售金额(亿)': round(amount_unit, 2),
                        '占该级药品比(%)_金额': round(amount_ratio, 2),
                        '进院率(%)': round(entry_rate, 2)
                    }
                    table_data.append(table_row)
                    first_row_for_level = False

                # 添加该级别的小计行
                level_entry_rate = (level_total_hospitals / level_all_hospitals * 100) if level_all_hospitals > 0 else 0
                level_volume_ratio = (level_total_volume / total_negotiated_volume * 100) if total_negotiated_volume > 0 else 0
                level_amount_ratio = (level_total_amount / total_negotiated_amount * 100) if total_negotiated_amount > 0 else 0

                if category_name == '创新药':
                    volume_unit = level_total_volume / 10000
                    amount_unit = level_total_amount / 10000
                else:
                    volume_unit = level_total_volume / 100000000
                    amount_unit = level_total_amount / 100000000

                table_row = {
                    '医院级别': '',
                    '年份': '小计',
                    '医院用量(万)' if category_name == '创新药' else '医院用量(亿)': round(volume_unit, 2),
                    '占该级药品比(%)': round(level_volume_ratio, 2),
                    '销售金额(万)' if category_name == '创新药' else '销售金额(亿)': round(amount_unit, 2),
                    '占该级药品比(%)_金额': round(level_amount_ratio, 2),
                    '进院率(%)': round(level_entry_rate, 2)
                }
                table_data.append(table_row)

            # 添加总计行
            total_volume = category_data['volume'].sum()
            total_amount = category_data['amount'].sum()
            total_hospitals = category_data['hospital'].nunique()
            all_hospitals = sum(self.hospital_totals.values())
            total_entry_rate = (total_hospitals / all_hospitals * 100) if all_hospitals > 0 else 0

            # 总计占比
            total_volume_ratio = (total_volume / total_negotiated_volume * 100) if total_negotiated_volume > 0 else 0
            total_amount_ratio = (total_amount / total_negotiated_amount * 100) if total_negotiated_amount > 0 else 0

            if category_name == '创新药':
                volume_unit = total_volume / 10000
                amount_unit = total_amount / 10000
            else:
                volume_unit = total_volume / 100000000
                amount_unit = total_amount / 100000000

            table_row = {
                '医院级别': '总计',
                '年份': '',
                '医院用量(万)' if category_name == '创新药' else '医院用量(亿)': round(volume_unit, 2),
                '占该级药品比(%)': round(total_volume_ratio, 2),
                '销售金额(万)' if category_name == '创新药' else '销售金额(亿)': round(amount_unit, 2),
                '占该级药品比(%)_金额': round(total_amount_ratio, 2),
                '进院率(%)': round(total_entry_rate, 2)
            }
            table_data.append(table_row)

            results[category_name] = pd.DataFrame(table_data)
            print(f"✓ {category_name}表格生成完成：{len(table_data)}行")

        return results
    
    def save_results(self, results: Dict, output_file='仙尊大人_110万数据完整分析结果.xlsx'):
        """保存结果"""
        print(f"\n=== 第四步：保存结果到{output_file} ===")
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for category_name, table_df in results.items():
                    table_df.to_excel(writer, sheet_name=category_name, index=False)
                    print(f"✓ 保存{category_name}工作表")
            
            print(f"✓ 结果保存完成：{output_file}")
            return True
        except Exception as e:
            print(f"✗ 保存失败：{e}")
            return False
    
    def run_big_data_analysis(self):
        """运行大数据分析"""
        print("🚀 开始110万数据药品分析")
        print("=" * 60)
        
        # 执行分析步骤
        if not self.load_negotiated_drugs():
            return False
        
        if not self.process_all_hospital_data():
            return False
        
        results = self.generate_summary_tables()
        if not results:
            return False
        
        if not self.save_results(results):
            return False
        
        print("\n" + "=" * 60)
        print("🎉 大数据分析完成！")
        
        # 显示结果预览
        for category_name, table_df in results.items():
            print(f"\n=== {category_name} ===")
            print(table_df.head(10).to_string(index=False))
        
        return True

if __name__ == "__main__":
    analyzer = BigDataPharmaceuticalAnalyzer()
    success = analyzer.run_big_data_analysis()
    
    if success:
        print("\n✅ 110万数据分析成功完成！")
    else:
        print("\n❌ 分析过程中出现错误！")
