
""" redact_config.py: Removes sensitive information from
    configuration files.
"""

__author__ = 'David Servais'
__version__ = '1.0'

import os
import re
from pathlib import Path
try:
    import tkinter as tk
except ImportError:
    os.system('python -m pip install tkinter')
    import tkinter as tk
from tkinter import filedialog as fd

regx = r'(.*ciphertext\s|.*key\s[057]\s|.*community\s|.*password\s[057]\s|.*md5\s[057]\s|.*secret\s[057]\s|.*key\s|.*password\scipher\s)(\S+)(.*)'

root = tk.Tk()
root.withdraw()
config_file = fd.askopenfilename(title='Select Router Configuration File')
if config_file == '':
    exit()

p = Path(config_file)

config_redact = str(p.parent) + '\\' + p.stem + '_redacted' + p.suffix

r = open(config_redact, 'w')
f = open(config_file, 'r')
cfg = f.readlines()

for x in cfg:
    tmp = re.search(regx, x)
    if tmp is None:
        r.write(x)
    else:
        print(tmp.group(1) + '[ --REDACTED-- ]' + tmp.group(3))
        r.write(tmp.group(1) + '[ --REDACTED-- ]' + tmp.group(3) + '\n')

f.close()
r.close()

os.startfile(config_redact)
