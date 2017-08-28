import six
import os
import sys
import subprocess
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
    if platform.system() == "Windows":
        path = sys.exec_prefix[0].upper() + sys.exec_prefix[1:]
        bin_dir = "Scripts"
        encoding = "gbk"
    elif platform.system() == "Linux":
        path = sys.exec_prefix
        bin_dir = "bin"
        encoding = "utf-8"
    else:
        raise OSError("Unsupported OS")
    cmd = [os.path.join(path, bin_dir, "conda"), "env", "list"]
    lines = subprocess.check_output(cmd, shell=True)
    if isinstance(lines, six.binary_type):
        lines = lines.decode(encoding)
    print(type(lines))
    for line in lines.splitlines():
        if not line.startswith("#") and line.endswith(path):
            return line.split(" ")[0]
    return "root"
