# -*- coding: utf-8 -*-
import unreal, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_bp_graph.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("BPG:"+str(m))
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")
try:
    bp=unreal.EditorAssetLibrary.load_asset("/Game/Core/Interact/BP_ShopInteract")
    log("bp="+str(bp)+" type="+str(type(bp)))
    log("dir_sample="+str([x for x in dir(bp) if "graph" in x.lower() or "uber" in x.lower() or "page" in x.lower() or "generated" in x.lower() or "class" in x.lower()][:40]))
    # ObjectIterator EdGraph under BP
    eg_cls=unreal.load_class(None,"/Script/Engine.EdGraph")
    log("EdGraph cls="+str(eg_cls))
    graphs=[]
    for o in unreal.ObjectIterator(eg_cls):
        try:
            pn=o.get_path_name()
            if "/Game/Core/Interact/BP_ShopInteract" in pn:
                graphs.append((o.get_name(), pn, o))
        except Exception:
            pass
    log("graphs_n="+str(len(graphs)))
    for name,pn,o in graphs:
        log("GRAPH "+name+" "+pn)
        try:
            nodes=list(o.get_editor_property("nodes"))
            log("  nodes="+str(len(nodes)))
            for n in nodes[:15]:
                log("  node "+n.get_class().get_name()+" "+n.get_name())
        except Exception as e:
            log("  nodes err "+str(e))
    # Try NewObject K2Node_Event
    if graphs:
        g=graphs[0][2]
        ev_cls=unreal.load_class(None,"/Script/BlueprintGraph.K2Node_Event")
        log("ev_cls="+str(ev_cls))
        try:
            node=unreal.new_object(ev_cls, g)
            log("new event node="+str(node))
            try:
                g.add_node(node, False, unreal.Vector2D(0,0))
                log("add_node ok")
            except Exception as e:
                log("add_node "+str(e))
                try:
                    nodes=list(g.get_editor_property("nodes"))
                    nodes.append(node)
                    g.set_editor_property("nodes", nodes)
                    log("set nodes ok")
                except Exception as e2:
                    log("set nodes "+str(e2))
        except Exception as e:
            log("new_object "+str(e))
    # uclass receive_tick test
    try:
        @unreal.uclass()
        class TickProbe(unreal.Actor):
            def _post_init(self):
                self._n=0
            @unreal.ufunction(override=True)
            def receive_begin_play(self):
                unreal.log("TickProbe begin_play")
                try:
                    self.set_actor_tick_enabled(True)
                except Exception as e:
                    unreal.log("tick enable "+str(e))
            @unreal.ufunction(override=True)
            def receive_tick(self, delta_seconds):
                self._n = getattr(self, "_n", 0) + 1
                if self._n <= 3:
                    unreal.log("TickProbe tick "+str(self._n))
        log("TickProbe class ok")
        # spawn in editor
        a=unreal.EditorLevelLibrary.spawn_actor_from_class(TickProbe, unreal.Vector(0,0,500), unreal.Rotator())
        log("spawned TickProbe "+str(a))
        if a:
            try:
                a.set_actor_tick_enabled(True)
                log("editor tick enabled")
            except Exception as e:
                log("editor tick "+str(e))
            # destroy so we don't pollute map
            try:
                a.destroy_actor()
                log("destroyed probe")
            except Exception as e:
                log("destroy "+str(e))
    except Exception as e:
        log("uclass tick fail "+traceback.format_exc())
    # GameplayStatics spawn APIs
    gs=unreal.GameplayStatics
    log("GS spawn-ish="+str([x for x in dir(gs) if "spawn" in x.lower()][:30]))
    # begin_deferred
    for name in ("begin_deferred_actor_spawn_from_class","finish_spawning_actor","get_all_actors_of_class"):
        log("GS.%s hasattr=%s"%(name, hasattr(gs,name)))
    log("DONE")
except Exception:
    log(traceback.format_exc())
flush()