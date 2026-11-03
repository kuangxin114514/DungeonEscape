# -*- coding: utf-8 -*-
import unreal, json
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_scs2.json"
r={"tries":[]}
def note(m,**k):
    e={"m":m}; e.update(k); r["tries"].append(e); unreal.log("SCS2:"+str(m))

bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
# call_method experiments
for meth in ("GetSimpleConstructionScript","get_simple_construction_script","GetBlueprintInheritedVariables"):
    try:
        val = bp.call_method(meth)
        note("call", meth=meth, val=str(val))
    except Exception as e:
        note("call_fail", meth=meth, err=str(e))

# AssetEditorSubsystem
try:
    aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    note("aes", val=str(aes), methods=[a for a in dir(aes) if not a.startswith("_")])
except Exception as e:
    note("aes_fail", err=str(e))

# Try open BP
tools = unreal.AssetToolsHelpers.get_asset_tools()
try:
    tools.open_editor_for_assets([bp])
    note("opened_bp")
except Exception as e:
    note("open_fail", err=str(e))

# EditorUtilitySubsystem
try:
    eus = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
    note("eus", methods=[a for a in dir(eus) if not a.startswith("_")])
except Exception as e:
    note("eus_fail", err=str(e))

# Try creating Actor BP (not child of Character) - Actor factory often creates SCS with DefaultSceneRoot
tools = unreal.AssetToolsHelpers.get_asset_tools()
path="/Game/Characters/Player/KayKit/BP_WeaponAttachProbe"
if unreal.EditorAssetLibrary.does_asset_exist(path):
    unreal.EditorAssetLibrary.delete_asset(path)
factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
bp_actor = tools.create_asset("BP_WeaponAttachProbe", "/Game/Characters/Player/KayKit", unreal.Blueprint, factory)
note("actor_bp", val=str(bp_actor))
if bp_actor:
    for prop in ("SimpleConstructionScript",):
        try:
            scs = bp_actor.get_editor_property(prop)
            note("actor_scs", val=str(scs), methods=[a for a in dir(scs) if not a.startswith("_")][:60])
        except Exception as e:
            note("actor_scs_fail", err=str(e))
    try:
        scs = bp_actor.call_method("GetSimpleConstructionScript")
        note("actor_call_scs", val=str(scs), methods=[a for a in dir(scs) if not a.startswith("_")][:60] if scs else [])
        if scs:
            for meth in ("CreateNode","create_node","GetAllNodes","get_all_nodes","AddNode","FindParentNode"):
                note("has", meth=meth, val=hasattr(scs, meth.lower()) or hasattr(scs, meth))
                try:
                    if meth in ("CreateNode","create_node"):
                        # try call_method
                        node = scs.call_method("CreateNode", (unreal.StaticMeshComponent, "SwordMesh")) if hasattr(scs,"call_method") else None
                        note("CreateNode_call", val=str(node))
                except Exception as e:
                    note("CreateNode_err", err=str(e))
    except Exception as e:
        note("actor_call_fail", err=str(e))

# Inspect SimpleConstructionScript class
try:
    scs_cls = unreal.load_class(None, "/Script/Engine.SimpleConstructionScript")
    note("scs_cls", val=str(scs_cls), dir=[a for a in dir(scs_cls) if not a.startswith("_")][:40])
    note("scs_cls_attrs", attrs=[a for a in dir(unreal.SimpleConstructionScript) if not a.startswith("_")] if hasattr(unreal,"SimpleConstructionScript") else "no_py_class")
except Exception as e:
    note("scs_cls_err", err=str(e))

if hasattr(unreal, "SimpleConstructionScript"):
    note("SCS_py", methods=[a for a in dir(unreal.SimpleConstructionScript) if not a.startswith("_")])
if hasattr(unreal, "SCS_Node"):
    note("SCS_Node", methods=[a for a in dir(unreal.SCS_Node) if not a.startswith("_")])

with open(OUT,"w",encoding="utf-8") as f: json.dump(r,f,indent=2,default=str)
print("SCS2_DONE")