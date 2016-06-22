import argparse
import json
import os
import re
import sys
import time

from runtime import Log
from fileage import CursesDashboard
from fileage import Status

class Watch:
    SCRIPT_ABBREV = 'dash'
    CONFIG_SECTION_NAME = 'fileage'
    DOTFILE_NAME = '.fileage'

    def __init__(self):
        self._dashboard = None

    @staticmethod
    def build_arg_parser():
        description = 'Show a colored dashboard indicating the relative age of files.'
        arg_parser = argparse.ArgumentParser(description)
        arg_parser.add_argument('-f',
                                dest='filenames',
                                action='append',
                                help='filenames to watch')
        arg_parser.add_argument('-s',
                                dest='success_pattern_string',
                                help='regexp indicating a successful build')

        return arg_parser

    @staticmethod
    def register_services(runtime):
        pass

    @staticmethod
    def is_config_required():
        return False

    def run(self, runtime):
        status = Status()

        self._dashboard = CursesDashboard()
        self._dashboard.set_status(status)
        if runtime.config.has_option(Watch.CONFIG_SECTION_NAME, 'long-sleep-duration'):
            long_sleep_duration = float(runtime.config.get(Watch.CONFIG_SECTION_NAME, 'long-sleep-duration'))
            self._dashboard.set_long_sleep_duration(long_sleep_duration)
        if runtime.config.has_option(Watch.CONFIG_SECTION_NAME, 'short-sleep-duration'):
            short_sleep_duration = float(runtime.config.get(Watch.CONFIG_SECTION_NAME, 'short-sleep-duration'))
            self._dashboard.set_short_sleep_duration(short_sleep_duration)
        if runtime.config.has_option(Watch.CONFIG_SECTION_NAME, 'short-sleep-period-seconds'):
            short_sleep_period_seconds = float(runtime.config.get(Watch.CONFIG_SECTION_NAME, 'short-sleep-period-seconds'))
            self._dashboard.set_short_sleep_period_seconds(short_sleep_period_seconds)
        if runtime.config.has_option(Watch.CONFIG_SECTION_NAME, 'new-age-seconds'):
            new_age_seconds = float(runtime.config.get(Watch.CONFIG_SECTION_NAME, 'new-age-seconds'))
            status.set_new_age_seconds(new_age_seconds)
        if runtime.config.has_option(Watch.CONFIG_SECTION_NAME, 'young-age-seconds'):
            young_age_seconds = float(runtime.config.get(Watch.CONFIG_SECTION_NAME, 'young-age-seconds'))
            status.set_young_age_seconds(young_age_seconds)

        watch_files = self._extract_watch_files(runtime)

        if not watch_files:
            runtime.log.error("No files to watch - Supply the `-f` option or configure files to watch in `config/dev.ini`.")
            return

        for watch_file in watch_files:
            status.add_filename(watch_file['filename'], watch_file['success-pattern-string'])
            self._dashboard.add_cell(watch_file['filename'], watch_file['label'])

        if runtime.options.log_level == Log.LEVEL_DEBUG:
            runtime.log.debug(json.dumps(watch_files, indent=2),
                              prefix="WATCH_FILES")
            statuses = status.get_statuses()
            runtime.log.debug(json.dumps(statuses, indent=2),
                              prefix="STATUS")
        else:
            self._dashboard.run()


    def _extract_watch_files(self, runtime):
        filename_pattern = re.compile('^(.*)-filename$')
        absolute_path_pattern = re.compile('^/')

        global_success_pattern = None
        if runtime.config.has_option(Watch.CONFIG_SECTION_NAME, 'global-success-pattern'):
            global_success_pattern = runtime.config.get(Watch.CONFIG_SECTION_NAME, 'global-success-pattern')

        filename_prefix = None
        if runtime.config.has_option(Watch.CONFIG_SECTION_NAME, 'filename-prefix'):
            filename_prefix = runtime.config.get(Watch.CONFIG_SECTION_NAME, 'filename-prefix')
        elif runtime.config.dotfile_dirname:
            filename_prefix = runtime.config.dotfile_dirname

        watch_files = []
        for key, value in runtime.config.each_in_section(Watch.CONFIG_SECTION_NAME):
            match = filename_pattern.match(key)
            if match:
                label = match.group(1)
                filename = value
                success_pattern_string = None
                success_pattern_key = '%s-success-pattern' % label
                if runtime.config.has_option(Watch.CONFIG_SECTION_NAME, success_pattern_key):
                    success_pattern_string = runtime.config.get(Watch.CONFIG_SECTION_NAME, success_pattern_key)

                watch_files.append({
                    'label': label,
                    'filename': filename,
                    'success-pattern-string': success_pattern_string
                })

        if runtime.options.filenames:
            for filename in runtime.options.filenames:
                watch_files.append({
                    'label': filename,
                    'filename': filename,
                    'success-pattern-string': runtime.options.success_pattern_string
                })

        if filename_prefix:
            for watch_file in watch_files:
                if not absolute_path_pattern.match(watch_file['filename']):
                    watch_file['filename'] = os.path.join(filename_prefix, watch_file['filename'])

        return watch_files
