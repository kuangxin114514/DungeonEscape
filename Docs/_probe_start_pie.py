# -*- coding: utf-8 -*-
import unreal, traceback, time
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_start_pie.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("SPIE:"+str(m))
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")

def list_worlds(tag):
    rows=[]
    for w in unreal.ObjectIterator(unreal.World.static_class()):
        try:
            pc=None; pawn=None
            try:
                pc=unreal.GameplayStatics.get_player_controller(w,0)
                if pc: pawn=pc.get_controlled_pawn()
            except Exception:
                pass
            rows.append("%s name=%s path=%s pc=%s pawn=%s"%(tag, w.get_name(), w.get_path_name(), bool(pc), bool(pawn)))
        except Exception as e:
            rows.append("%s ERR %s"%(tag,e))
    return rows

try:
    log("=== START ===")
    for r in list_worlds("before"): log(r)
    # Try multiple play start methods
    methods=[]
    # 1 editor_play_simulate
    methods.append("editor_play_simulate")
    # 2 console on editor world
    ed=None
    try: ed=unreal.EditorLevelLibrary.get_editor_world()
    except Exception: pass
    log("editor_world="+str(ed))

    # Probe APIs
    for name in dir(unreal.EditorLevelLibrary):
        if any(k in name.lower() for k in ("play","pie","session","simulate","game")):
            methods.append("ELL."+name)
    log("ELL candidates="+str(methods))

    # Try LevelEditorSubsystem style
    for path in (
        "/Script/LevelEditor.LevelEditorSubsystem",
        "/Script/UnrealEd.LevelEditorPlaySettings",
        "/Script/UnrealEd.PlayWorldCommandCallbacks",
        "/Script/EditorScriptingUtilities.EditorLevelLibrary",
    ):
        try:
            c=unreal.load_class(None,path)
            log("load "+path+" -> "+str(c))
            if c:
                log("  dir sample="+str([x for x in dir(unreal.get_default_object(c)) if "play" in x.lower() or "pie" in x.lower() or "session" in x.lower()][:30]))
        except Exception as e:
            log("load "+path+" "+str(e))

    # hasattr unreal
    log("hasattr LevelEditorSubsystem="+str(hasattr(unreal,"LevelEditorSubsystem")))
    log("hasattr start_play="+str(hasattr(unreal.EditorLevelLibrary,"start_play")))

    # Try execute console "forcenextpiewindow" etc
    if ed:
        for cmd in ("showflag.collision 1",):
            try:
                unreal.SystemLibrary.execute_console_command(ed, cmd)
                log("exec "+cmd)
            except Exception as e:
                log("exec fail "+str(e))

    # Start simulate and heavily poll ObjectIterator worlds
    try:
        unreal.EditorLevelLibrary.editor_play_simulate()
        log("simulate started")
    except Exception as e:
        log("simulate "+str(e))

    for i in range(15):
        time.sleep(0.5)
        pie=None
        try: pie=unreal.EditorLevelLibrary.get_pie_worlds(False)
        except Exception as e: pie="ERR "+str(e)
        gw=None
        try: gw=unreal.EditorLevelLibrary.get_game_world()
        except Exception as e: gw="ERR "+str(e)
        worlds=list_worlds("t%d"%i)
        has_pawn=any("pawn=True" in r for r in worlds)
        log("poll%d pie=%s gw=%s pawn_world=%s"%(i, pie, gw, has_pawn))
        if has_pawn or (pie and pie!="ERR" and len(pie)>0):
            for r in worlds: log(r)
            # test runtime scan
            import sys
            PY=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
            if PY not in sys.path: sys.path.insert(0,PY)
            import shop_interact_runtime as sir
            w=sir._get_pie_world()
            log("runtime _get_pie_world="+str(w))
            if w:
                pc=unreal.GameplayStatics.get_player_controller(w,0)
                pawn=pc.get_controlled_pawn() if pc else None
                log("runtime pc/pawn=%s / %s"%(pc,pawn))
                if pawn:
                    loc=pawn.get_actor_location()
                    title,gate=sir._scan_near(w, loc)
                    log("near title=%s gate=%s pawn=%s"%(title,gate,loc))
                    # Force open shop to verify widget path
                    sir.open_shop_widget(w, title or "测试店")
                    log("forced open widget="+str(sir._OPEN_WIDGET[0]))
            break
    try:
        unreal.EditorLevelLibrary.editor_end_play()
        log("end_play")
    except Exception as e:
        log("end "+str(e))
    log("=== DONE ===")
except Exception:
    log(traceback.format_exc())
flush()