# -*- coding: utf-8 -*-
import ast, shutil, re
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
bak = p + ".pre_t346_shield1"
shutil.copy2(p, bak)
t = open(p, encoding="utf-8").read()

if "T346_SHIELD1" not in t:
    t = t.replace("T345_LOAD_BP_TMPL", "T345_LOAD_BP_TMPL T346_SHIELD1", 1)

# constants after SWORD1 block
if "SHIELD1_ITEM" not in t:
    t = t.replace(
        "SWORD1_REL_ROT = (0.0, 0.0, 0.0)",
        "SWORD1_REL_ROT = (0.0, 0.0, 0.0)\n"
        "SHIELD1_ITEM = \"SM_KayKitShield_Round\"\n"
        "SHIELD1_COST = 5\n"
        "SHIELD1_MESH = \"/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield_Round\"\n"
        "DEFAULT_SHIELD_ITEM = \"SM_KayKitShield\"",
        1,
    )

# shop btn state
if "_SHOP_BTN_SHIELD1" not in t:
    t = t.replace(
        "_SHOP_BTN_SWORD1_DOWN = [False]",
        "_SHOP_BTN_SWORD1_DOWN = [False]\n"
        "_SHOP_BTN_SHIELD1 = [None]\n"
        "_SHOP_BTN_SHIELD1_DOWN = [False]",
        1,
    )

# meta default
t = t.replace(
    '_PLAYER_META = {"gold": DEFAULT_GOLD, "inventory": [], "equipped_sword": "SM_KayKitSword", "ready": False}',
    '_PLAYER_META = {"gold": DEFAULT_GOLD, "inventory": [], "equipped_sword": "SM_KayKitSword", "equipped_shield": "SM_KayKitShield", "ready": False}',
    1,
)

# load equipped_shield
if 'equipped_shield' not in t[t.find("def _meta_load_file"):t.find("def _meta_load_file")+800]:
    t = t.replace(
        'eq = data.get("equipped_sword", "SM_KayKitSword")\n'
        '            _PLAYER_META["equipped_sword"] = str(eq or "SM_KayKitSword")',
        'eq = data.get("equipped_sword", "SM_KayKitSword")\n'
        '            _PLAYER_META["equipped_sword"] = str(eq or "SM_KayKitSword")\n'
        '            es = data.get("equipped_shield", DEFAULT_SHIELD_ITEM)\n'
        '            _PLAYER_META["equipped_shield"] = str(es or DEFAULT_SHIELD_ITEM)',
        1,
    )

# save equipped_shield
t = t.replace(
    '"equipped_sword": str(_PLAYER_META.get("equipped_sword") or "SM_KayKitSword"),\n'
    '            },',
    '"equipped_sword": str(_PLAYER_META.get("equipped_sword") or "SM_KayKitSword"),\n'
    '                "equipped_shield": str(_PLAYER_META.get("equipped_shield") or DEFAULT_SHIELD_ITEM),\n'
    '            },',
    1,
)

# get/set equipped shield after set_equipped_sword
if "def get_equipped_shield" not in t:
    # find set_equipped_sword function end - insert after it
    m = re.search(r"def set_equipped_sword\(item_name, world_ctx=None\):\n(?:.*\n){1,8}?    return _PLAYER_META\[\"equipped_sword\"\]\n", t)
    if not m:
        raise SystemExit("set_equipped_sword block not found")
    insert = m.group(0) + '''

def get_equipped_shield(world_ctx=None):
    ensure_player_meta(world_ctx)
    return str(_PLAYER_META.get("equipped_shield") or DEFAULT_SHIELD_ITEM)


def set_equipped_shield(item_name, world_ctx=None):
    ensure_player_meta(world_ctx)
    _PLAYER_META["equipped_shield"] = str(item_name)
    _meta_push_gi(_gi_from_world(world_ctx))
    _meta_save_file()
    return _PLAYER_META["equipped_shield"]
'''
    t = t[:m.start()] + insert + t[m.end():]

# extend _bp_asset_path_for_leaf
old_bp = '''def _bp_asset_path_for_leaf(bp_path_leaf):
    """Map a BP leaf / class path fragment to a Content asset path."""
    leaf = str(bp_path_leaf or "")
    if "Sword1" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1"
    if "BP_KayKitKnight" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight"
    return None'''
