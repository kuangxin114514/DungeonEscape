# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
import time

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t229b_wire_mont.txt"
lines = []
def L(m):
    s = str(m); lines.append(s)
    try: unreal.log("T229b: " + s)
    except Exception: print(s)
def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines)+"\n")

ABP = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
CHOP = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop_Rig"
MONT = "/Game/Characters/Player/KayKit/Animations/AM_KayKit_1H_Chop"

def dump_pins(node, label):
    L("--- pins %s %s ---" % (label, node.get_name() if node else None))
    if node is None:
        return
    # try many ways to get pins
    for attr in ("pins", "Pins", "node_pins"):
        try:
            pins = node.get_editor_property(attr)
            L("  prop %s -> %s" % (attr, pins))
        except Exception as e:
            L("  prop %s ERR %s" % (attr, e))
    for meth in ("get_pins", "GetPins", "get_all_pins"):
        fn = getattr(node, meth, None)
        if fn:
            try:
                L("  meth %s -> %s" % (meth, fn()))
            except Exception as e:
                L("  meth %s ERR %s" % (meth, e))
    # iterate pin objects under path
    PinCls = unreal.load_class(None, "/Script/Engine.EdGraphPin")
    # EdGraphPin is often not a UObject in older UE - try EdGraphPin_Type
    for cls_path in (
        "/Script/Engine.EdGraphPin",
        "/Script/BlueprintGraph.EdGraphPin",
    ):
        c = unreal.load_class(None, cls_path)
        L("  load %s -> %s" % (cls_path, c))
    # inspect node methods
    names = [n for n in dir(node) if "pin" in n.lower() or "link" in n.lower() or "wire" in n.lower()]
    L("  dir pin/link: %s" % names[:40])

def find_nodes():
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    root = sm = slot = None
    for obj in unreal.ObjectIterator(EdGraphNode):
        pn = obj.get_path_name()
        if "ABP_KayKitLocomotion" not in pn or "Default__" in pn or "AnimPreview" in pn:
            continue
        cn = obj.get_class().get_name()
        if cn == "AnimGraphNode_Root":
            root = obj
        elif cn == "AnimGraphNode_StateMachine":
            sm = obj
        elif cn == "AnimGraphNode_Slot":
            slot = obj
    return root, sm, slot

def try_wire():
    root, sm, slot = find_nodes()
    L("root=%s sm=%s slot=%s" % (root, sm, slot))
    dump_pins(root, "root")
    dump_pins(sm, "sm")
    dump_pins(slot, "slot")
    # Try AnimationGraphSchema
    for path in (
        "/Script/AnimGraph.AnimationGraphSchema",
        "/Script/AnimGraph.AnimationGraphSchema_Base",
        "/Script/BlueprintGraph.EdGraphSchema_K2",
    ):
        cls = unreal.load_class(None, path)
        L("schema class %s -> %s" % (path, cls))
        if cls:
            try:
                cdo = unreal.get_default_object(cls)
                meths = [n for n in dir(cdo) if "link" in n.lower() or "create" in n.lower() or "connect" in n.lower()]
                L("  cdo meths %s" % meths[:50])
            except Exception as e:
                L("  cdo ERR %s" % e)
    # Try unreal.EditorGraph / GraphEditor
    for name in ("EdGraphSchema_K2", "AnimationGraphSchema", "BlueprintEditorLibrary", "AnimBlueprintExtensionLibrary"):
        L("hasattr unreal.%s %s" % (name, hasattr(unreal, name)))

def try_montage_v2():
    chop = unreal.EditorAssetLibrary.load_asset(CHOP)
    sk = chop.get_editor_property("skeleton")
    L("chop sk=%s" % (sk.get_path_name() if sk else None))
    # Inspect factory properties
    factory = unreal.AnimMontageFactory()
    props = []
    for n in dir(factory):
        if n.startswith("_"):
            continue
        props.append(n)
    L("factory dir sample: %s" % [p for p in props if "anim" in p.lower() or "skel" in p.lower() or "source" in p.lower() or "target" in p.lower()])
    # try get_editor_property on known names via try
    for pn in ("TargetSkeleton", "target_skeleton", "Skeleton", "skeleton", "SourceAnimation", "source_animation", "PreviewSkeletalMesh"):
        try:
            v = factory.get_editor_property(pn)
            L("factory.get %s = %s" % (pn, v))
        except Exception as e:
            L("factory.get %s ERR %s" % (pn, e))
    # Search asset registry for any AnimMontage to duplicate
    try:
        reg = unreal.AssetRegistryHelpers.get_asset_registry()
        ar_filter = unreal.ARFilter(class_names=["AnimMontage"], recursive_paths=True, package_paths=["/Game", "/Engine"])
        assets = reg.get_assets(ar_filter)
        L("AnimMontage assets found=%d" % len(assets))
        for a in list(assets)[:15]:
            try:
                L("  mont %s" % a.object_path)
            except Exception:
                L("  mont %s" % a)
    except Exception as e:
        L("ARFilter ERR %s" % e)
        # fallback list
        try:
            paths = unreal.EditorAssetLibrary.list_assets("/Game", True, False)
            monts = [p for p in paths if "Montage" in p or "AM_" in p]
            L("list_assets Montage-ish=%s" % monts[:20])
        except Exception as e2:
            L("list ERR %s" % e2)
    # Try create with factory after setting via call_method
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    if unreal.EditorAssetLibrary.does_asset_exist(MONT):
        L("montage already exists")
        return unreal.EditorAssetLibrary.load_asset(MONT)
    # Use AnimCompositeFactory? or create AnimSequence copy as montage via AssetDuplicate
    # Another approach: AssetTools.create_asset with factory, then use AnimationBlueprintLibrary
    try:
        # In some versions set_editor_properties works with dict
        factory2 = unreal.AnimMontageFactory()
        try:
            factory2.set_editor_properties({"TargetSkeleton": sk})
            L("set_editor_properties TargetSkeleton OK")
        except Exception as e:
            L("set_editor_properties ERR %s" % e)
        mont = tools.create_asset("AM_KayKit_1H_Chop", "/Game/Characters/Player/KayKit/Animations", unreal.AnimMontage, factory2)
        L("create2 -> %s" % mont)
        if mont:
            try:
                mont.set_editor_property("skeleton", sk)
            except Exception as e:
                L("set skel %s" % e)
            unreal.EditorAssetLibrary.save_asset(MONT, only_if_is_dirty=False)
            return mont
    except Exception as e:
        L("create2 ERR %s" % e)
    # Last resort: create via duplicate of chop into montage? can't convert type.
    # Use Python to invoke Factory CreateNewAsset via AssetToolsHelpers with DataTable? no.
    return None

def verify_runtime():
    import shop_interact_runtime as mod
    src = open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py", encoding="utf-8-sig").read()
    L("module file has playing=True: %s" % ("False, True, 0.0" in src))
    L("module ver strings: V15d=%s V15c=%s" % ("V15d" in src, "V15c" in src and "V15d" not in src[:200]))
    # ensure bootstrapped
    try:
        mod.bootstrap()
        L("bootstrap again OK")
    except Exception as e:
        L("bootstrap %s" % e)

L("=== T229b ===")
try_wire()
try_montage_v2()
verify_runtime()
L("=== DONE ===")
flush()
