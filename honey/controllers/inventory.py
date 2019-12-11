from cement import Controller, ex
from time import strftime
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
        Render the table id and name.
        Looks like below:
        warehouses =
        [<Warehouse Garage>, <Warehouse Office>, <Warehouse Kitchen>, <Warehouse Bathroom>]

        {'result': {'1': 'Garage', '2': 'Office', '6': 'Kitchen', '7': 'Bathroom'}}
        :return:
        """
        warehouses = session.query(Warehouse).all()
        # for jinja2 template
        # wh = {}
        # for wh_obj in warehouses:
        #     wh[wh_obj.id] = wh_obj.name
        # data = {"result": wh}
        # self.app.render(data, 'inventory/warehouses/list.jinja2')

        # for tabulate
        data = [['#', 'id', 'name']]
        count = 0
        for record in warehouses:
            count += 1
            data.append([count, record.id, record.name])
        print(tabulate(data, headers="firstrow"))

    @ex(
        help='create new warehouse',
        arguments=[
            (['name'],
             {'help': 'honey warehouse name',
              'action': 'store'})
        ],
    )
    def create(self):
        name = self.app.pargs.name
        # now = strftime("%Y-%m-%d %H:%M:%S")
        self.app.log.info(f'creating new warehouse: {name}')
        Warehouse.create(name=name)

    @ex(help='update an existing warehouse')
    def update(self):
        pass

    @ex(help='delete a warehouse')
    def delete(self):
        pass

    @ex(help='set active warehouse')
    def set(self):
        pass