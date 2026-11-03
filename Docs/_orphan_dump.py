import unreal
for path in [
 "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SwordMesh_GEN_VARIABLE",
 "/Game/Characters/Player/KayKit/BP_KayKitKnight.Default__BP_KayKitKnight_C:SwordMesh",
 "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:ShieldMesh_GEN_VARIABLE",
]:
    o=unreal.load_object(None,path)
    print(path,"=>",o)
    if o:
        try: print("  static_mesh=",o.get_editor_property("static_mesh"))
        except Exception as e: print("  err",e)
# also dump node props via T3D lines for orphans only
scs=unreal.load_object(None,"/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
task=unreal.AssetExportTask()
task.set_editor_property("object",scs)
task.set_editor_property("filename",r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_orphans.copy")
task.set_editor_property("automated",True)
task.set_editor_property("prompt",False)
task.set_editor_property("exporter",unreal.ObjectExporterT3D())
unreal.Exporter.run_asset_export_task(task)
text=open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_orphans.copy",encoding="utf-8",errors="ignore").read()
for line in text.splitlines():
    if any(k in line for k in ("Sword","Shield","AllNodes","RootNodes","StaticMesh=","InternalVariable","AttachTo","ParentComponentOrSocket","ComponentClass")):
        print(line.strip())
print("ORPHAN_DUMP_DONE")