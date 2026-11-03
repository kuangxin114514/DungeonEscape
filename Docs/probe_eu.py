# -*- coding: utf-8 -*-
import unreal, os, json
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_eu.json"
r = {"eu": [a for a in dir(unreal.EditorUtilityLibrary) if not a.startswith("_")],
     "asset_tools": [a for a in dir(unreal.AssetToolsHelpers.get_asset_tools()) if "blue" in a.lower() or "comp" in a.lower() or "create" in a.lower()],
     "unreal_blue": [a for a in dir(unreal) if "Blue" in a or "SCS" in a or "Subobject" in a or "Component" in a and "Library" in a],
     "sk_sockets": None,
     "sk_num_sockets": None,
     "find_hand": None}
sk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
try:
    r["sk_num_sockets"] = sk.num_sockets()
except Exception as e:
    r["sk_num_sockets"] = str(e)
try:
    for name in ("handslot_r","handslot_l","hand_r","hand_l","weapon_r","weapon_l"):
        s = sk.find_socket(name)
        r["find_"+name] = str(s)
except Exception as e:
    r["find_err"] = str(e)
# try open editor
try:
    unreal.EditorAssetLibrary.sync_browser_to_objects(["/Game/Characters/Player/KayKit/BP_KayKitKnight"])
    r["sync_ok"] = True
except Exception as e:
    r["sync_err"] = str(e)
# Can we use load_package and find SCS objects in BP?
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
try:
    outer_objs = unreal.EditorAssetLibrary.find_package_assets(bp.get_outer().get_name()) if False else None
except Exception:
    pass
# Iterate objects with same package
pkg_name = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
try:
    objs = unreal.EditorAssetLibrary.list_assets(pkg_name, True, True)
    r["pkg_assets"] = list(objs) if objs else []
except Exception as e:
    r["pkg_err"] = str(e)
# get all objects in memory related
try:
    import gc
except Exception:
    pass
# Probe sword actor BP for SCS pattern
sword_bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Weapons/BP_KayKitSwordActor")
r["sword_bp"] = str(sword_bp)
for prop in ("SimpleConstructionScript", "simple_construction_script"):
    try:
        r["sword_"+prop] = str(sword_bp.get_editor_property(prop))
    except Exception as e:
        r["sword_"+prop] = str(e)
# Check GeneratedClass CDO components
cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
cdo = unreal.get_default_object(cls)
r["cdo_comps"] = []
try:
    comps = cdo.get_components_by_class(unreal.ActorComponent)
    for c in comps:
        r["cdo_comps"].append({"name": c.get_name(), "class": c.get_class().get_name(), "owner": str(c.get_owner())})
except Exception as e:
    r["cdo_comps_err"] = str(e)
# ChildActorComponent on CDO?
try:
    mesh = cdo.get_editor_property("mesh")
    r["mesh"] = str(mesh)
    r["mesh_children"] = []
    # attach children?
    try:
        children = mesh.get_children_components(True)
        for ch in children:
            r["mesh_children"].append(ch.get_name() + ":" + ch.get_class().get_name())
    except Exception as e:
        r["mesh_children_err"] = str(e)
except Exception as e:
    r["mesh_err"] = str(e)

with open(OUT,"w",encoding="utf-8") as f:
    json.dump(r,f,indent=2,default=str)
print("EU_DONE")