# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback, sys, importlib
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t334_attach.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T334: "+str(m))
    except Exception: print(m)

def fix_bp_attach():
    DST="/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1"
    bp=unreal.load_asset(DST)
    # Compare with default knight socket attachment on GEN variables
    for label, path in (("default","/Game/Characters/Player/KayKit/BP_KayKitKnight"), ("sword1", DST)):
        L("--- "+label)
        for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
            try: pn=o.get_path_name()
            except Exception: continue
            if path.split("/")[-1] not in pn: continue
            if "GEN_VARIABLE" not in pn and "Default__" not in pn and "BP_KayKitKnight" not in pn:
                continue
            if path.split("/")[-1] not in pn: continue
            sm=None
            try: sm=o.get_editor_property("static_mesh")
            except Exception: pass
            try:
                attach=o.get_editor_property("attach_parent")
            except Exception:
                attach=None
            try:
                socket=o.get_editor_property("attach_socket_name")
            except Exception:
                socket=""
            try:
                rel=o.get_editor_property("relative_location")
                rrot=o.get_editor_property("relative_rotation")
                rsc=o.get_editor_property("relative_scale3d")
            except Exception:
                rel=rrot=rsc=None
            L("%s mesh=%s parent=%s socket=%s loc=%s rot=%s scale=%s" % (
                o.get_name(), sm.get_name() if sm else None,
                attach.get_name() if attach else None, socket, rel, rrot, rsc))

try:
    fix_bp_attach()
    # Also copy attach settings from default sword GEN to sword1 sword GEN if socket empty
    src_sword=None; dst_sword=None; dst_shield=None
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        pn=o.get_path_name()
        if "BP_KayKitKnight." in pn and "Sword1" not in pn and "GEN_VARIABLE" in pn:
            sm=o.get_editor_property("static_mesh")
            if sm and sm.get_name()=="SM_KayKitSword":
                src_sword=o
        if "BP_KayKitKnight_Sword1" in pn and "GEN_VARIABLE" in pn:
            sm=o.get_editor_property("static_mesh")
            nm=o.get_name()
            if sm and "Sword" in sm.get_name():
                dst_sword=o
            if sm and "Shield" in sm.get_name():
                dst_shield=o
            if nm.startswith("StaticMesh_GEN") and "StaticMesh1" not in nm:
                dst_sword=dst_sword or o
    L("src_sword=%s dst_sword=%s" % (src_sword, dst_sword))
    if src_sword and dst_sword:
        for prop in ("attach_socket_name", "relative_location", "relative_rotation"):
            try:
                val=src_sword.get_editor_property(prop)
                # keep sword1 scale if user set; copy loc/rot/socket from working default
                if prop=="relative_scale3d":
                    continue
                dst_sword.set_editor_property(prop, val)
                L("copied %s=%s" % (prop, val))
            except Exception as e:
                L("copy %s %s" % (prop, e))
        # ensure mesh is 2H
        mesh=unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword_2H")
        try:
            dst_sword.set_editor_property("static_mesh", mesh)
            L("mesh set 2H")
        except Exception as e:
            L("mesh "+str(e))
        # attach parent should be skeletal mesh - try set via attach_to
        try:
            parent=src_sword.get_editor_property("attach_parent")
            if parent is not None:
                dst_sword.set_editor_property("attach_parent", parent)
                L("parent set %s" % parent.get_name())
        except Exception as e:
            L("parent "+str(e))
        bp=unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1")
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        try: unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1")
        except Exception: pass
        L("saved")
    # live PIE fix
    py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path: sys.path.insert(0,py)
    m=importlib.reload(sys.modules["shop_interact_runtime"]) if "shop_interact_runtime" in sys.modules else __import__("shop_interact_runtime")
    try: m.bootstrap()
    except Exception as e: L("boot "+str(e))
    world=m._pie_world(); L("world=%s"%world)
    if world:
        pc=unreal.GameplayStatics.get_player_controller(world,0)
        pawn=pc.get_controlled_pawn() if pc else None
        L("before %s" % (pawn.get_class().get_path_name() if pawn else None))
        m.set_equipped_sword(m.SWORD1_ITEM, world)
        ok=m.ensure_equipped_pawn_class(world, force=True)
        L("swap=%s" % ok)
        pawn=pc.get_controlled_pawn() if pc else None
        L("after %s" % (pawn.get_class().get_path_name() if pawn else None))
        if pawn:
            for c in pawn.get_components_by_class(unreal.StaticMeshComponent.static_class()) or []:
                sm=c.get_editor_property("static_mesh")
                try: sock=c.get_editor_property("attach_socket_name")
                except Exception: sock="?"
                L("live %s mesh=%s sock=%s loc=%s" % (c.get_name(), sm.get_name() if sm else None, sock, c.get_editor_property("relative_location")))
except Exception as e:
    L("ERR "+str(e)); L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
