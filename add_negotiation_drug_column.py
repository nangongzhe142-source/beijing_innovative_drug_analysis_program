import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def extract_core_drug_name(drug_name):
    """
    提取药品的核心名称，用于匹配
    """
    if pd.isna(drug_name) or not isinstance(drug_name, str):
        return ""
    
    # 去除常见的前缀
    prefixes_to_remove = [
        '注射用', '口服', '外用', '吸入用', '滴眼用', '滴耳用', '滴鼻用',
        '甲磺酸', '盐酸', '硫酸', '磷酸', '枸橼酸', '琥珀酸', '富马酸',
        '马来酸', '酒石酸', '苯磺酸', '甲苯磺酸', '氢溴酸', '氢氯酸',
        '聚乙二醇', '重组', '人', '猪', '牛', '羊', '精氨酸', '甘草酸',
        '单铵', '半胱氨酸', '氯化钠', '碳酸氢钠', '右', '左', 'α', 'β', 'γ'
    ]
    
    # 去除常见的后缀（剂型）
    suffixes_to_remove = [
        '片', '胶囊', '注射液', '注射剂', '口服液', '颗粒', '散', '膏',
        '乳膏', '软膏', '凝胶', '贴', '栓', '滴眼液', '滴耳液', '滴鼻液',
        '吸入剂', '喷雾剂', '气雾剂', '粉雾剂', '混悬液', '混悬剂',
        '溶液', '浓溶液', '注射用浓溶液', '冻干粉', '冻干粉针',
        '缓释片', '控释片', '肠溶片', '薄膜衣片', '糖衣片',
        '缓释胶囊', '控释胶囊', '肠溶胶囊', '软胶囊', '硬胶囊',
        '微丸', '微球', '脂质体', '纳米粒', '微囊', '包衣',
        '组合包装', '复方', '单方', '单抗', '双抗', '三抗',
        '疫苗', '灭活疫苗', '减毒活疫苗', '重组疫苗', '蛋白疫苗',
        '细胞', '载体', '载体疫苗', '融合蛋白', '变应原', '点刺液',
        '干混悬剂', '常释剂型', '注射剂', '钠', '钾', '钙', '镁',
        '氯化物', '硫酸盐', '磷酸盐', '醋酸盐', '柠檬酸盐'
    ]
    
    core_name = drug_name.strip()
    
    # 去除前缀
    for prefix in prefixes_to_remove:
        if core_name.startswith(prefix):
            core_name = core_name[len(prefix):]
    
    # 去除后缀
    for suffix in suffixes_to_remove:
        if core_name.endswith(suffix):
            core_name = core_name[:-len(suffix)]
    
    # 去除括号及其内容
    import re
    core_name = re.sub(r'[（(].*?[）)]', '', core_name)
    
    # 去除数字和特殊字符
    core_name = re.sub(r'[0-9]+', '', core_name)
    core_name = re.sub(r'[^\u4e00-\u9fff]', '', core_name)
    
    return core_name.strip()

def fuzzy_match_drug_names(name1, name2):
    """
    模糊匹配药品名称
    """
    if pd.isna(name1) or pd.isna(name2):
        return False
    
    # 精确匹配
    if name1 == name2:
        return True
    
    # 提取核心名称进行匹配
    core1 = extract_core_drug_name(name1)
    core2 = extract_core_drug_name(name2)
    
    if core1 and core2 and core1 == core2:
        return True
    
    # 包含匹配
    if core1 in core2 or core2 in core1:
        return True
    
    return False

