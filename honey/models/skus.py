from sqlalchemy import (Integer, Column, ForeignKey,
                        Numeric, Unicode, UnicodeText, Table, UniqueConstraint)
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from honey.core.database import (ModelBase, CRUDMixin, SurrogatePK, AuditMixin,
                                 reference_col)

# one ProductSku can have many different SkuAttributes.
# one SkuAttribute can have stock in many ProductSku's.
productsku_skuattr_assoc = Table(
    'productskus_skuattrs', ModelBase.metadata,
    Column('sku_id', Integer, ForeignKey('product_skus.id')),
    Column('skuattr_id', Integer, ForeignKey('sku_attrs.id'))
)


class Container(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    A table to hold the various ProductSku containers. It has a self-referential
    relationship so that a container which contains another container can be
    properly identified. To init the table, it should be created top down starting
    with the master carton, which will reference itself as its own parent.  Then,
    create new container types starting with PARENT and then CHILD.
    """
    __tablename__ = 'containers'
    # retail-package, inner-box, inner-master-ctn, outer-master-ctn
    name = Column('name', Unicode(), nullable=False)
    description = Column('description', UnicodeText, nullable=False)
    # self-referential id
    parent_id = reference_col('containers')
    parent = relationship('Container', remote_side='Container.id', backref='children')
    # backref: skus

    def __init__(self, name, description, parent_id, **kwargs):
        self.name = name
        self.description = description
        self.parent_id = parent_id

    def __repr__(self):
        return f'<Container {self.name}>'


class ProductSku(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    The base model for Product Skus.

    NOTE for changes: this model is imported in alembic/env.py for migrations.
    """
    __tablename__ = 'product_skus'
    __table_args__ = (UniqueConstraint('sku', 'entity_id'),)
    # skus should be unique in combination with owner_id
    sku = Column('sku', Unicode(), nullable=False)
    upc = Column('upc', Unicode(), unique=True)
    description = Column('description', UnicodeText())

    entity_id = reference_col('entities')
    entity = relationship('Entity', backref='skus')
    container_id = reference_col('containers')
    container = relationship('Container', backref='skus')

    sku_attrs = relationship(
        "SkuAttribute",
        secondary=productsku_skuattr_assoc,
        lazy='selectin', backref=backref('skus'),
        cascade="all, delete", passive_deletes=True
    )

    # proxies to the InventoryLocation -> [<InventoryLocation ('hg-1', 'Office')>, ]  FALSE
    location = association_proxy('locations', 'location')

    # this proxies to the LocationSkuAssoc -> [1, ] its probably broken need to check
    quantity = association_proxy('locations', 'quantity')

    # proxies to the LocationSkuAssoc -> [<LocationSkuAssoc ('C2-W-L', 'hg-1')>, ]
    locations = relationship("LocationSkuAssoc", back_populates="sku",
                 lazy="selectin", passive_deletes=True)

    def __init__(self, sku, upc, description, entity_id, container_id, **kwargs):
        self.sku = sku
        self.description = description
        self.upc = upc
        self.entity_id = entity_id
        self.container_id = container_id

    def __repr__(self):
        return f'<ProductSku {self.sku, self.entity}>'


class SkuAttribute(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    A table allowing the creation of key:value grouping designations for SKUS.
    Like, Sku Family (Grapple, Flux-Field, ...) and Sku Class ('Pro', 'Grip', ...).
    This is similar/does the same thing as product SKU variants. Like, just create a
    Sku Group with key='color and value='White'.  Works for all physical attributes
    like length, width, height, and weight. Also use 'retail-capacity' and
    'child-capacity' here as keys with the value being the Unicode integer
    representation. You can cast those to integers when needed for summation.
    todo: a better data structure for this might be a jsonb in postgres as
        it would eliminate redundant keys in the db for each owner_id. But
        the owner_id reference column should make current structure very
        speed efficient and changing it to eliminate a few potential redundant
        keys is just nitpicking.
    """
    __tablename__ = 'sku_attrs'
    # key should be like "family", "class", "color", 'connector'
    key = Column('key', Unicode())
    # value should be the value for the key, like 'family':'Grapple', 'class':'Pro',
    # 'color':'white', 'connector':'Micro-USB'
    value = Column('value', Unicode())
    entity_id = reference_col('entities')
    entity = relationship('Entity', backref='sku_attrs')
    # backref: skus from ProductSku

    def __init__(self, key, value, entity_id, **kwargs):
        self.key = key
        self.value = value
        self.entity_id = entity_id

    def __repr__(self):
        return f'<SkuAttribute {self.key}={self.value}>'

