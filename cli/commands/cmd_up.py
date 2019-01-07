import subprocess

import click


@click.command()
def cli():
    """
    Start the docker container

    :return: Subprocess call result
    """
    cmd = "docker-compose up -d"
    return subprocess.call(cmd, shell=True)
