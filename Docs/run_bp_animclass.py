import sys,time
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
code=r'''
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_bp_animclass.txt"
lines=[]
def L(m):
    lines.append(str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
try:
    BP="/Game/Characters/Player/KayKit/BP_KayKitKnight"
    ABP="/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
    bp=unreal.EditorAssetLibrary.load_asset(BP)
    abp_c=unreal.EditorAssetLibrary.load_blueprint_class(ABP)
    bp_c=unreal.EditorAssetLibrary.load_blueprint_class(BP)
    L("bp=%s"%bp)
    L("bp_c=%s"%bp_c)
    L("abp_c=%s"%abp_c)
    if bp_c:
        cdo=unreal.get_default_object(bp_c)
        m=cdo.get_editor_property("mesh")
        L("mesh=%s"%m)
        L("anim_mode=%s"%m.get_editor_property("animation_mode"))
        L("anim_class=%s"%m.get_editor_property("anim_class"))
        L("skel_mesh=%s"%m.get_editor_property("skeletal_mesh"))
        # ensure correct
        changed=False
        if m.get_editor_property("anim_class") != abp_c:
            m.set_editor_property("anim_class", abp_c)
            L("SET anim_class -> ABP_KayKitLocomotion_C")
            changed=True
        want=unreal.AnimationMode.ANIMATION_BLUEPRINT
        if m.get_editor_property("animation_mode") != want:
            m.set_editor_property("animation_mode", want)
            L("SET animation_mode BLUEPRINT")
            changed=True
        cmc=cdo.get_editor_property("character_movement")
        L("max_walk_speed=%s"%cmc.get_editor_property("max_walk_speed"))
        if changed:
            unreal.EditorAssetLibrary.save_loaded_asset(bp)
            L("saved BP")
        L("FINAL anim_class=%s"%m.get_editor_property("anim_class"))
        L("FINAL anim_mode=%s"%m.get_editor_property("animation_mode"))
    # ABP CDO IsInAir variants
    if abp_c:
        acdo=unreal.get_default_object(abp_c)
        for v in ["Speed","IsInAir","bIsInAir","is_in_air","IsFalling","AirSpeed"]:
            try:
                L("abp.%s=%s"%(v, acdo.get_editor_property(v)))
            except Exception as e:
                L("abp.%s ERR"%v)
    # GM_Hub default pawn
    gm=unreal.EditorAssetLibrary.load_asset("/Game/Core/GameFlow/GM_Hub")
    gmc=unreal.EditorAssetLibrary.load_blueprint_class("/Game/Core/GameFlow/GM_Hub")
    L("gm=%s gmc=%s"%(gm,gmc))
    if gmc:
        gcdo=unreal.get_default_object(gmc)
        try:
            L("default_pawn_class=%s"%gcdo.get_editor_property("default_pawn_class"))
        except Exception as e:
            L("dpc ERR %s"%e)
    # Confirm BS samples still good after reload
    bs=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
    for i,s in enumerate(list(bs.get_editor_property("sample_data"))):
        anim=s.get_editor_property("animation")
        sk=anim.get_editor_property("skeleton") if anim else None
        L("BS[%d] %s skel=%s val=%s"%(i, anim.get_name() if anim else None, sk.get_name() if sk else None, s.get_editor_property("sample_value")))
    flush()
except Exception as e:
    L("ERR "+repr(e))
    flush()
'''
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_tmp_bp_animclass.py"
open(p,"w",encoding="utf-8").write(code)
remote=re.RemoteExecution(); remote.start()
try:
    for i in range(20):
        time.sleep(0.4)
        if remote.remote_nodes: break
    remote.open_command_connection(remote.remote_nodes[0]["node_id"])
    r=remote.run_command("exec(open(r'%s',encoding='utf-8').read())"%p.replace("\\","/"), unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success") if r else None)
    print("result", str(r.get("result"))[:800] if r else None)
finally:
    remote.stop()