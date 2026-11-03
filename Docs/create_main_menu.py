# -*- coding: utf-8 -*-
import unreal
import os
import re

MENUS = "/Game/UI/Menus"
MAPS_DIR = "/Game/Maps/MainMenu"
GAMEFLOW = "/Game/Core/GameFlow"
HUB = "/Game/Maps/Hub/Map_Hub"
MENU_MAP = "/Game/Maps/MainMenu/Map_MainMenu"
INI = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Config\DefaultEngine.ini"

def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)

def save(asset):
    if asset:
        unreal.EditorAssetLibrary.save_loaded_asset(asset)

def create_bp(parent, path, name):
    full = path + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("ParentClass", parent)
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, path, None, factory)
    save(bp)
    unreal.log("BP " + full)
    return unreal.EditorAssetLibrary.load_asset(full)

def create_wbp():
    ensure_dir(MENUS)
    full = MENUS + "/WBP_MainMenu"
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
    factory = unreal.WidgetBlueprintFactory()
    try:
        factory.set_editor_property("ParentClass", unreal.UserWidget)
    except Exception:
        pass
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    wbp = tools.create_asset("WBP_MainMenu", MENUS, unreal.WidgetBlueprint, factory)
    if not wbp:
        wbp = tools.create_asset("WBP_MainMenu", MENUS, None, factory)
    save(wbp)
    wbp = unreal.EditorAssetLibrary.load_asset(full)
    tree = wbp.widget_tree
    canvas = tree.construct_widget(unreal.CanvasPanel, "RootCanvas")
    tree.root_widget = canvas

    bg = tree.construct_widget(unreal.Image, "Img_Dim")
    slot = canvas.add_child_to_canvas(bg)
    slot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(0, 0), maximum=unreal.Vector2D(1, 1)))
    slot.set_offsets(unreal.Margin(0, 0, 0, 0))
    try:
        bg.set_color_and_opacity(unreal.LinearColor(0.015, 0.015, 0.04, 0.94))
    except Exception:
        pass

    title = tree.construct_widget(unreal.TextBlock, "Txt_Title")
    title.set_editor_property("text", unreal.Text("地牢逃脱"))
    try:
        fi = title.get_editor_property("font")
        fi.size = 72
        title.set_editor_property("font", fi)
    except Exception:
        pass
    ts = canvas.add_child_to_canvas(title)
    ts.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(0.5, 0.2), maximum=unreal.Vector2D(0.5, 0.2)))
    ts.set_alignment(unreal.Vector2D(0.5, 0.5))
    ts.set_auto_size(True)

    sub = tree.construct_widget(unreal.TextBlock, "Txt_Sub")
    sub.set_editor_property("text", unreal.Text("Dungeon Escape"))
    ss = canvas.add_child_to_canvas(sub)
    ss.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(0.5, 0.3), maximum=unreal.Vector2D(0.5, 0.3)))
    ss.set_alignment(unreal.Vector2D(0.5, 0.5))
    ss.set_auto_size(True)

    def add_btn(wname, label, y):
        btn = tree.construct_widget(unreal.Button, wname)
        txt = tree.construct_widget(unreal.TextBlock, wname + "_Txt")
        txt.set_editor_property("text", unreal.Text(label))
        try:
            btn.set_content(txt)
        except Exception:
            pass
        bs = canvas.add_child_to_canvas(btn)
        bs.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(0.5, y), maximum=unreal.Vector2D(0.5, y)))
        bs.set_alignment(unreal.Vector2D(0.5, 0.5))
        bs.set_size(unreal.Vector2D(340, 70))
        return btn

    add_btn("Btn_Start", "开始游戏", 0.48)
    add_btn("Btn_Quit", "退出游戏", 0.6)

    hint = tree.construct_widget(unreal.TextBlock, "Txt_Hint")
    hint.set_editor_property("text", unreal.Text("开始游戏 → 进入主城 Map_Hub"))
    hs = canvas.add_child_to_canvas(hint)
    hs.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(0.5, 0.75), maximum=unreal.Vector2D(0.5, 0.75)))
    hs.set_alignment(unreal.Vector2D(0.5, 0.5))
    hs.set_auto_size(True)

    save(wbp)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
    except Exception:
        pass
    unreal.log("WBP_MainMenu ready")
    return wbp

