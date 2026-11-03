# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_weapon_shop2.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("ProbeShop2: "+str(m))
    except Exception: print(m)

# list shop dir
try:
    for a in unreal.EditorAssetLibrary.list_assets("/Game/UI/Shop", True, False):
        L("asset "+a)
except Exception as e:
    L("list "+str(e))

for p in ("/Game/UI/Shop/WBP_Shop_Weapon","/Game/UI/Shop/WBP_Shop","/Game/Characters/Player/KayKit/BP_KayKitKnight"):
    L("exist "+p+" "+str(unreal.EditorAssetLibrary.does_asset_exist(p)))
    try:
        o=unreal.EditorAssetLibrary.load_asset(p)
        L("load "+p+" -> "+str(o)+" cls="+str(type(o)))
    except Exception as e:
        L("loaderr "+str(e))

# load class for weapon shop
for path in (
 "/Game/UI/Shop/WBP_Shop_Weapon.WBP_Shop_Weapon_C",
 "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",
):
    c=unreal.load_class(None, path)
    L("class "+path+" -> "+str(c))

# WidgetBlueprint API
wbp=unreal.EditorAssetLibrary.load_asset("/Game/UI/Shop/WBP_Shop_Weapon")
if wbp:
    L("wbp fields: try widget_tree")
    for prop in ("widget_tree","WidgetTree","generated_class","GeneratedClass"):
        try:
            v=wbp.get_editor_property(prop)
            L("prop %s=%s"%(prop,v))
        except Exception as e:
            L("prop %s fail %s"%(prop,e))
    # ObjectIterator after load
    for o in unreal.ObjectIterator(unreal.Button):
        try: pn=o.get_path_name()
        except Exception: continue
        if "WBP_Shop_Weapon" in pn:
            L("BTN "+pn+" name="+o.get_name())
    for o in unreal.ObjectIterator(unreal.TextBlock):
        try: pn=o.get_path_name()
        except Exception: continue
        if "WBP_Shop_Weapon" in pn:
            try: t=str(o.get_editor_property("text"))
            except Exception: t="?"
            L("TB "+o.get_name()+" text="+t+" path="+pn)

# knight
bp=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
if bp is None:
    # search
    try:
        for a in unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit", False, False):
            if "BP_KayKitKnight" in a and "Probe" not in a and "Armed" not in a:
                L("found "+a)
                bp=unreal.EditorAssetLibrary.load_asset(a.split(".")[0])
    except Exception as e:
        L("search "+str(e))
if bp:
    L("bp ok "+str(bp))
    try:
        scs=bp.get_editor_property("simple_construction_script")
    except Exception:
        scs=getattr(bp,"simple_construction_script",None)
    L("scs="+str(scs))
    if scs:
        try:
            nodes=scs.get_all_nodes()
        except Exception:
            nodes=[]
        for n in nodes:
            try: vn=str(n.get_variable_name())
            except Exception: vn="?"
            try: cc=n.get_editor_property("component_class")
            except Exception: cc=None
            L("SCS %s class=%s"%(vn, cc))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
