import unreal
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
print("bp", bp)
print("dir bp has scs", hasattr(bp, "simple_construction_script"))
for name in ["simple_construction_script", "SimpleConstructionScript", "UberGraphFunction"]:
    try:
        v = bp.get_editor_property(name)
        print("get_editor_property", name, type(v), v)
    except Exception as e:
        print("get_editor_property", name, "ERR", e)

# try GeneratedClass CDO components
try:
    gc = bp.generated_class()
    cdo = unreal.get_default_object(gc)
    print("cdo", cdo)
    comps = cdo.get_components_by_class(unreal.ActorComponent)
    print("cdo comps", len(comps))
    for c in comps:
        print(" ", c.get_name(), type(c).__name__)
except Exception as e:
    print("cdo ERR", e)

# try AssetEditorSubsystem / open and use ToolMenus
try:
    print("has BlueprintEditorLibrary", hasattr(unreal, "BlueprintEditorLibrary"))
    print("has SubobjectDataSubsystem", hasattr(unreal, "SubobjectDataSubsystem"))
    print("has KismetEditorUtilities", hasattr(unreal, "KismetEditorUtilities"))
except Exception as e:
    print(e)

# try create USCS node class
for n in ["SCS_Node", "USCS_Node", "SimpleConstructionScript"]:
    try:
        cls = unreal.find_object(None, "/Script/Engine." + n)
        print("find", n, cls)
    except Exception as e:
        print("find", n, e)
    try:
        cls = getattr(unreal, n, None)
        print("getattr unreal", n, cls)
    except Exception as e:
        print("getattr", n, e)

# list unreal attrs containing Component or SCS or Blueprint
hits = [a for a in dir(unreal) if "SCS" in a or "Subobject" in a or "ConstructionScript" in a or a.endswith("BlueprintLibrary")]
print("hits", hits[:40])