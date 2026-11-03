# -*- coding: utf-8 -*-
from __future__ import print_function
import shutil
from pathlib import Path

src = Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py")
docs = Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py")
bak = Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py.pre_t290_dist")

text = src.read_text(encoding="utf-8")
if "T290_DIST_SCALE" in text and "ENEMY_HP_BAR_REF_DISTANCE" in text:
    print("ALREADY_PATCHED")
else:
    shutil.copy2(str(src), str(bak))
    print("backup", bak)

    old_hdr = (
        "# T285: enemy HP = TRUE screen overlay (ProjectWorldToScreen + AddToViewport), fixed pixels.\n"
        "#       NO WidgetComponent World/Screen 3D plane (that still tilted / perspective).\n"
        "#       Each tick: head world loc -> project -> set_position_in_viewport; purge dead actors.\n"
        "# T288: ENEMY_HP_BAR_Z_OFFSET (file top) or BP HealthBarHeightOffset = simple height knob.\n"
        "# T278: after OpenLevel Hub<->Map_Dungeon1, clear HUD/enemy caches and recreate ensure_health_hud.\n"
    )
    new_hdr = (
        "# T285: enemy HP = TRUE screen overlay (ProjectWorldToScreen + AddToViewport).\n"
        "#       NO WidgetComponent World/Screen 3D plane (that still tilted / perspective).\n"
        "#       Each tick: head world loc -> project -> set_position_in_viewport; purge dead actors.\n"
        "# T288: ENEMY_HP_BAR_Z_OFFSET (file top) or BP HealthBarHeightOffset = simple height knob.\n"
        "# T290: distance scale like world nameplate — near=big far=small (still flat screen HUD).\n"
        "#       ENEMY_HP_BAR_REF_DISTANCE / MIN_SCALE / MAX_SCALE at file top.\n"
        "# T278: after OpenLevel Hub<->Map_Dungeon1, clear HUD/enemy caches and recreate ensure_health_hud.\n"
    )
    if old_hdr not in text:
        raise SystemExit("header block not found")
    text = text.replace(old_hdr, new_hdr, 1)

    old_const = (
        "ENEMY_HP_BAR_Z_OFFSET = 40.0\n"
        "_ENEMY_BODY_FALLBACK_Z = 120.0  # only if no head bone/bounds (from mesh/actor root)\n"
        "_ENEMY_BAR_Z = ENEMY_HP_BAR_Z_OFFSET  # alias for older call sites\n"
        "_ENEMY_DRAW = (140.0, 16.0)\n"
    )
    new_const = (
        "ENEMY_HP_BAR_Z_OFFSET = 40.0\n"
        "_ENEMY_BODY_FALLBACK_Z = 120.0  # only if no head bone/bounds (from mesh/actor root)\n"
        "_ENEMY_BAR_Z = ENEMY_HP_BAR_Z_OFFSET  # alias for older call sites\n"
        "_ENEMY_DRAW = (140.0, 16.0)\n"
        "# ============================================================\n"
        "# 距离缩放（像头顶铭牌）：近大远小，仍是贴屏平面不透视歪斜\n"
        "# REF_DISTANCE = 参考距离(cm)，大约在这个距离时血条≈当前默认大小\n"
        "# MIN/MAX_SCALE = 缩放上下限，拉开走近/走远的视觉差\n"
        "# ============================================================\n"
        "ENEMY_HP_BAR_REF_DISTANCE = 500.0  # cm; mid-range fight look ~ current size\n"
        "ENEMY_HP_BAR_MIN_SCALE = 0.30\n"
        "ENEMY_HP_BAR_MAX_SCALE = 2.50\n"
    )
    if old_const not in text:
        raise SystemExit("const block not found")
    text = text.replace(old_const, new_const, 1)

    # Insert helpers before _project_head_to_screen
    anchor = "def _project_head_to_screen(pc, world_loc):\n"
    helpers = '''def _pc_camera_world_loc(pc):
    """Player camera world location for distance scale (nameplate feel)."""
    if pc is None:
        return None
    try:
        pcm = pc.get_editor_property("player_camera_manager")
        if pcm is not None:
            loc = pcm.get_camera_location()
            if loc is not None:
                return loc
    except Exception:
        pass
    try:
        pcm = pc.player_camera_manager
        if pcm is not None:
            loc = pcm.get_camera_location()
            if loc is not None:
                return loc
    except Exception:
        pass
    try:
        out = pc.get_player_view_point()
        if isinstance(out, (tuple, list)) and out:
            return out[0]
        if out is not None and hasattr(out, "x"):
            return out
    except Exception:
        pass
    try:
        pawn = None
        try:
            pawn = pc.get_controlled_pawn()
        except Exception:
            pawn = None
        if pawn is None:
            try:
                pawn = pc.k2_get_pawn()
            except Exception:
                try:
                    pawn = pc.get_pawn()
                except Exception:
                    pawn = None
        if pawn is not None:
            return pawn.get_actor_location()
    except Exception:
        pass
    return None


def _enemy_bar_dist_scale(cam_loc, head_loc):
    """scale = clamp(REF / distance). Near -> large, far -> small (world nameplate feel)."""
    if cam_loc is None or head_loc is None:
        return 1.0
    try:
        d = float(_dist(cam_loc, head_loc))
    except Exception:
        return 1.0
    if d < 1.0:
        d = 1.0
    s = float(ENEMY_HP_BAR_REF_DISTANCE) / d
    if s < float(ENEMY_HP_BAR_MIN_SCALE):
        s = float(ENEMY_HP_BAR_MIN_SCALE)
    if s > float(ENEMY_HP_BAR_MAX_SCALE):
        s = float(ENEMY_HP_BAR_MAX_SCALE)
    return s


def _apply_enemy_bar_scale(widget, pb, scale):
    """Flat HUD: RenderTransform scale around bottom-center; fallback resize draw size."""
    if widget is None:
        return float(_ENEMY_DRAW[0]), float(_ENEMY_DRAW[1])
    s = float(scale)
    if s < 0.05:
        s = 0.05
    base_w = float(_ENEMY_DRAW[0])
    base_h = float(_ENEMY_DRAW[1])
    used_render = False
    try:
        widget.set_render_transform_pivot(unreal.Vector2D(0.5, 1.0))
        used_render = True
    except Exception:
        try:
            widget.set_editor_property("render_transform_pivot", unreal.Vector2D(0.5, 1.0))
            used_render = True
        except Exception:
            used_render = False
    if used_render:
        try:
            widget.set_render_scale(unreal.Vector2D(s, s))
        except Exception:
            try:
                rt = unreal.WidgetTransform()
                rt.scale = unreal.Vector2D(s, s)
                widget.set_editor_property("render_transform", rt)
            except Exception:
                used_render = False
    # Always keep layout size = base when using render scale; else scale layout size
    draw_w = base_w
    draw_h = base_h
    if not used_render:
        draw_w = base_w * s
        draw_h = base_h * s
        if pb is not None:
            slot = None
            try:
                slot = unreal.WidgetLayoutLibrary.slot_as_canvas_slot(pb)
            except Exception:
                slot = None
            if slot is not None:
                try:
                    slot.set_size(unreal.Vector2D(draw_w, draw_h))
                except Exception:
                    pass
    try:
        widget.set_desired_size_in_viewport(unreal.Vector2D(draw_w, draw_h))
    except Exception:
        pass
    return draw_w, draw_h


'''
    if "def _enemy_bar_dist_scale(" in text:
        print("helpers already present")
    else:
        if anchor not in text:
            raise SystemExit("project fn not found")
        text = text.replace(anchor, helpers + anchor, 1)

    # Update ensure_enemy_health_bars docstring
    old_doc = (
        '    """T285: flat screen HUD bars above live skeleton heads via ProjectWorldToScreen.\n'
        '    Fixed pixel size; no WidgetComponent plane. Purge bars whose actors died / left level.\n'
        '    """\n'
    )
    new_doc = (
        '    """T285/T290: flat screen HUD bars above live skeleton heads via ProjectWorldToScreen.\n'
        '    Distance-scaled (near=big far=small) like a world nameplate; no tilted WidgetComponent.\n'
        '    Purge bars whose actors died / left level. Tag: T290_DIST_SCALE.\n'
        '    """\n'
    )
    if old_doc in text:
        text = text.replace(old_doc, new_doc, 1)
    else:
        print("WARN: docstring not exact, continuing")

    # Replace projection/position block inside ensure_enemy_health_bars
    old_proj = '''        head = _enemy_head_world_loc(actor)
        ok, sx, sy = _project_head_to_screen(pc, head)
        if ok:
            px = sx - float(_ENEMY_DRAW[0]) * 0.5
            py = sy - float(_ENEMY_DRAW[1]) - 4.0
            try:
                widget.set_visibility(unreal.SlateVisibility.HIT_TEST_INVISIBLE)
            except Exception:
                try:
                    widget.set_visibility(unreal.SlateVisibility.VISIBLE)
                except Exception:
                    pass
            try:
                widget.set_position_in_viewport(unreal.Vector2D(px, py), False)
            except Exception as e:
                try:
                    widget.set_position_in_viewport(unreal.Vector2D(px, py), True)
                except Exception as e2:
                    _log("enemy screen pos " + str(e2))
            try:
                widget.set_desired_size_in_viewport(
                    unreal.Vector2D(float(_ENEMY_DRAW[0]), float(_ENEMY_DRAW[1]))
                )
            except Exception:
                pass
        else:
'''
    new_proj = '''        head = _enemy_head_world_loc(actor)
        ok, sx, sy = _project_head_to_screen(pc, head)
        if ok:
            cam = _pc_camera_world_loc(pc)
            scale = _enemy_bar_dist_scale(cam, head)
            draw_w, draw_h = _apply_enemy_bar_scale(widget, pb, scale)
            # Bottom-center of bar sits just above projected head (nameplate anchor)
            px = sx - float(draw_w) * 0.5
            py = sy - float(draw_h) - 4.0
            try:
                widget.set_visibility(unreal.SlateVisibility.HIT_TEST_INVISIBLE)
            except Exception:
                try:
                    widget.set_visibility(unreal.SlateVisibility.VISIBLE)
                except Exception:
                    pass
            try:
                widget.set_position_in_viewport(unreal.Vector2D(px, py), False)
            except Exception as e:
                try:
                    widget.set_position_in_viewport(unreal.Vector2D(px, py), True)
                except Exception as e2:
                    _log("enemy screen pos " + str(e2))
        else:
'''
    if old_proj not in text:
        raise SystemExit("proj block not found")
    text = text.replace(old_proj, new_proj, 1)

    # Update bootstrap log tags
    text = text.replace(
        "tick registered SPLIT_WBP_V15e_T285_PROJECT_HUD_T288_OFFSET gen=%s",
        "tick registered SPLIT_WBP_V15e_T290_DIST_SCALE gen=%s",
    )
    text = text.replace(
        'runtime ready SPLIT_WBP_V15e_T285_PROJECT_HUD_T288_OFFSET"',
        'runtime ready SPLIT_WBP_V15e_T290_DIST_SCALE"',
    )

    if "T290_DIST_SCALE" not in text:
        raise SystemExit("tag missing after patch")
    if "ENEMY_HP_BAR_REF_DISTANCE" not in text:
        raise SystemExit("ref distance missing")
    if "_enemy_bar_dist_scale" not in text:
        raise SystemExit("helper missing")

    src.write_text(text, encoding="utf-8")
    shutil.copy2(str(src), str(docs))
    print("PATCHED", src)
    print("SYNCED", docs)
    print("len", len(text))