def find_pins(node):
    try:
        return list(node.pins)
    except Exception:
        try:
            return list(node.get_editor_property("pins"))
        except Exception:
            return []

def pin_by_name(node, name):
    for p in find_pins(node):
        try:
            n = str(p.get_editor_property("pin_name"))
        except Exception:
            n = str(getattr(p, "pin_name", ""))
        if name.lower() in n.lower():
            return p
    return None

def pin_exec_out(node):
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_OUTPUT:
                if "exec" in str(p.get_editor_property("pin_type")).lower() or str(p.get_editor_property("pin_name")) in ("then", "execute", ""):
                    # prefer then
                    pass
        except Exception:
            pass
    # heuristic
    outs = []
    for p in find_pins(node):
        try:
            direction = p.get_editor_property("direction")
            pname = str(p.get_editor_property("pin_name"))
            if direction == unreal.EdGraphPinDirection.EGPD_OUTPUT and pname in ("then", "execute", "Completed", ""):
                outs.append(p)
        except Exception:
            continue
    return outs[0] if outs else (find_pins(node)[-1] if find_pins(node) else None)

def pin_exec_in(node):
    for p in find_pins(node):
        try:
            direction = p.get_editor_property("direction")
            pname = str(p.get_editor_property("pin_name"))
            if direction == unreal.EdGraphPinDirection.EGPD_INPUT and pname in ("execute", ""):
                return p
        except Exception:
            continue
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_INPUT:
                return p
        except Exception:
            continue
    return None

def try_link(a, b):
    if not a or not b:
        return False
    try:
        a.make_link_to(b)
        return True
    except Exception:
        try:
            schema = unreal.EdGraphSchema_K2()
            schema.try_create_connection(a, b)
            return True
        except Exception as e:
            unreal.log_warning("link fail " + str(e))
            return False

def wire_widget_buttons(wbp):
    """Wire Btn_Start OnClicked -> OpenLevel Map_Hub; Btn_Quit -> QuitGame."""
    try:
        # Widget BPs store graphs in ubergraph_pages too
        pages = list(wbp.ubergraph_pages)
        if not pages:
            unreal.log_warning("WBP no graph pages")
            return False
        graph = pages[0]
        # Start bind event
        start_ev = unreal.new_object(unreal.K2Node_ComponentBoundEvent, graph)
        try:
            start_ev.set_editor_property("component_property_name", "Btn_Start")
        except Exception:
            pass
        try:
            start_ev.component_property_name = "Btn_Start"
        except Exception:
            pass
        # Delegate OnClicked - property names vary
        for prop, val in [("delegate_property_name", "OnClicked"), ("delegate_reference", None)]:
            try:
                if val is not None:
                    start_ev.set_editor_property(prop, val)
            except Exception:
                pass
        start_ev.node_pos_x = 0
        start_ev.node_pos_y = 0
        graph.add_node(start_ev, False, False)

        # Open Level
        open_node = unreal.new_object(unreal.K2Node_CallFunction, graph)
        open_node.node_pos_x = 400
        open_node.node_pos_y = 0
        # Set function to GameplayStatics.OpenLevel
        try:
            open_node.set_from_function(unreal.GameplayStatics.static_class().static_class() and None)
        except Exception:
            pass
        try:
            # member reference
            unreal.K2Node_CallFunction.set_from_function(open_node, unreal.find_object(None, "/Script/Engine.Default__GameplayStatics:OpenLevel"))
        except Exception:
            try:
                func = unreal.GameplayStatics.static_class().get_editor_property("open_level")
            except Exception:
                pass
        # Alternative: set function name via member_reference
        try:
            mr = open_node.get_editor_property("function_reference")
            mr.set_editor_property("member_name", "OpenLevel")
            mr.set_editor_property("member_parent", unreal.GameplayStatics.static_class())
            open_node.set_editor_property("function_reference", mr)
        except Exception as e:
            unreal.log_warning("openlevel ref: " + str(e))
        graph.add_node(open_node, False, False)

        # Quit bind
        quit_ev = unreal.new_object(unreal.K2Node_ComponentBoundEvent, graph)
        try:
            quit_ev.component_property_name = "Btn_Quit"
        except Exception:
            pass
        quit_ev.node_pos_x = 0
        quit_ev.node_pos_y = 280
        graph.add_node(quit_ev, False, False)

        quit_node = unreal.new_object(unreal.K2Node_CallFunction, graph)
        quit_node.node_pos_x = 400
        quit_node.node_pos_y = 280
        try:
            mr = quit_node.get_editor_property("function_reference")
            mr.set_editor_property("member_name", "QuitGame")
            mr.set_editor_property("member_parent", unreal.KismetSystemLibrary.static_class())
            quit_node.set_editor_property("function_reference", mr)
        except Exception as e:
            unreal.log_warning("quit ref: " + str(e))
        graph.add_node(quit_node, False, False)

        save(wbp)
        unreal.log("widget events nodes added")
        return True
    except Exception as e:
        unreal.log_warning("wire_widget_buttons: " + str(e))
        return False

