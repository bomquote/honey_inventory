"""Load the honey framework."""
from honey.controllers.base import Base


def load(app):
    """Load the framework."""
    app.handler.register(Base)
