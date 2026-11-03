# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t425.txt"
lines=[]
def w(s):
    lines.append(str(s))
try:
    world=unreal.EditorLevelLibrary.get_editor_world()
except Exception:
    world=None
w("editor_world=%s"%world)
# PIE worlds
try:
    worlds=unreal.EditorLevelLibrary.get_pie_worlds(False)
    w("pie_count=%s"%len(worlds))
    for pw in worlds:
        w("pie path=%s name=%s"%(pw.get_path_name(), pw.get_name()))
        try:
            w("  level_name=%s"%unreal.GameplayStatics.get_current_level_name(pw, True))
        except Exception as e:
            w("  level_name_err=%s"%e)
        try:
            w("  map=%s"%unreal.SystemLibrary.get_object_name(pw))
        except Exception as e:
            w("  map_err=%s"%e)
        pc=unreal.GameplayStatics.get_player_controller(pw,0)
        pawn=pc.get_controlled_pawn() if pc else None
        w("  pawn=%s"%pawn)
        if pawn:
            loc=pawn.get_actor_location()
            w("  pawn_loc=%s"%loc)
            # nearby markers
            actors=unreal.GameplayStatics.get_all_actors_of_class(pw, unreal.Actor)
            near=[]
            for a in actors:
                try:
                    d=(a.get_actor_location()-loc).size()
                except Exception:
                    continue
                if d>600: continue
                lab=str(a.get_actor_label()) if hasattr(a,'get_actor_label') else str(a.get_name())
                tags=[str(t) for t in list(a.tags)] if hasattr(a,'tags') else []
                name=str(a.get_name())
                blob="|".join([lab,name]+tags)
                keys=("HubReturn","DungeonExit","Gate","Dungeon","Shop","Stairs","ToDungeon")
                if any(k in blob for k in keys) or d<350:
                    near.append((d,lab,name,tags))
            near.sort()
            for item in near[:40]:
                w("  near d=%.0f lab=%s name=%s tags=%s"%item)
except Exception as e:
    w("pie_err=%s"%e)
open(OUT,"w",encoding="utf-8").write("\n".join(lines))
print("wrote", len(lines))