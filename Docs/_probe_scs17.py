import unreal, traceback
LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs17.log"
lines = []
def log(m):
    lines.append(str(m))

aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
log("aes=%s" % aes)
log("aes methods: %s" % [n for n in dir(aes) if not n.startswith("_")])

# Search unreal for CreateBlueprint / FromActor / AddComponent
hits = [n for n in dir(unreal) if any(k in n.lower() for k in ("createblueprint","fromactor","addcomponent","components_to_blueprint","instancecomponent"))]
log("hits: %s" % hits)

# ToolMenus - list and find Add Component
tm = unreal.ToolMenus.get()
log("tm=%s" % tm)
# Try find menus related to blueprint component
for menu_name in [
    "BlueprintEditor.ComponentTree.AddComponent",
    "BlueprintEditor.AddComponent",
    "SCSEditor.AddComponent",
    "BlueprintEditor.ComponentTree.ContextMenu",
    "AssetEditor.BlueprintEditor.ToolBar",
]:
    try:
        menu = tm.find_menu(menu_name)
        log("menu %s => %s" % (menu_name, menu))
    except Exception as e:
        log("menu %s ERR %s" % (menu_name, e))

# List all registered menu names containing Component or Blueprint
try:
    # get_names might not exist
    log("tm dir: %s" % [n for n in dir(tm) if not n.startswith("_")])
except Exception as e:
    log(str(e))

# Spawn actor far away, add sword+shield via new_object, try CreateBlueprint via various paths
cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
loc = unreal.Vector(0, 0, 80000)
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc)
log("spawned %s" % actor)
sword = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
shield = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield")
mesh = actor.get_editor_property("mesh")

def add_smc(actor, name, sm, socket):
    smc = unreal.new_object(unreal.StaticMeshComponent, actor, name)
    smc.set_editor_property("static_mesh", sm)
    try:
        smc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    except Exception:
        pass
    smc.attach_to_component(mesh, socket, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.KEEP_WORLD, False)
    # Finish by setting bCreatedByConstructionScript or instance flags?
    try:
        smc.set_editor_property("creation_method", unreal.ComponentCreationMethod.INSTANCE)
    except Exception as e:
        log("creation_method ERR %s" % e)
    return smc

smc_s = add_smc(actor, "SwordMesh", sword, "handslot_r")
smc_h = add_smc(actor, "ShieldMesh", shield, "handslot_l")
log("sword=%s shield=%s" % (smc_s, smc_h))
for c in actor.get_components_by_class(unreal.StaticMeshComponent) or []:
    log("SMC %s mesh=%s parent=%s sock=%s" % (
        c.get_name(),
        c.get_editor_property("static_mesh"),
        c.get_attach_parent().get_name() if c.get_attach_parent() else None,
        c.get_attach_socket_name() if hasattr(c, "get_attach_socket_name") else None
    ))

# Select actor
unreal.EditorLevelLibrary.set_selected_level_actors([actor])

# Try AssetTools create blueprint - look at methods
tools = unreal.AssetToolsHelpers.get_asset_tools()
log("tools methods with blue/actor/create: %s" % [n for n in dir(tools) if any(k in n.lower() for k in ("blue","actor","create","harvest","instance"))])

# Try call_method on aes
for m in ["open_editor_for_assets", "close_all_editors_for_asset", "find_editor_for_asset"]:
    if hasattr(aes, m):
        log("aes has %s" % m)

# Cleanup - destroy without saving map
unreal.EditorLevelLibrary.destroy_actor(actor)
log("destroyed")

# Export sword actor as T3D for SCS template reference
sword_bp = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/BP_KayKitSwordActor")
try:
    task = unreal.AssetExportTask()
    task.set_editor_property("object", sword_bp)
    task.set_editor_property("filename", r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/BP_KayKitSwordActor_export.copy")
    task.set_editor_property("automated", True)
    task.set_editor_property("prompt", False)
    # Use ObjectExporterT3D
    exp = unreal.ObjectExporterT3D()
    task.set_editor_property("exporter", exp)
    ok = unreal.Exporter.run_asset_export_task(task)
    log("sword export %s" % ok)
except Exception as e:
    log("sword export ERR %s" % traceback.format_exc())

open(LOG,"w",encoding="utf-8").write("\n".join(lines))
print("WROTE", len(lines))