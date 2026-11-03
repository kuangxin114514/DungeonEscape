# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, os

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_abp_layered_t231.txt"
lines = []
def L(m):
    s = str(m); lines.append(s)
    try: unreal.log("T231P: " + s)
    except Exception: print(s)
def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")

CONTENT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content"

def disk_scan():
    L("--- disk ---")
    for root, dirs, files in os.walk(os.path.join(CONTENT, "Characters")):
        for f in files:
            if f.endswith(".uasset") and ("ABP_" in f or "BS_" in f or "Chop" in f or "KayKitKnight" in f or "AM_" in f):
                L("DISK " + os.path.join(root, f))
    # also Mannequin
    man = os.path.join(CONTENT, "Mannequin")
    if os.path.isdir(man):
        for root, dirs, files in os.walk(man):
            for f in files:
                if "AnimBP" in f or "IdleRun" in f:
                    L("DISK " + os.path.join(root, f))

def registry_scan():
    L("--- registry ---")
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    try:
        ar.search_all_assets(True)
    except Exception as e:
        L("search_all " + str(e))
    hits = []
    for a in ar.get_assets_by_path("/Game", recursive=True):
        n = str(a.asset_name)
        if any(k in n for k in ("ABP_Kay", "BS_Kay", "Chop", "ThirdPerson_Anim", "KayKitKnight", "AM_Kay")):
            hits.append("%s | %s | %s" % (a.package_name, n, a.asset_class))
    L("hits=%d" % len(hits))
    for h in hits[:80]:
        L("  " + h)

def try_load(path):
    L("try " + path)
    for fn_name, fn in (
        ("EAL.load", lambda p: unreal.EditorAssetLibrary.load_asset(p)),
        ("EAL.does", lambda p: unreal.EditorAssetLibrary.does_asset_exist(p)),
        ("load_asset", lambda p: unreal.load_asset(p)),
        ("load_object", lambda p: unreal.load_object(None, p)),
    ):
        try:
            v = fn(path)
            L("  %s -> %s" % (fn_name, v))
        except Exception as e:
            L("  %s ERR %s" % (fn_name, e))

def dump_loaded_abp(abp, tag):
    L("--- dump " + tag + " ---")
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    counts = {}
    for obj in unreal.ObjectIterator(EdGraphNode):
        pn = obj.get_path_name()
        if tag not in pn:
            continue
        if "Default__" in pn or "AnimPreview" in pn or "ANIM_PREVIEW" in pn.upper():
            continue
        cn = obj.get_class().get_name()
        counts[cn] = counts.get(cn, 0) + 1
        if "Slot" in cn or "Layered" in cn or "Root" in cn or "BlendSpace" in cn or "StateMachine" in cn or "Cached" in cn:
            extra = ""
            try:
                if "Slot" in cn:
                    node = obj.get_editor_property("node")
                    for prop in ("slot_name", "SlotName"):
                        try:
                            extra = " slot=" + str(node.get_editor_property(prop)); break
                        except Exception: pass
            except Exception: pass
            L("  NODE %s %s%s" % (cn, obj.get_name(), extra))
    L("counts=" + str(sorted(counts.items(), key=lambda x: -x[1])[:30]))

def bones_from_mesh(skm):
    L("--- bones ---")
    try:
        skel = skm.get_editor_property("skeleton")
        L("skel=" + skel.get_path_name())
    except Exception as e:
        L("skel " + str(e)); return
    names = []
    # try SoftObject / get_reference_skeleton via python
    try:
        # UE4 SkeletalMesh.get_bone_name may exist on some builds
        if hasattr(skm, "get_num_bones"):
            n = skm.get_num_bones(); L("get_num_bones=" + str(n))
            for i in range(n):
                names.append(str(skm.get_bone_name(i)))
    except Exception as e:
        L("get_num_bones path " + str(e))
    if not names:
        try:
            # Skeleton.get_editor_property reference_skeleton not exposed; try sockets
            sockets = skel.get_editor_property("sockets")
            L("sockets=" + str(sockets)[:200])
        except Exception as e:
            L("sockets " + str(e))
        try:
            # Import data / bone tree via raw object iterator Skeleton
            for attr in ("bone_tree", "BoneTree", "reference_skeleton", "ref_local_poses"):
                try:
                    v = skel.get_editor_property(attr)
                    L("skel.%s type=%s val=%s" % (attr, type(v), str(v)[:120]))
                except Exception as e:
                    L("skel.%s ERR %s" % (attr, e))
        except Exception:
            pass
    # PIE pawn mesh bone names if available
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        pc = unreal.GameplayStatics.get_player_controller(world, 0)
        pawn = pc.get_controlled_pawn() if pc else None
        if pawn:
            mesh = pawn.get_editor_property("mesh")
            # get_bone_names on component
            if hasattr(mesh, "get_num_bones"):
                n = mesh.get_num_bones()
                L("pie mesh bones=%s" % n)
                for i in range(min(n, 80)):
                    names.append(str(mesh.get_bone_name(i)))
            # bone names via get_bone_name
        else:
            L("no pie pawn")
    except Exception as e:
        L("pie bones " + str(e))
    if names:
        L("bone_count=%d" % len(names))
        L("bones=" + str(names))
        interesting = [n for n in names if any(k in n.lower() for k in ("spine","chest","pelvis","hip","neck","clav","root","body","torso"))]
        L("interesting=" + str(interesting))

def bp_mesh_anim():
    L("--- BP ---")
    # find BP via registry
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for a in ar.get_assets_by_path("/Game/Characters", recursive=True):
        if str(a.asset_name) == "BP_KayKitKnight":
            path = str(a.package_name)
            L("BP pkg=" + path)
            try:
                cls = unreal.EditorAssetLibrary.load_blueprint_class(path)
                cdo = unreal.get_default_object(cls)
                mesh = cdo.get_editor_property("mesh")
                L("anim_mode=%s anim_class=%s skm=%s" % (
                    mesh.get_editor_property("animation_mode"),
                    mesh.get_editor_property("anim_class"),
                    mesh.get_editor_property("skeletal_mesh"),
                ))
                skm = mesh.get_editor_property("skeletal_mesh")
                if skm:
                    bones_from_mesh(skm)
                ac = mesh.get_editor_property("anim_class")
                if ac:
                    L("anim_class path=" + ac.get_path_name())
                    # open generated abp package
                    # ABP_KayKitLocomotion_C -> load parent abp
            except Exception as e:
                L("BP err " + str(e))

def main():
    L("=== T231b START ===")
    disk_scan()
    registry_scan()
    for p in (
        "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion",
        "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight",
        "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight",
        "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop_Rig",
        "/Game/Mannequin/Animations/ThirdPerson_AnimBP",
    ):
        try_load(p)
    # Force load via registry soft paths
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for a in ar.get_assets_by_path("/Game", recursive=True):
        n = str(a.asset_name)
        if n in ("ABP_KayKitLocomotion", "ABP_KayKitKnight", "ThirdPerson_AnimBP"):
            pkg = str(a.package_name)
            L("force load " + pkg)
            asset = unreal.EditorAssetLibrary.load_asset(pkg)
            L("  -> " + str(asset))
            if asset:
                dump_loaded_abp(asset, n)
    bp_mesh_anim()
    L("=== T231b DONE ===")
    flush()

main()
