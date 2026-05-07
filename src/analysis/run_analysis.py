from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from script_registry import list_scripts_by_category  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="运行 analysis 类脚本")
    parser.add_argument("--script", default="", help="指定脚本名")
    args = parser.parse_args()

    records = list_scripts_by_category("analysis")
    if not args.script:
        for item in records:
            print(item["script"])
        return 0

    script_path = PROJECT_ROOT / args.script
    if not script_path.exists():
        print(f"脚本不存在: {script_path}")
        return 1

    return subprocess.run([sys.executable, str(script_path)], cwd=str(PROJECT_ROOT), check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
