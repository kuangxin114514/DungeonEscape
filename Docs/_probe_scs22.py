import unreal, ctypes, re, traceback
from ctypes import c_void_p, c_int32, c_uint32, c_char_p, c_int, c_uint64, Structure, byref

LOG = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs22.log"
lines = []
def log(m):
    s = str(m); lines.append(s); print(s)

def ue_ptr(obj):
    m = re.search(r"\(0x([0-9A-Fa-f]+)\)", repr(obj))
    if not m:
        raise RuntimeError("no ptr in %r" % (obj,))
    return int(m.group(1), 16)

class FName(Structure):
    _fields_ = [("ComparisonIndex", c_int32), ("Number", c_uint32)]

ENGINE = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Engine.dll"
CORE = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Core.dll"
engine = ctypes.CDLL(ENGINE)
core = ctypes.CDLL(CORE)

AddNode = getattr(engine, "?AddNode@USimpleConstructionScript@@QEAAXPEAVUSCS_Node@@@Z")
AddNode.argtypes = [c_void_p, c_void_p]
AddNode.restype = None

CreateNode = getattr(engine, "?CreateNode@USimpleConstructionScript@@QEAAPEAVUSCS_Node@@PEAVUClass@@VFName@@@Z")
# Pass FName as uint64 by value
CreateNode.argtypes = [c_void_p, c_void_p, c_uint64]
CreateNode.restype = c_void_p

CreateNodeAndRename = getattr(engine, "?CreateNodeAndRenameComponent@USimpleConstructionScript@@QEAAPEAVUSCS_Node@@PEAVUActorComponent@@@Z")
CreateNodeAndRename.argtypes = [c_void_p, c_void_p]
CreateNodeAndRename.restype = c_void_p

SetParent_SC = getattr(engine, "?SetParent@USCS_Node@@QEAAXPEBVUSceneComponent@@@Z")
SetParent_SC.argtypes = [c_void_p, c_void_p]
SetParent_SC.restype = None

# Also SetParent(USCS_Node* parent node) overload
SetParent_Node = getattr(engine, "?SetParent@USCS_Node@@QEAAXPEAV1@@Z")
SetParent_Node.argtypes = [c_void_p, c_void_p]
SetParent_Node.restype = None

scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
scs_ptr = ue_ptr(scs)
log("scs_ptr=0x%X" % scs_ptr)

sword_node = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_SwordMesh")
shield_node = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0.SCS_Node_ShieldMesh")
log("sword_node=%s" % sword_node)
log("shield_node=%s" % shield_node)

# Ensure meshes on templates
sword_mesh = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
shield_mesh = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield")
for node, mesh, label in [(sword_node, sword_mesh, "Sword"), (shield_node, shield_mesh, "Shield")]:
    if not node:
        continue
    # find child GEN
    for obj in unreal.ObjectIterator(unreal.StaticMeshComponent):
        pn = unreal.Object.get_path_name(obj)
        if unreal.Object.get_path_name(node) in pn and "GEN_VARIABLE" in pn:
            try:
                obj.set_editor_property("static_mesh", mesh)
                log("%s template mesh set on %s" % (label, pn))
            except Exception as e:
                log("%s mesh ERR %s" % (label, e))

# Strategy A: AddNode existing orphans
for label, node in [("Sword", sword_node), ("Shield", shield_node)]:
    if not node:
        continue
    try:
        AddNode(scs_ptr, ue_ptr(node))
        log("AddNode %s OK" % label)
    except Exception as e:
        log("AddNode %s FAIL %s" % (label, traceback.format_exc()))

# Export to check AllNodes
def export_scs(tag):
    task = unreal.AssetExportTask()
    task.set_editor_property("object", scs)
    task.set_editor_property("filename", r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_%s.copy" % tag)
    task.set_editor_property("automated", True)
    task.set_editor_property("prompt", False)
    task.set_editor_property("exporter", unreal.ObjectExporterT3D())
    unreal.Exporter.run_asset_export_task(task)
    log("exported %s" % tag)

export_scs("after_addnode")

# Read AllNodes lines from file
p = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/knight_scs_after_addnode.copy"
try:
    text = open(p, encoding="utf-8", errors="ignore").read()
    for line in text.splitlines():
        if "AllNodes" in line or "RootNodes" in line or "SwordMesh" in line or "ShieldMesh" in line or "InternalVariableName" in line or "AttachToName" in line or "ParentComponent" in line or "ComponentClass" in line:
            log("T3D: " + line.strip())
except Exception as e:
    log("read ERR %s" % e)

# Strategy B if AddNode didn't wire: CreateNode with NAME_None (0)
allnodes_ok = False
try:
    text = open(p, encoding="utf-8", errors="ignore").read()
    allnodes_ok = "SwordMesh" in text.split("AllNodes")[-1] if "AllNodes" in text else False
except Exception:
    pass

if not allnodes_ok:
    log("AddNode did not wire into AllNodes; trying CreateNode(NAME_None)")
    smc_cls = unreal.StaticMeshComponent.static_class()
    none_fname = c_uint64(0)
    try:
        ptr = CreateNode(scs_ptr, ue_ptr(smc_cls), none_fname)
        log("CreateNode None => 0x%X" % (ptr or 0))
    except Exception as e:
        log("CreateNode None FAIL %s" % traceback.format_exc())
    # CreateNodeAndRename with fresh template
    try:
        bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
        tmpl = unreal.new_object(unreal.StaticMeshComponent, scs, "TmpSwordTemplate")
        tmpl.set_editor_property("static_mesh", sword_mesh)
        log("tmpl=%s" % tmpl)
        ptr = CreateNodeAndRename(scs_ptr, ue_ptr(tmpl))
        log("CreateNodeAndRename => 0x%X" % (ptr or 0))
    except Exception as e:
        log("CreateNodeAndRename FAIL %s" % traceback.format_exc())
    export_scs("after_createnode")

# If we have nodes in AllNodes, set parent to Mesh via SetParent
gen_cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
cdo = unreal.get_default_object(gen_cls)
mesh = cdo.get_editor_property("mesh")
log("mesh=%s" % mesh)

# Try SetParent on sword/shield nodes to mesh
for label, node in [("Sword", sword_node), ("Shield", shield_node)]:
    if node and mesh:
        try:
            SetParent_SC(ue_ptr(node), ue_ptr(mesh))
            log("SetParent_SC %s OK" % label)
        except Exception as e:
            log("SetParent_SC %s FAIL %s" % (label, e))

export_scs("after_setparent")

# Save and open
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
ok = unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
log("save %s" % ok)
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
aes.open_editor_for_assets([bp])
log("opened")

open(LOG, "w", encoding="utf-8").write("\n".join(lines))
log("DONE")