#
# parse_comware_config.py

import csv
import os
try:
    import customvlan as vlan
    chackVlan = True
except ImportError:
    checkVlan = False
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


def list2string(listobj):
    s = ''
    for x in listobj:
        s += x.strip() + ','

    return s[:-1]


def checkKey(vlan, key):
    if key == '':
        return 'uplink'
    if not checkVlan:
        return ''

    key = key.split()[-1]

    if key in vlan.keys():
        return vlan[key]
    else:
        return 'data_port'


if checkVlan:
    vlans = vlan.defineVlans()

confparse = CiscoConfParse(config)

hostname = confparse.re_match_iter_typed(r'^sysname\s+(\S+)')
outfile = hostname.upper() + '_interfaces.csv'
outfile = Path(os.environ['TEMP'], outfile)

intf_all = []

# extract the interface details from config file
# get all ethernet interfaces from the configuration file
interface_cmds = confparse.find_objects(r'^interface(.+?thernet|.+?Bridge-Aggregation)')

# iterate over the resulting IOSCfgLine objects and parse out desired info
for interface_cmd in interface_cmds:
    intf = ['', '', '', '', '', '', '', '', '', '', '']
    vlanCmd = []
    exCmd = []
    stpCmd = []
    portsecCmd = []
    sdplxCmd = []
    qosCmd = []

    # get the interface name
    intf_name = interface_cmd.text[len('interface '):]
    intf.insert(0, intf_name)

    # search for the description command
    for cmd in interface_cmd.re_search_children(r'^\sdescription'):
        intf.insert(3, cmd.text.strip())

    # determine if this is a trunk or access port and capture specific info
    for cmd in interface_cmd.re_search_children(r'^\sport\slink-type'):

        if cmd.text == ' port link-type access':
            for cmd1 in interface_cmd.re_search_children(r'^\sport\saccess\svlan'):
                intf.insert(4, cmd1.text.strip())
        else:
            for cmd1 in interface_cmd.re_search_children(r'\sport\strunk\snative'):
                intf.insert(4, cmd1.text.strip())

            for cmd2 in interface_cmd.re_search_children(r'\sport\strunk\spermit'):
                vlanCmd.append(cmd2.text.strip())
            if len(vlanCmd) > 1:
                vlanStr = 'port trunk permit vlan ' + vlanCmd[0].split()[-1]
                for x in range(1, len(vlanCmd)):
                    vlanStr += ',' + vlanCmd[x].split()[-1]
                intf.insert(5, vlanStr)
            else:
                intf.insert(5, list2string(vlanCmd))

    for cmd in interface_cmd.re_search_children(r'^\sshutdown'):
        intf.insert(6, cmd.text.strip())

    for cmd in interface_cmd.re_search_children(r"^\sspeed|^\sduplex"):
        sdplxCmd.append(cmd.text.strip())

    # Process additional commands
    for cmd in interface_cmd.re_search_children(r'\sport\slink-aggregation'):
        exCmd.append(cmd.text.strip())

    for cmd in interface_cmd.re_search_children(r'^\sstp'):
        stpCmd.append(cmd.text.strip())

    intf.insert(7, list2string(sdplxCmd))
    intf.insert(8, list2string(exCmd))
    intf.insert(9, list2string(stpCmd))
    intf.insert(10, list2string(qosCmd))
    intf.insert(11, list2string(portsecCmd))

    # add interface info to the all interface list
    intf_all.append(intf)


# Output data to CSV file
with open(outfile, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, dialect='excel')
    writer.writerow(['Interface', 'New Interface', 'Type', 'Description',
                     'Access/Native', 'Voice/Allowed',
                     'Shutdown', 'Speed/Duplex', 'Commands',
                     'STP', 'QOS', 'Port Security'])

    for x in intf_all:
        writer.writerow([x[0], x[1], checkKey(vlans, x[4]),
                         x[3], x[4], x[5], x[6], x[7], x[8], x[9],
                         x[10], x[11]])

# open csv file for review
os.startfile(outfile)
