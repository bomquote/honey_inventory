from sqlalchemy import (Integer, Column, ForeignKey,
                        Numeric, Unicode, UnicodeText, Table, UniqueConstraint)
from sqlalchemy.orm import relationship, backref
from honey.core.database import (ModelBase, CRUDMixin, SurrogatePK, AuditMixin,
                                 reference_col)


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


class InventoryLocation(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    A location for a Sku. Right now I think of an InventoryLocation `label` as a
    unique name/number per each warehouse, for a Container which may hold multiple
    different SKUs. For example, we have mixed master carton boxes of retail packaged
    products and this will enable us to just put a label on each top level master
    carton box in a warehouse and call that label the "inventory location". Then,
    inventory locations are identified by the label. We associate the inventory
    location labels with SKUs in the Association object relation table,
    `SkuLocationAssoc`. I'm sure this can be made more complex for some use cases
    but it's already flexible and will cover the need for many use cases.
    Add extra data in the SkuLocationAssoc class (must migrate if changed).

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
        "SkuLocationAssoc", back_populates="location",
        primaryjoin="sku_locations.c.location_id == InventoryLocation.id",
        lazy="selectin", cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, label, warehouse_id):
        self.label = label
        self.warehouse_id = warehouse_id

    def __repr__(self):
        return f'<InventoryLocation {self.label, self.warehouse.name}>'


class SkuLocationAssoc(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    An association object for Skus and Locations. The left side of the relationship
    maps a Sku as a one-to-many to InventoryLocations. This allows one SKU to have many
    InventoryLocations, offering significant flexibility when combined with the
    ease of creating transient locations. The association allows to add some extra data
    like sku quantity in the location, and can also capture items like cost
    and sales price here as well. Then, the association class maps a
    many-to-one to the InventoryLocation, so we can have mixed Skus in a single
    InventoryLocation. Finally, we can use association_proxy to work with the
    data in this table, as done in the models/skus.py file in the ProductSku class.
    """
    __tablename__ = 'sku_locations'
    # parent is ProductSku
    sku_id = Column('sku_id', Integer,
                    ForeignKey("product_skus.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                    primary_key=True)
    # child is InventoryLocation
    location_id = Column('location_id', Integer,
                         ForeignKey("inventory_locations.id",
                                    onupdate="CASCADE",
                                    ondelete="CASCADE"),
                         primary_key=True)

    quantity = Column('quantity', Integer, nullable=False)

    # child
    location = relationship("InventoryLocation", back_populates="skus",
                            foreign_keys=[location_id],
                            lazy="joined", cascade="all, delete")

    # parent
    sku = relationship("ProductSku", back_populates='locations',
                       lazy="joined",
                       foreign_keys=[sku_id],
                       cascade="all, delete")

    def __init__(self, sku_id, location_id, quantity):
        self.sku_id = sku_id
        self.location_id = location_id
        self.quantity = quantity

    def __repr__(self):
        return f'<SkuLocationAssoc {self.sku.sku, self.location.label}>'
