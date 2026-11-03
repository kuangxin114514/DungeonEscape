# -*- coding: utf-8 -*-
import unreal

# List reload-related
names = [n for n in dir(unreal) if "reload" in n.lower() or "Unload" in n or "unload" in n or "Package" in n]
unreal.log("API {}".format(names[:40]))

# Try EditorLoadingAndSavingUtils
els = unreal.EditorLoadingAndSavingUtils
unreal.log("ELS {}".format([n for n in dir(els) if not n.startswith("_")]))

# Try PackageTools
try:
    pt = unreal.PackageTools
    unreal.log("PT {}".format([n for n in dir(pt) if not n.startswith("_")][:30]))
except Exception as e:
    unreal.log("PT ERR {}".format(e))

# Try AssetTools force reload
try:
    at = unreal.AssetToolsHelpers.get_asset_tools()
    unreal.log("AT {}".format([n for n in dir(at) if "reload" in n.lower() or "load" in n.lower()][:20]))
except Exception as e:
    unreal.log("AT ERR {}".format(e))

# SoftObjectPath / load_object force
bs_path = "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
# try unreal.reload
if hasattr(unreal, "reload"):
    unreal.log("has unreal.reload")

# Try closing asset then reimport from disk via load_package with LOAD_Reload flag
# ELoadFlags: LOAD_None=0, LOAD_Async=1, LOAD_NoWarn=2, LOAD_Verify=8, LOAD_AllowDll=16, LOAD_NoVerify=32, LOAD_Quiet=64, LOAD_FindIfFail=128, LOAD_MemoryReader=256, LOAD_NoRedirects=512, LOAD_ForVerify=1024, LOAD_DisableDotNetCheck=2048, LOAD_DisableEngineVersionCheck=4096, LOAD_IsVerifying=8192
# Actually FLoadPackage might use LOAD_Reload = 0x00080000?
try:
    # Unreal Python: load_package(outer, name, load_flags)
    # Flag 0x80000 = LOAD_Reload in some versions
    for flag in [0, 0x10, 0x80000, 0x100000]:
        try:
            pkg = unreal.load_package(None, bs_path, flag)
            unreal.log("load_package flag={} -> {}".format(hex(flag), pkg))
        except Exception as e:
            unreal.log("load_package flag={} ERR {}".format(hex(flag), e))
except Exception as e:
    unreal.log("outer ERR {}".format(e))

# Inspect BlendSpace for any settable skeleton via reflection
bs = unreal.EditorAssetLibrary.load_asset(bs_path)
# Try get_editor_property on all
props = []
for name in ["skeleton", "Skeleton", "preview_base_pose", "preview_pose_asset", "target_skeleton"]:
    try:
        v = bs.get_editor_property(name)
        props.append("{}={}".format(name, v))
    except Exception as e:
        props.append("{} ERR".format(name))
unreal.log("props {}".format(props))

# Can we duplicate BS onto a brand-new asset that somehow gets KayKit skeleton?
# Idea: create BlendSpace1D via factory with dialog is None; 
# Alternative: use AnimSequence.skeleton - set samples' skeleton? No.

# Check if BlendSample has skeleton override
sd = bs.get_editor_property("sample_data")
if len(sd)>0:
    s0 = sd[0]
    unreal.log("sample0 fields {}".format([n for n in dir(s0) if not n.startswith("_")][:40]))

unreal.log("PROBE_RELOAD_DONE")