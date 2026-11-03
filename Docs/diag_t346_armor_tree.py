# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_t346_armor_tree.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log(str(m))
    except Exception: print(m)
for leaf in ("WBP_Shop_Armor","WBP_Shop_Weapon","WBP_Shop"):
    for cls in (unreal.Widget, unreal.Button, unreal.TextBlock, unreal.CanvasPanel, unreal.VerticalBox, unreal.HorizontalBox):
        for o in unreal.ObjectIterator(cls):
            try: pn=o.get_path_name()
            except Exception: continue
            if ("/Game/UI/Shop/%s."%leaf) not in pn and (":%s"%leaf) not in pn:
                if leaf not in pn or "/Game/UI/Shop/" not in pn: continue
            if "REINST" in pn or "Transient" in pn: continue
            L("%s %s %s"%(leaf, o.get_class().get_name(), pn))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT, "lines", len(lines))
