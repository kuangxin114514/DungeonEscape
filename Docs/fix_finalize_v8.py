# -*- coding: utf-8 -*-
"""Finalize SAFE_V8: create via call_method; paint TextBlock_0; simulate E; dump CreateWidget nodes."""
from __future__ import print_function
import unreal
import traceback
import sys
import importlib
import re

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_finalize_v8.txt"
PYDIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
RT = PYDIR + r"\shop_interact_runtime.py"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("V8: " + s)
    except Exception:
        print("V8:", s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def patch_open_shop_text():
    src = open(RT, "r", encoding="utf-8").read()
    src = src.replace("SAFE_V7 new_object-first", "SAFE_V8 create-first")
    src = src.replace("runtime ready SAFE_V7", "runtime ready SAFE_V8")
    # Replace get_widget_from_name title block with ObjectIterator paint
    helper = '''
def _paint_shop_texts(widget, title_text):
    """Set all TextBlocks under widget; get_widget_from_name missing in UE4.27 py."""
    if widget is None:
        return
    base = widget.get_path_name()
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
        try:
            if name == "TextBlock_0" or "Title" in name:
                o.set_text(unreal.Text(str(title_text)))
            elif "Hint" in name or "Sub" in name:
                o.set_text(unreal.Text(u"E / Esc 关闭"))
            else:
                # leave other texts, but ensure visible
                pass
            o.set_visibility(unreal.SlateVisibility.VISIBLE)
        except Exception as e:
            _log("paint text " + str(e))
'''
    if "_paint_shop_texts" not in src:
        # insert before open_shop
        idx = src.find("\ndef open_shop(")
        if idx > 0:
            src = src[:idx] + "\n" + helper + "\n" + src[idx:]
            log("inserted _paint_shop_texts")
        else:
            log("open_shop not found for helper insert")
    # After successful create / before add_to_viewport, call paint
    if "_paint_shop_texts(widget" not in src:
        needle = "if not widget:\n        _log(\"open_shop FAIL create null\")\n        return False"
        insert_after = needle + "\n    _paint_shop_texts(widget, title_text)"
        if needle in src:
            src = src.replace(needle, insert_after, 1)
            log("wired paint call")
        else:
            log("needle missing for paint wire")
    # Remove broken get_widget_from_name loops? leave them, they just no-op if we wrap
    # Actually they will throw AttributeError each time - wrap or remove
    if "get_widget_from_name" in src:
        # comment-replace the for-name loops with pass via regex rough
        src2 = re.sub(
            r"for name in \(\"Txt_Title\".*?\n(?:.*?\n){0,12}?    pass\n",
            "    # title painted by _paint_shop_texts\n",
            src,
            count=1,
            flags=re.S,
        )
        if src2 != src:
            src = src2
            log("removed first get_widget_from_name loop")
        src2 = re.sub(
            r"for name, text in \(\n(?:.*?\n){0,20}?            pass\n",
            "    # subtexts painted by _paint_shop_texts\n",
            src,
            count=1,
        )
        if src2 != src:
            src = src2
            log("removed second get_widget_from_name loop")
        # Btn_Quit block can stay if wrapped - it also uses get_widget_from_name
        src = src.replace(
            'qb = widget.get_widget_from_name("Btn_Quit")',
            'qb = None  # get_widget_from_name unavailable in py',
        )
    open(RT, "w", encoding="utf-8").write(src)
    log("runtime file written V8")

def dump_createwidget_nodes():
    log("=== CreateWidget nodes on BP_KayKitKnight ===")
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight" in pn and "CreateWidget" in pn:
            log("NODE " + pn + " cls=" + o.get_class().get_name())
            # try export text
            for a in sorted(dir(o)):
                if "class" in a.lower() and not a.startswith("_"):
                    try:
                        v = getattr(o, a)
                        if not callable(v):
                            log("  " + a + "=" + str(v))
                    except Exception:
                        pass

def simulate_e():
    if PYDIR not in sys.path:
        sys.path.insert(0, PYDIR)
    import shop_interact_runtime as r
    importlib.reload(r)
    w = r._pie_world()
    log("pie=" + str(w))
    if not w:
        return False
    # close any open first so open is fresh
    r.close_shop(w)
    ok = r.handle_interact(w)
    log("handle_interact=" + str(ok))
    wid = r._OPEN_WIDGET[0]
    log("widget=" + str(wid))
    if not wid:
        return False
    base = wid.get_path_name()
    ntext = 0
    for o in unreal.ObjectIterator(unreal.TextBlock):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if base in pn:
            ntext += 1
            try:
                log("TB " + o.get_name() + " vis=" + str(o.get_visibility()))
            except Exception:
                log("TB " + pn)
    log("text_count=" + str(ntext))
    try:
        log("vis=" + str(wid.get_visibility()) + " invp=" + str(wid.is_in_viewport()))
    except Exception as e:
        log("vis err " + str(e))
    return ntext > 0 and wid.is_in_viewport()

def main():
    log("START")
    patch_open_shop_text()
    dump_createwidget_nodes()
    ok = simulate_e()
    log("FINAL_PROOF=" + str(ok))
    log("DONE")
    flush()

try:
    main()
except Exception:
    log("EXC\n" + traceback.format_exc())
    flush()
