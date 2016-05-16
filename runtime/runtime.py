
import inspect
import os
import sys
import argparse

from configuration import Config
from log import Log

class Runtime:
    """
    A class to hold all configuration and runtime objects to be used
    by command scripts.
    """

    @staticmethod
    def run_command(CommandClass, deployment_home):
        """
        Create a runtime and run an instance of the @CommandClass with it.

        @param deployment_home - locates our configuration in `deployment_home`/config/<env-name>.ini`.
        See configuration.py.
        """
        runtime = Runtime.build_default(deployment_home, [CommandClass])
        runtime.start()

        runtime.log.set_script_abbrev(CommandClass.SCRIPT_ABBREV)

        command = CommandClass()

        runtime.log.environment_info()
        runtime.log.info('starting script:%s', CommandClass.__name__)
        exit_status = command.run(runtime)
        runtime.log.info('finished script:%s with status: %s', CommandClass.__name__, exit_status)

        # TODO any service cleanup such as transaction commits.

        return exit_status

    @staticmethod
    def run_commands(CommandClasses, deployment_home):
        """
        Create a runtime and run a series of Commands, assuming the
        first's arguments match all others.

        @param deployment_home - locates our configuration in `deployment_home`/config/<env-name>.ini`.
        See configuration.py.
        """
        if len(CommandClasses):
            arg_parser = CommandClasses[0].build_arg_parser()
        else:
            arg_parser = Runtime.__create_placeholder_arg_parser()
        Runtime.add_default_arguments(arg_parser)
        runtime = Runtime.build_default(arg_parser, deployment_home, CommandClasses)

        for CommandClass in CommandClasses:
            CommandClass.register_services(runtime)
        runtime.start()

        for CommandClass in CommandClasses:
            runtime.log.set_script_abbrev(CommandClass.SCRIPT_ABBREV)

            command = CommandClass()

            runtime.log.environment_info()
            runtime.log.info('starting script:%s', CommandClass.__name__)
            exit_status = command.run(runtime)
            runtime.log.info('finished script:%s with status: %s', CommandClass.__name__, exit_status)

            # TODO early exit if status code not 0, if strict, etc.

        # TODO any service cleanup such as transaction commits.
        # TODO return status

    @staticmethod
    def __create_placeholder_arg_parser():
        return argparse.ArgumentParser("An anonymous runtime")

    @staticmethod
    def add_default_arguments(arg_parser):
        arg_parser.add_argument('-e',
                                dest='env_name',
                                default='dev',
                                help='configuration environment name')

        allowed_log_levels = [Log.LEVEL_SILENT,
                              Log.LEVEL_ERROR,
                              Log.LEVEL_WARNING,
                              Log.LEVEL_INFO,
                              Log.LEVEL_VERBOSE,
                              Log.LEVEL_DEBUG]
        arg_parser.add_argument('-l',
                                dest='log_level',
                                help='lowest log level to emit',
                                choices=allowed_log_levels)

    @staticmethod
    def build_default(deployment_home, CommandClasses):
        """
        Create a runtime from the command line arguments and configuration on
        disk.

        If you want something more custom, e.g. in testing, you can build
        it yourself ;)
        """

        if len(CommandClasses):
            arg_parser = CommandClasses[0].build_arg_parser()
        else:
            arg_parser = Runtime.__create_placeholder_arg_parser()
        Runtime.add_default_arguments(arg_parser)

        runtime = Runtime()

        for CommandClass in CommandClasses:
            CommandClass.register_services(runtime)

        for ServiceClass in runtime.each_service_class():
            add_default_arguments_method = getattr(ServiceClass, 'add_default_arguments', None)
            if add_default_arguments_method and callable(add_default_arguments_method):
                ServiceClass.add_default_arguments(arg_parser)

        options = arg_parser.parse_args()
        if not hasattr(options, 'deployment_home'):
            options.deployment_home = deployment_home

        config = Config()
        config.set_options(options)
        try:
            config.read()
        except Exception as e:
            if not hasattr(CommandClass, 'is_config_required') or CommandClass.is_config_required():
                exc_info = sys.exc_info()
                raise e, None, exc_info[2]

        log = Log()
        log.set_options(options)

        runtime.set_options(options)
        runtime.set_config(config)
        runtime.set_log(log)

        return runtime


    def __init__(self):
        self._required_feature_names = []
        self._started_features = set()
        self._service_classes = {}

        self.options = None
        self.config = None
        self.log = None
        self.cluster_database = None
        self.facebook_database = None
        self.ownership_factory = None
        self.facebook_factory = None

    def set_options(self, options):
        self.options = options

    def set_config(self, config):
        self.config = config

    def set_log(self, log):
        self.log = log

    def each_service_class(self):
        for alias, ServiceClass in self._service_classes.iteritems():
            yield ServiceClass

    def register_service(self, ServiceClass):
        alias = ServiceClass.SERVICE_ALIAS
        self._service_classes[alias] = ServiceClass

    def start(self):
        for alias, ServiceClass in self._service_classes.iteritems():
            service = ServiceClass()
            service.start(self)
            self.__dict__[alias] = service
