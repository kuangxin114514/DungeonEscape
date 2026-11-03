import unreal, json
out = {}
# find SK
for p in [
 "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight",
 "/Game/Characters/Player/KayKit/SK_KayKitKnight",
]:
    out[p] = unreal.EditorAssetLibrary.does_asset_exist(p)
    a = unreal.load_asset(p) if out[p] else None
    out[p+"_obj"] = str(a)
sk = unreal.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
out["sk"] = str(sk)
# sockets on mesh and skeleton
try:
    out["mesh_sockets"] = [str(s.socket_name) for s in (sk.sockets or [])]
except Exception as e:
    out["mesh_sockets_err"] = str(e)
skel = sk.skeleton
out["skel"] = str(skel)
try:
    out["skel_sockets"] = [str(s.socket_name) for s in (skel.sockets or [])]
except Exception as e:
    out["skel_sockets_err"] = str(e)
# bone names containing hand/slot/weapon via reference skeleton
try:
    ref = skel.get_reference_skeleton() if hasattr(skel, "get_reference_skeleton") else None
    out["ref"] = str(ref)
except Exception as e:
    out["ref_err"] = str(e)
# find SCS by object path
paths = [
 "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0",
 "/Game/Characters/Player/KayKit/BP_KayKitKnight.Default__BP_KayKitKnight_C:SimpleConstructionScript_0",
 "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:SimpleConstructionScript_0",
]
for p in paths:
    o = unreal.find_object(None, p)
    out["find:"+p] = str(o)
# also find all objects with SimpleConstructionScript in name under package
pkg = unreal.load_package("/Game/Characters/Player/KayKit/BP_KayKitKnight")
out["pkg"] = str(pkg)
found = []
for obj in unreal.ObjectIterator(unreal.SimpleConstructionScript):
    pn = obj.get_path_name()
    if "KayKitKnight" in pn:
        found.append(pn)
out["scs_iter"] = found
foundn = []
for obj in unreal.ObjectIterator(unreal.SCS_Node):
    pn = obj.get_path_name()
    if "KayKitKnight" in pn:
        foundn.append(pn)
out["scs_node_iter"] = foundn
# BP generated class
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
try:
    gc = bp.generated_class()
    out["gen"] = str(gc)
except Exception as e:
    try:
        gc = bp.get_editor_property("GeneratedClass")
        out["gen"] = str(gc)
    except Exception as e2:
        out["gen_err"] = str(e)+" | "+str(e2)
# try load BP_KayKitKnight_C
gc2 = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
out["gc2"] = str(gc2)
if gc2:
    cdo = unreal.get_default_object(gc2)
    out["cdo"] = str(cdo)
    # components on CDO
    try:
        comps = cdo.get_components_by_class(unreal.ActorComponent)
        out["cdo_comps"] = [c.get_name()+":"+c.get_class().get_name() for c in (comps or [])]
    except Exception as e:
        out["cdo_comps_err"] = str(e)
    try:
        smcs = cdo.get_components_by_class(unreal.StaticMeshComponent)
        out["cdo_smc"] = [c.get_name() for c in (smcs or [])]
    except Exception as e:
        out["cdo_smc_err"] = str(e)
open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs8.json","w",encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False))
print(json.dumps(out, indent=2, ensure_ascii=False)[:4000])