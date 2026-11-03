import unreal, traceback
LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs20.log"
lines = []
def log(m):
    lines.append(str(m))

# List ToolMenus - try common blueprint component menu names
tm = unreal.ToolMenus.get()
candidates = []
# Brute force common patterns
prefixes = [
    "BlueprintEditor", "AssetEditor.BlueprintEditor", "SCSEditor", "Kismet",
    "LevelEditor", "Edit", "MainFrame"
]
suffixes = [
    ".ComponentTree.ContextMenu", ".ComponentTree", ".AddComponentMenu",
    ".AddComponent", ".Components", ".Viewport.ContextMenu",
    ".ToolBar", ".Menu", ".Debug.ToolBar"
]
for p in prefixes:
    for s in suffixes:
        name = p + s
        try:
            if tm.is_menu_registered(name):
                candidates.append(name)
                log("REGISTERED " + name)
        except Exception as e:
            pass

# Also try exact known UE4 menu names from source
known = [
    "BlueprintEditor.ComponentTree.AddComponentPopup",
    "BlueprintEditor.ComponentTree.AddComponentMenu",
    "BlueprintEditor.AddComponentPopup",
    "SCSEditor.AddComponentPopup",
    "SCSEditor.ComponentTree.ContextMenu",
    "BlueprintEditor.ComponentTree.ContextMenu",
    "AssetEditor.BlueprintEditor.ComponentTree.ContextMenu",
    "BlueprintEditor.Tools",
]
for name in known:
    try:
        reg = tm.is_menu_registered(name)
        menu = tm.find_menu(name)
        log("known %s reg=%s menu=%s" % (name, reg, menu))
    except Exception as e:
        log("known %s ERR %s" % (name, e))

# ImportSubsystem
imps = unreal.get_editor_subsystem(unreal.ImportSubsystem) if hasattr(unreal, "get_editor_subsystem") else None
log("ImportSubsystem %s" % imps)
if imps:
    log("imps dir %s" % [n for n in dir(imps) if not n.startswith("_")])

# Save BP to persist in-memory orphans, compile
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
# Ensure sword mesh on template
gen = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_SwordMesh.SwordMesh_GEN_VARIABLE")
log("gen=%s" % gen)
if gen:
    sword = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
    try:
        gen.set_editor_property("static_mesh", sword)
        log("mesh set")
    except Exception as e:
        log("mesh ERR %s" % e)

# Create Shield orphan similarly
scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
shield_node = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_ShieldMesh")
if not shield_node:
    shield_node = unreal.new_object(unreal.load_class(None, "/Script/Engine.SCS_Node"), scs, "SCS_Node_ShieldMesh")
    log("created shield node %s" % shield_node)
# Create template SMC under shield node
shield_gen = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_ShieldMesh.ShieldMesh_GEN_VARIABLE")
if not shield_gen:
    shield_gen = unreal.new_object(unreal.StaticMeshComponent, shield_node, "ShieldMesh_GEN_VARIABLE")
    log("created shield gen %s" % shield_gen)
if shield_gen:
    shield = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield")
    try:
        shield_gen.set_editor_property("static_mesh", shield)
        log("shield mesh set")
    except Exception as e:
        log("shield mesh ERR %s" % e)

# Open BP editor focused on viewport
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
aes.open_editor_for_assets([bp])
log("opened editor")

# Save
ok = unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
log("save %s" % ok)

# Re-export SCS to see if AllNodes changed (won't) and orphans persisted
task = unreal.AssetExportTask()
task.set_editor_property("object", scs)
task.set_editor_property("filename", r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_after_save.copy")
task.set_editor_property("automated", True)
task.set_editor_property("prompt", False)
task.set_editor_property("exporter", unreal.ObjectExporterT3D())
unreal.Exporter.run_asset_export_task(task)
log("re-exported")

open(LOG,"w",encoding="utf-8").write("\n".join(lines))
print("WROTE", len(lines))