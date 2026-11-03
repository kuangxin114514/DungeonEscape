# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal

def open_shop_from_bp(title=u"商店"):
    try:
        import shop_interact_runtime as r
        world = r._pie_world()
        if world is None:
            unreal.log("open_shop_from_bp: no PIE")
            return False
        return r.open_shop(world, title)
    except Exception as e:
        unreal.log("open_shop_from_bp err " + str(e))
        return False
