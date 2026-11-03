# -*- coding: utf-8 -*-
import ast
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
t=open(p,encoding="utf-8").read()
old='xf = unreal.Transform(rot, loc, unreal.Vector(1.0, 1.0, 1.0))'
new='xf = unreal.Transform(loc, rot, unreal.Vector(1.0, 1.0, 1.0))'
if old not in t:
    raise SystemExit("transform line missing")
t=t.replace(old,new,1)
# also harden buy_sword1 so exceptions in swap still force mesh
old_buy_owned='''    if SWORD1_ITEM in inv:
        set_equipped_sword(SWORD1_ITEM, world_ctx)
        ensure_equipped_pawn_class(world_ctx, force=True)
        _print(world_ctx, u"已切换剑1角色", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True
'''
new_buy_owned='''    if SWORD1_ITEM in inv:
        set_equipped_sword(SWORD1_ITEM, world_ctx)
        try:
            ensure_equipped_pawn_class(world_ctx, force=True)
        except Exception as e:
            _log("buy_sword1 ensure " + str(e))
            try:
                pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
                _force_sword1_mesh_on_pawn(pc.get_controlled_pawn() if pc else None)
            except Exception:
                pass
        _print(world_ctx, u"已切换剑1角色", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True
'''
if old_buy_owned not in t:
    raise SystemExit("owned buy block missing")
t=t.replace(old_buy_owned, new_buy_owned, 1)
old_buy_new='''    add_item(SWORD1_ITEM, world_ctx)
    set_equipped_sword(SWORD1_ITEM, world_ctx)
    ensure_equipped_pawn_class(world_ctx, force=True)
'''
new_buy_new='''    add_item(SWORD1_ITEM, world_ctx)
    set_equipped_sword(SWORD1_ITEM, world_ctx)
    try:
        ensure_equipped_pawn_class(world_ctx, force=True)
    except Exception as e:
        _log("buy_sword1 ensure " + str(e))
        try:
            pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
            _force_sword1_mesh_on_pawn(pc.get_controlled_pawn() if pc else None)
        except Exception:
            pass
'''
if old_buy_new not in t:
    raise SystemExit("new buy block missing")
t=t.replace(old_buy_new, new_buy_new, 1)
if "T332_FIX_XFORM" not in t:
    t=t.replace("T331_FIX_SWAP", "T331_FIX_SWAP T332_FIX_XFORM", 1)
open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("SYNTAX_OK")
