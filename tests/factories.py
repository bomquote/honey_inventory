"""
Create model factories for the tests
"""
import pathlib
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from factory import PostGenerationMethodCall, Sequence, SubFactory, List
from factory.alchemy import SQLAlchemyModelFactory
from honey.core.database import time_utcnow
from honey.honey import path_matcher, path_constructor
from honey.models.inventory import (Warehouse, InventoryLocation, LocationSkuAssoc)
from honey.models.entities import Entity
from honey.models.skus import Container, ProductSku, SkuAttribute

yaml.add_implicit_resolver('!path', path_matcher)
yaml.add_constructor('!path', path_constructor)

config_dir = pathlib.Path.cwd().parent / 'config'
config_file = config_dir / 'honey.yml'
# parse YAML config file


with open(config_file, 'r') as stream:
    config_data = yaml.load(stream, Loader=yaml.FullLoader)


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


class EntityFactory(BaseFactory):
    """
    Warehouse factory.
    """
    class Meta:
        """Factory configuration."""
        model = Entity
    name = 'honeygear'


class WarehouseFactory(BaseFactory):
    """
    Warehouse factory.
    """
    class Meta:
        """Factory configuration."""
        model = Warehouse

    name = 'testGarage'
    entity_id = SubFactory('tests.factories.EntityFactory')
    entity = SubFactory('tests.factories.EntityFactory')


class LocationSkuAssocFactory(BaseFactory):
    """
    LocationSkuAssoc factory.
    """
    class Meta:
        """Factory config"""
        model = LocationSkuAssoc

    sku_id = SubFactory('tests.factories.ProductSkuFactory')
    location_id = SubFactory('tests.factories.InventoryLocationFactory')
    quantity = 1
    location = SubFactory('tests.factories.InventoryLocationFactory')
    sku = SubFactory('tests.factories.ProductSkuFactory')


class InventoryLocationFactory(BaseFactory):
    """
    InventoryLocation factory.
    """
    class Meta:
        """Factory configuration"""
        model = InventoryLocation

    label = Sequence(lambda n: 'HG-{0}'.format(n))
    warehouse_id = SubFactory('tests.factories.WarehouseFactory')
    warehouse = SubFactory('tests.factories.WarehouseFactory')
    skus = List([SubFactory('tests.factories.LocationSkuAssocFactory')])


class ContainerFactory(BaseFactory):
    """
    Container factory.
    """
    class Meta:
        """Factory configuration"""
        model = Container

    id = 1
    name = Sequence(lambda n: 'container-{0}'.format(n))
    description = Sequence(lambda n: 'A container-{0} for our products.'.format(n))
    parent_id = SubFactory('tests.factories.ContainerFactory')
    parent = SubFactory('tests.factories.ContainerFactory')
    # backref: children


class ProductSkuFactory(BaseFactory):
    """
    ProductSku factory
    """
    class Meta:
        """Factory configuration"""
        model = ProductSku

    sku = Sequence(lambda n: 'A{0}-W-L'.format(n))
    upc = Sequence(lambda n: 'upccode{0}'.format(n))
    description = Sequence(lambda n: 'A grapple A{0}, white, iphone'.format(n))
    entity_id = SubFactory('tests.factories.EntityFactory')
    entity = SubFactory('tests.factories.EntityFactory')
    container_id = SubFactory('tests.factories.ContainerFactory')
    container = SubFactory('tests.factories.ContainerFactory')
    sku_attrs = List([SubFactory('tests.factories.SkuAttributeFactory')])
    # location = SubFactory('tests.factories.InventoryLocationFactory')
    # quantity = SubFactory('tests.factories.LocationSkuAssocFactory')
    locations = List([SubFactory('tests.factories.LocationSkuAssocFactory')])


class SkuAttributeFactory(BaseFactory):
    """
    SkuAttribute factory
    """
    class Meta:
        """
        Factory Configuration
        """
        model = SkuAttribute

    key = 'color'
    value = 'white'
    entity_id = SubFactory('tests.factories.EntityFactory')