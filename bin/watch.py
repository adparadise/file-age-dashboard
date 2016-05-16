#!/usr/bin/env python

"""
Script to send a GET request to a WordStream endpoint
"""
import inspect
import sys
import os

# Build up the path to our code so that we can import it.
this_file_path = inspect.getfile(inspect.currentframe())
this_file_home = os.path.dirname(this_file_path)
project_home = os.path.join(this_file_home, '..')
project_home = os.path.abspath(project_home)
sys.path.append(project_home)

from runtime import Runtime
from fileage import command

if __name__ == "__main__":
    exit_status = Runtime.run_command(command.Watch, project_home)
    exit(exit_status)




