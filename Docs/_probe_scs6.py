import unreal
LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/_scs6_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")
open(LOG, "w", encoding="utf-8").write("start\n")

scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
smc = unreal.load_class(None, "/Script/Engine.StaticMeshComponent")
log("scs=%s smc=%s" % (scs, smc))

# CreateNode variants
for args in [
    None,
    (smc,),
    (smc, "SwordMesh"),
    (smc, unreal.Name("SwordMesh")),
]:
    try:
        if args is None:
            r = scs.call_method("CreateNode")
        else:
            r = scs.call_method("CreateNode", args)
        log("CreateNode %s -> %s" % (args, r))
    except Exception as e:
        log("CreateNode %s ERR %s" % (args, e))

# set_editor_property on existing sword node
sword = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_Sword")
log("sword=%s" % sword)
if sword:
    for name, val in [
        ("ComponentClass", smc),
        ("AttachToName", "handslot_r"),
        ("ParentComponentOrVariableName", "CharacterMesh0"),
        ("bIsParentComponentNative", True),
        ("InternalVariableName", "SwordMesh"),
        ("VariableName", "SwordMesh"),
    ]:
        try:
            sword.set_editor_property(name, val)
            log("SET OK %s" % name)
        except Exception as e:
            log("SET ERR %s %s" % (name, e))

# Try creating component template as subobject of node
try:
    tmpl = unreal.new_object(smc, sword, unreal.Name("SwordMesh_GEN_VARIABLE"))
    log("tmpl %s" % tmpl)
    try:
        sword.set_editor_property("ComponentTemplate", tmpl)
        log("SET ComponentTemplate OK")
    except Exception as e:
        log("SET ComponentTemplate ERR %s" % e)
except Exception as e:
    log("new tmpl ERR %s" % e)

# Inspect via get_fullname and rename
# Try modify AllNodes via set - maybe write works?
try:
    scs.set_editor_property("AllNodes", [sword])
    log("SET AllNodes OK")
except Exception as e:
    log("SET AllNodes ERR %s" % e)

# KismetSystemLibrary / compile
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
try:
    unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
    log("saved")
except Exception as e:
    log("save ERR %s" % e)

# List all call_method possibilities - try GetAllNodes
for m in ["GetAllNodes", "GetRootNodes", "CreateNode", "RemoveNode", "ValidateNode",
          "FindSCSNode", "GetSceneRootNode", "GetAllUCSNodes", "AddNode"]:
    try:
        r = scs.call_method(m)
        log("call %s -> %s type %s" % (m, r, type(r)))
    except Exception as e:
        log("call %s ERR %s" % (m, e))

log("done")