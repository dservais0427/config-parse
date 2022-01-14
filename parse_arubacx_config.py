
""" parse_arubacx_config.py: Process configuration file and save interface
    configuration data for use in project staging worksheets.
"""

__author__ = 'David Servais'
__version__ = '1.0'

import csv
import os
try:
    from ciscoconfparse import CiscoConfParse
except ImportError:
    os.system('python -m pip install CiscoConfParse')
    from ciscoconfparse import CiscoConfParse
try:
    import argparse
except ImportError:
    os.system('python -m pip install argarse')
    import argparse
try:
    from pathlib import Path
except ImportError:
    os.system('python -m pip install PathLib')
    from pathlib import Path
try:
    import tkinter as tk
except ImportError:
    os.system('python -m pip install tkinter')
    import tkinter as tk
from tkinter import filedialog

# Process command line

parser = argparse.ArgumentParser(description='Collect interface information \
                                 from config file and store in CSV file.')
parser.add_argument('--config', help='Configuration file to parse.')
parser.add_argument('--outfile', help='CSV filename',
                    default='attribute_file_interface.csv')
args = parser.parse_args()

if args.config is None:
    print('Select Configuration File')
    root = tk.Tk()
    root.withdraw()
    config = filedialog.askopenfilename()
    if config == '':
        exit()
else:
    config = args.config

confparse = CiscoConfParse(config)

hostname = confparse.re_match_iter_typed(r'^hostname\s+(\S+)')
outfile = hostname.upper() + '_interfaces.csv'
outfile = Path(os.environ['TEMP'], outfile)

intf_all = []

# extract the interface details from config file
# get all ethernet interfaces from the configuration file
interface_cmds = confparse.find_objects(r'^interface\s')

# iterate over the resulting IOSCfgLine objects and parse out desired info
for interface_cmd in interface_cmds:
    intf = ['', '', '', '', '', '', '', '']

    # get the interface name
    intf.insert(0, interface_cmd.text.strip())

    # search for the description command
    for cmd in interface_cmd.re_search_children(r"^\s\s\s\sdescription"):
        intf.insert(3, cmd.text.strip())

    for cmd in interface_cmd.re_search_children(r"^\s\s\s\svlan\saccess"):
        intf.insert(4, cmd.text.strip())

    for cmd in interface_cmd.re_search_children(r"^\s\s\s\svlan\strunk\snative"):
        intf.insert(4, cmd.text.strip())

    for cmd in interface_cmd.re_search_children(r"^\s\s\s\svlan\strunk\sallowed"):
        intf.insert(5, cmd.text.strip())

    for cmd in interface_cmd.re_search_children(r"^\s\s\s\sshutdown"):
        intf.insert(7, cmd.text.strip())

    for cmd in interface_cmd.re_search_children(r"^\s\s\s\slag"):
        intf.insert(8, cmd.text.strip())

    # add interface info to the all interface list
    intf_all.append(intf)


# Output data to CSV file
with open(outfile, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, dialect='excel')
    writer.writerow(['Interface', 'New Interface', 'Type', 'Description',
                     'Access/Native', 'Voice/Allowed',
                     'Speed/Duplex', 'Shutdown', 'Commands'])

    for x in intf_all:
        writer.writerow([x[0], x[1], 'data_port', x[3], x[4],
                         x[5], '', x[7], x[8]])

# open csv file for review
os.startfile(outfile)
