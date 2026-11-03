import unreal, json, traceback
out = {"log": []}
def log(m):
    out["log"].append(str(m))
    print(m)

# EditorUtilityLibrary methods
eul = [n for n in dir(unreal.EditorUtilityLibrary) if not n.startswith("_")]
out["eul"] = eul
log("eul: " + ", ".join(eul))

# EditorUtilitySubsystem
eus = unreal.EditorUtilitySubsystem() if hasattr(unreal, "EditorUtilitySubsystem") else None
out["eus_dir"] = [n for n in dir(eus) if not n.startswith("_")] if eus else []

# Find ALL objects under BP_KayKitKnight package with GEN_VARIABLE or StaticMesh in name
found = []
for obj in unreal.ObjectIterator(unreal.Object):
    try:
        pn = obj.get_path_name()
    except Exception:
        continue
    if "/Game/Characters/Player/KayKit/BP_KayKitKnight" not in pn:
        continue
    if "GEN_VARIABLE" in pn or "StaticMesh" in pn or "Sword" in pn or "Shield" in pn or "CameraBoom" in pn or "FollowCamera" in pn:
        found.append(pn + " [" + obj.get_class().get_name() + "]")
out["pkg_objs"] = found
log("pkg_objs " + str(len(found)))
for f in found:
    log("  " + f)

# Try add_component_by_class on most recent preview actor
BPCls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
sword = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
shield = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield")
preview = None
best_world_idx = -1
for obj in unreal.ObjectIterator(BPCls):
    pn = obj.get_path_name()
    if "Transient.World_" in pn and "PersistentLevel" in pn:
        # extract world number
        try:
            idx = int(pn.split("World_")[1].split(":")[0])
        except Exception:
            idx = 0
        if idx >= best_world_idx:
            best_world_idx = idx
            preview = obj
log("preview=%s world=%s" % (preview, best_world_idx))

if preview:
    mesh = None
    try:
        mesh = preview.get_editor_property("mesh")
    except Exception:
        mesh = getattr(preview, "mesh", None)
    log("preview.mesh=%s" % mesh)
    # List components again
    comps = preview.get_components_by_class(unreal.ActorComponent)
    for c in comps:
        log("COMP %s %s" % (c.get_name(), c.get_class().get_name()))
    # Try add_component_by_class
    if hasattr(preview, "add_component_by_class"):
        log("has add_component_by_class")
        try:
            tr = unreal.Transform()
            smc = preview.add_component_by_class(unreal.StaticMeshComponent, False, tr, False)
            log("added %s" % smc)
        except Exception as e:
            log("add_component_by_class ERR %s" % e)
    else:
        log("NO add_component_by_class")
    # Try create_component_from_template / AddComponent
    for mname in dir(preview):
        if "component" in mname.lower() and not mname.startswith("_"):
            pass
    out["actor_comp_methods"] = [n for n in dir(preview) if "omponent" in n or "ttach" in n]

    # Reparent existing StaticMeshComponent_0 if present
    for c in comps:
        if c.get_class().get_name() == "StaticMeshComponent":
            log("fixixing existing SMC %s" % c.get_name())
            try:
                c.set_editor_property("static_mesh", sword)
                log("  mesh set sword")
            except Exception as e:
                log("  mesh ERR %s" % e)
            if mesh:
                try:
                    # attach to mesh socket
                    c.attach_to_component(mesh, "handslot_r", unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.KEEP_WORLD, False)
                    log("  attach_to_component OK")
                except Exception as e:
                    log("  attach ERR %s" % e)
                    try:
                        c.k2_attach_to_component(mesh, "handslot_r", unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.KEEP_WORLD, False)
                        log("  k2_attach OK")
                    except Exception as e2:
                        log("  k2_attach ERR %s" % e2)

# Try BlueprintFactory to create NEW character BP from scratch with native parent, 
# then use duplicate_loaded_asset from a handcrafted approach:
# Create Actor BP via factory, open it - still need SCS

# Check convert_actors signature - maybe convert StaticMeshActor to add into BP? no

# FINAL attempt: use unreal.EditorLoadingAndSavingUtils + export blueprint text
out["elsu"] = [n for n in dir(unreal.EditorLoadingAndSavingUtils) if not n.startswith("_")] if hasattr(unreal, "EditorLoadingAndSavingUtils") else []

# Save log
open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs13.json","w",encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False))
log("DONE")