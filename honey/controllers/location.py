from cement import Controller, ex
from honey.core.database import session
from honey.models.inventory import Warehouse, InventoryLocation
from honey.models.entities import Entity
from honey.core.exc import HoneyError
from tabulate import tabulate
import sys


class InventoryLocationController(Controller):
    class Meta:
        label = 'invloc'
        stacked_type = 'nested'
        stacked_on = 'base'

    @ex(help='list invloc')
    def list(self):
        """
        Render the inventory_locations table id's and names.

        For jinja2 template output, this works:
        # wh = {}
        # for wh_obj in warehouses:
        #     wh[wh_obj.id] = wh_obj.name
        # data = {"result": wh}
        # self.app.render(data, 'inventory/warehouses/list.jinja2')
               Hint, looks like below:
        warehouses =
        [<Warehouse Garage>, <Warehouse Office>, <Warehouse Kitchen>, <Warehouse Bathroom>]
        {'result': {'1': 'Garage', '2': 'Office', '6': 'Kitchen', '7': 'Bathroom'}}
        """
        inventory_locations = self.app.session.query(InventoryLocation).all()
        # for tabulate
        headers = ['#', 'id', 'label', 'warehouse', 'owner']
        data = []
        count = 0
        for record in inventory_locations:
            count += 1
            data.append([count, record.id, record.label, record.warehouse.name,
                         record.warehouse.owner.name])
        # it appears we need this try block for easiest testing of tabulate data
        # this is mainly because the output_handler = 'jinja2' in the main Honey app
        # while, we want to use tabulate as the output handler in many cases
        # the solution here would be to just get rid of tabulate and make templates...
        # ...but I don't want to deal with it for now so doing it this way
        try:
            # we've set self.app.__test__ to True in the test methods
            # for easy testing we need to use the render method but that would
            # make us have to create a template, if we do that, what good is tabulate?
            if self.app.__test__:
                self.app.render(data, headers=headers, tablefmt="grid")
        except AttributeError:
            sys.stdout.write(tabulate(data, headers=headers, tablefmt="grid"))


    @ex(
        help='Create an inventory location at a warehouse',
        arguments=[
            (['label'],
             {'help': 'honey invloc create <name> -wh <warehouse>',
              'action': 'store'}),
            (['-wh', '--warehouse'],
             {'help': 'warehouse identifier (a name or id)',
              'action': 'store',
              'dest': 'wh_id'}),
        ],
    )
    def create(self):
        """
        Create a location, where location is a labeled container holding inventory
        at a named Warehouse.
        """
        label = self.app.pargs.label
        if not label:
            raise HoneyError('you must provide an inventory location label')
        wh_identifier = self.app.pargs.wh_id
        if wh_identifier and wh_identifier.isnumeric():
            wh_obj = self.app.session.query(Warehouse).filter(
                Warehouse.id == wh_identifier).first()
        else:
            wh_obj = self.app.session.query(Warehouse).filter(
                Warehouse.name == wh_identifier).first()
        if not wh_obj:
            # check the cache for an active warehouse
            wh_obj = Warehouse.get_active_warehouse(self.app)
            if not wh_obj:
                raise HoneyError(
                    'please set an active warehouse or use the -wh or --warehouse '
                    'flag to designate a warehouse')
        record = session.query(InventoryLocation).filter(
            InventoryLocation.label == label,
            InventoryLocation.warehouse_id == wh_obj.id).first()
        if record:
            raise HoneyError(
                f"The label {label} already exists in the {wh_obj.name} warehouse.")
        self.app.log.info(f'creating new inventory location: label={label}, '
                              f'warehouse={wh_obj.name}')
        new_invloc = InventoryLocation(label=label, warehouse_id=wh_obj.id)
        self.app.session.add(new_invloc)
        self.app.session.commit()
        return self.app.log.info(f'Created new location.')

    @ex(
        help='update a warehouse name to new name',
        arguments=[
            (['identifier'],
             {'help': 'warehouse database name or id',
              'action': 'store'}),
            (['-n', '--name'],
             {'help': 'updated warehouse name',
              'action': 'store',
              'dest': 'new_name'})  # I like to use `new_name` to highlight the change
        ],
    )
    def update(self):
        """
        Update the warehouse name:
        identifier: name or id

        usage: honey warehouse update <identifier> --name <newname>

        """
        identifier = self.app.pargs.identifier
        if identifier.isnumeric():
            wh_id = int(identifier)
            wh_obj = self.app.session.query(Warehouse).filter(
                Warehouse.id == wh_id).first()
        else:
            wh_obj = self.app.session.query(
                Warehouse).filter_by(name=identifier).first()
        if wh_obj:
            new_name = self.app.pargs.new_name
            if not new_name:
                raise HoneyError(f"Warehouse name can't be null")
            self.app.log.info(
                f"updating warehouse name from '{wh_obj.name}' to '{new_name}'")
            # update by assignment
            wh_obj.name = new_name
            self.app.session.commit()
        else:
            self.app.log.info(
                f"No warehouse with the identifier {identifier} exists.")

    @ex(
        help='delete a warehouse',
        arguments=[
            (['identifier'],
             {'help': 'warehouse database name or id',
              'action': 'store'}),
        ],
    )
    def delete(self):
        identifier = self.app.pargs.identifier
        if identifier.isnumeric():
            id = int(identifier)
            wh_obj = self.app.session.query(Warehouse).filter_by(id=id).first()
        else:
            wh_obj = self.app.session.query(Warehouse).filter_by(
                name=identifier).first()
        if wh_obj:
            self.app.log.info(
                f"deleting the warehouse '{wh_obj.name}' with id='{wh_obj.id}'")
            return self.app.session.delete(wh_obj)
        else:
            self.app.log.info(
                f"A warehouse with identifier='{identifier}' does not exist.")

    @ex(
        help='set the active warehouse by name or id',
        arguments=[
            (['identifier'],
             {'help': 'honey warehouse activate <identifier>',
              'action': 'store'})
        ],
    )
    def activate(self):
        """
        Sets the active warehouse in redis cache. This cuts down redundant
        commands in managing locations. It assumes the user is issuing
        multiple consecutive commands in working within the same warehouse.
        """
        identifier = self.app.pargs.identifier
        wh_cache_key = self.app.config.get('honey', 'WAREHOUSE_CACHE_KEY')
        if self.app.__test__:
            wh_cache_key = self.app.config.get('honeytest', 'WAREHOUSE_CACHE_KEY')
        if identifier.isnumeric():
            id = int(identifier)
            wh_obj = self.app.session.query(Warehouse).filter_by(id=id).first()
        else:
            wh_obj = self.app.session.query(Warehouse).filter_by(
                name=identifier).first()
        if wh_obj:
            self.deactivate()
            self.app.cache.set(wh_cache_key, wh_obj.name)
            self.app.log.info(
                f"Activating warehouse '{wh_obj.name}' with id='{wh_obj.id}'.")
        else:
            self.app.log.info(
                f"A warehouse with the identifier {identifier} does not exist.")

    @ex(
        help='clear active warehouse'
    )
    def deactivate(self):
        wh_cache_key = self.app.config.get('honey', 'WAREHOUSE_CACHE_KEY')
        if self.app.__test__:
            wh_cache_key = self.app.config.get('honeytest', 'WAREHOUSE_CACHE_KEY')
        active_warehouse = self.app.cache.get(wh_cache_key)
        if active_warehouse:
            self.app.log.info(f"Deactivated warehouse '{active_warehouse}'.")
            self.app.cache.delete(wh_cache_key)
        else:
            self.app.log.info(f"No active warehouse.")