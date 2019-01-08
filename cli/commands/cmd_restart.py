import os
import subprocess

import click


@click.command()
@click.argument("service")
def cli(service):
    """
    Start the docker container

    :return: Subprocess call result
    """

    cmd = f"docker-compose restart {service}"
    return subprocess.call(cmd, shell=True)
