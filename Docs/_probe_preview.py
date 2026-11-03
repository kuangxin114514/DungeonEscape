import sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_preview.txt"
def w(m):
  with open(LOG,"a",encoding="utf-8") as f: f.write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
sk=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
w("sk="+str(sk))
# list editor props related to preview/attach
props=[]
for name in dir(sk):
  ln=name.lower()
  if "preview" in ln or "attach" in ln or "socket" in ln:
    props.append(name)
w("dir="+str(props))
for n in ("preview_attached_asset_container","PreviewAttachedAssetContainer","preview_skeletal_mesh","morph_targets","materials","sockets"):
  try:
    v=sk.get_editor_property(n)
    w("PROP %s type=%s val=%s"%(n,type(v),v))
  except Exception as e:
    w("FAIL %s %s"%(n,e))
# skeleton sockets / bone names with handslot
skel=sk.get_editor_property("skeleton")
w("skel="+str(skel))
try:
  # bone tree
  ref=skel.get_editor_property("bone_tree") if False else None
except Exception as e:
  w("bonetree "+str(e))
# material slot names
try:
  mats=sk.materials
  w("nmat="+str(len(list(mats)) if mats else 0))
  for i,m in enumerate(list(mats)[:20]):
    w("mat%d %s"%(i,m))
except Exception as e:
  w("mats "+str(e))
# Try clear preview via set empty array if property exists
for n in ("preview_attached_asset_container","PreviewAttachedAssetContainer"):
  try:
    sk.set_editor_property(n, [])
    w("CLEARED "+n)
  except Exception as e:
    w("clearfail %s %s"%(n,e))
unreal.EditorAssetLibrary.save_loaded_asset(sk)
w("DONE")
'''
remote=re.RemoteExecution(); remote.start()
try:
  node_id=None
  for i in range(8):
    time.sleep(0.5)
    if remote.remote_nodes: node_id=remote.remote_nodes[0]["node_id"]; break
  remote.open_command_connection(node_id)
  r=remote.run_command(STMT, unattended=True, exec_mode=re.MODE_EXEC_FILE)
  print("success", r.get("success"), r.get("result"))
finally:
  remote.stop()
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_preview.txt",encoding="utf-8").read())
