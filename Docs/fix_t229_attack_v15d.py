# -*- coding: utf-8 -*-
"""T229: create chop montage, try add DefaultSlot to ABP, deploy V15d runtime (bIsPlaying=True)."""
from __future__ import print_function
import unreal
import shutil
import os
import sys
import time

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t229_attack_v15d.txt"
SRC = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
DST_DOCS = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py"
ABP = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
CHOP = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop_Rig"
CHOP2 = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop"
MONT_DIR = "/Game/Characters/Player/KayKit/Animations"
MONT_NAME = "AM_KayKit_1H_Chop"
MONT_PATH = MONT_DIR + "/" + MONT_NAME
lines = []


def L(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("T229: " + s)
    except Exception:
        print("T229:", s)


def flush():
    try:
        open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    except Exception as e:
        print("flush", e)


def _skel_of(obj):
    try:
        sk = obj.get_editor_property("skeleton")
        return sk
    except Exception:
        return None


def create_montage():
    chop = unreal.EditorAssetLibrary.load_asset(CHOP)
    if chop is None:
        chop = unreal.EditorAssetLibrary.load_asset(CHOP2)
    if chop is None:
        L("FAIL no chop sequence")
        return None
    sk = _skel_of(chop)
    L("chop=%s skel=%s len=%s" % (
        chop.get_name(),
        sk.get_path_name() if sk else None,
        chop.get_editor_property("sequence_length"),
    ))
    if unreal.EditorAssetLibrary.does_asset_exist(MONT_PATH):
        m = unreal.EditorAssetLibrary.load_asset(MONT_PATH)
        L("montage exists -> %s" % m)
        return m
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.AnimMontageFactory()
    try:
        factory.set_editor_property("target_skeleton", sk)
        L("factory target_skeleton set")
    except Exception as e:
        L("factory target_skeleton ERR %s" % e)
    # SourceAnimation makes a montage with one segment if supported
    for pn in ("source_animation", "SourceAnimation"):
        try:
            factory.set_editor_property(pn, chop)
            L("factory %s set" % pn)
            break
        except Exception as e:
            L("factory %s ERR %s" % (pn, e))
    try:
        mont = tools.create_asset(MONT_NAME, MONT_DIR, unreal.AnimMontage, factory)
        L("create_asset montage -> %s" % mont)
    except Exception as e:
        L("create_asset ERR %s" % e)
        mont = None
    if mont is None:
        # Fallback: duplicate any existing montage? none. Try empty then set skeleton
        try:
            factory2 = unreal.AnimMontageFactory()
            factory2.set_editor_property("target_skeleton", sk)
            mont = tools.create_asset(MONT_NAME, MONT_DIR, unreal.AnimMontage, factory2)
            L("create empty montage -> %s" % mont)
        except Exception as e2:
            L("empty montage ERR %s" % e2)
            return None
    # Ensure skeleton
    try:
        mont.set_editor_property("skeleton", sk)
    except Exception as e:
        L("mont skeleton ERR %s" % e)
    # Try to add/ensure slot track content via composite sections if API allows
    try:
        # slot_anim_tracks / slot_groups in UE4
        tracks = None
        for pn in ("slot_anim_tracks", "SlotAnimTracks"):
            try:
                tracks = mont.get_editor_property(pn)
                L("%s count=%s" % (pn, len(list(tracks)) if tracks is not None else None))
                break
            except Exception as e:
                L("get %s ERR %s" % (pn, e))
        if tracks is not None and len(list(tracks)) == 0:
            # Build a SlotAnimationTrack manually
            try:
                sat = unreal.SlotAnimationTrack()
                sat.set_editor_property("slot_name", "DefaultSlot")
                anim_track = unreal.AnimTrack()
                seg = unreal.AnimSegment()
                seg.set_editor_property("anim_reference", chop)
                try:
                    seg.set_editor_property("anim_start_time", 0.0)
                except Exception:
                    pass
                try:
                    seg.set_editor_property("anim_end_time", float(chop.get_editor_property("sequence_length")))
                except Exception:
                    pass
                try:
                    seg.set_editor_property("anim_play_rate", 1.0)
                except Exception:
                    pass
                try:
                    seg.set_editor_property("start_pos", 0.0)
                except Exception:
                    pass
                segs = anim_track.get_editor_property("anim_segments")
                # anim_segments may be Array
                try:
                    anim_track.set_editor_property("anim_segments", [seg])
                except Exception as e:
                    L("set anim_segments ERR %s" % e)
                sat.set_editor_property("anim_track", anim_track)
                mont.set_editor_property("slot_anim_tracks", [sat])
                L("wrote slot_anim_tracks DefaultSlot")
            except Exception as e:
                L("build SlotAnimationTrack ERR %s" % e)
    except Exception as e:
        L("tracks inspect ERR %s" % e)
    unreal.EditorAssetLibrary.save_asset(MONT_PATH, only_if_is_dirty=False)
    L("montage saved %s" % MONT_PATH)
    return mont


def list_abp_nodes(path):
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    name = path.split("/")[-1]
    rows = []
    for obj in unreal.ObjectIterator(EdGraphNode):
        pn = obj.get_path_name()
        if name not in pn:
            continue
        if "Default__" in pn or "AnimPreview" in pn:
            continue
        cn = obj.get_class().get_name()
        rows.append((cn, obj.get_name(), pn))
    return rows


def try_insert_slot():
    """Insert AnimGraphNode_Slot between StateMachine and Root if missing.
    UE4.27 Python graph edit is limited; best-effort.
    """
    rows = list_abp_nodes(ABP)
    slots = [r for r in rows if "Slot" in r[0]]
    L("ABP nodes=%d slots=%s" % (len(rows), [s[1] for s in slots]))
    # Also inspect ThirdPerson template
    tp_rows = list_abp_nodes("/Game/Mannequin/Animations/ThirdPerson_AnimBP")
    tp_slots = [r for r in tp_rows if "Slot" in r[0]]
    L("TP nodes=%d slots=%s" % (len(tp_rows), [s[1] for s in tp_slots]))
    if slots:
        L("Slot already present — skip insert")
        return True
    abp = unreal.EditorAssetLibrary.load_asset(ABP)
    if abp is None:
        L("no ABP")
        return False
    # Find AnimGraph EdGraph
    anim_graph = None
    EdGraph = unreal.load_class(None, "/Script/Engine.EdGraph")
    for obj in unreal.ObjectIterator(EdGraph):
        pn = obj.get_path_name()
        if "ABP_KayKitLocomotion" not in pn:
            continue
        if "Default__" in pn or "AnimPreview" in pn:
            continue
        try:
            n = obj.get_name()
        except Exception:
            n = ""
        if n == "AnimGraph" or "AnimGraph" in pn:
            anim_graph = obj
            L("found AnimGraph %s" % pn)
            break
    if anim_graph is None:
        L("AnimGraph not found — cannot insert Slot via Python")
        return False
    # Try construct Slot node
    slot_cls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_Slot")
    if slot_cls is None:
        L("no AnimGraphNode_Slot class")
        return False
    try:
        # construct_object outer=graph
        slot_node = unreal.new_object(slot_cls, anim_graph)
        L("new_object Slot -> %s" % slot_node)
    except Exception as e:
        L("new_object Slot ERR %s" % e)
        slot_node = None
    if slot_node is None:
        try:
            slot_node = unreal.Object.cast(slot_cls, None)
        except Exception:
            pass
    if slot_node is None:
        L("FAILED create Slot node")
        return False
    # Set slot name DefaultSlot on inner node
    try:
        inner = slot_node.get_editor_property("node")
        for pn in ("slot_name", "SlotName"):
            try:
                inner.set_editor_property(pn, "DefaultSlot")
                L("inner %s=DefaultSlot" % pn)
            except Exception as e:
                L("inner %s ERR %s" % (pn, e))
    except Exception as e:
        L("inner node ERR %s" % e)
    # Try add to graph
    try:
        nodes = anim_graph.get_editor_property("nodes")
        L("graph nodes before=%s" % (len(list(nodes)) if nodes is not None else None))
    except Exception as e:
        L("get nodes ERR %s" % e)
    # Schema create — often needed for pins
    try:
        schema = anim_graph.get_editor_property("schema")
        L("schema=%s" % schema)
    except Exception as e:
        L("schema ERR %s" % e)
    # Find Root and StateMachine graph nodes
    root = None
    sm = None
    for cn, nm, pn in rows:
        if cn == "AnimGraphNode_Root":
            # resolve object
            for obj in unreal.ObjectIterator(unreal.load_class(None, "/Script/Engine.EdGraphNode")):
                if obj.get_path_name() == pn:
                    root = obj
                    break
        if cn == "AnimGraphNode_StateMachine":
            for obj in unreal.ObjectIterator(unreal.load_class(None, "/Script/Engine.EdGraphNode")):
                if obj.get_path_name() == pn:
                    sm = obj
                    break
    L("root=%s sm=%s slot=%s" % (root, sm, slot_node))
    # Linking pins via Python in 4.27 is unreliable; open editor to compile if we at least added node
    try:
        unreal.EditorAssetLibrary.save_asset(ABP, only_if_is_dirty=False)
    except Exception:
        pass
    # Re-list
    rows2 = list_abp_nodes(ABP)
    slots2 = [r for r in rows2 if "Slot" in r[0]]
    L("after insert slots=%s" % [s[1] for s in slots2])
    if not slots2:
        L("Slot insert did not persist / not wired — montage path stays optional; single-node is primary")
        return False
    # Open to compile
    try:
        aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
        aes.open_editor_for_assets([abp])
        time.sleep(2.0)
        unreal.EditorAssetLibrary.save_asset(ABP, only_if_is_dirty=False)
        aes.close_all_editors_for_asset(abp)
        L("opened/closed ABP for compile")
    except Exception as e:
        L("compile open ERR %s" % e)
    return True


def deploy_runtime():
    if not os.path.isfile(SRC):
        L("FAIL missing " + SRC)
        return False
    shutil.copyfile(SRC, DST_DOCS)
    L("copied runtime -> Docs")
    py_dir = os.path.dirname(SRC)
    if py_dir not in sys.path:
        sys.path.insert(0, py_dir)
    code = open(SRC, encoding="utf-8-sig").read()
    # sanity: must contain playing=True
    if "override_animation_data(seq, False, True" not in code:
        L("FAIL runtime missing bIsPlaying=True patch")
        return False
    L("runtime contains bIsPlaying=True OK")
    mod = sys.modules.get("shop_interact_runtime")
    if mod is None:
        import shop_interact_runtime as mod
        L("imported shop_interact_runtime")
    else:
        try:
            exec(compile(code, SRC, "exec"), mod.__dict__)
            L("exec'd V15d into existing module")
        except Exception as e:
            L("exec fail " + str(e))
            return False
    try:
        mod.bootstrap()
        L("bootstrap OK V15d")
    except Exception as e:
        L("bootstrap " + str(e))
        return False
    return True


def pie_probe_attack():
    """If PIE running, fire one attack and log mesh playing state briefly."""
    try:
        ws = unreal.EditorLevelLibrary.get_pie_worlds(False)
        world = ws[0] if ws else None
    except Exception:
        world = None
    if world is None:
        L("PIE not running — skip live attack probe")
        return
    import shop_interact_runtime as mod
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        L("PIE no pawn")
        return
    mesh = mod._get_pawn_mesh(pawn)
    L("before attack mode=%s anim_class=%s" % (
        mesh.get_editor_property("animation_mode") if mesh else None,
        mesh.get_editor_property("anim_class") if mesh else None,
    ))
    ok = mod.try_attack(world, pawn)
    L("try_attack -> %s" % ok)
    if mesh:
        try:
            L("after mode=%s playing_prop_try" % mesh.get_editor_property("animation_mode"))
        except Exception as e:
            L("after mode ERR %s" % e)
        for pn in ("playing", "animation", "anim_class"):
            try:
                L("  mesh.%s=%s" % (pn, mesh.get_editor_property(pn)))
            except Exception as e:
                L("  mesh.%s ERR %s" % (pn, e))


def main():
    L("=== T229 V15d START ===")
    create_montage()
    try_insert_slot()
    ok = deploy_runtime()
    L("deploy_ok=" + str(ok))
    pie_probe_attack()
    L("=== T229 DONE ===")
    L("TEST: stop PIE if running, Play Map_Dungeon, LMB — expect multi-frame chop (not freeze).")
    flush()


main()
