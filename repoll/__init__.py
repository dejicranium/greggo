from pyramid.config import Configurator


SETTINGS = None
def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    SETTINGS = settings
    config = Configurator(settings=settings,)
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.cors')
    config.add_cors_preflight_handler()
    config.include('.routes')
    config.include('.security')
    config.include('..greggo')

    config.add_static_view('static', path='repoll:static')

    config.scan()
    return config.make_wsgi_app()
