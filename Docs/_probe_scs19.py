import unreal, traceback, os
LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs19.log"
lines = []
def log(m):
    lines.append(str(m))

hits = [n for n in dir(unreal) if "mport" in n or "paste" in n.lower() or "Paste" in n or "TextBuffer" in n]
log("hits: %s" % hits)

# Try import .copy as new asset via AssetImportTask
for factory_name in ["ReimportDataTableFactory", "Factoy", "SceneImportFactory", "ActorFactory"]:
    pass
factories = [n for n in dir(unreal) if n.endswith("Factory") and ("Import" in n or "Object" in n or "Text" in n or "Copy" in n or "Blueprint" in n)]
log("factories: %s" % factories[:50])

# Build modified SCS T3D with SwordMesh properly configured + ShieldMesh
sword_guid = "A1B2C3D44E5F67890123456789ABCDEF"
shield_guid = "B2C3D4E55F67890123456789ABCDEF01"

scs_t3d = r'''Begin Object Class=/Script/Engine.SimpleConstructionScript Name="SimpleConstructionScript_0"
   Begin Object Class=/Script/Engine.SCS_Node Name="SCS_Node_0"
   End Object
   Begin Object Class=/Script/Engine.SCS_Node Name="SCS_Node_2"
   End Object
   Begin Object Class=/Script/Engine.SCS_Node Name="SCS_Node_1"
   End Object
   Begin Object Class=/Script/Engine.SCS_Node Name="SCS_Node_SwordMesh"
      Begin Object Class=/Script/Engine.StaticMeshComponent Name="SwordMesh_GEN_VARIABLE"
      End Object
   End Object
   Begin Object Class=/Script/Engine.SCS_Node Name="SCS_Node_ShieldMesh"
      Begin Object Class=/Script/Engine.StaticMeshComponent Name="ShieldMesh_GEN_VARIABLE"
      End Object
   End Object
   Begin Object Name="SCS_Node_0"
      ComponentClass=Class'"/Script/Engine.SceneComponent"'
      ComponentTemplate=SceneComponent'"BP_KayKitKnight_C:SceneComponent_0"'
      CategoryName=NSLOCTEXT("", "B634704C4B8C2CD03940B9A1BCF61B28", "MyCharacter")
      VariableGuid=56BC9799C494E6E6321D42957D5EB316
      InternalVariableName="DefaultSceneRoot"
   End Object
   Begin Object Name="SCS_Node_2"
      ComponentClass=Class'"/Script/Engine.CameraComponent"'
      ComponentTemplate=CameraComponent'"BP_KayKitKnight_C:CameraComponent_0__CCE3C0B4"'
      CategoryName=NSLOCTEXT("", "657458004C703B3C725FFD887BD4726F", "MyCharacter")
      AttachToName="SpringEndpoint"
      VariableGuid=59532DB3100DA6837C332919BA93A9DE
      InternalVariableName="FollowCamera"
   End Object
   Begin Object Name="SCS_Node_1"
      ComponentClass=Class'"/Script/Engine.SpringArmComponent"'
      ComponentTemplate=SpringArmComponent'"BP_KayKitKnight_C:SpringArmComponent_0__A9892D03"'
      CategoryName=NSLOCTEXT("", "85FB7D4443CDB51853118E922B0AC7BB", "MyCharacter")
      ParentComponentOrVariableName="CollisionCylinder"
      bIsParentComponentNative=True
      ChildNodes(0)=SCS_Node'"BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_2"'
      VariableGuid=9FAECF1AC667795A865E0E9F2ED3478F
      InternalVariableName="CameraBoom"
   End Object
   Begin Object Name="SCS_Node_SwordMesh"
      Begin Object Name="SwordMesh_GEN_VARIABLE"
         StaticMesh=StaticMesh'"/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword.SM_KayKitSword"'
      End Object
      ComponentClass=Class'"/Script/Engine.StaticMeshComponent"'
      ComponentTemplate=StaticMeshComponent'"BP_KayKitKnight_C:SwordMesh_GEN_VARIABLE"'
      ParentComponentOrVariableName="Mesh"
      bIsParentComponentNative=True
      AttachToName="handslot_r"
      VariableGuid=A1B2C3D44E5F67890123456789ABCDEF
      InternalVariableName="SwordMesh"
   End Object
   Begin Object Name="SCS_Node_ShieldMesh"
      Begin Object Name="ShieldMesh_GEN_VARIABLE"
         StaticMesh=StaticMesh'"/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield.SM_KayKitShield"'
      End Object
      ComponentClass=Class'"/Script/Engine.StaticMeshComponent"'
      ComponentTemplate=StaticMeshComponent'"BP_KayKitKnight_C:ShieldMesh_GEN_VARIABLE"'
      ParentComponentOrVariableName="Mesh"
      bIsParentComponentNative=True
      AttachToName="handslot_l"
      VariableGuid=B2C3D4E55F67890123456789ABCDEF01
      InternalVariableName="ShieldMesh"
   End Object
   RootNodes(0)=SCS_Node'"SCS_Node_1"'
   RootNodes(1)=SCS_Node'"SCS_Node_SwordMesh"'
   RootNodes(2)=SCS_Node'"SCS_Node_ShieldMesh"'
   AllNodes(0)=SCS_Node'"SCS_Node_1"'
   AllNodes(1)=SCS_Node'"SCS_Node_2"'
   AllNodes(2)=SCS_Node'"SCS_Node_SwordMesh"'
   AllNodes(3)=SCS_Node'"SCS_Node_ShieldMesh"'
   DefaultSceneRootNode=SCS_Node'"SCS_Node_0"'
End Object
'''
path = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_armed.copy"
open(path,"w",encoding="utf-8").write(scs_t3d)
log("wrote " + path)

