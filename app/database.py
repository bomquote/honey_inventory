from sqlalchemy import (create_engine, Integer, Column, ForeignKey, MetaData)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, relationship, backref

# Database see http://alembic.zzzcomputing.com/en/latest/naming.html
metadata = MetaData(
    naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# create an engine
engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/hgdb')
# create a configured "Session" class
Session = sessionmaker(bind=engine)
# create a Session
session = Session()
# create the Base to inherit in the Model
Base = declarative_base(metadata=metadata)


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD (create, read, update,
    delete) operations."""

    @classmethod
    def create(cls, commit=True, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return commit and instance.save() or instance.save(commit=False)

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        session.add(self)
        if commit:
            session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        session.delete(self)
        return commit and session.commit()


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id``
     to any declarative-mapped class."""

    # {'extend_existing': True} broke in flask-sqlalchemy==2.3.2 but tests pass
    # __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID.
        :param record_id is the primary key ID for query.
        :return: the record by ID.
        """

        if any(
                (isinstance(record_id, str) and record_id.isdigit(),
                 isinstance(record_id, (int, float))),
        ):
            return cls.query.get(int(record_id))
        return None


def reference_col(tablename, pk_name='id', fk_kwargs=None,
                  col_kwargs=None):  # noqa
    """Column that adds primary key foreign key reference.
    :param tablename: The tablename object.
    :param nullable: Is null value accepted.
    :param pk_name: Name of primary key.
    :param kwargs1: Pass **kwargs for ForeignKey as a dict
    :param kwargs2: Pass **kwargs for Column as a dict
    Usage: ::
        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    if fk_kwargs is None:
        fk_kwargs = {}
    if col_kwargs is None:
        col_kwargs = {'nullable': False}
    if not isinstance(tablename, str):
        tablename = tablename.__tablename__
    return Column(
        ForeignKey('{0}.{1}'.format(tablename, pk_name), **fk_kwargs),
        **col_kwargs)



