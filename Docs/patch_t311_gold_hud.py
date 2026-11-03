# -*- coding: utf-8 -*-
"""Patch shop_interact_runtime.py for T311 top-right Gold HUD."""
from __future__ import print_function
import io
import os

PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\patch_t311.txt"
lines_log = []

def log(m):
    lines_log.append(str(m))
    print(m)

def main():
    src = io.open(PATH, "r", encoding="utf-8").read()
    orig = src

    if "T311_GOLD_HUD" in src and "ensure_gold_hud" in src:
        log("already patched")
        io.open(LOG, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")
        return

    # Header note
    needle = "# T309: GI_DungeonGame Gold/Inventory via player_meta helpers (OpenLevel-safe); dungeon exit E -> Map_Dungeon2.\n#       ClearProgress for new-save later. Map_Hub buildings untouched."
    insert_hdr = needle + "\n# T311_GOLD_HUD: screen Gold text top-RIGHT (WBP_PlayerGold / fallback health WBP); sync get_gold each tick; survive OpenLevel."
    if "T311_GOLD_HUD" not in src:
        if needle in src:
            src = src.replace(needle, insert_hdr, 1)
            log("hdr ok")
        else:
            log("hdr MISSING")

    # Globals after _HEALTH_TXT
    g_old = (
        "_HEALTH_WIDGET = [None]\n"
        "_HEALTH_BAR = [None]\n"
        "_HEALTH_TXT = [None]\n"
        "HEALTH_WBP_PATHS = (\n"
        '    "/Game/UI/HUD/WBP_PlayerHealthBar.WBP_PlayerHealthBar_C",\n'
        '    "/Game/UI/HUD/WBP_PlayerHealthBar_C",\n'
        ")"
    )
    g_new = (
        "_HEALTH_WIDGET = [None]\n"
        "_HEALTH_BAR = [None]\n"
        "_HEALTH_TXT = [None]\n"
        "_GOLD_WIDGET = [None]\n"
        "_GOLD_TXT = [None]\n"
        "HEALTH_WBP_PATHS = (\n"
        '    "/Game/UI/HUD/WBP_PlayerHealthBar.WBP_PlayerHealthBar_C",\n'
        '    "/Game/UI/HUD/WBP_PlayerHealthBar_C",\n'
        ")\n"
        "GOLD_WBP_PATHS = (\n"
        '    "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C",\n'
        '    "/Game/UI/HUD/WBP_PlayerGold_C",\n'
        '    "/Game/UI/HUD/WBP_PlayerHealthBar.WBP_PlayerHealthBar_C",\n'
        '    "/Game/UI/HUD/WBP_PlayerHealthBar_C",\n'
        ")"
    )
    if "_GOLD_WIDGET" not in src:
        if g_old in src:
            src = src.replace(g_old, g_new, 1)
            log("globals ok")
        else:
            log("globals MISSING")

    # _clear_health_hud -> also clear gold; insert _clear_gold_hud after _clear_health_hud
    clear_fn = '''
def _clear_gold_hud():
    w = _GOLD_WIDGET[0]
    _GOLD_WIDGET[0] = None
    _GOLD_TXT[0] = None
    if w is None:
        return
    if not _uobj_alive(w):
        return
    try:
        w.remove_from_viewport()
    except Exception:
        try:
            w.remove_from_parent()
        except Exception:
            pass


'''
    if "def _clear_gold_hud" not in src:
        marker = "def ensure_health_hud(world, pc, pawn):"
        if marker in src:
            src = src.replace(marker, clear_fn + marker, 1)
            log("clear_gold_hud ok")
        else:
            log("clear_gold insert MISSING")

    # Call clear gold from _clear_health_hud? Better from _reset and bootstrap and ensure separately.
    # Patch _reset_ui_after_travel
    reset_old = '''    try:
        _clear_health_hud()
    except Exception:
        pass
    try:
        _clear_enemy_bars()
    except Exception:
        pass'''
    reset_new = '''    try:
        _clear_health_hud()
    except Exception:
        pass
    try:
        _clear_gold_hud()
    except Exception:
        pass
    try:
        _clear_enemy_bars()
    except Exception:
        pass'''
    if "_clear_gold_hud()" not in src.split("def _reset_ui_after_travel")[1][:800] if "def _reset_ui_after_travel" in src else "":
        pass
    if "T311 reset" not in src:
        if reset_old in src:
            src = src.replace(reset_old, reset_new, 1)
            log("reset clear gold ok")
        else:
            # try only first occurrence context
            if "_clear_health_hud()" in src and "_clear_gold_hud()" not in src[src.find("def _reset_ui_after_travel"):src.find("def _reset_ui_after_travel")+600]:
                idx = src.find("def _reset_ui_after_travel")
                chunk = src[idx:idx+700]
                if reset_old in chunk:
                    src = src[:idx] + chunk.replace(reset_old, reset_new, 1) + src[idx+700:]
                    log("reset clear gold ok (chunk)")
                else:
                    log("reset pattern MISSING; chunk=\n" + chunk[:400])
            else:
                log("reset maybe already or weird")

    GOLD_FUNCS = r'''
def _load_gold_wbp_class():
    for p in GOLD_WBP_PATHS:
        try:
            cls = unreal.load_class(None, p)
            if cls:
                return cls, p
        except Exception:
            pass
    for asset_path in (
        "/Game/UI/HUD/WBP_PlayerGold",
        "/Game/UI/HUD/WBP_PlayerHealthBar",
    ):
        try:
            wbp = unreal.EditorAssetLibrary.load_asset(asset_path)
            if not wbp:
                continue
            try:
                unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
            except Exception:
                pass
            gc = None
            try:
                gc = wbp.generated_class()
            except Exception:
                gc = None
            if gc:
                return gc, gc.get_path_name()
        except Exception as e:
            _log("gold wbp load " + str(e))
    return None, None


def ensure_gold_hud(world, pc, pawn=None):
    """Screen-space Gold text fixed top-RIGHT. Recreates after OpenLevel travel. T311_GOLD_HUD."""
    if world is None or pc is None:
        return
    try:
        ensure_player_meta(world)
    except Exception:
        pass

    w_existing = _GOLD_WIDGET[0]
    if w_existing is not None:
        alive = _uobj_alive(w_existing)
        if not alive:
            _log("ensure_gold_hud: dead HUD ref -> recreate")
            _GOLD_WIDGET[0] = None
            _GOLD_TXT[0] = None
        else:
            in_vp = True
            try:
                in_vp = bool(w_existing.is_in_viewport())
            except Exception:
                in_vp = True
            if not in_vp:
                try:
                    w_existing.add_to_viewport(51)
                    _log("ensure_gold_hud: re-AddToViewport")
                except Exception as e:
                    _log("ensure_gold_hud: reattach fail " + str(e) + " -> recreate")
                    try:
                        w_existing.remove_from_viewport()
                    except Exception:
                        pass
                    _GOLD_WIDGET[0] = None
                    _GOLD_TXT[0] = None

    if _GOLD_WIDGET[0] is None:
        wcls, wpath = _load_gold_wbp_class()
        if not wcls:
            _log("ensure_gold_hud: no WBP class")
            return
        widget = None
        wbl = _wbl()
        if wbl:
            for attempt in (
                lambda: wbl.call_method(
                    "create", (),
                    {"world_context_object": world, "widget_type": wcls, "owning_player": pc},
                ),
                lambda: wbl.call_method(
                    "create", (),
                    {"world_context_object": pc, "widget_type": wcls, "owning_player": pc},
                ),
                lambda: wbl.call_method("create", (world, wcls, pc)),
                lambda: wbl.call_method("create", (pc, wcls, pc)),
            ):
                try:
                    widget = attempt()
                    if widget:
                        break
                except Exception as e:
                    _log("gold create " + str(e))
        if not widget:
            try:
                widget = unreal.new_object(wcls, pc)
            except Exception as e:
                _log("gold new_object " + str(e))
                return
        if not widget:
            _log("ensure_gold_hud create null")
            return
        try:
            widget.set_visibility(unreal.SlateVisibility.VISIBLE)
        except Exception:
            pass
        try:
            widget.add_to_viewport(51)
        except Exception as e:
            _log("gold viewport " + str(e))
            return
        _GOLD_WIDGET[0] = widget

        # Prefer Txt_Gold; else Txt_HP (health WBP fallback)
        txt = None
        for nm in ("Txt_Gold", "Txt_HP"):
            try:
                txt = widget.get_widget_from_name(nm)
            except Exception:
                txt = None
            if txt is None:
                try:
                    txt = _find_named_widget(widget, nm)
                except Exception:
                    txt = None
            if txt is not None:
                break
        _GOLD_TXT[0] = txt

        # Hide progress bar if we fell back to health WBP instance
        pb = None
        try:
            pb = widget.get_widget_from_name("PB_Health")
        except Exception:
            pb = None
        if pb is None:
            try:
                pb = _find_named_widget(widget, "PB_Health")
            except Exception:
                pb = None
        if pb is not None:
            try:
                pb.set_visibility(unreal.SlateVisibility.COLLAPSED)
            except Exception:
                try:
                    pb.set_visibility(unreal.SlateVisibility.HIDDEN)
                except Exception:
                    pass

        # Force top-right for the text (and widget alignment)
        try:
            widget.set_alignment_in_viewport(unreal.Vector2D(1.0, 0.0))
        except Exception:
            pass
        try:
            # Near top-right corner; negative X with align 1 = inset from right
            widget.set_position_in_viewport(unreal.Vector2D(-48.0, 36.0), True)
        except Exception:
            try:
                widget.set_position_in_viewport(unreal.Vector2D(-48.0, 36.0))
            except Exception:
                pass
        if txt is not None and getattr(txt, "slot", None) is not None:
            try:
                anc = unreal.Anchors()
                anc.minimum = unreal.Vector2D(1.0, 0.0)
                anc.maximum = unreal.Vector2D(1.0, 0.0)
                txt.slot.set_anchors(anc)
            except Exception:
                pass
            try:
                txt.slot.set_alignment(unreal.Vector2D(1.0, 0.0))
            except Exception:
                pass
            try:
                txt.slot.set_offsets(unreal.Margin(-268.0, 36.0, -48.0, 76.0))
            except Exception:
                try:
                    txt.slot.set_position(unreal.Vector2D(-268.0, 36.0))
                    txt.slot.set_size(unreal.Vector2D(220.0, 40.0))
                except Exception:
                    pass
            try:
                txt.set_visibility(unreal.SlateVisibility.VISIBLE)
            except Exception:
                pass
        _log("ensure_gold_hud created %s txt=%s T311_GOLD_HUD" % (wpath, txt))

    # Refresh gold number every tick
    try:
        gold = int(get_gold(world))
    except Exception:
        gold = int(DEFAULT_GOLD)
    label = u"金币: %d" % gold
    txt = _GOLD_TXT[0]
    if txt is not None:
        try:
            txt.set_text(unreal.Text(label))
        except Exception:
            try:
                txt.set_editor_property("text", unreal.Text(label))
            except Exception:
                pass
    else:
        # Last resort: keep widget alive; print once rarely via log throttle not needed
        pass


'''

    if "def ensure_gold_hud" not in src:
        # Insert after ensure_health_hud ends — before _load_enemy_health_wbp_class
        marker = "def _load_enemy_health_wbp_class():"
        if marker in src:
            src = src.replace(marker, GOLD_FUNCS + "\n" + marker, 1)
            log("ensure_gold_hud ok")
        else:
            log("ensure_gold insert marker MISSING")

    # Tick: call ensure_gold_hud after ensure_health_hud
    tick_old = '''    # Screen HUD health bar (top-left). Safe: uses existing WBP + PB_Health.
    if pawn is not None:
        try:
            ensure_health_hud(world, pc, pawn)
        except Exception as e:
            _log("ensure_health_hud " + str(e))
    # Enemy flat screen HP bars (ProjectWorldToScreen) above skeleton heads'''
    tick_new = '''    # Screen HUD health bar (top-left). Safe: uses existing WBP + PB_Health.
    if pawn is not None:
        try:
            ensure_health_hud(world, pc, pawn)
        except Exception as e:
            _log("ensure_health_hud " + str(e))
    # T311_GOLD_HUD: Gold top-right (independent of pawn Health vars)
    try:
        ensure_gold_hud(world, pc, pawn)
    except Exception as e:
        _log("ensure_gold_hud " + str(e))
    # Enemy flat screen HP bars (ProjectWorldToScreen) above skeleton heads'''
    if "ensure_gold_hud(world, pc, pawn)" not in src.split("def _on_tick")[1] if "def _on_tick" in src else "":
        pass
    if "T311_GOLD_HUD: Gold top-right" not in src:
        if tick_old in src:
            src = src.replace(tick_old, tick_new, 1)
            log("tick ok")
        else:
            log("tick pattern MISSING")

    # Also clear gold when pie_world_none clears health
    pie_old = '''        elif _HEALTH_WIDGET[0] is not None:
            _clear_health_hud()'''
    pie_new = '''        elif _HEALTH_WIDGET[0] is not None or _GOLD_WIDGET[0] is not None:
            _clear_health_hud()
            try:
                _clear_gold_hud()
            except Exception:
                pass'''
    if pie_old in src and "_GOLD_WIDGET[0] is not None" not in src[src.find("def _on_tick"):src.find("def _on_tick")+900]:
        src = src.replace(pie_old, pie_new, 1)
        log("pie clear ok")
    else:
        if "_GOLD_WIDGET[0] is not None" in src:
            log("pie clear already")
        else:
            log("pie clear skip/missing")

    # First bind after travel also clears gold
    bind_old = '''            _clear_health_hud()
            _clear_enemy_bars()
            _DUNGEON_PAWN_TRIED[0] = False'''
    bind_new = '''            _clear_health_hud()
            try:
                _clear_gold_hud()
            except Exception:
                pass
            _clear_enemy_bars()
            _DUNGEON_PAWN_TRIED[0] = False'''
    if bind_old in src and src.count("_clear_gold_hud()") < 2:
        # may already have one from reset
        src = src.replace(bind_old, bind_new, 1)
        log("bind clear ok")
    else:
        log("bind clear note count=%s" % src.count("_clear_gold_hud()"))

    # bootstrap clear + tag
    boot_old = '''    _clear_health_hud()
    _clear_enemy_bars()
    _PENDING_ATTACK_HIT[0] = None'''
    boot_new = '''    _clear_health_hud()
    try:
        _clear_gold_hud()
    except Exception:
        pass
    _clear_enemy_bars()
    _PENDING_ATTACK_HIT[0] = None'''
    if boot_old in src:
        src = src.replace(boot_old, boot_new, 1)
        log("bootstrap clear ok")
    else:
        log("bootstrap clear MISSING")

    for old_tag, new_tag in (
        ("SPLIT_WBP_V15e_T299_HP50", "SPLIT_WBP_V15e_T311_GOLD_HUD"),
        ("runtime ready SPLIT_WBP_V15e_T299_HP50", "runtime ready SPLIT_WBP_V15e_T311_GOLD_HUD"),
    ):
        if old_tag in src:
            src = src.replace(old_tag, new_tag)
            log("tag -> " + new_tag)

    if src == orig:
        log("NO CHANGES")
    else:
        io.open(PATH, "w", encoding="utf-8", newline="\n").write(src)
        log("wrote %d -> %d bytes" % (len(orig), len(src)))
        log("has ensure_gold_hud=%s" % ("ensure_gold_hud" in src))
        log("has T311_GOLD_HUD=%s" % ("T311_GOLD_HUD" in src))
        log("gold clear count=%s" % src.count("_clear_gold_hud"))

    io.open(LOG, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")

main()