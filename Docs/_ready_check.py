import unreal
LOG=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/ready_check.log"
L=[]
def log(m):
    L.append(str(m)); print(m)

sk=unreal.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
log("SK=%s"%sk)
for p in ["/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword","/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield"]:
    log("asset %s exist=%s"%(p, unreal.EditorAssetLibrary.does_asset_exist(p)))
for name in ["SCS_Node_SwordMesh","SCS_Node_ShieldMesh"]:
    n=unreal.load_object(None,"/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.%s"%name)
    log("orphan %s = %s"%(name,n))
    if n:
        try:
            v=n.get_editor_property("component_template")
            log("  template=%s"%v)
            if v:
                try: log("  static_mesh=%s"%v.get_editor_property("static_mesh"))
                except Exception as e: log("  sm_err=%s"%e)
        except Exception as e:
            log("  tmpl_err=%s"%e)
bp=unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp])
unreal.EditorAssetLibrary.sync_browser_to_objects(["/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword"])
gen=unreal.load_class(None,"/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
cdo=unreal.get_default_object(gen)
mesh=cdo.get_editor_property("mesh")
log("CDO_mesh=%s sk=%s"%(mesh, mesh.skeletal_mesh if mesh else None))
# socket names via mesh component
try:
    names=mesh.get_all_socket_names()
    log("mesh_sockets=%s"%[str(x) for x in names])
except Exception as e:
    log("sock_err=%s"%e)
open(LOG,"w",encoding="utf-8").write("\n".join(L))
print("READY_CHECK_DONE")