new_bp = '''def _bp_asset_path_for_leaf(bp_path_leaf):
    """Map a BP leaf / class path fragment to a Content asset path."""
    leaf = str(bp_path_leaf or "")
    if "Shield1" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight_Shield1"
    if "Sword1" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1"
    if "BP_KayKitKnight" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight"
    return None'''
if old_bp not in t:
    raise SystemExit("_bp_asset_path_for_leaf missing")
t = t.replace(old_bp, new_bp, 1)

old_pn = '''def _pn_matches_bp_leaf(pn, bp_path_leaf):
    """Exact-ish path match so BP_KayKitKnight does not hit BP_KayKitKnight_Sword1."""
    if not pn or not bp_path_leaf:
        return False
    leaf = str(bp_path_leaf)
    if "Sword1" in leaf:
        return "BP_KayKitKnight_Sword1" in pn
    # default knight: accept BP_KayKitKnight but reject Sword1 variant
    if "BP_KayKitKnight" in leaf:
        return ("BP_KayKitKnight" in pn) and ("BP_KayKitKnight_Sword1" not in pn)
    return leaf in pn'''
new_pn = '''def _pn_matches_bp_leaf(pn, bp_path_leaf):
    """Exact-ish path match so BP_KayKitKnight does not hit Sword1/Shield1 variants."""
    if not pn or not bp_path_leaf:
        return False
    leaf = str(bp_path_leaf)
    if "Shield1" in leaf:
        return "BP_KayKitKnight_Shield1" in pn
    if "Sword1" in leaf:
        return "BP_KayKitKnight_Sword1" in pn
    # default knight: accept BP_KayKitKnight but reject variants
    if "BP_KayKitKnight" in leaf:
        return (
            ("BP_KayKitKnight" in pn)
            and ("BP_KayKitKnight_Sword1" not in pn)
            and ("BP_KayKitKnight_Shield1" not in pn)
        )
    return leaf in pn'''
if old_pn not in t:
    raise SystemExit("_pn_matches_bp_leaf missing")
t = t.replace(old_pn, new_pn, 1)

