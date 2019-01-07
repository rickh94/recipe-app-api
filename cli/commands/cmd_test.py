import subprocess

import click


@click.command()
def cli():
    """
    Run tests

    :return: Subprocess call result
    """
    cmd = (
        'docker-compose run --rm app sh -c "pytest --disable-pytest-warnings && flake8"'
    )
    return subprocess.call(cmd, shell=True)
