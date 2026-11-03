# -*- coding: utf-8 -*-
"""Probe UE4.27 Python APIs for adding StaticMeshComponents to BP_KayKitKnight."""
import unreal
import os, json

ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
OUT = os.path.join(ROOT, "Docs", "probe_scs_apis.json")
result = {"steps": []}

def note(m, **kw):
    entry = {"msg": str(m)}
    entry.update(kw)
    result["steps"].append(entry)
    try: unreal.log("PROBE: " + str(m))
    except Exception: pass

bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
note("bp", val=str(bp))
scs = None
for prop in ("simple_construction_script", "SimpleConstructionScript"):
    try:
        scs = bp.get_editor_property(prop)
        note("got_scs", prop=prop, val=str(scs))
        break
    except Exception as e:
        note("scs_fail", prop=prop, err=str(e))

bel = getattr(unreal, "BlueprintEditorLibrary", None)
note("BlueprintEditorLibrary", exists=bel is not None)
if bel:
    note("BEL_attrs", attrs=[a for a in dir(bel) if not a.startswith("_")][:60])

if scs:
    note("scs_methods", attrs=[a for a in dir(scs) if not a.startswith("_")][:80])
    try:
        nodes = scs.get_editor_property("root_nodes")
        note("root_nodes", val=str(nodes))
    except Exception as e:
        note("root_nodes_err", err=str(e))
    for meth in ("create_node", "CreateNode", "add_node", "get_all_nodes"):
        note("has_"+meth, val=hasattr(scs, meth))

sk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
note("sk", val=str(sk))
if sk:
    try:
        mats = sk.materials
        note("materials_count", n=len(list(mats)) if mats is not None else -1)
        note("materials", names=[str(m) for m in list(mats)][:20] if mats else [])
    except Exception as e:
        note("mats_err", err=str(e))
    note("sk_interesting", attrs=[a for a in dir(sk) if any(x in a.lower() for x in ("section","lod","material","vert","socket"))][:50])

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
note("skel", val=str(skel))
if skel:
    note("skel_attrs", attrs=[a for a in dir(skel) if "socket" in a.lower() or "preview" in a.lower() or "bone" in a.lower()][:40])
    for prop in ("sockets", "Sockets"):
        try:
            socks = skel.get_editor_property(prop)
            note("sockets", val=str(socks), n=len(list(socks)) if socks is not None else -1)
            if socks:
                for s in list(socks)[:20]:
                    try:
                        note("sock", name=str(s.get_editor_property("socket_name")), bone=str(s.get_editor_property("bone_name")))
                    except Exception as e:
                        note("sock_item", raw=str(s), err=str(e))
        except Exception as e:
            note("sock_err", prop=prop, err=str(e))

tools = unreal.AssetToolsHelpers.get_asset_tools()
test_path = "/Game/Characters/Player/KayKit/BP_ProbeArmed"
if unreal.EditorAssetLibrary.does_asset_exist(test_path):
    try: unreal.EditorAssetLibrary.delete_asset(test_path)
    except Exception as e: note("del_probe", err=str(e))
parent = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
note("parent_cls", val=str(parent))
if parent:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    bp2 = tools.create_asset("BP_ProbeArmed", "/Game/Characters/Player/KayKit", unreal.Blueprint, factory)
    note("created_child", val=str(bp2))
    if bp2:
        scs2 = None
        for prop in ("simple_construction_script", "SimpleConstructionScript"):
            try:
                scs2 = bp2.get_editor_property(prop)
                note("child_scs", prop=prop, val=str(scs2))
                break
            except Exception as e:
                note("child_scs_fail", prop=prop, err=str(e))
        if scs2 is None:
            try:
                scs_cls = unreal.load_class(None, "/Script/Engine.SimpleConstructionScript")
                scs2 = unreal.new_object(scs_cls, bp2, "SimpleConstructionScript")
                note("new_scs_obj", val=str(scs2))
                try:
                    bp2.set_editor_property("simple_construction_script", scs2)
                    note("set_scs_ok")
                except Exception as e:
                    note("set_scs_fail", err=str(e))
            except Exception as e:
                note("new_scs_fail", err=str(e))
        if scs2:
            note("scs2_methods", attrs=[a for a in dir(scs2) if "node" in a.lower() or "create" in a.lower()][:40])
            try:
                node = scs2.create_node(unreal.StaticMeshComponent, "SwordMesh")
                note("create_node_ok", val=str(node))
                if node:
                    note("node_attrs", attrs=[a for a in dir(node) if not a.startswith("_")][:50])
                    for prop, val in (("parent_component_or_variable_name", "Mesh"), ("parent_socket_name", "handslot_r"), ("attach_to_name", "Mesh")):
                        try:
                            node.set_editor_property(prop, val)
                            note("set_node", prop=prop, ok=True)
                        except Exception as e:
                            note("set_node_fail", prop=prop, err=str(e))
                    try:
                        tmpl = node.get_editor_property("component_template")
                        note("tmpl", val=str(tmpl))
                        sm = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
                        if tmpl and sm:
                            tmpl.set_editor_property("static_mesh", sm)
                            note("tmpl_mesh_set")
                    except Exception as e:
                        note("tmpl_err", err=str(e))
            except Exception as e:
                note("create_node_fail", err=str(e))
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(bp2)
            note("saved_probe")
        except Exception as e:
            note("save_probe_fail", err=str(e))

for name in ("KismetEditorUtilities", "EditorUtilityLibrary", "SubobjectDataBlueprintFunctionLibrary", "SubobjectDataSubsystem"):
    note("mod_"+name, exists=hasattr(unreal, name))

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, default=str)
note("wrote", path=OUT)
print("PROBE_DONE")