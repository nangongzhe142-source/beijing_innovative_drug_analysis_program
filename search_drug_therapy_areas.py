#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创新药治疗领域搜索脚本
为创新药名单中的每个药品搜索其治疗领域信息
"""

import pandas as pd
import time
from typing import Dict, List, Optional
import re

class DrugTherapyAreaSearcher:
    def __init__(self):
        self.drug_therapy_areas = {}
    
    def search_drug_info(self, drug_name: str) -> Optional[str]:
        """搜索药品的治疗领域信息"""
        try:
            # 清理药品名称，去除剂型信息
            clean_name = self.clean_drug_name(drug_name)
            
            # 根据药品名称特征判断治疗领域
            therapy_area = self.classify_by_name_pattern(clean_name, drug_name)
            if therapy_area:
                return therapy_area
            
            # 如果无法通过名称判断，返回未知
            return "待查证"
            
        except Exception as e:
            print(f"搜索 {drug_name} 时出错: {e}")
            return "待查证"
    
    def clean_drug_name(self, drug_name: str) -> str:
        """清理药品名称，去除剂型等后缀"""
        # 去除常见剂型后缀
        suffixes = ['片', '胶囊', '注射液', '注射用', '乳膏', '鼻喷雾剂', '口服溶液用散', 
                   '肠溶片', '缓释片', '浓溶液', '皮肤点刺液', '组合包装']
        
        clean_name = drug_name
        for suffix in suffixes:
            if clean_name.endswith(suffix):
                clean_name = clean_name[:-len(suffix)]
        
        return clean_name.strip()
    
    def classify_by_name_pattern(self, clean_name: str, original_name: str) -> Optional[str]:
        """根据药品名称特征分类治疗领域"""
        
        # 抗肿瘤药物
        cancer_keywords = ['替尼', '单抗', '利珠', '替雷', '卡瑞', '达可', '泽布', '奥布', 
                          '索凡', '普拉', '帕米', '多纳非尼', '维迪西妥', '赛沃', '奥雷巴',
                          '阿布昔', '莫博赛', '瑞维鲁胺', '贝福替尼', '伏罗尼布', '舒沃替尼',
                          '利特昔', '氘可来昔', '地达西尼', '伯瑞替尼', '格菲妥', '索卡佐利']
        
        # 神经系统用药
        neuro_keywords = ['甘露特纳', '依达拉奉', '利司扑兰', '氘瑞米德韦', '凯普拉生']
        
        # 内分泌系统用药（糖尿病等）
        endo_keywords = ['洛塞那肽', '西格列他钠', '恒格列净', '多格列艾汀', '瑞格列汀']
        
        # 呼吸系统用药
        respiratory_keywords = ['苯环喹溴铵', '鼻喷雾剂']
        
        # 麻醉用药
        anesthesia_keywords = ['瑞马唑仑', '环泊酚', '磷丙泊酚']
        
        # 抗感染药物
        infection_keywords = ['可利霉素', '可洛派韦', '拉维达韦', '依米他韦', '康替唑胺',
                             '奈诺沙星', '艾米替诺福韦', '阿兹夫定', '奥马环素', '先诺特韦',
                             '来瑞特韦', '奥磷布韦', '阿泰特韦', '埃普奈明']
        
        # 免疫系统用药
        immune_keywords = ['泰它西普', '派安普利', '恩沃利', '舒格利', '安巴韦', '奥木替韦',
                          '卡度尼利', '佩索利', '普特利', '斯鲁利', '阿得贝利', '泽贝妥',
                          '托莱西', '纳鲁索拜']
        
        # 血液系统用药
        blood_keywords = ['海曲泊帕', '罗米司韦', '艾贝格司亭', '拓培非格司亭']
        
        # 心血管系统用药
        cardio_keywords = ['爱地那非', '非奈利酮', '维立西呱']
        
        # 皮肤科用药
        derma_keywords = ['本维莫德']
        
        # 消化系统用药
        gastro_keywords = ['安奈拉唑钠']
        
        # 疫苗
        vaccine_keywords = ['疫苗', '新型冠状病毒', '结核杆菌', '轮状病毒', '流感病毒']
        
        # 过敏原检测
        allergen_keywords = ['变应原', '皮肤点刺液']
        
        # 细胞治疗
        cell_therapy_keywords = ['仑赛', '瑞基奥仑赛', '伊基奥仑赛', '纳基奥仑赛']
        
        # 其他特殊用药
        other_keywords = ['西尼莫德', '海博麦布', '艾诺韦林', '托鲁地文拉法辛', '林普利塞',
                         '替戈拉生', '谷美替尼', '伊鲁阿克', '奧特康唑', '培莫沙肽']
        
        # 检查各个类别
        for keyword in cancer_keywords:
            if keyword in clean_name or keyword in original_name:
                return "抗肿瘤药物"
        
        for keyword in neuro_keywords:
            if keyword in clean_name or keyword in original_name:
                return "神经系统用药"
        
        for keyword in endo_keywords:
            if keyword in clean_name or keyword in original_name:
                return "内分泌系统用药"
        
        for keyword in respiratory_keywords:
            if keyword in clean_name or keyword in original_name:
                return "呼吸系统用药"
        
        for keyword in anesthesia_keywords:
            if keyword in clean_name or keyword in original_name:
                return "麻醉用药"
        
        for keyword in infection_keywords:
            if keyword in clean_name or keyword in original_name:
                return "抗感染药物"
        
        for keyword in immune_keywords:
            if keyword in clean_name or keyword in original_name:
                return "免疫系统用药"
        
        for keyword in blood_keywords:
            if keyword in clean_name or keyword in original_name:
                return "血液系统用药"
        
        for keyword in cardio_keywords:
            if keyword in clean_name or keyword in original_name:
                return "心血管系统用药"
        
        for keyword in derma_keywords:
            if keyword in clean_name or keyword in original_name:
                return "皮肤科用药"
        
        for keyword in gastro_keywords:
            if keyword in clean_name or keyword in original_name:
                return "消化系统用药"
        
        for keyword in vaccine_keywords:
            if keyword in clean_name or keyword in original_name:
                return "疫苗"
        
        for keyword in allergen_keywords:
            if keyword in clean_name or keyword in original_name:
                return "过敏原检测试剂"
        
        for keyword in cell_therapy_keywords:
            if keyword in clean_name or keyword in original_name:
                return "细胞治疗药物"
        
        # 特殊处理一些药物
        if '氟马替尼' in clean_name:
            return "抗肿瘤药物"
        if '尼拉帕利' in clean_name:
            return "抗肿瘤药物"
        if '恩沙替尼' in clean_name:
            return "抗肿瘤药物"
        if '氟唑帕利' in clean_name:
            return "抗肿瘤药物"
        if '阿美替尼' in clean_name:
            return "抗肿瘤药物"
        if '伏美替尼' in clean_name:
            return "抗肿瘤药物"
        if '达尔西利' in clean_name:
            return "抗肿瘤药物"
        if '艾诺米替' in clean_name:
            return "抗肿瘤药物"
        
        return None

def main():
    """主函数"""
    print("开始处理创新药治疗领域搜索...")
    
    # 读取Excel文件
    try:
        df = pd.read_excel('创新药名单_去重去中药版_最终完整版.xlsx')
        print(f"成功读取文件，共 {len(df)} 个药品")
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return
    
    # 创建搜索器
    searcher = DrugTherapyAreaSearcher()
    
    # 为每个药品搜索治疗领域
    therapy_areas = []
    for i, row in df.iterrows():
        drug_name = row['药品名称']
        print(f"正在处理第 {i+1}/{len(df)} 个药品: {drug_name}")
        
        therapy_area = searcher.search_drug_info(drug_name)
        therapy_areas.append(therapy_area)
        
        print(f"  -> 治疗领域: {therapy_area}")
        
        # 添加延时避免请求过快
        time.sleep(0.1)
    
    # 将治疗领域添加到DataFrame
    df['治疗领域'] = therapy_areas
    
    # 保存更新后的文件
    try:
        output_file = '创新药名单_含治疗领域_最终版.xlsx'
        df.to_excel(output_file, index=False)
        print(f"\n处理完成！结果已保存到: {output_file}")
        
        # 显示统计信息
        print("\n治疗领域统计:")
        area_counts = df['治疗领域'].value_counts()
        for area, count in area_counts.items():
            print(f"  {area}: {count} 个")
            
    except Exception as e:
        print(f"保存文件失败: {e}")

if __name__ == "__main__":
    main()
