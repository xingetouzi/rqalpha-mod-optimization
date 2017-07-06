__config__ = {
    "sigleton_datasource": True
}


def load_mod():
    from .mod import OptimizationMod
    return OptimizationMod()
