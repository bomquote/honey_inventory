from cement import Controller, ex
from honey.models.inventory import Warehouse
from honey.models.entities import Entity
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
        headers = ['#', 'id', 'name', 'entity']
        data = []
        count = 0
        for record in warehouses:
            count += 1
            data.append([count, record.id, record.name, record.entity.name])
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
        help='create new warehouse',
        arguments=[
            (['name'],
             {'help': 'honey warehouse create <name>',
              'action': 'store'}),
            (['-e', '--entity'],
             {'help': 'entity identifier (an entity name or entity id)',
              'action': 'store',
              'dest': 'entity_id'})
        ],
    )
    def create(self):
        name = self.app.pargs.name
        identifier = self.app.pargs.entity_id
        if any((name is None, identifier is None)):
            raise HoneyError("You must provide a warehouse name and entity identifier")
        if identifier and identifier.isnumeric():
            owner_obj = self.app.session.query(Entity).filter(
                Entity.id == identifier).first()
        else:
            owner_obj = self.app.session.query(Entity).filter(
                Entity.name == identifier).first()
        if owner_obj:
            self.app.log.info(f'creating new warehouse: name={name}, '
                              f'owner={owner_obj.name}')
            new_warehouse = Warehouse(name=name, entity_id=owner_obj.id)

            self.app.session.add(new_warehouse)
            self.app.session.commit()
        else:
            raise HoneyError(
                'provide a warehouse owner with the -e or --entity_identifier flag')

    @ex(
        help='update a warehouse name to new name',
        arguments=[
            (['identifier'],
             {'help': 'warehouse database name or id',
              'action': 'store'}),
            (['-e', '--entity'],
             {'help': 'entity identifier (an entity name or entity id)',
              'action': 'store',
              'dest': 'entity_id'}),
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
        usage: honey warehouse update <identifier> -e <entity identifier> -n <new name>

        """
        wh_identifier = self.app.pargs.identifier
        ent_identifier = self.app.pargs.entity_id
        new_name = self.app.pargs.new_name
        if wh_identifier is None:
            raise HoneyError("Please provide a warehouse identifier")
        if new_name is None:
            raise HoneyError("Provide a new warehouse name with the -n or --name flag")
        #if any((wh_identifier is None, ent_identifier is None)):
        #    raise HoneyError(
        #        "You must provide a warehouse identifier, entity identifier, "
        #        "and an updated warehouse name")
        if wh_identifier.isnumeric():
            wh_id = int(wh_identifier)
            wh_obj = self.app.session.query(Warehouse).filter(
                Warehouse.id == wh_id).first()
        else:
            # check, if more than one wh_obj with the same name, must include entity
            wh_obj = self.app.session.query(
                Warehouse).filter_by(name=wh_identifier).all()
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
                # do the update here to avoid if/else hell
                # update by assignment
                self.app.log.info(
                    f"updated warehouse name from '{wh_obj.name}' to '{new_name}'")
                wh_obj.name = new_name
                return self.app.session.commit()
            # because you queried Warehouse with `all()` the wh_obj is probably a list
            elif all((type(wh_obj) == list, len(wh_obj) == 1)):
                wh_obj = wh_obj[0]
        if all((wh_obj, wh_identifier.isnumeric())):
            self.app.log.info(
                f"updated warehouse name from '{wh_obj.name}' to '{new_name}'")
            wh_obj.name = new_name
            return self.app.session.commit()
        else:
            return self.app.log.info(
                f"No warehouse with the identifier {wh_identifier} exists.")

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
        try:
            if self.app.__test__:
                wh_cache_key = self.app.config.get('honeytest', 'WAREHOUSE_CACHE_KEY')
        except AttributeError:
            wh_cache_key = self.app.config.get('honey', 'WAREHOUSE_CACHE_KEY')
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
        try:
            if self.app.__test__:
                wh_cache_key = self.app.config.get('honeytest', 'WAREHOUSE_CACHE_KEY')
        except AttributeError:
            wh_cache_key = self.app.config.get('honey', 'WAREHOUSE_CACHE_KEY')
        active_warehouse = self.app.cache.get(wh_cache_key)
        if active_warehouse:
            self.app.log.info(f"Deactivated warehouse '{active_warehouse}'.")
            self.app.cache.delete(wh_cache_key)
        else:
            self.app.log.info(f"No active warehouse.")