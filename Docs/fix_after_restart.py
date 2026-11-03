
import unreal, sys, importlib, traceback, time
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_after_restart.txt"
L=[]
def log(m):
    L.append(str(m)); 
    try: unreal.log("AR:"+str(m))
    except Exception: pass
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(L)+"\n")
try:
    # Discover play APIs
    ell = unreal.EditorLevelLibrary
    play_apis=[a for a in dir(ell) if "play" in a.lower() or "pie" in a.lower() or "simulate" in a.lower()]
    log("play_apis="+str(play_apis))
    # Load map if needed
    try:
        cur = ell.get_editor_world()
        log("editor_world="+str(cur))
        if cur:
            log("map="+str(cur.get_path_name()))
    except Exception as e:
        log("get world "+str(e))
    try:
        # Ensure Map_Hub
        if cur is None or "Map_Hub" not in str(cur.get_path_name()):
            ok = unreal.EditorLoadingAndSavingUtils.load_map("/Game/Maps/Hub/Map_Hub")
            log("load_map="+str(ok))
            time.sleep(1)
    except Exception as e:
        log("load_map err "+str(e))
    # Start PIE
    started=False
    for name in ("editor_play_simulate","pilot_level_actor","editor_request_play"):
        fn=getattr(ell, name, None)
        if callable(fn):
            try:
                fn()
                log("called "+name)
                started=True
                break
            except Exception as e:
                log(name+" "+str(e))
    if not started:
        # try console
        try:
            unreal.SystemLibrary.execute_console_command(None, "KeepMapOpenOnStop 1")
        except Exception:
            pass
        # LevelEditorPlaySettings + request via EditorEngine
        try:
            eng = unreal.UnrealEditorSubsystem  # may fail UE4
        except Exception as e:
            log("no UnrealEditorSubsystem "+str(e))
        try:
            # Fallback: slate tick only works in PIE; try simulate
            if hasattr(ell, "editor_play_simulate"):
                ell.editor_play_simulate()
                log("simulate2")
                started=True
        except Exception as e:
            log("sim2 "+str(e))
    # Wait a moment for PIE world
    PY=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if PY not in sys.path: sys.path.insert(0,PY)
    import shop_interact_runtime as r
    importlib.reload(r)
    pie=None
    for i in range(20):
        pie=r._pie_world()
        if pie: break
        time.sleep(0.5)
    log("pie="+str(pie))
    if not pie:
        # Try create widget in editor world as secondary proof of create()
        world = ell.get_editor_world()
        pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
        log("editor pc="+str(pc))
        wbl=unreal.get_default_object(unreal.load_class(None,"/Script/UMG.WidgetBlueprintLibrary"))
        wcls=unreal.load_class(None,"/Game/UI/Shop/WBP_Shop.WBP_Shop_C")
        w=None
        try:
            w=wbl.call_method("create",(),{"world_context_object":world,"widget_type":wcls,"owning_player":pc})
        except Exception as e:
            log("create editor "+str(e))
        log("editor_create="+str(w))
        if w:
            base=w.get_path_name(); n=0
            for o in unreal.ObjectIterator(unreal.TextBlock):
                try:
                    if base in o.get_path_name(): n+=1
                except Exception: pass
                if n>=1: break
            log("editor_texts="+str(n))
            try: w.remove_from_parent()
            except Exception: pass
            log("PROOF_CREATE_API=True")
        else:
            log("PROOF_CREATE_API=False")
        flush(); 
    else:
        r.close_shop(pie)
        ok=r.open_shop(pie, u"武器店")
        log("open_shop="+str(ok))
        wid=r._OPEN_WIDGET[0]
        log("widget="+str(wid))
        n=0
        if wid:
            base=wid.get_path_name()
            for o in unreal.ObjectIterator(unreal.TextBlock):
                try:
                    if base in o.get_path_name(): n+=1
                except Exception: pass
                if n>=2: break
            log("texts="+str(n)+" vis="+str(wid.get_visibility())+" invp="+str(wid.is_in_viewport()))
        log("PROOF="+str(bool(ok and wid and n>0)))
        flush()
except Exception:
    log(traceback.format_exc()); flush()
