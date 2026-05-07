#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract innovative-drug records by list and export 12 files."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd


CSV_ENCODINGS: Tuple[str, ...] = ("utf-8-sig", "utf-8", "gb18030", "gbk")
YEARS: Tuple[str, ...] = ("2021", "2022", "2023")
LEVELS: Tuple[str, ...] = ("\u4e00\u7ea7", "\u4e8c\u7ea7", "\u4e09\u7ea7")

TEXT_INNOVATIVE_LIST = "\u521b\u65b0\u836f\u540d\u5355"
TEXT_YEAR_SUFFIX = "\u5e74"
TEXT_FOLDER_2021 = "2021\u5e74"
TEXT_FOLDER_2022 = "2022\u5e74"
TEXT_FOLDER_2023 = "2023\u5e74"
TEXT_OUTPUT_DIR = "\u5339\u914d\u7ed3\u679c_\u540d\u5355\u63d0\u53d6"

COL_DRUG_NAME_CANDIDATES: Tuple[str, ...] = (
    "\u836f\u54c1\u540d\u79f0",
    "\u4ea7\u54c1\u901a\u7528\u540d",
    "\u836f\u54c1\u901a\u7528\u540d",
    "\u901a\u7528\u540d",
)
COL_HOSPITAL_CANDIDATES: Tuple[str, ...] = (
    "\u673a\u6784\u540d\u79f0",
    "\u533b\u7597\u673a\u6784\u540d\u79f0",
    "\u533b\u9662\u540d\u79f0",
)
COL_LEVEL_CANDIDATES: Tuple[str, ...] = ("\u673a\u6784\u7b49\u7ea7", "\u533b\u9662\u7b49\u7ea7")
COL_AMOUNT_CANDIDATES: Tuple[str, ...] = ("\u9500\u552e\u91d1\u989d",)
COL_VOLUME_CANDIDATES: Tuple[str, ...] = ("\u9500\u552e\u5236\u5242\u91cf", "\u9500\u552e\u5305\u88c5\u91cf")

OUT_COL_MATCHED = "\u5339\u914d\u7684\u521b\u65b0\u836f\u540d\u79f0"
OUT_COL_YEAR = "\u5e74\u4efd"
OUT_COL_LEVEL = "\u533b\u9662\u7ea7\u522b"
OUT_COL_SRC_LEVEL = "\u6587\u4ef6\u63a8\u65ad\u7ea7\u522b"
OUT_COL_SRC_FILE = "\u6765\u6e90\u6587\u4ef6"
OUT_COL_HOSPITAL = "\u533b\u9662\u540d\u79f0"
OUT_COL_DRUG_RAW = "\u836f\u54c1\u540d\u79f0_\u539f\u5b57\u6bb5"
OUT_COL_AMOUNT = "\u9500\u552e\u91d1\u989d_\u63d0\u53d6"
OUT_COL_VOLUME = "\u9500\u552e\u91cf_\u63d0\u53d6"
LOG_COL_MATCH_COUNT = "\u5339\u914d\u8bb0\u5f55\u6570"

DOSAGE_SUFFIXES: Tuple[str, ...] = (
    "\u6ce8\u5c04\u6db2",
    "\u53e3\u670d\u6db2",
    "\u6ef4\u773c\u6db2",
    "\u55b7\u96fe\u5242",
    "\u5438\u5165\u5242",
    "\u7f13\u91ca\u80f6\u56ca",
    "\u63a7\u91ca\u80f6\u56ca",
    "\u80a0\u6eb6\u80f6\u56ca",
    "\u7f13\u91ca\u7247",
    "\u63a7\u91ca\u7247",
    "\u80a0\u6eb6\u7247",
    "\u5206\u6563\u7247",
    "\u5480\u56bc\u7247",
    "\u6ce8\u5c04\u7528",
    "\u8f6f\u818f",
    "\u4e73\u818f",
    "\u51dd\u80f6",
    "\u6df7\u60ac\u6db2",
    "\u6eb6\u6db2",
    "\u80f6\u56ca",
    "\u9897\u7c92",
    "\u7cd6\u6d46",
    "\u6ef4\u4e38",
    "\u8d34\u5242",
    "\u8d34\u7247",
    "\u6805\u5242",
    "\u6ce8\u5c04",
    "\u7247",
    "\u9488",
    "\u4e38",
    "\u6563",
)
SALT_PREFIXES: Tuple[str, ...] = (
    "\u7532\u82ef\u78fa\u9178",
    "\u76d0\u9178",
    "\u786b\u9178",
    "\u78f7\u9178",
    "\u67b8\u6a7c\u9178",
    "\u9a6c\u6765\u9178",
    "\u5bcc\u9a6c\u9178",
    "\u7425\u73c0\u9178",
    "\u9152\u77f3\u9178",
    "\u4e73\u9178",
    "\u918b\u9178",
    "\u91cd\u9152\u77f3\u9178",
    "\u53cc\u9a6c\u6765\u9178",
    "\u6c22\u6eb4\u9178",
)


