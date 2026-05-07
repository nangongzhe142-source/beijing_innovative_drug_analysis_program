# 数据处理脚本

本分类包含数据读取、编码修复、名单清洗、医院分类和匹配前处理脚本。

## 典型脚本
- `fix_csv_encoding.py`
- `hospital_classifier_new.py`
- `search_drug_therapy_areas.py`
- `add_negotiation_drug_column.py`
- `innovative_drug_tcm_matcher.py`
- `extract_innovative_by_list.py`

## 执行建议
1. 先处理编码和字段可读性；
2. 再完善药品名单标签（治疗领域、谈判药）；
3. 最后执行跨年份抽取脚本产出可分析数据集。
