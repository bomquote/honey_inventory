from sqlalchemy import (Column, Unicode)
from honey.core.database import (ModelBase, CRUDMixin, SurrogatePK, AuditMixin,
                                 reference_col)
from honey.core.exc import HoneyError


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

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Entity {self.name}>'

    @classmethod
    def get_obj(cls, app, identifier):
        """
        Get the entity object per the entity identifier or raise HoneyError
        :param: app: the current app
        :param: identifier: either a database record id or an Entity name
        :return: Entity object
        """
        ent_obj = None
        identifier = str(identifier)
        if identifier is not None and identifier.isnumeric():
            ent_obj = app.session.query(cls).filter_by(
                id=identifier).first()
        elif identifier is not None:
            ent_obj = app.session.query(cls).filter_by(name=identifier).first()
        if not ent_obj:
            raise HoneyError(
                'No Entity exists with the provided identifier')
        return ent_obj
