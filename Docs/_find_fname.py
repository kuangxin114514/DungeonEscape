import re
path = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Core.dll"
with open(path, "rb") as f:
    data = f.read()
print("size", len(data))
found = set()
for m in re.finditer(rb"\?\?0FName@@[A-Za-z0-9_@$?]{5,120}", data):
    found.add(m.group().decode("ascii", errors="ignore"))
for m in re.finditer(rb"\?Init@FName@@[A-Za-z0-9_@$?]{5,120}", data):
    found.add(m.group().decode("ascii", errors="ignore"))
# Also FName::FName(char*, EFindName)
for s in sorted(found):
    if len(s) < 150:
        print(s)
print("count", len(found))

# Also check Engine dll for StaticClass StaticMeshComponent
path2 = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Engine.dll"
with open(path2, "rb") as f:
    data2 = f.read()
found2 = set()
for m in re.finditer(rb"\?StaticClass@UStaticMeshComponent@@[A-Za-z0-9_@$?]{5,80}", data2):
    found2.add(m.group().decode("ascii", errors="ignore"))
for m in re.finditer(rb"\?StaticClass@UChildActorComponent@@[A-Za-z0-9_@$?]{5,80}", data2):
    found2.add(m.group().decode("ascii", errors="ignore"))
print("StaticClass matches:")
for s in sorted(found2):
    print(s)