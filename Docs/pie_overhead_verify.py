# -*- coding: utf-8 -*-
import unreal, time, traceback, sys, importlib, os
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\pie_overhead_verify.txt"
L=[]
def log(m):
    L.append(str(m))
    try: unreal.log("PIEOV:"+str(m))
    except Exception: print(m)
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(L)+"\n")

sys.path.insert(0,r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python")
import shop_interact_runtime as r
importlib.reload(r)
r.bootstrap()
log("bootstrapped Z=%s draw=%s"%(r._ENEMY_BAR_Z, r._ENEMY_DRAW))

# Ensure dungeon map is current editor world
try:
    w=unreal.EditorLevelLibrary.get_editor_world()
    log("editor="+ (w.get_path_name() if w else None))
except Exception as e:
    log("editor "+str(e))

# Start PIE selected viewport if possible
started=False
for attempt in (
    lambda: unreal.LevelEditorSubsystem().editor_request_play_session(
        unreal.PlayInEditorSessionInfo() if False else None
    ),
):
    pass

# Try console / EditorLevelLibrary methods
methods = []
for name in dir(unreal.EditorLevelLibrary):
    if "play" in name.lower() or "pie" in name.lower() or "simulate" in name.lower():
        methods.append(name)
log("ELL play-ish methods="+str(methods))

try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    log("LES="+str(les))
    if les:
        for name in dir(les):
            if "play" in name.lower() or "pie" in name.lower() or "session" in name.lower():
                log("LES."+name)
except Exception as e:
    log("LES "+str(e))

# Common UE4.27 approach
try:
    unreal.EditorLevelLibrary.editor_play_simulate()
    log("editor_play_simulate called")
    started=True
except Exception as e:
    log("simulate "+str(e))

# Wait for PIE
world=None
for i in range(40):
    time.sleep(0.25)
    try:
        ws=unreal.EditorLevelLibrary.get_pie_worlds(False) or unreal.EditorLevelLibrary.get_pie_worlds(True)
    except Exception:
        ws=None
    gw=None
    try:
        gw=unreal.EditorLevelLibrary.get_game_world()
    except Exception:
        gw=None
    log("wait %d pie=%s game=%s bars=%d"%(i, bool(ws), bool(gw), len(r._ENEMY_BARS)))
    if ws:
        world=ws[0]
        break
    if gw:
        world=gw
        break

if not world:
    log("NO_PIE - trying EditorActorSubsystem attach on preview instead")
    # Editor-time attach on Preview_Skeleton_1 so user can see component in viewport even without PIE? WidgetComponent may not show in editor the same way.
    try:
        acts=unreal.EditorLevelLibrary.get_all_level_actors()
        for a in acts:
            if "Preview_Skeleton" in a.get_name():
                log("preview "+a.get_name())
                # create WC on editor actor
                widget,pb,wpath=r._make_enemy_widget(unreal.EditorLevelLibrary.get_editor_world(), None)
                log("widget=%s pb=%s %s"%(widget,pb,wpath))
                if widget:
                    r._fit_enemy_bar_layout(widget,pb)
                wc=r._attach_widget_component(a, widget)
                log("editor wc="+str(wc))
                if wc:
                    for prop in ("relative_location","draw_size","space"):
                        try: log(" %s=%s"%(prop, wc.get_editor_property(prop)))
                        except Exception as e: log(" %s err %s"%(prop,e))
                    try: log(" user=%s"%wc.get_user_widget_object())
                    except Exception as e: log(" user err "+str(e))
                break
    except Exception:
        log(traceback.format_exc())
    flush(); 
else:
    log("world="+world.get_path_name())
    pc=unreal.GameplayStatics.get_player_controller(world,0)
    pawn=None
    try:
        pawn=pc.get_controlled_pawn() if pc else None
    except Exception:
        pass
    log("pc=%s pawn=%s"%(pc,pawn))
    try:
        r._clear_enemy_bars()
        r.ensure_enemy_health_bars(world, pc, pawn)
        log("ensure bars=%d"%len(r._ENEMY_BARS))
    except Exception:
        log(traceback.format_exc())
    for k,st in list(r._ENEMY_BARS.items()):
        log("BAR %s hp=%s/%s wc=%s pb=%s"%(k, st.get("health"), st.get("max_health"), st.get("wc"), st.get("pb")))
        wc=st.get("wc")
        if wc:
            for prop in ("relative_location","draw_size","space","pivot"):
                try: log("  %s=%s"%(prop, wc.get_editor_property(prop)))
                except Exception as e: log("  %s err %s"%(prop,e))
            try: log("  user=%s"%wc.get_user_widget_object())
            except Exception as e: log("  user err "+str(e))
            try: log("  comploc=%s"%wc.get_component_location())
            except Exception as e: log("  comploc "+str(e))
    flush()
