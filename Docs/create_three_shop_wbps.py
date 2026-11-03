# -*- coding: utf-8 -*-
"""Create WBP_Shop_Weapon / Armor / Health from WBP_Shop; set distinct titles; reload runtime."""
from __future__ import print_function
import unreal
import sys
import traceback

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\create_three_shop_wbps.txt"
PYDIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
SRC = "/Game/UI/Shop/WBP_Shop"
SHOPS = (
    ("WBP_Shop_Weapon", u"武器店", "/Game/UI/Shop/WBP_Shop_Weapon"),
    ("WBP_Shop_Armor", u"防具店", "/Game/UI/Shop/WBP_Shop_Armor"),
    ("WBP_Shop_Health", u"回血店", "/Game/UI/Shop/WBP_Shop_Health"),
)
lines = []


def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("SPLIT3: " + s)
    except Exception:
        print("SPLIT3:", s)


def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def ensure_folder():
    try:
        if not unreal.EditorAssetLibrary.does_directory_exist("/Game/UI/Shop"):
            unreal.EditorAssetLibrary.make_directory("/Game/UI/Shop")
            log("mkdir /Game/UI/Shop")
    except Exception as e:
        log("mkdir " + str(e))


def duplicate_or_create(name, dest_path):
    existing = unreal.load_object(None, dest_path + "." + name)
    if existing is not None:
        log("exists " + dest_path)
        return existing, False
    # Prefer duplicate from WBP_Shop
    src_obj = unreal.load_object(None, SRC + ".WBP_Shop")
    if src_obj is None:
        # try WBP_Shop2
        src_obj = unreal.load_object(None, "/Game/UI/Shop/WBP_Shop2.WBP_Shop2")
        src_path = "/Game/UI/Shop/WBP_Shop2"
    else:
        src_path = SRC
    log("src=" + str(src_obj) + " path=" + src_path)
    if src_obj is not None:
        try:
            dup = unreal.EditorAssetLibrary.duplicate_asset(src_path, dest_path)
            log("duplicated -> " + str(dup))
            if dup is not None:
                return dup, True
        except Exception as e:
            log("duplicate ERR " + str(e))
    # Fallback: create empty WidgetBlueprint
    try:
        factory = unreal.WidgetBlueprintFactory()
        try:
            factory.set_editor_property("parent_class", unreal.UserWidget)
        except Exception as e:
            log("parent set " + str(e))
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        bp = asset_tools.create_asset(name, "/Game/UI/Shop", unreal.WidgetBlueprint, factory)
        log("created blank=" + str(bp))
        if bp is not None:
            _build_minimal_tree(bp, dest_path, name)
            return bp, True
    except Exception as e:
        log("create ERR " + str(e))
        log(traceback.format_exc())
    return unreal.load_object(None, dest_path + "." + name), False


def _build_minimal_tree(bp, dest_path, name):
    tree = None
    try:
        tree = bp.get_editor_property("widget_tree")
    except Exception:
        try:
            tree = bp.get_editor_property("WidgetTree")
        except Exception:
            tree = unreal.load_object(None, dest_path + "." + name + ":WidgetTree")
    if tree is None:
        log("no tree for " + name)
        return
    canvas = None
    try:
        canvas = tree.construct_widget(unreal.CanvasPanel, "RootCanvas")
    except Exception as e:
        log("canvas " + str(e))
        return
    try:
        tree.set_editor_property("root_widget", canvas)
    except Exception:
        try:
            tree.set_editor_property("RootWidget", canvas)
        except Exception as e:
            log("set root " + str(e))
            return
    try:
        img = tree.construct_widget(unreal.Image, "BgImage")
        if img:
            try:
                img.set_editor_property("color_and_opacity", unreal.LinearColor(0.05, 0.05, 0.12, 0.9))
            except Exception:
                pass
            slot = canvas.add_child_to_canvas(img)
            if slot:
                slot.set_anchors(unreal.Anchors(0, 0, 1, 1))
                slot.set_offsets(unreal.Margin(0, 0, 0, 0))
    except Exception as e:
        log("img " + str(e))
    try:
        txt = tree.construct_widget(unreal.TextBlock, "Txt_Title")
        if txt:
            try:
                txt.set_editor_property("text", unreal.Text(name))
            except Exception:
                try:
                    txt.set_text(unreal.Text(name))
                except Exception:
                    pass
            try:
                font = txt.get_editor_property("font")
                font.set_editor_property("size", 72)
                txt.set_editor_property("font", font)
            except Exception:
                pass
            try:
                txt.set_editor_property("color_and_opacity", unreal.SlateColor(unreal.LinearColor(1, 1, 0, 1)))
            except Exception:
                pass
            slot = canvas.add_child_to_canvas(txt)
            if slot:
                slot.set_anchors(unreal.Anchors(0.5, 0.5, 0.5, 0.5))
                slot.set_alignment(unreal.Vector2D(0.5, 0.5))
                slot.set_offsets(unreal.Margin(-250, -60, 500, 120))
    except Exception as e:
        log("txt " + str(e))


