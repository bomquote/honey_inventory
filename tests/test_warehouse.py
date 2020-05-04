from honey.models.inventory import Warehouse

class TestWarehouse:
    """Warehouse tests."""

    def test_warehouse_list(self, HoneyApp, hooks, db, warehouse):
        """
        Test `honey_warehouse_list.  This is returned as a tabulate table.
        :return:
        """
        argv = ['warehouse', 'list']
        with HoneyApp(argv=argv, hooks=hooks, output_handler='tabulate') as app:
            app.run()
            data, output = app.last_rendered
            assert 'testGarage' in output

    def test_warehouse_create(self, HoneyApp, hooks, db, warehouse):
        """
        Test `honey warehouse create`
        :return:
        """
        argv = ['warehouse', 'create', 'testwh']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            initial_count = app.session.query(Warehouse).count()
            app.run()
            final_count = app.session.query(Warehouse).count()
            assert initial_count + 1 == final_count
            assert 'testwh' in [wh.name for wh in app.session.query(Warehouse).all()]

    def test_warehouse_update(self, HoneyApp, hooks, db, warehouse):
        """
        Test `honey warehouse update`
        :return:
        """
        argv = ['warehouse', 'update', 'testGarage']