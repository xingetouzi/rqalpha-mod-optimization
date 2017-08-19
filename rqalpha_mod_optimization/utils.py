import os
import sys
import platform


class Singleton(type):
    SINGLETON_ENABLED = True

    def __init__(cls, *args, **kwargs):
        cls._instance = None
        super(Singleton, cls).__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.SINGLETON_ENABLED:
            if cls._instance is None:
                cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
                return cls._instance
            else:
                return cls._instance
        else:
            return super(Singleton, cls).__call__(*args, **kwargs)


def get_conda_env():
    cmd = "conda env list"
    if platform.system() == "Windows":
        path = sys.exec_prefix[0].upper() + sys.exec_prefix[1:]
    elif platform.system() == "Linux":
        path = sys.exec_prefix
    lines = os.popen(cmd).readlines()
    for line in lines:
        line = line.replace("\n", "").replace("\r", " ")
        if not line.startswith("#") and line.endswith(path):
            return line.split(" ")[0]
    return "root"