def wire_gm_show_menu(gm, wbp):
    """GM BeginPlay: CreateWidget WBP_MainMenu, AddToViewport, SetInputMode UIOnly."""
    try:
        pages = list(gm.ubergraph_pages)
        if not pages:
            return False
        graph = pages[0]
        ev = unreal.new_object(unreal.K2Node_Event, graph)
        try:
            ev.event_reference.member_name = "ReceiveBeginPlay"
        except Exception:
            try:
                ref = ev.get_editor_property("event_reference")
                ref.set_editor_property("member_name", "ReceiveBeginPlay")
            except Exception:
                pass
        ev.node_pos_x = 0
        ev.node_pos_y = 0
        graph.add_node(ev, False, False)

        cw = unreal.new_object(unreal.K2Node_CreateWidget, graph)
        cw.node_pos_x = 280
        cw.node_pos_y = 0
        try:
            cw.set_editor_property("widget_class", wbp.generated_class())
        except Exception:
            try:
                cw.widget_class = wbp.generated_class
            except Exception as e:
                unreal.log_warning("cw class " + str(e))
        graph.add_node(cw, False, False)

        # Add to Viewport
        addv = unreal.new_object(unreal.K2Node_CallFunction, graph)
        addv.node_pos_x = 560
        addv.node_pos_y = 0
        try:
            mr = addv.get_editor_property("function_reference")
            mr.set_editor_property("member_name", "AddToViewport")
            # UserWidget.AddToViewport
            mr.set_editor_property("member_parent", unreal.UserWidget.static_class())
            addv.set_editor_property("function_reference", mr)
        except Exception as e:
            unreal.log_warning("addv " + str(e))
        graph.add_node(addv, False, False)

        save(gm)
        unreal.log("gm beginplay nodes added")
        return True
    except Exception as e:
        unreal.log_warning("wire_gm: " + str(e))
        return False

