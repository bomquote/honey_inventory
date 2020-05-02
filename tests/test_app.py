from pytest import raises
from honey.honey import HoneyTest


def test_app():
    # test app without any subcommands or arguments
    with HoneyTest() as app:
        app.run()
        assert app.exit_code == 0


def test_app_debug():
    # test that debug mode is functional
    argv = ['--debug']
    with HoneyTest(argv=argv) as app:
        app.run()
        assert app.debug is True


def test_command1():
    # test command1 without arguments
    argv = ['command1']
    with HoneyTest(argv=argv) as app:
        app.run()
        data, output = app.last_rendered
        assert data['foo'] == 'bar'
        assert output.find('Foo => bar')

    # test command1 with arguments
    argv = ['command1', '--foo', 'not-bar']
    with HoneyTest(argv=argv) as app:
        app.run()
        data, output = app.last_rendered
        assert data['foo'] == 'not-bar'
        assert output.find('Foo => not-bar')

### warehouse


class TestWarehouse:
    """Warehouse tests."""

    def test_warehouse_list(self, db_func, warehouse):
        """
        Test `honey_warehouse_list.  This is returned as a tabulate table.
        :return:
        """
        argv = ['warehouse', 'list']
        with HoneyTest(argv=argv) as app:
            app.run()
            # data, output = app.last_rendered
            # print(type(res))
            # assert output.find('Garage')
