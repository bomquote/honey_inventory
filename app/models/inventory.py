from sqlalchemy import (Integer, Column, ForeignKey,
                        Numeric, Unicode, UnicodeText, Table, UniqueConstraint)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from app.database import Base, CRUDMixin, SurrogatePK, reference_col


class InventoryLocation(Base, CRUDMixin, SurrogatePK):
    """
    A location for a Sku. Right now I think of this as a unique name/number for
    a Container which may hold multiple different SKUs. For example, we have mixed
    boxes of retail packaged products and this will enable us to just put a label on
    each box and call that label the "location". Then, I can populate a location
    with SKUs and relate them in the many-many table. I'm sure this could be made
    more complex in the future but it may be all we ever need.
    """
    # name the box like SkuOwner-Number
    __tablename__ = 'inventory_locations'
    __table_args__ = (UniqueConstraint('label', 'warehouse'),)
    label = Column('label', Unicode(), nullable=False)
    warehouse = Column('warehouse', Unicode(), nullable=False, default='Calabria')

    # backref: skus -> SkuLocationAssoc

    def __init__(self, label, warehouse):
        self.label = label
        self.warehouse = warehouse

    def __repr__(self):
        return f'<InventoryLocation {self.label, self.warehouse}>'


class SkuLocationAssoc(Base, CRUDMixin, SurrogatePK):
    """
    An association object for Skus and Locations. The left side of the relationship
    maps a Sku as a one-to-many to InventoryLocations. This allows one SKU to have many
    InventoryLocations. The association allows to add some extra data like
    sku quantity in the location, cost, sales price, then the association class maps a
    many-to-one to the InventoryLocation.  Use hybrid relationships to work
    with this table.
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
    location = relationship("InventoryLocation", backref="skus",
                                cascade="all, delete",
                                single_parent=True)

    # parent
    sku = relationship("ProductSku", backref="locations",
                          foreign_keys=[location_id],
                          cascade="all, delete",
                          primary_join="product_skus.c.id == SkuLocationAssoc.sku_id",
                          single_parent=True)

    def __init__(self, sku_id, location_id, quantity):
        self.sku_id = sku_id
        self.location_id = location_id
        self.quantity = quantity

    def __repr__(self):
        return f'<SkuLocationAssoc {self.sku.sku, self.location.label}>'


