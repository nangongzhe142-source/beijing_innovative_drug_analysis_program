# 方法学与处理流程

## 总体方法
项目采用“政策与调研信息 + 三年医院药品使用数据 + Python 脚本计算”的研究路径。

从代码可验证的技术路径包括：
- 多源数据读取（Excel/CSV）与编码检测；
- 医院分级与医院类型识别（委属/市属/其他）；
- 药品名称标准化与匹配（精确匹配、包含匹配、模糊匹配）；
- 医保状态切分（医保药/非医保药）；
- 指标计算（金额、用量、进院率、单价、排名、治疗领域分布）；
- 输出多工作表 Excel 报告、JSON 和校验报告。

## 数据处理流程（按脚本职责归纳）
1. 原始数据读取与编码处理  
   - 典型脚本：`fix_csv_encoding.py`、`comprehensive_hospital_drug_analysis_system.py`
2. 名单整理与药品匹配  
   - 典型脚本：`extract_innovative_by_list.py`、`add_negotiation_drug_column.py`、`innovative_drug_tcm_matcher.py`
3. 医院分类与结构化  
   - 典型脚本：`hospital_classifier_new.py`、`verify_data_correctness.py`
4. 核心统计分析  
   - 典型脚本：`仙尊大人_精确进院率计算系统.py`、`calculate_all_levels_prices.py`、`analyze_drug_statistics_by_treatment_area.py`
5. 排名与专项分析  
   - 典型脚本：`analyze_drug_sales_ranking.py`、`innovative_drug_sales_analysis.py`、`medical_insurance_sales_ranking_analysis.py`
6. 三年对比与综合输出  
   - 典型脚本：`analyze_2021_2022_2023_corrected.py`、`big_data_pharmaceutical_analyzer.py`

## 核心指标（来自报告与脚本）
- 配备率（毛配备率、谈判药配备率）
- 使用金额（总金额、医保/非医保、分级医院）
- 使用量（总量、医保/非医保、分级医院）
- 平均进院率（总创新药、医保创新药、谈判创新药、非医保创新药）
- 平均单价（按医院级别、医保属性）
- 治疗领域分布（药品数量、金额、用量）
- 前十/后十药品排名（金额口径）

## 可复现执行建议
可先运行：
- `python src/run_pipeline.py --list` 查看脚本与顺序建议；
- 再按数据可用性执行单脚本。

## 说明
当前仓库未包含原始业务数据，因此复现依赖本地放置的同名输入文件。涉及路径固定的脚本，应先将文件名与目录调整为实际环境一致。
