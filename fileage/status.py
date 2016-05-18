import os
import sys
import time
import re

import constants

class Status(object):
    """
    Class to find the age of files on disk as a service to other components.
    """

    def __init__(self):
        self._filenames = []
        self._success_pattern = None
        self._new_age_seconds = 3
        self._young_age_seconds = 10

    def set_new_age_seconds(self, new_age_seconds):
        self._new_age_seconds = new_age_seconds

    def set_young_age_seconds(self, young_age_seconds):
        self._young_age_seconds = young_age_seconds

    def add_filename(self, filename, success_pattern_string=None):
        self._filenames.append(filename)
        if success_pattern_string:
            self._success_pattern = re.compile(success_pattern_string);

    def get_statuses(self):
        statuses = {}

        now = time.time()
        for filename in self._filenames:
            status = {
                'any_info': False,
                'age_seconds': None,
                'is_success': None
            }

            if os.path.exists(filename):
                stat = os.stat(filename);
                status['any_info'] = True
                status['age_seconds'] = now - stat.st_mtime
                status['is_success'] = self._file_is_success(filename)

            self._compute_status_code(status)

            statuses[filename] = status

        return statuses

    def _compute_status_code(self, status):
        state = constants.States.NO_INFO
        if not status['any_info']:
            state = constants.States.NO_INFO
        elif not status['is_success']:
            state = constants.States.ERROR
        else:
            if status['age_seconds'] < self._new_age_seconds:
                state = constants.States.NEW
            elif status['age_seconds'] < self._young_age_seconds:
                state = constants.States.YOUNG
            else:
                state = constants.States.OLD

        status['state'] = state

    def _file_is_success(self, filename):
        if not self._success_pattern:
            return True

        is_success = False
        with open(filename, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if self._success_pattern.match(line):
                    is_success = True
                    break

        return is_success

