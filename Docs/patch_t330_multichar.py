# -*- coding: utf-8 -*-
import ast, shutil
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copyfile(p, p + ".pre_t330_multichar")
t = open(p, encoding="utf-8").read()

if "_BP_KNIGHT_SWORD1" not in t:
    t = t.replace(
        '_BP_KNIGHT = "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C"',
        '_BP_KNIGHT = "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C"\n'
        '_BP_KNIGHT_SWORD1 = "/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1.BP_KayKitKnight_Sword1_C"\n'
        "_PAWN_SWAP_KEY = [None]  # (wkey, equipped, pawn_path)\n",
        1,
    )

a = t.find("def apply_equipped_sword_to_pawn")
b = t.find("def buy_sword1")
if a < 0 or b < 0:
    raise SystemExit("apply/buy markers missing")

new_funcs = '''
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
    base = class_path.replace("_C", "").split(".")[-1]
    try:
        cn = obj.get_class().get_name()
    except Exception:
        cn = ""
    return base in cn or cn in class_path


def ensure_equipped_pawn_class(world_ctx, force=False):
    """Swap possessed pawn between default knight / sword1 knight by equipped item."""
    if world_ctx is None:
        return False
    ensure_player_meta(world_ctx)
    want = desired_knight_class_path(world_ctx)
    pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
    if pc is None:
        return False
    try:
        pawn = pc.get_controlled_pawn()
    except Exception:
        pawn = None
    if pawn is None:
        return False
    try:
        ppath = pawn.get_path_name()
    except Exception:
        ppath = str(id(pawn))
    try:
        wkey = _world_key(world_ctx)
    except Exception:
        wkey = str(world_ctx)
    eq = get_equipped_sword(world_ctx)
    key = (wkey, eq, ppath)
    if _class_path_matches(pawn, want):
        _PAWN_SWAP_KEY[0] = key
        return True
    if (not force) and _PAWN_SWAP_KEY[0] == key:
        return True
    cls = unreal.load_class(None, want)
    if cls is None:
        _log("pawn swap FAIL load " + want)
        return False
    try:
        loc = pawn.get_actor_location()
        rot = pawn.get_actor_rotation()
    except Exception as e:
        _log("pawn swap get xform " + str(e))
        return False
    try:
        ctrl = pc.get_control_rotation()
    except Exception:
        ctrl = rot
    new_pawn = None
    try:
        new_pawn = world_ctx.spawn_actor(cls, loc, rot)
    except Exception:
        new_pawn = None
    if new_pawn is None:
        try:
            new_pawn = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc, rot)
        except Exception as e:
            _log("pawn swap spawn " + str(e))
            return False
    if new_pawn is None:
        _log("pawn swap spawn None")
        return False
    old = pawn
    try:
        pc.possess(new_pawn)
    except Exception as e:
        _log("pawn swap possess " + str(e))
        try:
            new_pawn.destroy_actor()
        except Exception:
            pass
        return False
    try:
        pc.set_control_rotation(ctrl)
    except Exception:
        pass
    try:
        old.destroy_actor()
    except Exception as e:
        _log("pawn swap destroy old " + str(e))
    try:
        ppath2 = new_pawn.get_path_name()
    except Exception:
        ppath2 = str(id(new_pawn))
    _PAWN_SWAP_KEY[0] = (wkey, eq, ppath2)
    _log("pawn swap -> %s equipped=%s" % (want, eq))
    return True


def apply_equipped_sword_to_pawn(pawn, world_ctx=None):
    """Compat shim: multi-character swap instead of mesh edit."""
    if world_ctx is None and pawn is not None:
        try:
            world_ctx = pawn.get_world()
        except Exception:
            world_ctx = None
    return ensure_equipped_pawn_class(world_ctx, force=False)


'''
t = t[:a] + new_funcs + t[b:]

b = t.find("def buy_sword1")
c = t.find("def _widget_buttons", b)
if b < 0 or c < 0:
    raise SystemExit("buy bounds missing")

new_buy = '''def buy_sword1(world_ctx):
    """Weapon shop Button_0: cost 5 -> inventory + switch to BP_KayKitKnight_Sword1."""
    if world_ctx is None:
        return False
    ensure_player_meta(world_ctx)
    inv = get_inventory(world_ctx)
    if SWORD1_ITEM in inv:
        set_equipped_sword(SWORD1_ITEM, world_ctx)
        ensure_equipped_pawn_class(world_ctx, force=True)
        _print(world_ctx, u"已切换剑1角色", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True
    if not spend_gold(SWORD1_COST, world_ctx):
        _print(world_ctx, u"金币不足（需要5）", (1.0, 0.35, 0.35, 1.0), 2.5)
        _log("buy_sword1 not enough gold=%s" % get_gold(world_ctx))
        return False
    add_item(SWORD1_ITEM, world_ctx)
    set_equipped_sword(SWORD1_ITEM, world_ctx)
    ensure_equipped_pawn_class(world_ctx, force=True)
    try:
        pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
        pawn = pc.get_controlled_pawn() if pc else None
        ensure_gold_hud(world_ctx, pc, pawn)
    except Exception:
        pass
    _print(world_ctx, u"购买剑1成功（-5金币）", (0.4, 1.0, 0.5, 1.0), 2.5)
    _log("buy_sword1 OK gold=%s inv=%s" % (get_gold(world_ctx), get_inventory(world_ctx)))
    return True


'''
t = t[:b] + new_buy + t[c:]

t = t.replace(
    '''    try:
        if pawn is not None:
            apply_equipped_sword_to_pawn(pawn, world)
    except Exception as e:
        _log("apply_equipped_sword " + str(e))
''',
    '''    try:
        if pawn is not None:
            ensure_equipped_pawn_class(world, force=False)
    except Exception as e:
        _log("ensure_equipped_pawn_class " + str(e))
''',
)

t = t.replace(
    '''        try:
            pc0 = unreal.GameplayStatics.get_player_controller(world, 0)
            pawn0 = pc0.get_controlled_pawn() if pc0 else None
            apply_equipped_sword_to_pawn(pawn0, world)
        except Exception as e:
            _log("T327 apply default sword " + str(e))
''',
    '''        try:
            _PAWN_SWAP_KEY[0] = None
            ensure_equipped_pawn_class(world, force=True)
        except Exception as e:
            _log("T327 ensure default pawn " + str(e))
''',
)

if "T330_MULTI_CHAR" not in t:
    t = t.replace("T327_PIE_RESET", "T327_PIE_RESET T330_MULTI_CHAR", 1)

open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("SYNTAX_OK")
print("has_sword1_bp", "_BP_KNIGHT_SWORD1" in t)
print("has_ensure", "def ensure_equipped_pawn_class" in t)
