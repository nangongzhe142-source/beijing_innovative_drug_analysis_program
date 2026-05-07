from __future__ import annotations

from typing import Dict, List


SCRIPT_REGISTRY: List[Dict[str, str]] = [
    {
        "script": "fix_csv_encoding.py",
        "category": "data_processing",
        "purpose": "检测并修复CSV编码读取问题",
        "inputs": "2022年相关CSV文件",
        "outputs": "控制台验证输出",
        "dependencies": "pandas,chardet",
        "order": "01",
    },
    {
        "script": "hospital_classifier_new.py",
        "category": "data_processing",
        "purpose": "医院名称标准化与委属/市属/其他分类",
        "inputs": "医院名称字段",
        "outputs": "医院分类映射JSON与日志",
        "dependencies": "pandas,numpy",
        "order": "02",
    },
    {
        "script": "search_drug_therapy_areas.py",
        "category": "data_processing",
        "purpose": "根据药品名称规则补充治疗领域",
        "inputs": "创新药名单Excel",
        "outputs": "含治疗领域创新药名单Excel",
        "dependencies": "pandas",
        "order": "03",
    },
    {
        "script": "add_negotiation_drug_column.py",
        "category": "data_processing",
        "purpose": "为创新药名单添加谈判药标识列",
        "inputs": "创新药名单Excel",
        "outputs": "含谈判药标识的Excel",
        "dependencies": "pandas",
        "order": "04",
    },
    {
        "script": "innovative_drug_tcm_matcher.py",
        "category": "data_processing",
        "purpose": "创新药与中药/中成药成分匹配",
        "inputs": "创新药名单+中药数据Excel",
        "outputs": "含中药成分名单、纯化学名单、文本报告",
        "dependencies": "pandas,numpy",
        "order": "05",
    },
    {
        "script": "extract_innovative_by_list.py",
        "category": "data_processing",
        "purpose": "按创新药名单从三年分级医院数据中抽取记录",
        "inputs": "三年医院数据+创新药名单",
        "outputs": "9个明细+3个汇总+日志",
        "dependencies": "pandas",
        "order": "06",
    },
    {
        "script": "verify_data_correctness.py",
        "category": "reporting",
        "purpose": "验证分类后9个医院文件完整性和一致性",
        "inputs": "年度分类文件+医院标准名单",
        "outputs": "数据正确性验证报告Excel",
        "dependencies": "pandas",
        "order": "07",
    },
    {
        "script": "comprehensive_hospital_drug_analysis_system.py",
        "category": "analysis",
        "purpose": "综合分析医院数据、创新药匹配与TOP药品",
        "inputs": "三年医院数据+医院名单+创新药名单",
        "outputs": "综合分析JSON与控制台统计",
        "dependencies": "pandas,numpy,chardet",
        "order": "08",
    },
    {
        "script": "big_data_pharmaceutical_analyzer.py",
        "category": "analysis",
        "purpose": "大样本谈判药匹配与分层汇总",
        "inputs": "谈判药名单+三年医院数据",
        "outputs": "完整分析结果Excel",
        "dependencies": "pandas,numpy",
        "order": "09",
    },
    {
        "script": "accurate_negotiated_drug_analyzer.py",
        "category": "analysis",
        "purpose": "高准确性谈判药匹配与标准表生成",
        "inputs": "谈判药名单+9个医院分类文件",
        "outputs": "4组标准表格+准确性报告",
        "dependencies": "pandas",
        "order": "10",
    },
    {
        "script": "仙尊大人_精确进院率计算系统.py",
        "category": "analysis",
        "purpose": "计算分年分级药品进院率和加权进院率",
        "inputs": "创新药医院匹配结果Excel",
        "outputs": "精确进院率分析结果Excel",
        "dependencies": "pandas,numpy",
        "order": "11",
    },
    {
        "script": "calculate_all_levels_prices.py",
        "category": "analysis",
        "purpose": "按医院级别和医保属性计算平均单价",
        "inputs": "创新药医院匹配结果Excel",
        "outputs": "单价分析结果Excel",
        "dependencies": "pandas,numpy,openpyxl",
        "order": "12",
    },
    {
        "script": "analyze_drug_statistics_by_treatment_area.py",
        "category": "analysis",
        "purpose": "按治疗领域与谈判属性统计金额与用量",
        "inputs": "创新药名单+医院匹配结果Excel",
        "outputs": "治疗领域统计结果Excel",
        "dependencies": "pandas,openpyxl",
        "order": "13",
    },
    {
        "script": "analyze_treatment_areas.py",
        "category": "analysis",
        "purpose": "分析创新药治疗领域分布",
        "inputs": "创新药名单Excel",
        "outputs": "治疗领域分布Excel",
        "dependencies": "pandas",
        "order": "14",
    },
    {
        "script": "analyze_drug_sales_ranking.py",
        "category": "analysis",
        "purpose": "分析国谈药销售金额前十与后十",
        "inputs": "国谈药统计分析结果Excel",
        "outputs": "销售金额排名Excel",
        "dependencies": "pandas,numpy,openpyxl",
        "order": "15",
    },
    {
        "script": "innovative_drug_sales_analysis.py",
        "category": "analysis",
        "purpose": "创新药三年销售金额排名与年度明细",
        "inputs": "创新药名单+三年医院数据",
        "outputs": "创新药销售分析Excel",
        "dependencies": "pandas,numpy,chardet,openpyxl",
        "order": "16",
    },
    {
        "script": "medical_insurance_sales_ranking_analysis.py",
        "category": "analysis",
        "purpose": "医保药销售金额排名与状态变化分析",
        "inputs": "三年医院数据",
        "outputs": "医保药排名分析Excel",
        "dependencies": "pandas,numpy,chardet,openpyxl",
        "order": "17",
    },
    {
        "script": "analyze_2021_2022_2023_corrected.py",
        "category": "analysis",
        "purpose": "三年各级医院品规数和品类数对比",
        "inputs": "三年分级医院数据",
        "outputs": "三年对比分析Excel",
        "dependencies": "pandas,numpy,matplotlib,openpyxl",
        "order": "18",
    },
    {
        "script": "关联规则挖掘计算程序.py",
        "category": "analysis",
        "purpose": "关联规则挖掘（支持度/置信度/提升度）",
        "inputs": "示例数据或CSV",
        "outputs": "关联规则CSV",
        "dependencies": "pandas,numpy",
        "order": "19",
    },
    {
        "script": "data_aggregator_final.py",
        "category": "analysis",
        "purpose": "跨模块聚合汇总（依赖外部模块）",
        "inputs": "预处理/分类/匹配中间数据",
        "outputs": "聚合统计输出",
        "dependencies": "pandas,numpy",
        "order": "20",
    },
    {
        "script": "negotiated_drugs_analysis_plan.py",
        "category": "planning",
        "purpose": "分析计划与结构探查脚本",
        "inputs": "谈判药与医院数据文件",
        "outputs": "实施计划文本",
        "dependencies": "pandas",
        "order": "21",
    },
    {
        "script": "view_final_report.py",
        "category": "reporting",
        "purpose": "查看最终Excel分析报告关键工作表",
        "inputs": "仙尊大人_完整医院药品分析报告_*.xlsx",
        "outputs": "控制台摘要",
        "dependencies": "pandas",
        "order": "22",
    },
]


def list_categories() -> List[str]:
    return sorted({item["category"] for item in SCRIPT_REGISTRY})


def list_scripts() -> List[Dict[str, str]]:
    return sorted(SCRIPT_REGISTRY, key=lambda item: item["order"])


def list_scripts_by_category(category: str) -> List[Dict[str, str]]:
    normalized_category = category.strip().lower()
    return [item for item in list_scripts() if item["category"] == normalized_category]

