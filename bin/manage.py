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


@inv.command()
@click.option("--warehouse",
              prompt="Warehouse where location should be created",
              default="Garage", help="Select warehouse.")
@click.option("--label", prompt="Enter a name for the inventory location label",
              default="Required", help="Create a location label.")
def create_location(warehouse, label):
    """Create a warehouse, where a warehouse is a container for inventory locations."""
    if label == 'Required':
        return print("You must provide a new location label.")
    wh = session.query(Warehouse).filter_by(name=warehouse).first()
    if not wh:
        return print(f"The {warehouse} warehouse doesn't exist.")
    record = session.query(InventoryLocation).filter(
        InventoryLocation.label == label,
        InventoryLocation.warehouse_id == wh.id).first()
    if record:
        return print(f"The label {label} alrady exists in the {warehouse} warehouse.")
    print(f'Created location')

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
