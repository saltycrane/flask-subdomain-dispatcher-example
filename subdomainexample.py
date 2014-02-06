from threading import Lock

from flask import Flask

from simple_page.simple_page import simple_page


API_HOST = 'default-host'
DB_SERVER = 'default-db-server'


class FakeApiRequester(object):
    def __init__(self, host):
        self.host = host

    def __repr__(self):
        return 'FakeApiRequester(host={})'.format(self.host)


class FakeDatabase(object):
    def __init__(self, host):
        self.host = host

    def __repr__(self):
        return 'FakeDatabase(host={})'.format(self.host)


def create_app(debug=False, subdomain=None, configobj=None):
    app = Flask(__name__)
    app.debug = debug

    # Default configuration
    app.config.from_object(__name__)

    # Override configuration using config passed into create_app
    if configobj:
        app.config.from_object(configobj)

    # Instantiate stuff using the configuration variables
    app.fake_api_requester = FakeApiRequester(app.config['API_HOST'])
    app.fake_database = FakeDatabase(app.config['DB_SERVER'])

    app.register_blueprint(simple_page)

    return app


class SubdomainDispatcher(object):
    """
    Modified from http://flask.pocoo.org/docs/patterns/appdispatch/#dispatch-by-subdomain

    Creates multiple instances of a Flask application where there is one
    instance per subdomain. This allows each subdomain to run an app
    with its own configuration.

    The instance of this class is an app called by a WSGI handler.

    NOTE: this is only used by the local development server.
    """

    def __init__(self, create_app, domain='', *args, **kwargs):
        """
        :param create_app: a function that returns a `flask.Flask` instance
        :param domain: str - used to determine the subdomain
        :param args: *args passed to create_app
        :param kwargs: **kwargs passed to create_app
        """
        self.create_app = create_app
        self.domain = domain
        self.args = args
        self.kwargs = kwargs
        self.lock = Lock()
        self.instances = {}

    def __call__(self, environ, start_response):
        app = self._get_application(environ['HTTP_HOST'])
        return app(environ, start_response)

    def _get_application(self, host):
        host = host.split(':')[0]
        assert host.endswith(self.domain), 'Configuration error'
        subdomain = host[:-len(self.domain)].rstrip('.')
        with self.lock:
            app = self.instances.get(subdomain)
            if app is None:
                configobj = self._get_subdomain_based_config(subdomain)
                app = self.create_app(
                    configobj=configobj, *self.args, **self.kwargs)
                self.instances[subdomain] = app
            return app

    @staticmethod
    def _get_subdomain_based_config(subdomain):

        class Config(object):
            pass
        config = Config()

        if subdomain == 'dev':
            config.API_HOST = 'dev-host'
            config.DB_SERVER = 'dev-db-server'
        elif subdomain == 'qa':
            config.API_HOST = 'qa-host'
            config.DB_SERVER = 'qa-db-server'

        return config


def rundevserver(host=None, port=None, domain='', debug=True, **options):
    """
    Modified from `flask.Flask.run`

    Runs the application on a local development server.

    :param host: the hostname to listen on. Set this to ``'0.0.0.0'`` to
                 have the server available externally as well. Defaults to
                 ``'127.0.0.1'``.
    :param port: the port of the webserver. Defaults to ``5000``
    :param domain: used to determine the subdomain
    :param debug: if given, enable or disable debug mode.
                  See :attr:`debug`.
    :param options: the options to be forwarded to the underlying
                    Werkzeug server.  See
                    :func:`werkzeug.serving.run_simple` for more
                    information.
    """
    from werkzeug.serving import run_simple

    if host is None:
        host = '127.0.0.1'
    if port is None:
        port = 5000
    options.setdefault('use_reloader', debug)
    options.setdefault('use_debugger', debug)

    app = SubdomainDispatcher(create_app, domain, debug=debug)

    run_simple(host, port, app, **options)


if __name__ == '__main__':
    rundevserver(host='0.0.0.0', port=5000, domain='localhost')
