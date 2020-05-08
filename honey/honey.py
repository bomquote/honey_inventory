import yaml
import re
import os
from cement import App, TestApp
from cement.core.exc import CaughtSignal
from honey import config_file
from honey.core.database import extend_sqla
from honey.core.exc import HoneyError
from honey.controllers.base import Base
from honey.controllers.entity import EntityController
from honey.controllers.warehouse import WarehouseController
from honey.controllers.inventory_location import InventoryLocationController
from honey.ext.redis import HoneyRedisCacheHandler

# match on ${ env variable } in the yaml file
path_matcher = re.compile(r'\$\{([^}^{]+)\}')
def path_constructor(loader, node):
    """
    Extract the matched value, expand env variable, and replace the match.
    This allows to use environment variables in the honey.yml file.
    source: https://stackoverflow.com/a/52412796/1493069
    """
    value = node.value
    match = path_matcher.match(value)
    env_var = match.group()[2:-1]
    return os.environ.get(env_var) + value[match.end():]

yaml.add_implicit_resolver('!path', path_matcher)
yaml.add_constructor('!path', path_constructor)


with open(config_file, 'r') as stream:
    config_data = yaml.load(stream, Loader=yaml.FullLoader)

CONFIG = config_data

class Honey(App):
    """Honey Inventory primary application."""

    class Meta:
        label = 'honey'

        #config_defaults = CONFIG
        config_section = 'honey'
        config_files = [str(config_file)]

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
            'honey.ext.alarm', # the default included breaks due to SIGALRM fail on windows
            'tabulate'
        ]

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        template_handler = 'jinja2'

        # set the output handler
        output_handler = 'jinja2'

        cache_handler = HoneyRedisCacheHandler

        # register handlers
        # bob: if register handlers in honey.bootstrap, don't need to register here
        handlers = [
            Base,
            EntityController,
            WarehouseController,
            InventoryLocationController
        ]

        hooks = [
            ('post_setup', extend_sqla),
        ]

        # not currently using the bootstrap method
        # bootstrap = 'honey.bootstrap'


class HoneyTest(TestApp, Honey):
    """A sub-class of Honey that is better suited for testing."""

    class Meta:
        label = 'honey'
        config_section = 'honeytest'
        config_files = [str(config_file)]


def main():
    with Honey() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except HoneyError as e:
            print('HoneyError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == "__main__":
    main()
