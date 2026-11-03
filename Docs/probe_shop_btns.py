# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_shop_btns.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("ProbeBtn: "+str(m))
    except Exception: print(m)

def text_of(tb):
    for g in ("get_text",):
        try:
            return str(getattr(tb,g)())
        except Exception:
            pass
    for p in ("text","Text"):
        try: return str(tb.get_editor_property(p))
        except Exception: pass
    return "?"

# Inspect template widget tree buttons via ObjectIterator on asset CDO-ish objects
for o in unreal.ObjectIterator(unreal.Button):
    try: pn=o.get_path_name()
    except Exception: continue
    if "WBP_Shop_Weapon.WBP_Shop_Weapon:WidgetTree." not in pn:
        continue
    L("BUTTON "+o.get_name()+" path="+pn)
    # children
    try:
        n=o.get_children_count()
    except Exception:
        n=-1
    L("  children="+str(n))
    if n and n>0:
        for i in range(n):
            try:
                ch=o.get_child_at(i)
                L("  child%d %s %s"%(i, ch.get_class().get_name(), ch.get_name()))
                if "Text" in ch.get_class().get_name():
                    L("   text="+text_of(ch))
            except Exception as e:
                L("  childerr "+str(e))
    # content slot widget
    try:
        slot=o.get_content_slot() if hasattr(o,"get_content_slot") else None
        L("  content_slot="+str(slot))
    except Exception as e:
        L("  contentslot "+str(e))
    try:
        # Button has set_content / get content via widget tree parent
        content = None
        for prop in ("content","Content"):
            try:
                content=o.get_editor_property(prop)
                break
            except Exception:
                pass
        L("  content="+str(content))
        if content and "Text" in content.get_class().get_name():
            L("  content_text="+text_of(content))
    except Exception as e:
        L("  contenterr "+str(e))

# All textblocks on asset
for o in unreal.ObjectIterator(unreal.TextBlock):
    try: pn=o.get_path_name()
    except Exception: continue
    if "WBP_Shop_Weapon.WBP_Shop_Weapon:WidgetTree." not in pn:
        continue
    L("TB "+o.get_name()+" = "+text_of(o))

# Runtime pawn sword comps if PIE
world=None
try:
    world=unreal.EditorLevelLibrary.get_editor_world()
except Exception:
    pass
pc=None
if world:
    try: pc=unreal.GameplayStatics.get_player_controller(world,0)
    except Exception: pass
pawn=None
if pc:
    try: pawn=pc.get_controlled_pawn()
    except Exception: pass
L("pawn="+str(pawn))
if pawn:
    try:
        comps=pawn.get_components_by_class(unreal.StaticMeshComponent.static_class())
    except Exception:
        comps=[]
    for c in comps:
        try:
            sm=c.get_editor_property("static_mesh")
        except Exception:
            sm=None
        try:
            mesh=c.static_mesh
        except Exception:
            mesh=sm
        L("SMC name=%s mesh=%s attach=%s"%(c.get_name(), mesh, getattr(c,"attach_parent",None)))
        try:
            L("  scale="+str(c.get_relative_scale3d())+" loc="+str(c.relative_location))
        except Exception:
            pass

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
