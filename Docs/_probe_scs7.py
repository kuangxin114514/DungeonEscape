import unreal, json, traceback, os
out = {"ok": True}
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
sk = unreal.load_asset("/Game/Characters/Player/KayKit/SK_KayKitKnight")
out["bp"] = str(bp)
out["bp_class"] = str(type(bp))
out["sk"] = str(sk)
out["bp_dir_scs"] = [a for a in dir(bp) if "scs" in a.lower() or "construction" in a.lower() or "simple" in a.lower()]
# try editor properties
for prop in ["simple_construction_script", "SimpleConstructionScript", "generated_class"]:
    try:
        out["prop_"+prop] = str(bp.get_editor_property(prop))
    except Exception as e:
        out["prop_"+prop] = "ERR:"+str(e)
try:
    socks = list(sk.sockets) if sk.sockets else []
    out["sk_sockets"] = [str(getattr(s, "socket_name", s)) for s in socks]
except Exception as e:
    out["sk_sockets_err"] = str(e)
# try skeleton sockets
try:
    skel = sk.skeleton
    out["skeleton"] = str(skel)
    # socket names on skeleton
    try:
        ss = skel.sockets
        out["skel_sockets"] = [str(getattr(s,"socket_name",s)) for s in (ss or [])]
    except Exception as e:
        out["skel_sockets_err"] = str(e)
except Exception as e:
    out["skel_err"] = str(e)
mats = []
for i in range(0, 12):
    try:
        m = sk.get_material(i)
        if not m:
            break
        mats.append(m.get_path_name())
    except Exception:
        break
out["materials"] = mats
# get SCS via generated class or editor property variants
scs = None
for getter in [
    lambda: bp.get_editor_property("simple_construction_script"),
    lambda: bp.get_editor_property("SimpleConstructionScript"),
]:
    try:
        scs = getter()
        if scs:
            break
    except Exception as e:
        out.setdefault("scs_get_errs", []).append(str(e))
out["scs"] = str(scs)
if scs:
    out["scs_dir"] = [a for a in dir(scs) if any(k in a.lower() for k in ("node", "add", "create", "root", "all", "remove", "find", "get"))]
    try:
        nodes = scs.get_editor_property("all_nodes")
        out["all_nodes_len"] = len(nodes) if nodes is not None else None
        out["all_nodes"] = []
        if nodes:
            for n in nodes:
                info = {"str": str(n)}
                for prop in ["component_class", "component_template", "attach_to_name", "parent_component_or_variable_name", "variable_name", "internal_variable_name", "b_is_parent_component_native", "parent_component_owner_class_name"]:
                    try:
                        info[prop] = str(n.get_editor_property(prop))
                    except Exception as e:
                        info[prop] = "ERR:" + str(e)
                out["all_nodes"].append(info)
    except Exception as e:
        out["all_nodes_err"] = str(e)
out["has_BEL"] = hasattr(unreal, "BlueprintEditorLibrary")
out["has_SDS"] = hasattr(unreal, "SubobjectDataSubsystem")
out["has_KEU"] = hasattr(unreal, "KismetEditorUtilities")
out["bp_related"] = sorted([n for n in dir(unreal) if any(k in n for k in ("Blueprint", "SCS", "Subobject", "Construction", "KismetEditor"))])
# weapon assets
for p in ["/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword", "/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield"]:
    out["exists_"+p.split("/")[-1]] = unreal.EditorAssetLibrary.does_asset_exist(p)
docdir = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs"
out["docs_fbx"] = [f for f in os.listdir(docdir) if f.lower().endswith(".fbx")]
# body only reimport log
for logn in ["ue_body_only_reimport.log", "export_knight_body_only.log"]:
    lp = os.path.join(docdir, logn)
    if os.path.exists(lp):
        out["log_"+logn] = open(lp, encoding="utf-8", errors="replace").read()[-1500:]
# open editor
try:
    aes = unreal.AssetEditorSubsystem()
    aes.open_editor_for_assets([bp])
    out["opened"] = True
except Exception as e:
    out["opened_err"] = str(e)
# Explore KismetEditorUtilities methods
if hasattr(unreal, "KismetEditorUtilities"):
    out["KEU_dir"] = [a for a in dir(unreal.KismetEditorUtilities) if not a.startswith("_")]
path = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs7.json"
open(path, "w", encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False))
print("WROTE")
print("scs", out.get("scs"))
print("nodes", out.get("all_nodes_len"), out.get("all_nodes"))
print("BEL", out.get("has_BEL"), "SDS", out.get("has_SDS"), "KEU", out.get("has_KEU"))
print("bp_related", out.get("bp_related"))
print("fbx", out.get("docs_fbx"))
print("socks", out.get("sk_sockets") or out.get("skel_sockets"))
print("mats", out.get("materials"))