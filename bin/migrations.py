"""
This module is the entrypoint for alembic migrations
"""

import click
import os
from alembic import config as alembic_config


@click.group()
def db():
    pass


@db.command()
@click.option("--identifier", prompt="Revision identifier", default='head', help="The revision identifier to target.")
def migratedb(identifier):
    """Migrate the db."""
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    alembic_config.main(argv=['upgrade', f'{identifier}'])

@db.command()
@click.option("--message", prompt="Revision message", help="New revision.")
def revision(message):
    """Create a revision. If you use this then you will need to manually
    edit the upgrade/downgrade methods in the py file created in
    alembic/versions/<file>.py"""
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    alembic_config.main(argv=['revision', f'-m "{message}"'])

@db.command()
def dropdb():
    click.echo('Dropped the database')


if __name__ == "__main__":
    db()