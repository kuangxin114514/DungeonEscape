# -*- coding: utf-8 -*-
from __future__ import print_function
import shutil
import os

SRC = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
BAK = SRC + ".pre_t313"
OUT_LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\patch_t313_gold_right.txt"

lines_log = []

def log(m):
    lines_log.append(str(m))
    print(m)

with open(SRC, "r", encoding="utf-8") as f:
    text = f.read()

shutil.copy2(SRC, BAK)
log("backup " + BAK)

HELPER = '''
def _viewport_size_xy(world_ctx):
    """DPI-aware viewport size for HUD pinning. T313_GOLD_RIGHT."""
    try:
        sz = unreal.WidgetLayoutLibrary.get_viewport_size(world_ctx)
        x = float(sz.x)
        y = float(sz.y)
        if x > 32.0 and y > 32.0:
            return x, y
    except Exception:
        pass
    try:
        # Some builds expose get_viewport_widget_geometry
        geo = unreal.WidgetLayoutLibrary.get_viewport_widget_geometry(world_ctx)
        sz = geo.get_local_size()
        x = float(sz.x)
        y = float(sz.y)
        if x > 32.0 and y > 32.0:
            return x, y
    except Exception:
        pass
    return 1920.0, 1080.0


def _pin_gold_widget_top_right(widget, world_ctx):
    """Pin entire gold UserWidget to true viewport TOP-RIGHT (not left canvas). T313_GOLD_RIGHT."""
    if widget is None:
        return
    vx, vy = _viewport_size_xy(world_ctx if world_ctx is not None else widget)
    try:
        widget.set_desired_size_in_viewport(unreal.Vector2D(280.0, 56.0))
    except Exception:
        pass
    try:
        # Pivot = top-right corner of the widget
        widget.set_alignment_in_viewport(unreal.Vector2D(1.0, 0.0))
    except Exception:
        pass
    px = float(vx) - 24.0
    if px < 120.0:
        px = float(vx) * 0.98
    py = 36.0
    try:
        widget.set_position_in_viewport(unreal.Vector2D(px, py), True)
    except Exception:
        try:
            widget.set_position_in_viewport(unreal.Vector2D(px, py))
        except Exception:
            pass


def _layout_gold_text_in_small_widget(txt):
    """Text sits top-left inside the small gold widget (widget itself is top-right)."""
    if txt is None or getattr(txt, "slot", None) is None:
        return
    slot = None
    try:
        slot = unreal.WidgetLayoutLibrary.slot_as_canvas_slot(txt)
    except Exception:
        slot = txt.slot
    if slot is None:
        return
    try:
        anc = unreal.Anchors()
        anc.minimum = unreal.Vector2D(0.0, 0.0)
        anc.maximum = unreal.Vector2D(0.0, 0.0)
        slot.set_anchors(anc)
    except Exception:
        try:
            anc = unreal.Anchors()
            anc.minimum = unreal.Vector2D(0.0, 0.0)
            anc.maximum = unreal.Vector2D(0.0, 0.0)
            slot.set_editor_property("anchors", anc)
        except Exception:
            pass
    try:
        slot.set_alignment(unreal.Vector2D(0.0, 0.0))
    except Exception:
        pass
    try:
        # Point-anchor: Right/Bottom = width/height
        slot.set_offsets(unreal.Margin(0.0, 0.0, 280.0, 48.0))
    except Exception:
        try:
            slot.set_position(unreal.Vector2D(0.0, 0.0))
            slot.set_size(unreal.Vector2D(280.0, 48.0))
        except Exception:
            pass
    try:
        slot.set_auto_size(True)
    except Exception:
        pass

'''

