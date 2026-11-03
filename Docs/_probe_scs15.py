import unreal, json, traceback
LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs15.log"
lines = []
def log(m):
    s = str(m)
    lines.append(s)
    print(s)

# 1) Find KismetEditorUtilities
for path in [
    "/Script/UnrealEd.Default__KismetEditorUtilities",
    "/Script/UnrealEd.KismetEditorUtilities",
    "/Script/Blutility.Default__EditorUtilityLibrary",
]:
    o = unreal.load_object(None, path)
    log("load %s => %s" % (path, o))

# Check if class exists
for cname in ["KismetEditorUtilities", "BlueprintEditorLibrary", "SubobjectDataSubsystem", "BlueprintEditorUtils"]:
    log("hasattr unreal.%s = %s" % (cname, hasattr(unreal, cname)))
    cls = unreal.load_class(None, "/Script/UnrealEd." + cname)
    if not cls:
        cls = unreal.load_class(None, "/Script/BlueprintEditorLibrary." + cname)
    if not cls:
        cls = unreal.load_class(None, "/Script/Engine." + cname)
    log("  load_class %s => %s" % (cname, cls))

# 2) Knight SCS - try AddNode / GetAllNodes via call_method
scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
log("scs=%s" % scs)
log("scs dir node/add: %s" % [n for n in dir(scs) if any(k in n.lower() for k in ("node","add","create","all","root","child"))])

# List ALL call_method capable - try common USCS API names from source
api_names = [
    "CreateNode", "CreateNodeAndRenameComponent", "AddNode", "AddNodeAndValidate",
    "RemoveNode", "GetAllNodes", "GetRootNodes", "GetSceneRootNodes",
    "FindSceneNodeForVariable", "GetComponentEditorActorInstance",
    "ValidateNode", "ValidateSceneRootNodes",
]
for name in api_names:
    try:
        # probe with no args first for getters
        if name.startswith("Get") or name.startswith("Validate"):
            r = scs.call_method(name)
            log("%s() => %s" % (name, r))
        else:
            r = scs.call_method(name, (unreal.StaticMeshComponent.static_class(),))
            log("%s(SMC) => %s" % (name, r))
    except Exception as e:
        log("%s ERR %s" % (name, e))

# CreateNode with name
try:
    r = scs.call_method("CreateNode", (unreal.StaticMeshComponent.static_class(), "SwordMesh2"))
    log("CreateNode(SMC,name) => %s" % r)
except Exception as e:
    log("CreateNode named ERR %s" % e)

# 3) new_object SCS_Node then AddNode
try:
    node = unreal.new_object(unreal.load_class(None, "/Script/Engine.SCS_Node"), scs, "SCS_Node_Sword2")
    log("new node %s" % node)
    for m in ["AddNode", "AddNodeAndValidate"]:
        try:
            r = scs.call_method(m, (node,))
            log("%s(node) => %s" % (m, r))
        except Exception as e:
            log("%s(node) ERR %s" % (m, e))
except Exception as e:
    log("new_object node ERR %s" % traceback.format_exc())

# 4) Try ChildActorComponent CreateNode
try:
    r = scs.call_method("CreateNode", (unreal.ChildActorComponent.static_class(), "SwordActor"))
    log("CreateNode ChildActor => %s" % r)
except Exception as e:
    log("CreateNode ChildActor ERR %s" % e)

# 5) Factory create SMA BP + inspect + reparent using ParentClass property variants
factory = unreal.BlueprintFactory()
factory.set_editor_property("ParentClass", unreal.StaticMeshActor)
tools = unreal.AssetToolsHelpers.get_asset_tools()
dest = "/Game/Characters/Player/KayKit/Weapons/BP_ProbeSMA"
if unreal.EditorAssetLibrary.does_asset_exist(dest):
    unreal.EditorAssetLibrary.delete_asset(dest)
# create_asset(asset_name, package_path, asset_class, factory)
new_bp = tools.create_asset("BP_ProbeSMA", "/Game/Characters/Player/KayKit/Weapons", unreal.Blueprint, factory)
log("new_bp=%s" % new_bp)
if new_bp:
    unreal.EditorAssetLibrary.save_asset(dest)
    # find parent class prop
    for p in ["parent_class", "ParentClass", "generated_class", "GeneratedClass", "skeleton_generated_class"]:
        try:
            log("bp.%s = %s" % (p, new_bp.get_editor_property(p)))
        except Exception as e:
            log("bp.%s ERR %s" % (p, e))
    # Set StaticMesh on Default CDO
    gen = unreal.load_class(None, dest + ".BP_ProbeSMA_C")
    log("gen=%s" % gen)
    if gen:
        cdo = unreal.get_default_object(gen)
        log("cdo=%s" % cdo)
        # StaticMeshActor has StaticMeshComponent
        try:
            smc = cdo.get_component_by_class(unreal.StaticMeshComponent)
            log("smc=%s" % smc)
            sword = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
            if smc and sword:
                smc.set_editor_property("static_mesh", sword)
                log("set sword on CDO smc")
        except Exception as e:
            log("cdo smc ERR %s" % e)
    # Reparent: set ParentClass to Character / KayKitKnight
    parent = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
    for p in ["parent_class", "ParentClass"]:
        try:
            new_bp.set_editor_property(p, parent)
            log("set %s OK" % p)
        except Exception as e:
            log("set %s ERR %s" % (p, e))
    unreal.EditorAssetLibrary.save_asset(dest)
    gen2 = unreal.load_class(None, dest + ".BP_ProbeSMA_C")
    log("gen2=%s" % gen2)
    if gen2:
        cdo2 = unreal.get_default_object(gen2)
        try:
            comps = cdo2.get_components_by_class(unreal.ActorComponent)
            for c in (comps or []):
                log("CDO2 %s [%s]" % (c.get_name(), c.get_class().get_name()))
        except Exception as e:
            log("cdo2 ERR %s" % e)

open(LOG, "w", encoding="utf-8").write("\n".join(lines))
log("WROTE " + LOG)