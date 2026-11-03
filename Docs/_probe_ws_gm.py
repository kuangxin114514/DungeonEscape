# -*- coding: utf-8 -*-
import unreal, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_ws_gm.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("WSGM:"+str(m))
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")
try:
    world=unreal.EditorLevelLibrary.get_editor_world()
    log("world="+str(world)+" path="+ (world.get_path_name() if world else ""))
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        cn=a.get_class().get_name()
        if "WorldSettings" in cn or "GameMode" in cn or a.get_actor_label().startswith("WorldSettings"):
            log("actor %s cls=%s label=%s"%(a.get_name(), cn, a.get_actor_label()))
            # dump properties with game/mode/pawn/controller in name via dir? get_editor_property list unknown
            for p in ("default_game_mode","DefaultGameMode","game_mode_class","GameModeOverride","default_game_mode_class",
                      "kill_z","b_enable_world_composition"):
                try: log("  %s=%s"%(p, a.get_editor_property(p)))
                except Exception as e: pass
    # WorldSettings via GameplayStatics?
    try:
        ws = unreal.GameplayStatics.get_game_mode(world)
        log("get_game_mode(editor)="+str(ws))
    except Exception as e:
        log("get_game_mode "+str(e))
    # Iterate WorldSettings class
    ws_cls = unreal.load_class(None, "/Script/Engine.WorldSettings")
    log("WorldSettings cls="+str(ws_cls))
    if ws_cls:
        for a in unreal.GameplayStatics.get_all_actors_of_class(world, ws_cls):
            log("WS actor "+a.get_name())
            for p in dir(a):
                if "game" in p.lower() or "mode" in p.lower() or "pawn" in p.lower() or "controller" in p.lower():
                    try:
                        val=getattr(a,p)
                        if not callable(val):
                            log("  attr %s=%s"%(p,val))
                    except Exception:
                        pass
            for p in ("default_game_mode","DefaultGameMode"):
                try: log("  prop %s=%s"%(p,a.get_editor_property(p)))
                except Exception as e: log("  prop %s ERR %s"%(p,e))
    log("DONE")
except Exception:
    log(traceback.format_exc())
flush()