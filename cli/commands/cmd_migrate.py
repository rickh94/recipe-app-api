import subprocess

import click


@click.command()
def cli():
    """
    Migrate the database

    :return: Subprocess call result
    """
    cmd = f'docker-compose run --rm app sh -c "python manage.py migrate"'
    return subprocess.call(cmd, shell=True)
