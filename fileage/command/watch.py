import argparse
import requests
import json
import time

from runtime import Log
from fileage import CursesDashboard
from fileage import Status

class Watch:
    SCRIPT_ABBREV = 'dash'

    def __init__(self):
        self._dashboard = None

    @staticmethod
    def build_arg_parser():
        description = 'Show a colored dashboard indicating the relative age of files.'
        arg_parser = argparse.ArgumentParser(description)
        arg_parser.add_argument('-f',
                                dest='filenames',
                                action='append',
                                required=True,
                                help='filenames to watch')

        return arg_parser

    @staticmethod
    def register_services(runtime):
        pass

    def run(self, runtime):
        status = Status()

        self._dashboard = CursesDashboard()
        self._dashboard.set_status(status)
        if runtime.config.has_option('fileage', 'long_sleep_duration'):
            long_sleep_duration = float(runtime.config.get('fileage', 'long_sleep_duration'))
            self._dashboard.set_long_sleep_duration(long_sleep_duration)
        if runtime.config.has_option('fileage', 'short_sleep_duration'):
            short_sleep_duration = float(runtime.config.get('fileage', 'short_sleep_duration'))
            self._dashboard.set_short_sleep_duration(short_sleep_duration)
        if runtime.config.has_option('fileage', 'short_sleep_period_seconds'):
            short_sleep_period_seconds = float(runtime.config.get('fileage', 'short_sleep_period_seconds'))
            self._dashboard.set_short_sleep_period_seconds(short_sleep_period_seconds)
        if runtime.config.has_option('fileage', 'new_age_seconds'):
            new_age_seconds = float(runtime.config.get('fileage', 'new_age_seconds'))
            self._dashboard.set_new_age_seconds(new_age_seconds)
        if runtime.config.has_option('fileage', 'young_age_seconds'):
            young_age_seconds = float(runtime.config.get('fileage', 'young_age_seconds'))
            self._dashboard.set_young_age_seconds(young_age_seconds)

        print runtime.options.filenames
        for filename in runtime.options.filenames:
            status.add_filename(filename)
            self._dashboard.add_cell(filename)

        if runtime.options.log_level == Log.LEVEL_DEBUG:
            statuses = status.get_statuses()
            runtime.log.debug(json.dumps(statuses, indent=2),
                              prefix="STATUS")
        else:
            self._dashboard.run()
