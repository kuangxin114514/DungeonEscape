# -*- coding: utf-8 -*-
import unreal, ctypes, re, traceback
from ctypes import c_void_p, c_int32, c_uint8, Structure, byref

LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/finish_drag_ready.log"
L = []
def log(m):
    s = str(m); L.append(s); print(s)

def ue_ptr(obj):
    for s in (repr(obj), str(obj)):
        m = re.search(r"\(0x([0-9A-Fa-f]+)\)", s)
        if m:
            return int(m.group(1), 16)
    # Fallback: ObjectIterator lookup by path
    try:
        pn = unreal.Object.get_path_name(obj)
    except Exception:
        pn = obj.get_path_name() if hasattr(obj, "get_path_name") else None
    if pn:
        for o in unreal.ObjectIterator(unreal.Object):
            try:
                if unreal.Object.get_path_name(o) == pn:
                    m = re.search(r"\(0x([0-9A-Fa-f]+)\)", repr(o))
                    if m:
                        return int(m.group(1), 16)
            except Exception:
                pass
    raise RuntimeError("no ptr in %r / %r" % (obj, pn if "pn" in dir() else None))

def as_uobject(obj):
    """Return an Object-wrapper with (0x..) in repr for the same path."""
    try:
        pn = unreal.Object.get_path_name(obj)
    except Exception:
        pn = obj.get_path_name()
    loaded = unreal.load_object(None, pn)
    if loaded is not None:
        return loaded
    for o in unreal.ObjectIterator(type(obj) if False else unreal.StaticMeshComponent):
        try:
            if unreal.Object.get_path_name(o) == pn:
                return o
        except Exception:
            pass
    return obj

class TArray(Structure):
    _fields_ = [("Data", c_void_p), ("ArrayNum", c_int32), ("ArrayMax", c_int32)]

UNREALED = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-UnrealEd.dll"
ENGINE = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Engine.dll"
unrealed = ctypes.CDLL(UNREALED)
engine = ctypes.CDLL(ENGINE)

AddCB = getattr(unrealed, "?AddComponentsToBlueprint@FKismetEditorUtilities@@SAXPEAVUBlueprint@@AEBV?$TArray@PEAVUActorComponent@@V?$TSizedDefaultAllocator@$0CA@@@@@_NPEAVUSCS_Node@@2@Z")
AddCB.argtypes = [c_void_p, c_void_p, c_uint8, c_void_p, c_uint8]
AddCB.restype = None

# Also try harvest-mode overload
AddCB2 = getattr(unrealed, "?AddComponentsToBlueprint@FKismetEditorUtilities@@SAXPEAVUBlueprint@@AEBV?$TArray@PEAVUActorComponent@@V?$TSizedDefaultAllocator@$0CA@@@@@W4EAddComponentToBPHarvestMode@1@PEAVUSCS_Node@@_N@Z")
AddCB2.argtypes = [c_void_p, c_void_p, c_uint8, c_void_p, c_uint8]
AddCB2.restype = None

CreateNodeAndRename = getattr(engine, "?CreateNodeAndRenameComponent@USimpleConstructionScript@@QEAAPEAVUSCS_Node@@PEAVUActorComponent@@@Z")
CreateNodeAndRename.argtypes = [c_void_p, c_void_p]
CreateNodeAndRename.restype = c_void_p

SetParent_SC = getattr(engine, "?SetParent@USCS_Node@@QEAAXPEBVUSceneComponent@@@Z")
SetParent_SC.argtypes = [c_void_p, c_void_p]
SetParent_SC.restype = None

AddNode = getattr(engine, "?AddNode@USimpleConstructionScript@@QEAAXPEAVUSCS_Node@@@Z")
AddNode.argtypes = [c_void_p, c_void_p]
AddNode.restype = None

BP_PATH = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
SWORD_PATH = "/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword"
SHIELD_PATH = "/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield"

