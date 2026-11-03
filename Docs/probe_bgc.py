# -*- coding: utf-8 -*-
import unreal, json
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_bgc.json"
r={"tries":[]}
def note(m,**k):
 e={"m":m};e.update(k);r["tries"].append(e)

# Open BP editor again
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
aes.open_editor_for_assets([bp])

cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
note("cls", val=str(cls), type=type(cls).__name__)
note("cls_dir", d=[a for a in dir(cls) if not a.startswith("_")][:60])
for prop in ("SimpleConstructionScript","simple_construction_script","OverridenArchetype","ComponentTemplates","InheritableComponentHandler","CookedComponentInstancingData"):
  try:
    v=cls.get_editor_property(prop); note("cls_prop", prop=prop, val=str(v)[:200])
  except Exception as e:
    note("cls_prop_fail", prop=prop, err=str(e)[:200])

# Try on BlueprintGeneratedClass default
try:
  bgc = unreal.BlueprintGeneratedClass.cast(cls)
  note("bgc", val=str(bgc))
except Exception as e:
  note("bgc_cast", err=str(e))

# NewObject SCS_Node?
for name in ("SCS_Node","SimpleConstructionScript","BPEditorLibrary","BlueprintEditorLibrary","SubobjectDataSubsystem"):
  note("has_"+name, val=hasattr(unreal, name))

# Try creating Actor BP, compile, then inspect CDO for DefaultSceneRoot - Actor BPs created in editor UI have SCS; Python-created ones might too internally
tools = unreal.AssetToolsHelpers.get_asset_tools()
path="/Game/Characters/Player/KayKit/BP_ArmedSocketTest"
if unreal.EditorAssetLibrary.does_asset_exist(path):
  unreal.EditorAssetLibrary.delete_asset(path)
factory=unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
abp=tools.create_asset("BP_ArmedSocketTest","/Game/Characters/Player/KayKit", unreal.Blueprint, factory)
note("abp", val=str(abp))
# After create, compile via loading class
try:
  # Force generate
  unreal.EditorAssetLibrary.save_loaded_asset(abp)
except Exception as e:
  note("save_abp", err=str(e))

# Use CoreRedirects? 
# Try accessing via find_object
try:
  scs = unreal.find_object(abp, "SimpleConstructionScript")
  note("find_scs", val=str(scs))
  if scs:
    note("find_scs_dir", d=[a for a in dir(scs) if not a.startswith("_")])
    # Try CreateNode via call_method with different signatures
    for args in [
      (unreal.StaticMeshComponent,),
      (unreal.StaticMeshComponent, "Sword"),
    ]:
      try:
        n=scs.call_method("CreateNode", args); note("CreateNode", args=str(args), n=str(n))
      except Exception as e:
        note("CreateNode_fail", err=str(e)[:300])
except Exception as e:
  note("find_fail", err=str(e))

# find_object on knight BP
try:
  scs2 = unreal.find_object(bp, "SimpleConstructionScript")
  note("knight_scs", val=str(scs2))
except Exception as e:
  note("knight_scs_fail", err=str(e))

# All objects with outer = bp
try:
  # iterate
  note("bp_outer", val=str(bp.get_outer()))
except Exception as e:
  pass

with open(OUT,"w",encoding="utf-8") as f: json.dump(r,f,indent=2,default=str)
print("BGC_DONE")