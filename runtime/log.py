
import binascii
import sys
import os
from datetime import datetime


class Log:
    """
    A class to allow logging in a standard format.
    """
    LEVEL_SILENT = 'silent'
    LEVEL_ERROR = 'error'
    LEVEL_WARNING = 'warning'
    LEVEL_INFO = 'info'
    LEVEL_VERBOSE = 'verbose'
    LEVEL_DEBUG = 'debug'

    SILENT = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    VERBOSE = 4
    DEBUG = 5

    DEFAULT = INFO

    LEVEL_INDICATOR = [
        '    ',
        'ERR ',
        'WARN',
        'INFO',
        'VERB',
        'DBG '
    ]

    def __init__(self):
        self._level = Log.DEFAULT
        self._output_handle = sys.stdout
        self._instance_hash = Log._generate_instance_hash()
        self._script_abbrev = None

    @staticmethod
    def _generate_instance_hash():
        sample = binascii.b2a_hex(os.urandom(15))
        sample = sample[0:4]

        return sample

    def set_script_abbrev(self, script_abbrev):
        self._script_abbrev = script_abbrev

    def set_options(self, options):
        if hasattr(options, 'log_level'):
            self.set_log_level(options.log_level)

        if hasattr(options, 'log_filename'):
            output_filename = options.log_filename
            self.set_output_filename(output_filename)

    def set_log_level(self, log_level):
        level = Log.resolve_log_level(log_level)
        if level is not None:
            self._level = level

    def set_output_filename(self, output_filename):
        output_handle = open(output_filename, 'w')
        self.set_output_handle(output_handle)

    def set_output_handle(self, output_handle):
        self._output_handle = output_handle

    def set_instance_hash(self, instance_hash):
        self._instance_hash = instance_hash

    def environment_info(self):
        self.info('python_version:%d.%d.%d',
                  sys.version_info.major,
                  sys.version_info.minor,
                  sys.version_info.micro)

    def error(self, message, *args, **kwargs):
        self.log(Log.ERROR, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self.log(Log.WARNING, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self.log(Log.INFO, message, *args, **kwargs)

    def verbose(self, message, *args, **kwargs):
        self.log(Log.VERBOSE, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self.log(Log.DEBUG, message, *args, **kwargs)

    def log(self, level, message, *args, **kwargs):
        if level > self._level:
            return

        if len(args) == 0:
            message_string = message
        else:
            if len(args) == 1:
                args = args[0]
            message_string = message % args

        message_string_lines = message_string.split("\n")

        prefix = self._format_prefix(level, **kwargs)
        for line in message_string_lines:
            self._output_handle.write("%s  %s\n" % (prefix, line))

    def _format_prefix(self, level, **kwargs):
        timestamp = datetime.now().isoformat()
        level_indicator = Log.LEVEL_INDICATOR[level]
        output_payload = [timestamp, self._script_abbrev, self._instance_hash, level_indicator]
        output_format = "%s %s_%s %s"
        if 'prefix' in kwargs:
            output_format = "%s %%s" % output_format
            output_payload.append(kwargs['prefix'])

        output_string = output_format % tuple(output_payload)

        return output_string

    @staticmethod
    def resolve_log_level(log_level):
        LOG_LEVELS = {
            'silent':   Log.SILENT,
            'error':    Log.ERROR,
            'warning':  Log.WARNING,
            'info':     Log.INFO,
            'verbose':  Log.VERBOSE,
            'debug':    Log.DEBUG
        }

        level = None
        if log_level in LOG_LEVELS:
            level = LOG_LEVELS[log_level]

        return level