def make_map(gm):
    ensure_dir(MAPS_DIR)
    if not unreal.EditorAssetLibrary.does_asset_exist(MENU_MAP):
        if unreal.EditorAssetLibrary.does_asset_exist(HUB):
            unreal.EditorAssetLibrary.duplicate_asset("Map_MainMenu", MAPS_DIR, HUB)
            unreal.log("duplicated hub -> main menu map")
        else:
            unreal.EditorLevelLibrary.new_level(MENU_MAP)
    unreal.EditorLoadingAndSavingUtils.load_map(MENU_MAP)
    # wipe gameplay actors, keep lights/sky/playerstart
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        cls = a.get_class().get_name()
        lab = a.get_actor_label()
        keep = any(k in cls for k in ("Light", "Sky", "Fog", "Atmosphere", "Reflection", "PlayerStart", "WorldSettings", "Brush", "DefaultPhysicsVolume", "Gameplay"))
        keep = keep or lab in ("Floor", "HubGround_Plane", "Menu_Camera", "Menu_Title3D")
        if lab.startswith("Hub"):
            keep = False
        if "ThirdPerson" in lab or "Character" in cls and "Player" not in cls:
            keep = False
        if not keep and "WorldSettings" not in cls and "Brush" not in cls and "PhysicsVolume" not in cls:
            try:
                unreal.EditorLevelLibrary.destroy_actor(a)
            except Exception:
                pass

    # ensure player start
    has_ps = False
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if "PlayerStart" in a.get_class().get_name():
            has_ps = True
            a.set_actor_location(unreal.Vector(0, 0, 100), False, True)
    if not has_ps:
        ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 100), unreal.Rotator())
        if ps:
            ps.set_actor_label("Menu_PlayerStart")

    # camera
    cam = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(-400, 0, 180), unreal.Rotator(0, 0, 0))
    if cam:
        cam.set_actor_label("Menu_Camera")

    # soft light if none
    has_light = any("DirectionalLight" in a.get_class().get_name() for a in unreal.EditorLevelLibrary.get_all_level_actors())
    if not has_light:
        sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 500), unreal.Rotator(-40, 30, 0))
        if sun:
            sun.set_actor_label("Menu_Sun")

    # world game mode override
    try:
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if "WorldSettings" in a.get_class().get_name():
                a.set_editor_property("default_game_mode", gm.generated_class())
                unreal.log("world GM set")
    except Exception as e:
        unreal.log_warning("world gm " + str(e))

    unreal.EditorLevelLibrary.save_current_level()

def set_ini():
    try:
        with open(INI, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        if "EditorStartupMap=" in text:
            text = re.sub(r"EditorStartupMap=.*", "EditorStartupMap=/Game/Maps/MainMenu/Map_MainMenu", text)
        else:
            text += "\nEditorStartupMap=/Game/Maps/MainMenu/Map_MainMenu\n"
        if "GameDefaultMap=" in text:
            text = re.sub(r"GameDefaultMap=.*", "GameDefaultMap=/Game/Maps/MainMenu/Map_MainMenu", text)
        else:
            text += "GameDefaultMap=/Game/Maps/MainMenu/Map_MainMenu\n"
        if "ServerDefaultMap=" in text:
            text = re.sub(r"ServerDefaultMap=.*", "ServerDefaultMap=/Game/Maps/MainMenu/Map_MainMenu", text)
        with open(INI, "w", encoding="utf-8") as f:
            f.write(text)
        unreal.log("ini updated")
    except Exception as e:
        unreal.log_warning("ini " + str(e))

def set_gm_defaults(gm):
    try:
        gen = gm.generated_class()
        cdo = unreal.get_default_object(gen)
        cdo.set_editor_property("default_pawn_class", unreal.SpectatorPawn.static_class())
        # no HUD
        unreal.log("gm spectator ok")
    except Exception as e:
        unreal.log_warning("gm defaults " + str(e))
    save(gm)

# ---- run ----
ensure_dir(MENUS)
ensure_dir(MAPS_DIR)
ensure_dir(GAMEFLOW)
wbp = create_wbp()
gm = create_bp(unreal.GameModeBase.static_class(), GAMEFLOW, "GM_MainMenu")
set_gm_defaults(gm)
wire_gm_show_menu(gm, wbp)
wire_widget_buttons(wbp)
try:
    unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
    unreal.BlueprintEditorLibrary.compile_blueprint(gm)
except Exception:
    pass
make_map(gm)
set_ini()
unreal.EditorAssetLibrary.save_directory(MENUS)
unreal.EditorAssetLibrary.save_directory(MAPS_DIR)
unreal.EditorAssetLibrary.save_directory(GAMEFLOW)
unreal.log("MAIN MENU CREATE DONE")
