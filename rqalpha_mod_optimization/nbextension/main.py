import os
import json
import codecs
import sys
import shutil
import click
import platform

from rqalpha_mod_optimization.utils import get_conda_env

CONTEXT_SETTINGS = {
}

BIN_DIR = {
    "Windows": "Scripts",
    "Linux": "bin"
}


def entry_point():
    cli(obj={})


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("-v", "--verbose", count=True)
@click.pass_context
def cli(ctx, verbose):
    ctx.obj["VERBOSE"] = verbose


@cli.command()
@click.help_option("-h", "--help")
@click.option("-p", "--path", default=os.environ.get("IPYTHONPATH", os.path.join(os.path.expanduser("~"), ".ipython")),
              help="profile's path")
@click.option("-n", "--name", default="root",
              help="profile's name")
def create_profile(path, name):
    profile_name = get_conda_env()
    prefix = sys.exec_prefix
    cmd = "%s profile create --parallel --profile=%s --ipython-dir=%s" % \
          (os.path.join(prefix, BIN_DIR[platform.system()], "ipython"), profile_name, path)
    print(cmd)
    status = os.system(cmd)
    if status:
        return status
    shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ipcluster_config.py"),
                os.path.join(path, "profile_%s" % profile_name, "ipcluster_config.py"))
    config = {
        "environment": {
            "CONDA_DEFAULT_ENV": profile_name
        }
    }
    with codecs.open(os.path.join(path, "profile_%s" % profile_name, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f)
