from cement import Controller, ex
from honey.core.database import session
from honey.models.inventory import Warehouse, InventoryLocation, SkuLocationAssoc
from tabulate import tabulate


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
        warehouses = session.query(Warehouse).all()
        # for tabulate
        data = [['#', 'id', 'name']]
        count = 0
        for record in warehouses:
            count += 1
            data.append([count, record.id, record.name])
        print(tabulate(data, headers="firstrow", tablefmt="grid"))

    @ex(
        help='create new warehouse',
        arguments=[
            (['name'],
             {'help': 'honey warehouse create <name>',
              'action': 'store'})
        ],
    )
    def create(self):
        name = self.app.pargs.name
        # now = strftime("%Y-%m-%d %H:%M:%S")
        self.app.log.info(f'creating new warehouse: {name}')
        Warehouse.create(name=name)

    @ex(
        help='update a warehouse name to newname',
        arguments=[
            (['warehouse_id'],
             {'help': 'warehouse database id',
              'action': 'store'}),
            (['--name'],
             {'help': 'updated warehouse name',
              'action': 'store',
              'dest': 'new_name'})
        ],
    )
    def update(self):
        """
        Update the warehouse name.

        usage: honey warehouse uu <id> --name <newname>

        """
        id = int(self.app.pargs.warehouse_id)
        name = self.app.pargs.new_name
        # wh_obj = session.query(Warehouse).filter_by(name=name).first()
        wh_obj = Warehouse.get_by_id(id)
        self.app.log.info(f"updating warehouse name from '{wh_obj.name}' to '{name}'")
        wh_obj.update(name=name)

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
            (['wh_name_or_id'],
             {'help': 'warehouse database name or id',
              'action': 'store'})
        ],
        )
    def activate(self):
        if self.app.pargs.wh_name_or_id.isnumeric():
            id = int(self.app.pargs.wh_name_or_id)
            wh_obj = Warehouse.get_by_id(id)
        else:
            wh_obj = session.query(
                Warehouse).filter_by(name=self.app.pargs.wh_name_or_id).first()
        if wh_obj:
            self.deactivate()
            self.app.cache.set(f'honey-active_warehouse', wh_obj.name)
            self.app.log.info(f"Activating warehouse '{wh_obj.name}' with id='{wh_obj.id}'.")
        else:
            self.app.log.info(
                f"A warehouse with the identifier {self.app.pargs.wh_name_or_id} does not exist.")

    @ex(
        help='clear active warehouse'
    )
    def deactivate(self):
        active_warehouse = self.app.cache.get('honey-active_warehouse')
        if active_warehouse:
            self.app.log.info(f"Deactivated warehouse '{active_warehouse}'.")
            self.app.cache.delete(f'honey-active_warehouse')
        else:
            self.app.log.info(f"No active warehouse.")