# shield helpers + buy + wire before _wire_weapon_shop_buttons
if "def buy_shield1" not in t:
    marker = "def _wire_weapon_shop_buttons(widget, world_ctx):"
    if marker not in t:
        raise SystemExit("wire marker missing")
    block = r'''
def _read_bp_shield_template(bp_path_leaf):
    """Read shield StaticMesh template from knight BP (force-load like sword)."""
    cache_key = "shield|%s" % bp_path_leaf
    if cache_key in _SWORD_TMPL_CACHE:
        return _SWORD_TMPL_CACHE[cache_key]
    asset_path = _bp_asset_path_for_leaf(bp_path_leaf)
    if asset_path:
        try:
            unreal.load_asset(asset_path)
        except Exception as e:
            _log("load shield BP %s %s" % (asset_path, e))
        try:
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
        nm = ""
        try:
            nm = o.get_name() or ""
        except Exception:
            nm = ""
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
        if "Sword" in sname:
            continue
        is_shield = ("Shield" in sname) or ("StaticMesh1" in nm) or ("shield" in nm.lower())
        if not is_shield:
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
    return best


def _pawn_shield_static_meshes(pawn):
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
        if "Sword" in sname:
            continue
        if ("Shield" in sname) or ("StaticMesh1" in nm) or ("shield" in nm.lower()) or ("KayKitShield" in sname):
            out.append(c)
    return out


def apply_equipped_shield_look(pawn, world_ctx=None):
    """Apply shield mesh+transform from Shield1 BP / default knight BP onto live pawn."""
    if pawn is None:
        return False
    ensure_player_meta(world_ctx)
    if get_equipped_shield(world_ctx) == SHIELD1_ITEM:
        tmpl = _read_bp_shield_template("BP_KayKitKnight_Shield1")
    else:
        tmpl = _read_bp_shield_template("BP_KayKitKnight")
    if tmpl is None:
        key = "shield:" + str(get_equipped_shield(world_ctx))
        if key not in _SWORD_TMPL_FAIL_LOGGED:
            _SWORD_TMPL_FAIL_LOGGED.add(key)
            _log("apply shield look FAIL no BP template")
        return False
    mesh, loc, rot, sc = tmpl
    comps = _pawn_shield_static_meshes(pawn)
    if not comps:
        _log("apply shield look FAIL no shield SMC on pawn")
        return False
    ok = 0
    for c in comps:
        try:
            c.set_static_mesh(mesh)
        except Exception:
            try:
                c.set_editor_property("static_mesh", mesh)
            except Exception as e:
                _log("set shield mesh " + str(e))
                continue
        try:
            c.set_editor_property("relative_location", loc)
            c.set_editor_property("relative_rotation", rot)
            c.set_editor_property("relative_scale3d", sc)
        except Exception as e:
            _log("set shield xform " + str(e))
        ok += 1
    _log("apply shield look comps=%d equipped=%s mesh=%s" % (
        ok, get_equipped_shield(world_ctx), mesh.get_name() if mesh else None))
    return ok > 0


def buy_shield1(world_ctx):
    """Armor shop: cost 5, apply BP_KayKitKnight_Shield1 shield look onto current knight."""
    if world_ctx is None:
        return False
    ensure_player_meta(world_ctx)
    inv = get_inventory(world_ctx)
    pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if SHIELD1_ITEM in inv:
        set_equipped_shield(SHIELD1_ITEM, world_ctx)
        apply_equipped_shield_look(pawn, world_ctx)
        _print(world_ctx, u"已装备盾1", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True
    if not spend_gold(SHIELD1_COST, world_ctx):
        _print(world_ctx, u"金币不足（需5）", (1.0, 0.35, 0.35, 1.0), 2.5)
        return False
    add_item(SHIELD1_ITEM, world_ctx)
    set_equipped_shield(SHIELD1_ITEM, world_ctx)
    apply_equipped_shield_look(pawn, world_ctx)
    try:
        ensure_gold_hud(world_ctx, pc, pawn)
    except Exception:
        pass
    _print(world_ctx, u"购买盾1成功（-5金币）", (0.4, 1.0, 0.5, 1.0), 2.5)
    _log("buy_shield1 OK")
    return True


def _wire_armor_shop_buttons(widget, world_ctx):
    """Bind 购买盾1 (Button_0) on armor shop."""
    if widget is None:
        return False
    try:
        wid = widget.get_path_name()
    except Exception:
        wid = str(id(widget))
    # reuse sword wired-id store? separate: allow rewire when different widget
    btns = _widget_buttons(widget)
    btn = btns.get("Button_0") or btns.get("Button")
    if btn is None:
        try:
            btn = widget.get_widget_from_name("Button_0")
        except Exception:
            btn = None
    if btn is None:
        _log("wire armor shop: no Button_0")
        return False
    _set_button_label(btn, u"购买盾1 (5金币)")
    btn2 = btns.get("Button")
    if btn2 is not None and btn2 is not btn:
        _set_button_label(btn2, u"购买盾2（未开放）")
    wired = False
    try:
        def _on_buy():
            try:
                buy_shield1(world_ctx)
            except Exception as e:
                _log("buy_shield1 cb " + str(e))
        try:
            btn.on_clicked.clear()
        except Exception:
            pass
        try:
            btn.on_clicked.add_callable(_on_buy)
            wired = True
            _log("wired armor Button_0 on_clicked add_callable")
        except Exception as e:
            _log("armor on_clicked " + str(e))
    except Exception as e:
        _log("armor wire " + str(e))
    _SHOP_BTN_SHIELD1[0] = btn
    _SHOP_BTN_SHIELD1_DOWN[0] = False
    if not wired:
        _log("armor Button_0 will use tick is_pressed fallback")
    return True


def _poll_armor_shop_buy(world_ctx):
    """Fallback: detect armor Button_0 press while shop open."""
    btn = _SHOP_BTN_SHIELD1[0]
    if btn is None:
        _SHOP_BTN_SHIELD1_DOWN[0] = False
        return
    try:
        down = bool(btn.is_pressed())
    except Exception:
        try:
            down = bool(btn.get_editor_property("is_pressed"))
        except Exception:
            down = False
    if down and not _SHOP_BTN_SHIELD1_DOWN[0]:
        _SHOP_BTN_SHIELD1_DOWN[0] = True
        try:
            buy_shield1(world_ctx)
        except Exception as e:
            _log("poll buy_shield1 " + str(e))
    elif not down:
        _SHOP_BTN_SHIELD1_DOWN[0] = False


'''
    t = t.replace(marker, block + marker, 1)

