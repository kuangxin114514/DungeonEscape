# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\setup_t350_dual.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T350: "+str(m))
    except Exception: print(m)

SRC="/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1"
SHIELD_SRC="/Game/Characters/Player/KayKit/BP_KayKitKnight_Shield1"
DST_PATH="/Game/Characters/Player/KayKit"
DST_NAME="BP_KayKitKnight_Sword1Shield1"
DST=DST_PATH+"/"+DST_NAME

def _get_scs(bp):
    scs=None
    try: scs=bp.get_editor_property("simple_construction_script")
    except Exception: pass
    try:
        if scs is None: scs=bp.simple_construction_script
    except Exception: pass
    return scs

def _walk_nodes(scs):
    nodes=[]
    if scs is None: return nodes
    try: nodes=list(scs.get_all_nodes())
    except Exception as e: L("nodes "+str(e))
    return nodes

def _varname(n):
    try: return str(n.get_variable_name())
    except Exception:
        try: return str(n.get_editor_property("internal_variable_name"))
        except Exception: return ""

def _tmpl(n):
    for getter in (lambda: n.component_template, lambda: n.get_editor_property("component_template")):
        try:
            t=getter()
        except Exception:
            t=None
        if t is not None: return t
    return None

def _is_shield_name(varname):
    low=(varname or "").lower()
    return ("shield" in low) or (varname in ("StaticMesh1","StaticMesh1_GEN_VARIABLE")) or low.endswith("staticmesh1")

def _read_shield_props(bp_path):
    """Return (mesh, loc, rot, scale) from Shield1 GEN_VARIABLE / SCS."""
    bp=unreal.load_asset(bp_path)
    L("shield_src=%s"%bp)
    if bp is None: return None
    found=None
    # Prefer GEN_VARIABLE StaticMeshComponent
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try: pn=o.get_path_name()
        except Exception: continue
        if "BP_KayKitKnight_Shield1" not in pn or "GEN_VARIABLE" not in pn: continue
        # exact Shield1, not dual
        if "Sword1Shield1" in pn: continue
        nm=o.get_name()
        try: sm=o.get_editor_property("static_mesh")
        except Exception: sm=None
        sname=sm.get_name() if sm else ""
        if ("StaticMesh1" in nm) or ("Shield" in sname) or ("Shield" in nm):
            try:
                loc=o.get_editor_property("relative_location")
                rot=o.get_editor_property("relative_rotation")
                sc=o.get_editor_property("relative_scale3d")
            except Exception as e:
                L("read gen xform "+str(e)); continue
            found=(sm, loc, rot, sc)
            L("read GEN %s mesh=%s loc=%s rot=%s sc=%s"%(nm, sname, loc, rot, sc))
            break
    if found is not None:
        return found
    # Fallback SCS
    scs=_get_scs(bp)
    for n in _walk_nodes(scs):
        stack=[n]
        while stack:
            cur=stack.pop(0)
            vn=_varname(cur)
            if _is_shield_name(vn):
                t=_tmpl(cur)
                if t is not None:
                    try:
                        sm=t.get_editor_property("static_mesh")
                        loc=t.get_editor_property("relative_location")
                        rot=t.get_editor_property("relative_rotation")
                        sc=t.get_editor_property("relative_scale3d")
                        found=(sm, loc, rot, sc)
                        L("read SCS '%s' mesh=%s"%(vn, sm.get_name() if sm else None))
                        return found
                    except Exception as e:
                        L("scs read "+str(e))
            kids=[]
            try: kids=list(cur.get_editor_property("child_nodes") or [])
            except Exception: pass
            stack.extend(kids)
    return found

