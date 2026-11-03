# -*- coding: utf-8 -*-
import unreal, sys, importlib, traceback, time
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_pie_shop.txt"
L=[]
def log(m):
    L.append(str(m))
    try: unreal.log("PS:"+str(m))
    except Exception: pass
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(L)+"\n")

def patch_pie_world():
    path=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
    src=open(path,encoding="utf-8").read()
    if "get_pie_worlds" in src:
        log("pie_world already patched")
        return
    old='''def _pie_world():
    try:
        worlds = unreal.EditorLevelLibrary.get_pie_worlds(False)
        if worlds:
            return worlds[0]
    except Exception:
        pass
    for o in unreal.ObjectIterator(unreal.World):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "UEDPIE" in pn:
            return o
    return None'''
    # find actual function - may differ
    if "def _pie_world" not in src:
        log("no _pie_world fn")
        return
    # Replace body by injecting better detection at start of function via unique marker
    new_fn = '''def _pie_world():
    # Prefer official PIE/Simulate worlds
    try:
        worlds = unreal.EditorLevelLibrary.get_pie_worlds(False)
        if worlds:
            return worlds[0]
    except Exception:
        pass
    try:
        worlds = unreal.EditorLevelLibrary.get_pie_worlds(True)
        if worlds:
            return worlds[0]
    except Exception:
        pass
    for o in unreal.ObjectIterator(unreal.World):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "UEDPIE" in pn or "UEDPIE_0_Map_Hub" in pn:
            return o
        # Simulate-in-editor worlds often lack UEDPIE prefix
        if "Map_Hub" in pn and "Editor" not in pn and o != unreal.EditorLevelLibrary.get_editor_world():
            # likely PIE/sim
            try:
                if o.get_world_type().name in ("PIE", "Game", "GamePreview"):
                    return o
            except Exception:
                pass
    return None
'''
    import re
    src2=re.sub(r"def _pie_world\(\):(?:\n(?:[ \t].*\n|\n))*?(?=\ndef |\Z)", new_fn+"\n", src, count=1)
    if src2==src:
        log("regex replace failed — append override")
        src2 = src + "\n\n# V8 override\n" + new_fn
    open(path,"w",encoding="utf-8").write(src2)
    log("patched _pie_world")

try:
    patch_pie_world()
    # Inspect pie worlds now
    for flag in (False, True):
        try:
            ws=unreal.EditorLevelLibrary.get_pie_worlds(flag)
            log("get_pie_worlds(%s)=%s"%(flag, ws))
            if ws:
                for w in ws:
                    log("  "+w.get_path_name()+" type="+str(getattr(w,"world_type",None)))
        except Exception as e:
            log("get_pie_worlds %s ERR %s"%(flag,e))
    # If no pie, start simulate again
    ws=None
    try:
        ws=unreal.EditorLevelLibrary.get_pie_worlds(False)
    except Exception:
        pass
    if not ws:
        try:
            unreal.EditorLevelLibrary.editor_end_play()
            time.sleep(0.5)
        except Exception as e:
            log("end_play "+str(e))
        try:
            unreal.EditorLevelLibrary.editor_play_simulate()
            log("started simulate")
            time.sleep(2)
        except Exception as e:
            log("sim "+str(e))
    PY=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if PY not in sys.path: sys.path.insert(0,PY)
    import shop_interact_runtime as r
    importlib.reload(r)
    pie=None
    for i in range(15):
        pie=r._pie_world()
        if pie: break
        # also raw
        try:
            ws=unreal.EditorLevelLibrary.get_pie_worlds(False)
            if ws:
                pie=ws[0]; break
        except Exception:
            pass
        time.sleep(0.4)
    log("pie="+str(pie))
    if pie:
        ok=r.open_shop(pie, u"武器店")
        log("open_shop="+str(ok))
        wid=r._OPEN_WIDGET[0]
        log("widget="+str(wid))
        n=0
        if wid:
            base=wid.get_path_name()
            for o in unreal.ObjectIterator(unreal.TextBlock):
                try:
                    if base in o.get_path_name():
                        n+=1
                        try: o.set_text(unreal.Text("SHOP OPEN"))
                        except Exception: pass
                except Exception:
                    pass
                if n>=2: break
            log("texts=%d vis=%s invp=%s"%(n, wid.get_visibility(), wid.is_in_viewport()))
        log("PROOF="+str(bool(ok and wid and n>0 and wid.is_in_viewport())))
    else:
        # Still prove create API on editor world
        world=unreal.EditorLevelLibrary.get_editor_world()
        wbl=unreal.get_default_object(unreal.load_class(None,"/Script/UMG.WidgetBlueprintLibrary"))
        wcls=unreal.load_class(None,"/Game/UI/Shop/WBP_Shop.WBP_Shop_C")
        w=wbl.call_method("create",(),{"world_context_object":world,"widget_type":wcls,"owning_player":None})
        log("fallback_create="+str(w))
        n=0
        if w:
            base=w.get_path_name()
            for o in unreal.ObjectIterator(unreal.TextBlock):
                try:
                    if base in o.get_path_name(): n+=1
                except Exception: pass
                if n>=1: break
            try:
                w.set_visibility(unreal.SlateVisibility.VISIBLE)
                w.add_to_viewport(300)
            except Exception as e:
                log("vp "+str(e))
            log("texts="+str(n))
            log("PROOF_CREATE="+str(n>0))
        else:
            log("PROOF=False")
    flush()
except Exception:
    log(traceback.format_exc()); flush()
