#!/usr/bin/env python3
"""
Reads each top-level folder and writes .analysis/folder_summaries.json
Usage: python summarize_folders.py <repo_path>
"""
import os, json, sys
from pathlib import Path

SKIP = {'.git','node_modules','__pycache__','.venv','dist','build','.analysis'}
EXTS = {'.py','.js','.ts','.md','.yaml','.toml'}

def sample_folder(folder):
    samples = []
    for fpath in sorted(folder.rglob("*")):
        if any(p in fpath.parts for p in SKIP): continue
        if fpath.suffix.lower() not in EXTS: continue
        try:
            text = fpath.read_text(errors='ignore')[:2000]
            samples.append(fpath.name)
        except: pass
        if len(samples) >= 5: break
    return samples

if __name__ == "__main__":
    root = Path(sys.argv[1]).resolve()
    out = root / ".analysis"; out.mkdir(exist_ok=True)
    summaries = {}
    for item in sorted(root.iterdir()):
        if item.is_dir() and item.name not in SKIP:
            summaries[item.name] = {
                "note": "LLM should summarize this folder from sampled content.",
                "sampled_files": sample_folder(item)
            }
    (out/"folder_summaries.json").write_text(json.dumps(summaries, indent=2))
    print(f"Wrote summaries for {len(summaries)} folders to .analysis/folder_summaries.json")
