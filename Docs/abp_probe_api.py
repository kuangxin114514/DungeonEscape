# -*- coding: utf-8 -*-
import unreal
OUT = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\abp_probe.txt"
lines = []
def L(m):
    lines.append(str(m))

# list anim/blueprint related APIs
for n in sorted(dir(unreal)):
    ln = n.lower()
    if any(k in ln for k in ["animblue", "blendspace", "kismet", "blueprintfactory", "animgraph", "editoranim", "compile", "package"]):
        L("unreal." + n)

# AnimBlueprint props
abp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP")
props = []
for n in dir(abp):
    if n.startswith("_"):
        continue
    ln = n.lower()
    if any(k in ln for k in ["skel", "status", "graph", "page", "generat", "parent", "compile", "blueprint"]):
        props.append(n)
L("abp methods/attrs: " + ",".join(props))

# try get_editor_property common ones
for p in ["blueprint_status", "status", "parent_class", "generated_class", "skeleton_generated_class",
          "simple_construction_script", "ubergraph_pages", "function_graphs", "macro_graphs",
          "delegate_signature_graphs", "intermediate_generated_graphs", "event_graphs"]:
    try:
        v = abp.get_editor_property(p)
        L("prop {} = {}".format(p, v))
    except Exception as e:
        L("prop {} ERR {}".format(p, e))

# Factory availability
for n in ["AnimBlueprintFactory", "BlueprintFactory", "AnimBlueprint"]:
    L("hasattr {} {}".format(n, hasattr(unreal, n)))

# PackageTools methods
if hasattr(unreal, "PackageTools"):
    L("PackageTools: " + ",".join([x for x in dir(unreal.PackageTools) if not x.startswith("_")][:40]))

# EditorLoadingAndSavingUtils
if hasattr(unreal, "EditorLoadingAndSavingUtils"):
    L("ELSU: " + ",".join([x for x in dir(unreal.EditorLoadingAndSavingUtils) if not x.startswith("_")][:40]))

# AssetEditorSubsystem methods
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
L("AES: " + ",".join([x for x in dir(aes) if not x.startswith("_") and ("open" in x.lower() or "close" in x.lower() or "comp" in x.lower() or "find" in x.lower())]))

# Check ABP_KayKitKnight
for path in ["/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight",
             "/Game/Characters/Player/KayKit/ABP_KayKitKnight",
             "/Game/ThirdPersonBP/Blueprints/ThirdPerson_AnimBP"]:
    exists = unreal.EditorAssetLibrary.does_asset_exist(path)
    L("exists {} {}".format(path, exists))
    if exists:
        a = unreal.EditorAssetLibrary.load_asset(path)
        try:
            L("  class={} target={}".format(a.get_class().get_name(), a.get_editor_property("target_skeleton").get_path_name() if a.get_editor_property("target_skeleton") else None))
        except Exception as e:
            L("  ERR {}".format(e))

open(OUT, "w", encoding="utf-8").write("\\n".join(lines)+"\\n")
