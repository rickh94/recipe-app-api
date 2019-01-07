import subprocess

import click


@click.command()
@click.argument("app", default="")
def cli(app):
    """
    Run a test coverage report.

    :param path: Test coverage path
    :return: Subprocess call result
    """
    cmd = f'docker-compose run --rm app sh -c "python manage.py makemigrations {app}"'
    return subprocess.call(cmd, shell=True)
