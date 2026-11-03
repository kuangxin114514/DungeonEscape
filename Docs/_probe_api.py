import unreal
LOG=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_api.log"
L=[]
def log(m):
    L.append(str(m)); print(m)

smc = unreal.StaticMeshComponent
names = [n for n in dir(smc) if any(k in n.lower() for k in ("attach","register","socket","static_mesh","setup"))]
log("SMC methods: %s" % names)
actor_names = [n for n in dir(unreal.Actor) if any(k in n.lower() for k in ("component","attach","add_"))]
log("Actor methods: %s" % actor_names)
for cls in ["EditorLevelLibrary","EditorActorSubsystem","GameplayStatics","KismetSystemLibrary"]:
    try:
        c=getattr(unreal, cls)
        hits=[n for n in dir(c) if any(k in n.lower() for k in ("spawn","component","add_"))]
        log("%s: %s" % (cls, hits[:40]))
    except Exception as e:
        log("%s ERR %s" % (cls, e))

bp_cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
log("bp_cls=%s" % bp_cls)
loc = unreal.Vector(0,0,500)
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(bp_cls, loc)
log("spawned=%s" % actor)
if actor:
    mesh = None
    try:
        comps = actor.get_components_by_class(unreal.SkeletalMeshComponent)
        log("skel comps=%s" % [c.get_name() for c in comps])
        mesh = comps[0] if comps else None
    except Exception as e:
        log("get comps ERR %s" % e)
    log("mesh=%s" % mesh)
    sword_asset = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
    try:
        sword = unreal.new_object(unreal.StaticMeshComponent, actor, "SwordMeshProbe")
        log("new_object sword=%s" % sword)
        try:
            sword.set_editor_property("static_mesh", sword_asset)
            log("set mesh ok")
        except Exception as e:
            log("set mesh ERR %s" % e)
        for meth in ["register_component", "RegisterComponent", "register_component_with_world"]:
            if hasattr(sword, meth):
                log("has %s" % meth)
                try:
                    getattr(sword, meth)()
                    log("%s OK" % meth)
                except Exception as e:
                    log("%s ERR %s" % (meth, e))
        for meth in ["attach_to_component", "k2_attach_to_component", "setup_attachment"]:
            if hasattr(sword, meth):
                log("has %s" % meth)
        try:
            ok = sword.attach_to_component(mesh, unreal.Name("handslot_r"), unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, False)
            log("attach_to_component => %s parent=%s sock=%s" % (ok, sword.get_attach_parent(), sword.get_attach_socket_name()))
        except Exception as e:
            log("attach ERR %s" % e)
    except Exception as e:
        import traceback; log("new_object ERR %s" % traceback.format_exc())
    try:
        unreal.EditorLevelLibrary.destroy_actor(actor)
        log("destroyed actor")
    except Exception as e:
        log("destroy ERR %s" % e)

open(LOG,"w",encoding="utf-8").write("\n".join(L))
print("PROBE_API_DONE")