# open_shop: wire armor
old_open = '''    if shop_key == "Weapon":
        try:
            _wire_weapon_shop_buttons(widget, world_ctx)
        except Exception as e:
            _log("wire weapon shop " + str(e))
    return True'''
new_open = '''    if shop_key == "Weapon":
        try:
            _wire_weapon_shop_buttons(widget, world_ctx)
        except Exception as e:
            _log("wire weapon shop " + str(e))
    elif shop_key == "Armor":
        try:
            _wire_armor_shop_buttons(widget, world_ctx)
        except Exception as e:
            _log("wire armor shop " + str(e))
    return True'''
if old_open not in t:
    raise SystemExit("open_shop wire block missing")
t = t.replace(old_open, new_open, 1)

# clear_progress reset shield
old_clear = '''def clear_progress(world_ctx=None):
    """Wipe run state: gold -> DEFAULT_GOLD, inventory empty, default sword."""
    _PLAYER_META["gold"] = int(DEFAULT_GOLD)
    _PLAYER_META["inventory"] = []
    _PLAYER_META["equipped_sword"] = "SM_KayKitSword"'''
# read actual clear_progress
m = re.search(r"def clear_progress\(world_ctx=None\):.*?_PLAYER_META\[\"equipped_sword\"\] = \"SM_KayKitSword\"", t, re.S)
if not m:
    # try find loosely
    idx = t.find("def clear_progress")
    print("CLEAR SNIP", repr(t[idx:idx+350]))
    raise SystemExit("clear_progress block not found")
# just add after equipped_sword line if missing
if 'equipped_shield' not in t[t.find("def clear_progress"):t.find("def clear_progress")+500]:
    t = t.replace(
        '_PLAYER_META["equipped_sword"] = "SM_KayKitSword"',
        '_PLAYER_META["equipped_sword"] = "SM_KayKitSword"\n'
        '    _PLAYER_META["equipped_shield"] = DEFAULT_SHIELD_ITEM',
        1,
    )

# ensure_equipped_pawn_class applies shield too
old_ens = '''def ensure_equipped_pawn_class(world_ctx, force=False):
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
    return apply_equipped_sword_look(pawn, world_ctx)'''
new_ens = '''def ensure_equipped_pawn_class(world_ctx, force=False):
    """Keep current pawn; apply sword+shield look from authored BPs (no class swap)."""
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
    ok_s = apply_equipped_sword_look(pawn, world_ctx)
    ok_h = False
    try:
        ok_h = apply_equipped_shield_look(pawn, world_ctx)
    except Exception as e:
        _log("ensure shield look " + str(e))
    return bool(ok_s or ok_h)'''
if old_ens not in t:
    raise SystemExit("ensure_equipped_pawn_class missing")
t = t.replace(old_ens, new_ens, 1)

# tick poll armor
old_poll = '''    try:
        if _OPEN_WIDGET[0] is not None:
            _poll_weapon_shop_buy(world)
    except Exception as e:
        _log("poll weapon shop " + str(e))'''
new_poll = '''    try:
        if _OPEN_WIDGET[0] is not None:
            _poll_weapon_shop_buy(world)
    except Exception as e:
        _log("poll weapon shop " + str(e))
    try:
        if _OPEN_WIDGET[0] is not None:
            _poll_armor_shop_buy(world)
    except Exception as e:
        _log("poll armor shop " + str(e))'''
if old_poll not in t:
    raise SystemExit("poll weapon block missing")
t = t.replace(old_poll, new_poll, 1)

# reset shield btn on close-ish places that clear sword btn
if "_SHOP_BTN_SHIELD1[0] = None" not in t:
    t = t.replace(
        "_SHOP_BTN_SWORD1[0] = None\n"
        "_SHOP_BTN_SWORD1_DOWN[0] = False",
        "_SHOP_BTN_SWORD1[0] = None\n"
        "_SHOP_BTN_SWORD1_DOWN[0] = False\n"
        "_SHOP_BTN_SHIELD1[0] = None\n"
        "_SHOP_BTN_SHIELD1_DOWN[0] = False",
        1,
    )

open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("OK", "buy_shield1" in t, "T346_SHIELD1" in t, "SHIELD1_ITEM" in t, "apply_equipped_shield_look" in t)
