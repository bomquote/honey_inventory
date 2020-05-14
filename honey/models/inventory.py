from sqlalchemy import (Integer, Column, ForeignKey,
                        Numeric, Unicode, UnicodeText, Table, UniqueConstraint)
from sqlalchemy.orm import relationship, backref
from honey.core.database import (ModelBase, CRUDMixin, SurrogatePK, AuditMixin,
                                 reference_col, session)
from honey.models.entities import Entity
from honey.core.exc import HoneyError


class Warehouse(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    A Warehouse is an InventoryLocation container. It can be owned by
    a WarehouseOwner. In reality, a warehouse may be a truck trailer, garage,
    retail location, storage shed, room in a house, or any other place that
    can physically contain an InventoryLocation.
    """
    __tablename__ = 'warehouses'
    __table_args__ = (UniqueConstraint('name', 'entity_id'),)
    name = Column('name', Unicode())
    entity_id = reference_col('entities')
    entity = relationship('Entity', backref='warehouses')

    # backref: locations

    def __init__(self, name, entity_id):
        self.name = name
        self.entity_id = entity_id

    def __repr__(self):
        return f'<Warehouse name={self.name}, entity={self.entity_id}>'

    @classmethod
    def get_obj(cls, app, identifier):
        """
        Get the Warehouse object per the Warehouse identifier or raise HoneyError
        :param: app: the current app
        :param: identifier: either a database record id or a Warehouse name
        :return: Warehouse object or raise HoneyError
        """
        wh_obj = None
        if identifier is not None and identifier.isnumeric():
            wh_obj = app.session.query(cls).filter_by(
                id=identifier).first()
        elif identifier is not None:
            wh_obj = app.session.query(cls).filter_by(
                name=identifier).first()
        if not wh_obj:
            raise HoneyError(
                'No warehouse exists with the provided identifier')
        return wh_obj

    @classmethod
    def get_obj_with_entity(cls, app, wh_identifier, ent_identifier, return_none=False):
        """
        Get the Warehouse object per the Warehouse identifier or raise HoneyError
        :param: app: the current app
        :param: wh_identifier: either a warehouse table record id or a Warehouse.name
        :param: ent_identifier: either a entity table record id or Entity.name
        :return: Warehouse object or raise HoneyError if return_none == False.
        Warehouse object or None if return_none == True.
        """
        wh_obj = None
        wh_identifier = str(wh_identifier)
        ent_identifier = str(ent_identifier)
        if wh_identifier is None:
            raise HoneyError("You must provide a warehouse identifier")
        if wh_identifier is not None and wh_identifier.isnumeric():
            wh_obj = app.session.query(cls).filter_by(
                id=wh_identifier).first()
            return wh_obj
        if wh_identifier is not None:
            wh_obj = app.session.query(cls).filter_by(
                name=wh_identifier).all()
            if len(wh_obj) == 1:
                return wh_obj[0]
            if ent_identifier is None:
                raise HoneyError(f"You must provide an entity identifier to find the "
                                 f"correct warehouse with name={wh_identifier}")
            ent_obj = Entity.get_obj(app, ent_identifier)
            wh_obj = app.session.query(cls).filter_by(
                    name=wh_identifier, entity_id=ent_obj.id).first()
        if not wh_obj and not return_none:
            raise HoneyError(
                'No warehouse exists with the provided identifier')
        return wh_obj

    @classmethod
    def get_active_warehouse(cls, app):
        """
        Check if there is an active warehouse in the app.cache
        param: app: the active app object
        returns: A class: <Warehouse> object or none
        """
        wh_cache_key = None
        try:
            if app.__test__:
                wh_cache_key = app.config.get('honeytest', 'WAREHOUSE_CACHE_KEY')
        except AttributeError:
            wh_cache_key = app.config.get('honey', 'WAREHOUSE_CACHE_KEY')
        active_warehouse = app.cache.get(wh_cache_key)
        if active_warehouse:
            return session.query(cls).filter_by(name=active_warehouse).first()
        else:
            return None


class InventoryLocation(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    A location for a Sku. Right now I think of an InventoryLocation `label` as a
    unique name/number per each warehouse, for a Container which may hold multiple
    different SKUs. For example, we have mixed master carton boxes of retail packaged
    products and this will enable us to just put a label on each top level master
    carton box in a warehouse and call that label the "inventory location". Then,
    inventory locations are identified by the label. We associate the inventory
    location labels with SKUs in the Association object relation table,
    `LocationSkuAssoc`. I'm sure this can be made more complex for some use cases
    but it's already flexible and will cover the need for many use cases.
    Add extra data in the LocationSkuAssoc class (must migrate if changed).

    NOTE for changes: this model is imported in alembic/env.py for migrations.
    """
    # name the box like SkuOwner-Number
    __tablename__ = 'inventory_locations'
    __table_args__ = (UniqueConstraint('label', 'warehouse_id'),)
    label = Column('label', Unicode(), nullable=False)
    warehouse_id = reference_col('warehouses')

    warehouse = relationship("Warehouse", backref="locations",
                             cascade="save-update, merge",
                             single_parent=True)

    skus = relationship(
        "LocationSkuAssoc", back_populates="location",
        primaryjoin="sku_locations.c.location_id == InventoryLocation.id",
        lazy="selectin", cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, label, warehouse_id, **kwargs):
        self.label = label
        self.warehouse_id = warehouse_id

    def __repr__(self):
        return f'<InventoryLocation {self.label, self.warehouse.name}>'


class LocationSkuAssoc(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    An association object for Locations and Skus. The left side of the relationship
    maps a InventoryLocation as a one-to-many to LocationSkuAssoc. Then,
    LocationSkuAssoc maps a one-to-many to ProductSku.
    This allows one Location to have many ProductSkus, offering significant flexibility
    when combined with the ease of creating transient locations. The association allows
    to add some extra data like sku quantity in the location, and can also capture
    items like cost and sales price here as well. Then, the association class maps a
    many-to-one to the ProductSku, so we can have mixed Skus in a single
    InventoryLocation. Finally, we can use association_proxy to work with the
    data in this table, as done in the models/skus.py file in the ProductSku class.
    """
    # ideally this table should be named location_skus, I got it backwards here
    __tablename__ = 'sku_locations'
    # Parent is InventoryLocation
    location_id = Column('location_id', Integer,
                         ForeignKey("inventory_locations.id",
                                    onupdate="CASCADE",
                                    ondelete="CASCADE"),
                         primary_key=True)

    # Child is ProductSku
    sku_id = Column('sku_id', Integer,
                    ForeignKey("product_skus.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    primary_key=True)

    quantity = Column('quantity', Integer, nullable=False)

    # parent
    location = relationship("InventoryLocation", back_populates="skus",
                            foreign_keys=[location_id],
                            lazy="joined", cascade="all, delete")

    # child
    sku = relationship("ProductSku", back_populates='locations',
                       lazy="joined",
                       foreign_keys=[sku_id],
                       cascade="all, delete")

    def __init__(self, sku_id, location_id, quantity, **kwargs):
        self.sku_id = sku_id
        self.location_id = location_id
        self.quantity = quantity

    def __repr__(self):
        return f'<LocationSkuAssoc {self.sku.sku, self.location.label}>'
