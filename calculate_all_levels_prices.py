import pandas as pd
import numpy as np
from collections import defaultdict

# 正确的文件路径
file_path = '仙尊大人_创新药医院数据完整匹配结果_20250908_144656.xlsx'

print("="*80)
print("创新药平均单价计算 - 按医院级别和医保属性分类")
print("="*80)

# 读取文件
xls = pd.ExcelFile(file_path, engine='openpyxl')
sheet_names = xls.sheet_names

print(f"\n文件: {file_path}")
print(f"总表格数: {len(sheet_names)}\n")

# 第4-12张表格（索引3-11）
target_indices = list(range(3, 12))

print("目标表格（第4-12张，索引3-11）:")
for idx in target_indices:
    print(f"  第{idx+1}张（索引{idx}）: {sheet_names[idx]}")

print("\n" + "="*80)
print("开始计算")
print("="*80)

# 存储结果的数据结构
# results[级别][医保属性] = {'记录数': x, '总金额': x, '总制剂量': x}
results = {
    '一级': {'总创新药': defaultdict(float), '医保创新药': defaultdict(float), '非医保创新药': defaultdict(float)},
    '二级': {'总创新药': defaultdict(float), '医保创新药': defaultdict(float), '非医保创新药': defaultdict(float)},
    '三级': {'总创新药': defaultdict(float), '医保创新药': defaultdict(float), '非医保创新药': defaultdict(float)}
}

# 处理每张表格
for idx in target_indices:
    sheet_name = sheet_names[idx]
    print(f"\n处理: 第{idx+1}张 - {sheet_name}")
    
    # 判断医院级别
    if '一级' in sheet_name:
        level = '一级'
    elif '二级' in sheet_name:
        level = '二级'
    elif '三级' in sheet_name:
        level = '三级'
    else:
        print(f"  跳过：无法识别级别")
        continue
    
    # 判断年份（用于确定销售制剂量列）
    if '2021' in sheet_name:
        quantity_col_idx = 9  # J列
        year = '2021'
    elif '2022' in sheet_name or '2023' in sheet_name:
        quantity_col_idx = 10  # K列
        year = '2022' if '2022' in sheet_name else '2023'
    else:
        print(f"  跳过：无法识别年份")
        continue
    
    # 读取数据
    df = pd.read_excel(file_path, sheet_name=idx, engine='openpyxl')
    
    print(f"  级别: {level}  年份: {year}  行数: {len(df)}")
    
    # 提取关键列
    sales_amount = pd.to_numeric(df.iloc[:, 8], errors='coerce')  # I列：销售金额
    quantity = pd.to_numeric(df.iloc[:, quantity_col_idx], errors='coerce')  # J/K列：销售制剂量
    insurance_flag = df.iloc[:, 24]  # Y列：是否医保用药
    
    # 有效数据筛选（销售金额>0 且 销售制剂量>0）
    valid_mask = (sales_amount > 0) & (quantity > 0)
    
    valid_amount = sales_amount[valid_mask]
    valid_quantity = quantity[valid_mask]
    valid_insurance = insurance_flag[valid_mask]
    
    print(f"  有效记录数: {valid_mask.sum()}")
    
    # 分类统计
    # 1. 总创新药（所有有效记录）
    results[level]['总创新药']['记录数'] += valid_mask.sum()
    results[level]['总创新药']['总金额'] += valid_amount.sum()
    results[level]['总创新药']['总制剂量'] += valid_quantity.sum()
    
    # 2. 医保创新药（Y列='Y'）
    insured_mask = (valid_insurance == 'Y')
    insured_count = insured_mask.sum()
    if insured_count > 0:
        results[level]['医保创新药']['记录数'] += insured_count
        results[level]['医保创新药']['总金额'] += valid_amount[insured_mask].sum()
        results[level]['医保创新药']['总制剂量'] += valid_quantity[insured_mask].sum()
    
    # 3. 非医保创新药（Y列='N'或空）
    non_insured_mask = (valid_insurance == 'N') | (valid_insurance.isna()) | (valid_insurance == '')
    non_insured_count = non_insured_mask.sum()
    if non_insured_count > 0:
        results[level]['非医保创新药']['记录数'] += non_insured_count
        results[level]['非医保创新药']['总金额'] += valid_amount[non_insured_mask].sum()
        results[level]['非医保创新药']['总制剂量'] += valid_quantity[non_insured_mask].sum()
    
    print(f"    - 总创新药: {valid_mask.sum()} 条")
    print(f"    - 医保创新药: {insured_count} 条")
    print(f"    - 非医保创新药: {non_insured_count} 条")

