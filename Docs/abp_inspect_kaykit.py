# -*- coding: utf-8 -*-
import unreal
OUT = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\abp_inspect.txt"
lines = []
def L(m):
    lines.append(str(m))

# Find ThirdPerson animbp
ar = unreal.AssetRegistryHelpers.get_asset_registry()
for a in ar.get_assets_by_path("/Game", recursive=True):
    n = str(a.asset_name)
    if "AnimBP" in n or "Anim_BP" in n or n.startswith("ABP_"):
        L("ASSET {} {}".format(a.package_name, n))

abp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight")
L("ABP_KayKitKnight target={}".format(abp.get_editor_property("target_skeleton").get_path_name()))

EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
BSPCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_BlendSpacePlayer")
SPCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_SequencePlayer")

count = 0
for obj in unreal.ObjectIterator(EdGraphNode):
    pn = obj.get_path_name()
    if "ABP_KayKitKnight" not in pn:
        continue
    if "Default__" in pn or "AnimPreview" in pn or "ANIM_PREVIEW" in pn.upper():
        continue
    count += 1
    cn = obj.get_class().get_name()
    extra = ""
    try:
        if cn == "AnimGraphNode_BlendSpacePlayer":
            node = obj.get_editor_property("node")
            for n in ["blend_space", "BlendSpace", "blend_space_asset"]:
                try:
                    bsa = node.get_editor_property(n)
                    if bsa:
                        extra = " bs={} skel={}".format(bsa.get_name(), bsa.get_editor_property("skeleton").get_name())
                        break
                except Exception:
                    pass
        elif cn == "AnimGraphNode_SequencePlayer":
            node = obj.get_editor_property("node")
            seq = node.get_editor_property("sequence")
            extra = " seq={}".format(seq.get_name() if seq else None)
            if seq:
                try:
                    extra += " skel={}".format(seq.get_editor_property("skeleton").get_name())
                except Exception:
                    pass
    except Exception as e:
        extra = " ERR:{}".format(e)
    L("NODE {} {}{}".format(cn, obj.get_name(), extra))
L("node_count={}".format(count))

# gen class
gen = unreal.load_object(None, "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight.ABP_KayKitKnight_C")
L("gen={}".format(gen))

# Open to compile and see log
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
aes.open_editor_for_assets([abp])
import time
time.sleep(2)
aes.close_all_editors_for_asset(abp)
unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight", only_if_is_dirty=False)
L("opened/closed ABP_KayKitKnight")

open(OUT, "w", encoding="utf-8").write("\\n".join(lines)+"\\n")
