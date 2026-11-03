import sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT=r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_preview2.txt"
def w(m):
  open(LOG,"a",encoding="utf-8").write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
sk=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
skel=sk.get_editor_property("skeleton")
w("sk methods preview/attach/call: "+str([x for x in dir(sk) if "preview" in x.lower() or "attach" in x.lower() or "call" in x.lower() or "socket" in x.lower()]))
w("skel methods: "+str([x for x in dir(skel) if "preview" in x.lower() or "attach" in x.lower() or "socket" in x.lower() or "call" in x.lower()]))
# try call_method variants
for name in ("GetPreviewAttachedAssetContainer","get_preview_attached_asset_container","ValidatePreviewAttachedObjects","ClearAllPreviewAttached","SetPreviewAttachedAssetContainer"):
  for obj,label in ((sk,"sk"),(skel,"skel")):
    try:
      if hasattr(obj, name):
        w(label+" hasattr "+name+" -> "+str(getattr(obj,name)))
      r=obj.call_method(name)
      w(label+" call "+name+" -> "+str(r)+" typ="+str(type(r)))
    except Exception as e:
      w(label+" fail "+name+" "+str(e))
# PreviewAssetAttachContainer type?
w("types: "+str([x for x in dir(unreal) if "Preview" in x and "Attach" in x]))
w("FPreview: "+str([x for x in dir(unreal) if "Preview" in x][:40]))
# sockets on sk
try:
  n=sk.num_sockets()
  w("num_sockets "+str(n))
  for i in range(n):
    s=sk.get_socket_by_index(i)
    w("sock "+str(i)+" "+str(s)+" name="+str(s.get_editor_property("socket_name") if s else None))
except Exception as e:
  w("sockerr "+str(e))
w("DONE")
'''
remote=re.RemoteExecution(); remote.start()
try:
  for i in range(10):
    time.sleep(0.5)
    if remote.remote_nodes:
      remote.open_command_connection(remote.remote_nodes[0]["node_id"]); break
  else:
    print("NO_NODES"); raise SystemExit(2)
  r=remote.run_command(STMT, unattended=True, exec_mode=re.MODE_EXEC_FILE)
  print("success", r.get("success"), r.get("result"))
finally:
  remote.stop()
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_preview2.txt",encoding="utf-8",errors="replace").read())
