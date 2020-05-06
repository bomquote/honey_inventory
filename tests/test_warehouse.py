from cement.core.extension import ExtensionInterface, ExtensionHandler
from honey.models.inventory import Warehouse
from .factories import config_data

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
        argv = ['warehouse', 'create', 'testwh', '-i', 'honeygear']
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
        argv = ['warehouse', 'update', 'testGarage', '-n', 'testKitchen']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            app.run()
            app.session.flush()
            assert 'testKitchen' in [
                wh.name for wh in app.session.query(Warehouse).all()]

    def test_warehouse_delete(self, HoneyApp, hooks, db, warehouse, sku_owner):
        """
        Test `honey warehouse delete`
        :return:
        """
        argv = ['warehouse', 'delete', 'testGarage']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            new_warehouse = Warehouse(name="testKitchen", owner_id=sku_owner.id)
            app.session.add(new_warehouse)
            app.session.commit()
            initial_count = app.session.query(Warehouse).count()
            app.run()
            final_count = app.session.query(Warehouse).count()
            assert initial_count - 1 == final_count
            assert 'testGarage' not in [
                wh.name for wh in app.session.query(Warehouse).all()]

    def test_warehouse_activate(self, HoneyApp, hooks, db, warehouse, sku_owner):
        """
        Test `honey warehouse activate`
        :return:
        """
        argv = ['warehouse', 'activate', 'testGarage']
        with HoneyApp(argv=argv, hooks=hooks) as app:

            # print(f'key -> {app.config.get("cache.redis", "PASSWORD")}')
            # the cache key is not set in redis
            # assert wh_cache_key is None
            wh_cache_key = app.config.get("honeytest", "WAREHOUSE_CACHE_KEY")
            assert app.cache.get(wh_cache_key) is None
            app.run()
            # the cache key is set in redis
            print(f'cache -> {app.cache.get(wh_cache_key)}')
            assert 'testGarage' in app.cache.get(wh_cache_key)
