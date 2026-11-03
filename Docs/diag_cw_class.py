from __future__ import print_function
import unreal
LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_cw_class.txt"
f = open(LOG, "w")
def log(m):
    f.write(str(m)+"\n"); f.flush()
for i in (0,1):
    n = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph.K2Node_CreateWidget_%d" % i)
    log("CW%d=%s" % (i,n))
    if not n: continue
    log("dir: %s" % [m for m in dir(n) if not m.startswith("_")])
    for m in ("get_class_to_spawn", "GetClassToSpawn", "get_widget_class", "find_pin", "FindPin", "get_all_pins", "get_pin_names"):
        if hasattr(n, m):
            try:
                fn = getattr(n, m)
                log("%s -> %s" % (m, fn() if callable(fn) else fn))
            except Exception as e:
                try:
                    log("%s(Class) -> %s" % (m, getattr(n,m)("Class")))
                except Exception as e2:
                    log("%s err %s / %s" % (m, e, e2))
    # try call_method
    for meth in ("GetClass", "get_class_to_spawn", "GetWidgetClass"):
        try:
            log("call %s -> %s" % (meth, n.call_method(meth)))
        except Exception as e:
            log("call %s %s" % (meth, e))
# verify slot still TL
slot = unreal.load_object(None, "/Game/UI/HUD/WBP_PlayerHealthBar.WBP_PlayerHealthBar:WidgetTree.CanvasPanel_0.CanvasPanelSlot_3")
log("slot pos=%s size=%s" % (slot.get_position(), slot.get_size()))
# verify ensure still in tick after reload
import shop_interact_runtime as sir, inspect
log("in tick=%s" % ("ensure_health_hud(world, pc, pawn)" in inspect.getsource(sir._on_tick)))
log("slot force in ensure=%s" % ("health slot force" in inspect.getsource(sir.ensure_health_hud) or "Force top-left" in inspect.getsource(sir.ensure_health_hud)))
f.close(); print("OK")