import re
for path in [
 r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Engine.dll",
 r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-UnrealEd.dll",
]:
  print("===", path.split("\\")[-1])
  with open(path,"rb") as f: data=f.read()
  for key in [b"SetAttachToName", b"AttachToName", b"SetParent@USCS", b"AddNode@USimple", b"CreateNodeAndRename", b"ValidateNode", b"AddComponentsToBlueprint"]:
    found=set()
    for m in re.finditer(rb"[?A-Za-z_][A-Za-z0-9_@$?]{0,200}"+re.escape(key)+rb"[A-Za-z0-9_@$?]{0,100}", data):
      s=m.group().decode("ascii","ignore")
      if len(s)<180: found.add(s)
    if found:
      print("--", key.decode())
      for s in sorted(found)[:20]: print(s)
