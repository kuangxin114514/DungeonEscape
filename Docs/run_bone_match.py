import sys,time
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
code=r'''
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_bone_match.txt"
lines=[]
def L(m):
    lines.append(str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
try:
    sa=unreal.EditorAssetLibrary.load_asset("/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX")
    idle=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle")
    idle_rig=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
    bt=sa.get_editor_property("bone_tree")
    bones=[]
    for b in bt:
        try:
            bones.append(str(b.get_editor_property("name")))
        except Exception:
            try: bones.append(str(b.name))
            except Exception: bones.append(str(b))
    L("skel bones n=%d sample=%s"%(len(bones), bones[:8]))
    tracks=list(unreal.AnimationLibrary.get_animation_track_names(idle))
    track_names=[str(t) for t in tracks]
    L("idle tracks n=%d sample=%s"%(len(track_names), track_names[:8]))
    # match
    missing=[b for b in track_names if b not in bones]
    extra=[b for b in bones if b not in track_names]
    L("tracks not in skel=%s"%missing[:20])
    L("skel bones not in tracks count=%d sample=%s"%(len(extra), extra[:20]))
    # idle_rig tracks still exist even with null skel?
    try:
        tr2=list(unreal.AnimationLibrary.get_animation_track_names(idle_rig))
        L("idle_rig tracks n=%d skel=%s"%(len(tr2), idle_rig.get_editor_property("skeleton")))
    except Exception as e:
        L("idle_rig tracks ERR %s"%e)
    # Can we get a bone pose from idle?
    try:
        pose=unreal.AnimationLibrary.get_bone_pose_for_time(idle, "root", 0.0, True)
        L("idle root pose at 0=%s"%pose)
    except Exception as e:
        L("get_bone_pose ERR %s"%e)
        # try common bone names
        for bn in track_names[:5]:
            try:
                pose=unreal.AnimationLibrary.get_bone_pose_for_time(idle, bn, 0.0, True)
                L("pose %s=%s"%(bn,pose)); break
            except Exception as e2:
                L("pose %s ERR %s"%(bn,e2))
    # Mark BS dirty and save again; reload packages
    bs=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
    unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion", only_if_is_dirty=False)
    unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion", only_if_is_dirty=False)
    unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight", only_if_is_dirty=False)
    L("rescued saves done")
    flush()
except Exception as e:
    import traceback; L(traceback.format_exc()); flush()
'''
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_tmp_bone_match.py"
open(p,"w",encoding="utf-8").write(code)
remote=re.RemoteExecution(); remote.start()
try:
    for i in range(20):
        time.sleep(0.4)
        if remote.remote_nodes: break
    remote.open_command_connection(remote.remote_nodes[0]["node_id"])
    r=remote.run_command("exec(open(r'%s',encoding='utf-8').read())"%p.replace("\\","/"), unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success") if r else None)
    print("result", str(r.get("result"))[:1000] if r else None)
finally:
    remote.stop()