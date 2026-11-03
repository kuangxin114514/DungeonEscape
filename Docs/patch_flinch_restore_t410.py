# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()
old = '''        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0
            # keep flinch_left: after 2 flinches stay armored until de-aggro
            if st.get("anim") == "attack":
                st["anim"] = None'''
new = '''        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0
            st["flinch_left"] = 2  # attack done: allow 2 flinches again
            if st.get("anim") == "attack":
                st["anim"] = None'''
if old not in raw:
    print("MISSING", repr(raw[raw.find("if atk_until > 0.0 and now >= atk_until"):raw.find("if atk_until > 0.0 and now >= atk_until")+220] if "if atk_until > 0.0 and now >= atk_until" in raw else "no"))
else:
    raw = raw.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(raw)
    compile(raw, p, "exec")
    print("restored_ok")