try:
    src=unreal.load_asset(SRC)
    L("src_sword1=%s"%src)
    if src is None:
        raise RuntimeError("missing Sword1 BP")

    shield_props=_read_shield_props(SHIELD_SRC)
    if shield_props is None:
        raise RuntimeError("could not read Shield1 shield props")
    use_mesh, use_loc, use_rot, use_sc = shield_props
    L("use_mesh=%s"% (use_mesh.get_name() if use_mesh else None))

    bp=unreal.load_asset(DST)
    if bp is None:
        tools=unreal.AssetToolsHelpers.get_asset_tools()
        bp=tools.duplicate_asset(DST_NAME, DST_PATH, src)
        L("duplicated=%s"%bp)
    else:
        L("already=%s"%bp)
    if bp is None:
        raise RuntimeError("dual BP create failed")

    # Apply shield onto dual BP SCS
    scs=_get_scs(bp)
    nodes=_walk_nodes(scs)
    L("nodes=%d"%len(nodes))
    changed=0
    def walk(n, depth=0):
        global changed
        varname=_varname(n)
        L(("  "*depth)+"node '%s'"%varname)
        tmpl=_tmpl(n)
        if _is_shield_name(varname) and tmpl is not None:
            try:
                if use_mesh is not None:
                    tmpl.set_editor_property("static_mesh", use_mesh)
                tmpl.set_editor_property("relative_location", use_loc)
                tmpl.set_editor_property("relative_rotation", use_rot)
                tmpl.set_editor_property("relative_scale3d", use_sc)
                changed+=1
                L("  shield SCS OK -> %s"% (use_mesh.get_name() if use_mesh else None))
            except Exception as e:
                L("  scs set "+str(e))
        kids=[]
        try: kids=list(n.get_editor_property("child_nodes") or [])
        except Exception: pass
        for k in kids: walk(k, depth+1)
    for n in nodes: walk(n)
    L("scs_changed=%d"%changed)

    # Stamp GEN_VARIABLE on dual BP
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try: pn=o.get_path_name()
        except Exception: continue
        if "BP_KayKitKnight_Sword1Shield1" not in pn or "GEN_VARIABLE" not in pn: continue
        nm=o.get_name()
        try: sm=o.get_editor_property("static_mesh")
        except Exception: sm=None
        sname=sm.get_name() if sm else ""
        if ("StaticMesh1" in nm) or ("Shield" in sname) or ("Shield" in nm):
            try:
                if use_mesh is not None:
                    o.set_editor_property("static_mesh", use_mesh)
                o.set_editor_property("relative_location", use_loc)
                o.set_editor_property("relative_rotation", use_rot)
                o.set_editor_property("relative_scale3d", use_sc)
                L("GEN shield set %s -> %s"%(nm, use_mesh.get_name() if use_mesh else None))
                changed+=1
            except Exception as e:
                L("GEN set fail "+str(e))

    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        L("compiled")
    except Exception as e:
        L("compile "+str(e))
    try:
        unreal.EditorAssetLibrary.save_asset(DST); L("save OK")
    except Exception as e:
        L("save "+str(e))
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(bp); L("save_loaded OK")
        except Exception as e2:
            L("save_loaded "+str(e2))

    # Verify both sword + shield GEN meshes
    sword_ok=None; shield_ok=None
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try: pn=o.get_path_name()
        except Exception: continue
        if "BP_KayKitKnight_Sword1Shield1" not in pn or "GEN_VARIABLE" not in pn: continue
        nm=o.get_name()
        try: sm=o.get_editor_property("static_mesh")
        except Exception: sm=None
        sname=sm.get_name() if sm else ""
        L("VERIFY %s mesh=%s"%(nm, sname))
        if ("StaticMesh1" in nm) or ("Shield" in sname):
            shield_ok=sname
        elif ("Sword" in sname) or (nm == "StaticMesh" or nm.startswith("StaticMesh_GEN")):
            sword_ok=sname
    L("VERIFY_SWORD=%s"%sword_ok)
    L("VERIFY_SHIELD=%s"%shield_ok)
except Exception as e:
    L("ERR "+str(e))
    L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
