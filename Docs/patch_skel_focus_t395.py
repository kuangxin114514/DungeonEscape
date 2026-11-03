# -*- coding: utf-8 -*-
from __future__ import print_function
import io, re
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()

raw2, n1 = re.subn(
    r'mov\.set_editor_property\("orient_rotation_to_movement", True\)\n'
    r'\s*mov\.set_editor_property\("use_controller_desired_rotation", False\)',
    'mov.set_editor_property("orient_rotation_to_movement", False)\n'
    '            mov.set_editor_property("use_controller_desired_rotation", True)',
    raw, count=1)
print("settings_swap", n1)

helpers = '''
def _set_focus_player(controller, player):
    if controller is None or player is None:
        return
    try:
        controller.set_focus(player)
        return
    except Exception:
        pass
    try:
        controller.set_focal_point(player.get_actor_location())
    except Exception:
        pass


def _clear_focus(controller):
    if controller is None:
        return
    try:
        controller.clear_focus()
    except Exception:
        pass


'''

if "def _set_focus_player" not in raw2:
    raw2 = raw2.replace("def _add_input_toward(pawn, target_loc):", helpers + "def _add_input_toward(pawn, target_loc):", 1)
    print("helpers_added")
else:
    print("helpers_exist")

raw2, n2 = re.subn(
    r'(if dist > LOSE_RANGE:\n'
    r'\s*st\["aggro"\] = False\n'
    r'\s*st\["in_melee_since"\] = 0\.0\n'
    r'\s*if ctrl:\n'
    r'\s*_stop_move\(ctrl\))',
    r'\1\n                _clear_focus(ctrl)',
    raw2, count=1)
print("lose_focus", n2)

raw2, n3 = re.subn(
    r'(if dist <= AGGRO_RANGE and _has_los\(world, enemy, player\):\n'
    r'\s*st\["aggro"\] = True\n)',
    r'\1                if ctrl:\n                    _set_focus_player(ctrl, player)\n',
    raw2, count=1)
print("aggro_focus", n3)

raw2, n4 = re.subn(
    r'(if dist <= ATTACK_RANGE:\n'
    r'\s*if ctrl:\n'
    r'\s*_stop_move\(ctrl\))',
    r'\1\n                _set_focus_player(ctrl, player)',
    raw2, count=1)
print("atk_focus", n4)

raw2, n5 = re.subn(
    r'(st\["in_melee_since"\] = 0\.0\n)'
    r'(\s*)_move_to\(ctrl, player, enemy\)',
    r'\1\2if ctrl:\n\2    _set_focus_player(ctrl, player)\n\2_move_to(ctrl, player, enemy)',
    raw2, count=1)
print("chase_focus", n5)

if raw2 == raw:
    print("NO_CHANGE")
else:
    io.open(p, "w", encoding="utf-8", newline="\n").write(raw2)
    print("WRITTEN", len(raw2))

for i, line in enumerate(io.open(p, encoding="utf-8"), 1):
    if any(k in line for k in ("orient_rotation", "use_controller_desired", "_set_focus", "_clear_focus")):
        print("%d:%s" % (i, line.rstrip()))
