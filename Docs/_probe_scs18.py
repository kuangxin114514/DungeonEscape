import unreal, traceback
LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs18.log"
lines = []
def log(m):
    lines.append(str(m))

def export_obj(obj, path):
    task = unreal.AssetExportTask()
    task.set_editor_property("object", obj)
    task.set_editor_property("filename", path)
    task.set_editor_property("automated", True)
    task.set_editor_property("prompt", False)
    task.set_editor_property("exporter", unreal.ObjectExporterT3D())
    ok = unreal.Exporter.run_asset_export_task(task)
    log("export %s => %s" % (path, ok))
    return ok

# Export SCS and SCS_Node and GEN from sword
scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/Weapons/BP_KayKitSwordActor.BP_KayKitSwordActor_C:SimpleConstructionScript_0")
node = unreal.load_object(None, "/Game/Characters/Player/KayKit/Weapons/BP_KayKitSwordActor.BP_KayKitSwordActor_C:SimpleConstructionScript_0.SCS_Node_0")
export_obj(scs, r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/sword_scs.copy")
export_obj(node, r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/sword_scs_node.copy")
# Default SMC
smc = unreal.load_object(None, "/Game/Characters/Player/KayKit/Weapons/BP_KayKitSwordActor.Default__BP_KayKitSwordActor_C:StaticMeshComponent0")
if smc:
    export_obj(smc, r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/sword_smc.copy")

# Knight SCS + orphan nodes
kscs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
export_obj(kscs, r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs.copy")
for suffix in ["SCS_Node_0", "SCS_Node_1", "SCS_Node_2", "SCS_Node_Sword", "SCS_Node_SwordMesh", "SCS_Node_Sword2"]:
    n = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0." + suffix)
    log("node %s => %s" % (suffix, n))
    if n:
        export_obj(n, r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_%s.copy" % suffix)

# Try reading AllNodes via ExportText through ObjectExporter - maybe nested in scs export

# Try EditorSkeletalMeshLibrary / set lod
# Binary approach: use Package unload + file edit
# Check if we can use ImportText on a property

# CRITICAL: try unreal.SystemLibrary / execute_console_command to run 
# "KeepSimulationChanges" or blueprint apply

# Try call_method on AssetEditorSubsystem for anything
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
for name in ["OpenEditorForAssets", "FindEditorForAsset", "GetEditedAssets", "CloseAllAssetEditors"]:
    try:
        r = aes.call_method(name)
        log("aes.%s => %s" % (name, r))
    except Exception as e:
        log("aes.%s ERR %s" % (name, e))

# Open knight BP and try to find SSCSEditor via ObjectIterator on all UObjects matching editor
# Count objects with SCSEditor in name
count = 0
scs_cls = unreal.load_class(None, "/Script/Engine.SCS_Node")
# Try get_editor_property with capitalized names that worked as protected - use call_method GetAllNodes on Blueprint instead
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
for name in ["GetSimpleConstructionScript", "GetBlueprintClass", "GeneratedClass"]:
    try:
        r = bp.call_method(name)
        log("bp.%s => %s" % (name, r))
    except Exception as e:
        log("bp.%s ERR %s" % (name, e))

# Try Import into existing package using unreal.AssetImportTask with Interchange - no

# Use TextBufferExporter or dump via print of ExportText
# In C++: SCS->GetAllNodes() is native non-UFUNCTION so not in Python

# LAST RESORT binary: read uasset, find string SCS_Node_SwordMesh, see if AllNodes refs exist
open(LOG,"w",encoding="utf-8").write("\n".join(lines))
print("WROTE", len(lines))