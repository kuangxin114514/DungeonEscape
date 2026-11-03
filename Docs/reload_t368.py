# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t368.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T368RL: "+str(m))
    except Exception: print(m)
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
if "shop_interact_runtime" in sys.modules:
    m=importlib.reload(sys.modules["shop_interact_runtime"]); L("reloaded")
else:
    import shop_interact_runtime as m; L("imported")
# Verify T368 symbols
for name in ("update_skeleton_ai","_has_line_of_sight","_damage_player","SKELETON_ATTACK_DAMAGE","SKELETON_AGGRO_RANGE","_clear_skeleton_ai"):
    L("%s=%s" % (name, hasattr(m, name)))
L("AGGRO=%.0f ATTACK_RANGE=%.0f DMG=%.0f CD=%.2f" % (
    float(getattr(m,"SKELETON_AGGRO_RANGE",-1)),
    float(getattr(m,"SKELETON_ATTACK_RANGE",-1)),
    float(getattr(m,"SKELETON_ATTACK_DAMAGE",-1)),
    float(getattr(m,"SKELETON_ATTACK_COOLDOWN",-1)),
))
# Anim loads
for kind in ("idle","run","attack"):
    try:
        seq=m._load_skeleton_anim(kind)
        L("anim_%s=%s" % (kind, seq.get_name() if seq else None))
    except Exception as e:
        L("anim_%s ERR %s" % (kind, e))
# LOS smoke (only if PIE)
world=None
try: world=m._pie_world()
except Exception: world=None
L("pie_world=%s" % world)
if world:
    try:
        pc=unreal.GameplayStatics.get_player_controller(world,0)
        pawn=pc.get_controlled_pawn() if pc else None
        enemies=m._list_live_enemy_actors(world)
        L("enemies=%d pawn=%s" % (len(enemies), pawn.get_name() if pawn else None))
        if pawn and enemies:
            e0=enemies[0]
            d=m._dist(pawn.get_actor_location(), e0.get_actor_location())
            los=m._has_line_of_sight(world, e0, pawn)
            L("sample dist=%.1f los=%s" % (d, los))
    except Exception as e:
        L("pie sample "+str(e))
fn=getattr(m,"bootstrap",None)
if callable(fn):
    try: fn(); L("bootstrap ok")
    except Exception as e: L("bootstrap ERR "+str(e))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
