import six
import rqalpha as rq
from rqalpha.interface import AbstractMod
from rqalpha_mod_optimization.utils import Singleton


def when_imported(*a, **kw):
    def decorator(func):
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapped

    return decorator

if six.PY3:
    from rqalpha_mod_optimization.singleton import when_imported

_BASE_DATA_SOURCE = None


class OptimizationMod(AbstractMod):
    def start_up(self, env, mod_config):
        global _BASE_DATA_SOURCE
        Singleton.SINGLETON_ENABLED = mod_config.sigleton_datasource
        if six.PY2 and mod_config.sigleton_datasource:
            self.patch_singleton(rq)
        if not env.data_source:
            env.set_data_source(_BASE_DATA_SOURCE(env.config.base.data_bundle_path))

    @staticmethod
    @when_imported("rqalpha")
    def patch_singleton(mod):
        global _BASE_DATA_SOURCE

        if _BASE_DATA_SOURCE is None:
            mod.interface.AbstractDataSource = Singleton("AbstractDataSource", (mod.interface.AbstractDataSource,), {})
            mod.data.base_data_source.BaseDataSource = Singleton("BaseDataSource",
                                                                 (mod.data.base_data_source.BaseDataSource,), {})
            _BASE_DATA_SOURCE = mod.data.base_data_source.BaseDataSource

    def tear_down(self, code, exception=None):
        pass
