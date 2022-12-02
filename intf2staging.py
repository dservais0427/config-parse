
"""
    intf2staging.py: Add interface CSV files to existing
    staging workbook.

"""

__author__ = 'David Servais'
__version__ = '0.0.1'

import csv
import os
import re

try:
    from pathlib import Path
except ImportError:
    os.system('python -m pip install PathLib')
    from pathlib import Path
try:
    import pandas as pd
except ImportError:
    os.system('python -m pip install Pandas')
    import pandas as pd
try:
    import tkinter as tk
except ImportError:
    os.system('python -m pip install tkinter')
    import tkinter as tk
from tkinter import filedialog as fd

from openpyxl import load_workbook

root = tk.Tk()
root.withdraw()
int_files = fd.askopenfilenames(title='Select Interface CSV Files')
if int_files == '':
    exit()
root = tk.Tk()
root.withdraw()
staging_wb = fd.askopenfilename(title='Select Staging Workbook')
if staging_wb == '':
    exit()

# writer = pd.ExcelWriter(staging_wb)

file = staging_wb
book = load_workbook(file)
writer = pd.ExcelWriter(file, engine='openpyxl')
writer.book = book

sheet = os.path.splitext(os.path.basename(int_files[0]))[0]

print(sheet)
pd.read_csv(int_files[0]).to_excel(writer, sheet)
writer.save()
