# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback, sys, importlib, json
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_t331_sword1.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T331: "+str(m))
    except Exception: print(m)
try:
    py = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path: sys.path.insert(0, py)
    if "shop_interact_runtime" in sys.modules:
        m = importlib.reload(sys.modules["shop_interact_runtime"])
    else:
        import shop_interact_runtime as m
    L("SWORD1_ITEM=%s COST=%s" % (m.SWORD1_ITEM, m.SWORD1_COST))
    L("BP=%s" % getattr(m, "_BP_KNIGHT", None))
    L("BP1=%s" % getattr(m, "_BP_KNIGHT_SWORD1", None))
    L("meta=%s" % dict(m._PLAYER_META))
    try:
        L("file=%s" % open(m._PLAYER_META_PATH,encoding="utf-8").read())
    except Exception as e:
        L("file err "+str(e))
    world = m._pie_world()
    L("world=%s" % world)
    if world:
        pc = unreal.GameplayStatics.get_player_controller(world, 0)
        pawn = pc.get_controlled_pawn() if pc else None
        L("pc=%s pawn=%s" % (pc, pawn))
        if pawn:
            L("pawn_class=%s path=%s" % (pawn.get_class().get_name(), pawn.get_class().get_path_name()))
            L("match_default=%s" % m._class_path_matches(pawn, m._BP_KNIGHT))
            L("match_sword1=%s" % m._class_path_matches(pawn, m._BP_KNIGHT_SWORD1))
            comps = pawn.get_components_by_class(unreal.StaticMeshComponent.static_class())
            for c in comps or []:
                try:
                    sm = c.get_editor_property("static_mesh")
                except Exception:
                    sm = None
                L("SMC %s mesh=%s scale=%s" % (c.get_name(), sm.get_name() if sm else None, c.get_editor_property("relative_scale3d")))
        L("desired=%s" % m.desired_knight_class_path(world))
        cls1 = unreal.load_class(None, m._BP_KNIGHT_SWORD1)
        L("load_class sword1=%s" % cls1)
        # CDO sword mesh on sword1 class
        if cls1:
            cdo = unreal.get_default_object(cls1)
            for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
                pn = o.get_path_name()
                if "BP_KayKitKnight_Sword1" in pn and "GEN_VARIABLE" in pn:
                    sm = o.get_editor_property("static_mesh")
                    L("CDO/GEN %s -> %s" % (o.get_name(), sm.get_name() if sm else None))
        # try force swap now
        ok = m.ensure_equipped_pawn_class(world, force=True)
        L("force_swap=%s" % ok)
        pawn2 = pc.get_controlled_pawn() if pc else None
        if pawn2:
            L("after class=%s" % pawn2.get_class().get_path_name())
            comps = pawn2.get_components_by_class(unreal.StaticMeshComponent.static_class())
            for c in comps or []:
                sm = c.get_editor_property("static_mesh")
                L("after SMC %s mesh=%s" % (c.get_name(), sm.get_name() if sm else None))
except Exception as e:
    L("ERR "+str(e)); L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
