# -*- coding: utf-8 -*-
import unreal, traceback
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_umg_slot_api.txt"
L=[]; 
def log(m):
    L.append(str(m)); unreal.log("UMGAPI: "+str(m))
# Anchors / Margin constructors
for args in [(), (0,), ((0,0),(0,0)), ]:
    pass
try:
    a=unreal.Anchors(); log("Anchors()="+str(a))
    for prop in ("minimum","maximum","min","max"):
        try:
            log("Anchors."+prop+"="+str(a.get_editor_property(prop)))
        except Exception as e:
            log("Anchors."+prop+" "+str(e))
    a.set_editor_property("minimum", unreal.Vector2D(0.0,0.0))
    a.set_editor_property("maximum", unreal.Vector2D(0.0,0.0))
    log("set min/max ok")
except Exception as e:
    log("Anchors "+str(e)+"\n"+traceback.format_exc())
try:
    m=unreal.Margin(); log("Margin()="+str(m))
    for prop in ("left","top","right","bottom"):
        try:
            m.set_editor_property(prop, 10.0); log("margin "+prop+" ok")
        except Exception as e:
            log("margin "+prop+" "+str(e))
except Exception as e:
    log("Margin "+str(e))
# Inspect shop / menu trees
for path in ["/Game/UI/Menus/WBP_MainMenu","/Game/UI/Shop/WBP_Shop","/Game/UI/Shop/WBP_Shop2","/Game/UI/Shop/WBP_Shop_Health"]:
    name=path.split("/")[-1]
    tree=unreal.load_object(None, path+"."+name+":WidgetTree")
    log("=== "+path+" tree="+str(tree))
    if not tree: continue
    root=None
    for prop in ("RootWidget","root_widget"):
        try:
            root=tree.get_editor_property(prop); log("root via "+prop+"="+str(root))
        except Exception as e:
            log("root "+prop+" "+str(e))
    # try get_editor_property via call
    try:
        root=tree.call_method("GetRootWidget"); log("GetRootWidget="+str(root))
    except Exception as e:
        log("GetRootWidget "+str(e))
    # list subobjects
    try:
        # iterate outer
        pass
    except Exception:
        pass
# Duplicate MainMenu as health bar base
src="/Game/UI/Menus/WBP_MainMenu"
if unreal.EditorAssetLibrary.does_asset_exist(src):
    dest="/Game/UI/HUD/WBP_PlayerHealthBar"
    # delete empty broken one first?
    try:
        unreal.EditorAssetLibrary.delete_asset(dest)
        log("deleted old health bar")
    except Exception as e:
        log("delete "+str(e))
    dup=unreal.EditorAssetLibrary.duplicate_asset(src, dest)
    log("dup="+str(dup))
else:
    log("no main menu")
# WidgetBlueprintLibrary compile?
for name in dir(unreal):
    if "Widget" in name and ("Blueprint" in name or "Editor" in name or "Tree" in name):
        log("unreal."+name)
open(OUT,"w",encoding="utf-8").write("\n".join(L)+"\n")
