import unreal
LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/drag_verify.log"
lines = []
def log(m):
    lines.append(str(m)); print(m)
scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
task = unreal.AssetExportTask()
task.set_editor_property("object", scs)
task.set_editor_property("filename", r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_verify.copy")
task.set_editor_property("automated", True)
task.set_editor_property("prompt", False)
task.set_editor_property("exporter", unreal.ObjectExporterT3D())
unreal.Exporter.run_asset_export_task(task)
text = open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_verify.copy",encoding="utf-8",errors="ignore").read()
for line in text.splitlines():
    if any(k in line for k in ("AllNodes","RootNodes","Sword","Shield","AttachTo","InternalVariable","ParentComponent","StaticMesh=","ComponentClass")):
        log(line.strip())
# CDO comps
gen = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
cdo = unreal.get_default_object(gen)
for c in cdo.get_components_by_class(unreal.StaticMeshComponent) or []:
    try:
        sm = c.get_editor_property("static_mesh")
    except Exception:
        sm = None
    log("CDO_SMC %s mesh=%s" % (c.get_name(), sm))
# preview actor
BPCls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
best=None; besti=-1
for obj in unreal.ObjectIterator(BPCls):
    pn = unreal.Object.get_path_name(obj)
    if "Transient.World_" in pn and "PersistentLevel" in pn:
        try: i=int(pn.split("World_")[1].split(":")[0])
        except: i=0
        if i>=besti: besti=i; best=obj
if best:
    for c in best.get_components_by_class(unreal.StaticMeshComponent) or []:
        try: sm=c.get_editor_property("static_mesh")
        except: sm=None
        parent=c.get_attach_parent().get_name() if c.get_attach_parent() else None
        sock=c.get_attach_socket_name() if hasattr(c,"get_attach_socket_name") else None
        log("PREV %s mesh=%s parent=%s sock=%s" % (c.get_name(), sm, parent, sock))
ok = unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
log("save=%s" % ok)
open(LOG,"w",encoding="utf-8").write("\n".join(lines))