def paint_title(dest_path, name, title):
    """Set TextBlock titles inside the asset WidgetTree (editor)."""
    n = 0
    needle = dest_path + "." + name + ":WidgetTree."
    for o in unreal.ObjectIterator(unreal.TextBlock):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if needle not in pn and (dest_path + "." + name) not in pn:
            continue
        try:
            wname = o.get_name()
        except Exception:
            wname = ""
        try:
            o.set_editor_property("text", unreal.Text(str(title)))
            n += 1
            log("set text %s -> %s" % (wname, title))
        except Exception:
            try:
                o.set_text(unreal.Text(str(title)))
                n += 1
                log("set_text %s -> %s" % (wname, title))
            except Exception as e:
                log("text fail %s %s" % (wname, e))
        try:
            font = o.get_editor_property("font")
            font.set_editor_property("size", 72)
            o.set_editor_property("font", font)
        except Exception:
            pass
        try:
            o.set_editor_property("color_and_opacity", unreal.SlateColor(unreal.LinearColor(1, 0.95, 0.2, 1)))
        except Exception:
            pass
        try:
            o.set_editor_property("visibility", unreal.SlateVisibility.VISIBLE)
        except Exception:
            pass
    log("painted %d texts on %s" % (n, name))
    return n


def compile_and_save(path):
    try:
        unreal.EditorAssetLibrary.save_asset(path)
        log("saved " + path)
    except Exception as e:
        log("save ERR " + str(e))
    # Try compile widget blueprint
    bp = unreal.load_object(None, path + "." + path.rsplit("/", 1)[-1])
    if bp is None:
        return
    for meth in ("compile",):
        # KismetEditorUtilities
        pass
    try:
        kue = unreal.KismetEditorUtilities
        kue.compile_blueprint(bp)
        log("compiled " + path)
    except Exception as e:
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
            log("compiled via BEL " + path)
        except Exception as e2:
            log("compile skip " + str(e) + " / " + str(e2))


def reload_runtime():
    if PYDIR not in sys.path:
        sys.path.insert(0, PYDIR)
    # kill old ticks
    n = 0
    prev = getattr(unreal, "_de_shop_tick_handle", None)
    if prev is not None:
        for name in ("unregister_slate_post_tick_callback", "unregister_slate_pre_tick_callback"):
            fn = getattr(unreal, name, None)
            if fn:
                try:
                    fn(prev)
                    n += 1
                except Exception:
                    pass
        try:
            unreal._de_shop_tick_handle = None
        except Exception:
            pass
    for modname, mod in list(sys.modules.items()):
        if "shop_interact" not in str(modname):
            continue
        val = getattr(mod, "_TICK", None)
        if isinstance(val, list) and val and val[0] is not None:
            for name in ("unregister_slate_post_tick_callback", "unregister_slate_pre_tick_callback"):
                fn = getattr(unreal, name, None)
                if fn:
                    try:
                        fn(val[0])
                        n += 1
                    except Exception:
                        pass
            try:
                val[0] = None
            except Exception:
                pass
    try:
        unreal._de_shop_tick_gen = int(getattr(unreal, "_de_shop_tick_gen", 0)) + 1
    except Exception:
        unreal._de_shop_tick_gen = 1
    for k in list(sys.modules.keys()):
        if "shop_interact_runtime" in k:
            del sys.modules[k]
    import shop_interact_runtime as r
    src = open(PYDIR + r"\shop_interact_runtime.py", encoding="utf-8", errors="replace").read()
    log("killed_ticks~%d" % n)
    log("has_SPLIT=%s" % ("SPLIT_WBP_V12" in src))
    log("SHOP_WBP_keys=%s" % list(getattr(r, "SHOP_WBP", {}).keys()))
    log("tick=%s gen=%s" % (getattr(r, "_TICK", [None])[0], getattr(r, "_MY_GEN", [None])[0]))
    # Verify classes load
    for key in ("Weapon", "Armor", "Health"):
        c, p = r._load_shop_class(key)
        log("load %s -> %s (%s)" % (key, p, bool(c)))


def main():
    log("=== create three shop WBPs ===")
    ensure_folder()
    src = unreal.load_object(None, SRC + ".WBP_Shop")
    log("WBP_Shop=" + str(src))
    if src is None:
        log("WARN no WBP_Shop — will try Shop2 / blank create")
    for name, title, path in SHOPS:
        log("--- %s ---" % name)
        bp, created = duplicate_or_create(name, path)
        log("bp=%s created=%s" % (bp, created))
        if bp is None:
            log("FAIL create " + name)
            continue
        paint_title(path, name, title)
        compile_and_save(path)
        # verify asset exists
        ok = unreal.EditorAssetLibrary.does_asset_exist(path)
        log("exists_on_disk=%s" % ok)
    reload_runtime()
    log("OK_SPLIT3")


try:
    main()
except Exception as e:
    log("FAIL " + str(e))
    log(traceback.format_exc())
finally:
    flush()
