# -*- coding: utf-8 -*-
from pathlib import Path
p = Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py")
docs = Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py")
src = p.read_text(encoding="utf-8")
old = """    if widget is not None:
        try:
            wc.set_widget(widget)
        except Exception as e:
            _log(\"enemy wc set_widget \" + str(e))
            try:
                wc.set_editor_property(\"widget\", widget)
            except Exception as e2:
                _log(\"enemy wc widget prop \" + str(e2))
                return None
    try:
        wc.set_active(True, True)
    except Exception:
        pass
    return wc"""
new = """    # Prefer set_widget_class so the component owns a fresh instance sized to DrawSize
    wcls = None
    if widget is not None:
        try:
            wcls = widget.get_class()
        except Exception:
            wcls = None
    owned_pb = None
    if wcls is not None:
        try:
            wc.set_widget_class(wcls)
            _log(\"enemy wc set_widget_class ok\")
        except Exception as e:
            _log(\"enemy wc set_widget_class \" + str(e))
            try:
                wc.set_editor_property(\"widget_class\", wcls)
            except Exception as e2:
                _log(\"enemy wc widget_class prop \" + str(e2))
        owned = None
        try:
            owned = wc.get_user_widget_object()
        except Exception:
            owned = None
        if owned is None:
            try:
                wc.init_widget()
            except Exception:
                pass
            try:
                owned = wc.get_user_widget_object()
            except Exception:
                owned = None
        if owned is not None:
            pb2 = None
            try:
                pb2 = owned.get_widget_from_name(\"PB_Health\")
            except Exception:
                pb2 = None
            _fit_enemy_bar_layout(owned, pb2)
            widget = owned
            owned_pb = pb2
        elif widget is not None:
            try:
                wc.set_widget(widget)
            except Exception as e:
                _log(\"enemy wc set_widget \" + str(e))
                return None
    elif widget is not None:
        try:
            wc.set_widget(widget)
        except Exception as e:
            _log(\"enemy wc set_widget \" + str(e))
            try:
                wc.set_editor_property(\"widget\", widget)
            except Exception as e2:
                _log(\"enemy wc widget prop \" + str(e2))
                return None
    try:
        wc.set_active(True, True)
    except Exception:
        pass
    try:
        wc.set_visibility(True, True)
    except Exception:
        pass
    # stash owned pb on component via a python-side return isn't possible; caller re-queries
    try:
        wc._de_owned_pb = owned_pb  # type: ignore
        wc._de_owned_widget = widget  # type: ignore
    except Exception:
        pass
    return wc"""
if old not in src:
    print("OLD_BLOCK_NOT_FOUND")
    i = src.find("enemy wc set_widget")
    print("idx", i)
    print(repr(src[i-160:i+260]))
else:
    src2 = src.replace(old, new, 1)
    # After attach in ensure_enemy_health_bars, refresh widget/pb from component if present
    needle = """            wc = _attach_widget_component(actor, widget)
            st[\"widget\"] = widget
            st[\"pb\"] = pb
            st[\"wc\"] = wc
"""
    repl = """            wc = _attach_widget_component(actor, widget)
            st[\"wc\"] = wc
            # Prefer component-owned widget/pb after set_widget_class
            if wc is not None:
                try:
                    owned = getattr(wc, \"_de_owned_widget\", None) or wc.get_user_widget_object()
                except Exception:
                    owned = getattr(wc, \"_de_owned_widget\", None)
                if owned is not None:
                    widget = owned
                try:
                    opb = getattr(wc, \"_de_owned_pb\", None)
                except Exception:
                    opb = None
                if opb is None and widget is not None:
                    try:
                        opb = widget.get_widget_from_name(\"PB_Health\")
                    except Exception:
                        opb = None
                if opb is not None:
                    pb = opb
            st[\"widget\"] = widget
            st[\"pb\"] = pb
"""
    if needle in src2:
        src2 = src2.replace(needle, repl, 1)
        print("ensure refresh patched")
    else:
        print("ensure needle missing")
    p.write_text(src2, encoding="utf-8")
    docs.write_text(src2, encoding="utf-8")
    print("PATCHED", len(src2))