def add_negotiation_drug_column(target_drugs=None):
    """
    在文件中添加"谈判药"列，匹配指定的药品
    """
    try:
        # 读取当前文件
        print("读取创新药名单_去重去中药版_最终完整版_含国产进口信息_标记有数据.xlsx...")
        df = pd.read_excel('c:\\偷偷用用AI\\创新药名单_去重去中药版_最终完整版_含国产进口信息_标记有数据.xlsx')
        print(f"文件行数: {len(df)}")
        print(f"列名: {df.columns.tolist()}")
        
        # 如果没有提供目标药品列表，使用一些常见的谈判药品作为示例
        if target_drugs is None:
            # 这里可以设置一些常见的谈判药品作为示例
            target_drugs = [
                '替雷利珠单抗注射液',
                '卡瑞利珠单抗',
                '甲磺酸阿美替尼片',
                '泽布替尼胶囊',
                '甲磺酸氟马替尼片',
                '甲苯磺酸尼拉帕利胶囊',
                '达可替尼片',
                '奥布替尼片',
                '索凡替尼胶囊',
                '西尼莫德片',
                '甲磺酸伏美替尼片',
                '普拉替尼胶囊',
                '帕米帕利胶囊',
                '甲苯磺酸多纳非尼片',
                '维迪西妥单抗',
                '利司扑兰口服溶液用散',
                '海曲泊帕乙醇胺片',
                '赛沃替尼片',
                '艾米替诺福韦片',
                '阿兹夫定片',
                '派安普利单抗注射液',
                '瑞基奥仑赛注射液',
                '赛帕利单抗注射液',
                '西格列他钠片',
                '恩沃利单抗注射液',
                '奥雷巴替尼片',
                '舒格利单抗注射液',
                '安巴韦单抗注射液',
                '罗米司韦单抗注射液',
                '脯氨酸恒格列净片',
                '羟乙磺酸达尔西利片',
                '阿布昔替尼片',
                '多格列艾汀片',
                '非奈利酮片',
                '琥珀酸莫博赛替尼胶囊',
                '林普利塞片',
                '瑞维鲁胺片',
                '维立西呱片',
                '卡度尼利单抗注射液',
                '斯鲁利单抗注射液',
                '氢溴酸氘瑞米德韦片',
                '先诺特韦片',
                '谷美替尼片',
                '来瑞特韦片',
                '甲磺酸贝福替尼胶囊',
                '阿得贝利单抗注射液'
            ]
        
        print(f"\n要匹配的谈判药品数量: {len(target_drugs)}")
        print("前10个谈判药品:")
        for i, drug in enumerate(target_drugs[:10]):
            print(f"{i+1}. {drug}")
        
        # 在文件末尾添加"谈判药"列
        df['谈判药'] = '否'
        
        # 匹配统计
        exact_matches = 0
        fuzzy_matches = 0
        no_matches = 0
        
        print(f"\n开始匹配药品名称...")
        
        # 对文件中的每一行进行匹配
        for idx1, row1 in df.iterrows():
            drug_name1 = row1['药品名称']
            matched = False
            
            # 首先尝试精确匹配
            for target_drug in target_drugs:
                if drug_name1 == target_drug:
                    df.at[idx1, '谈判药'] = '是'
                    exact_matches += 1
                    matched = True
                    break
            
            # 如果精确匹配失败，尝试模糊匹配
            if not matched:
                for target_drug in target_drugs:
                    if fuzzy_match_drug_names(drug_name1, target_drug):
                        df.at[idx1, '谈判药'] = '是'
                        fuzzy_matches += 1
                        matched = True
                        break
            
            # 如果没有匹配到，保持"否"
            if not matched:
                no_matches += 1
            
            if (idx1 + 1) % 20 == 0:
                print(f"已处理 {idx1 + 1}/{len(df)} 个药品...")
        
        print(f"\n匹配完成！")
        print(f"精确匹配: {exact_matches}个")
        print(f"模糊匹配: {fuzzy_matches}个")
        print(f"未匹配: {no_matches}个")
        
        # 显示匹配结果统计
        print(f"\n谈判药列统计:")
        print(df['谈判药'].value_counts())
        
        # 保存结果
        output_file = 'c:\\偷偷用用AI\\创新药名单_去重去中药版_最终完整版_含国产进口信息_标记有数据_含谈判药.xlsx'
        df.to_excel(output_file, index=False)
        print(f"\n结果已保存到: {output_file}")
        
        # 显示谈判药品列表
        negotiation_drugs = df[df['谈判药'] == '是']
        print(f"\n谈判药品列表 ({len(negotiation_drugs)}个):")
        print(negotiation_drugs[['药品名称', '国产', '进口', '有数据', '谈判药']].to_string(index=False))
        
        # 显示前10行结果
        print(f"\n前10行结果预览:")
        print(df[['药品名称', '国产', '进口', '有数据', '谈判药']].head(10))
        
        return df
        
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        return None

if __name__ == "__main__":
    # 您可以在这里指定要匹配的具体药品列表
    # 如果为None，将使用默认的谈判药品列表
    custom_drugs = None  # 在这里设置您的药品列表
    
    result_df = add_negotiation_drug_column(custom_drugs)



