# 计算单价并生成汇总表
print("\n\n" + "="*80)
print("计算结果汇总")
print("="*80)

summary_data = []

for level in ['一级', '二级', '三级']:
    for category in ['总创新药', '医保创新药', '非医保创新药']:
        data = results[level][category]
        
        if data['总制剂量'] > 0:
            unit_price = data['总金额'] / data['总制剂量']
        else:
            unit_price = 0
        
        summary_data.append({
            '医院级别': level,
            '分类': category,
            '记录数': int(data['记录数']),
            '总销售金额（元）': data['总金额'],
            '总销售制剂量': data['总制剂量'],
            '单价（元）': unit_price
        })
        
        print(f"\n【{level}医院 - {category}】")
        print(f"  记录数: {int(data['记录数']):,} 条")
        print(f"  总销售金额: {data['总金额']:,.2f} 元")
        print(f"  总销售制剂量: {data['总制剂量']:,.2f}")
        print(f"  单价: {unit_price:.4f} 元")

# 计算总计
print(f"\n{'='*80}")
print("【总计】")
print(f"{'='*80}")

for category in ['总创新药', '医保创新药', '非医保创新药']:
    total_records = sum(results[level][category]['记录数'] for level in ['一级', '二级', '三级'])
    total_amount = sum(results[level][category]['总金额'] for level in ['一级', '二级', '三级'])
    total_quantity = sum(results[level][category]['总制剂量'] for level in ['一级', '二级', '三级'])
    
    if total_quantity > 0:
        total_price = total_amount / total_quantity
    else:
        total_price = 0
    
    summary_data.append({
        '医院级别': '总计',
        '分类': category,
        '记录数': int(total_records),
        '总销售金额（元）': total_amount,
        '总销售制剂量': total_quantity,
        '单价（元）': total_price
    })
    
    print(f"\n【{category}】")
    print(f"  记录数: {int(total_records):,} 条")
    print(f"  总销售金额: {total_amount:,.2f} 元")
    print(f"  总销售制剂量: {total_quantity:,.2f}")
    print(f"  单价: {total_price:.4f} 元")

# 保存到Excel
output_file = '创新药平均单价分析结果_按级别和医保分类_20250908.xlsx'

summary_df = pd.DataFrame(summary_data)

# 创建矩阵视图
matrix_data = []
for level in ['一级', '二级', '三级', '总计']:
    row = {'医院级别': level}
    for category in ['总创新药', '医保创新药', '非医保创新药']:
        matching_row = summary_df[(summary_df['医院级别'] == level) & (summary_df['分类'] == category)]
        if not matching_row.empty:
            row[f'{category}_单价'] = matching_row.iloc[0]['单价（元）']
            row[f'{category}_记录数'] = matching_row.iloc[0]['记录数']
        else:
            row[f'{category}_单价'] = 0
            row[f'{category}_记录数'] = 0
    matrix_data.append(row)

matrix_df = pd.DataFrame(matrix_data)

# 保存到Excel（两个sheet）
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='详细数据', index=False)
    matrix_df.to_excel(writer, sheet_name='单价矩阵', index=False)

print(f"\n\n{'='*80}")
print(f"结果已保存到: {output_file}")
print(f"{'='*80}")
print("包含两个工作表:")
print("  1. 详细数据 - 完整的统计信息")
print("  2. 单价矩阵 - 单价对照表")
print("\n计算完成！")

