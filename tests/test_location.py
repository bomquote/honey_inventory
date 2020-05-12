from honey.models.inventory import InventoryLocation

class TestInventoryLocation:
    """
     Inventory location tests.
     """
    def test_invloc_list(self, HoneyApp, hooks, db):
        """
        Test `honey_warehouse_list.  This is returned as a tabulate table.
        :return:
        """
        argv = ['invloc', 'list']
        with HoneyApp(argv=argv, hooks=hooks, output_handler='tabulate') as app:
            app.run()
            data, output = app.last_rendered
            assert 'HG-1' in output
