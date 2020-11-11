from cement import Controller, ex
from honey.core.database import session
from honey.models.inventory import Warehouse, InventoryLocation, LocationSkuAssoc
from honey.models.skus import ProductSku
from honey.models.entities import Entity
from honey.core.exc import HoneyError
from tabulate import tabulate
import sys


class InventoryActionController(Controller):
    class Meta:
        label = 'invact'
        stacked_type = 'nested'
        stacked_on = 'base'

    @ex(
        help='Scan inventory at an inventory location at a warehouse',
        arguments=[
            (['label'],
             {'help': 'honey invloc scan <name> -a <action> -wh <warehouse> -e <entity>',
              'action': 'store'}),
            (['-a', '--action'],
             {'help': 'action to take (increase, decrease)',
              'action': 'store',
              'dest': 'action'}),
            (['-c', '--count'],
             {'default': 1,
              'help': 'number of repeats',
              'action': 'store',
              'dest': 'count'}),
            (['-w', '--warehouse'],
             {'help': 'warehouse identifier (a name or id)',
              'action': 'store',
              'dest': 'wh_id'}),
            (['-e', '--entity'],
             {'help': 'warehouse owner entity (a name or id)',
              'action': 'store',
              'dest': 'entity_id'}),
        ],
    )
    def scan(self):
        """
        Scan inventory in a specific location, where location is a labeled container
        holding inventory at a named unique Warehouse/Entity combination
        """
        label = self.app.pargs.label
        action = self.app.pargs.action
        count = int(self.app.pargs.count)
        ent_identifier = self.app.pargs.entity_id
        if not label:
            raise HoneyError('you must provide an inventory location label')
        wh_identifier = self.app.pargs.wh_id
        if wh_identifier and wh_identifier.isnumeric():
            wh_obj = self.app.session.query(Warehouse).filter(
                Warehouse.id == wh_identifier).first()
        else:
            wh_obj = self.app.session.query(Warehouse).filter(
                Warehouse.name == wh_identifier).all()
            # check if more than one wh_obj with the same name, must include entity
            ent_obj = None
            if all((wh_obj, len(wh_obj) > 1)):
                # find the entity if it exists
                if ent_identifier and ent_identifier.isnumeric():
                    ent_obj = self.app.session.query(Entity).filter_by(
                        id=ent_identifier).first()
                elif ent_identifier:
                    ent_obj = self.app.session.query(Entity).filter_by(
                        name=ent_identifier).first()
                if not ent_obj:
                    raise HoneyError(
                        'No Entity exists with the provided identifier')
                wh_obj = self.app.session.query(Warehouse).filter(
                    Warehouse.name == wh_identifier,
                    Warehouse.entity_id == ent_obj.id
                ).first()
            # because you queried Warehouse with `all()` the wh_obj is probably a list
            elif all((type(wh_obj) == list, len(wh_obj) == 1)):
                wh_obj = wh_obj[0]
        if not wh_obj:
            message = f'The warehouse identifier does not exist. ' \
                      f'Using the active warehouse from cache.'
            # check the cache for an active warehouse
            wh_obj = Warehouse.get_active_warehouse(self.app)
            if not wh_obj:
                raise HoneyError(
                    'The warehouse does not exist. Please set an active '
                    'warehouse or use the flags to designate an existing warehouse')
            self.app.log.info(message)
        location_obj = session.query(InventoryLocation).filter(
            InventoryLocation.label == label,
            InventoryLocation.warehouse_id == wh_obj.id).first()
        if not location_obj:
            raise HoneyError(
                f"The label {label} does not exist in the {wh_obj.name} warehouse.")
        self.app.log.info(f'{action} inventory at location: label={label}, '
                          f'warehouse={wh_obj.name}')
        while True:
            ucc = input('Scan a UCC: ')
            ucc = ucc.lower().strip().replace('\t', '').replace('\n', '')
            if ucc.lower == 'exit':
                break
            # lookup the UCC to get the sku
            sku_obj = self.app.session.query(ProductSku).filter(
                ProductSku.upc == ucc).first()
            if not sku_obj:
                self.app.log.info(f'command {ucc} not recognized.')
                break
            loc_assoc_obj = self.app.session.query(LocationSkuAssoc).filter(
                LocationSkuAssoc.sku_id == sku_obj.id,
                LocationSkuAssoc.location_id == location_obj.id).first()

            for _ in range(count):
                if action.lower() == 'increase':
                    self.app.log.info(f'You scanned {ucc} with + action {action}. This is a {sku_obj.description}')
                    # does the association table object exist? If not then create it.
                    if loc_assoc_obj:
                        last_qty = loc_assoc_obj.quantity
                        loc_assoc_obj.quantity = last_qty+1
                    else:
                        new_record = LocationSkuAssoc(sku_obj.id, location_obj.id, quantity=1)
                        self.app.session.add(new_record)
                elif action.lower() == 'decrease':
                    self.app.log.info(f'You scanned {ucc} with - action {action}. This is a {sku_obj.description}')
                    if loc_assoc_obj:
                        last_qty = loc_assoc_obj.quantity
                        if last_qty-1 == 0:
                            self.app.session.delete(loc_assoc_obj)
                        else:
                            loc_assoc_obj.quantity = last_qty-1
                    else:
                        self.app.log.warning(f'No quantity of {sku_obj.sku} exists in {location_obj.label}.')
                else:
                    raise HoneyError(f'The action {action} does not exist.')
            self.app.session.commit()
        return self.app.log.info(f'Scan completed.')

    @ex(help='just run a query -> honey invact testquery')
    def testquery(self):

        sku_obj = self.app.session.query(ProductSku).filter(
            ProductSku.sku == 'A2-B-M').first()

        print(f'sku_obj.location -> {sku_obj.location}')
        print(f'sku_obj.locations -> {sku_obj.locations}')
        print(f'sku_obj.quantity -> {sku_obj.quantity}')
        # print(sku_obj.description)