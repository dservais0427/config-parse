import csv
import tkinter as tk
from tkinter import filedialog as fd


root = tk.Tk()
root.withdraw()
config = fd.askopenfilenames(title='Select Device Configuration File')


vlanNames = {}

headers = ['interface', 'Type', 'Description', 'Access/Native', 'Voice/Trunk Allowed', 'S/D', 'Shutdown', 'Notes/Extra Commands']

fileList = list(config)

for file in fileList:
    counter = 0
    endArray = []
    hostname = ''

    with open(file) as f:
        for line in f:
            if ' # ' in line:                
                hostname = line.split()[0].split('.')[0]

            if 'Untagged' in line:
                if counter == 0:
                    counter += 1
                    continue
            
                arr = line.split()
                port = counter
                vlan = arr[-1].split('-')[-1]
                if vlan == 'Default':
                    vlan = 1
                counter += 1

                endArray.append([f'interface gi1/0/{port}', 'other', '', f'vlan {vlan}'])



    with open(f'{hostname}.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for item in endArray:
            writer.writerow(item)
