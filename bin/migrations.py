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
def upgrade(identifier):
    """Migrate the db up to the new version. This supports partial revision identifiers
    and relative migration identifiers.
    see:
    https://alembic.sqlalchemy.org/en/latest/tutorial.html#partial-revision-identifiers
    https://alembic.sqlalchemy.org/en/latest/tutorial.html#relative-migration-identifiers
    """
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    alembic_config.main(argv=['upgrade', f'{identifier}'])

@db.command()
@click.option("--identifier", prompt="Revision identifier", default='', help="The revision identifier to target.")
def downgrade(identifier):
    """Migrate the db to a previous version or all the way back to base, using 'base' as
    the revision identifier. This supports partial revision identifiers and relative
    migration identifiers.
    see:
    https://alembic.sqlalchemy.org/en/latest/tutorial.html#partial-revision-identifiers
    https://alembic.sqlalchemy.org/en/latest/tutorial.html#relative-migration-identifiers
    """
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    alembic_config.main(argv=['downgrade', f'{identifier}'])


@db.command()
@click.option("--message", prompt="Revision message", help="New revision.")
@click.option("--autogenerate", prompt="Autogenerate the migration?", default="True",
              help="Create a rudimentary migration automatically.")
def revision(message, autogenerate):
    """Create a revision. If you use this then you will need to manually
    edit the upgrade/downgrade methods in the py file created in
    alembic/versions/<file>.py

    Lot's more functionality not implemented here. See:
    https://alembic.sqlalchemy.org/en/latest/api/commands.html?highlight=stamp#alembic.command.revision
    """
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    if autogenerate == 'True':
        alembic_config.main(argv=['revision', '--autogenerate', f'-m "{message}"'])
    else:
        alembic_config.main(argv=['revision', f'-m "{message}"'])


@db.command()
@click.option("--verbose", prompt="Use Verbose?", default="True", help="Return a verbose info response?")
def current(verbose):
    """Get information about the state of the current revision."""
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    if not verbose == "True":
        alembic_config.main(argv=['current'])
    else:
        alembic_config.main(argv=['current', '--verbose'])


@db.command()
@click.option("--identifier", prompt="Revision identifier", default='head', help="The revision identifier to target.")
def show(identifier):
    """Show the revision(s) denoted by the given symbol. This supports partial revision
    identifiers and relative migration identifiers.
    see:
    https://alembic.sqlalchemy.org/en/latest/api/commands.html?highlight=stamp#alembic.command.show
    """
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    alembic_config.main(argv=['show', f'{identifier}'])


@db.command()
@click.option("--verbose", prompt="Use Verbose?", default="False", help="Return a verbose info response?")
def heads(verbose):
    """Show current available heads in the script directory.
    see:
    https://alembic.sqlalchemy.org/en/latest/api/commands.html?highlight=stamp#alembic.command.heads
    """
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    if verbose == "False":
        alembic_config.main(argv=['heads'])
    else:
        alembic_config.main(argv=['heads', '--verbose'])


@db.command()
@click.option("--identifier", prompt="Revision identifier", default='head', help="The revision identifier to target.")
def stamp(identifier):
    """ ‘stamp’ the revision table with the given revision; don’t run any migrations.
    see:
    https://alembic.sqlalchemy.org/en/latest/api/commands.html?highlight=stamp#alembic.command.stamp
    """
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    alembic_config.main(argv=['stamp', f'{identifier}'])


@db.command()
@click.option("--verbose", prompt="Use Verbose?", default="True", help="Return a verbose info response?")
@click.option("--history_range", prompt="Input a history range?", default="False",
              help="accepts an argument [start]:[end]")
def history(verbose, history_range):
    """Get information about the state of the current revision and it's history.
    Supports viewing history ranges, see:
    https://alembic.sqlalchemy.org/en/latest/tutorial.html#viewing-history-ranges
    """
    os.chdir('C:\\Users\\bjord\\PycharmProjects\\hg_inventory')
    if not verbose == "True":
        if history_range == "False":
            alembic_config.main(argv=['history'])
        else:
            alembic_config.main(argv=['history', f'-r{history_range}'])
    else:
        if not history_range == "False":
            alembic_config.main(argv=['history', '--verbose', f'-r{history_range}'])
        else:
            alembic_config.main(argv=['history', '--verbose'])


@db.command()
def dropdb():
    click.echo('Dropped the database')


if __name__ == "__main__":
    db()