@dataclass(frozen=True)
class SourceFile:
    year: str
    level: str
    path: Path


def pick_first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> str:
    for name in candidates:
        if name in df.columns:
            return name
    return ""


def read_csv_with_fallback(path: Path, max_rows: int = 0) -> pd.DataFrame:
    last_error: Optional[Exception] = None
    for encoding in CSV_ENCODINGS:
        try:
            return pd.read_csv(path, encoding=encoding, low_memory=False, nrows=max_rows or None)
        except Exception as error:  # noqa: BLE001
            last_error = error
    raise ValueError(f"CSV read failed: {path}") from last_error


def read_table(path: Path, max_rows: int = 0) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, nrows=max_rows or None)
    if suffix == ".csv":
        return read_csv_with_fallback(path, max_rows=max_rows)
    raise ValueError(f"Unsupported file type: {path}")


def normalize_drug_name(value: object) -> str:
    if pd.isna(value):
        return ""
    name = str(value).strip().lower()
    if not name:
        return ""
    name = re.sub(r"\(.*?\)|\uFF08.*?\uFF09|\[.*?]|\u3010.*?\u3011", "", name)
    name = re.sub(r"[\s\-_/\u00B7,\uFF0C\u3002\uFF1B;:\uFF1A]+", "", name)
    for prefix in SALT_PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix) :]
            break
    for suffix in DOSAGE_SUFFIXES:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name.strip()


def infer_level_from_filename(file_name: str) -> str:
    lowered = file_name.lower()
    if "\u57fa\u5c42" in file_name or lowered.endswith("_1.csv") or lowered.endswith("1.csv"):
        return "\u4e00\u7ea7"
    if "\u4e00\u7ea7" in file_name:
        return "\u4e00\u7ea7"
    if lowered.endswith("_2.csv") or lowered.endswith("2.csv") or "\u4e8c\u7ea7" in file_name:
        return "\u4e8c\u7ea7"
    if lowered.endswith("_3.csv") or lowered.endswith("3.csv") or "\u4e09\u7ea7" in file_name:
        return "\u4e09\u7ea7"
    return "\u672a\u77e5"


def choose_list_file(base_dir: Path, specified_name: str) -> Path:
    if specified_name:
        selected = base_dir / specified_name
        if not selected.exists():
            raise FileNotFoundError(f"List file not found: {selected}")
        return selected
    candidates = sorted(
        [
            path
            for path in base_dir.glob("*.xlsx")
            if path.is_file() and TEXT_INNOVATIVE_LIST in path.name
        ],
        key=lambda path: path.name,
    )
    if not candidates:
        raise FileNotFoundError("No innovative list xlsx found")
    priority_suffix = (
        "\u53bb\u91cd\u53bb\u4e2d\u836f\u7248_\u6700\u7ec8\u5b8c\u6574\u7248_"
        "\u542b\u56fd\u4ea7\u8fdb\u53e3\u4fe1\u606f_\u6807\u8bb0\u6709\u6570\u636e_"
        "\u542b\u8c08\u5224\u836f_\u6b63\u786e\u6a21\u7cca\u5339\u914d.xlsx"
    )
    for path in candidates:
        if path.name.endswith(priority_suffix):
            return path
    return candidates[-1]


