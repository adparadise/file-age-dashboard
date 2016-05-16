
import functools

from postgres_database import PostgresDatabase

class DatabaseServiceFactory(object):

    @staticmethod
    def generate(config_section_name=None):
        """
        Return a PostgresDatabase instance modified to participate in
        the service class lifecycle.

        TODO: This is too clever! A service should allow a generator function directly.
        """

        def init_method(config_section_name):
            postgres_database = PostgresDatabase(config_section_name)

            def start_method(runtime):
                assert runtime.config.has_section(config_section_name), "no configuration section defined: %s" % config_section_name
                postgres_database.set_config(runtime.config)
                postgres_database.connect()
            setattr(postgres_database, 'start', start_method)

            return postgres_database

        generator = functools.partial(init_method, config_section_name)
        setattr(generator, 'SERVICE_ALIAS', config_section_name or 'database')

        return generator
