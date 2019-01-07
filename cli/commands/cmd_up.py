import subprocess

import click


@click.command()
def cli():
    """
    Run a test coverage report.

    :param path: Test coverage path
    :return: Subprocess call result
    """
    cmd = "docker-compose up -d"
    return subprocess.call(cmd, shell=True)
