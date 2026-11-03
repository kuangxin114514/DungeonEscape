import unreal, json, traceback
LOG = []
def log(m):
    LOG.append(str(m))
    print(m)

sword_sm = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
shield_sm = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield")
log("sword_sm=%s shield_sm=%s" % (sword_sm, shield_sm))

# Existing orphan template
tmpl = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_Sword.SwordMesh_GEN_VARIABLE")
log("tmpl=%s" % tmpl)
if tmpl:
    for prop, val in [
        ("static_mesh", sword_sm),
        ("StaticMesh", sword_sm),
        ("relative_location", unreal.Vector(0,0,0)),
        ("relative_rotation", unreal.Rotator(0,0,0)),
        ("relative_scale3d", unreal.Vector(1,1,1)),
    ]:
        try:
            tmpl.set_editor_property(prop, val)
            log("SET tmpl %s OK" % prop)
        except Exception as e:
            log("SET tmpl %s ERR %s" % (prop, e))
    # also try attach methods on template - usually set at SCS level
    for m in ["set_static_mesh", "SetStaticMesh", "set_relative_location", "K2_AttachToComponent"]:
        if hasattr(tmpl, m):
            log("tmpl has %s" % m)

scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
log("scs=%s" % scs)

# Read AllNodes (protected set but maybe get works via different name)
for prop in ["all_nodes", "AllNodes"]:
    try:
        v = scs.get_editor_property(prop)
        log("GET %s -> %s len=%s" % (prop, type(v), len(v) if v is not None else None))
        if v:
            for n in v:
                log("  ALLNODE %s" % n.get_path_name())
    except Exception as e:
        log("GET %s ERR %s" % (prop, e))

# Duplicate sword actor SCS node into our SCS
donor = unreal.load_object(None, "/Game/Characters/Player/KayKit/Weapons/BP_KayKitSwordActor.BP_KayKitSwordActor_C:SimpleConstructionScript_0.SCS_Node_0")
log("donor=%s" % donor)
if donor and scs:
    try:
        # remove old orphan name conflict
        new_node = unreal.duplicate_object(donor, scs, "SCS_Node_SwordMesh")
        log("dup sword -> %s" % new_node)
    except Exception as e:
        log("dup sword ERR %s" % e)
        try:
            new_node = unreal.duplicate_object(donor, scs, "SCS_Node_SwordMesh2")
            log("dup sword2 -> %s" % new_node)
        except Exception as e2:
            log("dup sword2 ERR %s" % e2)
            new_node = None
    if new_node:
        # try set attach props
        for prop, val in [
            ("attach_to_name", "handslot_r"),
            ("AttachToName", "handslot_r"),
            ("parent_component_or_variable_name", "CharacterMesh0"),
            ("ParentComponentOrVariableName", "CharacterMesh0"),
            ("parent_socket_name", "handslot_r"),
            ("ParentSocketName", "handslot_r"),
            ("b_is_parent_component_native", True),
            ("bIsParentComponentNative", True),
        ]:
            try:
                new_node.set_editor_property(prop, val)
                log("SET node %s OK" % prop)
            except Exception as e:
                log("SET node %s ERR %s" % (prop, e))
        # find/set template mesh on duplicated node
        SMC = unreal.load_class(None, "/Script/Engine.StaticMeshComponent")
        for obj in unreal.ObjectIterator(SMC):
            pn = obj.get_path_name()
            if "SCS_Node_SwordMesh" in pn and "GEN_VARIABLE" in pn:
                log("found gen %s" % pn)
                try:
                    obj.set_editor_property("static_mesh", sword_sm)
                    log("set gen mesh OK")
                except Exception as e:
                    log("set gen mesh ERR %s" % e)

# Duplicate shield similarly
donor2 = unreal.load_object(None, "/Game/Characters/Player/KayKit/Weapons/BP_KayKitShieldActor.BP_KayKitShieldActor_C:SimpleConstructionScript_0.SCS_Node_0")
log("donor_shield=%s" % donor2)
if donor2 and scs:
    try:
        n2 = unreal.duplicate_object(donor2, scs, "SCS_Node_ShieldMesh")
        log("dup shield -> %s" % n2)
    except Exception as e:
        log("dup shield ERR %s" % e)
        n2 = None
    if n2:
        for prop, val in [
            ("AttachToName", "handslot_l"),
            ("ParentComponentOrVariableName", "CharacterMesh0"),
            ("bIsParentComponentNative", True),
        ]:
            try:
                n2.set_editor_property(prop, val)
                log("SET shield node %s OK" % prop)
            except Exception as e:
                log("SET shield node %s ERR %s" % (prop, e))

# Try compile blueprint
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
# KismetEditorUtilities missing - try other compile paths
compiled = False
for name in ["compile_blueprint", "CompileBlueprint"]:
    pass
# EditorAssetLibrary save
try:
    unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight", only_if_is_dirty=False)
    log("saved")
except Exception as e:
    log("save ERR %s" % e)

# Try unreal.BlueprintEditorLibrary via load_class
for path in [
    "/Script/BlueprintEditorLibrary.BlueprintEditorLibrary",
    "/Script/UnrealEd.KismetEditorUtilities",
    "/Script/Engine.BlueprintEditorLibrary",
]:
    cls = unreal.load_class(None, path)
    log("load_class %s -> %s" % (path, cls))

# Try get AllNodes again after dup
for prop in ["AllNodes", "all_nodes"]:
    try:
        v = scs.get_editor_property(prop)
        log("AFTER GET %s len=%s" % (prop, len(v) if v is not None else None))
        if v:
            for n in v:
                log("  %s" % n.get_path_name())
    except Exception as e:
        log("AFTER GET %s ERR %s" % (prop, e))

# List current SCS nodes under knight
SCSNode = unreal.load_class(None, "/Script/Engine.SCS_Node")
for obj in unreal.ObjectIterator(SCSNode):
    pn = obj.get_path_name()
    if "BP_KayKitKnight" in pn:
        log("NODE %s" % pn)

# Open BP editor + try focus viewport via python menus?
try:
    aes = unreal.AssetEditorSubsystem()
    aes.open_editor_for_assets([bp])
    log("opened editor")
except Exception as e:
    log("open ERR %s" % e)

# CDO comps after
gc = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
cdo = unreal.get_default_object(gc)
try:
    comps = cdo.get_components_by_class(unreal.ActorComponent)
    for c in (comps or []):
        log("CDO %s %s" % (c.get_name(), c.get_class().get_name()))
except Exception as e:
    log("cdo ERR %s" % e)

open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/_scs_dup_log.txt","w",encoding="utf-8").write("\n".join(LOG))
log("DONE")