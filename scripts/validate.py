"""Checks content.json before it reaches the app. Run: python scripts/validate.py"""
import json, sys

errors = []
def err(msg): errors.append(msg)

try:
    c = json.load(open("content.json", encoding="utf-8"))
except Exception as e:
    print(f"✗ content.json is not valid JSON: {e}")
    print("  Usually a missing comma, an extra comma before ] or }, or a missing quote.")
    sys.exit(1)

if not isinstance(c.get("version"), int):
    err("'version' must be a whole number, e.g. 2")

def each(key, check, need):
    items = c.get(key)
    if items is None: return
    if not isinstance(items, list): err(f"{key} must be a list [ ... ]"); return
    for i, x in enumerate(items):
        miss = [f for f in need if not check(x, f)]
        if miss: err(f"{key} item {i+1}: missing {', '.join(miss)}")

has = lambda x, f: isinstance(x, dict) and x.get(f) not in (None, "")
each("WORDS", has, ["sa", "en", "kn"])
each("SHLOKAS", has, ["sa", "en", "kn", "src"])
each("DHATUS", has, ["r", "en", "kn", "lat", "lrt", "kta", "ktva", "tum", "t"])
each("SENTENCES", has, ["en", "kn", "ans", "extra"])
each("DIALOGUES", has, ["t", "en", "kn", "l"])
classic = [x for x in c.get("STORIES", []) if x.get("kind") != "notes"]
notes_st = [x for x in c.get("STORIES", []) if x.get("kind") == "notes"]
for i, x in enumerate(classic):
    miss = [f for f in ["t", "en", "kn", "src", "lvl", "s", "moral", "g"] if not has(x, f)]
    if miss: err(f"STORIES (retold) item {i+1}: missing {', '.join(miss)}")
for x in notes_st:
    miss = [f for f in ["t", "en", "src", "lvl", "text", "trans"] if not has(x, f)]
    if miss: err(f"STORIES (class notes) {x.get('n','?')}: missing {', '.join(miss)}")

for i, d in enumerate(c.get("DIALOGUES", [])):
    for j, l in enumerate(d.get("l", [])):
        if not (isinstance(l, list) and len(l) == 4 and l[0] in ("A", "B")):
            err(f"DIALOGUES item {i+1}, line {j+1}: must be [\"A\" or \"B\", sanskrit, english, kannada]")
for i, s in enumerate(classic):
    for j, l in enumerate(s.get("s", [])):
        if not (isinstance(l, list) and len(l) == 3):
            err(f"STORIES item {i+1}, sentence {j+1}: must be [sanskrit, english, kannada]")
    if not (isinstance(s.get("moral"), list) and len(s["moral"]) == 3):
        err(f"STORIES item {i+1}: moral must be [sanskrit, english, kannada]")
for i, d in enumerate(c.get("DHATUS", [])):
    if d.get("t") not in ("p", "a", "x"): err(f"DHATUS item {i+1}: t must be p, a or x")
    if d.get("t") == "x" and len(d.get("full", [])) != 9: err(f"DHATUS item {i+1}: type x needs a 'full' list of 9 forms")
for i, s in enumerate(c.get("SENTENCES", [])):
    if any(a in s.get("extra", []) for a in s.get("ans", [])):
        err(f"SENTENCES item {i+1}: a word is in both 'ans' and 'extra'")

text = json.dumps(c, ensure_ascii=False)
if any(ch in text for ch in "<>`"):
    err("Remove the characters < > ` — the app strips them anyway")

if errors:
    print(f"✗ {len(errors)} problem(s) found:")
    for e in errors: print("  -", e)
    sys.exit(1)
print(f"✓ content.json v{c['version']} looks good: "
      f"{len(c.get('STORIES', []))} stories, {len(c.get('WORDS', []))} words, "
      f"{len(c.get('SHLOKAS', []))} ślokas, {len(c.get('DIALOGUES', []))} dialogues, "
      f"{len(c.get('DHATUS', []))} roots, {len(c.get('SENTENCES', []))} sentences")
