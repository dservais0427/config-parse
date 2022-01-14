
""" parse_cisco_config.py: Process configuration file and save interface
    configuration data for use in project staging worksheets.
"""

__author__ = 'David Servais'
__version__ = '1.0'

import csv
import os
import re
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
import openpyxl

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
    root.title('Select Router Configuration File')
    root.withdraw()
    config = fd.askopenfilename(title='Select Router Configuration File')
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
        return 'uplink'
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
RE_PTYPE = r'^\s(switchport\smode|no\sswitchport)'
RE_SWVOICE = r'^\sswitchport\svoice\svlan'
RE_SWACCESS = r'^\sswitchport\saccess\svlan'
RE_SWNATIVE = r'^\sswitchport\strunk\snative\svlan'
RE_SWTRUNK = r'^\sswitchport\strunk\sallowed\svlan'

# Determine if we are using a vlan map file
if os.path.exists('vlanmap.txt'):
    vlans = defineVlans()
    checkVlan = True
else:
    checkVlan = False

# Begin processing
confparse = CiscoConfParse(config)

hostname = confparse.re_match_iter_typed(RE_HOSTNAME)
outfile = hostname.upper() + '_interfaces.xlsx'
outfile = Path(os.environ['TEMP'], outfile)

intf_all = []

# extract thce interface details from config file
# get all ethernet interfaces from the configuration file
intf_cmds = confparse.find_objects(RE_INTERFACE)

# iterate over the resulting IOSCfgLine objects and parse out desired info
for intf_cmd in intf_cmds:
    intf = ['', '', '', '', '', '', '', '', '', '', '']
    vlanCmd = []
    exCmd = []
    stpCmd = []
    portsecCmd = []
    sdplxCmd = []
    qosCmd = []
    ipCmd = []
    rtrCmd = []
    intShut = ''
    vlAllow = ''
    vlAccess = ''
    intDesc = ''

    # get the interface name
    intf_name = intf_cmd.text[len("interface "):]
    intf.insert(0, intf_name)

    # search for the description command
    for cmd in intf_cmd.re_search_children(r"^\sdescription"):
        intDesc = cmd.text.strip()

    #  intf_name.startswith('lo'):
    if re.match(r'[L|l]oopback', intf_name) is not None:
        for cmd1 in intf_cmd.re_search_children(r'^\sip\saddress'):
            ipCmd.append(cmd1.text.strip())
        vlAccess = ','.join(ipCmd)

    # determine if this is a trunk or access port and capture specific info
    for cmd in intf_cmd.re_search_children(RE_PTYPE):

        if cmd.text == ' switchport mode access':
            for cmd1 in intf_cmd.re_search_children(RE_SWACCESS):
                vlAccess = cmd1.text.strip()

            for cmd2 in intf_cmd.re_search_children(RE_SWVOICE):
                vlAllow = cmd2.text.strip()

        elif cmd.text == ' switchport mode trunk':
            for cmd1 in intf_cmd.re_search_children(RE_SWNATIVE):
                vlAccess = cmd1.text.strip()

            for cmd2 in intf_cmd.re_search_children(RE_SWTRUNK):
                vlanCmd.append(cmd2.text.strip())

            if len(vlanCmd) > 1:
                vlanStr = 'switchport trunk allowed vlan ' \
                    + vlanCmd[0].split()[-1]
                for x in range(1, len(vlanCmd)):
                    vlanStr += ',' + vlanCmd[x].split()[-1]
                vlAllow = vlanStr
            else:
                vlAllow = ','.join(vlanCmd)

        else:
            for cmd1 in intf_cmd.re_search_children(r'^\sip\saddress'):
                ipCmd.append(cmd1.text.strip())
            vlAccess = ','.join(ipCmd)

    for cmd in intf_cmd.re_search_children(r"^\sshutdown"):
        intShut = cmd.text.strip()

    for cmd in intf_cmd.re_search_children(r"^\sspeed|^\sduplex"):
        sdplxCmd.append(cmd.text.strip())

    for cmd in intf_cmd.re_search_children(r"^\sswitchport\snonegotiate"):
        exCmd.append(cmd.text.strip())

    # Process additional commands
    for cmd in intf_cmd.re_search_children(r"^\schannel-group"):
        exCmd.append(cmd.text.strip())

    for cmd in intf_cmd.re_search_children(r'^\sudld+'):
        exCmd.append(cmd.text.strip())

    for cmd in intf_cmd.re_search_children(r'^\saccess-group'):
        exCmd.append(cmd.text.strip())

    for cmd in intf_cmd.re_search_children(r'^\sip\sdhcp'):
        exCmd.append(cmd.text.strip())

    for cmd in intf_cmd.re_search_children(r'^\sspanning-tree'):
        stpCmd.append(cmd.text.strip())

    for cmd in intf_cmd.re_search_children(r'^\sswitchport\sport-security+'):
        portsecCmd.append(cmd.text.strip())

    # Process routing commands
    for cmd in intf_cmd.re_search_children(r'^\sip\s(eigrp|ospf)'):
        rtrCmd.append(cmd.text.strip())

    # Process IGMP commands
    for cmd in intf_cmd.re_search_children(r'^\sip\spim'):
        exCmd.append(cmd.text.strip())

    # Process AutoQOS commands
    for cmd in intf_cmd.re_search_children(r'^(\sauto|^\smls)\sqos'):
        qosCmd.append(cmd.text.strip())

    for cmd in intf_cmd.re_search_children(r'^\strust\sdevice'):
        qosCmd.append(cmd.text.strip())
    intf.insert(2, checkKey(vlans, vlAccess))
    intf.insert(3, intDesc)
    intf.insert(4, vlAccess)
    intf.insert(5, vlAllow)
    intf.insert(6, ','.join(sdplxCmd))
    intf.insert(7, intShut)
    intf.insert(8, ','.join(exCmd))
    intf.insert(9, ','.join(stpCmd))
    intf.insert(10, ','.join(qosCmd))
    intf.insert(11, ','.join(rtrCmd))
    intf.insert(12, ','.join(portsecCmd))

    # add interface info to the all interface list
    intf_all.append(intf)


