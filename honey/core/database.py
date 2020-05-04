"""

from tabulate import tabulate
table = [["Sun", 696000, 1989100000], ["Earth", 6371, 5973.6],
                     ["Moon", 1737, 73.5], ["Mars", 3390, 641.85]]
print(tabulate(table))
-----  ------  -------------
Sun    696000     1.9891e+09
Earth    6371  5973.6
Moon     1737    73.5
Mars     3390   641.85
-----  ------  -------------
"""
import yaml
import pendulum
from sqlalchemy import (create_engine, Integer, Column, ForeignKey, MetaData,
                        TypeDecorator, DateTime)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from honey import config_file


with open(config_file, 'r') as stream:
    config_data = yaml.safe_load(stream)

conn = config_data['honey']['DB_CONNECTION']

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
engine = create_engine(conn)
# create a configured "Session" class
Session = scoped_session(sessionmaker(bind=engine))
# create a Session
session = Session()
ModelBase = declarative_base(metadata=metadata)


def extend_sqla(app):
    """
    hook for cement framework to extend and have self.app.session
    for now, I'm just importing session from here throughout the app
    """
    # app.log.info('extending Honey application with sqlalchemy')
    # db_connection = app.config.get('honey', 'db_connection')
    # app.log.info(f'the db_connection string is : {db_connection}')
    # 'postgresql+psycopg2://postgres:password@localhost:5432/hgdb'
    # create an engine
    # engine = create_engine(db_connection)
    # create a configured "Session" class
    # Session = sessionmaker(bind=engine)
    # create a Session
    # session = Session()
    app.extend('session', session)


def time_utcnow():
    """Returns a timezone aware utc timestamp."""
    return pendulum.now('UTC')


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD (create, read, update,
    delete) operations.  Using these methods makes it harder to test within
    the scope of the Cement framework, as the testdb is hard to access on the
    correct session object. So, minimize the use of these methods and just
    use the vanilla sqlalchemy pattern of db.session.add and db.session.commit."""

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
            return session.query(cls).get(int(record_id))
        return None


class UTCDateTime(TypeDecorator):

    impl = DateTime

    def process_bind_param(self, value, dialect):
        """Way into the database."""
        if value is not None:
            # store naive datetime for sqlite and mysql
            if dialect.name in ("sqlite", "mysql"):
                return value.replace(tzinfo=None)

            return value.astimezone(pendulum.UTC)

    def process_result_value(self, value, dialect):
        """Way out of the database."""
        # convert naive datetime to non naive datetime
        if dialect.name in ("sqlite", "mysql") and value is not None:
            return value.replace(tzinfo=pendulum.UTC)

        # other dialects are already non-naive
        return value


class AuditMixin:
    """Convenience fields to DRY up tables that need to track the user that
        created or updated a record and the time of the create or update"""

    created_at = Column(UTCDateTime(timezone=True), default=time_utcnow, index=True)
    updated_on = Column(UTCDateTime(timezone=True), default=time_utcnow,
                        onupdate=time_utcnow)


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
