import subprocess

import click


@click.command()
@click.option("-v", "--verbose", is_flag=True)
def cli(verbose):
    """
    Run tests

    :return: Subprocess call result
    """
    dash_v = "-v" if verbose else ""
    cmd = (
        "docker-compose run --rm app sh"
        f' -c "pytest {dash_v} --disable-pytest-warnings && flake8"'
    )
    return subprocess.call(cmd, shell=True)
