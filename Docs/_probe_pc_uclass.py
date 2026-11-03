# -*- coding: utf-8 -*-
import unreal, sys, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_pc_uclass.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("PCU:"+str(m))
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")
try:
    PY=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if PY not in sys.path: sys.path.insert(0, PY)

    @unreal.uclass()
    class DE_ShopPC(unreal.PlayerController):
        @unreal.ufunction(override=True)
        def receive_begin_play(self):
            unreal.log("DE_ShopPC begin_play")
            try:
                self.set_actor_tick_enabled(True)
            except Exception as e:
                unreal.log("DE_ShopPC tick en "+str(e))
        @unreal.ufunction(override=True)
        def receive_tick(self, dt):
            n=getattr(self,"_n",0)+1
            self._n=n
            if n==1 or n%180==0:
                unreal.log("DE_ShopPC tick "+str(n))
            # Edge detect E and open shop via runtime
            try:
                import shop_interact_runtime as sir
                world=self.get_world()
                down=False
                try:
                    down=bool(self.is_input_key_down(unreal.Key(key_name="E")))
                except Exception:
                    down=False
                prev=getattr(self,"_prev_e", False)
                self._prev_e=down
                pressed=down and not prev
                if pressed:
                    unreal.log("DE_ShopPC E pressed")
                    pawn=self.get_controlled_pawn()
                    if pawn:
                        title,gate=sir._scan_near(world, pawn.get_actor_location())
                        unreal.log("DE_ShopPC near %s gate=%s"%(title,gate))
                        if sir._OPEN_WIDGET[0] is not None:
                            sir.close_shop_widget(world)
                        elif title:
                            sir.open_shop_widget(world, title)
                        elif gate:
                            try:
                                unreal.KismetSystemLibrary.print_string(world, "地下城入口（待接入）", True, True, unreal.LinearColor(1,0.85,0.2,1), 3.0)
                            except Exception:
                                pass
            except Exception as e:
                if getattr(self,"_n",0) < 5:
                    unreal.log("DE_ShopPC tick err "+str(e))

    log("DE_ShopPC="+str(DE_ShopPC)+" static="+str(DE_ShopPC.static_class()))

    # Set on GM_Hub CDO (runtime for this editor session; may not persist class ref)
    gm_cls = unreal.load_class(None, "/Game/Core/GameFlow/GM_Hub.GM_Hub_C")
    log("GM_Hub_C="+str(gm_cls))
    cdo = unreal.get_default_object(gm_cls)
    try:
        old = cdo.get_editor_property("player_controller_class")
        log("old PC class="+str(old))
    except Exception as e:
        log("old PC "+str(e)); old=None
    try:
        cdo.set_editor_property("player_controller_class", DE_ShopPC.static_class())
        log("set PC class OK -> "+str(cdo.get_editor_property("player_controller_class")))
    except Exception as e:
        log("set PC FAIL "+traceback.format_exc())

    # Also try ThirdPersonGameMode if Map uses that
    for path in (
        "/Game/ThirdPersonBP/Blueprints/ThirdPersonGameMode.ThirdPersonGameMode_C",
        "/Game/Core/GameFlow/GM_Dungeon.GM_Dungeon_C",
    ):
        try:
            cls=unreal.load_class(None, path)
            if not cls: 
                log("no "+path); continue
            d=unreal.get_default_object(cls)
            try:
                log(path+" PC="+str(d.get_editor_property("player_controller_class")))
            except Exception as e:
                log(path+" "+str(e))
        except Exception as e:
            log(path+" load "+str(e))

    # Check Map_Hub world settings game mode override
    try:
        unreal.EditorLoadingAndSavingUtils.load_map("/Game/Maps/Hub/Map_Hub")
        world=unreal.EditorLevelLibrary.get_editor_world()
        ws=world.get_editor_property("world_settings") if world else None
        # WorldSettings often via actor
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if a.get_class().get_name().startswith("WorldSettings"):
                try:
                    gm=a.get_editor_property("default_game_mode")
                    log("WorldSettings default_game_mode="+str(gm))
                except Exception:
                    try:
                        gm=a.get_editor_property("DefaultGameMode")
                        log("WorldSettings DefaultGameMode="+str(gm))
                    except Exception as e:
                        log("WS gm err "+str(e))
                try:
                    # game_mode_override / authored
                    for p in ("default_game_mode","game_mode_override","DefaultGameMode"):
                        try: log("WS.%s=%s"%(p,a.get_editor_property(p)))
                        except Exception: pass
                except Exception:
                    pass
    except Exception as e:
        log("ws "+traceback.format_exc())

    # Persist note: store flag in runtime module so slate tick also uses PC path
    import shop_interact_runtime as sir
    sir._SHOP_PC_CLASS = [DE_ShopPC.static_class()]
    log("runtime still tick="+str(sir._TICK_HANDLE[0]))
    log("DONE")
except Exception:
    log(traceback.format_exc())
flush()