import subprocess

import click


@click.command()
@click.argument("app", default="")
def cli(app):
    """
    Make new database migrations

    :param app: app to make migrations for
    :return: Subprocess call result
    """
    cmd = f'docker-compose run --rm app sh -c "python manage.py makemigrations {app}"'
    return subprocess.call(cmd, shell=True)