def writeHeader():
    sheet['A1'] = 'Interface'
    sheet['B1'] = 'New Interface'
    sheet['C1'] = 'Port Type'
    sheet['D1'] = 'Description'
    sheet['E1'] = 'Access/Native'
    sheet['F1'] = 'Voice/Allowed'
    sheet['G1'] = 'Speed/Duplex'
    sheet['H1'] = 'Shutdown'
    sheet['I1'] = 'Commands'
    sheet['J1'] = 'STP'
    sheet['K1'] = 'QOS'
    sheet['L1'] = 'Routing'
    sheet['M1'] = 'Port Security'


def addRow(intf, row):
    xlRow = 'ABCDEFGHIJKLM'
    y = 0

    for x in xlRow:
        sheet[x + str(row)] = intf[y]
        y += 1


mywb = openpyxl.Workbook()
sheet = mywb.active
sheet.title = hostname

writeHeader()
count = 2
for ointf in intf_all:
    
    print(ointf)
    print(count)
    addRow(ointf, count)
    count = count + 1


mywb.save(outfile)

"""
# Output data to CSV file
with open(outfile, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, dialect='excel')
    writer.writerow(['Interface', 'New Interface', 'Type', 'Description',
                     'Access/Native', 'Voice/Allowed',
                     'Speed/Duplex', 'Shutdown', 'Commands',
                     'STP', 'QOS', 'Routing', 'Port Security'])

    for x in intf_all:
        writer.writerow([x[0], x[1], checkKey(vlans, x[4].strip()),
                         x[3], x[4], x[5], x[6], x[7], x[8], x[9],
                         x[10], x[11], x[12], x[13], x[14]])

"""

# open csv file for review
os.startfile(outfile)
