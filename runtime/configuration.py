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
        self.dotfile_dirname = None
        self._dotfile_name = None
        self._cwd = None

    def set_dotfile_name(self, dotfile_name):
        self._dotfile_name = dotfile_name

    def set_cwd(self, cwd):
        self._cwd = cwd

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

    def _resolve_dotfile_path(self):
        """
        March up our directories to find a matching dotfile, if appropriate.
        """
        if not self._dotfile_name:
            return

        current = self._cwd
        found_dotfile_path = None
        while True:
            dotfile_path = os.path.join(current, self._dotfile_name)
            if os.path.exists(dotfile_path):
                found_dotfile_path = dotfile_path
                break
            next = os.path.dirname(current)
            if next == current:
                break
            current = next

        return found_dotfile_path


    def read(self):
        """
        Read the configuration options present on disk.
        """
        config_filenames = []

        dotfile_path = self._resolve_dotfile_path()
        if dotfile_path:
            config_filenames.append(dotfile_path)
            self.dotfile_dirname = os.path.dirname(dotfile_path)
        else:
            default_config_file_path = self.config_file_path('default')
            if os.path.isfile(default_config_file_path):
                config_filenames.append(default_config_file_path)

            env_config_file_path = self.config_file_path()
            if not os.path.isfile(env_config_file_path):
                raise Exception('no config found: %s' % env_config_file_path)
            config_filenames.append(env_config_file_path)

        self.config = ConfigParser.RawConfigParser()
        self.config.read(config_filenames)

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

    def each_in_section(self, section_name):
        """
        Generator iterating over all key/value pairs in a section.
        """
        if not self.has_section(section_name):
            return

        for key, value in self.config.items(section_name):
            yield(key, value)

    def to_string(self):
        buf = StringIO.StringIO()
        self.config.write(buf)

        return buf.getvalue()

