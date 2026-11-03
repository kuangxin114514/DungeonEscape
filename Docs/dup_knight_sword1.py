# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\dup_knight_sword1.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T330: "+str(m))
    except Exception: print(m)

SRC = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
DST_PATH = "/Game/Characters/Player/KayKit"
DST_NAME = "BP_KayKitKnight_Sword1"
DST = DST_PATH + "/" + DST_NAME
SWORD = "/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword_2H"
SCALE = 0.45

try:
    src_asset = unreal.load_asset(SRC)
    L("src=%s" % src_asset)
    bp = unreal.load_asset(DST)
    if bp is None:
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        bp = tools.duplicate_asset(DST_NAME, DST_PATH, src_asset)
        L("duplicated=%s" % bp)
    else:
        L("already=%s" % bp)
    if bp is None:
        raise RuntimeError("dup failed")
    mesh = unreal.load_asset(SWORD)
    L("mesh=%s" % mesh)

    scs = None
    try:
        scs = bp.get_editor_property("simple_construction_script")
    except Exception as e:
        L("scs prop " + str(e))
    try:
        if scs is None:
            scs = bp.simple_construction_script
    except Exception:
        pass
    nodes = []
    if scs is not None:
        try:
            nodes = list(scs.get_all_nodes())
        except Exception as e:
            L("get_all_nodes " + str(e))
    L("nodes=%d" % len(nodes))
    changed = 0

    def walk(n, depth=0):
        global changed
        varname = ""
        try:
            varname = str(n.get_variable_name())
        except Exception:
            try:
                varname = str(n.get_editor_property("internal_variable_name"))
            except Exception:
                varname = ""
        L(("  "*depth) + "node '%s'" % varname)
        if "sword" in varname.lower():
            tmpl = None
            for getter in (
                lambda: n.component_template,
                lambda: n.get_editor_property("component_template"),
            ):
                try:
                    tmpl = getter()
                except Exception:
                    tmpl = None
                if tmpl is not None:
                    break
            L("  tmpl=%s" % tmpl)
            if tmpl is not None and mesh is not None:
                try:
                    tmpl.set_editor_property("static_mesh", mesh)
                    changed += 1
                    L("  mesh OK")
                except Exception as e:
                    L("  mesh " + str(e))
                try:
                    tmpl.set_editor_property("relative_scale3d", unreal.Vector(SCALE, SCALE, SCALE))
                    L("  scale OK")
                except Exception as e:
                    L("  scale " + str(e))
        kids = []
        try:
            kids = list(n.get_editor_property("child_nodes") or [])
        except Exception:
            pass
        for k in kids:
            walk(k, depth + 1)

    for n in nodes:
        walk(n)

    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        L("compiled via BlueprintEditorLibrary")
    except Exception as e:
        L("compile lib " + str(e))
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(bp)
        except Exception:
            pass

    try:
        unreal.EditorAssetLibrary.save_asset(DST)
        L("save_asset OK")
    except Exception as e:
        L("save_asset " + str(e))
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(bp)
            L("save_loaded OK")
        except Exception as e2:
            L("save_loaded " + str(e2))

    # verify load generated class
    gen = unreal.load_asset(DST + "." + DST_NAME + "_C")
    L("gen=%s changed=%d" % (gen, changed))
except Exception as e:
    L("ERR " + str(e))
    L(traceback.format_exc())
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("WROTE", OUT)
