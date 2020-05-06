from cement import Controller, ex
from honey.models.inventory import Warehouse
from honey.models.skus import SkuOwner
from honey.core.exc import HoneyError
from tabulate import tabulate
import sys


class WarehouseController(Controller):
    class Meta:
        label = 'warehouse'
        stacked_type = 'nested'
        stacked_on = 'base'

    @ex(help='list warehouses')
    def list(self):
        """
        Render the warehouse table id's and names.

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
        warehouses = self.app.session.query(Warehouse).all()
        # for tabulate
        headers = [['#', 'id', 'name']]
        data = []
        count = 0
        for record in warehouses:
            count += 1
            data.append([count, record.id, record.name])
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
                headers = headers[0]
                self.app.render(data, headers=headers, tablefmt="grid")
        except AttributeError:
            sys.stdout.write(tabulate(data, headers="firstrow", tablefmt="grid"))


    @ex(
        help='create new warehouse',
        arguments=[
            (['name'],
             {'help': 'honey warehouse create <name>',
              'action': 'store'}),
            (['-i', '--owner_identifier'],
             {'help': 'owner identifier (a name or id)',
              'action': 'store',
              'dest': 'owner_id'})
        ],
    )
    def create(self):
        name = self.app.pargs.name
        identifier = self.app.pargs.owner_id
        if identifier and identifier.isnumeric():
            owner_obj = self.app.session.query(SkuOwner).filter(
                SkuOwner.id == identifier).first()
        else:
            owner_obj = self.app.session.query(SkuOwner).filter(
                SkuOwner.name == identifier).first()
        if owner_obj:
            self.app.log.info(f'creating new warehouse: name={name}, '
                              f'owner={owner_obj.name}')
            new_warehouse = Warehouse(name=name, owner_id=owner_obj.id)

            self.app.session.add(new_warehouse)
            self.app.session.commit()
        else:
            raise HoneyError(
                'provide a warehouse owner with the -i or --owner_identifier flag')

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
        if self.app.pargs.identifier.isnumeric():
            wh_id = int(self.app.pargs.identifier)
            wh_obj = self.app.session.query(Warehouse.id == wh_id).first()
        else:
            wh_obj = self.app.session.query(
                Warehouse).filter_by(name=self.app.pargs.identifier).first()
        if wh_obj:
            name = self.app.pargs.new_name
            if not name:
                raise HoneyError(f"Warehouse name can't be null")
            self.app.log.info(f"updating warehouse name from '{wh_obj.name}' to '{name}'")
            wh_obj.update(name=name)
        else:
            self.app.log.info(
                f"No warehouse with the identifier {self.app.pargs.identifier} exists.")

    @ex(
        help='delete a warehouse',
        arguments=[
            (['warehouse_id'],
             {'help': 'warehouse database id',
              'action': 'store'}),
        ],
    )
    def delete(self):
        id = int(self.app.pargs.warehouse_id)
        wh_obj = Warehouse.get_by_id(id)
        if wh_obj:
            self.app.log.info(f"deleting the warehouse '{wh_obj.name}' with id='{id}'")
            return wh_obj.delete()
        else:
            self.app.log.info(f"A warehouse with id='{id}' does not exist.")

    @ex(
        help='set active warehouse',
        arguments=[
            (['identifier'],
             {'help': 'warehouse database name or id',
              'action': 'store'})
        ],
        )
    def activate(self):
        wh_cache_key = self.app.config.get('honey', 'WAREHOUSE_CACHE_KEY')
        if self.app.pargs.identifier.isnumeric():
            wh_id = int(self.app.pargs.identifier)
            wh_obj = Warehouse.get_by_id(wh_id)
        else:
            wh_obj = self.app.session.query(
                Warehouse).filter_by(name=self.app.pargs.identifier).first()
        if wh_obj:
            self.deactivate()
            # todo: use a config instead of hard coding the cache key
            self.app.cache.set(wh_cache_key, wh_obj.name)
            self.app.log.info(f"Activating warehouse '{wh_obj.name}' with id='{wh_obj.id}'.")
        else:
            self.app.log.info(
                f"A warehouse with the identifier {self.app.pargs.identifier} does not exist.")

    @ex(
        help='clear active warehouse'
    )
    def deactivate(self):
        wh_cache_key = self.app.config.get('honey', 'WAREHOUSE_CACHE_KEY')
        active_warehouse = self.app.cache.get(wh_cache_key)
        if active_warehouse:
            self.app.log.info(f"Deactivated warehouse '{active_warehouse}'.")
            self.app.cache.delete(wh_cache_key)
        else:
            self.app.log.info(f"No active warehouse.")