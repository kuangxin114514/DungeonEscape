import unreal, json, traceback
out = {}
# Resolve classes via load_class
SCS = unreal.load_class(None, "/Script/Engine.SimpleConstructionScript")
SCSNode = unreal.load_class(None, "/Script/Engine.SCS_Node")
SMC = unreal.load_class(None, "/Script/Engine.StaticMeshComponent")
out["SCS"] = str(SCS)
out["SCSNode"] = str(SCSNode)
out["SMC"] = str(SMC)
scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
out["scs"] = str(scs)
# Iterate all SCS nodes in memory
nodes = []
if SCSNode:
    for obj in unreal.ObjectIterator(SCSNode):
        pn = obj.get_path_name()
        nodes.append(pn)
out["all_scs_nodes_count"] = len(nodes)
out["kaykit_nodes"] = [n for n in nodes if "KayKit" in n or "Kaykit" in n]
out["sample_nodes"] = nodes[:30]
# Find StaticMeshComponent templates under SCS nodes
sm_donors = []
for pn in nodes:
    try:
        node = unreal.load_object(None, pn)
        if not node:
            continue
        # try read component_class / template even if "protected" via get_editor_property
        info = {"path": pn}
        for prop in ["component_class", "ComponentClass", "component_template", "ComponentTemplate", "attach_to_name", "AttachToName", "parent_component_or_variable_name", "ParentComponentOrVariableName", "internal_variable_name", "InternalVariableName"]:
            try:
                v = node.get_editor_property(prop)
                info[prop] = str(v)
            except Exception as e:
                if "protected" in str(e).lower():
                    info[prop] = "PROTECTED"
                else:
                    info[prop] = "ERR"
        # Check subobjects
        # list children names via get_name on outer chain - try find GEN_VARIABLE
        clsname = info.get("component_class") or info.get("ComponentClass") or ""
        if "StaticMesh" in clsname:
            sm_donors.append(info)
        elif "PROTECTED" in str(info.values()):
            # peek template by load_object convention
            pass
        out.setdefault("node_infos", []).append(info)
    except Exception as e:
        out.setdefault("node_errs", []).append(pn+":"+str(e))
out["sm_donors"] = sm_donors
# Also search GEN_VARIABLE StaticMeshComponents
smcs = []
for obj in unreal.ObjectIterator(SMC):
    pn = obj.get_path_name()
    if "SCS_Node" in pn or "GEN_VARIABLE" in pn:
        smcs.append(pn)
out["smc_gen_vars"] = smcs[:50]
out["smc_gen_count"] = len(smcs)
# SK body check
sk = unreal.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
out["sk"] = str(sk)
try:
    # lod info
    out["sk_lods"] = sk.get_num_lods() if hasattr(sk, "get_num_lods") else None
except Exception as e:
    out["sk_lods_err"] = str(e)
# sockets - mesh socket array editor property
for prop in ["sockets", "Sockets"]:
    try:
        socks = sk.get_editor_property(prop)
        out["sk_"+prop] = [str(getattr(s,"socket_name",s)) for s in (socks or [])]
    except Exception as e:
        out["sk_"+prop+"_err"] = str(e)
skel = sk.skeleton
out["skel"] = str(skel)
for prop in ["sockets", "Sockets"]:
    try:
        socks = skel.get_editor_property(prop)
        out["skel_"+prop] = [str(getattr(s,"socket_name",s)) for s in (socks or [])]
    except Exception as e:
        out["skel_"+prop+"_err"] = str(e)
# BP mesh component current skeletal mesh
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
gc = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
out["gc"] = str(gc)
if gc:
    cdo = unreal.get_default_object(gc)
    out["cdo"] = str(cdo)
    try:
        mesh = cdo.get_editor_property("mesh")  # Character.Mesh
        out["cdo_mesh"] = str(mesh)
        if mesh:
            out["cdo_mesh_sk"] = str(mesh.get_editor_property("skeletal_mesh"))
            # try sockets on mesh component
    except Exception as e:
        out["cdo_mesh_err"] = str(e)
        try:
            mesh = cdo.mesh
            out["cdo_mesh_attr"] = str(mesh)
            out["cdo_mesh_sk"] = str(mesh.skeletal_mesh)
        except Exception as e2:
            out["cdo_mesh_err2"] = str(e2)
# Try duplicate CameraBoom node if exists
boom_candidates = [n for n in nodes if "CameraBoom" in n or "FollowCamera" in n]
out["boom_candidates"] = boom_candidates
# Attempt: create node via duplicate_object from any existing node under our scs
our_nodes = [n for n in nodes if "BP_KayKitKnight" in n]
out["our_nodes"] = our_nodes
open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs9.json","w",encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False))
print("sm_donors", len(sm_donors), sm_donors[:5])
print("smc_gen", len(smcs), smcs[:20])
print("our_nodes", our_nodes)
print("kaykit_nodes", out["kaykit_nodes"])
print("sk", out.get("sk"), "sockets", out.get("skel_Sockets") or out.get("skel_sockets") or out.get("sk_Sockets"))
print("cdo_mesh_sk", out.get("cdo_mesh_sk"))