from sqlalchemy import (Column, Unicode)
from honey.core.database import (ModelBase, CRUDMixin, SurrogatePK, AuditMixin,
                                 reference_col)


class Entity(ModelBase, CRUDMixin, SurrogatePK, AuditMixin):
    """
    A table designating ultimate top level owners of assets and the
    API will use parent child relationships to further specify warehouses,
    product SKUs, or other assets owned by themselves and others.
    Parent -> Entity, Child -> ProductSku.
    """
    __tablename__ = 'entities'
    name = Column('name', Unicode(), nullable=False, unique=True)

    # backref: skus
    # backref: warehouses

    def __init__(self, name, **kwargs):
        self.name = name

    def __repr__(self):
        return f'<Entity {self.name}>'
