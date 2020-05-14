
from honey.models.inventory import Warehouse


class TestWarehouse:
    """
    Warehouse tests.
    """

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
        argv = ['warehouse', 'create', 'testwh', '-e', 'honeygear']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            initial_count = app.session.query(Warehouse).count()
            app.run()
            final_count = app.session.query(Warehouse).count()
            assert initial_count + 1 == final_count
            assert 'testwh' in [wh.name for wh in app.session.query(Warehouse).all()]

    def test_warehouse_update(self, HoneyApp, hooks, db, warehouse, entity):
        """
        Test `honey warehouse update`
        :return:
        """
        argv = ['warehouse', 'update', 'testGarage', '-n', 'testKitchen', '-e',
                'honeygear']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            app.run()
            app.session.flush()
            assert 'testKitchen' in [
                wh.name for wh in app.session.query(Warehouse).all()]

    def test_warehouse_delete(self, HoneyApp, hooks, db, warehouse, entity):
        """
        Test `honey warehouse delete`
        :return:
        """
        argv = ['warehouse', 'delete', 'testGarage']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            new_warehouse = Warehouse(name="testKitchen", entity_id=entity.id)
            app.session.add(new_warehouse)
            app.session.commit()
            initial_count = app.session.query(Warehouse).count()
            app.run()
            final_count = app.session.query(Warehouse).count()
            assert initial_count - 1 == final_count
            assert 'testGarage' not in [
                wh.name for wh in app.session.query(Warehouse).all()]

    def test_warehouse_activate(self, HoneyApp, hooks, db, warehouse):
        """
        Test `honey warehouse activate`
        :return:
        """
        argv = ['warehouse', 'activate', 'testGarage']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            wh_cache_key = app.config.get("honeytest", "WAREHOUSE_CACHE_KEY")
            assert app.cache.get(wh_cache_key) is None
            app.run()
            # the cache key is set in redis
            assert 'testGarage' in app.cache.get(wh_cache_key)
            # teardown
            app.cache.delete(wh_cache_key)

    def test_warehouse_deactivate(self, HoneyApp, hooks, db, warehouse):
        """
        Test `honey warehouse deactivate`
        :return:
        """
        argv = ['warehouse', 'deactivate']
        with HoneyApp(argv=argv, hooks=hooks) as app:
            wh_cache_key = app.config.get("honeytest", "WAREHOUSE_CACHE_KEY")
            app.cache.set(wh_cache_key, 'testGarage')
            assert 'testGarage' in app.cache.get(wh_cache_key)
            app.run()
            # the cache key is unset in redis
            assert app.cache.get(wh_cache_key) is None