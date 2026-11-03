# -*- coding: utf-8 -*-
from __future__ import print_function
import io

PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
with io.open(PATH, "r", encoding="utf-8") as f:
    src = f.read()

# Insert helper after _paint_shop_texts if missing
HELPER = '''
def _find_textblock_under(widget, prefer_names=("Txt_Gold", "TextBlock_0", "Txt_HP")):
    """Shop-style TextBlock bind: ObjectIterator scoped by UserWidget path. T311_GOLD_HUD."""
    if widget is None:
        return None
    try:
        base = widget.get_path_name()
    except Exception:
        return None
    if not base:
        return None
    preferred = None
    any_tb = None
    try:
        for o in unreal.ObjectIterator(unreal.TextBlock):
            try:
                pn = o.get_path_name()
            except Exception:
                continue
            if base not in pn:
                continue
            try:
                name = o.get_name()
            except Exception:
                name = ""
            if any_tb is None:
                any_tb = o
            if name in prefer_names:
                preferred = o
                break
            if preferred is None and (name.startswith("Txt_") or "Gold" in name or "Title" in name):
                preferred = o
    except Exception:
        return None
    return preferred if preferred is not None else any_tb


'''

if "_find_textblock_under" not in src:
    anchor = "def close_shop(world_ctx=None):"
    if anchor not in src:
        raise SystemExit("close_shop anchor missing")
    src = src.replace(anchor, HELPER + anchor, 1)
    print("helper inserted")
else:
    print("helper already present")

# Replace the refresh block at end of ensure_gold_hud to always rebind if needed
OLD_REFRESH = '''    # Refresh gold number every tick
    try:
        gold = int(get_gold(world))
    except Exception:
        gold = int(DEFAULT_GOLD)
    label = u"金币: %d" % gold
    txt = _GOLD_TXT[0]
    if txt is not None:
        try:
            txt.set_text(unreal.Text(label))
        except Exception:
            try:
                txt.set_editor_property("text", unreal.Text(label))
            except Exception:
                pass
    else:
        # Last resort: keep widget alive; print once rarely via log throttle not needed
        pass
'''

NEW_REFRESH = '''    # Refresh gold number every tick (rebind TextBlock via ObjectIterator if needed)
    try:
        gold = int(get_gold(world))
    except Exception:
        gold = int(DEFAULT_GOLD)
    label = u"金币: %d" % gold
    txt = _GOLD_TXT[0]
    if txt is None or (not _uobj_alive(txt)):
        try:
            txt = _find_textblock_under(_GOLD_WIDGET[0])
            _GOLD_TXT[0] = txt
        except Exception:
            txt = None
    if txt is not None:
        try:
            txt.set_visibility(unreal.SlateVisibility.VISIBLE)
        except Exception:
            pass
        try:
            txt.set_text(unreal.Text(label))
        except Exception:
            try:
                txt.set_editor_property("text", unreal.Text(label))
            except Exception:
                pass
    else:
        # Path-scoped paint fallback (same as shop titles)
        w = _GOLD_WIDGET[0]
        if w is not None and _uobj_alive(w):
            try:
                base = w.get_path_name()
                for o in unreal.ObjectIterator(unreal.TextBlock):
                    try:
                        pn = o.get_path_name()
                    except Exception:
                        continue
                    if base not in pn:
                        continue
                    try:
                        o.set_visibility(unreal.SlateVisibility.VISIBLE)
                        o.set_text(unreal.Text(label))
                        _GOLD_TXT[0] = o
                        break
                    except Exception:
                        pass
            except Exception:
                pass
'''

if OLD_REFRESH not in src:
    raise SystemExit("OLD_REFRESH not found")
src = src.replace(OLD_REFRESH, NEW_REFRESH, 1)
print("refresh patched")

# Also after create, bind with helper
OLD_BIND_END = '''        _GOLD_TXT[0] = txt

        # Hide progress bar if we fell back to health WBP instance
'''
NEW_BIND_END = '''        if txt is None:
            try:
                txt = _find_textblock_under(widget)
            except Exception:
                txt = None
        _GOLD_TXT[0] = txt

        # Hide progress bar if we fell back to health WBP instance
'''
if OLD_BIND_END not in src:
    raise SystemExit("OLD_BIND_END not found")
src = src.replace(OLD_BIND_END, NEW_BIND_END, 1)
print("bind patched")

with io.open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(src)
print("done")