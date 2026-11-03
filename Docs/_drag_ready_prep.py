import unreal
LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/drag_ready_prep.log"
lines = []
def log(m):
    lines.append(str(m)); print(m)

sk = unreal.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
log("SK=%s verts~%s" % (sk, sk.get_num_vertices(0) if sk and hasattr(sk,"get_num_vertices") else "?"))
# material/slot names hint weapons?
try:
    n = sk.get_num_sections(0) if hasattr(sk, "get_num_sections") else None
    log("sections=%s" % n)
except Exception as e:
    log("sec ERR %s" % e)
# sockets exist
cdo = unreal.get_default_object(unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C"))
mesh = cdo.get_editor_property("mesh")
for s in ["handslot_r","handslot_l"]:
    try:
        log("%s exists=%s" % (s, mesh.does_socket_exist(s)))
    except Exception as e:
        log("%s ERR %s" % (s, e))
# assets
for p in ["/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword","/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield"]:
    log("%s exists=%s" % (p, unreal.EditorAssetLibrary.does_asset_exist(p)))
# Open BP editor
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
aes.open_editor_for_assets([bp])
log("BP editor opened")
# Sync CB to sword for Add Component common list
sword = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
unreal.EditorAssetLibrary.sync_browser_to_objects(["/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword"])
log("CB synced to sword")
# Focus: try set viewport tab - can't easily; user Viewport should be default
open(LOG,"w",encoding="utf-8").write("\n".join(lines))
log("DONE")