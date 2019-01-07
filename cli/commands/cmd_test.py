import subprocess

import click


@click.command()
def cli():
    """
    Run a test coverage report.

    :param path: Test coverage path
    :return: Subprocess call result
    """
    cmd = 'docker-compose run --rm app sh -c "python manage.py test && flake8"'
    return subprocess.call(cmd, shell=True)
