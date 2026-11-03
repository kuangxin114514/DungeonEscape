# -*- coding: utf-8 -*-
import unreal, sys, importlib, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\finalize_overhead_wc.txt"
L=[]
def log(m):
    L.append(str(m))
    try: unreal.log("FINOV:"+str(m))
    except Exception: print(m)
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(L)+"\n")

try:
    sys.path.insert(0,r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python")
    import shop_interact_runtime as r
    importlib.reload(r)
    r.bootstrap()
    log("ready %s %s"%(r._ENEMY_BAR_Z, r._ENEMY_DRAW))

    world=None
    try:
        world=unreal.EditorLevelLibrary.get_editor_world()
    except Exception as e:
        log("get_editor_world "+str(e))
    log("world="+ (world.get_path_name() if world else "None"))
    acts=[]
    try:
        acts=unreal.EditorLevelLibrary.get_all_level_actors()
    except Exception as e:
        log("actors "+str(e))
    log("actor_count="+str(len(acts) if acts else 0))
    for a in (acts or []):
        try:
            nm=a.get_name(); cn=a.get_class().get_name()
        except Exception:
            continue
        if ("Preview_Skeleton" not in nm) and ("BP_Enemy_Skeleton" not in cn):
            continue
        log("actor="+nm+" class="+cn+" loc="+str(a.get_actor_location()))
        wcs=[]
        try:
            wcs=list(a.get_components_by_class(unreal.WidgetComponent) or [])
        except Exception as e:
            log("wcs err "+str(e))
        log("wcs="+str(len(wcs)))
        if not wcs:
            wdg,pb,path=r._make_enemy_widget(world, None)
            log("make %s %s %s"%(wdg,pb,path))
            if wdg:
                r._fit_enemy_bar_layout(wdg,pb)
            wc=r._attach_widget_component(a, wdg)
            log("attached "+str(wc))
            wcs=[wc] if wc else []
        for wc in wcs:
            if wc is None: continue
            log("wc="+wc.get_name())
            try: wc.set_relative_location(unreal.Vector(0,0,float(r._ENEMY_BAR_Z)), False, False)
            except Exception as e: log("setrel "+str(e))
            try: wc.set_draw_size(unreal.Vector2D(float(r._ENEMY_DRAW[0]), float(r._ENEMY_DRAW[1])))
            except Exception as e: log("setdraw "+str(e))
            try: wc.set_widget_space(unreal.WidgetSpace.SCREEN)
            except Exception:
                try: wc.set_editor_property("space", unreal.WidgetSpace.SCREEN)
                except Exception as e: log("setspace "+str(e))
            wdg=None
            try: wdg=wc.get_user_widget_object()
            except Exception: wdg=None
            log("user="+str(wdg))
            if wdg is None:
                wdg,pb,path=r._make_enemy_widget(world, None)
                log("remake %s %s"%(wdg,pb))
                if wdg:
                    try: wc.set_widget(wdg)
                    except Exception as e: log("set_widget "+str(e))
            pb=None
            if wdg:
                try: pb=wdg.get_widget_from_name("PB_Health")
                except Exception: pb=None
                r._fit_enemy_bar_layout(wdg,pb)
                if pb:
                    try:
                        slot=unreal.WidgetLayoutLibrary.slot_as_canvas_slot(pb)
                        if slot:
                            log("anchors="+str(slot.get_anchors()))
                            log("offsets="+str(slot.get_offsets()))
                    except Exception as e:
                        log("slot "+str(e))
                    try: pb.set_percent(1.0)
                    except Exception: pass
            try:
                log("final rel=%s space=%s draw=%s"%(wc.get_editor_property("relative_location"), wc.get_editor_property("space"), wc.get_editor_property("draw_size")))
            except Exception as e:
                log("final "+str(e))
    log("DONE")
except Exception:
    log(traceback.format_exc())
flush()
