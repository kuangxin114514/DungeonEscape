# -*- coding: utf-8 -*-
"""Deploy V15e: Slot-first attack keep AnimBP; guide for Layered+spine wire."""
from __future__ import print_function
import unreal
import shutil
import os
import sys
import importlib

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\deploy_v15e_t231.txt"
SRC = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime_v15e.py"
DST_PY = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
DST_DOCS = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py"
GUIDE_SRC = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\wire_upperbody_attack_t231.md"
lines = []


def L(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("T231: " + s)
    except Exception:
        print("T231:", s)


def flush():
    try:
        open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    except Exception as e:
        print("flush", e)


def main():
    L("=== deploy V15e upperbody slot ===")
    if not os.path.isfile(SRC):
        L("MISSING SRC " + SRC)
        flush()
        return
    for dst in (DST_PY, DST_DOCS):
        d = os.path.dirname(dst)
        if not os.path.isdir(d):
            os.makedirs(d)
        shutil.copyfile(SRC, dst)
        L("copied -> %s (%d bytes)" % (dst, os.path.getsize(dst)))
    if os.path.isfile(GUIDE_SRC):
        L("guide present: " + GUIDE_SRC)
    # List AnimGraph nodes briefly
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    kinds = {}
    for obj in unreal.ObjectIterator(EdGraphNode):
        pn = obj.get_path_name()
        if "ABP_KayKitLocomotion:AnimGraph." not in pn:
            continue
        if "StateMachine_1.Default" in pn:
            continue
        cn = obj.get_class().get_name()
        kinds[cn] = kinds.get(cn, 0) + 1
        if cn == "AnimGraphNode_Slot":
            try:
                sn = obj.get_editor_property("node").get_editor_property("slot_name")
                L("Slot node path=%s name=%s" % (pn, sn))
            except Exception as e:
                L("Slot node %s err %s" % (pn, e))
    L("AnimGraph node counts: %s" % kinds)
    # Reload module + restart tick
    sys.path.insert(0, r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python")
    mod = sys.modules.get("shop_interact_runtime")
    try:
        if mod is None:
            import shop_interact_runtime as mod
            L("imported shop_interact_runtime")
        else:
            importlib.reload(mod)
            L("reload OK")
    except Exception as e:
        L("import/reload fail " + str(e))
        try:
            import shop_interact_runtime as mod
            L("fresh import OK")
        except Exception as e2:
            L("fresh import fail " + str(e2))
            flush()
            return
    # Confirm V15e markers
    try:
        src_txt = open(DST_PY, encoding="utf-8").read(400)
        L("header_snip: " + src_txt.replace("\n", " | ")[:300])
    except Exception as e:
        L("read header " + str(e))
    try:
        if hasattr(mod, "try_attack"):
            doc = (mod.try_attack.__doc__ or "")[:120]
            L("try_attack doc: " + doc.replace("\n", " "))
        if hasattr(mod, "start") or hasattr(mod, "ensure_tick") or hasattr(mod, "install"):
            L("mod attrs sample: %s" % [a for a in dir(mod) if not a.startswith("_")][:30])
    except Exception as e:
        L("probe mod " + str(e))
    # Re-register tick if module exposes helpers
    for fn_name in ("bootstrap", "ensure_tick", "install", "start", "register", "boot", "restart"):
        fn = getattr(mod, fn_name, None)
        if callable(fn):
            try:
                fn()
                L("called %s()" % fn_name)
            except TypeError:
                try:
                    fn(None)
                    L("called %s(None)" % fn_name)
                except Exception as e:
                    L("%s err %s" % (fn_name, e))
            except Exception as e:
                L("%s err %s" % (fn_name, e))
            if fn_name == "bootstrap":
                break
    L("DONE V15e")
    flush()
    print("WROTE", OUT)


main()
