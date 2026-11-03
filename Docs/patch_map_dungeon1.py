# -*- coding: utf-8 -*-
from __future__ import print_function
import os, re, shutil
root = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
src = os.path.join(root, "Content", "Python", "shop_interact_runtime.py")
docs = os.path.join(root, "Docs", "shop_interact_runtime.py")
bak = src + ".pre_map_dungeon1"
shutil.copy2(src, bak)
text = open(src, "r", encoding="utf-8", errors="replace").read()
old = (
    'DUNGEON_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon"\n'
    'HUB_LEVEL = "/Game/Maps/Hub/Map_Hub"\n'
    "\n"
    "\n"
    "def enter_dungeon(world_ctx):\n"
    '    """OpenLevel to Map_Dungeon when E near red gate."""\n'
)
new = (
    "DUNGEON_LEVEL_CANDIDATES = (\n"
    '    "/Game/Maps/Dungeon/Map_Dungeon1",\n'
    '    "/Game/Maps/Dungeon/Map_Dungeon",\n'
    ")\n"
    'DUNGEON_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon1"\n'
    'HUB_LEVEL = "/Game/Maps/Hub/Map_Hub"\n'
    "\n"
    "\n"
    "def resolve_dungeon_level():\n"
    '    """Prefer Map_Dungeon1 when Map_Dungeon package is missing."""\n'
    "    global DUNGEON_LEVEL\n"
    "    chosen = DUNGEON_LEVEL_CANDIDATES[0]\n"
    "    try:\n"
    "        eal = unreal.EditorAssetLibrary\n"
    "        found = False\n"
    "        for path in DUNGEON_LEVEL_CANDIDATES:\n"
    "            try:\n"
    "                if eal.does_asset_exist(path):\n"
    "                    chosen = path\n"
    "                    found = True\n"
    "                    break\n"
    "            except Exception:\n"
    "                continue\n"
    "        if not found:\n"
    "            chosen = DUNGEON_LEVEL_CANDIDATES[0]\n"
    "    except Exception:\n"
    "        chosen = DUNGEON_LEVEL_CANDIDATES[0]\n"
    "    DUNGEON_LEVEL = chosen\n"
    "    return chosen\n"
    "\n"
    "\n"
    "def enter_dungeon(world_ctx):\n"
    '    """OpenLevel to Map_Dungeon1 (fallback Map_Dungeon) when E near red gate."""\n'
)
if old not in text:
    raise SystemExit("ANCHOR_NOT_FOUND")
text = text.replace(old, new, 1)
old2 = (
    "def enter_dungeon(world_ctx):\n"
    '    """OpenLevel to Map_Dungeon1 (fallback Map_Dungeon) when E near red gate."""\n'
    "    if world_ctx is None:\n"
    "        return False\n"
    "    close_shop(world_ctx)\n"
)
new2 = (
    "def enter_dungeon(world_ctx):\n"
    '    """OpenLevel to Map_Dungeon1 (fallback Map_Dungeon) when E near red gate."""\n'
    "    if world_ctx is None:\n"
    "        return False\n"
    "    level = resolve_dungeon_level()\n"
    "    close_shop(world_ctx)\n"
)
if old2 not in text:
    raise SystemExit("ENTER_HEAD_NOT_FOUND")
text = text.replace(old2, new2, 1)
m = re.search(r"def enter_dungeon\(world_ctx\):.*?def return_to_hub\(world_ctx\):", text, re.S)
if not m:
    raise SystemExit("ENTER_FN_NOT_FOUND")
block = m.group(0)
block2 = block
block2 = block2.replace(
    'unreal.GameplayStatics.open_level(world_ctx, DUNGEON_LEVEL, True, "")',
    'unreal.GameplayStatics.open_level(world_ctx, level, True, "")',
)
block2 = block2.replace('_log("OpenLevel " + DUNGEON_LEVEL)', '_log("OpenLevel " + level)')
block2 = block2.replace(
    'unreal.SystemLibrary.execute_console_command(world_ctx, "Open " + DUNGEON_LEVEL)',
    'unreal.SystemLibrary.execute_console_command(world_ctx, "Open " + level)',
)
block2 = block2.replace('_log("console Open " + DUNGEON_LEVEL)', '_log("console Open " + level)')
text = text[: m.start()] + block2 + text[m.end() :]
text = text.replace("OpenLevel Map_Dungeon FIRST", "OpenLevel Map_Dungeon1 FIRST", 1)
text = text.replace("# Map_Dungeon: near DungeonExit", "# Map_Dungeon1: near DungeonExit", 1)
text = text.replace(
    "Gate: Hub -> Map_Dungeon. hub_exit: Map_Dungeon stairs",
    "Gate: Hub -> Map_Dungeon1. hub_exit: Map_Dungeon1 stairs",
    1,
)
text = text.replace(
    "# Dungeon stairs exit wins in Map_Dungeon;",
    "# Dungeon stairs exit wins in Map_Dungeon1;",
    1,
)
text = text.replace(
    '"""If Map_Dungeon PIE has PC but no pawn',
    '"""If Map_Dungeon1 PIE has PC but no pawn',
    1,
)
open(src, "w", encoding="utf-8", newline="\n").write(text)
shutil.copy2(src, docs)
print("OK patched", src)
print("OK copied", docs)
for i, line in enumerate(open(src, encoding="utf-8"), 1):
    if "DUNGEON_LEVEL" in line or "resolve_dungeon_level" in line:
        print("%d:%s" % (i, line.rstrip()))
