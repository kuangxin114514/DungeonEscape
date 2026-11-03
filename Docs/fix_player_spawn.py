# -*- coding: utf-8 -*-
import unreal

HUB = "/Game/Maps/Hub/Map_Hub"
BP_PATH = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
GM_HUB = "/Game/Core/GameFlow/GM_Hub"
TP_GM = "/Game/ThirdPersonBP/Blueprints/ThirdPersonGameMode"
# Safe plaza spawn away from well/buildings at origin
SPAWN = unreal.Vector(400.0, 400.0, 200.0)

def log(m):
    unreal.log("SPAWNFIX: " + str(m))

def save(a):
    if a:
        unreal.EditorAssetLibrary.save_loaded_asset(a)

def set_default_pawn(gm_path):
    gm = unreal.EditorAssetLibrary.load_asset(gm_path)
    if not gm:
        log("missing gm " + gm_path)
        return
    cls = unreal.load_class(None, BP_PATH + ".BP_KayKitKnight_C")
    if not cls:
        # try generated
        try:
            cls = unreal.EditorAssetLibrary.load_blueprint_class(BP_PATH)
        except Exception as e:
            log("load_blueprint_class: " + str(e))
    if not cls:
        log("NO pawn class")
        return
    try:
        cdo = unreal.get_default_object(gm.generated_class()) if hasattr(gm, "generated_class") else None
    except Exception:
        cdo = None
    if cdo is None:
        try:
            gc = gm.get_editor_property("generated_class")
            cdo = unreal.get_default_object(gc)
        except Exception as e:
            log("cdo fail: " + str(e))
            # set via class default on Blueprint directly
            try:
                gm.set_editor_property("default_pawn_class", cls)
                save(gm)
                log("set default_pawn_class on BP asset " + gm_path)
                return
            except Exception as e2:
                log("set on bp: " + str(e2))
                return
    try:
        cdo.set_editor_property("default_pawn_class", cls)
        save(gm)
        log("set CDO default_pawn_class " + str(cls))
    except Exception as e:
        log("set CDO: " + str(e))

unreal.EditorLoadingAndSavingUtils.load_map(HUB)

# Collect PlayerStarts; do NOT touch HubKay_ / buildings
starts = []
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    name = a.get_class().get_name()
    lab = a.get_actor_label()
    if "PlayerStart" in name or "PlayerStart" in lab:
        starts.append(a)
        log("found PlayerStart label=%s loc=%s" % (lab, a.get_actor_location()))

if not starts:
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, SPAWN, unreal.Rotator(0, 0, 0))
    if ps:
        ps.set_actor_label("PlayerStart_Hub")
        starts.append(ps)
        log("spawned PlayerStart_Hub at " + str(SPAWN))
    else:
        log("FAILED spawn PlayerStart")
else:
    for ps in starts:
        ps.set_actor_location(SPAWN, False, True)
        try:
            ps.set_actor_rotation(unreal.Rotator(0, 0, 0), False)
        except Exception:
            pass
        log("moved PlayerStart to " + str(SPAWN))

# Ensure GM uses KayKit pawn
set_default_pawn(GM_HUB)
set_default_pawn(TP_GM)

# Place a preview Knight in editor viewport so user can SEE it without PIE
# (Destroy only previous preview labeled HubPlayerPreview — never buildings)
for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    if a.get_actor_label() == "HubPlayerPreview":
        unreal.EditorLevelLibrary.destroy_actor(a)
        log("removed old HubPlayerPreview")

bp_cls = unreal.load_class(None, BP_PATH + ".BP_KayKitKnight_C")
if not bp_cls:
    try:
        bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(BP_PATH)
    except Exception as e:
        log("preview class: " + str(e))
if bp_cls:
    preview = unreal.EditorLevelLibrary.spawn_actor_from_class(bp_cls, SPAWN, unreal.Rotator(0, 0, 0))
    if preview:
        preview.set_actor_label("HubPlayerPreview")
        # Disable collision on preview so PIE PlayerStart spawn won't fail if left in level
        try:
            root = preview.root_component
            if root:
                root.set_editor_property("collision_enabled", unreal.CollisionEnabled.NO_COLLISION)
        except Exception as e:
            log("preview collision: " + str(e))
        log("preview placed " + str(preview))
    else:
        log("preview spawn failed")
else:
    log("no bp class for preview")

unreal.EditorLevelLibrary.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
log("SPAWNFIX READY at " + str(SPAWN))
