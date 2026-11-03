# -*- coding: utf-8 -*-
"""t207: reload near-only shop interact runtime into UE."""
from __future__ import print_function
import unreal
import sys

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t207_near.txt"
PYDIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
lines = []

def log(m):
    lines.append(str(m))

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def kill_ticks():
    n = 0
    prev = getattr(unreal, "_de_shop_tick_handle", None)
    if prev is not None:
        for name in ("unregister_slate_post_tick_callback", "unregister_slate_pre_tick_callback"):
            fn = getattr(unreal, name, None)
            if fn:
                try:
                    fn(prev); n += 1
                except Exception:
                    pass
        try:
            unreal._de_shop_tick_handle = None
        except Exception:
            pass
    for modname, mod in list(sys.modules.items()):
        if "shop_interact" not in str(modname):
            continue
        for attr in ("_TICK", "_TICK_HANDLE"):
            val = getattr(mod, attr, None)
            handles = []
            if isinstance(val, list):
                handles = [h for h in val if h is not None]
            elif val is not None:
                handles = [val]
            for h in handles:
                for name in ("unregister_slate_post_tick_callback", "unregister_slate_pre_tick_callback"):
                    fn = getattr(unreal, name, None)
                    if fn:
                        try:
                            fn(h); n += 1
                        except Exception:
                            pass
            if isinstance(val, list):
                try:
                    val[0] = None
                except Exception:
                    pass
    try:
        unreal._de_shop_tick_gen = int(getattr(unreal, "_de_shop_tick_gen", 0)) + 1
    except Exception:
        unreal._de_shop_tick_gen = 1
    log("killed_ticks~%d gen=%s" % (n, getattr(unreal, "_de_shop_tick_gen", None)))

try:
    kill_ticks()
    if PYDIR not in sys.path:
        sys.path.insert(0, PYDIR)
    for k in list(sys.modules.keys()):
        if "shop_interact_runtime" in k:
            del sys.modules[k]
    import shop_interact_runtime as r
    # sanity: ensure near-only code is loaded
    src = open(PYDIR + r"\shop_interact_runtime.py", encoding="utf-8", errors="replace").read()
    log("has_NEAR_ONLY=%s" % ("NEAR_ONLY_V11" in src))
    log("has_always_open=%s" % ("Always open shop" in src))
    log("SHOP_RANGE=%s" % getattr(r, "SHOP_RANGE", None))
    log("tick=%s gen=%s" % (getattr(r, "_TICK", [None])[0], getattr(r, "_MY_GEN", [None])[0]))
    # peek handle_interact source behavior by calling with mock is hard; just confirm function exists
    log("handle_interact=%s" % callable(getattr(r, "handle_interact", None)))
    log("OK_NEAR_ONLY")
except Exception as e:
    import traceback
    log("FAIL " + str(e))
    log(traceback.format_exc())
finally:
    flush()
