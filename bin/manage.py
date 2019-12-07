import click
from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/hgdb')


@click.command()
@click.option("--count", default=1, help="Number of repeats.")
@click.option("--name", prompt="Your Name", help="Name of the person scanning.")
def scan_processor(count, name):
    """Scan a UCC code and do something with it."""
    while True:
        ucc = input('Scan a UCC: ')
        ucc = ucc.lower().strip().replace('\t', '').replace('\n', '')
        for _ in range(count):
            print(f'You scanned {ucc}')


@click.group()
def scan():
    pass

scan.add_command(scan_processor)
# scan.add_command(dropdb)

if __name__ == "__main__":

    scan_processor()