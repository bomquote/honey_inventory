from cement import Controller, ex
from honey.models.entities import Entity
from honey.core.exc import HoneyError
from tabulate import tabulate
import sys


class EntityController(Controller):
    class Meta:
        label = 'entity'
        stacked_type = 'nested'
        stacked_on = 'base'

    @ex(help='list entities')
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
        entities = self.app.session.query(Entity).all()
        # for tabulate
        headers = ['#', 'id', 'name']
        data = []
        count = 0
        for record in entities:
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
                self.app.render(data, headers=headers, tablefmt="grid")
        except AttributeError:
            sys.stdout.write(tabulate(data, headers=headers, tablefmt="grid"))

    @ex(
        help='create new entity',
        arguments=[
            (['name'],
             {'help': 'honey entity create <name>',
              'action': 'store'}),
        ],
    )
    def create(self):
        name = self.app.pargs.name
        entity_obj = self.app.session.query(Entity).filter(
            Entity.name == name).first()
        if entity_obj:
            raise HoneyError('Entity already exists')
        self.app.log.info(f'creating new entity: name={name}')
        new_entity = Entity(name=name)
        self.app.session.add(new_entity)
        self.app.session.commit()