# Try various import methods onto existing SCS
scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")

# Method: ImportObjectProperties via call_method
for m in ["ImportCustomProperties", "ImportObjectProperties", "ExportCustomProperties"]:
    try:
        r = scs.call_method(m, (scs_t3d,))
        log("%s => %s" % (m, r))
    except Exception as e:
        log("%s ERR %s" % (m, e))

# Try paste through EditorEngine
engine = unreal.EditorLevelLibrary.get_editor_world().get_outer() if False else None
# get UnrealEdEngine
try:
    eng = unreal.EditorLevelLibrary  # 
    # find engine object
    for obj in unreal.ObjectIterator(unreal.UnrealEditorSubsystem) if hasattr(unreal, "UnrealEditorSubsystem") else []:
        log("ues %s" % obj)
except Exception as e:
    log("eng ERR %s" % e)

# AssetImportTask
try:
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", path)
    task.set_editor_property("destination_path", "/Game/Characters/Player/KayKit")
    task.set_editor_property("destination_name", "BP_KayKitKnight_SCSImport")
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    log("import task done results=%s" % task.get_editor_property("result"))
except Exception as e:
    log("import task ERR %s" % traceback.format_exc())

# Try using ObjectFactory / new object from text - check EditorLoadingAndSavingUtils
log("elsu: %s" % [n for n in dir(unreal.EditorLoadingAndSavingUtils) if not n.startswith("_")])

# CRITICAL trick used in community: write to clipboard and invoke Paste
# Or use unreal.SystemLibrary.execute_console_command with MACRO

# Try: save package, then use file-level approach with reload
# First, dump raw property using exporter of JUST the AllNodes by modifying in-memory via
# creating a DUPLICATE SCS as new asset?

# Use Blueprint diff / merge

# Try set_editor_property on InternalVariableName of SwordMesh node - some props might be writable
node = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_SwordMesh")
log("node=%s" % node)
for p,v in [
    ("InternalVariableName", "SwordMesh"),
    ("internal_variable_name", "SwordMesh"),
    ("AttachToName", "handslot_r"),
    ("attach_to_name", "handslot_r"),
    ("ParentComponentOrVariableName", "Mesh"),
    ("parent_component_or_variable_name", "Mesh"),
    ("bIsParentComponentNative", True),
    ("ComponentClass", unreal.StaticMeshComponent.static_class()),
    ("component_class", unreal.StaticMeshComponent.static_class()),
]:
    try:
        node.set_editor_property(p, v)
        log("SET %s OK" % p)
    except Exception as e:
        log("SET %s ERR %s" % (p, e))
    try:
        got = node.get_editor_property(p)
        log("GET %s = %s" % (p, got))
    except Exception as e:
        log("GET %s ERR %s" % (p, e))

open(LOG,"w",encoding="utf-8").write("\n".join(lines))
print("WROTE", len(lines))