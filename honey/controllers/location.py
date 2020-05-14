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

    # todo: optionally add a warehouse_identifier to filter locations by warehouse
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
                         record.warehouse.entity.name])
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
    def create(self):
        """
        Create a location, where location is a labeled container holding inventory
        at a named unique Warehouse/Entity combination
        """
        label = self.app.pargs.label
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
        help='update an inventory location record label',
        arguments=[
            (['identifier'],
             {'help': 'inventory location identifier, record id or label + warehouse',
              'action': 'store'}),
            (['-n', '--new_label'],
             {'help': 'updated inventory location label',
              'action': 'store',
              'dest': 'new_label'}),
            (['-w', '--warehouse'],
             {'help': 'warehouse identifier, name or id',
              'action': 'store',
              'dest': 'warehouse'}),

        ],
    )
    def update(self):
        """
        Update the warehouse name:
        identifier: name or id

        usage: honey invloc update <label identifier> --new_label <new_label>
        --warehouse <warehouse identifier>

        """
        label_identifier = self.app.pargs.identifier
        new_label = self.app.pargs.new_label
        if any((label_identifier is None, new_label is None)):
            raise HoneyError(f"You must provide a label identifier and new label")
        # warehouse identifier may or may not be needed so we'll deal with it later
        wh_identifier = self.app.pargs.warehouse
        if label_identifier.isnumeric():
            # then it's a db record id and we just try to find it
            loc_id = int(label_identifier)
            loc_obj = self.app.session.query(InventoryLocation).filter(
                InventoryLocation.id==loc_id).first()
        else:
            # assume the label_identifier must be a name
            loc_obj = self.app.session.query(
                InventoryLocation).filter_by(label=label_identifier).all()
        if not loc_obj:
            raise HoneyError('The location label is not found, '
                             'please provide a valid location label identifier.')
        # if there is more than one location record with the same label,
        #   then we must require a warehouse ID to find the unique targeted label
        # first check for a provided warehouse name. if none is found,
        # check the cache for an active warehouse
        if len(loc_obj) > 1:
            wh_obj = None
            if wh_identifier:
                if wh_identifier.isnumeric():
                    wh_id = int(wh_identifier)
                    wh_obj = self.app.session.query(Warehouse).filter(
                        Warehouse.id == wh_id).first()
                else:
                    wh_obj = self.app.session.query(
                        Warehouse).filter_by(name=wh_identifier).first()
                if not wh_obj:
                    raise HoneyError('No warehouse exists with that identifier')

            # only go to this next block if the wh_identifier does not exist
            elif not wh_identifier:
                wh_obj = Warehouse.get_active_warehouse(self.app)
                # we assume label_identifier is a label name because if it is a
                # database record ID then we would only have one record result.
                # we only get to this block if there is more than one record result.
                if wh_obj:
                    loc_obj = self.app.session.query(
                        InventoryLocation).filter_by(
                        label=label_identifier, warehouse_id=wh_obj.id).all()
                    if not loc_obj:
                        raise HoneyError('You must provide both a location label '
                                         'and warehouse identifier.')
            if not wh_obj:
                raise HoneyError(
                    'The warehouse does not exist. Please set an active '
                    'warehouse or use the flags to designate an existing warehouse')
            else:
                raise HoneyError('You must provide a warehouse identifier.')
        # update by assignment
        print(f'this is loc_obj -> {loc_obj}')
        print(f'this is new_label -> "{new_label}"')
        loc_obj[0].label = new_label
        self.app.session.commit()
        return self.app.log.info(
            f"updated location label name from '{loc_obj[0].label}' to '{new_label}'")

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