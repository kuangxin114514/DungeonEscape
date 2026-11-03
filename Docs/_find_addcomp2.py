import re
path = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-UnrealEd.dll"
with open(path,"rb") as f: data=f.read()
# Get full null-terminated export-like strings
for m in re.finditer(rb"\?AddComponentsToBlueprint@FKismetEditorUtilities@@[A-Za-z0-9_@$?]+", data):
    s=m.group().decode("ascii","ignore")
    print(len(s), s)
print("--- AttachTo ---")
path2 = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Engine.dll"
with open(path2,"rb") as f: data2=f.read()
for key in [b"SetupAttachment@USceneComponent", b"AttachToComponent@USceneComponent", b"RegisterComponent@UActorComponent", b"UnregisterComponent@UActorComponent", b"DestroyComponent@UActorComponent", b"SetStaticMesh@UStaticMeshComponent"]:
  print("KEY", key.decode())
  for m in re.finditer(rb"\?"+key[1:].split(b"@")[0]+rb"@"+key.split(b"@")[1]+rb"@@[A-Za-z0-9_@$?]+" if b"@" in key else key, data2):
    s=m.group().decode("ascii","ignore")
    if len(s)<160: print(" ", s)
# broader
for pat in [rb"\?SetupAttachment@USceneComponent@@[A-Za-z0-9_@$?]+", rb"\?K2_AttachToComponent@USceneComponent@@[A-Za-z0-9_@$?]+", rb"\?RegisterComponent@UActorComponent@@[A-Za-z0-9_@$?]+", rb"\?RegisterComponentWithWorld@UActorComponent@@[A-Za-z0-9_@$?]+"]:
  print("PAT", pat)
  found=set(m.group().decode("ascii","ignore") for m in re.finditer(pat, data2))
  for s in sorted(found)[:10]:
    if len(s)<170: print(" ", s)
