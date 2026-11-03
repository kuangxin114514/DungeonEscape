# -*- coding: utf-8 -*-
import unreal, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_pie_spawn.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("PSP:"+str(m))
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")
try:
    world_cls = unreal.World.static_class()
    # sample World methods
    w = unreal.EditorLevelLibrary.get_editor_world()
    log("editor_world="+str(w))
    log("world spawn-ish="+str([x for x in dir(w) if "spawn" in x.lower() or "actor" in x.lower()][:50]))
    # InputComponent
    ic_cls = unreal.load_class(None, "/Script/Engine.InputComponent")
    log("InputComponent="+str(ic_cls))
    ic_cdo = unreal.get_default_object(ic_cls)
    log("IC bind-ish="+str([x for x in dir(ic_cdo) if "bind" in x.lower() or "action" in x.lower()][:40]))
    # try start simulate briefly
    try:
        unreal.EditorLevelLibrary.editor_play_simulate()
        log("editor_play_simulate called")
    except Exception as e:
        log("simulate fail "+str(e))
    import time
    # can't sleep long in editor easily - poll pie
    for i in range(8):
        unreal.SystemLibrary.delay  # no
        pie = unreal.EditorLevelLibrary.get_pie_worlds(False)
        gw = None
        try:
            gw = unreal.EditorLevelLibrary.get_game_world()
        except Exception:
            pass
        log("poll%d pie=%s gw=%s"%(i, pie, gw))
        if pie:
            pw = pie[0]
            log("PIE world methods spawn="+str([x for x in dir(pw) if "spawn" in x.lower()][:20]))
            pc = unreal.GameplayStatics.get_player_controller(pw, 0)
            log("PC="+str(pc))
            if pc:
                pawn = pc.get_controlled_pawn()
                log("Pawn="+str(pawn))
                try:
                    down = pc.is_input_key_down(unreal.Key(key_name="E"))
                    just = pc.was_input_key_just_pressed(unreal.Key(key_name="E"))
                    log("E down=%s just=%s"%(down, just))
                except Exception as e:
                    log("key err "+str(e))
            # try spawn actor into PIE via EditorLevelLibrary
            try:
                @unreal.uclass()
                class PieHelper(unreal.Actor):
                    @unreal.ufunction(override=True)
                    def receive_begin_play(self):
                        unreal.log("PieHelper begin_play world="+str(self.get_world()))
                    @unreal.ufunction(override=True)
                    def receive_tick(self, dt):
                        n=getattr(self,"_n",0)+1; self._n=n
                        if n<=2: unreal.log("PieHelper tick "+str(n))
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(PieHelper, unreal.Vector(0,0,300), unreal.Rotator())
                log("spawn_actor_from_class during PIE -> "+str(a)+" world="+str(a.get_world() if a else None))
                if a:
                    try:
                        a.set_actor_label("PieHelper_Diag")
                    except Exception:
                        pass
            except Exception as e:
                log("spawn during pie "+traceback.format_exc())
            break
        # small wait via slate - busy loop bad; use platform
        import time as _t; _t.sleep(0.4)
    # end play
    try:
        unreal.EditorLevelLibrary.editor_end_play()
        log("editor_end_play ok")
    except Exception as e:
        log("end_play "+str(e))
    log("DONE")
except Exception:
    log(traceback.format_exc())
flush()