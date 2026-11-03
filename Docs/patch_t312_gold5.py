# -*- coding: utf-8 -*-
from pathlib import Path
import json, os, re

p = Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py")
text = p.read_text(encoding="utf-8")

# 1) header comment bump
text = text.replace(
    "# T311_GOLD_HUD: screen Gold text top-RIGHT (WBP_PlayerGold / fallback health WBP); sync get_gold each tick; survive OpenLevel.",
    "# T311_GOLD_HUD: screen Gold text top-RIGHT (WBP_PlayerGold / fallback health WBP); sync get_gold each tick; survive OpenLevel.\n# T312_GOLD5: fix gold TextBlock canvas size (point-anchor Right/Bottom = width/height); DEFAULT_GOLD=5; meta JSON source-of-truth.",
)

# 2) DEFAULT_GOLD
if "DEFAULT_GOLD = 100" not in text:
    raise SystemExit("DEFAULT_GOLD=100 missing")
text = text.replace("DEFAULT_GOLD = 100", "DEFAULT_GOLD = 5", 1)

# 3) ensure_player_meta: module+JSON wins; push to GI (do not pull GI over defaults)
old_meta = '''def ensure_player_meta(world_ctx=None):
    """Init Gold/Inventory once per session; sync GI if BP vars exist."""
    if not _PLAYER_META["ready"]:
        if not _meta_load_file():
            _PLAYER_META["gold"] = int(DEFAULT_GOLD)
            _PLAYER_META["inventory"] = []
        _PLAYER_META["ready"] = True
    gi = _gi_from_world(world_ctx)
    if gi is not None:
        _meta_pull_gi(gi)
        _meta_push_gi(gi)
    return _PLAYER_META'''

new_meta = '''def ensure_player_meta(world_ctx=None):
    """Init Gold/Inventory once per session. Module+JSON is source of truth; push into GI."""
    if not _PLAYER_META["ready"]:
        if not _meta_load_file():
            _PLAYER_META["gold"] = int(DEFAULT_GOLD)
            _PLAYER_META["inventory"] = []
        _PLAYER_META["ready"] = True
        # Do NOT pull GI here — GI CDO default (often 100) would wipe DEFAULT_GOLD/file.
        gi = _gi_from_world(world_ctx)
        _meta_push_gi(gi)
        _meta_save_file()
    else:
        gi = _gi_from_world(world_ctx)
        _meta_push_gi(gi)
    return _PLAYER_META'''

if old_meta not in text:
    raise SystemExit("ensure_player_meta block not found exactly")
text = text.replace(old_meta, new_meta, 1)

# 4) Fix ensure_gold_hud positioning: remove bad viewport shift + negative width margins
old_pos = '''        # Force top-right for the text (and widget alignment)
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
        _log("ensure_gold_hud created %s txt=%s T311_GOLD_HUD" % (wpath, txt))'''

new_pos = '''        # Keep full-screen canvas (like health HUD). Do NOT shift widget in viewport —
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

if old_pos not in text:
    raise SystemExit("positioning block not found exactly")
text = text.replace(old_pos, new_pos, 1)

# 5) Every-tick: also force widget visible + re-apply slot if text exists (cheap)
old_refresh = '''    # Refresh gold number every tick (rebind TextBlock via ObjectIterator if needed)
    try:
        gold = int(get_gold(world))
    except Exception:
        gold = int(DEFAULT_GOLD)
    label = u"金币: %d" % gold
    txt = _GOLD_TXT[0]
    if txt is None or (not _uobj_alive(txt)):
        try:
            txt = _find_textblock_under(_GOLD_WIDGET[0])
            _GOLD_TXT[0] = txt
        except Exception:
            txt = None
    if txt is not None:
        try:
            txt.set_visibility(unreal.SlateVisibility.VISIBLE)
        except Exception:
            pass
        try:
            txt.set_text(unreal.Text(label))
        except Exception:
            try:
                txt.set_editor_property("text", unreal.Text(label))
            except Exception:
                pass
    else:'''

new_refresh = '''    # Refresh gold number every tick (rebind TextBlock via ObjectIterator if needed)
    try:
        gold = int(get_gold(world))
    except Exception:
        gold = int(DEFAULT_GOLD)
    label = u"金币: %d" % gold
    try:
        wforce = _GOLD_WIDGET[0]
        if wforce is not None and _uobj_alive(wforce):
            wforce.set_visibility(unreal.SlateVisibility.VISIBLE)
    except Exception:
        pass
    txt = _GOLD_TXT[0]
    if txt is None or (not _uobj_alive(txt)):
        try:
            txt = _find_textblock_under(_GOLD_WIDGET[0])
            _GOLD_TXT[0] = txt
        except Exception:
            txt = None
    if txt is not None:
        try:
            txt.set_visibility(unreal.SlateVisibility.VISIBLE)
        except Exception:
            pass
        # Keep top-right slot valid every tick (Designer/Shop2 offsets can regress)
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
            pass
        try:
            txt.set_text(unreal.Text(label))
        except Exception:
            try:
                txt.set_editor_property("text", unreal.Text(label))
            except Exception:
                pass
    else:'''

if old_refresh not in text:
    raise SystemExit("refresh block not found exactly")
text = text.replace(old_refresh, new_refresh, 1)

# 6) version tags
text = text.replace("SPLIT_WBP_V15e_T311_GOLD_HUD", "SPLIT_WBP_V15e_T312_GOLD5")

p.write_text(text, encoding="utf-8")
print("patched runtime", p.stat().st_size)

# 7) PlayerMeta.json force gold=5
meta_path = Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Saved\PlayerMeta.json")
meta_path.parent.mkdir(parents=True, exist_ok=True)
data = {"gold": 5, "inventory": []}
if meta_path.is_file():
    try:
        old = json.loads(meta_path.read_text(encoding="utf-8"))
        if isinstance(old, dict):
            data["inventory"] = list(old.get("inventory") or [])
    except Exception:
        pass
meta_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("PlayerMeta", meta_path.read_text(encoding="utf-8"))

# sanity
t2 = p.read_text(encoding="utf-8")
assert "DEFAULT_GOLD = 5" in t2
assert "Margin(-24.0, 36.0, 240.0, 40.0)" in t2
assert "Margin(-268.0, 36.0, -48.0, 76.0)" not in t2
assert "T312_GOLD5" in t2
assert "_meta_pull_gi(gi)" not in t2.split("def ensure_player_meta")[1].split("def get_gold")[0]
print("SANITY_OK")
