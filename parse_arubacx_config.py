
"""
    parse_arubacx_config.py: Process configuration file and save interface
    configuration data for use in project staging worksheets.
"""

__author__ = 'David Servais'
__version__ = '0.1.2'

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
from tkinter import filedialog as fd

# Process command line
parser = argparse.ArgumentParser(description='Collect interface information \
                                 from config file and store in CSV file.')
parser.add_argument('--config', help='Configuration file to parse.')
parser.add_argument('--vlanmap',
                    help='Text file containing vlan to port type mappings',
                    default='vlanmap.txt')
parser.add_argument('--outfile', help='CSV filename',
                    default='attribute_file_interface.csv')

args = parser.parse_args()

if args.config is None:
    root = tk.Tk()
    root.withdraw()
    config = fd.askopenfilenames(title='Select Router Configuration File')
    if config == '':
        exit()
else:
    config = args.config

if args.vlanmap is None:
    vlanmap = 'vlanmap.txt'
else:
    vlanmap = args.vlanmap


# Define script functions
def defineVlans():
    vlans = {}

    with open(vlanmap, 'r') as f:
        for x in f:
            (k, v) = x.split(',')
            vlans[k] = v.strip()

    return vlans


def checkKey(vlan, key):
    if key == '':
        return '**CHECK**'
    elif key.startswith('ip'):
        return 'routed'
    elif not checkVlan:
        return ''
    else:
        key = key.split()[-1]

        if key in vlan.keys():
            return vlan[key]
        else:
            return 'data_port'


# Define global variables
RE_INTERFACE = r'^interface(.+?thernet|.+?ort-[Cc]hannel|.+?oopback)'
RE_HOSTNAME = r'^hostname\s+(\S+)'
RE_PTYPE = r'^\s+routing|^\s+vlan\saccess|^\s+vlan\strunk\snative'
RE_SWACCESS = r'^\s+vlan\saccess'
RE_SWNATIVE = r'^\s+vlan\strunk\snative'
RE_SWTRUNK = r'^\s+vlan\strunk\sallowed'


if os.path.exists('vlanmap.txt'):
    vlans = defineVlans()
    checkVlan = True
else:
    checkVlan = False

file_list = list(config)

for x in file_list:
    # Begin processing
    confparse = CiscoConfParse(x)

    hostname = confparse.re_match_iter_typed(RE_HOSTNAME)
    outfile = hostname.upper() + '_interfaces.csv'
    outfile = Path('output', outfile)

    intf_all = []

    # extract the interface details from config file
    # get all ethernet interfaces from the configuration file
    interface_cmds = confparse.find_objects(r'^interface\s')

    # iterate over the resulting IOSCfgLine objects and parse out desired info
    for intf_cmd in interface_cmds:
        intf = ['', '', '', '', '', '', '', '']
        intShut, vlAllow, vlAccess, intDesc = '', '', '', ''
        vlanCmd, exCmd, stpCmd, portsecCmd = [], [], [], []
        sdplxCmd, qosCmd, ipCmd, rtrCmd = [], [], [], []

        # get the interface name
        intf.insert(0, intf_cmd.text.strip())

        # search for the description command
        for cmd in intf_cmd.re_search_children(r'^\s+description'):
            intDesc = cmd.text.strip()[12:]

        # determine if this is a trunk or access port and capture specific info
        for cmd in intf_cmd.re_search_children(RE_PTYPE):

            if cmd.text.strip().startswith('vlan access'):
                for cmd1 in intf_cmd.re_search_children(RE_SWACCESS):
                    vlAccess = cmd1.text.strip()

            elif cmd.text.strip().startswith('vlan trunk native'):
                for cmd1 in intf_cmd.re_search_children(RE_SWNATIVE):
                    vlAccess = cmd1.text.strip()

                for cmd2 in intf_cmd.re_search_children(RE_SWTRUNK):
                    vlanCmd.append(cmd2.text.strip())

                if len(vlanCmd) > 1:
                    vlanStr = 'vlan trunk allowed ' \
                        + vlanCmd[0].split()[-1]
                    for x in range(1, len(vlanCmd)):
                        vlanStr += ',' + vlanCmd[x].split()[-1]
                    vlAllow = vlanStr
                else:
                    vlAllow = ','.join(vlanCmd)

            else:
                for cmd1 in intf_cmd.re_search_children(r'^\s+ip\saddress'):
                    ipCmd.append(cmd1.text.strip())
                vlAccess = ','.join(ipCmd)

        for cmd in intf_cmd.re_search_children(r'^\s+shutdown'):
            intShut = cmd.text.strip()

        for cmd in intf_cmd.re_search_children(r"^\sspeed|^\sduplex"):
            sdplxCmd.append(cmd.text.strip())

        for cmd in intf_cmd.re_search_children(r'^\s+lag'):
            exCmd.append(cmd.text.strip())

        for cmd in intf_cmd.re_search_children(r'^\s+lacp|^\s+dhcp|^\s+udld'):
            exCmd.append(cmd.text.strip())

        for cmd in intf_cmd.re_search_children(r'^\s+spanning-tree'):
            stpCmd.append(cmd.text.strip())

        for cmd in intf_cmd.re_search_children(r'^\s+loop-protect+'):
            exCmd.append(cmd.text.strip())

        for cmd in intf_cmd.re_search_children(r'^\s+ip\sospf'):
            rtrCmd.append(cmd.text.strip())

        intf.insert(2, checkKey(vlans, vlAccess))
        intf.insert(3, intDesc)
        intf.insert(4, vlAccess)
        intf.insert(5, vlAllow)
        intf.insert(6, ','.join(sdplxCmd))
        intf.insert(7, intShut)
        intf.insert(8, ','.join(exCmd))
        intf.insert(9, ','.join(stpCmd))
        intf.insert(10, '')     # ','.join(qosCmd))
        intf.insert(11, ','.join(rtrCmd))

        # add interface info to the all interface list
        intf_all.append(intf)

    # Output data to CSV file
    with open(outfile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(['Interface', 'Switch Name', 'New Interface', 'Type',
                         'Description', 'Access/Native', 'Voice/Allowed',
                         'Speed/Duplex', 'Shutdown', 'Commands', 'STP',
                         'QOS', 'Routing'])

        for x in intf_all:
            writer.writerow([x[0], '', x[1], checkKey(vlans, x[4].strip()),
                             x[3], x[4], x[5], x[6], x[7], x[8], x[9],
                             x[10], x[11]])

    # open csv file for review
    os.startfile(outfile)
