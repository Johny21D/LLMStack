#!/usr/bin/env python3
"""
Builds .analysis/manifest.json and .analysis/symbol_map.json
Usage: python build_index.py <repo_path>
"""
import os, json, ast, sys
from pathlib import Path
from datetime import datetime

SKIP = {'.git','node_modules','__pycache__','.venv','dist','build','.analysis'}
EXTS = {'.py','.js','.ts','.sh','.md','.yaml','.yml','.json','.toml'}

def build_manifest(root):
    tree, lang_lines = [], {}
    total_files = total_lines = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        rel = str(Path(dirpath).relative_to(root))
        if rel == '.': continue
        dir_files = dir_lines = 0
        for f in filenames:
            ext = Path(f).suffix.lower()
            if ext not in EXTS: continue
            try: lines = (Path(dirpath)/f).read_text(errors='ignore').count('\n')
            except: lines = 0
            dir_files += 1; dir_lines += lines
            lang_lines[ext] = lang_lines.get(ext, 0) + lines
        if dir_files:
            tree.append({"path": rel, "files": dir_files, "lines": dir_lines})
            total_files += dir_files; total_lines += dir_lines
    entry_points = []
    for name in ['main.py','app.py','manage.py','index.js','server.js','Makefile']:
        if (root/name).exists(): entry_points.append(name)
    return {"generated_at": datetime.utcnow().isoformat(), "repo_root": str(root),
            "total_files": total_files, "total_lines": total_lines,
            "language_breakdown": lang_lines, "tree": tree, "entry_points": entry_points}

def extract_symbols(root):
    sm = {}
    for fpath in root.rglob("*.py"):
        if any(p in fpath.parts for p in SKIP): continue
        try:
            tree = ast.parse(fpath.read_text(errors='ignore'))
            sm[str(fpath.relative_to(root))] = {
                "classes": [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)],
                "functions": [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            }
        except: pass
    return sm

if __name__ == "__main__":
    root = Path(sys.argv[1]).resolve()
    out = root / ".analysis"; out.mkdir(exist_ok=True)
    print("Building manifest...")
    (out/"manifest.json").write_text(json.dumps(build_manifest(root), indent=2))
    print("Extracting symbols...")
    (out/"symbol_map.json").write_text(json.dumps(extract_symbols(root), indent=2))
    print("Done. Output in .analysis/")
