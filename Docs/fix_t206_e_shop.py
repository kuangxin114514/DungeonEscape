# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, sys, traceback
LOG = r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t206.txt'
PYDIR = r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python'
lines=[]
def log(m): lines.append(str(m))
def flush(): open(LOG,'w',encoding='utf-8').write(chr(10).join(lines)+chr(10))
try:
    if PYDIR not in sys.path: sys.path.insert(0, PYDIR)
    for k in list(sys.modules.keys()):
        if 'shop_interact_runtime' in k: del sys.modules[k]
    import shop_interact_runtime as r
    log('V10=%s gen=%s tick=%s' % ('SAFE_V10' in open(r.__file__,encoding='utf-8').read(80), r._MY_GEN[0], r._TICK[0]))
    ws = unreal.EditorLevelLibrary.get_pie_worlds(False) or unreal.EditorLevelLibrary.get_pie_worlds(True)
    log('pie=%s' % ws)
    world = ws[0] if ws else None
    if not world:
        log('NO_PIE'); flush(); raise SystemExit
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    log('pc=%s pawn=%s' % (pc, pawn))
    if pawn:
        loc = pawn.get_actor_location()
        log('loc=%s,%s,%s' % (loc.x, loc.y, loc.z))
        title, gate = r.scan_near(world, loc)
        log('near title=%s gate=%s' % (title, gate))
    # open shop
    ok = r.open_shop(world, u'\u56de\u8840\u5e97')
    wid = r._OPEN_WIDGET[0]
    texts=0; invp=False; vis=None
    if wid is not None:
        try: invp=bool(wid.is_in_viewport())
        except Exception: pass
        try: vis=str(wid.get_visibility())
        except Exception: pass
        base=wid.get_path_name()
        for o in unreal.ObjectIterator(unreal.TextBlock):
            try:
                if base in o.get_path_name(): texts += 1
            except Exception: pass
    proof = bool(ok and wid is not None and (texts>=1 or invp))
    log('open_shop=%s wid=%s texts=%s vis=%s invp=%s' % (ok, wid, texts, vis, invp))
    log('PROOF_OPEN=%s' % proof)
    # close + handle_interact (E path)
    try: r.close_shop(world)
    except Exception: pass
    ok2 = r.handle_interact(world)
    wid2 = r._OPEN_WIDGET[0]
    texts2=0; invp2=False
    if wid2 is not None:
        try: invp2=bool(wid2.is_in_viewport())
        except Exception: pass
        base=wid2.get_path_name()
        for o in unreal.ObjectIterator(unreal.TextBlock):
            try:
                if base in o.get_path_name(): texts2 += 1
            except Exception: pass
    proof2 = bool(ok2 and wid2 is not None and (texts2>=1 or invp2))
    log('handle_interact=%s texts=%s invp=%s PROOF_HANDLE=%s' % (ok2, texts2, invp2, proof2))
    log('E_TICK_ARMED=%s' % (r._TICK[0] is not None))
    # leave shop open for user visibility
    flush()
    unreal.log('T206 PROOF_OPEN=%s PROOF_HANDLE=%s' % (proof, proof2))
except Exception:
    log('FATAL '+traceback.format_exc()); flush()
