from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from script_registry import list_categories, list_scripts, list_scripts_by_category


def print_scripts(records: list[dict[str, str]]) -> None:
    if not records:
        print("未找到匹配脚本。")
        return

    for item in records:
        print(
            f"[{item['order']}] {item['script']} | 类别: {item['category']} | "
            f"用途: {item['purpose']}"
        )


def run_single_script(project_root: Path, script_name: str) -> int:
    script_path = project_root / script_name
    if not script_path.exists():
        print(f"脚本不存在: {script_path}")
        return 1

    command = [sys.executable, str(script_path)]
    print(f"执行脚本: {' '.join(command)}")
    result = subprocess.run(command, cwd=str(project_root), check=False)
    return result.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="项目脚本统一入口")
    parser.add_argument("--list", action="store_true", help="列出全部脚本")
    parser.add_argument("--category", default="", help="按类别筛选脚本")
    parser.add_argument("--script", default="", help="执行指定脚本")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent

    if args.list:
        print("全部脚本：")
        print_scripts(list_scripts())
        return 0

    if args.category:
        available_categories = list_categories()
        if args.category.strip().lower() not in available_categories:
            print(f"无效类别: {args.category}")
            print(f"可用类别: {', '.join(available_categories)}")
            return 1
        print(f"类别 {args.category} 下的脚本：")
        print_scripts(list_scripts_by_category(args.category))
        return 0

    if args.script:
        return run_single_script(project_root, args.script)

    print("请至少提供一个参数：--list / --category / --script")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
