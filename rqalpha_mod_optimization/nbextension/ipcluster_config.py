# Required
# MUST SET
import os
import json

profile = os.path.split(os.path.dirname(os.path.abspath(__file__)))[-1]
profile = profile[profile.find("_") + 1:]
user = os.environ.get("JPY_USER")
group = os.environ.get("MARATHON_IPYPARALLEL_APP_GROUP_FORMAT", "{username}/{profile}")
home = os.environ.get("HOST_HOME_DIR")


def parse_runtime_config():
    """using for read runtime config"""
    with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
        try:
            config = json.load(f, encoding="utf-8")
        except ValueError:
            return
        environment = config.get("environment", None)
        for k, v in environment.items():
            os.environ["k"] = v


parse_runtime_config()

# url with port to a marathon master
c.MarathonLauncher.marathon_master_url = os.environ.get("MARATHON_MASTER_URL",
                                                        'http://192.168.0.100:8080')
# Marathon application group. These needs to be unique per a cluster so if you have multiple users deploying clusters
# make sure they choose their own application group.
group = group.format(username=user, profile=profile)
group = group if group.endswith('/') else group + '/'

c.MarathonLauncher.marathon_app_group = group

# Resonable defaults
c.IPClusterStart.controller_launcher_class = 'ipyparallel_mesos.launcher.MarathonControllerLauncher'
c.IPClusterEngines.engine_launcher_class = 'ipyparallel_mesos.launcher.MarathonEngineSetLauncher'

# Docker container image for the controller
c.MarathonLauncher.controller_docker_image = \
    os.environ.get("IPYPARALLEL_CONTROLLER_DOCKER_IMAGE_" + profile.upper()) or \
    os.environ.get("IPYPARALLEL_CONTROLLER_DOCKER_IMAGE") or \
    'registry.fxdayu.com/ipyparallel-marathon-controller:1.0'
# Docker image for the engine. This is where you should install custom dependencies
c.MarathonLauncher.engine_docker_image = \
    os.environ.get("IPYPARALLEL_ENGINE_DOCKER_IMAGE_" + profile.upper()) or \
    os.environ.get("IPYPARALLEL_ENGINE_DOCKER_IMAGE") or \
    'registry.fxdayu.com/ipyparallel-marathon-engine:1.0'

# Optional Amount of memory (in megabytes) to limit the docker container. NOTE: if your engine uses more the this,
# the docker container will be killed by the kernel without warning.
c.MarathonLauncher.engine_memory = int(os.environ.get("IPYPARALLEL_ENGINE_MEMORY", 1024))
# Amount of memory (in megabytes) to limit the docker container. NOTE: if your engine uses more the this, the docker
# container will be killed by the kernel without warning.
c.MarathonLauncher.controller_memory = int(os.environ.get("IPYPARALLEL_CONTROLLER_MEMORY", 512))
# The port the controller exposes for clients and engines to retrive connection information. Note, if there are
# multiple users on the same cluster this will need to be changed
c.MarathonLauncher.controller_config_port = '1235'

c.MarathonLauncher.engine_docker_env_keep.extend([
    "CONDA_ENVS_PATH",
    "CONDA_DEFAULT_ENV",
    "USER",
    "USER_ID",
])

if home:
    c.MarathonLauncher.engine_docker_volumes.append("%s:%s" % (os.path.join(home, user), os.path.join("/home", user)))
