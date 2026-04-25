#!/usr/bin/env python3
"""
Searches symbol_map.json for a class or function name.
Usage: python query_index.py <repo_path> --symbol <name>
"""
import json, sys, argparse
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path")
    parser.add_argument("--symbol", required=True)
    args = parser.parse_args()

    sm_path = Path(args.repo_path) / ".analysis" / "symbol_map.json"
    if not sm_path.exists():
        print("ERROR: symbol_map.json not found. Run build_index.py first.")
        sys.exit(1)

    symbol_map = json.loads(sm_path.read_text())
    results = []
    for filepath, data in symbol_map.items():
        if args.symbol in data.get("classes", []) + data.get("functions", []):
            results.append(filepath)

    if results:
        print(f"Symbol '{args.symbol}' found in:")
        for r in results: print(f"  {r}")
    else:
        print(f"Symbol '{args.symbol}' not found in any indexed file.")
