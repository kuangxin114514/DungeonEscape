# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t380_skel.txt"
lines=[]
def L(m):
    lines.append(str(m)); 
    try: unreal.log("T380P: "+str(m))
    except Exception: print(m)

BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
L("exists="+str(unreal.EditorAssetLibrary.does_asset_exist(BP)))
bp=unreal.EditorAssetLibrary.load_asset(BP)
L("bp="+str(bp)+" cls="+str(bp.get_class().get_name() if bp else None))
bcls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
L("bcls="+str(bcls))
if bcls:
    cdo=unreal.get_default_object(bcls)
    L("cdo="+str(cdo))
    for prop in ("ai_controller_class","AIControllerClass","auto_possess_ai","AutoPossessAI","character_movement","mesh"):
        try:
            L("prop %s=%s"%(prop, cdo.get_editor_property(prop)))
        except Exception as e:
            L("prop %s ERR %s"%(prop,e))
    try:
        mesh=cdo.get_editor_property("mesh")
        L("mesh="+str(mesh))
        L("anim_mode="+str(mesh.get_editor_property("animation_mode")))
        try: L("anim_class="+str(mesh.get_editor_property("anim_class")))
        except Exception as e: L("anim_class ERR "+str(e))
        try: L("skeletal_mesh="+str(mesh.get_editor_property("skeletal_mesh")))
        except Exception as e: L("skelmesh ERR "+str(e))
        try:
            r=mesh.get_editor_property("relative_rotation")
            L("mesh_rel_rot pitch=%.1f yaw=%.1f roll=%.1f"%(r.pitch,r.yaw,r.roll))
        except Exception as e: L("relrot ERR "+str(e))
    except Exception as e:
        L("mesh block "+str(e))
    try:
        mov=cdo.get_editor_property("character_movement")
        for p in ("orient_rotation_to_movement","max_walk_speed","rotation_rate","use_controller_desired_rotation","bOrientRotationToMovement","MaxWalkSpeed"):
            try: L("mov.%s=%s"%(p, mov.get_editor_property(p)))
            except Exception as e: L("mov.%s ERR %s"%(p,e))
    except Exception as e:
        L("mov ERR "+str(e))

# maps nav
for mp in ("/Game/Maps/Dungeon/Map_Dungeon1","/Game/Maps/Dungeon/Map_Dungeon2","/Game/Maps/Map_Dungeon1","/Game/Maps/Map_Dungeon2"):
    L("map %s exist=%s"%(mp, unreal.EditorAssetLibrary.does_asset_exist(mp)))

# find dungeon maps
asset_reg=unreal.AssetRegistryHelpers.get_asset_registry()
for a in asset_reg.get_assets_by_path("/Game/Maps", recursive=True):
    n=str(a.asset_name)
    if "ungeon" in n or "Dungeon" in n or "Hub" in n:
        L("mapasset %s / %s"%(a.package_name, a.asset_name))

# anims
for p in [
 "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Idle_Rig",
 "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig",
 "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_1H_Melee_Attack_Chop_Rig",
]:
    L("anim %s exist=%s"%(p, unreal.EditorAssetLibrary.does_asset_exist(p)))

# Mannequin animbp for duplicate?
for p in ["/Game/Mannequin/Animations/ThirdPerson_AnimBP","/Game/Characters/Mannequin/Animations/ThirdPerson_AnimBP"]:
    L("tp_abp %s=%s"%(p, unreal.EditorAssetLibrary.does_asset_exist(p)))

# AI helpers
for name in ("AIBlueprintHelperLibrary","NavigationSystemV1","PawnSensingComponent","AIController"):
    try:
        c=getattr(unreal, name, None)
        L("unreal.%s=%s"%(name,c))
    except Exception as e:
        L("unreal.%s ERR %s"%(name,e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
