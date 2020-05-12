"""
PyTest Fixtures.
"""

import pytest
import pathlib
from cement import fs
from .factories import Session, engine
from honey.honey import HoneyTest
from honey.core.database import ModelBase
from .factories import (WarehouseFactory, EntityFactory, InventoryLocationFactory,
                        LocationSkuAssocFactory, ProductSkuFactory, ContainerFactory,
                        SkuAttributeFactory)


def test_app_extend_sqla(app):
    """
    hook for cement framework to extend and have self.app.session
    """
    session = Session()
    app.extend('session', session)


test_app_hooks = [
    ('post_setup', test_app_extend_sqla),
]


@pytest.fixture(scope="function")
def hooks():
    """hooks ensures the hgdbtest is the focus"""
    return test_app_hooks


@pytest.fixture(scope="function")
def template_path():
    yield pathlib.Path.cwd().parent / 'honey' / 'templates'


@pytest.fixture(scope="function")
def HoneyApp():
    """
    Need to use this like `with HoneyTest(argv=argv, hooks=hooks):`
    """
    HoneyTest.__test__ = True
    yield HoneyTest


@pytest.fixture(scope="function")
def tmp(request):
    """
    Create a `tmp` object that generates a unique temporary directory, and file
    for each test function that requires it.
    """
    t = fs.Tmp()
    yield t
    t.remove()


@pytest.fixture(scope="function")
def db():
    ModelBase.metadata.create_all(engine)
    yield Session()
    Session.close_all()
    ModelBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def entity(db):
    ent = EntityFactory()
    db.add(ent)
    db.commit()
    yield ent


@pytest.fixture(scope="function")
def warehouse(db, entity):
    wh = WarehouseFactory(entity_id=entity.id)
    db.add(wh)
    db.commit()
    yield wh


@pytest.fixture(scope="function")
def container(db):
    cont = ContainerFactory(
        parent_id=1,
        skus=None,
        parent=None,
    )
    db.add(cont)
    db.commit()
    yield cont


@pytest.fixture(scope="function")
def invlocation(db, warehouse):
    """
    One InventoryLocation can have many ProductSkus.
    """

    location = InventoryLocationFactory(
        warehouse_id=warehouse.id,
        skus=None,
        label='HG-1'
    )
    a = LocationSkuAssocFactory(
        sku_id=None,
        location_id=None,
        quantity=0,
        location=None,
        sku=None
    )

    location.skus.append(a)
    db.add(location)
    db.commit()
    yield location