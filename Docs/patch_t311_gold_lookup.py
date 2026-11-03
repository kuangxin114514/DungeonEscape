# -*- coding: utf-8 -*-
"""Patch ensure_gold_hud text lookup to include TextBlock_0 + first TextBlock fallback."""
from __future__ import print_function
import io
import os

PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
with io.open(PATH, "r", encoding="utf-8") as f:
    src = f.read()

OLD = '''        # Prefer Txt_Gold; else Txt_HP (health WBP fallback)
        txt = None
        for nm in ("Txt_Gold", "Txt_HP"):
            try:
                txt = widget.get_widget_from_name(nm)
            except Exception:
                txt = None
            if txt is None:
                try:
                    txt = _find_named_widget(widget, nm)
                except Exception:
                    txt = None
            if txt is not None:
                break
        _GOLD_TXT[0] = txt
'''

NEW = '''        # Prefer Txt_Gold; else TextBlock_0 (WBP_PlayerGold from Shop2); else Txt_HP
        txt = None
        for nm in ("Txt_Gold", "TextBlock_0", "Txt_HP"):
            try:
                txt = widget.get_widget_from_name(nm)
            except Exception:
                txt = None
            if txt is None:
                try:
                    txt = _find_named_widget(widget, nm)
                except Exception:
                    txt = None
            if txt is not None:
                break
        if txt is None:
            # Last resort: first TextBlock under this UserWidget
            try:
                stack = []
                try:
                    wt = widget.get_editor_property("widget_tree")
                    if wt is not None:
                        rw = wt.get_editor_property("root_widget")
                        if rw is not None:
                            stack.append(rw)
                except Exception:
                    pass
                try:
                    n = int(widget.get_children_count())
                    for i in range(n):
                        ch = widget.get_child_at(i)
                        if ch is not None:
                            stack.append(ch)
                except Exception:
                    pass
                seen = set()
                while stack and txt is None:
                    cur = stack.pop()
                    try:
                        cid = int(cur.get_unique_id())
                    except Exception:
                        cid = id(cur)
                    if cid in seen:
                        continue
                    seen.add(cid)
                    try:
                        if cur.get_class() and cur.get_class().get_name() == "TextBlock":
                            txt = cur
                            break
                    except Exception:
                        pass
                    try:
                        kids = cur.get_all_children()
                        if kids:
                            for k in kids:
                                if k is not None:
                                    stack.append(k)
                    except Exception:
                        try:
                            cn = int(cur.get_children_count())
                            for i in range(cn):
                                k = cur.get_child_at(i)
                                if k is not None:
                                    stack.append(k)
                        except Exception:
                            pass
            except Exception as e:
                _log("gold txt scan " + str(e))
        _GOLD_TXT[0] = txt
'''

if OLD not in src:
    raise SystemExit("OLD block not found")
src = src.replace(OLD, NEW, 1)

# Ensure tag string present
if "T311_GOLD_HUD" not in src:
    raise SystemExit("missing T311 tag")

with io.open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(src)
print("patched ok")