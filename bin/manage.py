import click
import os
from app.models.skus import ProductSku
from app.models import (Warehouse, InventoryLocation, SkuLocationAssoc, SkuOwner,
                        Container, ProductSku, SkuAttribute)
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
    """Create a location, where location is a labeled container holding inventory."""
    if label == 'Required':
        return print("You must provide a new location label.")
    wh = session.query(Warehouse).filter_by(name=warehouse).first()
    if not wh:
        return print(
            f"The {warehouse} warehouse doesn't exist. Please create it first.")
    record = session.query(InventoryLocation).filter(
        InventoryLocation.label == label,
        InventoryLocation.warehouse_id == wh.id).first()
    if record:
        return print(f"The label {label} already exists in the {warehouse} warehouse.")
    InventoryLocation.create(label=label, warehouse_id=wh.id)
    # todo: set the new location to the "active" location (enable an active location)
    return print(f'Created new location.')


@inv.command()
@click.option("--warehouse",
              prompt="Warehouse where location should be deleted",
              default="Garage", help="Select warehouse.")
@click.option("--label", prompt="Enter the inventory location label",
              default="Required", help="Provide the location label.")
def delete_location(label, warehouse):
    """
    Delete a location. If the location contains inventory then offer to transfer
    the inventory to a new or existing location.
    todo: if the location has inventory associated with it, ask the user if they would
        like to transfer the inventory to a new or existing location
    would like to transfer the inventory to a new inventory location.
    """
    if label == 'Required':
        return print("You must provide a location label.")
    wh = session.query(Warehouse).filter_by(name=warehouse).first()
    if not wh:
        return print(
            f"The {warehouse} warehouse doesn't exist. Please create it first.")
    original_location = session.query(InventoryLocation).filter(
        InventoryLocation.label == label,
        InventoryLocation.warehouse_id == wh.id).first()
    if original_location and original_location.skus:
        print(f"The following skus exist in the location: "
                     f"{[(inst.sku.sku, str(inst.quantity)+' pcs') for inst in original_location.skus]}")
        answer = input('Shall we transfer the inventory location [Yes]? ') or "Yes"
        if answer.lower() == 'yes':
            transfer_warehouse = input('Enter the warehouse name for the transfer [Garage]: ') or 'Garage'
            transfer_warehouse_obj = session.query(Warehouse).filter_by(name=transfer_warehouse).first()
            if not transfer_warehouse_obj:
                return print(
                    f"The {transfer_warehouse} warehouse doesn't exist. "
                    f"Please create it first using `create_warehouse`.")
            def transf():
                """Use this to give two attempts to enter the label."""
                return input('Enter the transfer label [Required]: ') or None
            transfer_label = transf()
            if not transfer_label:
                # user error, assign and run it again
                transfer_label = transf()
            if transfer_label:
                # search to see if the warehouse/label location exists.
                transfer_location = session.query(InventoryLocation).filter(
                    InventoryLocation.label == transfer_label,
                    InventoryLocation.warehouse_id == transfer_warehouse_obj.id).first()
                if transfer_location:
                    # transfer the inventory from original location to the new location
                    for inst in original_location.skus:
                        inst.update(location_id=transfer_location.id)
                    print(f'Transferred inventory to {transfer_location} and deleted {original_location}')
                    return original_location.delete()
                else:
                    create_new_label = input(
                        f"The label {transfer_label} doesn't exist at the {transfer_warehouse_obj.name} warehouse. Create it now and transfer? [Yes]: ") or 'Yes'
                    if create_new_label == "Yes":
                        InventoryLocation.create(
                            label=transfer_label,
                            warehouse_id=transfer_warehouse_obj.id)
                        print(f"Created the new inventory location with label {transfer_label}")
                        transfer_location = session.query(InventoryLocation).filter(
                            InventoryLocation.label == transfer_label,
                            InventoryLocation.warehouse_id == transfer_warehouse_obj.id).first()
                        # transfer from original location to the new location
                        for inst in original_location.skus:
                            inst.update(location_id=transfer_location.id)
                        print(
                            f'Transferred inventory to {transfer_location} and deleted {original_location}')
                        return original_location.delete()
            return print('Cancelling the delete due to bad transfer label')
        else:
            return print('cascade delete finished.')
    # InventoryLocation.create(label=label, warehouse_id=wh.id)
    if original_location:
        print(f"Deleted location.")
        return original_location.delete()
    return print(f"Location does not exist so nothing was deleted.")


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
