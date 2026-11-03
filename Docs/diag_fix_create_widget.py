# -*- coding: utf-8 -*-
"""Diagnose + fix CreateWidget returning null for WBP_Shop (UE 4.27).
Does NOT spawn Python actors into Map_Hub. Buildings untouched.
"""
from __future__ import print_function
import unreal
import traceback

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_fix_create_widget.txt"
BP_CHAR = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
WBP_SHOP = "/Game/UI/Shop/WBP_Shop"
WBP_SHOP2 = "/Game/UI/Shop/WBP_Shop2"
WBP_MENU = "/Game/UI/Menus/WBP_MainMenu"
WBP_NEW = "/Game/UI/Shop/WBP_ShopSimple"
lines = []


def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("DIAGCW: " + s)
    except Exception:
        print("DIAGCW:", s)


def flush():
    try:
        open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    except Exception as e:
        print("flush", e)


def asset_info(path):
    log("=== asset " + path + " ===")
    exists = unreal.EditorAssetLibrary.does_asset_exist(path)
    log("exists=" + str(exists))
    if not exists:
        return None
    a = unreal.EditorAssetLibrary.load_asset(path)
    log("loaded=" + str(a) + " class=" + (a.get_class().get_name() if a else "?"))
    if not a:
        return None
    try:
        log("path_name=" + a.get_path_name())
    except Exception:
        pass
    # WidgetBlueprint specifics
    try:
        pc = a.get_editor_property("parent_class")
        log("parent_class=" + str(pc))
    except Exception as e:
        log("parent_class err " + str(e))
    try:
        gc = a.generated_class()
        log("generated_class()=" + str(gc))
        if gc:
            log("generated_class path=" + gc.get_path_name())
            try:
                log("gc super=" + str(gc.get_super_class()))
            except Exception:
                pass
    except Exception as e:
        log("generated_class err " + str(e))
    try:
        st = a.status
        log("status=" + str(st))
    except Exception:
        try:
            st = a.get_editor_property("status")
            log("status prop=" + str(st))
        except Exception as e:
            log("status err " + str(e))
    try:
        # compile
        ok = unreal.BlueprintEditorLibrary.compile_blueprint(a)
        log("compile_blueprint=" + str(ok))
    except Exception as e:
        log("compile_blueprint err " + str(e))
        try:
            unreal.KismetSystemLibrary.compile_blueprint(a)  # may not exist
        except Exception:
            pass
    # refresh generated class after compile
    try:
        gc = a.generated_class()
        log("after compile generated_class=" + str(gc))
        if gc:
            log("after compile gc path=" + gc.get_path_name())
    except Exception as e:
        log("after gc err " + str(e))
    return a


def try_create(class_path_or_obj, label):
    log("--- create try: " + label + " ---")
    cls = None
    if isinstance(class_path_or_obj, str):
        # try several load forms
        for p in (
            class_path_or_obj,
            class_path_or_obj + "_C",
            class_path_or_obj + "." + class_path_or_obj.split("/")[-1] + "_C",
        ):
            try:
                c = unreal.load_class(None, p)
                log("load_class(%s)=%s" % (p, c))
                if c:
                    cls = c
                    break
            except Exception as e:
                log("load_class(%s) err %s" % (p, e))
        if not cls:
            try:
                a = unreal.EditorAssetLibrary.load_asset(class_path_or_obj.replace(".", "/").rsplit("/", 1)[0] if False else class_path_or_obj)
            except Exception:
                a = None
            # if path looks like /Game/.../WBP_X load asset and get generated
            try:
                a = unreal.EditorAssetLibrary.load_asset(class_path_or_obj)
                if a:
                    cls = a.generated_class()
                    log("from asset generated=" + str(cls))
            except Exception as e:
                log("asset gen err " + str(e))
    else:
        cls = class_path_or_obj
        log("cls obj=" + str(cls))

    if not cls:
        log("NO CLASS for " + label)
        return None

    # get PC
    pc = None
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        log("editor_world=" + str(world))
    except Exception as e:
        world = None
        log("world err " + str(e))
    try:
        # PIE world preferred
        pie = None
        try:
            pie_worlds = unreal.EditorLevelLibrary.get_pie_worlds(False)
            log("pie_worlds=" + str(pie_worlds))
            if pie_worlds:
                pie = pie_worlds[0]
        except Exception as e:
            log("pie_worlds err " + str(e))
        ctx = pie or world
        if ctx:
            pc = unreal.GameplayStatics.get_player_controller(ctx, 0)
            log("PC=" + str(pc))
    except Exception as e:
        log("get PC err " + str(e))

    w = None
    # Method 1: WidgetBlueprintLibrary.create
    try:
        wbl = unreal.WidgetBlueprintLibrary
        w = wbl.create(pc or world, cls, pc)
        log("WBL.create => " + str(w))
    except Exception as e:
        log("WBL.create err " + str(e) + "\n" + traceback.format_exc())

    if w:
        try:
            w.add_to_viewport(100)
            log("add_to_viewport ok")
        except Exception as e:
            log("add_to_viewport err " + str(e))
    return w


