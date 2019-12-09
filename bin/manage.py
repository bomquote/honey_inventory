import click
import os
from app.models.skus import ProductSku
from app.models.inventory import Warehouse, InventoryLocation, SkuLocationAssoc
from app.models.skus import SkuOwner, Container, ProductSku, SkuAttribute
from app.database import session

@click.group()
def inv():
    pass

@inv.command()
@click.option("--name", prompt="Enter new warehouse name", help="Create a warehouse.")
def create_warehouse(name):
    """Create a warehouse, where a warehouse is a container for inventory locations."""
    Warehouse.create(name=name)
    print(f'Created warehouse {name}')

@inv.command()
@click.option("--name", prompt="Enter warehouse name to delete", help="Delete a warehouse.")
def delete_warehouse(name):
    """Create a warehouse, where a warehouse is a container for inventory locations."""
    wh = session.query(Warehouse).filter_by(name=name).first()
    if not wh:
        return print('Warehouse not found.')
    Warehouse.delete(wh)
    return print(f'Deleted warehouse {name}.')

def last_active_warehouse():
    """Returns the name last active warehouse in the DB."""
    wh = session.query(Warehouse).order_by()

@inv.command()
@click.option("--warehouse", prompt="Enter new inventory location warehouse name", help="Select warehouse.")
def create_location(name):
    """Create a warehouse, where a warehouse is a container for inventory locations."""
    Warehouse.create(name=name)
    print(f'Created warehouse {name}')

@inv.command()
@click.option("--name", prompt="Enter warehouse name to delete", help="Delete a warehouse.")
def delete_location(name):
    """Create a warehouse, where a warehouse is a container for inventory locations."""
    wh = session.query(Warehouse).filter_by(name=name).first()
    if not wh:
        return print('Warehouse not found.')
    Warehouse.delete(wh)
    return print(f'Deleted warehouse {name}.')


@inv.command()
@click.option("--count", default=1, help="Number of repeats.")
@click.option("--name", prompt="Your Name", help="Name of the person scanning.")
def scan_processor(count, name):
    """Scan a UCC code and do something with it."""
    while True:
        ucc = input('Scan a UCC: ')
        ucc = ucc.lower().strip().replace('\t', '').replace('\n', '')
        for _ in range(count):
            print(f'You scanned {ucc}')


if __name__ == "__main__":
    inv()
