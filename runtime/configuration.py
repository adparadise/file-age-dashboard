import os
import ConfigParser
import StringIO


class Config:
    """
    Class to read and give access to the configuration options stored on disk.
    """

    def __init__(self):
        self.env_name = None
        self.deployment_home = None
        self.config = None

    def set_options(self, options):
        self.env_name = options.env_name
        self.deployment_home = options.deployment_home

    def config_file_path(self, env_name=None):
        """
        Resolve the path to one configuration file.
        """
        assert self.deployment_home
        assert self.env_name

        if not env_name:
            env_name = self.env_name
        join_paths = (self.deployment_home, "config", "%s.ini" % env_name)
        config_file_path = os.path.join(*join_paths)

        return config_file_path

    def read(self):
        """
        Read the configuration options present on disk.
        """
        env_config_file_path = self.config_file_path()
        if not os.path.isfile(env_config_file_path):
            raise Exception('no config found: %s' % env_config_file_path)

        default_config_file_path = self.config_file_path('default')
        if not os.path.isfile(default_config_file_path):
            message_pattern = 'no default configuration found: %s'
            raise Exception(message_pattern % default_config_file_path)

        self.config = ConfigParser.RawConfigParser()
        self.config.read([default_config_file_path, env_config_file_path])

        return self

    def get(self, *args):
        """
        Get one configuration property from our store.
        """
        value = None
        if self.config and self.config.has_option(*args):
            value = self.config.get(*args)

        return value

    def get_strict(self, *args):
        """
        Get one configuration property from our store, raising an exception if missing
        """
        value = self.config.get(*args)

        return value

    def has_option(self, *args):
        """
        Indicate whether a key is set at the specified location.
        """
        return self.config and self.config.has_option(*args)

    def has_section(self, section_name):
        """
        Indicate whether a section exists in the config.
        """
        return self.config and self.config.has_section(section_name)

    def to_string(self):
        buf = StringIO.StringIO()
        self.config.write(buf)

        return buf.getvalue()

