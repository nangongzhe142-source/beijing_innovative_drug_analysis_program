#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医院分类识别系统
构建医院名称标准化和分类匹配系统，区分委属、市属、其他医院
"""

import pandas as pd
import numpy as np
import logging
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from difflib import SequenceMatcher

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hospital_classifier_new.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HospitalClassifierNew:
    """医院分类识别器"""
    
    def __init__(self):
        """初始化医院分类器"""
        self.base_path = Path('.')
        
        # 委属医院名单（11家）
        self.weishu_hospitals = [
            '北京医院',
            '中日友好医院', 
            '中国医学科学院协和医院',
            '中国医学科学院阜外心血管病医院',
            '中国医学科学院肿瘤医院',
            '中国医学科学院整形外科医院',
            '北京大学第一医院',
            '北京大学人民医院',
            '北京大学第三医院',
            '北京大学口腔医院',
            '北京大学第六医院'
        ]
        
        # 市属医院名单（22家）
        self.shishu_hospitals = [
            '北京友谊医院',
            '北京同仁医院',
            '北京朝阳医院',
            '北京积水潭医院',
            '北京天坛医院',
            '北京安贞医院',
            '北京世纪坛医院',
            '宣武医院',
            '北京清华长庚医院',
            '北京中医医院',
            '北京肿瘤医院',
            '北京儿童医院',
            '首都儿科研究所',
            '北京妇产医院',
            '北京口腔医院',
            '北京胸科医院',
            '北京佑安医院',
            '北京地坛医院',
            '北京安定医院',
            '北京回龙观医院',
            '北京老年医院',
            '北京小汤山医院'
        ]
        
        # 医院名称标准化映射
        self.hospital_mapping = {}
        
        # 初始化分类数据
        self._initialize_classification_data()
        
        logger.info("医院分类识别器初始化完成")
        logger.info(f"委属医院: {len(self.weishu_hospitals)}家")
        logger.info(f"市属医院: {len(self.shishu_hospitals)}家")
    
    def _initialize_classification_data(self):
        """初始化分类数据"""
        # 创建标准化映射
        all_hospitals = self.weishu_hospitals + self.shishu_hospitals
        
        for hospital in all_hospitals:
            # 标准化名称作为键
            normalized_name = self.normalize_hospital_name(hospital)
            
            # 确定分类
            if hospital in self.weishu_hospitals:
                category = '委属'
            else:
                category = '市属'
            
            self.hospital_mapping[normalized_name] = {
                'original_name': hospital,
                'category': category,
                'level': 3  # 委属和市属都是三级医院
            }
    
    def normalize_hospital_name(self, name: str) -> str:
        """
        标准化医院名称
        
        Args:
            name: 原始医院名称
            
        Returns:
            str: 标准化后的医院名称
        """
        if pd.isna(name) or not name:
            return ""
        
        name = str(name).strip()
        
        # 去除常见的前缀
        prefixes_to_remove = [
            '北京市', '北京', '首都医科大学附属', '中国医学科学院', 
            '中国中医科学院', '清华大学附属', '首都儿科研究所附属'
        ]
        
        for prefix in prefixes_to_remove:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()
        
        # 去除括号内容
        name = re.sub(r'[（(].*?[）)]', '', name)
        
        # 去除多余空格
        name = re.sub(r'\s+', '', name)
        
        # 标准化常见别名
        name_mappings = {
            '协和': '协和医院',
            '阜外': '阜外心血管病医院',
            '北大一院': '第一医院',
            '北大人民': '人民医院',
            '北大三院': '第三医院',
            '北大口腔': '口腔医院',
            '北大六院': '第六医院',
            '友谊': '友谊医院',
            '同仁': '同仁医院',
            '朝阳': '朝阳医院',
            '积水潭': '积水潭医院',
            '天坛': '天坛医院',
            '安贞': '安贞医院',
            '世纪坛': '世纪坛医院',
            '宣武': '宣武医院',
            '长庚': '清华长庚医院',
            '中医': '中医医院',
            '肿瘤': '肿瘤医院',
            '儿童': '儿童医院',
            '儿研所': '儿科研究所',
            '妇产': '妇产医院',
            '口腔': '口腔医院',
            '胸科': '胸科医院',
            '佑安': '佑安医院',
            '地坛': '地坛医院',
            '安定': '安定医院',
            '回龙观': '回龙观医院',
            '老年': '老年医院',
            '小汤山': '小汤山医院'
        }
        
        for alias, standard in name_mappings.items():
            if alias in name and standard not in name:
                name = name.replace(alias, standard)
        
        return name
    
    def calculate_similarity(self, name1: str, name2: str) -> float:
        """
        计算两个医院名称的相似度
        
        Args:
            name1: 医院名称1
            name2: 医院名称2
            
        Returns:
            float: 相似度分数 (0-1)
        """
        if not name1 or not name2:
            return 0.0
        
        # 标准化名称
        norm_name1 = self.normalize_hospital_name(name1)
        norm_name2 = self.normalize_hospital_name(name2)
        
        # 完全匹配
        if norm_name1 == norm_name2:
            return 1.0
        
        # 包含关系（更严格的匹配）
        if len(norm_name1) >= 3 and len(norm_name2) >= 3:
            if norm_name1 in norm_name2 or norm_name2 in norm_name1:
                return 0.9
        
        # 序列匹配
        seq_similarity = SequenceMatcher(None, norm_name1, norm_name2).ratio()
        
        # 关键词匹配
        keywords1 = set(re.findall(r'[\u4e00-\u9fff]+', norm_name1))
        keywords2 = set(re.findall(r'[\u4e00-\u9fff]+', norm_name2))
        
        if keywords1 and keywords2:
            keyword_similarity = len(keywords1 & keywords2) / len(keywords1 | keywords2)
            # 综合相似度
            return max(seq_similarity, keyword_similarity)
        
        return seq_similarity
    
    def classify_hospital(self, hospital_name: str, hospital_level: int = None) -> Dict:
        """
        分类单个医院
        
        Args:
            hospital_name: 医院名称
            hospital_level: 医院级别 (1=一级, 2=二级, 3=三级)
            
        Returns:
            Dict: 分类结果
        """
        result = {
            'original_name': hospital_name,
            'normalized_name': self.normalize_hospital_name(hospital_name),
            'category': '其他',
            'level': hospital_level or 3,
            'confidence': 0.0,
            'matched_hospital': None
        }
        
        if not hospital_name or pd.isna(hospital_name):
            return result
        
        normalized_name = result['normalized_name']
        
        # 对于一级和二级医院，直接分类为其他（委属和市属医院只存在于三级医院）
        if hospital_level in [1, 2]:
            result.update({
                'category': '其他',
                'confidence': 1.0
            })
            return result
        
        # 对于三级医院，进行详细匹配
        best_match = None
        best_similarity = 0.0
        best_category = '其他'
        
        # 检查委属医院
        for weishu_hospital in self.weishu_hospitals:
            similarity = self.calculate_similarity(hospital_name, weishu_hospital)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = weishu_hospital
                best_category = '委属'
        
        # 检查市属医院
        for shishu_hospital in self.shishu_hospitals:
            similarity = self.calculate_similarity(hospital_name, shishu_hospital)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = shishu_hospital
                best_category = '市属'
        
        # 设置阈值（提高阈值以减少误分类）
        confidence_threshold = 0.8

        if best_similarity >= confidence_threshold:
            result.update({
                'category': best_category,
                'confidence': best_similarity,
                'matched_hospital': best_match
            })
        else:
            # 对于相似度较高但未达到阈值的情况，进行二次验证
            if best_similarity >= 0.6 and best_match:
                # 检查是否包含关键词
                normalized_input = self.normalize_hospital_name(hospital_name)
                normalized_match = self.normalize_hospital_name(best_match)

                # 如果输入名称包含匹配医院的关键部分，则认为匹配
                key_parts = [part for part in normalized_match.split() if len(part) >= 2]
                if any(part in normalized_input for part in key_parts):
                    result.update({
                        'category': best_category,
                        'confidence': best_similarity,
                        'matched_hospital': best_match
                    })
                else:
                    result.update({
                        'category': '其他',
                        'confidence': best_similarity,
                        'matched_hospital': best_match
                    })
            else:
                result.update({
                    'category': '其他',
                    'confidence': best_similarity,
                    'matched_hospital': best_match if best_similarity > 0.3 else None
                })
        
        return result

    def classify_hospitals_batch(self, hospital_data: pd.DataFrame) -> pd.DataFrame:
        """
        批量分类医院

        Args:
            hospital_data: 包含医院数据的DataFrame

        Returns:
            pd.DataFrame: 添加分类信息的DataFrame
        """
        logger.info(f"开始批量分类医院，共{len(hospital_data)}条记录")

        # 添加分类列
        hospital_data = hospital_data.copy()
        hospital_data['hospital_category'] = '其他'
        hospital_data['hospital_confidence'] = 0.0
        hospital_data['matched_hospital'] = None

        # 按医院名称分组，避免重复计算
        unique_hospitals = hospital_data[['hospital_name', 'hospital_level']].drop_duplicates()

        classification_cache = {}

        for _, row in unique_hospitals.iterrows():
            hospital_name = row['hospital_name']
            hospital_level = row['hospital_level']

            # 转换级别（委属和市属医院只存在于三级医院）
            if hospital_level == '三级':
                level_num = 3
            elif hospital_level == '二级':
                level_num = 2  # 二级医院只能是其他
            elif hospital_level == '一级':
                level_num = 1  # 一级医院只能是其他
            else:
                level_num = 3  # 默认三级

            # 分类医院
            classification = self.classify_hospital(hospital_name, level_num)
            classification_cache[hospital_name] = classification

        # 应用分类结果
        for idx, row in hospital_data.iterrows():
            hospital_name = row['hospital_name']
            hospital_level = row['hospital_level']

            if hospital_name in classification_cache:
                classification = classification_cache[hospital_name]

                # 强制检查：一级和二级医院只能是"其他"
                if hospital_level in ['一级', '二级'] and classification['category'] in ['委属', '市属']:
                    hospital_data.at[idx, 'hospital_category'] = '其他'
                    hospital_data.at[idx, 'hospital_confidence'] = 1.0
                    hospital_data.at[idx, 'matched_hospital'] = None
                else:
                    hospital_data.at[idx, 'hospital_category'] = classification['category']
                    hospital_data.at[idx, 'hospital_confidence'] = classification['confidence']
                    hospital_data.at[idx, 'matched_hospital'] = classification['matched_hospital']

        # 统计分类结果
        category_counts = hospital_data['hospital_category'].value_counts()
        logger.info(f"分类结果统计: {dict(category_counts)}")

        return hospital_data

    def get_classification_summary(self, classified_data: pd.DataFrame) -> pd.DataFrame:
        """
        获取分类摘要统计

        Args:
            classified_data: 已分类的数据

        Returns:
            pd.DataFrame: 分类摘要
        """
        summary_data = []

        for year in classified_data['year'].unique():
            year_data = classified_data[classified_data['year'] == year]

            for level in year_data['hospital_level'].unique():
                level_data = year_data[year_data['hospital_level'] == level]

                for category in ['委属', '市属', '其他']:
                    category_data = level_data[level_data['hospital_category'] == category]

                    if len(category_data) > 0:
                        summary_data.append({
                            'year': year,
                            'hospital_level': level,
                            'hospital_category': category,
                            'hospital_count': category_data['hospital_name'].nunique(),
                            'record_count': len(category_data),
                            'total_sales_amount': category_data['sales_amount'].sum(),
                            'total_sales_volume': category_data['sales_volume'].sum(),
                            'insurance_drug_count': len(category_data[category_data['is_insurance'] == True]),
                            'non_insurance_drug_count': len(category_data[category_data['is_insurance'] == False])
                        })

        return pd.DataFrame(summary_data)

    def save_classification_mapping(self, output_file: str = '医院分类映射.json'):
        """保存分类映射到文件"""
        mapping_data = {
            'weishu_hospitals': self.weishu_hospitals,
            'shishu_hospitals': self.shishu_hospitals,
            'hospital_mapping': self.hospital_mapping
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, ensure_ascii=False, indent=2)

        logger.info(f"医院分类映射已保存到: {output_file}")


def main():
    """主函数，用于测试"""
    classifier = HospitalClassifierNew()
    
    # 测试单个医院分类
    test_hospitals = [
        '北京友谊医院',
        '中国医学科学院协和医院',
        '北京大学第一医院',
        '首都医科大学附属北京朝阳医院',
        '北京市某某医院',
        '清华大学附属北京清华长庚医院'
    ]
    
    logger.info("=== 测试单个医院分类 ===")
    for hospital in test_hospitals:
        result = classifier.classify_hospital(hospital, 3)
        logger.info(f"{hospital} -> {result['category']} (置信度: {result['confidence']:.2f})")


if __name__ == "__main__":
    main()
