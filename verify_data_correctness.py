#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仙尊大人专属数据正确性验证系统
验证生成的9个医院分类文件的数据正确性
"""

import pandas as pd
import os

def verify_data_correctness():
    """验证数据正确性"""
    print("="*80)
    print("仙尊大人，开始验证医院数据分类的正确性")
    print("="*80)
    
    # 1. 验证文件是否都存在
    print("\n1. 验证文件存在性...")
    expected_files = []
    for year in [2021, 2022, 2023]:
        for category in ['委属', '市属', '其他三级']:
            filename = f"{year}年_{category}_医院数据.xlsx"
            expected_files.append(filename)
    
    missing_files = []
    existing_files = []
    
    for filename in expected_files:
        if os.path.exists(filename):
            existing_files.append(filename)
            file_size = os.path.getsize(filename) / 1024 / 1024
            print(f"✅ {filename} ({file_size:.1f} MB)")
        else:
            missing_files.append(filename)
            print(f"❌ {filename} - 文件不存在")
    
    if missing_files:
        print(f"\n⚠️ 缺失文件: {len(missing_files)}个")
        return False
    
    print(f"\n✅ 所有9个文件都存在")
    
    # 2. 验证数据总量
    print("\n2. 验证数据总量...")
    
    # 读取原始数据总量
    original_totals = {}
    original_files = {
        2021: '2021年/三级药品使用数据.xlsx',
        2022: '2022年/RPT_DRUG_USE_2022_BIG-北京市-三级.csv',
        2023: '2023年/RPT_DRUG_USE_2023_BIG_北京_3.csv'
    }
    
    for year, file_path in original_files.items():
        if os.path.exists(file_path):
            try:
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                else:
                    # 尝试不同编码
                    encodings = ['gb18030', 'utf-8', 'gbk']
                    df = None
                    for encoding in encodings:
                        try:
                            df = pd.read_csv(file_path, encoding=encoding)
                            break
                        except:
                            continue
                
                if df is not None:
                    original_totals[year] = len(df)
                    print(f"原始{year}年数据: {len(df):,}条")
                else:
                    print(f"❌ 无法读取{year}年原始数据")
            except Exception as e:
                print(f"❌ 读取{year}年原始数据失败: {e}")
    
    # 统计分类后的数据总量
    classified_totals = {}
    for year in [2021, 2022, 2023]:
        year_total = 0
        year_details = {}
        
        for category in ['委属', '市属', '其他三级']:
            filename = f"{year}年_{category}_医院数据.xlsx"
            try:
                df = pd.read_excel(filename)
                count = len(df)
                year_details[category] = count
                year_total += count
                print(f"{year}年{category}: {count:,}条")
            except Exception as e:
                print(f"❌ 读取{filename}失败: {e}")
                return False
        
        classified_totals[year] = {'total': year_total, 'details': year_details}
        print(f"{year}年分类后总计: {year_total:,}条")
        
        # 对比原始数据
        if year in original_totals:
            diff = year_total - original_totals[year]
            if diff == 0:
                print(f"✅ {year}年数据完整，无丢失")
            else:
                print(f"⚠️ {year}年数据差异: {diff}条")
    
    # 3. 验证医院分类正确性
    print("\n3. 验证医院分类正确性...")
    
    # 读取医院分类标准
    weishu_hospitals = []
    shishu_hospitals = []
    
    try:
        weishu_df = pd.read_csv('北京委属医院分类_20250623_084700.csv', encoding='utf-8')
        weishu_hospitals = weishu_df['医院名称'].tolist()
        
        shishu_df = pd.read_csv('北京市属医院分类_20250623_084700.csv', encoding='utf-8')
        shishu_hospitals = shishu_df['医院名称'].tolist()
        
        print(f"标准委属医院: {len(weishu_hospitals)}家")
        print(f"标准市属医院: {len(shishu_hospitals)}家")
    except Exception as e:
        print(f"❌ 读取医院分类标准失败: {e}")
        return False
    
    # 检查分类文件中的医院是否正确
    classification_errors = []
    
    for year in [2021, 2022, 2023]:
        print(f"\n验证{year}年医院分类...")
        
        # 检查委属医院文件
        try:
            weishu_file = f"{year}年_委属_医院数据.xlsx"
            df = pd.read_excel(weishu_file)
            hospital_col = df.columns[0]  # 假设第一列是医院名称
            hospitals_in_file = df[hospital_col].unique()
            
            print(f"委属文件中的医院 ({len(hospitals_in_file)}家):")
            for hospital in hospitals_in_file:
                print(f"  - {hospital}")
                
                # 检查是否应该在委属分类中
                is_weishu = any(weishu in str(hospital) or str(hospital) in weishu for weishu in weishu_hospitals)
                if not is_weishu:
                    classification_errors.append(f"{year}年委属文件中的'{hospital}'可能分类错误")
        
        except Exception as e:
            print(f"❌ 验证{year}年委属医院失败: {e}")
        
        # 检查市属医院文件
        try:
            shishu_file = f"{year}年_市属_医院数据.xlsx"
            df = pd.read_excel(shishu_file)
            hospital_col = df.columns[0]
            hospitals_in_file = df[hospital_col].unique()
            
            print(f"市属文件中的医院 ({len(hospitals_in_file)}家):")
            for hospital in hospitals_in_file:
                print(f"  - {hospital}")
                
                # 检查是否应该在市属分类中
                is_shishu = any(shishu in str(hospital) or str(hospital) in shishu for shishu in shishu_hospitals)
                if not is_shishu:
                    classification_errors.append(f"{year}年市属文件中的'{hospital}'可能分类错误")
        
        except Exception as e:
            print(f"❌ 验证{year}年市属医院失败: {e}")
    
    # 4. 验证数据结构一致性
    print("\n4. 验证数据结构一致性...")
    
    column_structures = {}
    for year in [2021, 2022, 2023]:
        for category in ['委属', '市属', '其他三级']:
            filename = f"{year}年_{category}_医院数据.xlsx"
            try:
                df = pd.read_excel(filename)
                columns = list(df.columns)
                key = f"{year}_{category}"
                column_structures[key] = columns
                print(f"{filename}: {len(columns)}列")
            except Exception as e:
                print(f"❌ 读取{filename}结构失败: {e}")
    
    # 检查列结构是否一致
    all_columns = list(column_structures.values())
    if all_columns:
        first_columns = all_columns[0]
        structure_consistent = all(cols == first_columns for cols in all_columns)
        
        if structure_consistent:
            print("✅ 所有文件的列结构一致")
            print(f"列名: {first_columns}")
        else:
            print("⚠️ 文件列结构不一致")
            for key, cols in column_structures.items():
                if cols != first_columns:
                    print(f"  {key}: {cols}")
    
    # 5. 生成验证报告
    print("\n5. 生成验证报告...")
    
    total_records = sum(classified_totals[year]['total'] for year in classified_totals)
    
    verification_report = {
        'files_generated': len(existing_files),
        'total_records': total_records,
        'yearly_breakdown': classified_totals,
        'classification_errors': classification_errors,
        'structure_consistent': structure_consistent if 'structure_consistent' in locals() else False
    }
    
    # 保存验证报告
    report_df = pd.DataFrame([
        ['文件生成数量', len(existing_files), '个'],
        ['总记录数', total_records, '条'],
        ['分类错误数', len(classification_errors), '个'],
        ['结构一致性', '是' if verification_report['structure_consistent'] else '否', ''],
    ], columns=['验证项目', '结果', '单位'])
    
    # 添加年度详细数据
    for year, data in classified_totals.items():
        for category, count in data['details'].items():
            report_df = pd.concat([report_df, pd.DataFrame([
                [f'{year}年{category}', count, '条']
            ], columns=['验证项目', '结果', '单位'])], ignore_index=True)
    
    report_filename = f"数据正确性验证报告_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    report_df.to_excel(report_filename, index=False)
    
    print(f"\n验证报告已保存: {report_filename}")
    
    # 6. 总结
    print("\n" + "="*80)
    print("数据正确性验证总结")
    print("="*80)
    
    if len(existing_files) == 9:
        print("✅ 文件完整性: 通过 (9/9个文件)")
    else:
        print(f"❌ 文件完整性: 失败 ({len(existing_files)}/9个文件)")
    
    print(f"📊 数据总量: {total_records:,}条记录")
    
    if len(classification_errors) == 0:
        print("✅ 分类准确性: 通过 (无明显错误)")
    else:
        print(f"⚠️ 分类准确性: 发现{len(classification_errors)}个潜在问题")
        for error in classification_errors[:5]:  # 只显示前5个错误
            print(f"  - {error}")
    
    if verification_report['structure_consistent']:
        print("✅ 数据结构: 一致")
    else:
        print("⚠️ 数据结构: 不一致")
    
    overall_success = (len(existing_files) == 9 and 
                      len(classification_errors) == 0 and 
                      verification_report['structure_consistent'])
    
    if overall_success:
        print("\n🎉 仙尊大人，数据正确性验证全部通过！")
    else:
        print("\n⚠️ 仙尊大人，发现一些需要注意的问题，请查看详细报告。")
    
    return overall_success

if __name__ == "__main__":
    try:
        verify_data_correctness()
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
