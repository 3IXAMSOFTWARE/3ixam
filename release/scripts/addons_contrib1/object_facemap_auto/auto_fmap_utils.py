

# <pep8 compliant>


# Use so we can develop modules without reloading the add-on.

def import_reload_or_none(name, reload=True):
    """
    Import and reload a module.
    """
    try:
        mod = __import__(name)
        if reload:
            import importlib
            mod = importlib.reload(mod)
        import sys
        return sys.modules[name]
    except Exception:
        import traceback
        traceback.print_exc()
        return None
