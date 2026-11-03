# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_weapon_shop.txt"
lines=[]
def L(m):
    lines.append(str(m)); 
    try: unreal.log("ProbeShop: "+str(m))
    except Exception: print(m)

paths=[
 "/Game/UI/Shop/WBP_Shop_Weapon",
 "/Game/UI/Shop/WBP_Shop",
]
for p in paths:
    L("=== "+p+" ===")
    if not unreal.EditorAssetLibrary.does_asset_exist(p):
        L("missing"); continue
    unreal.EditorAssetLibrary.load_asset(p)
    # iterate widgets belonging to this asset
    for cls_name, cls in (
        ("Button", unreal.Button),
        ("TextBlock", unreal.TextBlock),
        ("Image", unreal.Image),
        ("Border", unreal.Border),
        ("CanvasPanel", unreal.CanvasPanel),
        ("VerticalBox", unreal.VerticalBox),
        ("HorizontalBox", unreal.HorizontalBox),
    ):
        for o in unreal.ObjectIterator(cls):
            try: pn=o.get_path_name()
            except Exception: continue
            if p+"." not in pn and "/WBP_Shop_Weapon." not in pn and (p.split('/')[-1]+"." not in pn):
                # filter by asset
                if "/"+p.split("/")[-1]+"." not in pn:
                    continue
            if "/Game/UI/Shop/" not in pn:
                continue
            if p.split("/")[-1] not in pn:
                continue
            extra=""
            if cls_name=="TextBlock":
                try: extra=" text="+str(o.get_editor_property("text"))
                except Exception:
                    try: extra=" text="+str(o.text)
                    except Exception: extra=""
            L("%s %s%s" % (cls_name, o.get_name(), extra))

# also knight BP components
L("=== BP_KayKitKnight SCS ===")
bp=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
L("bp="+str(bp))
try:
    scs=bp.simple_construction_script
    for n in scs.get_all_nodes():
        try:
            vn=n.get_variable_name()
        except Exception:
            vn="?"
        try:
            cn=n.component_class.get_name() if n.component_class else "?"
        except Exception:
            cn="?"
        L("node var=%s class=%s" % (vn, cn))
except Exception as e:
    L("scs "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
