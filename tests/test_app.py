

def test_app(HoneyApp, hooks):
    # test app without any subcommands or arguments
    with HoneyApp(hooks=hooks) as app:
        app.run()
        assert app.exit_code == 0


def test_app_debug(HoneyApp, hooks):
    # test that debug mode is functional
    argv = ['--debug']
    with HoneyApp(argv=argv, hooks=hooks) as app:
        app.run()
        assert app.debug is True


def test_command1(HoneyApp, hooks, template_path):
    # test command1 without arguments
    argv = ['command1']
    with HoneyApp(argv=argv, hooks=hooks) as app:
        app.add_template_dir(template_path)
        app.run()
        data, output = app.last_rendered
        assert data['foo'] == 'bar'
        assert output.find('Foo => bar')

    # test command1 with arguments
    argv = ['command1', '--foo', 'not-bar']
    with HoneyApp(argv=argv, hooks=hooks) as app:
        app.add_template_dir(template_path)
        app.run()
        data, output = app.last_rendered
        assert data['foo'] == 'not-bar'
        assert output.find('Foo => not-bar')

