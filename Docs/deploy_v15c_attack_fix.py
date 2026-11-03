# -*- coding: utf-8 -*-
"""Deploy V15c attack fix: skip fake dynamic-slot, force single-node Chop."""
from __future__ import print_function
import unreal
import shutil
import os
import sys
import importlib

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t228_attack_v15c.txt"
SRC = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime_v15c.py"
DST_PY = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
DST_DOCS = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py"
lines = []


def L(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("T228: " + s)
    except Exception:
        print("T228:", s)


def flush():
    try:
        open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    except Exception as e:
        print("flush", e)


def probe_skeletons():
    mesh_paths = (
        "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight",
    )
    anim_paths = (
        "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop_Rig",
        "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop",
        "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig",
        "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle",
    )
    for mp in mesh_paths:
        skm = unreal.EditorAssetLibrary.load_asset(mp)
        if not skm:
            L("mesh MISSING " + mp)
            continue
        try:
            sk = skm.get_editor_property("skeleton")
            L("mesh %s skeleton=%s" % (mp, sk.get_path_name() if sk else None))
        except Exception as e:
            L("mesh skel err " + str(e))
    for ap in anim_paths:
        a = unreal.EditorAssetLibrary.load_asset(ap)
        if not a:
            L("anim MISSING " + ap)
            continue
        try:
            sk = a.get_editor_property("skeleton")
            ln = a.get_editor_property("sequence_length")
            L("anim %s skeleton=%s len=%.3f" % (
                ap.split("/")[-1], sk.get_path_name() if sk else None, float(ln or 0)))
        except Exception as e:
            L("anim err " + str(e))
    # BP mesh anim class
    try:
        cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Player/KayKit/BP_KayKitKnight")
        cdo = unreal.get_default_object(cls)
        mesh = cdo.get_editor_property("mesh")
        L("BP anim_mode=%s anim_class=%s skm=%s" % (
            mesh.get_editor_property("animation_mode"),
            mesh.get_editor_property("anim_class"),
            mesh.get_editor_property("skeletal_mesh"),
        ))
    except Exception as e:
        L("BP probe " + str(e))
    # Confirm ABP still has no Slot
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    for path in (
        "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion",
        "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight",
    ):
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            L("abp missing " + path)
            continue
        slots = []
        for obj in unreal.ObjectIterator(EdGraphNode):
            pn = obj.get_path_name()
            if path.split("/")[-1] not in pn:
                continue
            if "Default__" in pn or "AnimPreview" in pn:
                continue
            cn = obj.get_class().get_name()
            if "Slot" in cn:
                slots.append(cn + ":" + obj.get_name())
        L("abp %s slots=%s" % (path.split("/")[-1], slots[:8]))


def install_runtime():
    if not os.path.isfile(SRC):
        L("FAIL missing SRC " + SRC)
        return False
    for dst in (DST_PY, DST_DOCS):
        shutil.copyfile(SRC, dst)
        L("copied -> " + dst)
    # Ensure Content/Python is importable
    py_dir = os.path.dirname(DST_PY)
    if py_dir not in sys.path:
        sys.path.insert(0, py_dir)
    mod = sys.modules.get("shop_interact_runtime")
    code = open(DST_PY, encoding="utf-8-sig").read()
    if mod is None:
        import shop_interact_runtime as mod
        L("imported shop_interact_runtime")
    else:
        try:
            exec(compile(code, DST_PY, "exec"), mod.__dict__)
            L("exec'd V15c into existing module")
        except Exception as e:
            L("exec fail " + str(e))
            try:
                importlib.reload(mod)
                L("reload OK")
            except Exception as e2:
                L("reload fail " + str(e2))
                return False
    try:
        mod.bootstrap()
        L("bootstrap OK ver hint in module file V15c")
    except Exception as e:
        L("bootstrap " + str(e))
        return False
    return True


def main():
    L("=== T228 V15c START ===")
    probe_skeletons()
    ok = install_runtime()
    L("install_ok=" + str(ok))
    L("=== T228 DONE ===")
    L("TEST: stop PIE if running, Play again, LMB — should see chop motion not only 挥砍！")
    flush()


main()
