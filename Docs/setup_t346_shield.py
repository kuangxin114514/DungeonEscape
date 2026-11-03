# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\setup_t346_shield.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T346S: "+str(m))
    except Exception: print(m)

SRC="/Game/Characters/Player/KayKit/BP_KayKitKnight"
DST_PATH="/Game/Characters/Player/KayKit"
DST_NAME="BP_KayKitKnight_Shield1"
DST=DST_PATH+"/"+DST_NAME
SHIELD_MESH="/Game/Characters/Player/KayKit/Mesh/Round_Shield"
# also keep a Weapons alias if possible
SHIELD_ALIAS_PATH="/Game/Characters/Player/KayKit/Weapons"
SHIELD_ALIAS_NAME="SM_KayKitShield_Round"

try:
    src=unreal.load_asset(SRC)
    L("src=%s"%src)
    mesh=unreal.load_asset(SHIELD_MESH)
    L("mesh=%s"%mesh)
    alias=unreal.load_asset(SHIELD_ALIAS_PATH+"/"+SHIELD_ALIAS_NAME)
    if alias is None and mesh is not None:
        try:
            tools=unreal.AssetToolsHelpers.get_asset_tools()
            alias=tools.duplicate_asset(SHIELD_ALIAS_NAME, SHIELD_ALIAS_PATH, mesh)
            L("alias_dup=%s"%alias)
            try: unreal.EditorAssetLibrary.save_asset(SHIELD_ALIAS_PATH+"/"+SHIELD_ALIAS_NAME)
            except Exception as e: L("alias_save "+str(e))
        except Exception as e:
            L("alias_dup_fail "+str(e)); alias=None
    else:
        L("alias=%s"%alias)
    use_mesh = alias if alias is not None else mesh

    bp=unreal.load_asset(DST)
    if bp is None:
        tools=unreal.AssetToolsHelpers.get_asset_tools()
        bp=tools.duplicate_asset(DST_NAME, DST_PATH, src)
        L("duplicated=%s"%bp)
    else:
        L("already=%s"%bp)

    # set shield component mesh on SCS (StaticMesh1 / Shield)
    scs=None
    try: scs=bp.get_editor_property("simple_construction_script")
    except Exception: pass
    try:
        if scs is None: scs=bp.simple_construction_script
    except Exception: pass
    nodes=[]
    if scs is not None:
        try: nodes=list(scs.get_all_nodes())
        except Exception as e: L("nodes "+str(e))
    L("nodes=%d"%len(nodes))
    changed=0
    def walk(n, depth=0):
        global changed
        varname=""
        try: varname=str(n.get_variable_name())
        except Exception:
            try: varname=str(n.get_editor_property("internal_variable_name"))
            except Exception: varname=""
        L(("  "*depth)+"node '%s'"%varname)
        low=varname.lower()
        is_shield=("shield" in low) or (varname in ("StaticMesh1","StaticMesh1_GEN_VARIABLE")) or low.endswith("staticmesh1")
        tmpl=None
        for getter in (lambda: n.component_template, lambda: n.get_editor_property("component_template")):
            try:
                tmpl=getter()
            except Exception:
                tmpl=None
            if tmpl is not None: break
        if is_shield and tmpl is not None and use_mesh is not None:
            try:
                tmpl.set_editor_property("static_mesh", use_mesh)
                changed+=1
                L("  shield mesh OK -> %s"%use_mesh.get_name())
            except Exception as e:
                L("  mesh "+str(e))
            # keep existing relative transform; Round_Shield may need scale tweak later by user
        kids=[]
        try: kids=list(n.get_editor_property("child_nodes") or [])
        except Exception: pass
        for k in kids: walk(k, depth+1)
    for n in nodes: walk(n)
    L("changed=%d"%changed)

    # Also stamp GEN_VARIABLE directly if present
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try: pn=o.get_path_name()
        except Exception: continue
        if "BP_KayKitKnight_Shield1" not in pn or "GEN_VARIABLE" not in pn: continue
        nm=o.get_name()
        try: sm=o.get_editor_property("static_mesh")
        except Exception: sm=None
        sname=sm.get_name() if sm else ""
        if ("StaticMesh1" in nm) or ("Shield" in sname) or ("Shield" in nm):
            try:
                o.set_editor_property("static_mesh", use_mesh)
                L("GEN set %s -> %s"%(nm, use_mesh.get_name() if use_mesh else None))
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

    # --- Armor shop: ensure Button_0 exists ---
    abp=unreal.load_asset("/Game/UI/Shop/WBP_Shop_Armor")
    L("armor_bp=%s"%abp)
    tree=None
    for getter in (
        lambda: abp.get_editor_property("widget_tree"),
        lambda: abp.get_editor_property("WidgetTree"),
        lambda: unreal.load_object(None, "/Game/UI/Shop/WBP_Shop_Armor.WBP_Shop_Armor:WidgetTree"),
    ):
        try:
            tree=getter()
        except Exception:
            tree=None
        if tree is not None: break
    L("tree=%s"%tree)
    # detect existing button
    has_btn=False
    for o in unreal.ObjectIterator(unreal.Button):
        try: pn=o.get_path_name()
        except Exception: continue
        if "/Game/UI/Shop/WBP_Shop_Armor.WBP_Shop_Armor:WidgetTree" in pn:
            has_btn=True; L("existing btn "+pn)
    if tree is not None and not has_btn:
        canvas=None
        try: canvas=tree.root_widget
        except Exception: pass
        try:
            if canvas is None: canvas=tree.get_editor_property("root_widget")
        except Exception: pass
        L("canvas=%s"%canvas)
        btn=None
        try:
            btn=tree.construct_widget(unreal.Button, "Button_0")
            L("btn=%s"%btn)
        except Exception as e:
            L("construct btn "+str(e))
        txt=None
        try:
            txt=tree.construct_widget(unreal.TextBlock, "Txt_BuyShield1")
            if txt is not None:
                try: txt.set_text(u"购买盾1 (5金币)")
                except Exception:
                    try: txt.set_editor_property("text", unreal.Text(u"购买盾1 (5金币)"))
                    except Exception as e: L("set text "+str(e))
                L("txt=%s"%txt)
        except Exception as e:
            L("construct txt "+str(e))
        if btn is not None and txt is not None:
            try:
                btn.set_content(txt); L("btn set_content OK")
            except Exception as e:
                L("set_content "+str(e))
                try:
                    btn.add_child(txt); L("btn add_child OK")
                except Exception as e2:
                    L("add_child "+str(e2))
        if btn is not None and canvas is not None:
            try:
                slot=canvas.add_child_to_canvas(btn)
                L("slot=%s"%slot)
                if slot is not None:
                    try: slot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(0.5,0.5), maximum=unreal.Vector2D(0.5,0.5)))
                    except Exception as e: L("anchors "+str(e))
                    try: slot.set_alignment(unreal.Vector2D(0.5,0.5))
                    except Exception as e: L("align "+str(e))
                    try: slot.set_position(unreal.Vector2D(0.0, 40.0))
                    except Exception as e: L("pos "+str(e))
                    try: slot.set_size(unreal.Vector2D(280.0, 56.0))
                    except Exception as e: L("size "+str(e))
                    try: slot.set_auto_size(False)
                    except Exception: pass
            except Exception as e:
                L("add_to_canvas "+str(e)+traceback.format_exc())
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(abp); L("armor compiled")
        except Exception as e: L("armor compile "+str(e))
        try:
            unreal.EditorAssetLibrary.save_asset("/Game/UI/Shop/WBP_Shop_Armor"); L("armor saved")
        except Exception as e:
            L("armor save "+str(e))
            try: unreal.EditorAssetLibrary.save_loaded_asset(abp); L("armor save_loaded")
            except Exception as e2: L("armor save_loaded "+str(e2))
    # verify
    for o in unreal.ObjectIterator(unreal.Button):
        try: pn=o.get_path_name()
        except Exception: continue
        if "WBP_Shop_Armor" in pn and "Transient" not in pn:
            L("VERIFY BTN "+pn)
except Exception as e:
    L("ERR "+str(e))
    L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
