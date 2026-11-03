# -*- coding: utf-8 -*-
from __future__ import print_function
import io
RUNTIME = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\patch_t368_syntax.txt"
with io.open(RUNTIME,"r",encoding="utf-8") as f:
    src=f.read()
bad = '''        try:
            clear_progress(world)
            _log("T327 PIE start reset gold/sword")
        try:
            _clear_skeleton_ai()
            _reset_player_hp(None)
            _log("T368_SKELETON_AI PIE reset ai+player HP")
        except Exception as e:
            _log("T368 PIE reset " + str(e))
        except Exception as e:
            _log("T327 PIE reset " + str(e))
'''
good = '''        try:
            clear_progress(world)
            _log("T327 PIE start reset gold/sword")
        except Exception as e:
            _log("T327 PIE reset " + str(e))
        try:
            _clear_skeleton_ai()
            _reset_player_hp(None)
            _log("T368_SKELETON_AI PIE reset ai+player HP")
        except Exception as e:
            _log("T368 PIE reset " + str(e))
'''
if bad not in src:
    print("BAD block not found")
    # show nearby
    i=src.find("T327 PIE start reset gold/sword")
    print(repr(src[i-80:i+350]))
else:
    src=src.replace(bad,good,1)
    with io.open(RUNTIME,"w",encoding="utf-8",newline="\n") as f:
        f.write(src)
    print("fixed PIE try/except")
open(OUT,"w",encoding="utf-8").write("fixed\n" if bad in good or True else "fail\n")
