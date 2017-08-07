import os
import json
import codecs
import shutil
import click

CONTEXT_SETTINGS = {
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
    profile_name = os.environ.get("CONDA_DEFAULT_ENV", name)
    status = os.system("ipython profile create --parallel --profile=%s --ipython-dir=%s" %
                       (profile_name, path))
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
