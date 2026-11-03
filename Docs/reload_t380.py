# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys, traceback
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t380.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T380RL: "+str(m))
    except Exception: print(m)

# Rebuild nav on current + both dungeon maps
def rebuild_nav_world(world, label):
    L("rebuild "+label+" world="+str(world))
    if world is None:
        return
    try:
        unreal.SystemLibrary.execute_console_command(world, "RebuildNavigation")
        L("console RebuildNavigation ok")
    except Exception as e:
        L("console RebuildNavigation ERR "+str(e))
    try:
        nav = unreal.NavigationSystemV1.get_navigation_system(world)
        L("nav="+str(nav)+" dir="+str([x for x in dir(nav) if "build" in x.lower() or "nav" in x.lower()][:40]))
        if nav:
            for meth in ("build", "rebuild_all", "simple_build", "execute_navigation_update"):
                if hasattr(nav, meth):
                    try:
                        getattr(nav, meth)()
                        L("nav.%s ok"%meth)
                    except Exception as e:
                        L("nav.%s ERR %s"%(meth,e))
    except Exception as e:
        L("navsys ERR "+str(e))

for mp in ("/Game/Maps/Dungeon/Map_Dungeon1","/Game/Maps/Dungeon/Map_Dungeon2"):
    try:
        unreal.EditorLevelLibrary.load_level(mp)
        w=unreal.EditorLevelLibrary.get_editor_world()
        # ensure volume exists
        vols=[]
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            try:
                if a.get_class().get_name()=="NavMeshBoundsVolume":
                    vols.append(a)
            except Exception:
                pass
        L("%s vols=%d"%(mp,len(vols)))
        if not vols:
            v=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(0,0,100), unreal.Rotator())
            try:
                root=v.get_editor_property("root_component")
                root.set_editor_property("relative_scale3d", unreal.Vector(80.0,80.0,30.0))
            except Exception as e:
                L("scale ERR "+str(e))
            L("spawned vol "+str(v))
        rebuild_nav_world(w, mp)
        try:
            unreal.EditorLevelLibrary.save_current_level()
            L("saved "+mp)
        except Exception as e:
            L("save ERR "+str(e))
    except Exception as e:
        L("map ERR "+mp+" "+traceback.format_exc())

# Reload python modules
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
for name in ("skeleton_engine_ai","shop_interact_runtime"):
    try:
        if name in sys.modules:
            importlib.reload(sys.modules[name]); L("reloaded "+name)
        else:
            __import__(name); L("imported "+name)
    except Exception as e:
        L("load ERR "+name+" "+traceback.format_exc())

m=sys.modules.get("shop_interact_runtime")
L("has update_skeleton_ai=%s"%hasattr(m,"update_skeleton_ai"))
L("has _damage_player=%s"%hasattr(m,"_damage_player"))
L("has _clear_skeleton_ai=%s"%hasattr(m,"_clear_skeleton_ai"))
L("has T380 tag=%s"%("T380_REMOVE_PY_AI" in open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py",encoding="utf-8").read()))
sk=sys.modules.get("skeleton_engine_ai")
L("skai tick=%s"%hasattr(sk,"tick_skeleton_engine_ai"))
L("skai AGGRO=%s"%getattr(sk,"AGGRO_RANGE",None))
L("skai SPEED=%s"%getattr(sk,"CHASE_SPEED",None))
L("skai DMG=%s"%getattr(sk,"ATTACK_DAMAGE",None))

# bootstrap
try:
    if m and hasattr(m,"bootstrap"):
        m.bootstrap(); L("bootstrap ok")
except Exception as e:
    L("bootstrap ERR "+str(e))

# verify BP movement props
bp_cls=unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton")
L("bp_cls="+str(bp_cls))
if bp_cls:
    cdo=unreal.get_default_object(bp_cls)
    mov=cdo.get_editor_property("character_movement")
    L("ortm=%s speed=%s"%(mov.get_editor_property("orient_rotation_to_movement"), mov.get_editor_property("max_walk_speed")))
    mesh=cdo.get_editor_property("mesh")
    try: L("anim_class=%s mode=%s"%(mesh.get_editor_property("anim_class"), mesh.get_editor_property("animation_mode")))
    except Exception as e: L("anim read "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
