#!/usr/bin/env python3
"""stdin の JSON 配列（no をキーにした部分更新）を boats.json にマージする。

例: echo '[{"no":1,"status":"済","catches":[...]}]' | python3 scripts/apply_patch.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOATS_JSON = os.path.join(ROOT, "data", "boats.json")

with open(BOATS_JSON, encoding="utf-8") as f:
    boats = json.load(f)
by_no = {b["no"]: b for b in boats}

patches = json.load(sys.stdin)
for p in patches:
    b = by_no.get(p["no"])
    if b is None:
        print(f"WARN: no={p['no']} not found", file=sys.stderr)
        continue
    b.update(p)

with open(BOATS_JSON, "w", encoding="utf-8") as f:
    json.dump(boats, f, ensure_ascii=False, indent=1)

st = {}
for b in boats:
    st[b["status"]] = st.get(b["status"], 0) + 1
print(f"patched {len(patches)} boats; status counts: {st}")