def load_innovative_names(list_path: Path) -> Tuple[str, List[str], Dict[str, str]]:
    df = pd.read_excel(list_path)
    name_col = pick_first_existing_column(df, COL_DRUG_NAME_CANDIDATES)
    if not name_col:
        raise ValueError(f"No drug name column in list: {list_path}")

    raw_names = [str(v).strip() for v in df[name_col].dropna().tolist()]
    normalized_to_raw: Dict[str, str] = {}
    for raw_name in raw_names:
        key = normalize_drug_name(raw_name)
        if key and key not in normalized_to_raw:
            normalized_to_raw[key] = raw_name
    return name_col, raw_names, normalized_to_raw


def build_source_files(base_dir: Path) -> List[SourceFile]:
    files = [
        SourceFile("2021", "\u4e00\u7ea7", base_dir / TEXT_FOLDER_2021 / "\u4f7f\u7528\u6570\u636e\uff08\u57fa\u5c42\uff09.xlsx"),
        SourceFile("2021", "\u4e8c\u7ea7", base_dir / TEXT_FOLDER_2021 / "\u4e8c\u7ea7\u836f\u54c1\u4f7f\u7528\u6570\u636e.xlsx"),
        SourceFile("2021", "\u4e09\u7ea7", base_dir / TEXT_FOLDER_2021 / "\u4e09\u7ea7\u836f\u54c1\u4f7f\u7528\u6570\u636e.xlsx"),
        SourceFile("2022", "\u4e00\u7ea7", base_dir / TEXT_FOLDER_2022 / "RPT_DRUG_USE_2022_BIG-\u5317\u4eac\u5e02-\u57fa\u5c42_\u7f16\u7801\u4fee\u590d.csv"),
        SourceFile("2022", "\u4e8c\u7ea7", base_dir / TEXT_FOLDER_2022 / "RPT_DRUG_USE_2022_BIG-\u5317\u4eac\u5e02-\u4e8c\u7ea7.csv"),
        SourceFile("2022", "\u4e09\u7ea7", base_dir / TEXT_FOLDER_2022 / "RPT_DRUG_USE_2022_BIG-\u5317\u4eac\u5e02-\u4e09\u7ea7_\u7f16\u7801\u4fee\u590d.csv"),
        SourceFile("2023", "\u4e00\u7ea7", base_dir / TEXT_FOLDER_2023 / "RPT_DRUG_USE_2023_BIG_\u5317\u4eac_1.csv"),
        SourceFile("2023", "\u4e8c\u7ea7", base_dir / TEXT_FOLDER_2023 / "RPT_DRUG_USE_2023_BIG_\u5317\u4eac_2.csv"),
        SourceFile("2023", "\u4e09\u7ea7", base_dir / TEXT_FOLDER_2023 / "RPT_DRUG_USE_2023_BIG_\u5317\u4eac_3.csv"),
    ]
    missing = [item.path for item in files if not item.path.exists()]
    if missing:
        raise FileNotFoundError("Missing source files:\n" + "\n".join(str(path) for path in missing))
    return files


def build_match_map(unique_hospital_names: Iterable[str], list_map: Dict[str, str]) -> Dict[str, str]:
    innovation_keys = list(list_map.keys())
    matched: Dict[str, str] = {}
    for hospital_name in unique_hospital_names:
        normalized_hospital = normalize_drug_name(hospital_name)
        if not normalized_hospital:
            continue
        if normalized_hospital in list_map:
            matched[hospital_name] = list_map[normalized_hospital]
            continue
        selected = ""
        for innovation_key in innovation_keys:
            if innovation_key in normalized_hospital or normalized_hospital in innovation_key:
                selected = list_map[innovation_key]
                break
        if selected:
            matched[hospital_name] = selected
    return matched


