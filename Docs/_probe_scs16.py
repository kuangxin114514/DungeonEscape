import unreal, traceback
LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs16.log"
lines = []
def log(m):
    lines.append(str(m))

# Asset editor APIs
for n in sorted(dir(unreal)):
    if any(k in n.lower() for k in ("asseteditor", "blueprinteditor", "toolmenu", "toolkit", "kismet", "subobject", "scs")):
        lines.append("unreal." + n)

log("has AssetEditorSubsystem %s" % hasattr(unreal, "AssetEditorSubsystem"))
log("has AssetEditorToolkitMenus %s" % hasattr(unreal, "AssetEditorToolkitMenus"))

# Try open editor on knight and find toolkit objects
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
try:
    unreal.AssetToolsHelpers.get_asset_tools().open_editor_for_assets([bp])
    log("open_editor OK")
except Exception as e:
    log("open_editor ERR %s" % e)

# Search for BlueprintEditor objects in memory
for cls_name in [
    "/Script/Kismet.BlueprintEditor",
    "/Script/Kismet.SSCSEditor",
    "/Script/Kismet.SCSEditor",
    "/Script/UnrealEd.SCSEditor",
    "/Script/Kismet.SComponentClassList",
]:
    cls = unreal.load_class(None, cls_name)
    log("cls %s => %s" % (cls_name, cls))

# Iterate all classes with SCS or BlueprintEditor in name - limited
# Use EditorUtilitySubsystem
if hasattr(unreal, "EditorUtilitySubsystem"):
    eus = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem) if hasattr(unreal, "get_editor_subsystem") else unreal.EditorUtilitySubsystem()
    log("eus=%s dir=%s" % (eus, [n for n in dir(eus) if not n.startswith("_")]))

# Export knight BP
export_path = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/BP_KayKitKnight_export"
try:
    task = unreal.AssetExportTask()
    task.set_editor_property("object", bp)
    task.set_editor_property("filename", export_path + ".copy")
    task.set_editor_property("automated", True)
    task.set_editor_property("prompt", False)
    task.set_editor_property("replace_identical", True)
    # Find exporters
    exporters = []
    for n in dir(unreal):
        if "Export" in n and "Factory" not in n:
            exporters.append(n)
    log("export-ish: %s" % exporters[:40])
    ok = unreal.Exporter.run_asset_export_task(task) if hasattr(unreal, "Exporter") else None
    log("run_asset_export_task => %s" % ok)
except Exception as e:
    log("export ERR %s" % traceback.format_exc())

# Try duplicate_asset of ProbeSMA as starting point - user wants knight though
# Alternative: use Construction Script by spawning components via existing AnimBP?
# Check skeleton sockets for PreviewAsset property we can set (editor preview mesh on socket)
sk = unreal.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
skel = sk.get_editor_property("skeleton") if sk else None
log("skel=%s" % skel)
if skel:
    log("skel dir socket: %s" % [n for n in dir(skel) if "socket" in n.lower() or "Socket" in n])
    # Try get_socket_by_name / sockets array
    for p in ["sockets", "Sockets", "preview_attached_assets", "PreviewAttachedAssetContainer"]:
        try:
            log("skel.%s = %s" % (p, skel.get_editor_property(p)))
        except Exception as e:
            log("skel.%s ERR %s" % (p, e))

# Preview attached assets on skeletal mesh
if sk:
    for p in ["preview_attached_assets", "PreviewAttachedAssetContainer", "socket_maps"]:
        try:
            log("sk.%s = %s" % (p, sk.get_editor_property(p)))
        except Exception as e:
            log("sk.%s ERR %s" % (p, e))
    log("sk dir attach/socket/preview: %s" % [n for n in dir(sk) if any(k in n.lower() for k in ("socket","attach","preview"))])

# Compile blueprint library
for n in ["EditorAssetLibrary", "BlueprintEditorLibrary"]:
    pass

# Try: use Level Editor spawn knight, add instance components via new_object+register, then
# "Create Blueprint from Selected Actor (With Other Actors)" console
# First check console commands related
log("trying instance component on spawned actor in CURRENT Map_Hub - will destroy after")
try:
    cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
    loc = unreal.Vector(0, 0, 50000)  # far away so not near buildings
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc)
    log("spawned %s" % actor)
    if actor:
        mesh = actor.get_editor_property("mesh")
        sword = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
        shield = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield")
        # Create components as subobjects of actor
        smc = unreal.new_object(unreal.StaticMeshComponent, actor, "SwordMesh")
        log("new smc %s" % smc)
        smc.set_editor_property("static_mesh", sword)
        try:
            actor.add_instance_component(smc)
            log("add_instance_component OK")
        except Exception as e:
            log("add_instance_component ERR %s" % e)
        try:
            smc.register_component()
            log("register OK")
        except Exception as e:
            log("register ERR %s" % e)
        try:
            smc.attach_to_component(mesh, "handslot_r", unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.KEEP_WORLD, False)
            log("attach OK")
        except Exception as e:
            log("attach ERR %s" % e)
        # list comps
        for c in actor.get_components_by_class(unreal.ActorComponent) or []:
            if "Sword" in c.get_name() or "Shield" in c.get_name() or "StaticMesh" in c.get_name():
                log("ACTORCOMP %s %s" % (c.get_name(), c.get_class().get_name()))
        # Try create blueprint from actor via AssetTools
        # Cleanup - destroy so Map_Hub untouched
        unreal.EditorLevelLibrary.destroy_actor(actor)
        log("destroyed temp actor")
        # Don't save level!
except Exception as e:
    log("spawn path ERR %s" % traceback.format_exc())

open(LOG,"w",encoding="utf-8").write("\n".join(lines))
print("WROTE", len(lines))