# -*- coding: utf-8 -*-
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t228_attack_once.txt"
lines = []


def L(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("P228: " + s)
    except Exception:
        print("P228:", s)


def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def pie_world():
    try:
        worlds = unreal.EditorLevelLibrary.get_pie_worlds(False)
        if worlds:
            return worlds[0]
    except Exception as e:
        L("get_pie_worlds " + str(e))
    # fallback: scan object iterator for UEDPIE
    try:
        World = unreal.load_class(None, "/Script/Engine.World")
        for obj in unreal.ObjectIterator(World):
            n = obj.get_name()
            if "UEDPIE" in n:
                return obj
    except Exception as e:
        L("iter worlds " + str(e))
    return None


def main():
    L("=== probe attack once ===")
    import shop_interact_runtime as m
    L("module file ok; has try_attack=%s" % hasattr(m, "try_attack"))
    L("ATTACK paths first=%s" % (m.ATTACK_ANIM_PATHS[0] if hasattr(m, "ATTACK_ANIM_PATHS") else None))
    world = pie_world()
    L("world=" + str(world))
    if world is None:
        L("NO PIE — ask user to Play, then retest LMB")
        flush()
        return
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    L("pc=%s pawn=%s" % (pc, pawn))
    if not pawn:
        L("NO pawn")
        flush()
        return
    mesh = m._get_pawn_mesh(pawn)
    L("mesh=%s mode=%s anim_class=%s" % (
        mesh,
        mesh.get_editor_property("animation_mode") if mesh else None,
        mesh.get_editor_property("anim_class") if mesh else None,
    ))
    m._LAST_ATTACK_T[0] = 0.0
    m._ATTACK_RESTORE[0] = 0.0
    m._ATTACK_RESTORE[1] = None
    m._ATTACK_RESTORE[2] = None
    ok = m.try_attack(world, pawn)
    L("try_attack -> %s" % ok)
    if mesh:
        L("after mode=%s anim=%s" % (
            mesh.get_editor_property("animation_mode"),
            mesh.get_editor_property("animation") if True else None,
        ))
    L("restore until=%s has_mesh=%s" % (m._ATTACK_RESTORE[0], m._ATTACK_RESTORE[1] is not None))
    flush()


main()
