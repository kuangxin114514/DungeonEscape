try:
    import shop_interact_runtime
except Exception as e:
    try:
        import unreal
        unreal.log_warning('init_unreal: '+str(e))
    except Exception:
        print('init_unreal', e)
