#!/usr/bin/env python

import signal
import sys
import curses
import math
from curses import textpad
import time
import datetime

import constants

class CursesDashboard(object):
    NO_INFO_COLOR = 1
    NEW_COLOR = 2
    YOUNG_COLOR = 3
    OLD_COLOR = 4
    ERROR_COLOR = 5

    def __init__(self):
        self._stdscr = None
        self._is_signal_handler_installed = False
        self._cells = []
        self._status = None

        self._long_sleep_duration = 0.7
        self._short_sleep_duration = 0.3
        self._short_sleep_period_seconds = 3

    def add_cell(self, filename, label=None):
        cell = {
            'filename': filename,
            'label': label or filename,
            'window': None
        }
        self._cells.append(cell)

    def set_status(self, status):
        self._status = status

    def set_long_sleep_duration(self, long_sleep_duration):
        self._long_sleep_duration = long_sleep_duration

    def set_short_sleep_duration(self, short_sleep_duration):
        self._short_sleep_duration = short_sleep_duration

    def set_short_sleep_period_seconds(self, short_sleep_period_seconds):
        self._short_sleep_period_seconds = short_sleep_period_seconds

    def run(self):
        assert self._status, "no status helper object set."

        try:
            self._setup()
            self._install_signal_handler()

            sleep_duration = self._short_sleep_duration
            time_last_changed = datetime.datetime.now()

            while True:
                if not self._stdscr:
                    break
                any_changes = self._update_status()
                now = datetime.datetime.now()
                if any_changes:
                    time_last_changed = now
                time_since_changed = now - time_last_changed
                if time_since_changed.seconds > self._short_sleep_period_seconds:
                    sleep_duration = self._long_sleep_duration
                else:
                    sleep_duration = self._short_sleep_duration
                self._redraw()
                time.sleep(sleep_duration)
        except Exception as exception:
            exc_info = sys.exc_info()
            self._teardown()
            raise exc_info[1], None, exc_info[2]

        self._teardown()

    def _setup(self):
        self._setup_curses()
        self._setup_colors()
        self._setup_cell_windows()

    def _setup_curses(self):
        self._stdscr = curses.initscr()
        self._stdscr.keypad(1)
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

    def _teardown(self):
        self._teardown_curses()

    def _teardown_curses(self):
        if not self._stdscr:
            return
        self._stdscr.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        curses.curs_set(1)
        self._stdscr = None

    def _setup_colors(self):
        curses.init_pair(CursesDashboard.NO_INFO_COLOR, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(CursesDashboard.NEW_COLOR, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(CursesDashboard.YOUNG_COLOR, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(CursesDashboard.OLD_COLOR, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(CursesDashboard.ERROR_COLOR, curses.COLOR_BLACK, curses.COLOR_RED)

    def _setup_cell_windows(self):
        min_cell_width = 20
        cell_count = len(self._cells)

        (total_height, total_width) = self._stdscr.getmaxyx()

        cells_per_row = 1
        cells_per_col = math.ceil(cell_count / cells_per_row) or 1

        cell_height = int(math.floor(total_height / cells_per_col))
        cell_width = int(math.floor(total_width / cells_per_row))
        for index, cell in enumerate(self._cells):
            cell['height'] = cell_height
            cell['width'] = cell_width
            cell['row'] = int(math.floor(index / cells_per_row) * cell_height)
            cell['col'] = (index % cells_per_row) * cell_width
            cell['state'] = CursesDashboard.NO_INFO_COLOR
            win = self._stdscr.subwin(cell['height'], cell['width'], cell['row'], cell['col'])
            cell['window'] = win

    def _install_signal_handler(self):
        if self._is_signal_handler_installed:
            return

        def signal_handler(signal, frame):
            self._teardown()
        signal.signal(signal.SIGINT, signal_handler)
        self._is_signal_handler_installed = True

    def _update_status(self):
        statuses = self._status.get_statuses()
        any_changes = False
        for cell in self._cells:
            filename = cell['filename']
            state = CursesDashboard.NO_INFO_COLOR
            if filename in statuses:
                status = statuses[filename]
                if status['state'] == constants.States.NO_INFO:
                    state = CursesDashboard.NO_INFO_COLOR
                elif status['state'] == constants.States.NEW:
                    state = CursesDashboard.NEW_COLOR
                elif status['state'] == constants.States.YOUNG:
                    state = CursesDashboard.YOUNG_COLOR
                elif status['state'] == constants.States.OLD:
                    state = CursesDashboard.OLD_COLOR
                elif status['state'] == constants.States.ERROR:
                    state = CursesDashboard.ERROR_COLOR

            if cell['state'] != state:
                any_changes = True

            cell['state'] = state

        return any_changes

    def _redraw(self):
        if len(self._cells) == 0:
            self._stdscr.addstr(0, 0, "No cells added to dashboard... nothing to display.", 0)

        for index, cell in enumerate(self._cells):
            linenum = 0
            cell['window'].addstr(linenum, 0, cell['label'], cell['state'])
            linenum += 1
            if cell['label'] != cell['filename']:
                cell['window'].addstr(linenum, 0, cell['filename'], cell['state'])
                linenum += 1
            if index == 0:
                now = datetime.datetime.now()
                cell['window'].addstr(linenum, 0, now.isoformat(), cell['state'])
            self._fill_cell(cell)
            cell['window'].refresh()

    def _fill_cell(self, cell):
        win = cell['window']
        win.bkgd(curses.color_pair(cell['state']))

