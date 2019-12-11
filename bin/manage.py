import click
import os
from honey.models.skus import ProductSku
from honey.models import (Warehouse, InventoryLocation, SkuLocationAssoc, SkuOwner,
                        Container, ProductSku, SkuAttribute)

from honey.core.database import session

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
            return print('Delete cancelled due to bad transfer label')
        else:
            return print('Delete cancelled due to unhandled inventory transfer.')
    # InventoryLocation.create(label=label, warehouse_id=wh.id)
    if original_location:
        print(f"Deleted location {original_location}.")
        return original_location.delete()
    return print(f"Location does not exist so nothing was deleted.")


@inv.command()
@click.option("--original_warehouse",
              prompt="Enter the original warehouse name",
              default="Garage", help="Select warehouse.")
@click.option("--original_label", prompt="Enter the original inventory location label",
              default="Required", help="Provide the location label.")
def transfer_location(original_warehouse, original_label):
    """
    Transfer all of the inventory registered in an original location to a new or
    existing location.
    """
    if original_label == 'Required':
        return print("You must provide a location label.")
    wh = session.query(Warehouse).filter_by(name=original_warehouse).first()
    if not wh:
        return print(
            f"The {original_warehouse} warehouse doesn't exist. Please create it first.")
    original_location = session.query(InventoryLocation).filter(
        InventoryLocation.label == original_label,
        InventoryLocation.warehouse_id == wh.id).first()
    if original_location and original_location.skus:
        print(f"The following skus exist in the location: "
                     f"{[(inst.sku.sku, str(inst.quantity)+' pcs') for inst in original_location.skus]}")
        answer = input('Shall we transfer all of the inventory at the location [Yes]? ') or "Yes"
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
                    return print(f'Transferred inventory to {transfer_location}')
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
                        return print(
                            f'Transferred inventory to {transfer_location} and deleted {original_location}')
            return print('Transfer cancelled due to bad transfer label.')
        else:
            return print("This method only transfers all the SKU's from one location "
                         "to another. Use `transfer-skus` to manage individual SKU's.")
    # InventoryLocation.create(label=label, warehouse_id=wh.id)
    if original_location:
        return print(f"Location {original_location} has no inventory to transfer.")
    return print(f"Location <InventoryLocation ('{original_label}', '{original_warehouse}')> does not exist.")


@inv.command()
@click.option("--original_warehouse",
              prompt="Enter the original warehouse name",
              default="Garage", help="Select warehouse.")
@click.option("--original_label", prompt="Enter the original inventory location label",
              default="Required", help="Provide the location label.")
