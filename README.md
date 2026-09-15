# 北京市医疗机构创新药品配备及使用模式研究

## 项目简介
本项目用于支撑《北京市医疗机构创新药品配备及使用模式研究》的数据处理与分析工作。仓库保留了原始 Python 脚本，并补充了文档化目录、统一入口与复现说明，便于研究归档、GitHub 展示和后续维护。

最终研究报告：[北京市医疗机构创新药品配备及使用模式研究.pdf](./北京市医疗机构创新药品配备及使用模式研究.pdf)。

## 研究背景
根据最终报告前言，项目围绕北京市创新药临床可及性与使用模式开展研究，背景包括国家与北京市 2025 年创新药支持政策落地需求。研究基于 2021-2023 年北京市公立医院药品使用数据，并结合企业调研、医院调研与专家咨询。

## 项目文件结构
```text
.
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ LICENSE_NOTICE.md
├─ 北京市医疗机构创新药品配备及使用模式研究.pdf
├─ docs/
│  ├─ project_background.md
│  ├─ methodology.md
│  └─ data_dictionary.md
├─ src/
│  ├─ run_pipeline.py
│  ├─ script_registry.py
│  ├─ data_processing/
│  │  └─ README.md
│  ├─ analysis/
│  │  └─ README.md
│  └─ reporting/
│     └─ README.md
├─ data/
│  └─ README.md
├─ outputs/
│  └─ README.md
├─ tests/
│  ├─ README.md
│  └─ test_script_registry.py
└─ *.py（原始研究脚本，已保留）
```

## 核心分析流程
1. 准备创新药名单、医院分级数据、医保标识数据和三年医院药品使用数据（2021-2023）。
2. 进行医院分类、药品名称标准化与创新药/谈判药匹配。
3. 分别计算配备率、使用金额、使用量、平均进院率、单价、治疗领域分布、前后十药品排名等指标。
4. 产出 Excel/JSON/TXT 分析结果，并用于最终报告撰写。

## 环境依赖
- Python 3.9+
- 依赖见 `requirements.txt`

## 安装方式
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 使用方法
### 1) 查看脚本清单和执行顺序建议
```bash
python src/run_pipeline.py --list
```

### 2) 按脚本名称执行单个步骤
```bash
python src/run_pipeline.py --script comprehensive_hospital_drug_analysis_system.py
```

### 3) 按类别查看脚本
```bash
python src/run_pipeline.py --category analysis
```

## 主要脚本说明
主要脚本按功能已在 `src/script_registry.py` 分类为：
- `data_processing`：编码修复、医院分类、创新药名单清理、中药匹配等前处理。
- `analysis`：进院率、金额/用量、治疗领域、排名、三年对比、谈判药分析等核心计算。
- `reporting`：结果核验与报告查看辅助脚本。
- `planning`：分析计划与流程草案脚本。

完整脚本说明见：
- `src/data_processing/README.md`
- `src/analysis/README.md`
- `src/reporting/README.md`

## 输入数据说明
当前仓库未默认包含原始业务数据文件（CSV/XLSX）。代码中可验证的输入文件命名模式包括但不限于：
- `2021年/`, `2022年/`, `2023年/` 下的医院药品使用文件
- 创新药名单、谈判药名单、医院分类名单等 Excel/CSV 文件

请将原始数据放入 `data/raw/`，并按脚本中约定命名或在脚本参数中改为实际路径。

## 输出结果说明
脚本主要输出：
- 统计分析 Excel（前后十、分类汇总、年度明细）
- 数据校验报告 Excel
- JSON 汇总结果
- 文本报告

建议统一输出到 `outputs/`（原脚本默认可能输出到项目根目录，详见 `src/script_registry.py`）。

## 最终报告链接
- [北京市医疗机构创新药品配备及使用模式研究.pdf](./北京市医疗机构创新药品配备及使用模式研究.pdf)

## 注意事项
- 多数原始脚本存在固定文件名假设，运行前需确保输入文件名与脚本一致。
- 个别脚本包含绝对路径示例（如 `c:\...`），若在本仓库复现建议改为相对路径后再运行。
- 本次整理默认保留原始逻辑，不对算法结果做改写。

## 数据合规与隐私说明
- 本仓库默认不上传原始敏感数据。
- 涉及医疗机构、药品采购/销售明细的原始数据建议仅在受控环境处理。
- 上传前请检查并移除任何个人信息、密钥、凭据和受限业务数据。

## 维护说明
- 新增脚本后请同步更新 `src/script_registry.py` 与对应分类 README。
- 若调整数据路径，请在脚本注释或文档中记录变更原因与影响范围。
- 建议在 `tests/` 补充最小化自动化检查，确保整理后的流程可持续维护。
