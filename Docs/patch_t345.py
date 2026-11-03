# -*- coding: utf-8 -*-
import ast, shutil
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
bak = p + ".pre_t345_load_bp"
shutil.copy2(p, bak)
t = open(p, encoding="utf-8").read()

# tag
if "T345_LOAD_BP_TMPL" not in t:
    t = t.replace("T343_KILL_GOLD", "T343_KILL_GOLD T345_LOAD_BP_TMPL", 1)

# cache near sword constants
if "_SWORD_TMPL_CACHE" not in t:
    t = t.replace(
        "SWORD1_REL_ROT = (0.0, 0.0, 0.0)",
        "SWORD1_REL_ROT = (0.0, 0.0, 0.0)\n"
        "_SWORD_TMPL_CACHE = {}  # leaf -> (mesh, loc, rot, scale) or None\n"
        "_SWORD_TMPL_FAIL_LOGGED = set()",
        1,
    )

old = '''def _read_bp_sword_template(bp_path_leaf, prefer_mesh_substr=None):
    """Read StaticMesh sword template (mesh/loc/rot/scale) from a knight BP."""
    best = None
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if bp_path_leaf not in pn or "GEN_VARIABLE" not in pn:
            continue
        if "StaticMesh1" in o.get_name():
            continue
        try:
            sm = o.get_editor_property("static_mesh")
        except Exception:
            sm = None
        if sm is None:
            continue
        try:
            sname = sm.get_name()
        except Exception:
            sname = ""
        if "Shield" in sname:
            continue
        if prefer_mesh_substr and prefer_mesh_substr not in sname and "Sword" not in sname:
            continue
        if "Sword" not in sname and prefer_mesh_substr is None:
            continue
        try:
            loc = o.get_editor_property("relative_location")
            rot = o.get_editor_property("relative_rotation")
            sc = o.get_editor_property("relative_scale3d")
        except Exception:
            continue
        best = (sm, loc, rot, sc)
        break
    return best'''

new = '''def _bp_asset_path_for_leaf(bp_path_leaf):
    """Map a BP leaf / class path fragment to a Content asset path."""
    leaf = str(bp_path_leaf or "")
    if "Sword1" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1"
    if "BP_KayKitKnight" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight"
    return None


def _pn_matches_bp_leaf(pn, bp_path_leaf):
    """Exact-ish path match so BP_KayKitKnight does not hit BP_KayKitKnight_Sword1."""
    if not pn or not bp_path_leaf:
        return False
    leaf = str(bp_path_leaf)
    if "Sword1" in leaf:
        return "BP_KayKitKnight_Sword1" in pn
    # default knight: accept BP_KayKitKnight but reject Sword1 variant
    if "BP_KayKitKnight" in leaf:
        return ("BP_KayKitKnight" in pn) and ("BP_KayKitKnight_Sword1" not in pn)
    return leaf in pn


def _read_bp_sword_template(bp_path_leaf, prefer_mesh_substr=None):
    """Read StaticMesh sword template (mesh/loc/rot/scale) from a knight BP.
    T345: force-load the Blueprint asset first so cold editor restart still works.
    """
    cache_key = "%s|%s" % (bp_path_leaf, prefer_mesh_substr or "")
    if cache_key in _SWORD_TMPL_CACHE:
        return _SWORD_TMPL_CACHE[cache_key]

    # Force load Blueprint into memory so GEN_VARIABLE components exist for ObjectIterator.
    asset_path = _bp_asset_path_for_leaf(bp_path_leaf)
    if asset_path:
        try:
            unreal.load_asset(asset_path)
        except Exception as e:
            _log("load sword BP %s %s" % (asset_path, e))
        try:
            # Also load generated class; helps some cold-start sessions.
            unreal.load_class(None, asset_path + "." + asset_path.rsplit("/", 1)[-1] + "_C")
        except Exception:
            pass

    best = None
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "GEN_VARIABLE" not in pn:
            continue
        if not _pn_matches_bp_leaf(pn, bp_path_leaf):
            continue
        if "StaticMesh1" in o.get_name():
            continue
        try:
            sm = o.get_editor_property("static_mesh")
        except Exception:
            sm = None
        if sm is None:
            continue
        try:
            sname = sm.get_name()
        except Exception:
            sname = ""
        if "Shield" in sname:
            continue
        if prefer_mesh_substr and prefer_mesh_substr not in sname and "Sword" not in sname:
            continue
        if "Sword" not in sname and prefer_mesh_substr is None:
            continue
        try:
            loc = o.get_editor_property("relative_location")
            rot = o.get_editor_property("relative_rotation")
            sc = o.get_editor_property("relative_scale3d")
        except Exception:
            continue
        best = (sm, loc, rot, sc)
        break

    _SWORD_TMPL_CACHE[cache_key] = best
    return best'''

if old not in t:
    raise SystemExit("old _read_bp_sword_template not found")
t = t.replace(old, new, 1)

# throttle FAIL log in apply_equipped_sword_look
old_fail = '''    if tmpl is None:
        _log("apply sword look FAIL no BP template")
        return False'''
new_fail = '''    if tmpl is None:
        key = str(get_equipped_sword(world_ctx))
        if key not in _SWORD_TMPL_FAIL_LOGGED:
            _SWORD_TMPL_FAIL_LOGGED.add(key)
            _log("apply sword look FAIL no BP template equipped=%s" % key)
        return False'''
if old_fail not in t:
    raise SystemExit("fail log block not found")
t = t.replace(old_fail, new_fail, 1)

# clear template cache on PIE start / clear_progress so edits to BP are picked up next run
if "_SWORD_TMPL_CACHE.clear()" not in t:
    t = t.replace(
        '_log("clear_progress gold=%s inv=0" % _PLAYER_META["gold"])',
        '_SWORD_TMPL_CACHE.clear()\n'
        '    _SWORD_TMPL_FAIL_LOGGED.clear()\n'
        '    _log("clear_progress gold=%s inv=0" % _PLAYER_META["gold"])',
        1,
    )

open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("OK", "T345_LOAD_BP_TMPL" in t, "_bp_asset_path_for_leaf" in t, "_SWORD_TMPL_CACHE" in t)
