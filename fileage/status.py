import os
import sys
import time

class Status(object):
    """
    Class to find the age of files on disk as a service to other components.
    """

    def __init__(self):
        self._filenames = []

    def add_filename(self, filename):
        self._filenames.append(filename)

    def get_statuses(self):
        statuses = {}

        now = time.time()
        for filename in self._filenames:
            status = {
                'any_info': False,
                'age_seconds': None
            }

            if os.path.exists(filename):
                stat = os.stat(filename);
                status['any_info'] = True
                status['age_seconds'] = now - stat.st_mtime

            statuses[filename] = status

        return statuses

