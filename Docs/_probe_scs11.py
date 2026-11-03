import unreal, json
out = {"gens": [], "notes": []}
# List ALL subobjects under knight SCS by path prefix search via ObjectIterator Object
for cls_path in [
 "/Script/Engine.StaticMeshComponent",
 "/Script/Engine.SpringArmComponent",
 "/Script/Engine.CameraComponent",
 "/Script/Engine.SceneComponent",
 "/Script/Engine.ChildActorComponent",
 "/Script/Engine.SCS_Node",
]:
    cls = unreal.load_class(None, cls_path)
    if not cls:
        out["notes"].append("no "+cls_path)
        continue
    for obj in unreal.ObjectIterator(cls):
        pn = obj.get_path_name()
        if "BP_KayKitKnight" in pn and "SimpleConstructionScript" in pn:
            item = {"path": pn, "cls": cls_path.split(".")[-1]}
            if "StaticMesh" in cls_path:
                try:
                    item["mesh"] = str(obj.get_editor_property("static_mesh"))
                except Exception as e:
                    item["mesh"] = str(e)[:60]
            out["gens"].append(item)

# Try unreal.EditorAssetLibrary.duplicate_asset of sword actor as intermediate?
# Better: use AssetTools duplicate
# Try find DuplicateObject in unreal
out["has_dup"] = [n for n in dir(unreal) if "dup" in n.lower() or "Dup" in n]
out["has_copy"] = [n for n in dir(unreal) if "copy" in n.lower() or "Clone" in n or "clone" in n]

# Try EngineStaticDuplicateObject via load
# In UE Python sometimes: unreal.SystemLibrary ...
out["sys_dir"] = [n for n in dir(unreal.SystemLibrary) if "dup" in n.lower() or "copy" in n.lower()] if hasattr(unreal, "SystemLibrary") else []

# Construction script graph approach - list ubergraph
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
for prop in ["ubergraph_pages", "UbergraphPages", "function_graphs", "FunctionGraphs", "macro_graphs", "MacroGraphs", "delegate_signature_graphs", "DelegateSignatureGraphs", "new_variables", "NewVariables"]:
    try:
        v = bp.get_editor_property(prop)
        out["bp_"+prop] = str(type(v)) + ":" + (str(len(v)) if v is not None and hasattr(v,"__len__") else str(v)[:80])
    except Exception as e:
        out["bp_"+prop] = "ERR:"+str(e)[:100]

# Try create BlueprintFactory child with parent Character - then use EditorUtility
# Check EditorAssetLibrary methods for compile
out["eal"] = [n for n in dir(unreal.EditorAssetLibrary) if not n.startswith("_")]

# IMPORTANT: try using StaticDuplicateObject via unreal.Object
# Some versions expose:
try:
    import unreal as u
    # ctypes call into UE? skip
except Exception:
    pass

# Try new_object SCS_Node with proper RF flags and then force compile via AssetRegistry
scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
SCSNode = unreal.load_class(None, "/Script/Engine.SCS_Node")
SMC = unreal.load_class(None, "/Script/Engine.StaticMeshComponent")

# Create properly named node + template like editor does
try:
    node = unreal.new_object(SCSNode, scs, "SCS_Node_SwordMesh")
    out["new_node"] = str(node)
except Exception as e:
    out["new_node"] = "ERR:"+str(e)
    # maybe exists
    node = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_SwordMesh")
    out["load_node"] = str(node)

if node:
    try:
        tmpl = unreal.new_object(SMC, node, "SwordMesh_GEN_VARIABLE")
        out["new_tmpl"] = str(tmpl)
    except Exception as e:
        out["new_tmpl"] = "ERR:"+str(e)
        tmpl = unreal.load_object(None, node.get_path_name()+".SwordMesh_GEN_VARIABLE")
        out["load_tmpl"] = str(tmpl)
    if tmpl:
        sword = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
        try:
            tmpl.set_editor_property("static_mesh", sword)
            out["mesh_set"] = True
        except Exception as e:
            out["mesh_set"] = str(e)

# Check if there's a way to mark package dirty and use fixup
try:
    pkg = scs.get_outer() if hasattr(scs, "get_outer") else None
    out["scs_outer"] = str(pkg)
except Exception as e:
    out["scs_outer"] = str(e)

# Try call_method on BP for compile
for m in ["status", "Status"]:
    pass

# AssetEditorSubsystem compile?
aes = unreal.AssetEditorSubsystem()
out["aes_dir"] = [n for n in dir(aes) if not n.startswith("_")]

# Try PythonScriptLibrary
out["has_PSL"] = hasattr(unreal, "PythonScriptLibrary")
if hasattr(unreal, "PythonScriptLibrary"):
    out["psl"] = [n for n in dir(unreal.PythonScriptLibrary) if not n.startswith("_")]

open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs11.json","w",encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False))
print("gens", json.dumps(out["gens"], indent=2))
print("dup", out.get("has_dup"), "eal_sample", [x for x in out.get("eal",[]) if "save" in x.lower() or "compile" in x.lower() or "dup" in x.lower()])
print("bp graphs", {k:v for k,v in out.items() if k.startswith("bp_")})
print("aes", out.get("aes_dir"))
print("new", out.get("new_node"), out.get("new_tmpl"), out.get("mesh_set"))