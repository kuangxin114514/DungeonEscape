import ctypes
from ctypes import wintypes
import sys

dll_path = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-UnrealEd.dll"
# Load as data to parse exports
with open(dll_path, "rb") as f:
    data = f.read()

# Parse PE exports for CreateNode / AddNode
e_lfanew = int.from_bytes(data[0x3C:0x40], "little")
# PE32+ 
optional_magic = int.from_bytes(data[e_lfanew+0x18:e_lfanew+0x1A], "little")
print("optional_magic", hex(optional_magic))
if optional_magic == 0x20b:  # PE32+
    export_rva = int.from_bytes(data[e_lfanew+0x88:e_lfanew+0x8C], "little")
else:
    export_rva = int.from_bytes(data[e_lfanew+0x78:e_lfanew+0x7C], "little")
print("export_rva", hex(export_rva))

# Map RVA to file offset via sections
num_sections = int.from_bytes(data[e_lfanew+6:e_lfanew+8], "little")
size_optional = int.from_bytes(data[e_lfanew+0x14:e_lfanew+0x16], "little")
section_start = e_lfanew + 0x18 + size_optional

def rva_to_off(rva):
    for i in range(num_sections):
        off = section_start + i*40
        virt = int.from_bytes(data[off+12:off+16], "little")
        raw_size = int.from_bytes(data[off+16:off+20], "little")
        raw_ptr = int.from_bytes(data[off+20:off+24], "little")
        virt_size = int.from_bytes(data[off+8:off+12], "little")
        size = max(virt_size, raw_size)
        if virt <= rva < virt + size:
            return raw_ptr + (rva - virt)
    return None

exp_off = rva_to_off(export_rva)
print("exp_off", exp_off)
number_of_names = int.from_bytes(data[exp_off+24:exp_off+28], "little")
names_rva = int.from_bytes(data[exp_off+32:exp_off+36], "little")
ords_rva = int.from_bytes(data[exp_off+36:exp_off+40], "little")
funcs_rva = int.from_bytes(data[exp_off+28:exp_off+32], "little")
names_off = rva_to_off(names_rva)
ords_off = rva_to_off(ords_rva)
print("number_of_names", number_of_names)

matches = []
for i in range(number_of_names):
    name_rva = int.from_bytes(data[names_off+i*4:names_off+i*4+4], "little")
    name_off = rva_to_off(name_rva)
    end = data.index(b"\x00", name_off)
    name = data[name_off:end].decode("ascii", errors="ignore")
    if any(k in name for k in ("CreateNode", "AddNode", "AddComponentsToBlueprint", "CreateBlueprintFromActor")):
        matches.append(name)

print("MATCHES", len(matches))
for m in matches[:80]:
    print(m)