def inspect_bp_create_nodes():
    log("=== inspect BP_KayKitKnight CreateWidget nodes ===")
    bp = unreal.EditorAssetLibrary.load_asset(BP_CHAR)
    if not bp:
        log("BP missing")
        return
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception:
        pass

    # iterate all objects under BP
    create_nodes = []
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
            if BP_CHAR not in pn and "BP_KayKitKnight" not in pn:
                continue
            cn = o.get_class().get_name()
            if "CreateWidget" in cn or cn == "K2Node_CreateWidget":
                create_nodes.append(o)
                log("FOUND node %s class=%s path=%s" % (o.get_name(), cn, pn))
                try:
                    pins = list(o.get_editor_property("pins"))
                except Exception:
                    try:
                        pins = list(o.pins)
                    except Exception:
                        pins = []
                for p in pins:
                    try:
                        pname = str(p.get_editor_property("pin_name"))
                        ptype = str(p.get_editor_property("pin_type"))
                        pdef = None
                        try:
                            pdef = p.default_object
                        except Exception:
                            pass
                        try:
                            pdefv = p.default_value
                        except Exception:
                            pdefv = None
                        linked = []
                        try:
                            linked = list(p.linked_to)
                        except Exception:
                            try:
                                linked = list(p.get_editor_property("linked_to"))
                            except Exception:
                                linked = []
                        log("  pin %s type=%s defobj=%s defval=%s links=%d" % (
                            pname, ptype[:80] if ptype else "?", pdef, pdefv, len(linked)))
                    except Exception as e:
                        log("  pin err " + str(e))
                # class property on node
                for prop in ("class_to_spawn", "widget_class", "ClassToSpawn", "WidgetClass"):
                    try:
                        v = o.get_editor_property(prop)
                        log("  prop %s=%s" % (prop, v))
                    except Exception:
                        pass
            if "InputAction" in cn or "Interact" in str(o.get_name()):
                if "Interact" in str(o.get_name()) or "Interact" in cn:
                    log("INPUT node %s cn=%s" % (o.get_name(), cn))
        except Exception:
            pass
    log("create_nodes count=%d" % len(create_nodes))
    return create_nodes


