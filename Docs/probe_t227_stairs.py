# -*- coding: utf-8 -*-
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t227_stairs.txt"
lines=[]
def L(m):
    lines.append(str(m)); unreal.log("P227s: "+str(m))

unreal.EditorLoadingAndSavingUtils.load_map("/Game/Maps/Dungeon/Map_Dungeon")
L("loaded dungeon")
# actors near user corridor wall (130,-840)
near=[]
all_labs=[]
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    try:
        lab = a.get_actor_label() or a.get_name() or ""
        loc = a.get_actor_location()
    except Exception:
        continue
    mesh_name=""
    try:
        smc=a.static_mesh_component
        if smc:
            sm=smc.get_editor_property("static_mesh")
            if sm: mesh_name=sm.get_name()
    except Exception:
        pass
    all_labs.append((lab, mesh_name, round(loc.x,1), round(loc.y,1), round(loc.z,1)))
    dx=loc.x-130; dy=loc.y-(-840); dz=loc.z
    d=(dx*dx+dy*dy)**0.5
    if d < 800:
        near.append((d, lab, mesh_name, loc.x, loc.y, loc.z))
near.sort()
L("NEAR count=%d" % len(near))
for t in near[:60]:
    L(" d=%.0f lab=%s mesh=%s loc=(%.1f,%.1f,%.1f)" % t)
# any stair-like anywhere
L("ALL stair-like:")
for lab,mesh,x,y,z in all_labs:
    key=(lab+" "+mesh).lower()
    if any(k in key for k in ("stair","step","ramp","ladder","exit","hubreturn","dungeonexit")):
        L("  %s / %s (%.1f,%.1f,%.1f)" % (lab,mesh,x,y,z))
L("actor_count=%d" % len(all_labs))
# ABP node classes
abp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion")
try:
    aes=unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    aes.open_editor_for_assets([abp])
except Exception as e:
    L("open abp "+str(e))
EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
classes={}
slotish=[]
for obj in unreal.ObjectIterator(EdGraphNode):
    pn=obj.get_path_name()
    if "ABP_KayKitLocomotion" not in pn: continue
    if "Default__" in pn or "AnimPreview" in pn: continue
    cn=obj.get_class().get_name()
    classes[cn]=classes.get(cn,0)+1
    if "slot" in cn.lower() or "Slot" in cn or "montage" in cn.lower():
        slotish.append(cn+":"+obj.get_name()+":"+pn[-80:])
L("ABP node classes="+str(sorted(classes.items())))
L("slotish="+str(slotish[:20]))
# ThirdPerson for comparison
classes2={}
slotish2=[]
for obj in unreal.ObjectIterator(EdGraphNode):
    pn=obj.get_path_name()
    if "ThirdPerson_AnimBP" not in pn: continue
    if "Default__" in pn or "AnimPreview" in pn: continue
    cn=obj.get_class().get_name()
    classes2[cn]=classes2.get(cn,0)+1
    if "slot" in cn.lower() or "Slot" in cn:
        slotish2.append(cn+":"+obj.get_name())
L("TP node classes="+str(sorted(classes2.items())))
L("TP slotish="+str(slotish2[:20]))
try:
    aes.close_all_editors_for_asset(abp)
except Exception:
    pass
# restore hub
unreal.EditorLoadingAndSavingUtils.load_map("/Game/Maps/Hub/Map_Hub")
L("hub restored")
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("DONE")