def extract_group_data(df: pd.DataFrame, source_file: SourceFile, list_map: Dict[str, str]) -> pd.DataFrame:
    drug_col = pick_first_existing_column(df, COL_DRUG_NAME_CANDIDATES)
    if not drug_col and len(df.columns) >= 8:
        drug_col = df.columns[7]
    if not drug_col:
        raise ValueError(f"Cannot identify drug column: {source_file.path.name}")

    hospital_col = pick_first_existing_column(df, COL_HOSPITAL_CANDIDATES)
    level_col = pick_first_existing_column(df, COL_LEVEL_CANDIDATES)
    amount_col = pick_first_existing_column(df, COL_AMOUNT_CANDIDATES)
    volume_col = pick_first_existing_column(df, COL_VOLUME_CANDIDATES)

    drug_series = df[drug_col].fillna("").astype(str).str.strip()
    unique_names = [name for name in drug_series.unique().tolist() if name]
    match_map = build_match_map(unique_names, list_map)
    result = df[drug_series.isin(match_map.keys())].copy()
    if result.empty:
        return result

    result[OUT_COL_MATCHED] = result[drug_col].astype(str).map(match_map)
    result[OUT_COL_YEAR] = source_file.year
    if level_col:
        result[OUT_COL_LEVEL] = result[level_col].fillna("").astype(str).str.strip().replace("", source_file.level)
    else:
        result[OUT_COL_LEVEL] = source_file.level
    result[OUT_COL_SRC_LEVEL] = infer_level_from_filename(source_file.path.name)
    result[OUT_COL_SRC_FILE] = source_file.path.name
    result[OUT_COL_HOSPITAL] = result[hospital_col].fillna("").astype(str).str.strip() if hospital_col else ""
    result[OUT_COL_DRUG_RAW] = result[drug_col].fillna("").astype(str).str.strip()
    result[OUT_COL_AMOUNT] = pd.to_numeric(result[amount_col], errors="coerce") if amount_col else pd.NA
    result[OUT_COL_VOLUME] = pd.to_numeric(result[volume_col], errors="coerce") if volume_col else pd.NA
    return result


