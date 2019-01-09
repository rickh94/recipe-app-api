import subprocess

import click


@click.command()
def cli():
    """
    Rebuild the docker container

    :return: Subprocess call result
    """
    cmd = "docker-compose down && docker-compose build"
    return subprocess.call(cmd, shell=True)
