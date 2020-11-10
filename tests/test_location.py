from honey.models.inventory import InventoryLocation
from honey.core.exc import HoneyError
from pytest import raises

class TestInventoryLocation:
    """
     Inventory location tests.
     """
    def test_invloc_list(self, HoneyApp, hooks, db, inventory_location):
        """
        Test `honey_warehouse_list.  This is returned as a tabulate table.
        :return:
        """
        argv = ['invloc', 'list']
        with HoneyApp(argv=argv, hooks=hooks, output_handler='tabulate') as app:
            app.run()
            data, output = app.last_rendered
            assert 'HG-1' in output

    def test_invloc_create(self, HoneyApp, hooks, db, inventory_location):
        """
        Test `honey warehouse create`
        :return:
        """
        argv = ['invloc', 'create', 'HG-2', '-w', 'testGarage']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            initial_count = app.session.query(InventoryLocation).count()
            app.run()
            final_count = app.session.query(InventoryLocation).count()
            assert initial_count + 1 == final_count
            assert 'HG-2' in \
                   [x.label for x in app.session.query(InventoryLocation).all()]

    def test_invloc_create_wh_not_exist_raises(self, HoneyApp, hooks, db, inventory_location):
        """
        Test `honey invloc create` raises if a warehouse doesn't exist
        :return:
        """
        argv = ['invloc', 'create', 'HG-2', '-w', 'testGarage2']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            with raises(HoneyError):
                app.run()

    def test_invloc_update(self, HoneyApp, hooks, db, inventory_location):
        """
        Test `honey invloc update hg-1 -n hg-1a`
        """
        argv = ['invloc', 'update', 'HG-1', '-n', 'HG-1a']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            app.run()
            assert 'HG-1a' in \
                   [x.label for x in app.session.query(InventoryLocation).all()]