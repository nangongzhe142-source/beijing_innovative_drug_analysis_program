#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创新药与中药成分匹配系统
将创新药名单与中药数据进行匹配，区分含中药成分和纯化学创新药
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path

class InnovativeDrugTCMMatcher:
    def __init__(self):
        self.innovative_drugs = None
        self.tcm_data = None
        self.tcm_patent_data = None
        self.matched_drugs = []
        self.unmatched_drugs = []
        
    def load_data(self):
        """加载所有数据文件"""
        print("=== 开始加载数据文件 ===")
        
        # 1. 加载创新药名单
        try:
            self.innovative_drugs = pd.read_excel("创新药名单 国产进口.xlsx")
            print(f"成功加载创新药名单，共{len(self.innovative_drugs)}条记录")
            print("创新药名单列名:", self.innovative_drugs.columns.tolist())
            print("前5行数据:")
            print(self.innovative_drugs.head())
        except Exception as e:
            print(f"加载创新药名单失败: {e}")
            return False
            
        # 2. 加载中药数据
        try:
            self.tcm_data = pd.read_excel("中药数据A列不重复项_简化版.xlsx")
            print(f"\n成功加载中药数据，共{len(self.tcm_data)}条记录")
            print("中药数据列名:", self.tcm_data.columns.tolist())
            print("前5行数据:")
            print(self.tcm_data.head())
        except Exception as e:
            print(f"加载中药数据失败: {e}")
            return False
            
        # 3. 加载中成药数据
        try:
            self.tcm_patent_data = pd.read_excel("中成药不重复清理结果.xlsx")
            print(f"\n成功加载中成药数据，共{len(self.tcm_patent_data)}条记录")
            print("中成药数据列名:", self.tcm_patent_data.columns.tolist())
            print("前5行数据:")
            print(self.tcm_patent_data.head())
        except Exception as e:
            print(f"加载中成药数据失败: {e}")
            return False
            
        return True
    
    def clean_drug_name(self, name):
        """清理药品名称，去除特殊字符和空格"""
        if pd.isna(name):
            return ""
        
        name = str(name).strip()
        # 去除常见的剂型后缀
        suffixes = ['片', '胶囊', '颗粒', '丸', '散', '膏', '贴', '注射液', '注射剂', 
                   '口服液', '糖浆', '滴丸', '软胶囊', '肠溶片', '缓释片', '控释片']
        
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
                
        return name.strip()
    
    def extract_drug_names(self):
        """提取各数据源的药品名称"""
        print("\n=== 提取药品名称 ===")
        
        # 提取创新药名称
        if '药品名称' in self.innovative_drugs.columns:
            innovative_names = self.innovative_drugs['药品名称'].dropna().unique()
        elif '药品通用名' in self.innovative_drugs.columns:
            innovative_names = self.innovative_drugs['药品通用名'].dropna().unique()
        else:
            # 使用第一列作为药品名称
            innovative_names = self.innovative_drugs.iloc[:, 0].dropna().unique()
            
        print(f"创新药名称数量: {len(innovative_names)}")
        print("创新药名称示例:", innovative_names[:5])
        
        # 提取中药名称
        if '药品名称' in self.tcm_data.columns:
            tcm_names = self.tcm_data['药品名称'].dropna().unique()
        elif 'A' in self.tcm_data.columns:
            tcm_names = self.tcm_data['A'].dropna().unique()
        else:
            tcm_names = self.tcm_data.iloc[:, 0].dropna().unique()
            
        print(f"中药名称数量: {len(tcm_names)}")
        print("中药名称示例:", tcm_names[:5])
        
        # 提取中成药名称
        if '药品名称' in self.tcm_patent_data.columns:
            tcm_patent_names = self.tcm_patent_data['药品名称'].dropna().unique()
        elif 'A' in self.tcm_patent_data.columns:
            tcm_patent_names = self.tcm_patent_data['A'].dropna().unique()
        else:
            tcm_patent_names = self.tcm_patent_data.iloc[:, 1].dropna().unique()  # 使用第二列，第一列是序号
            
        print(f"中成药名称数量: {len(tcm_patent_names)}")
        print("中成药名称示例:", tcm_patent_names[:5])
        
        return innovative_names, tcm_names, tcm_patent_names
    
    def match_drugs(self):
        """执行药品匹配"""
        print("\n=== 开始药品匹配 ===")
        
        innovative_names, tcm_names, tcm_patent_names = self.extract_drug_names()
        
        # 合并中药和中成药名称
        all_tcm_names = set(tcm_names) | set(tcm_patent_names)
        print(f"合并后中药总数量: {len(all_tcm_names)}")
        
        matched_count = 0
        unmatched_count = 0
        
        for innovative_drug in innovative_names:
            if pd.isna(innovative_drug):
                continue
                
            innovative_clean = self.clean_drug_name(innovative_drug)
            is_matched = False
            matched_tcm = []
            
            # 检查是否包含任何中药成分
            for tcm_drug in all_tcm_names:
                if pd.isna(tcm_drug):
                    continue
                    
                tcm_clean = self.clean_drug_name(tcm_drug)
                
                # 匹配逻辑：创新药名称包含中药名称即算匹配
                if tcm_clean and (tcm_clean in innovative_clean or innovative_clean in tcm_clean):
                    is_matched = True
                    matched_tcm.append(tcm_drug)
            
            # 获取创新药的完整信息
            if '药品名称' in self.innovative_drugs.columns:
                drug_info = self.innovative_drugs[self.innovative_drugs['药品名称'] == innovative_drug]
            elif '药品通用名' in self.innovative_drugs.columns:
                drug_info = self.innovative_drugs[self.innovative_drugs['药品通用名'] == innovative_drug]
            else:
                drug_info = self.innovative_drugs[self.innovative_drugs.iloc[:, 0] == innovative_drug]
            
            if len(drug_info) > 0:
                drug_record = drug_info.iloc[0].to_dict()
                drug_record['匹配的中药成分'] = '; '.join([str(tcm) for tcm in matched_tcm]) if matched_tcm else ''
                
                if is_matched:
                    self.matched_drugs.append(drug_record)
                    matched_count += 1
                else:
                    self.unmatched_drugs.append(drug_record)
                    unmatched_count += 1
        
        print(f"匹配完成:")
        print(f"  含中药成分的创新药: {matched_count}个")
        print(f"  纯化学创新药: {unmatched_count}个")
        
        return matched_count, unmatched_count
    
    def save_results(self):
        """保存匹配结果"""
        print("\n=== 保存匹配结果 ===")
        
        # 保存含中药成分的创新药
        if self.matched_drugs:
            matched_df = pd.DataFrame(self.matched_drugs)
            matched_filename = "含中药成分的创新药名单.xlsx"
            matched_df.to_excel(matched_filename, index=False)
            print(f"已保存含中药成分的创新药: {matched_filename}")
            print(f"数量: {len(matched_df)}")
            
            # 显示匹配示例
            print("\n含中药成分的创新药示例:")
            for i, row in matched_df.head(10).iterrows():
                drug_name = row.get('药品名称', row.get('药品通用名', str(row.iloc[0])))
                tcm_components = row.get('匹配的中药成分', '')
                print(f"  {drug_name} -> {tcm_components}")
        
        # 保存纯化学创新药
        if self.unmatched_drugs:
            unmatched_df = pd.DataFrame(self.unmatched_drugs)
            unmatched_filename = "纯化学创新药名单.xlsx"
            unmatched_df.to_excel(unmatched_filename, index=False)
            print(f"\n已保存纯化学创新药: {unmatched_filename}")
            print(f"数量: {len(unmatched_df)}")
            
            # 显示未匹配示例
            print("\n纯化学创新药示例:")
            for i, row in unmatched_df.head(10).iterrows():
                drug_name = row.get('药品名称', row.get('药品通用名', str(row.iloc[0])))
                print(f"  {drug_name}")
        
        # 生成匹配统计报告
        self.generate_summary_report(len(self.matched_drugs), len(self.unmatched_drugs))
    
    def generate_summary_report(self, matched_count, unmatched_count):
        """生成匹配统计报告"""
        total_count = matched_count + unmatched_count
        
        report = f"""
=== 创新药与中药成分匹配统计报告 ===

总创新药数量: {total_count}
含中药成分的创新药: {matched_count} ({matched_count/total_count*100:.1f}%)
纯化学创新药: {unmatched_count} ({unmatched_count/total_count*100:.1f}%)

匹配规则: 创新药名称包含中药或中成药名称即算匹配成功

输出文件:
1. 含中药成分的创新药名单.xlsx - 包含匹配的中药成分信息
2. 纯化学创新药名单.xlsx - 不含中药成分的创新药

生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        print(report)
        
        # 保存报告到文件
        with open("创新药中药成分匹配报告.txt", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("已保存匹配报告: 创新药中药成分匹配报告.txt")

def main():
    """主函数"""
    matcher = InnovativeDrugTCMMatcher()
    
    # 加载数据
    if not matcher.load_data():
        print("数据加载失败，程序退出")
        return
    
    # 执行匹配
    matcher.match_drugs()
    
    # 保存结果
    matcher.save_results()
    
    print("\n=== 匹配完成 ===")

if __name__ == "__main__":
    main()