bp = unreal.load_asset(BP_PATH)
sword_asset = unreal.load_asset(SWORD_PATH)
shield_asset = unreal.load_asset(SHIELD_PATH)
bp_cls = unreal.load_class(None, BP_PATH + ".BP_KayKitKnight_C")
scs = unreal.load_object(None, BP_PATH + ".BP_KayKitKnight_C:SimpleConstructionScript_0")
log("bp=%s scs=%s" % (bp, scs))

# Clean any leftover temp knights from prior runs
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    try:
        if a.get_class().get_name() == "BP_KayKitKnight_C" and a.get_actor_location().z < -1000:
            unreal.EditorLevelLibrary.destroy_actor(a)
            log("cleaned leftover %s" % a.get_name())
    except Exception:
        pass

loc = unreal.Vector(50, 50, -50000)
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(bp_cls, loc)
log("spawned=%s repr=%s" % (actor.get_name(), repr(actor)[:120]))
mesh = actor.get_components_by_class(unreal.SkeletalMeshComponent)[0]
log("mesh repr=%s" % repr(mesh)[:160])

def make_weapon(name, asset, socket):
    comp = unreal.new_object(unreal.StaticMeshComponent, actor, name)
    log("new_object %s raw=%r" % (name, comp))
    try:
        pn = unreal.Object.get_path_name(comp)
    except Exception:
        pn = None
        try: pn = comp.get_path_name()
        except Exception as e: log("path ERR %s" % e)
    log("path=%s" % pn)
    # Reload as UObject wrapper
    loaded = unreal.load_object(None, pn) if pn else None
    log("loaded=%r" % (loaded,))
    if loaded is None and pn:
        for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
            try:
                if unreal.Object.get_path_name(o) == pn:
                    loaded = o
                    break
            except Exception:
                pass
        log("iter loaded=%r" % (loaded,))
    use = loaded if loaded is not None else comp
    use.set_editor_property("static_mesh", asset)
    ok = use.attach_to_component(
        mesh,
        unreal.Name(socket),
        unreal.AttachmentRule.SNAP_TO_TARGET,
        unreal.AttachmentRule.SNAP_TO_TARGET,
        unreal.AttachmentRule.SNAP_TO_TARGET,
        False,
    )
    log("made %s ok=%s parent=%s sock=%s" % (
        name, ok,
        use.get_attach_parent().get_name() if use.get_attach_parent() else None,
        use.get_attach_socket_name()))
    log("use repr=%s" % repr(use)[:200])
    return use

sword = make_weapon("SwordMesh", sword_asset, "handslot_r")
shield = make_weapon("ShieldMesh", shield_asset, "handslot_l")

sp = ue_ptr(sword)
sh = ue_ptr(shield)
bp_ptr = ue_ptr(bp)
scs_ptr = ue_ptr(scs)
mesh_ptr = ue_ptr(mesh)
log("ptrs sword=0x%X shield=0x%X bp=0x%X scs=0x%X mesh=0x%X" % (sp, sh, bp_ptr, scs_ptr, mesh_ptr))

ptrs = (c_void_p * 2)(sp, sh)
arr = TArray(ctypes.cast(ptrs, c_void_p), 2, 2)

# Strategy 1: AddComponentsToBlueprint (bool overload)
try:
    AddCB(bp_ptr, byref(arr), 0, None, 0)
    log("AddCB bool OK")
except Exception as e:
    log("AddCB bool FAIL %s" % traceback.format_exc())

