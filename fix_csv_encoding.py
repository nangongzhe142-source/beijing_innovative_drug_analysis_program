#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复2022年CSV文件编码问题
"""

import pandas as pd
import chardet

def detect_and_read_csv():
    """检测并读取CSV文件"""
    file_path = "2022年/RPT_DRUG_USE_2022_BIG-北京市-三级.csv"
    
    # 检测文件编码
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # 读取前10000字节
        result = chardet.detect(raw_data)
        print(f"检测到的编码: {result}")
    
    # 尝试使用检测到的编码
    detected_encoding = result['encoding']
    
    try:
        df = pd.read_csv(file_path, encoding=detected_encoding)
        print(f"成功使用编码 {detected_encoding} 读取文件")
        print(f"数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"使用检测编码失败: {e}")
        
        # 尝试其他编码
        encodings = ['gb18030', 'big5', 'latin1', 'cp1252']
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"成功使用编码 {encoding} 读取文件")
                print(f"数据形状: {df.shape}")
                print(f"列名: {list(df.columns)}")
                return df
            except:
                continue
        
        print("所有编码尝试都失败")
        return None

if __name__ == "__main__":
    df = detect_and_read_csv()
    if df is not None:
        print("\n前5行数据:")
        print(df.head())
