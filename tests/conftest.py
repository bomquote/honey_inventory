"""
PyTest Fixtures.
"""

import pytest
import pathlib
import yaml
from cement import fs
from .factories import Session, engine
from honey.honey import HoneyTest
from honey.core.database import ModelBase
from .factories import WarehouseFactory


@pytest.fixture(scope="function")
def tmp(request):
    """
    Create a `tmp` object that geneates a unique temporary directory, and file
    for each test function that requires it.
    """
    t = fs.Tmp()
    yield t
    t.remove()


@pytest.fixture(scope="function")
def db_func():
    ModelBase.metadata.create_all(engine)
    yield Session()
    Session.close_all()
    ModelBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def warehouse(db_func):
    wh = WarehouseFactory()
    db_func.add(wh)
    db_func.commit()
    return wh