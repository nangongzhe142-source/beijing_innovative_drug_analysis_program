#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
药品审批关联规则挖掘计算程序
用于计算支持度、置信度、提升度等关联规则指标
"""

import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class DrugApprovalAssociationRules:
    """药品审批关联规则挖掘类"""
    
    def __init__(self):
        self.data = None
        self.total_records = 0
        self.frequent_itemsets = {}
        self.association_rules = []
    
    def load_sample_data(self):
        """加载示例数据"""
        # 模拟药品审批数据
        sample_data = {
            'drug_id': range(1, 343),  # 342个药物
            'indication': np.random.choice(['晚期实体瘤', '心血管疾病', '糖尿病', '罕见病', '精神疾病'], 342),
            'trial_design': np.random.choice(['随机双盲', '随机开放', '单臂试验', '历史对照'], 342),
            'control_type': np.random.choice(['安慰剂对照', '阳性对照', '最佳支持治疗', '历史对照', '无对照'], 342),
            'center_count': np.random.choice(['<10', '10-50', '≥50'], 342),
            'primary_endpoint': np.random.choice(['总生存期', '无进展生存期', '客观缓解率', '替代终点'], 342),
            'secondary_endpoint': np.random.choice(['有', '无'], 342),
            'biomarker': np.random.choice(['有', '无'], 342),
            'age_range': np.random.choice(['18-65岁', '18-75岁', '全年龄段', '儿科'], 342),
            'disease_severity': np.random.choice(['早期', '中期', '晚期/转移性', '复发/难治'], 342),
            'prior_treatment': np.random.choice(['初治', '1线失败', '≥2线失败', '无标准治疗'], 342),
            'approval_status': np.random.choice(['获批', '拒绝'], 342, p=[0.667, 0.333])  # 66.7%获批率
        }
        
        # 创建特定的成功模式数据
        # 模拟"晚期实体瘤 + 随机双盲 + 安慰剂对照 + ≥50中心"的高成功率模式
        success_pattern_indices = np.random.choice(342, 53, replace=False)
        for idx in success_pattern_indices:
            sample_data['indication'][idx] = '晚期实体瘤'
            sample_data['trial_design'][idx] = '随机双盲'
            sample_data['control_type'][idx] = '安慰剂对照'
            sample_data['center_count'][idx] = '≥50'
            # 89.3%的成功率，所以53个中47个获批
            if idx in success_pattern_indices[:47]:
                sample_data['approval_status'][idx] = '获批'
            else:
                sample_data['approval_status'][idx] = '拒绝'
        
        self.data = pd.DataFrame(sample_data)
        self.total_records = len(self.data)
        return self.data
    
    def load_data(self, data_path=None, data_df=None):
        """加载数据"""
        if data_df is not None:
            self.data = data_df
        elif data_path:
            self.data = pd.read_csv(data_path)
        else:
            self.data = self.load_sample_data()
        
        self.total_records = len(self.data)
        print(f"数据加载完成，共{self.total_records}条记录")
        return self.data
    
    def create_transaction_data(self, target_column='approval_status'):
        """将数据转换为事务格式"""
        transactions = []
        
        for _, row in self.data.iterrows():
            transaction = []
            for col in self.data.columns:
                if col != target_column and col != 'drug_id':
                    # 创建"属性=值"格式的项
                    item = f"{col}={row[col]}"
                    transaction.append(item)
            
            # 添加目标变量
            target_item = f"{target_column}={row[target_column]}"
            transaction.append(target_item)
            
            transactions.append(transaction)
        
        return transactions
    
    def calculate_support(self, itemset, transactions):
        """计算支持度"""
        count = 0
        for transaction in transactions:
            if all(item in transaction for item in itemset):
                count += 1
        
        support = count / len(transactions)
        return support, count
    
    def find_frequent_itemsets(self, transactions, min_support=0.01):
        """发现频繁项集"""
        # 获取所有单项
        all_items = set()
        for transaction in transactions:
            all_items.update(transaction)
        
        # 计算单项频繁集
        frequent_1_itemsets = {}
        for item in all_items:
            support, count = self.calculate_support([item], transactions)
            if support >= min_support:
                frequent_1_itemsets[frozenset([item])] = {
                    'support': support,
                    'count': count
                }
        
        self.frequent_itemsets[1] = frequent_1_itemsets
        
        # 生成更大的频繁项集
        k = 2
        while True:
            # 生成候选项集
            candidates = self.generate_candidates(list(self.frequent_itemsets[k-1].keys()), k)
            
            if not candidates:
                break
            
            frequent_k_itemsets = {}
            for candidate in candidates:
                support, count = self.calculate_support(list(candidate), transactions)
                if support >= min_support:
                    frequent_k_itemsets[candidate] = {
                        'support': support,
                        'count': count
                    }
            
            if not frequent_k_itemsets:
                break
            
            self.frequent_itemsets[k] = frequent_k_itemsets
            k += 1
        
        return self.frequent_itemsets
    
    def generate_candidates(self, frequent_itemsets, k):
        """生成候选项集"""
        candidates = []
        n = len(frequent_itemsets)
        
        for i in range(n):
            for j in range(i + 1, n):
                # 合并两个(k-1)项集
                itemset1 = frequent_itemsets[i]
                itemset2 = frequent_itemsets[j]
                
                # 检查是否可以合并
                union = itemset1.union(itemset2)
                if len(union) == k:
                    candidates.append(union)
        
        return candidates
    
    def generate_association_rules(self, min_confidence=0.5, target_consequent='approval_status=获批'):
        """生成关联规则"""
        self.association_rules = []
        
        # 遍历所有频繁项集（k>=2）
        for k in range(2, len(self.frequent_itemsets) + 1):
            for itemset, itemset_info in self.frequent_itemsets[k].items():
                # 生成所有可能的前件和后件组合
                items = list(itemset)
                
                # 检查是否包含目标后件
                if target_consequent in items:
                    # 生成前件（去除目标后件）
                    antecedent_items = [item for item in items if item != target_consequent]
                    
                    if len(antecedent_items) > 0:
                        antecedent = frozenset(antecedent_items)
                        consequent = frozenset([target_consequent])
                        
                        # 计算置信度
                        antecedent_support = self.get_itemset_support(antecedent)
                        if antecedent_support > 0:
                            confidence = itemset_info['support'] / antecedent_support
                            
                            if confidence >= min_confidence:
                                # 计算提升度
                                consequent_support = self.get_itemset_support(consequent)
                                lift = confidence / consequent_support if consequent_support > 0 else 0
                                
                                rule = {
                                    'antecedent': list(antecedent),
                                    'consequent': list(consequent),
                                    'support': itemset_info['support'],
                                    'confidence': confidence,
                                    'lift': lift,
                                    'count': itemset_info['count'],
                                    'antecedent_count': int(antecedent_support * self.total_records)
                                }
                                
                                self.association_rules.append(rule)
        
        # 按置信度排序
        self.association_rules.sort(key=lambda x: x['confidence'], reverse=True)
        return self.association_rules
    
    def get_itemset_support(self, itemset):
        """获取项集的支持度"""
        itemset_size = len(itemset)
        
        if itemset_size in self.frequent_itemsets:
            if itemset in self.frequent_itemsets[itemset_size]:
                return self.frequent_itemsets[itemset_size][itemset]['support']
        
        # 如果不在频繁项集中，重新计算
        transactions = self.create_transaction_data()
        support, _ = self.calculate_support(list(itemset), transactions)
        return support
    
    def print_rule_details(self, rule_index=0):
        """打印规则详细信息"""
        if rule_index >= len(self.association_rules):
            print("规则索引超出范围")
            return
        
        rule = self.association_rules[rule_index]
        
        print("=" * 60)
        print(f"关联规则 #{rule_index + 1}")
        print("=" * 60)
        
        # 格式化前件
        antecedent_str = " AND ".join(rule['antecedent'])
        consequent_str = " AND ".join(rule['consequent'])
        
        print(f"IF ({antecedent_str})")
        print(f"THEN {consequent_str}")
        print()
        
        # 计算具体数值
        total_records = self.total_records
        rule_count = rule['count']
        antecedent_count = rule['antecedent_count']
        
        print(f"支持度 = {rule['support']:.3f} ({rule_count}/{total_records}个药物符合此模式)")
        print(f"置信度 = {rule['confidence']:.3f} ({rule_count}个中有{rule_count}个获批)")
        print(f"提升度 = {rule['lift']:.2f} (比总体成功率高{(rule['lift']-1)*100:.1f}%)")
        print()
        
        # 计算总体获批率
        overall_approval_rate = len(self.data[self.data['approval_status'] == '获批']) / total_records
        print(f"总体获批率 = {overall_approval_rate:.1%}")
        print(f"该规则获批率 = {rule['confidence']:.1%}")
        print(f"提升效果 = {rule['confidence'] - overall_approval_rate:.1%}")
        print("=" * 60)
    
    def export_rules_to_csv(self, filename='association_rules.csv'):
        """导出规则到CSV文件"""
        if not self.association_rules:
            print("没有生成关联规则")
            return
        
        # 准备导出数据
        export_data = []
        for i, rule in enumerate(self.association_rules):
            antecedent_str = " AND ".join(rule['antecedent'])
            consequent_str = " AND ".join(rule['consequent'])
            
            export_data.append({
                'rule_id': i + 1,
                'antecedent': antecedent_str,
                'consequent': consequent_str,
                'support': rule['support'],
                'confidence': rule['confidence'],
                'lift': rule['lift'],
                'count': rule['count'],
                'antecedent_count': rule['antecedent_count']
            })
        
        df = pd.DataFrame(export_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"关联规则已导出到 {filename}")
    
    def analyze_specific_pattern(self, conditions, target='approval_status=获批'):
        """分析特定模式的统计指标"""
        print("=" * 60)
        print("特定模式分析")
        print("=" * 60)
        
        # 构建查询条件
        query_conditions = []
        for key, value in conditions.items():
            query_conditions.append(f"{key} == '{value}'")
        
        query_str = " & ".join(query_conditions)
        
        # 筛选符合条件的数据
        matching_data = self.data.query(query_str)
        total_matching = len(matching_data)
        
        # 计算获批数量
        approved_data = matching_data[matching_data['approval_status'] == '获批']
        approved_count = len(approved_data)
        
        # 计算指标
        support = total_matching / self.total_records
        confidence = approved_count / total_matching if total_matching > 0 else 0
        
        # 计算总体获批率
        overall_approval_rate = len(self.data[self.data['approval_status'] == '获批']) / self.total_records
        lift = confidence / overall_approval_rate if overall_approval_rate > 0 else 0
        
        # 打印结果
        condition_str = " AND ".join([f"{k}={v}" for k, v in conditions.items()])
        print(f"IF ({condition_str})")
        print(f"THEN 审批成功率 = {confidence:.1%}")
        print()
        print(f"支持度 = {support:.3f} ({total_matching}/{self.total_records}个药物符合此模式)")
        print(f"置信度 = {confidence:.3f} ({total_matching}个中有{approved_count}个获批)")
        print(f"提升度 = {lift:.2f} (比总体成功率{overall_approval_rate:.1%}高{(lift-1)*100:.1f}%)")
        print("=" * 60)
        
        return {
            'support': support,
            'confidence': confidence,
            'lift': lift,
            'total_matching': total_matching,
            'approved_count': approved_count,
            'overall_approval_rate': overall_approval_rate
        }

def main():
    """主函数 - 演示程序使用"""
    print("药品审批关联规则挖掘程序")
    print("=" * 60)
    
    # 创建分析器实例
    analyzer = DrugApprovalAssociationRules()
    
    # 加载数据
    print("1. 加载数据...")
    data = analyzer.load_data()
    print(f"数据概览：")
    print(data.head())
    print()
    
    # 创建事务数据
    print("2. 创建事务数据...")
    transactions = analyzer.create_transaction_data()
    print(f"事务数据示例：{transactions[0]}")
    print()
    
    # 发现频繁项集
    print("3. 发现频繁项集...")
    frequent_itemsets = analyzer.find_frequent_itemsets(transactions, min_support=0.01)
    print(f"发现 {sum(len(itemsets) for itemsets in frequent_itemsets.values())} 个频繁项集")
    print()
    
    # 生成关联规则
    print("4. 生成关联规则...")
    rules = analyzer.generate_association_rules(min_confidence=0.6)
    print(f"生成 {len(rules)} 条关联规则")
    print()
    
    # 显示前5条规则
    print("5. 显示前5条关联规则...")
    for i in range(min(5, len(rules))):
        analyzer.print_rule_details(i)
        print()
    
    # 分析特定模式
    print("6. 分析特定模式...")
    conditions = {
        'indication': '晚期实体瘤',
        'trial_design': '随机双盲',
        'control_type': '安慰剂对照',
        'center_count': '≥50'
    }
    
    result = analyzer.analyze_specific_pattern(conditions)
    print()
    
    # 导出结果
    print("7. 导出结果...")
    analyzer.export_rules_to_csv('drug_approval_rules.csv')
    
    print("分析完成！")

if __name__ == "__main__":
    main()