# Insert helpers just before ensure_gold_hud if missing
if "_pin_gold_widget_top_right" not in text:
    needle = "def ensure_gold_hud(world, pc, pawn=None):"
    if needle not in text:
        log("FAIL: ensure_gold_hud not found")
        open(OUT_LOG, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")
        raise SystemExit(2)
    text = text.replace(needle, HELPER + "\n" + needle, 1)
    log("inserted helpers")
else:
    log("helpers already present")

# Replace create-time viewport pin block
OLD_CREATE = '''        # Keep full-screen canvas (like health HUD). Do NOT shift widget in viewport
        # that + Shop2 full layout pushed gold off-screen. Point-anchor Margin:
        # Left/Top = pos, Right/Bottom = WIDTH/HEIGHT (must be positive!).
        try:
            widget.set_alignment_in_viewport(unreal.Vector2D(0.0, 0.0))
        except Exception:
            pass
        try:
            widget.set_position_in_viewport(unreal.Vector2D(0.0, 0.0), True)
        except Exception:
            try:
                widget.set_position_in_viewport(unreal.Vector2D(0.0, 0.0))
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
            # Top-right: X=-24 (inset from right with align 1), Y=36, W=240, H=40
            try:
                txt.slot.set_offsets(unreal.Margin(-24.0, 36.0, 240.0, 40.0))
            except Exception:
                try:
                    txt.slot.set_position(unreal.Vector2D(-24.0, 36.0))
                    txt.slot.set_size(unreal.Vector2D(240.0, 40.0))
                except Exception:
                    pass
            try:
                txt.slot.set_auto_size(True)
            except Exception:
                pass
            try:
                txt.set_visibility(unreal.SlateVisibility.VISIBLE)
            except Exception:
                pass
            # High-contrast gold text in case Designer color was transparent
            try:
                txt.set_editor_property(
                    "color_and_opacity",
                    unreal.SlateColor(unreal.LinearColor(1.0, 0.9, 0.2, 1.0)),
                )
            except Exception:
                pass
            try:
                font = txt.get_editor_property("font")
                font.set_editor_property("size", 28)
                txt.set_editor_property("font", font)
            except Exception:
                pass
        _log("ensure_gold_hud created %s txt=%s T312_GOLD5" % (wpath, txt))'''

NEW_CREATE = '''        # T313_GOLD_RIGHT: pin WHOLE widget to viewport top-RIGHT.
        # (Previously widget sat at 0,0 left; text "right" anchor only meant right of a left-sized box.)
        try:
            _pin_gold_widget_top_right(widget, world)
        except Exception as e:
            _log("gold pin create " + str(e))
        try:
            _layout_gold_text_in_small_widget(txt)
        except Exception as e:
            _log("gold txt layout " + str(e))
        if txt is not None:
            try:
                txt.set_visibility(unreal.SlateVisibility.VISIBLE)
            except Exception:
                pass
            # High-contrast gold text in case Designer color was transparent
            try:
                txt.set_editor_property(
                    "color_and_opacity",
                    unreal.SlateColor(unreal.LinearColor(1.0, 0.9, 0.2, 1.0)),
                )
            except Exception:
                pass
            try:
                font = txt.get_editor_property("font")
                font.set_editor_property("size", 28)
                txt.set_editor_property("font", font)
            except Exception:
                pass
        _log("ensure_gold_hud created %s txt=%s T313_GOLD_RIGHT" % (wpath, txt))'''

# The file may have a special dash character that broke my OLD_CREATE - match more flexibly
marker_a = "Keep full-screen canvas (like health HUD). Do NOT shift widget in viewport"
marker_b = '_log("ensure_gold_hud created %s txt=%s T312_GOLD5" % (wpath, txt))'
idx_a = text.find(marker_a)
idx_b = text.find(marker_b)
if idx_a < 0 or idx_b < 0:
    log("FAIL markers create idx_a=%s idx_b=%s" % (idx_a, idx_b))
    # show nearby
    i = text.find("set_alignment_in_viewport(unreal.Vector2D(0.0, 0.0))")
    log("alt align0 idx=%s" % i)
    open(OUT_LOG, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")
    raise SystemExit(3)

# Include leading spaces before marker_a: find start of comment line
line_start = text.rfind("\n", 0, idx_a) + 1
end = idx_b + len(marker_b)
old_chunk = text[line_start:end]
log("create chunk len=%d" % len(old_chunk))
text = text[:line_start] + NEW_CREATE + text[end:]
log("replaced create-time pin")

OLD_TICK = '''        # Keep top-right slot valid every tick (Designer/Shop2 offsets can regress)
        try:
            if getattr(txt, "slot", None) is not None:
                anc = unreal.Anchors()
                anc.minimum = unreal.Vector2D(1.0, 0.0)
                anc.maximum = unreal.Vector2D(1.0, 0.0)
                try:
                    txt.slot.set_anchors(anc)
                except Exception:
                    pass
                try:
                    txt.slot.set_alignment(unreal.Vector2D(1.0, 0.0))
                except Exception:
                    pass
                try:
                    txt.slot.set_offsets(unreal.Margin(-24.0, 36.0, 240.0, 40.0))
                except Exception:
                    try:
                        txt.slot.set_position(unreal.Vector2D(-24.0, 36.0))
                        txt.slot.set_size(unreal.Vector2D(240.0, 40.0))
                    except Exception:
                        pass
        except Exception:
            pass'''

NEW_TICK = '''        # Keep widget pinned top-RIGHT every tick (resize / layout regress)
        try:
            wpin = _GOLD_WIDGET[0]
            if wpin is not None and _uobj_alive(wpin):
                _pin_gold_widget_top_right(wpin, world)
        except Exception:
            pass
        try:
            _layout_gold_text_in_small_widget(txt)
        except Exception:
            pass'''

if OLD_TICK not in text:
    log("FAIL tick block not exact match")
    # try find start
    mt = text.find("Keep top-right slot valid every tick")
    log("tick marker idx=%s" % mt)
    open(OUT_LOG, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")
    raise SystemExit(4)

text = text.replace(OLD_TICK, NEW_TICK, 1)
log("replaced tick pin")

# Tag bumps
text = text.replace("SPLIT_WBP_V15e_T312_GOLD5", "SPLIT_WBP_V15e_T313_GOLD_RIGHT")
# header comment
if "T313_GOLD_RIGHT" not in text.split("\n", 40)[0:40].__str__() if False else True:
    pass
old_hdr = "# T312_GOLD5: fix gold TextBlock canvas size (point-anchor Right/Bottom = width/height); DEFAULT_GOLD=5; meta JSON source-of-truth."
new_hdr = "# T312_GOLD5: fix gold TextBlock canvas size (point-anchor Right/Bottom = width/height); DEFAULT_GOLD=5; meta JSON source-of-truth.\n# T313_GOLD_RIGHT: pin WBP_PlayerGold UserWidget to true viewport TOP-RIGHT (was under HP on left)."
if old_hdr in text and "T313_GOLD_RIGHT: pin WBP_PlayerGold" not in text:
    text = text.replace(old_hdr, new_hdr, 1)
    log("header note added")

# docstring
text = text.replace(
    '"""Screen-space Gold text fixed top-RIGHT. Recreates after OpenLevel travel. T311_GOLD_HUD."""',
    '"""Screen-space Gold text fixed top-RIGHT. Recreates after OpenLevel travel. T313_GOLD_RIGHT."""',
    1,
)

# Ensure DEFAULT_GOLD still 5
if "DEFAULT_GOLD = 5" not in text:
    log("WARN DEFAULT_GOLD not 5")
else:
    log("DEFAULT_GOLD=5 ok")

with open(SRC, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
log("wrote " + SRC)
log("has_pin=%s" % ("_pin_gold_widget_top_right" in text))
log("has_T313=%s" % ("T313_GOLD_RIGHT" in text))
log("no_old_align0_gold=%s" % (text.count("Keep full-screen canvas (like health HUD)") == 0))

# Also sync Docs copy if present
docs = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py"
try:
    shutil.copy2(SRC, docs)
    log("synced Docs copy")
except Exception as e:
    log("docs sync skip " + str(e))

open(OUT_LOG, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")
print("OK")
