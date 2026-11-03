# -*- coding: utf-8 -*-
import io
path = r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py'
with io.open(path, 'r', encoding='utf-8-sig') as f:
    text = f.read()

old_hdr = (
    "# T290: distance scale like world nameplate — near=big far=small (still flat screen HUD).\n"
    "#       ENEMY_HP_BAR_REF_DISTANCE / MIN_SCALE / MAX_SCALE at file top.\n"
    "# T278: after OpenLevel Hub<->Map_Dungeon1, clear HUD/enemy caches and recreate ensure_health_hud."
)
new_hdr = (
    "# T290: distance scale like world nameplate — near=big far=small (still flat screen HUD).\n"
    "#       ENEMY_HP_BAR_REF_DISTANCE / MIN_SCALE / MAX_SCALE at file top.\n"
    "# T295: ENEMY_HP_BAR_X_OFFSET at file top = simple left/right knob (screen px; +right / -left).\n"
    "# T278: after OpenLevel Hub<->Map_Dungeon1, clear HUD/enemy caches and recreate ensure_health_hud."
)
if old_hdr not in text:
    raise SystemExit('header block not found')
text = text.replace(old_hdr, new_hdr, 1)

old_z = (
    "ENEMY_HP_BAR_Z_OFFSET = 40.0\n"
    "_ENEMY_BODY_FALLBACK_Z = 120.0  # only if no head bone/bounds (from mesh/actor root)\n"
    "_ENEMY_BAR_Z = ENEMY_HP_BAR_Z_OFFSET  # alias for older call sites\n"
    "_ENEMY_DRAW = (140.0, 16.0)\n"
    "# ============================================================\n"
    "# 距离缩放（像头顶铭牌）：近大远小，仍是贴屏平面不透视歪斜"
)
new_z = (
    "ENEMY_HP_BAR_Z_OFFSET = 40.0\n"
    "# ============================================================\n"
    "# 改这个数字调骷髅血条左右：正数往右，负数往左（屏幕像素）\n"
    "# Change THIS number to nudge the enemy HP bar left/right on screen.\n"
    "# ============================================================\n"
    "ENEMY_HP_BAR_X_OFFSET = 0.0\n"
    "_ENEMY_BODY_FALLBACK_Z = 120.0  # only if no head bone/bounds (from mesh/actor root)\n"
    "_ENEMY_BAR_Z = ENEMY_HP_BAR_Z_OFFSET  # alias for older call sites\n"
    "_ENEMY_DRAW = (140.0, 16.0)\n"
    "# ============================================================\n"
    "# 距离缩放（像头顶铭牌）：近大远小，仍是贴屏平面不透视歪斜"
)
if old_z not in text:
    raise SystemExit('Z offset block not found')
text = text.replace(old_z, new_z, 1)

old_pos = (
    "            # Bottom-center of bar sits just above projected head (nameplate anchor)\n"
    "            px = sx - float(draw_w) * 0.5\n"
    "            py = sy - float(draw_h) - 4.0"
)
new_pos = (
    "            # Bottom-center of bar sits just above projected head (nameplate anchor)\n"
    "            # T295_X_OFFSET: screen-pixel left/right nudge after ProjectWorldToScreen\n"
    "            px = (sx + float(ENEMY_HP_BAR_X_OFFSET)) - float(draw_w) * 0.5\n"
    "            py = sy - float(draw_h) - 4.0"
)
if old_pos not in text:
    raise SystemExit('position block not found')
text = text.replace(old_pos, new_pos, 1)

old_log = '_log("runtime ready SPLIT_WBP_V15e_T290_DIST_SCALE")'
new_log = '_log("runtime ready SPLIT_WBP_V15e_T295_X_OFFSET")'
if old_log not in text:
    raise SystemExit('bootstrap log not found')
text = text.replace(old_log, new_log, 1)

with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
print('OK patched', path)
print('X_OFFSET present', 'ENEMY_HP_BAR_X_OFFSET = 0.0' in text)
print('pos wired', 'sx + float(ENEMY_HP_BAR_X_OFFSET)' in text)
