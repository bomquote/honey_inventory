
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from honey.core.exc import HoneyError
from honey.controllers.base import Base
from honey.controllers.inventory import WarehouseController
from honey.ext.redis import HoneyRedisCacheHandler

from time import sleep

# configuration defaults
CONFIG = init_defaults('honey')
# CONFIG['honey']['db_connection'] = 'postgresql+psycopg2://postgres:password@localhost:5432/hgdb'
CONFIG['honey']['foo'] = 'bar'


class Honey(App):
    """Honey Inventory primary application."""

    class Meta:
        label = 'honey'

        # configuration defaults
        config_defaults = CONFIG

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
            WarehouseController
        ]

        hooks = [
            # ('post_setup', extend_sqla),
        ]

        # not currently using the bootstrap method
        # bootstrap = 'honey.bootstrap'


class HoneyTest(TestApp, Honey):
    """A sub-class of Honey that is better suited for testing."""

    class Meta:
        label = 'honey'


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
