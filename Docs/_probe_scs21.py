import unreal, ctypes, re, traceback
from ctypes import c_void_p, c_int32, c_uint32, c_char_p, c_int, c_uint64, Structure, byref, POINTER

LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs21.log"
lines = []
def log(m):
    s = str(m)
    lines.append(s)
    print(s)

def ue_ptr(obj):
    # repr like <Object '/path' (0x000001CC58AB6200) Class 'X'>
    m = re.search(r"\(0x([0-9A-Fa-f]+)\)", repr(obj))
    if not m:
        m = re.search(r"\(0x([0-9A-Fa-f]+)\)", str(obj))
    if not m:
        raise RuntimeError("no ptr in %r" % (obj,))
    return int(m.group(1), 16)

class FName(Structure):
    _fields_ = [("ComparisonIndex", c_int32), ("Number", c_uint32)]

CORE = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Core.dll"
ENGINE = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Engine.dll"
UNREALED = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-UnrealEd.dll"

core = ctypes.CDLL(CORE)
engine = ctypes.CDLL(ENGINE)

# FName(const char*, EFindName)
fname_ctor = getattr(core, "??0FName@@QEAA@PEBDW4EFindName@@@Z")
fname_ctor.argtypes = [c_void_p, c_char_p, c_int]
fname_ctor.restype = c_void_p

def make_fname(name):
    fn = FName()
    # EFindName::FNAME_Add = 1
    fname_ctor(byref(fn), name.encode("ascii"), 1)
    log("FName(%s) = ComparisonIndex=%s Number=%s" % (name, fn.ComparisonIndex, fn.Number))
    return fn

# CreateNode(this, UClass*, FName) -> USCS_Node*
CreateNode = getattr(engine, "?CreateNode@USimpleConstructionScript@@QEAAPEAVUSCS_Node@@PEAVUClass@@VFName@@@Z")
CreateNode.argtypes = [c_void_p, c_void_p, FName]
CreateNode.restype = c_void_p

# AddNode(this, USCS_Node*)
AddNode = getattr(engine, "?AddNode@USimpleConstructionScript@@QEAAXPEAVUSCS_Node@@@Z")
AddNode.argtypes = [c_void_p, c_void_p]
AddNode.restype = None

# SetParent if available
SetParent = None
try:
    SetParent = getattr(engine, "?SetParent@USCS_Node@@QEAAXPEBVUSceneComponent@@@Z")
    SetParent.argtypes = [c_void_p, c_void_p]
    SetParent.restype = None
    log("SetParent found")
except Exception as e:
    log("SetParent missing: %s" % e)
    # try other manglings
    for mang in [
        "?SetParent@USCS_Node@@QEAAXPEBVUSceneComponent@@@Z",
        "?SetParent@USCS_Node@@QEAAXPEAVUSceneComponent@@@Z",
    ]:
        try:
            SetParent = getattr(engine, mang)
            SetParent.argtypes = [c_void_p, c_void_p]
            SetParent.restype = None
            log("SetParent found as %s" % mang)
            break
        except Exception:
            pass

scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
smc_cls = unreal.StaticMeshComponent.static_class()
log("scs=%s ptr=0x%X" % (scs, ue_ptr(scs)))
log("smc_cls=%s ptr=0x%X" % (smc_cls, ue_ptr(smc_cls)))

sword_name = make_fname("SwordMesh")
shield_name = make_fname("ShieldMesh")

try:
    sword_node_ptr = CreateNode(ue_ptr(scs), ue_ptr(smc_cls), sword_name)
    log("CreateNode SwordMesh => 0x%X" % (sword_node_ptr or 0))
except Exception as e:
    log("CreateNode Sword FAIL %s" % traceback.format_exc())
    sword_node_ptr = None

try:
    shield_node_ptr = CreateNode(ue_ptr(scs), ue_ptr(smc_cls), shield_name)
    log("CreateNode ShieldMesh => 0x%X" % (shield_node_ptr or 0))
except Exception as e:
    log("CreateNode Shield FAIL %s" % traceback.format_exc())
    shield_node_ptr = None

# Re-export SCS to verify AllNodes
task = unreal.AssetExportTask()
task.set_editor_property("object", scs)
task.set_editor_property("filename", r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_after_ctypes.copy")
task.set_editor_property("automated", True)
task.set_editor_property("prompt", False)
task.set_editor_property("exporter", unreal.ObjectExporterT3D())
unreal.Exporter.run_asset_export_task(task)
log("exported after CreateNode")

# Find new nodes / templates via load_object
for path in [
    "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_SwordMesh",
    "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SwordMesh_GEN_VARIABLE",
    "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_3",
    "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_4",
]:
    o = unreal.load_object(None, path)
    log("load %s => %s" % (path, o))

# Iterate SCS_Node under knight
scs_node_cls = unreal.load_class(None, "/Script/Engine.SCS_Node")
sword_assets = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
shield_assets = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield")
for obj in unreal.ObjectIterator(scs_node_cls):
    pn = unreal.Object.get_path_name(obj)
    if "BP_KayKitKnight" in pn and "SimpleConstructionScript_0" in pn:
        log("NODE %s" % pn)

# Find StaticMeshComponent GEN_VARIABLE under knight SCS and assign meshes by name
smc_cls_u = unreal.StaticMeshComponent
for obj in unreal.ObjectIterator(smc_cls_u):
    pn = unreal.Object.get_path_name(obj)
    if "BP_KayKitKnight" in pn and "GEN_VARIABLE" in pn:
        log("GEN %s" % pn)
        try:
            if "Sword" in pn:
                obj.set_editor_property("static_mesh", sword_assets)
                log("  set sword")
            elif "Shield" in pn:
                obj.set_editor_property("static_mesh", shield_assets)
                log("  set shield")
        except Exception as e:
            log("  set ERR %s" % e)

# Try SetParent to Mesh component template - native Mesh on Character
# Get CDO mesh component
gen_cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
cdo = unreal.get_default_object(gen_cls)
mesh = cdo.get_editor_property("mesh")
log("cdo.mesh=%s ptr=%s" % (mesh, hex(ue_ptr(mesh)) if mesh else None))

# Save + open
ok = unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
log("save %s" % ok)
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
aes.open_editor_for_assets([bp])
log("opened BP editor")

open(LOG, "w", encoding="utf-8").write("\n".join(lines))
log("DONE")