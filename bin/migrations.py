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
def migratedb():
    """Migrate the db."""
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    alembic_config.main(argv=['upgrade', 'head'])


@db.command()
def dropdb():
    click.echo('Dropped the database')


if __name__ == "__main__":
    db()