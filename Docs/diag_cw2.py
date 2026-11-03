# -*- coding: utf-8 -*-
"""UE4.27-compatible CreateWidget diagnosis. No map Python actors."""
from __future__ import print_function
import unreal
import traceback

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_cw2.txt"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("CW2: " + s)
    except Exception:
        print("CW2:", s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def list_path(p):
    log("list_assets " + p)
    try:
        arr = unreal.EditorAssetLibrary.list_assets(p, True, False)
        log(" count=" + str(len(arr)))
        for a in list(arr)[:50]:
            log("  " + str(a))
    except Exception as e:
        log(" list err " + str(e))

def registry_search(substr):
    log("registry search " + substr)
    try:
        reg = unreal.AssetRegistryHelpers.get_asset_registry()
        assets = reg.get_all_assets()
        n = 0
        for a in assets:
            try:
                path = str(a.object_path) if hasattr(a, "object_path") else ""
                pname = str(a.package_name) if hasattr(a, "package_name") else ""
                aname = str(a.asset_name) if hasattr(a, "asset_name") else ""
                blob = (path + " " + pname + " " + aname).lower()
                if substr.lower() in blob:
                    log("  pkg=%s name=%s class=%s path=%s" % (pname, aname, a.asset_class, path))
                    n += 1
                    if n > 40:
                        break
            except Exception:
                pass
        log(" matched=" + str(n))
    except Exception as e:
        log("registry err " + str(e) + "\n" + traceback.format_exc())

def find_objects(substr):
    log("ObjectIterator " + substr)
    hits = []
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
            if substr in pn:
                hits.append(o)
        except Exception:
            pass
    log(" hits=" + str(len(hits)))
    for o in hits[:60]:
        try:
            log("  %s | %s" % (o.get_class().get_name(), o.get_path_name()))
        except Exception as e:
            log("  err " + str(e))
    return hits

def dump_create_widget_nodes():
    log("=== dump CreateWidget nodes ===")
    for o in unreal.ObjectIterator():
        try:
            if o.get_class().get_name() != "K2Node_CreateWidget":
                continue
            pn = o.get_path_name()
            log("NODE " + pn)
            # all properties
            try:
                for prop in ("class_pin_name", "class_to_spawn", "widget_class", "ClassToSpawn"):
                    try:
                        log("  prop.%s=%s" % (prop, o.get_editor_property(prop)))
                    except Exception as e:
                        log("  prop.%s ERR %s" % (prop, e))
            except Exception:
                pass
            # pins
            pins = []
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
                except Exception:
                    pname = "?"
                try:
                    direction = str(p.get_editor_property("direction"))
                except Exception:
                    direction = "?"
                try:
                    defobj = p.get_editor_property("default_object")
                except Exception:
                    try:
                        defobj = p.default_object
                    except Exception:
                        defobj = "ERR"
                try:
                    defval = p.get_editor_property("default_value")
                except Exception:
                    try:
                        defval = p.default_value
                    except Exception:
                        defval = "ERR"
                try:
                    linked = list(p.get_editor_property("linked_to"))
                except Exception:
                    try:
                        linked = list(p.linked_to)
                    except Exception:
                        linked = []
                # pin type
                try:
                    pt = p.get_editor_property("pin_type")
                    pin_cat = str(pt.get_editor_property("pin_category"))
                    pin_sub = str(pt.get_editor_property("pin_sub_category"))
                    pin_subobj = pt.get_editor_property("pin_sub_category_object")
                except Exception:
                    pin_cat = pin_sub = pin_subobj = "?"
                log("  PIN name=%s dir=%s cat=%s sub=%s subobj=%s defobj=%s defval=%s links=%d" % (
                    pname, direction, pin_cat, pin_sub, pin_subobj, defobj, defval, len(linked)))
                for lk in linked[:5]:
                    try:
                        log("    link -> " + str(lk) + " owner=" + str(lk.get_owning_node() if hasattr(lk, "get_owning_node") else "?"))
                    except Exception as e:
                        log("    link err " + str(e))
        except Exception as e:
            log("node dump err " + str(e))

def try_load_variants():
    paths = [
        "/Game/UI/Shop/WBP_Shop",
        "/Game/UI/Shop/WBP_Shop.WBP_Shop",
        "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",
        "/Game/UI/Shop/WBP_Shop2",
        "/Game/UI/Shop/WBP_Shop2.WBP_Shop2",
        "/Game/UI/Shop/WBP_ShopSimple",
        "/Game/UI/Shop/WBP_ShopSimple.WBP_ShopSimple",
        "/Game/UI/Menus/WBP_MainMenu",
        "/Game/UI/Menus/WBP_MainMenu.WBP_MainMenu",
        "/Game/Characters/Player/KayKit/BP_KayKitKnight",
        "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight",
    ]
    for p in paths:
        log("-- try " + p)
        try:
            a = unreal.EditorAssetLibrary.load_asset(p)
            log("  EAL.load_asset => " + str(a))
        except Exception as e:
            log("  EAL err " + str(e))
        try:
            o = unreal.load_object(None, p)
            log("  load_object => " + str(o))
        except Exception as e:
            log("  load_object err " + str(e))
        try:
            c = unreal.load_class(None, p)
            log("  load_class => " + str(c))
        except Exception as e:
            log("  load_class err " + str(e))
        try:
            bc = unreal.EditorAssetLibrary.load_blueprint_class(p)
            log("  load_blueprint_class => " + str(bc))
        except Exception as e:
            log("  load_blueprint_class err " + str(e))

def try_create_with_cls(cls, label):
    log("CREATE " + label + " cls=" + str(cls))
    if not cls:
        return None
    pc = None
    world = None
    try:
        worlds = []
        try:
            worlds = list(unreal.EditorLevelLibrary.get_pie_worlds(True) or [])
        except Exception:
            try:
                worlds = list(unreal.EditorLevelLibrary.get_pie_worlds(False) or [])
            except Exception:
                worlds = []
        log(" pie count=" + str(len(worlds)))
        if worlds:
            world = worlds[0]
        else:
            world = unreal.EditorLevelLibrary.get_editor_world()
        log(" world=" + str(world))
        if world:
            pc = unreal.GameplayStatics.get_player_controller(world, 0)
            log(" pc=" + str(pc))
    except Exception as e:
        log(" world/pc err " + str(e))

    # create methods
    w = None
    try:
        w = unreal.WidgetBlueprintLibrary.create(world, cls, pc)
        log("  create(world,cls,pc) => " + str(w))
    except Exception as e:
        log("  create(world) err " + str(e))
    if not w:
        try:
            w = unreal.WidgetBlueprintLibrary.create(pc, cls, pc)
            log("  create(pc,cls,pc) => " + str(w))
        except Exception as e:
            log("  create(pc) err " + str(e))
    if not w:
        try:
            # NewObject style
            outer = pc or world
            w = unreal.new_object(cls, outer)
            log("  new_object => " + str(w))
        except Exception as e:
            log("  new_object err " + str(e))
    if w:
        try:
            w.add_to_viewport(50)
            log("  add_to_viewport OK")
        except Exception as e:
            log("  add_to_viewport err " + str(e))
    return w

def compile_bp(bp):
    # UE4.27
    for name in ("compile_blueprint",):
        try:
            getattr(unreal.KismetEditorUtilities, name)(bp)
            log("KismetEditorUtilities.compile_blueprint OK")
            return True
        except Exception as e:
            log("compile via KEU err " + str(e))
    try:
        unreal.SystemLibrary.execute_console_command(None, "COMPILE %s" % bp.get_path_name())
    except Exception as e:
        log("console compile err " + str(e))
    return False

def get_generated_class(bp):
    # UE4 WidgetBlueprint / Blueprint
    for meth in ("generated_class", "get_blueprint_generated_class"):
        try:
            fn = getattr(bp, meth, None)
            if callable(fn):
                gc = fn()
                log("gc via %s => %s" % (meth, gc))
                if gc:
                    return gc
        except Exception as e:
            log("gc %s err %s" % (meth, e))
    for prop in ("generated_class", "GeneratedClass", "skeleton_generated_class"):
        try:
            gc = bp.get_editor_property(prop)
            log("gc prop %s => %s" % (prop, gc))
            if gc:
                return gc
        except Exception as e:
            log("gc prop %s err %s" % (prop, e))
    # load _C
    try:
        path = bp.get_path_name()  # /Game/.../WBP_Shop.WBP_Shop
        if path.endswith("_C"):
            cpath = path
        else:
            cpath = path + "_C"
        c = unreal.load_class(None, cpath)
        log("load_class %s => %s" % (cpath, c))
        if c:
            return c
    except Exception as e:
        log("load _C err " + str(e))
    return None

def fix_create_widget_class_pin(gc):
    log("=== FIX CreateWidget class pin to %s ===" % gc)
    if not gc:
        return False
    changed = False
    for o in unreal.ObjectIterator():
        try:
            if o.get_class().get_name() != "K2Node_CreateWidget":
                continue
            if "BP_KayKitKnight" not in o.get_path_name():
                continue
            log("fixing " + o.get_path_name())
            pins = []
            try:
                pins = list(o.get_editor_property("pins"))
            except Exception:
                pins = list(o.pins)
            for p in pins:
                try:
                    pname = str(p.get_editor_property("pin_name")).lower()
                except Exception:
                    continue
                if pname != "class":
                    continue
                log("  found Class pin")
                # Break existing links on class pin (should be none)
                try:
                    p.break_all_pin_links()
                except Exception:
                    try:
                        p.break_all_pin_links(True)
                    except Exception:
                        pass
                # Set default object to generated class
                for setter in (
                    lambda: setattr(p, "default_object", gc),
                    lambda: p.set_editor_property("default_object", gc),
                ):
                    try:
                        setter()
                        log("  set default_object OK")
                        changed = True
                    except Exception as e:
                        log("  set default_object err " + str(e))
                try:
                    p.set_editor_property("default_value", gc.get_path_name())
                    log("  set default_value " + gc.get_path_name())
                    changed = True
                except Exception as e:
                    log("  default_value err " + str(e))
                # Also try Autowire / notify
            try:
                o.reconstruct_node()
                log("  reconstruct_node OK")
            except Exception as e:
                log("  reconstruct err " + str(e))
            # Mark blueprint modified
            try:
                bp = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight")
                if bp:
                    unreal.EditorAssetLibrary.save_loaded_asset(bp)
                    log("  saved BP")
            except Exception as e:
                log("  save bp err " + str(e))
        except Exception as e:
            log("fix node err " + str(e) + "\n" + traceback.format_exc())
    return changed

def ensure_healthy_wbp():
    """Ensure a creatable UserWidget exists; return generated class."""
    log("=== ensure healthy WBP ===")
    # Prefer existing WBP_ShopSimple from prior run
    candidates = [
        "/Game/UI/Shop/WBP_ShopSimple",
        "/Game/UI/Shop/WBP_Shop",
        "/Game/UI/Shop/WBP_Shop2",
        "/Game/UI/Menus/WBP_MainMenu",
    ]
    for path in candidates:
        log("candidate " + path)
        bp = None
        try:
            bp = unreal.EditorAssetLibrary.load_asset(path)
        except Exception:
            bp = None
        if not bp:
            try:
                bp = unreal.load_object(None, path + "." + path.split("/")[-1])
            except Exception:
                bp = None
        log("  bp=" + str(bp))
        if not bp:
            continue
        compile_bp(bp)
        gc = get_generated_class(bp)
        if gc:
            w = try_create_with_cls(gc, path)
            if w:
                log("  SUCCESS create with " + path)
                return bp, gc
            else:
                log("  create FAILED for " + path)
    # Create new via factory
    log("creating fresh WBP_ShopFix via factory")
    out_path = "/Game/UI/Shop"
    name = "WBP_ShopFix"
    full = out_path + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        try:
            unreal.EditorAssetLibrary.delete_asset(full)
        except Exception:
            pass
    factory = unreal.WidgetBlueprintFactory()
    try:
        factory.set_editor_property("parent_class", unreal.UserWidget)
    except Exception as e:
        log("parent set err " + str(e))
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    bp = tools.create_asset(name, out_path, unreal.WidgetBlueprint, factory)
    log("factory bp=" + str(bp))
    if bp:
        compile_bp(bp)
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(bp)
        except Exception as e:
            log("save err " + str(e))
        gc = get_generated_class(bp)
        w = try_create_with_cls(gc, "WBP_ShopFix")
        log("ShopFix create => " + str(w))
        return bp, gc
    return None, None

def main():
    log("START cw2")
    list_path("/Game/UI")
    list_path("/Game/UI/Shop")
    list_path("/Game/Characters/Player/KayKit")
    registry_search("WBP_Shop")
    registry_search("BP_KayKitKnight")
    try_load_variants()
    find_objects("WBP_Shop")
    find_objects("BP_KayKitKnight")
    dump_create_widget_nodes()

    bp, gc = ensure_healthy_wbp()
    log("healthy bp=%s gc=%s" % (bp, gc))
    if gc:
        fix_create_widget_class_pin(gc)
        dump_create_widget_nodes()
        # final create proof
        w = try_create_with_cls(gc, "FINAL")
        log("FINAL_OK=" + str(w is not None))
    log("DONE")
    flush()

try:
    main()
except Exception:
    log("EXC\n" + traceback.format_exc())
    flush()
