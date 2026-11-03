# -*- coding: utf-8 -*-
import ast
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
t=open(p,encoding="utf-8").read()
a=t.find("def desired_knight_class_path")
c=t.find("def buy_sword1")
if a<0 or c<0: raise SystemExit("markers")

new='''
def desired_knight_class_path(world_ctx=None):
    ensure_player_meta(world_ctx)
    if get_equipped_sword(world_ctx) == SWORD1_ITEM:
        return _BP_KNIGHT_SWORD1
    return _BP_KNIGHT


def _class_path_matches(obj, class_path):
    if obj is None or not class_path:
        return False
    try:
        cp = obj.get_class().get_path_name()
    except Exception:
        cp = ""
    if cp == class_path:
        return True
    try:
        cn = obj.get_class().get_name()
    except Exception:
        cn = ""
    want = class_path.split(".")[-1]
    return cn == want or cn == want.replace("_C", "")


def _read_bp_sword_template(bp_path_leaf, prefer_mesh_substr=None):
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
    return best


def _pawn_sword_static_meshes(pawn):
    out = []
    if pawn is None:
        return out
    try:
        comps = list(pawn.get_components_by_class(unreal.StaticMeshComponent.static_class()) or [])
    except Exception:
        comps = []
    for c in comps:
        try:
            sm = c.get_editor_property("static_mesh")
        except Exception:
            sm = None
        try:
            nm = c.get_name() or ""
        except Exception:
            nm = ""
        sname = sm.get_name() if sm else ""
        if sname == "SM_KayKitShield" or "StaticMesh1" in nm:
            continue
        if ("Sword" in sname) or nm.startswith("StaticMesh") or ("KayKitSword" in sname):
            out.append(c)
    return out


def apply_equipped_sword_look(pawn, world_ctx=None):
    """Apply sword mesh+transform from the matching knight BP onto the live pawn.
    Uses YOUR saved BP_KayKitKnight_Sword1 values when sword1 is equipped.
    """
    if pawn is None:
        return False
    ensure_player_meta(world_ctx)
    if get_equipped_sword(world_ctx) == SWORD1_ITEM:
        tmpl = _read_bp_sword_template("BP_KayKitKnight_Sword1", prefer_mesh_substr="Sword")
    else:
        tmpl = _read_bp_sword_template("BP_KayKitKnight.BP_KayKitKnight", prefer_mesh_substr="SM_KayKitSword")
        if tmpl is None:
            tmpl = _read_bp_sword_template("BP_KayKitKnight", prefer_mesh_substr="Sword")
    if tmpl is None:
        _log("apply sword look FAIL no BP template")
        return False
    mesh, loc, rot, sc = tmpl
    comps = _pawn_sword_static_meshes(pawn)
    if not comps:
        _log("apply sword look FAIL no sword SMC on pawn")
        return False
    ok = 0
    for c in comps:
        try:
            c.set_static_mesh(mesh)
        except Exception:
            try:
                c.set_editor_property("static_mesh", mesh)
            except Exception as e:
                _log("set mesh " + str(e))
                continue
        try:
            c.set_editor_property("relative_location", loc)
            c.set_editor_property("relative_rotation", rot)
            c.set_editor_property("relative_scale3d", sc)
        except Exception as e:
            _log("set xform " + str(e))
        ok += 1
    _log("apply sword look comps=%d equipped=%s mesh=%s" % (
        ok, get_equipped_sword(world_ctx), mesh.get_name() if mesh else None))
    return ok > 0


def ensure_equipped_pawn_class(world_ctx, force=False):
    """Keep current pawn; apply sword look from the authored BP (no class swap)."""
    if world_ctx is None:
        return False
    ensure_player_meta(world_ctx)
    pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
    if pc is None:
        return False
    try:
        pawn = pc.get_controlled_pawn()
    except Exception:
        pawn = None
    if pawn is None:
        return False
    return apply_equipped_sword_look(pawn, world_ctx)


def apply_equipped_sword_to_pawn(pawn, world_ctx=None):
    if world_ctx is None and pawn is not None:
        try:
            world_ctx = pawn.get_world()
        except Exception:
            world_ctx = None
    return apply_equipped_sword_look(pawn, world_ctx)


'''
t=t[:a]+new+t[c:]

# simplify buy to only set meta + apply look
b=t.find("def buy_sword1")
e=t.find("def _widget_buttons", b)
new_buy='''def buy_sword1(world_ctx):
    """Weapon shop: cost 5, then apply BP_KayKitKnight_Sword1 sword look onto current knight."""
    if world_ctx is None:
        return False
    ensure_player_meta(world_ctx)
    inv = get_inventory(world_ctx)
    pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if SWORD1_ITEM in inv:
        set_equipped_sword(SWORD1_ITEM, world_ctx)
        apply_equipped_sword_look(pawn, world_ctx)
        _print(world_ctx, u"已装备剑1", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True
    if not spend_gold(SWORD1_COST, world_ctx):
        _print(world_ctx, u"金币不足（需要5）", (1.0, 0.35, 0.35, 1.0), 2.5)
        return False
    add_item(SWORD1_ITEM, world_ctx)
    set_equipped_sword(SWORD1_ITEM, world_ctx)
    apply_equipped_sword_look(pawn, world_ctx)
    try:
        ensure_gold_hud(world_ctx, pc, pawn)
    except Exception:
        pass
    _print(world_ctx, u"购买剑1成功（-5金币）", (0.4, 1.0, 0.5, 1.0), 2.5)
    _log("buy_sword1 OK")
    return True


'''
t=t[:b]+new_buy+t[e:]

# tick: call apply look not class swap thrash — but applying every tick may fight user?
# Only apply when equipped is sword1 or when key changes
# Replace ensure_equipped_pawn_class(world, force=False) in tick with smarter apply once
# Keep ensure which now only applies look - applying every tick re-reads BP so user edits mid-PIE work after save. OK.

if "T340_APPLY_BP_LOOK" not in t:
    t=t.replace("T339_TRUST_USER_BP","T339_TRUST_USER_BP T340_APPLY_BP_LOOK",1)

open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("SYNTAX_OK")
