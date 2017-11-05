import os
import subprocess
import sys

# Open the file in the default application
# From: https://stackoverflow.com/a/434612/2337254
def open_in_default_app(filename):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filename))
    elif os.name == 'nt':
        os.startfile(filename)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filename))