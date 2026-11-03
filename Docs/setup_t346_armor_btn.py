# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\setup_t346_armor_btn.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T346A: "+str(m))
    except Exception: print(m)

try:
    # Replace armor shop with a duplicate of weapon shop (has Button_0 / Button), then relabel.
    armor="/Game/UI/Shop/WBP_Shop_Armor"
    weapon="/Game/UI/Shop/WBP_Shop_Weapon"
    tmp="/Game/UI/Shop/WBP_Shop_Armor_Tmp"
    # delete tmp if any
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(tmp):
            unreal.EditorAssetLibrary.delete_asset(tmp); L("del tmp")
    except Exception as e: L("del tmp "+str(e))
    # backup old armor aside
    bak="/Game/UI/Shop/WBP_Shop_Armor_OldTitleOnly"
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(armor) and not unreal.EditorAssetLibrary.does_asset_exist(bak):
            unreal.EditorAssetLibrary.rename_asset(armor, bak); L("renamed old armor -> bak")
        elif unreal.EditorAssetLibrary.does_asset_exist(armor):
            unreal.EditorAssetLibrary.delete_asset(armor); L("deleted old armor")
    except Exception as e:
        L("backup/del armor "+str(e))
        try:
            unreal.EditorAssetLibrary.delete_asset(armor); L("force del armor")
        except Exception as e2: L("force del "+str(e2))

    dup=unreal.EditorAssetLibrary.duplicate_asset(weapon, armor)
    L("dup weapon->armor = %s"%dup)
    # if duplicate_asset created wrong name, fix
    abp=unreal.load_asset(armor)
    L("armor load=%s"%abp)

    # Relabel texts in asset WidgetTree
    for o in unreal.ObjectIterator(unreal.TextBlock):
        try: pn=o.get_path_name()
        except Exception: continue
        if "/Game/UI/Shop/WBP_Shop_Armor.WBP_Shop_Armor:WidgetTree" not in pn:
            continue
        nm=o.get_name()
        try: cur=str(o.get_text())
        except Exception:
            try: cur=str(o.get_editor_property("text"))
            except Exception: cur=""
        L("TB %s cur=%s"%(nm, cur))
        new=None
        if nm=="TextBlock_0" or u"武器" in cur or "Weapon" in cur:
            new=u"防具店"
        elif nm=="TextBlock_1" or u"剑1" in cur:
            new=u"购买盾1"
        elif nm=="TextBlock" or u"剑2" in cur:
            new=u"购买盾2（未开放）"
        if new is not None:
            ok=False
            for setter in (
                lambda: o.set_text(new),
                lambda: o.set_editor_property("text", unreal.Text(new)),
                lambda: o.set_editor_property("Text", unreal.Text(new)),
            ):
                try:
                    setter(); ok=True; break
                except Exception:
                    pass
            L("  set -> %s ok=%s"%(new, ok))

    try:
        unreal.EditorAssetLibrary.save_asset(armor); L("save armor OK")
    except Exception as e:
        L("save "+str(e))
        try:
            if abp: unreal.EditorAssetLibrary.save_loaded_asset(abp); L("save_loaded")
        except Exception as e2: L("save_loaded "+str(e2))

    # verify buttons
    for o in unreal.ObjectIterator(unreal.Button):
        try: pn=o.get_path_name()
        except Exception: continue
        if "/Game/UI/Shop/WBP_Shop_Armor.WBP_Shop_Armor" in pn and "Transient" not in pn:
            L("BTN "+pn+" name="+o.get_name())

    # verify shield1 BP template still Round
    unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Shield1")
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try: pn=o.get_path_name()
        except Exception: continue
        if "BP_KayKitKnight_Shield1" not in pn or "GEN_VARIABLE" not in pn: continue
        try: sm=o.get_editor_property("static_mesh")
        except Exception: sm=None
        L("Shield1 %s mesh=%s"%(o.get_name(), sm.get_name() if sm else None))
except Exception as e:
    L("ERR "+str(e)); L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