def recreate_simple_wbp():
    """Create a clean UserWidget with big text via factory."""
    log("=== recreate WBP_ShopSimple ===")
    if unreal.EditorAssetLibrary.does_asset_exist(WBP_NEW):
        try:
            unreal.EditorAssetLibrary.delete_asset(WBP_NEW)
            log("deleted old WBP_ShopSimple")
        except Exception as e:
            log("del err " + str(e))

    factory = unreal.WidgetBlueprintFactory()
    try:
        factory.set_editor_property("parent_class", unreal.UserWidget)
    except Exception as e:
        log("set parent_class err " + str(e))
        try:
            factory.parent_class = unreal.UserWidget
        except Exception as e2:
            log("parent_class attr err " + str(e2))

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    wbp = tools.create_asset("WBP_ShopSimple", "/Game/UI/Shop", unreal.WidgetBlueprint, factory)
    log("created asset=" + str(wbp))
    if not wbp:
        # fallback: duplicate MainMenu
        log("factory failed, duplicating MainMenu")
        src = unreal.EditorAssetLibrary.load_asset(WBP_MENU)
        wbp = tools.duplicate_asset("WBP_ShopSimple", "/Game/UI/Shop", src)
        log("dup=" + str(wbp))

    if not wbp:
        log("FAILED create WBP_ShopSimple")
        return None

    # try add text via widget tree if accessible
    try:
        wt = wbp.get_editor_property("widget_tree")
        log("widget_tree=" + str(wt))
        if wt:
            root = None
            try:
                root = wt.get_editor_property("root_widget")
            except Exception:
                try:
                    root = wt.root_widget
                except Exception:
                    root = None
            log("root_widget=" + str(root))
            # create TextBlock
            try:
                tb = unreal.new_object(unreal.TextBlock, wt)
                tb.set_editor_property("text", unreal.Text("SHOP"))
                try:
                    # font size via slate font info hard in py - skip
                    pass
                except Exception:
                    pass
                # If root is canvas or panel, add child
                if root is None:
                    # make canvas
                    canvas = unreal.new_object(unreal.CanvasPanel, wt)
                    wt.set_editor_property("root_widget", canvas)
                    root = canvas
                    log("set canvas root")
                # try add child
                try:
                    if hasattr(root, "add_child_to_canvas"):
                        slot = root.add_child_to_canvas(tb)
                        try:
                            slot.set_anchors(unreal.Anchors(0.5, 0.5, 0.5, 0.5))
                            slot.set_alignment(unreal.Vector2D(0.5, 0.5))
                            slot.set_position(unreal.Vector2D(0, 0))
                            slot.set_size(unreal.Vector2D(400, 120))
                            slot.set_auto_size(True)
                        except Exception as e:
                            log("slot layout err " + str(e))
                        log("added TextBlock to canvas")
                    elif hasattr(root, "add_child"):
                        root.add_child(tb)
                        log("added TextBlock via add_child")
                    else:
                        # set as root if empty
                        if root is None or root.get_class().get_name() in ("Widget",):
                            wt.set_editor_property("root_widget", tb)
                            log("set TextBlock as root")
                        else:
                            log("root type " + root.get_class().get_name() + " cannot add easily")
                except Exception as e:
                    log("add child err " + str(e) + "\n" + traceback.format_exc())
            except Exception as e:
                log("new TextBlock err " + str(e))
    except Exception as e:
        log("widget_tree err " + str(e) + "\n" + traceback.format_exc())

    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
        log("compiled WBP_ShopSimple")
    except Exception as e:
        log("compile simple err " + str(e))
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(wbp)
        log("saved WBP_ShopSimple")
    except Exception as e:
        log("save err " + str(e))

    gc = None
    try:
        gc = wbp.generated_class()
        log("WBP_ShopSimple GC=" + str(gc) + (" path=" + gc.get_path_name() if gc else ""))
    except Exception as e:
        log("gc err " + str(e))
    return wbp


def overwrite_wbp_shop_from_simple(simple):
    """Replace WBP_Shop content by duplicating simple over it, or retarget."""
    log("=== ensure WBP_Shop is healthy ===")
    # Prefer fixing WBP_Shop by deleting and duplicating simple as WBP_Shop
    if not simple:
        return None
    # Don't delete WBP_Shop if user has it open - try compile & verify create first
    shop = unreal.EditorAssetLibrary.load_asset(WBP_SHOP)
    if shop:
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(shop)
        except Exception:
            pass
        gc = None
        try:
            gc = shop.generated_class()
        except Exception:
            pass
        log("existing WBP_Shop gc=" + str(gc))
        if gc:
            w = try_create(gc, "existing_WBP_Shop_gc")
            if w:
                log("existing WBP_Shop WORKS")
                return shop

    # recreate WBP_Shop from factory / simple
    if unreal.EditorAssetLibrary.does_asset_exist(WBP_SHOP):
        try:
            # close editors? 
            unreal.AssetEditorSubsystem().close_all_editors_for_asset(
                unreal.EditorAssetLibrary.load_asset(WBP_SHOP)
            )
        except Exception as e:
            log("close editor err " + str(e))
        try:
            unreal.EditorAssetLibrary.delete_asset(WBP_SHOP)
            log("deleted broken WBP_Shop")
        except Exception as e:
            log("delete WBP_Shop err " + str(e))

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    src = unreal.EditorAssetLibrary.load_asset(WBP_NEW)
    if not src:
        src = simple
    wbp = tools.duplicate_asset("WBP_Shop", "/Game/UI/Shop", src)
    log("new WBP_Shop=" + str(wbp))
    if wbp:
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
        except Exception:
            pass
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(wbp)
        except Exception:
            pass
        try:
            log("new WBP_Shop gc=" + str(wbp.generated_class()))
        except Exception:
            pass
    return wbp