def export_files(
    output_dir: Path,
    grouped_data: Dict[Tuple[str, str], pd.DataFrame],
    list_file_name: str,
    list_size: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    export_log_rows: List[Dict[str, object]] = []

    for year in YEARS:
        summary_rows: List[Dict[str, object]] = []
        for level in LEVELS:
            group = grouped_data.get((year, level), pd.DataFrame())
            detail_name = f"\u521b\u65b0\u836f\u5339\u914d\u7ed3\u679c_{year}{TEXT_YEAR_SUFFIX}_{level}\u533b\u9662.xlsx"
            detail_path = output_dir / detail_name
            group.to_excel(detail_path, index=False)

            summary_rows.append(
                {
                    OUT_COL_YEAR: year,
                    OUT_COL_LEVEL: level,
                    "\u5339\u914d\u8bb0\u5f55\u6570": int(len(group)),
                    "\u5339\u914d\u836f\u54c1\u6570": int(group[OUT_COL_MATCHED].nunique()) if not group.empty else 0,
                    "\u9500\u552e\u91d1\u989d\u5408\u8ba1": float(pd.to_numeric(group[OUT_COL_AMOUNT], errors="coerce").sum()) if not group.empty else 0.0,
                    "\u9500\u552e\u91cf\u5408\u8ba1": float(pd.to_numeric(group[OUT_COL_VOLUME], errors="coerce").sum()) if not group.empty else 0.0,
                    TEXT_INNOVATIVE_LIST + "\u6587\u4ef6": list_file_name,
                    TEXT_INNOVATIVE_LIST + "\u89c4\u6a21": list_size,
                }
            )

            export_log_rows.append(
                {
                    "\u6587\u4ef6\u7c7b\u578b": "\u660e\u7ec6",
                    OUT_COL_YEAR: year,
                    OUT_COL_LEVEL: level,
                    "\u6587\u4ef6\u540d": detail_name,
                    "\u8bb0\u5f55\u6570": int(len(group)),
                }
            )

        summary_df = pd.DataFrame(summary_rows)
        summary_name = f"\u521b\u65b0\u836f\u5339\u914d\u6c47\u603b_{year}{TEXT_YEAR_SUFFIX}.xlsx"
        summary_path = output_dir / summary_name
        summary_df.to_excel(summary_path, index=False)

        export_log_rows.append(
            {
                "\u6587\u4ef6\u7c7b\u578b": "\u5e74\u5ea6\u6c47\u603b",
                OUT_COL_YEAR: year,
                OUT_COL_LEVEL: "\u6c47\u603b",
                "\u6587\u4ef6\u540d": summary_name,
                "\u8bb0\u5f55\u6570": int(len(summary_df)),
            }
        )

    pd.DataFrame(export_log_rows).to_csv(
        output_dir / "\u5bfc\u51fa\u6587\u4ef6\u6e05\u5355.csv",
        index=False,
        encoding="utf-8-sig",
    )


def run_extraction(base_dir: Path, list_file: str, output_dir_name: str, max_rows: int) -> None:
    list_path = choose_list_file(base_dir, list_file)
    list_col, raw_names, list_map = load_innovative_names(list_path)
    source_files = build_source_files(base_dir)

    grouped_data: Dict[Tuple[str, str], pd.DataFrame] = {}
    logs: List[Dict[str, object]] = []

    for source_file in source_files:
        try:
            source_df = read_table(source_file.path, max_rows=max_rows)
            matched_df = extract_group_data(source_df, source_file, list_map)
            grouped_data[(source_file.year, source_file.level)] = matched_df
            logs.append(
                {
                    OUT_COL_YEAR: source_file.year,
                    OUT_COL_LEVEL: source_file.level,
                    OUT_COL_SRC_FILE: source_file.path.name,
                    "\u539f\u59cb\u8bb0\u5f55\u6570": int(len(source_df)),
                    LOG_COL_MATCH_COUNT: int(len(matched_df)),
                    "\u72b6\u6001": "\u6210\u529f",
                    "\u9519\u8bef\u4fe1\u606f": "",
                }
            )
        except Exception as error:  # noqa: BLE001
            grouped_data[(source_file.year, source_file.level)] = pd.DataFrame()
            logs.append(
                {
                    OUT_COL_YEAR: source_file.year,
                    OUT_COL_LEVEL: source_file.level,
                    OUT_COL_SRC_FILE: source_file.path.name,
                    "\u539f\u59cb\u8bb0\u5f55\u6570": 0,
                    LOG_COL_MATCH_COUNT: 0,
                    "\u72b6\u6001": "\u5931\u8d25",
                    "\u9519\u8bef\u4fe1\u606f": str(error),
                }
            )

    output_dir = base_dir / output_dir_name
    export_files(output_dir, grouped_data, list_path.name, len(raw_names))
    pd.DataFrame(logs).to_csv(output_dir / "\u5904\u7406\u65e5\u5fd7.csv", index=False, encoding="utf-8-sig")

    summary_text = "\u3001".join(
        f"{row[OUT_COL_YEAR]}{row[OUT_COL_LEVEL]}:{row[LOG_COL_MATCH_COUNT]}"
        for row in logs
    )
    print(f"{TEXT_INNOVATIVE_LIST}\u5217: {list_col}")
    print(f"{TEXT_INNOVATIVE_LIST}\u6587\u4ef6: {list_path.name}")
    print(f"\u8f93\u51fa\u76ee\u5f55: {output_dir}")
    print(f"\u5404\u7ec4\u5339\u914d\u8bb0\u5f55\u6570: {summary_text}")
    print("\u5bfc\u51fa\u5b8c\u6210: 9\u4e2a\u660e\u7ec6 + 3\u4e2a\u6c47\u603b (12\u4e2a\u4e3b\u6587\u4ef6)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract innovative drug records by list")
    parser.add_argument("--base-dir", default=".", help="Workspace directory")
    parser.add_argument("--list-file", default="", help="List file name")
    parser.add_argument("--output-dir", default=TEXT_OUTPUT_DIR, help="Output directory name")
    parser.add_argument("--max-rows", type=int, default=0, help="Debug row limit per source file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_extraction(
        base_dir=Path(args.base_dir).resolve(),
        list_file=args.list_file,
        output_dir_name=args.output_dir,
        max_rows=max(0, args.max_rows),
    )


if __name__ == "__main__":
    main()