def dump_scs(tag):
    task = unreal.AssetExportTask()
    task.set_editor_property("object", scs)
    task.set_editor_property("filename", r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_%s.copy" % tag)
    task.set_editor_property("automated", True)
    task.set_editor_property("prompt", False)
    task.set_editor_property("exporter", unreal.ObjectExporterT3D())
    unreal.Exporter.run_asset_export_task(task)
    text = open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_%s.copy" % tag, encoding="utf-8", errors="ignore").read()
    for line in text.splitlines():
        if any(k in line for k in ("AllNodes", "RootNodes", "Sword", "Shield", "AttachTo", "InternalVariable", "ParentComponent", "StaticMesh=", "handslot")):
            log("[%s] %s" % (tag, line.strip()))
    return text

text = dump_scs("after_addcb")
all_has_sword = any(("AllNodes" in ln and "Sword" in ln) for ln in text.splitlines())
log("all_has_sword=%s" % all_has_sword)

if not all_has_sword:
    # Strategy 2: CreateNodeAndRename for each component
    log("trying CreateNodeAndRename")
    for label, comp in [("Sword", sword), ("Shield", shield)]:
        try:
            p = CreateNodeAndRename(scs_ptr, ue_ptr(comp))
            log("CreateNodeAndRename %s => 0x%X" % (label, p or 0))
        except Exception as e:
            log("CreateNodeAndRename %s FAIL %s" % (label, traceback.format_exc()))
    text = dump_scs("after_createrename")
    all_has_sword = any(("AllNodes" in ln and "Sword" in ln) for ln in text.splitlines())
    log("all_has_sword2=%s" % all_has_sword)

if not all_has_sword:
    # Strategy 3: harvest mode overload
    log("trying AddCB harvest mode 0")
    try:
        AddCB2(bp_ptr, byref(arr), 0, None, 0)
        log("AddCB2 OK")
    except Exception as e:
        log("AddCB2 FAIL %s" % traceback.format_exc())
    text = dump_scs("after_addcb2")

# If nodes exist (even orphans), SetParent to mesh
for name in ["SCS_Node_SwordMesh", "SCS_Node_ShieldMesh"]:
    node = unreal.load_object(None, BP_PATH + ".BP_KayKitKnight_C:SimpleConstructionScript_0." + name)
    log("node %s = %s" % (name, node))
    if node:
        try:
            AddNode(scs_ptr, ue_ptr(node))
            log("AddNode %s OK" % name)
        except Exception as e:
            log("AddNode %s ERR %s" % (name, e))
        try:
            SetParent_SC(ue_ptr(node), mesh_ptr)
            log("SetParent %s OK" % name)
        except Exception as e:
            log("SetParent %s ERR %s" % (name, e))

# Also try SetParent with CDO mesh (native) after destroying actor
cdo_mesh = unreal.get_default_object(bp_cls).get_editor_property("mesh")
log("cdo_mesh=%s" % cdo_mesh)

# Destroy temp actor BEFORE final SetParent to CDO mesh
try:
    unreal.EditorLevelLibrary.destroy_actor(actor)
    log("destroyed temp actor")
except Exception as e:
    log("destroy ERR %s" % e)

for name, sock in [("SCS_Node_SwordMesh", "handslot_r"), ("SCS_Node_ShieldMesh", "handslot_l")]:
    node = unreal.load_object(None, BP_PATH + ".BP_KayKitKnight_C:SimpleConstructionScript_0." + name)
    if node and cdo_mesh:
        try:
            SetParent_SC(ue_ptr(node), ue_ptr(cdo_mesh))
            log("SetParent CDO %s OK" % name)
        except Exception as e:
            log("SetParent CDO %s ERR %s" % (name, e))

text = dump_scs("final")

ok = unreal.EditorAssetLibrary.save_asset(BP_PATH)
log("save=%s" % ok)
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
aes.open_editor_for_assets([bp])
unreal.EditorAssetLibrary.sync_browser_to_objects([SWORD_PATH, SHIELD_PATH])
log("opened")

# Mark package dirty / notify
try:
    bp.modify()
    log("bp.modify OK")
except Exception as e:
    log("modify ERR %s" % e)

open(LOG, "w", encoding="utf-8").write("\n".join(L))
print("FINISH_V2_DONE")