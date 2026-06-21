# -*- coding: utf-8 -*-
"""
Genderbend dialogue diff tool (lives inside the mod folder next to xnb_unpacker.py).

Tracks the ORIGINAL game text of every line a Content Patcher pack patches, so after
a Stardew Valley update you can see which patched lines changed (and need re-checking).

Usage (run from the mod folder):
    python dialogue_diff.py snapshot --version 1.6.15
    python dialogue_diff.py check
The pack is auto-detected (the script sits inside it). Pass --mod <folder> to override,
or --content if the game Content folder differs from the default.
"""
import os, sys, json, glob, argparse, datetime, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from xnb_unpacker import parse_dict

DEFAULT_CONTENT = r"E:\SteamLibrary\steamapps\common\Stardew Valley\Content"

def find_packs():
    out = []
    for d in sorted(glob.glob(os.path.join(glob.escape(HERE), "*"))):
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "manifest.json")) \
           and os.path.exists(os.path.join(d, "content.json")):
            out.append(d)
    return out

def resolve_mod(arg):
    if arg:
        return os.path.abspath(arg)
    if os.path.exists(os.path.join(HERE, "manifest.json")) \
       and os.path.exists(os.path.join(HERE, "content.json")):
        return HERE
    packs = find_packs()
    if len(packs) == 1:
        return packs[0]
    if not packs:
        sys.exit("no Content Patcher pack found here; pass --mod <folder>")
    sys.exit("multiple packs found; pass --mod <folder>: " + ", ".join(os.path.basename(p) for p in packs))

_cache = {}
def _decode(content, target, locale):
    k = (content, target, locale)
    if k not in _cache:
        path = os.path.join(content, *target.split("/")) + ("" if locale == "" else "." + locale) + ".xnb"
        _cache[k] = parse_dict(path)[0] if os.path.exists(path) else None
    return _cache[k]

def patched_entries(mod):
    for pf in sorted(glob.glob(os.path.join(glob.escape(mod), "patches", "**", "*.json"), recursive=True)):
        for ch in json.load(open(pf, encoding="utf-8")).get("Changes", []):
            if "Entries" not in ch:
                continue
            t = ch["Target"]; l = ch.get("TargetLocale", "")
            for key, val in ch["Entries"].items():
                yield t, l, key, val

def _eid(t, l, k): return f"{t}|{l}|{k}"
def baseline_path(mod): return os.path.join(mod, "baseline", "originals.json")

def cmd_snapshot(args):
    mod = resolve_mod(args.mod); base = {}; miss = 0
    for t, l, k, _ in patched_entries(mod):
        o = _decode(args.content, t, l)
        if o is None:
            print(f"!! asset not found: {t} [{l}] (check --content)"); miss += 1; continue
        base[_eid(t, l, k)] = o.get(k)
    bp = baseline_path(mod); os.makedirs(os.path.dirname(bp), exist_ok=True)
    json.dump({"gameVersion": args.version,
               "capturedAt": datetime.datetime.now().isoformat(timespec="seconds"),
               "mod": os.path.basename(mod), "entries": base},
              open(bp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"baseline written: {bp}\n  {len(base)} entries | gameVersion={args.version} | missing assets={miss}")

def cmd_check(args):
    mod = resolve_mod(args.mod); bp = baseline_path(mod)
    if not os.path.exists(bp):
        sys.exit(f"no baseline for {os.path.basename(mod)}. run: python dialogue_diff.py snapshot --version <ver>")
    snap = json.load(open(bp, encoding="utf-8"))
    patched = {_eid(t, l, k): v for t, l, k, v in patched_entries(mod)}
    changed = missing = added = ok = 0
    print(f"[{os.path.basename(mod)}] baseline gameVersion={snap.get('gameVersion')} capturedAt={snap.get('capturedAt')}")
    print(f"comparing against content: {args.content}\n")
    for eid, old in snap["entries"].items():
        t, l, k = eid.split("|", 2); a = _decode(args.content, t, l); cur = None if a is None else a.get(k)
        if cur is None:
            print(f"[MISSING] {eid}\n    key no longer in game\n"); missing += 1
        elif cur != old:
            print(f"[CHANGED] {eid}")
            for line in difflib.unified_diff([(old or '') + '\n'], [cur + '\n'], "baseline", "current", lineterm=""):
                print("    " + line)
            print(f"    -> your patch outputs:\n       {patched.get(eid, '(?)')[:200]}\n"); changed += 1
        else:
            ok += 1
    for eid in patched:
        if eid not in snap["entries"]:
            print(f"[NEW PATCH] {eid} — run snapshot to record"); added += 1
    print(f"\nsummary: {ok} unchanged | {changed} CHANGED | {missing} MISSING | {added} new-patch")
    sys.exit(1 if (changed or missing) else 0)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Diff a CP pack's patched game lines against a baseline (for game updates).")
    ap.add_argument("--content", default=DEFAULT_CONTENT, help="game Content folder")
    ap.add_argument("--mod", help="pack folder (auto-detected if only one here)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot"); s.add_argument("--version", default="unknown"); s.set_defaults(func=cmd_snapshot)
    c = sub.add_parser("check"); c.set_defaults(func=cmd_check)
    args = ap.parse_args(); args.func(args)
