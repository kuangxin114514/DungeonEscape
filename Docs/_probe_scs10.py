import unreal, json, traceback

def try_props(obj, props):
    info = {}
    for prop in props:
        try:
            v = obj.get_editor_property(prop)
            info[prop] = str(v)
        except Exception as e:
            info[prop] = "ERR:" + str(e)[:120]
    return info

out = {}
# Inspect probe BPs and weapon actors
paths = [
 "/Game/Characters/Player/KayKit/BP_ArmedSocketTest",
 "/Game/Characters/Player/KayKit/BP_WeaponAttachProbe",
 "/Game/Characters/Player/KayKit/BP_ProbeArmed",
 "/Game/Characters/Player/KayKit/Weapons/BP_KayKitSwordActor",
 "/Game/Characters/Player/KayKit/Weapons/BP_KayKitShieldActor",
 "/Game/Characters/Player/KayKit/BP_KayKitKnight",
]
for p in paths:
    a = unreal.load_asset(p)
    info = {"asset": str(a), "class": a.get_class().get_name() if a else None}
    # parent class
    try:
        info["parent"] = str(a.get_editor_property("parent_class"))
    except Exception as e:
        info["parent"] = str(e)[:100]
    # generated class CDO components
    gc = unreal.load_object(None, p + "." + p.split("/")[-1] + "_C")
    info["gc"] = str(gc)
    if gc:
        cdo = unreal.get_default_object(gc)
        info["cdo"] = str(cdo)
        try:
            comps = cdo.get_components_by_class(unreal.ActorComponent)
            info["comps"] = []
            for c in (comps or []):
                ci = {"name": c.get_name(), "class": c.get_class().get_name()}
                if isinstance(c, unreal.StaticMeshComponent) or c.get_class().get_name() == "StaticMeshComponent":
                    try:
                        ci["mesh"] = str(c.get_editor_property("static_mesh"))
                    except Exception:
                        try: ci["mesh"] = str(c.static_mesh)
                        except Exception as e: ci["mesh"] = str(e)
                    try:
                        ci["rel"] = str(c.get_editor_property("relative_location"))
                    except Exception: pass
                if isinstance(c, unreal.SkeletalMeshComponent) or "SkeletalMesh" in c.get_class().get_name():
                    try:
                        ci["sk"] = str(c.get_editor_property("skeletal_mesh"))
                    except Exception:
                        try: ci["sk"] = str(c.skeletal_mesh)
                        except Exception as e: ci["sk"] = str(e)
                if isinstance(c, unreal.ChildActorComponent) or "ChildActor" in c.get_class().get_name():
                    try:
                        ci["child"] = str(c.get_editor_property("child_actor_class"))
                    except Exception as e:
                        ci["child"] = str(e)
                info["comps"].append(ci)
        except Exception as e:
            info["comps_err"] = str(e)
    # SCS nodes under this BP
    scs = unreal.load_object(None, p + "." + p.split("/")[-1] + "_C:SimpleConstructionScript_0")
    info["scs"] = str(scs)
    SCSNode = unreal.load_class(None, "/Script/Engine.SCS_Node")
    info["nodes"] = []
    if SCSNode:
        for obj in unreal.ObjectIterator(SCSNode):
            pn = obj.get_path_name()
            if p.split("/")[-1] in pn and "SimpleConstructionScript" in pn:
                ni = {"path": pn, "name": obj.get_name()}
                ni.update(try_props(obj, [
                    "component_class","ComponentClass","component_template","ComponentTemplate",
                    "attach_to_name","AttachToName","parent_component_or_variable_name","ParentComponentOrVariableName",
                    "parent_socket_name","ParentSocketName","b_is_parent_component_native","bIsParentComponentNative",
                    "internal_variable_name","InternalVariableName","category_name","CategoryName"
                ]))
                # template mesh if SMC
                tmpl_path = pn + "." + obj.get_name().replace("SCS_Node_", "") + "_GEN_VARIABLE"
                # also search GEN_VARIABLE children via iterator
                info["nodes"].append(ni)
    out[p] = info

# List all GEN_VARIABLE under sword/shield/probe
SMC = unreal.load_class(None, "/Script/Engine.StaticMeshComponent")
gens = []
for obj in unreal.ObjectIterator(SMC):
    pn = obj.get_path_name()
    if any(k in pn for k in ("KayKit", "Probe", "Armed", "WeaponAttach")):
        gi = {"path": pn, "name": obj.get_name()}
        try: gi["mesh"] = str(obj.get_editor_property("static_mesh"))
        except Exception as e: gi["mesh"] = str(e)[:80]
        try: gi["rel"] = str(obj.get_editor_property("relative_location"))
        except Exception as e: gi["rel"] = str(e)[:80]
        try: gi["attach"] = str(obj.get_attach_socket_name()) if hasattr(obj, "get_attach_socket_name") else None
        except Exception: pass
        gens.append(gi)
out["kaykit_smc"] = gens

# Try READ AllNodes via get_editor_property on scs even if set is protected
scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
if scs:
    for prop in ["all_nodes","AllNodes","root_nodes","RootNodes","default_scene_root_node","DefaultSceneRootNode"]:
        try:
            v = scs.get_editor_property(prop)
            out["scs_"+prop] = str(v) if not isinstance(v, (list,)) else [str(x) for x in v]
        except Exception as e:
            out["scs_"+prop] = "ERR:"+str(e)[:150]

open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs10.json","w",encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False))
print("WROTE")
for p, info in out.items():
    if p == "kaykit_smc":
        print("SMC", info)
        continue
    if not isinstance(info, dict):
        continue
    print("==", p.split("/")[-1], "parent", info.get("parent"))
    print("  comps", info.get("comps"))
    print("  nodes", [(n.get("name"), n.get("ComponentClass") or n.get("component_class"), n.get("AttachToName") or n.get("attach_to_name")) for n in info.get("nodes",[])])