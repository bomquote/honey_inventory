from sqlalchemy import (Integer, Column, ForeignKey,
                        Numeric, Unicode, UnicodeText, Table, UniqueConstraint)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from honey.core.database import ModelBase, CRUDMixin, SurrogatePK, AuditMixin, reference_col
from cement.core.handler import Handler


class Warehouse(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    A Warehouse is an InventoryLocation container.
    """
    __tablename__ = 'warehouses'
    name = Column('name', Unicode())

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Warehouse {self.name}>'


class InventoryLocation(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    A location for a Sku. Right now I think of this as a unique name/number for
    a Container which may hold multiple different SKUs. For example, we have mixed
    boxes of retail packaged products and this will enable us to just put a label on
    each box and call that label the "location". Then, I can populate a location
    with SKUs and relate them in the Association object table. I'm sure this can be made
    more complex in the future but it may be all we ever need now.

    NOTE for changes: this model is imported in alembic/env.py for migrations.
    """
    # name the box like SkuOwner-Number
    __tablename__ = 'inventory_locations'
    __table_args__ = (UniqueConstraint('label', 'warehouse_id'),)
    label = Column('label', Unicode(), nullable=False)
    warehouse_id = reference_col('warehouses')

    warehouse = relationship("Warehouse", backref="inventory_locations",
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
    ease of creating transient locatins. The association allows to add some extra data
    like sku quantity in the location, and could potentially capture items like cost
    and sales price here as well. Then, the association class maps a
    many-to-one to the InventoryLocation. Finally, we can use hybrid relationships to
    work with this table.
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


