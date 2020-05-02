"""
Create model factories for the tests
"""
import factory
import pathlib
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from factory import PostGenerationMethodCall, Sequence
from factory.alchemy import SQLAlchemyModelFactory
from honey.core.database import time_utcnow
from honey.models.inventory import (Warehouse, InventoryLocation, SkuLocationAssoc)
from honey.models.skus import SkuOwner, Container, ProductSku, SkuAttribute

config_dir = pathlib.Path.cwd().parent / 'config'
config_file = config_dir / 'honey.yml'
# parse YAML config file

with open(config_file) as stream:
    config_data = yaml.safe_load(stream)

conn = config_data['honeytest']['DB_CONNECTION']


# create an engine to the test database
engine = create_engine(conn)
# create a configured "Session" class
Session = scoped_session(sessionmaker(bind=engine))


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""
    class Meta:
        """Factory configuration."""
        abstract = True
        sqlalchemy_session = Session()


class WarehouseFactory(BaseFactory):
    """
    Warehouse factory.
    """

    class Meta:
        """Factory configuration."""
        model = Warehouse

    name = 'Garage'
