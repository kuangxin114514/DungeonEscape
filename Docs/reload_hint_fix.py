# -*- coding: utf-8 -*-
"""Hot-reload shop_interact_runtime so enter-once hint takes effect."""
from __future__ import print_function
import unreal
import importlib
import sys

OUT = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/reload_hint_fix.txt"

def w(s):
    try:
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(str(s) + "\n")
    except Exception:
        pass
    try:
        unreal.log("ReloadHint: " + str(s))
    except Exception:
        print(s)

# clear previous out
try:
    open(OUT, "w", encoding="utf-8").write("start\n")
except Exception as e:
    print("out fail", e)

# Unregister any stacked slate ticks we know about
prev = getattr(unreal, "_de_shop_tick_handle", None)
if prev is not None:
    for name in ("unregister_slate_post_tick_callback", "unregister_slate_pre_tick_callback"):
        fn = getattr(unreal, name, None)
        if not fn:
            continue
        try:
            fn(prev)
            w("unregistered prev " + name)
        except Exception as e:
            w("unreg prev " + str(e))
    try:
        unreal._de_shop_tick_handle = None
    except Exception:
        pass

# Also try to unregister from already-loaded module before reload
mod = sys.modules.get("shop_interact_runtime")
if mod is not None:
    tick = getattr(mod, "_TICK", [None])[0] if hasattr(mod, "_TICK") else None
    if tick is not None:
        for name in ("unregister_slate_post_tick_callback", "unregister_slate_pre_tick_callback"):
            fn = getattr(unreal, name, None)
            if not fn:
                continue
            try:
                fn(tick)
                w("unregistered module tick via " + name)
            except Exception as e:
                w("unreg mod " + str(e))

# Force re-import from disk
path = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Content/Python"
if path not in sys.path:
    sys.path.insert(0, path)

# Remove cached module so import reads new file
if "shop_interact_runtime" in sys.modules:
    del sys.modules["shop_interact_runtime"]

import shop_interact_runtime as sir
w("reloaded ok")
w("has_LAST_HINT=" + str(hasattr(sir, "_LAST_HINT_KEY")))
w("no_HINT_ACC=" + str(not hasattr(sir, "_HINT_ACC")))
w("tick=" + str(getattr(sir, "_TICK", [None])[0]))
w("handle=" + str(getattr(unreal, "_de_shop_tick_handle", None)))
w("done")