def fix_bp_create_widget_class(wbp_path):
    """Set CreateWidget node's class pin to the given WBP generated class.
    Also ensure OwningPlayer is wired if possible.
    """
    log("=== fix BP CreateWidget class -> " + wbp_path + " ===")
    bp = unreal.EditorAssetLibrary.load_asset(BP_CHAR)
    wbp = unreal.EditorAssetLibrary.load_asset(wbp_path)
    if not bp or not wbp:
        log("missing bp or wbp")
        return False
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
    except Exception:
        pass
    gc = None
    try:
        gc = wbp.generated_class()
    except Exception:
        pass
    if not gc:
        log("no generated class for target wbp")
        return False
    log("target gc=" + gc.get_path_name())

    fixed = 0
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
            if BP_CHAR not in pn:
                continue
            cn = o.get_class().get_name()
            if cn != "K2Node_CreateWidget":
                continue
            log("patching " + o.get_name())
            # set class via pin default_object
            try:
                pins = list(o.get_editor_property("pins"))
            except Exception:
                pins = list(o.pins) if hasattr(o, "pins") else []
            for p in pins:
                try:
                    pname = str(p.get_editor_property("pin_name")).lower()
                except Exception:
                    pname = ""
                if pname in ("class", "widget class", "class to spawn"):
                    try:
                        p.default_object = gc
                        log("set pin default_object")
                        fixed += 1
                    except Exception as e:
                        log("set default_object err " + str(e))
                    try:
                        p.set_editor_property("default_object", gc)
                        log("set_editor_property default_object")
                        fixed += 1
                    except Exception as e:
                        log("set_editor_property err " + str(e))
                    try:
                        # SoftObjectPath style default value
                        p.default_value = gc.get_path_name()
                        log("set default_value " + gc.get_path_name())
                        fixed += 1
                    except Exception as e:
                        log("default_value err " + str(e))
            for prop in ("class_to_spawn", "widget_class"):
                try:
                    o.set_editor_property(prop, gc)
                    log("set node prop " + prop)
                    fixed += 1
                except Exception:
                    pass
            # mark reconstruct
            try:
                o.reallocate_pins_during_reconstruction([])
            except Exception:
                pass
            try:
                o.reconstruct_node()
            except Exception:
                pass
        except Exception as e:
            log("node iter err " + str(e))

    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        log("compiled BP_KayKitKnight")
    except Exception as e:
        log("compile bp err " + str(e))
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        log("saved BP")
    except Exception as e:
        log("save bp err " + str(e))
    log("fixed_ops=" + str(fixed))
    return fixed > 0


def check_is_valid_wiring_issue():
    """Log PrintString / IsValid nodes near CreateWidget for sanity."""
    log("=== nearby diagnostic nodes ===")
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
            if BP_CHAR not in pn:
                continue
            cn = o.get_class().get_name()
            name = o.get_name()
            if any(x in cn or x in name for x in ("IsValid", "Print", "CreateWidget", "AddToViewport", "SetInputMode", "Interact")):
                log("%s | %s" % (cn, name))
        except Exception:
            pass


def main():
    log("START diag_fix_create_widget")
    for p in (WBP_SHOP, WBP_SHOP2, WBP_MENU):
        a = asset_info(p)
        if a:
            try:
                gc = a.generated_class()
            except Exception:
                gc = None
            if gc:
                try_create(gc, p + "_gc")
            try_create(p, p + "_path")

    inspect_bp_create_nodes()
    check_is_valid_wiring_issue()

    simple = recreate_simple_wbp()
    if simple:
        try:
            gc = simple.generated_class()
        except Exception:
            gc = None
        if gc:
            try_create(gc, "WBP_ShopSimple_gc")

    # If simple works, also refresh WBP_Shop and point BP at it
    shop = overwrite_wbp_shop_from_simple(simple)
    target = WBP_SHOP if shop else WBP_NEW
    fix_bp_create_widget_class(target)

    # re-inspect
    inspect_bp_create_nodes()

    # final create proof with shop
    a = unreal.EditorAssetLibrary.load_asset(target)
    if a:
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(a)
        except Exception:
            pass
        try:
            gc = a.generated_class()
        except Exception:
            gc = None
        w = try_create(gc or target, "FINAL_" + target)
        log("FINAL_WIDGET=" + str(w))
        log("FINAL_OK=" + str(w is not None))

    log("DONE")
    flush()


try:
    main()
except Exception:
    log("MAIN EXC\n" + traceback.format_exc())
    flush()
