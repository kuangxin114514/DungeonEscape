# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
import importlib
import sys
import json
import os

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t312.txt"
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("T312RL: " + str(m))
    except Exception:
        print(m)

def fix_wbp_gold():
    DST = "/Game/UI/HUD/WBP_PlayerGold"
    if not unreal.EditorAssetLibrary.does_asset_exist(DST):
        log("WBP_PlayerGold missing")
        return
    unreal.EditorAssetLibrary.load_asset(DST)
    fixed = 0
    for o in unreal.ObjectIterator(unreal.TextBlock):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "/Game/UI/HUD/WBP_PlayerGold" not in pn:
            continue
        if "WidgetTree." not in pn:
            continue
        try:
            o.set_editor_property("visibility", unreal.SlateVisibility.VISIBLE)
            o.set_editor_property("text", unreal.Text(u"\u91d1\u5e01: 5"))
            try:
                o.set_editor_property(
                    "color_and_opacity",
                    unreal.SlateColor(unreal.LinearColor(1.0, 0.9, 0.2, 1.0)),
                )
            except Exception:
                pass
            try:
                font = o.get_editor_property("font")
                font.set_editor_property("size", 28)
                o.set_editor_property("font", font)
            except Exception:
                pass
            slot = getattr(o, "slot", None)
            if slot is not None:
                anc = unreal.Anchors()
                anc.minimum = unreal.Vector2D(1.0, 0.0)
                anc.maximum = unreal.Vector2D(1.0, 0.0)
                try:
                    slot.set_anchors(anc)
                except Exception:
                    try:
                        slot.set_editor_property("anchors", anc)
                    except Exception:
                        pass
                try:
                    slot.set_alignment(unreal.Vector2D(1.0, 0.0))
                except Exception:
                    try:
                        slot.set_editor_property("alignment", unreal.Vector2D(1.0, 0.0))
                    except Exception:
                        pass
                # Point anchor: Right/Bottom = width/height (POSITIVE)
                try:
                    slot.set_offsets(unreal.Margin(-24.0, 36.0, 240.0, 40.0))
                except Exception:
                    try:
                        slot.set_editor_property("offsets", unreal.Margin(-24.0, 36.0, 240.0, 40.0))
                    except Exception as e:
                        log("offsets err " + str(e))
                try:
                    slot.set_auto_size(True)
                except Exception:
                    pass
            fixed += 1
            log("fixed TB " + o.get_name() + " " + pn[-80:])
        except Exception as e:
            log("tb err " + str(e))
    try:
        unreal.EditorAssetLibrary.save_asset(DST)
        log("WBP saved fixed=%d" % fixed)
    except Exception as e:
        log("save " + str(e))

def main():
    # Force PlayerMeta.json = 5
    meta_path = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Saved\PlayerMeta.json"
    try:
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    except TypeError:
        d = os.path.dirname(meta_path)
        if d and not os.path.isdir(d):
            os.makedirs(d)
    open(meta_path, "w", encoding="utf-8").write(
        json.dumps({"gold": 5, "inventory": []}, ensure_ascii=False, indent=2)
    )
    log("wrote PlayerMeta gold=5")

    fix_wbp_gold()

    py = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path:
        sys.path.insert(0, py)
    if "shop_interact_runtime" in sys.modules:
        m = importlib.reload(sys.modules["shop_interact_runtime"])
        log("reloaded")
    else:
        import shop_interact_runtime as m
        log("imported")

    log("DEFAULT_GOLD=%s" % getattr(m, "DEFAULT_GOLD", "?"))
    log("tag_has_T312=%s" % ("T312_GOLD5" in open(m.__file__, encoding="utf-8").read()))

    # Reset in-memory meta so DEFAULT/file apply
    try:
        m._PLAYER_META["ready"] = False
        m._PLAYER_META["gold"] = int(m.DEFAULT_GOLD)
        m._PLAYER_META["inventory"] = []
        m._GOLD_WIDGET[0] = None
        m._GOLD_TXT[0] = None
        log("cleared meta+gold widget cache")
    except Exception as e:
        log("clear err " + str(e))

    try:
        m.ensure_player_meta(None)
        # Force 5 even if something else snuck in
        m.set_gold(5, None)
        log("gold_now=%s" % m.get_gold(None))
    except Exception as e:
        log("meta err " + str(e))

    fn = getattr(m, "bootstrap", None)
    if callable(fn):
        try:
            fn()
            log("bootstrap ok")
        except Exception as e:
            log("bootstrap err " + str(e))

    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("WROTE", OUT)

main()
