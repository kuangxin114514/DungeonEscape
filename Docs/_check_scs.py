import unreal
bp = unreal.load_asset('/Game/Characters/Player/KayKit/BP_KayKitKnight')
scs = bp.simple_construction_script
print('scs', scs)
try:
  nodes = scs.get_editor_property('all_nodes')
  print('all_nodes', len(nodes) if nodes is not None else None)
  if nodes:
    for n in nodes:
      print('NODE', n)
      try:
        print(' tmpl', n.get_editor_property('component_template'))
      except Exception as e:
        print(' tmplerr', e)
      try:
        print(' cls', n.get_editor_property('component_class'))
      except Exception as e:
        print(' clserr', e)
      try:
        print(' attach', n.get_editor_property('attach_to_name'))
      except Exception as e:
        print(' attacherr', e)
except Exception as e:
  print('all_nodes err', e)