def transfer_sku(original_warehouse, original_label):
    if original_label == 'Required':
        return print("You must provide a location label.")
    wh = session.query(Warehouse).filter_by(name=original_warehouse).first()
    if not wh:
        return print(
            f"The {original_warehouse} warehouse doesn't exist. Please create it first.")
    original_location = session.query(InventoryLocation).filter(
        InventoryLocation.label == original_label,
        InventoryLocation.warehouse_id == wh.id).first()
    if original_location and original_location.skus:
        original_loc_sku_id_list = [inst.sku.id for inst in original_location.skus]
        print(f"The following skus exist in the location: "
                     f"{[(inst.sku.sku, str(inst.quantity)+' pcs') for inst in original_location.skus]}")
        answer = input("Shall we transfer a SKU of inventory at the location [Yes]? ") or "Yes"
        if answer.lower() == 'yes':
            target_sku = input("Enter the SKU to transfer [Required]: ") or 'Required'
            target_sku_obj = session.query(ProductSku).filter_by(sku=target_sku).first()
            if not target_sku_obj:
                return print('Invalid target SKU. Transfer cancelled.')
            if target_sku_obj.id not in original_loc_sku_id_list:
                return print('Target SKU not in location. Transfer cancelled.')
            transfer_warehouse = input(
                'Enter the warehouse name for the transfer [Garage]: ') or 'Garage'
            transfer_warehouse_obj = session.query(Warehouse).filter_by(
                name=transfer_warehouse).first()
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
                    # transfer the target SKU from original location to the new location
                    for inst in original_location.skus:
                        if inst.sku.id == target_sku_obj.id:
                            inst.update(location_id=transfer_location.id)
                    return print(f'Transferred {target_sku_obj.sku} to {transfer_location}')
                else:
                    create_new_label = input(
                        f"The label {transfer_label} doesn't exist at the {transfer_warehouse_obj.name} warehouse. Create it now and transfer? [Yes]: ") or 'Yes'
                    if create_new_label == "Yes":
                        InventoryLocation.create(
                            label=transfer_label,
                            warehouse_id=transfer_warehouse_obj.id)
                        print(
                            f"Created the new inventory location with label {transfer_label}")
                        transfer_location = session.query(InventoryLocation).filter(
                            InventoryLocation.label == transfer_label,
                            InventoryLocation.warehouse_id == transfer_warehouse_obj.id).first()
                        # transfer the target SKU from original location to the new location
                        for inst in original_location.skus:
                            if inst.sku.id == target_sku_obj.id:
                                inst.update(location_id=transfer_location.id)
                        return print(
                            f'Transferred {target_sku_obj.sku} to {transfer_location}')
            return print('Transfer cancelled due to bad transfer label.')
        else:
            return print("This method only transfers individual SKU's from one location "
                         "to another. Use `transfer-location` to transfer all sku's at once.")
    # InventoryLocation.create(label=label, warehouse_id=wh.id)
    if original_location:
        return print(f"Location {original_location} has no inventory to transfer.")
    return print(
        f"Location <InventoryLocation ('{original_label}', '{original_warehouse}')> does not exist.")


@inv.command()
@click.option("--warehouse",
              prompt="Enter the warehouse name",
              default="Garage", help="Select warehouse.")
@click.option("--label", prompt="Enter the inventory location label",
              default="Required", help="Provide the location label.")
def adjust_sku_qty(warehouse, label):
    """
    Adjust a single sku quantity as found in a specific location.
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
        original_loc_sku_id_list = [inst.sku.id for inst in original_location.skus]
        print(f"The following skus exist in the location: "
                     f"{[(inst.sku.sku, str(inst.quantity)+' pcs') for inst in original_location.skus]}")
        target_sku = input(f"Enter the SKU targeted for quantity change [{[inst.sku.sku for inst in original_location.skus][0]}]: ") or f'{[inst.sku.sku for inst in original_location.skus][0]}'
        target_sku_obj = session.query(ProductSku).filter_by(sku=target_sku).first()
        if not target_sku_obj:
            return print('Invalid target SKU. Transaction cancelled.')
        if target_sku_obj.id not in original_loc_sku_id_list:
            return print('Target SKU not in location. Transaction cancelled.')
        # transfer the target SKU from original location to the new location
        update_quantity = input(
            "Enter the updated total quantity for the SKU [Required]: ") or 'Required'
            # return print('Invalid quantity. Transaction Cancelled.')
        try:
            int(update_quantity)
        except ValueError:
            return print(
                f"Transaction cancelled as {update_quantity} is an invalid integer quantity.")
        for inst in original_location.skus:
            if inst.sku.id == target_sku_obj.id:
                if int(update_quantity) == 0:
                    inst.delete()
                else:
                    inst.update(quantity=int(update_quantity))
        return print(f'Updated {target_sku_obj.sku} to quantity {int(update_quantity)}')
    # InventoryLocation.create(label=label, warehouse_id=wh.id)
    if original_location:
        return print(f"Location {original_location} has no SKU's with inventory.")
    return print(
        f"Location <InventoryLocation ('{label}', '{warehouse}')> does not exist.")


@inv.command()
@click.option("--count", default=1, help="Number of repeats.")
@click.option("--name", prompt="Your Name", help="Name of the person scanning.")
def scan_location(count, name):
    """Scan a UCC code and do something with it."""
    while True:
        ucc = input('Scan a UCC: ')
        ucc = ucc.lower().strip().replace('\t', '').replace('\n', '')
        for _ in range(count):
            print(f'You scanned {ucc}')


if __name__ == "__main__":
    inv()
