Config Parse

Project consists of several scripts designed to parse the running configuration 
of a switch and place the relevent information into a CSV file that can be 
added to the staging workbook for a project.

The purpose of the scripts is to make sure that we capture consistent and 
acurate information for each device, this information can then be used create 
interface configurations for the new switch using the specific Jinja template 
file for the project.

To use the scripts you will need to run the script that coresponds to the type 
of switch config you will be parsing.
    
    parse_cisco_config.py   - Cisco IOS Switches
    parse_arubaos_config.py - ArubaOS/Procurve Switches
    parse_arubacx_config.py - Aruba-CX Switches
    parse_comware_config.py - HPE Comware Switches
    
The script relies on the Parent/Child relationship of most configuration files, 
if the configuration file does not follow this format it will not work.  This 
issue is typically found with ArubaOS/Procurve switches, newer versions allow 
you to run the command 'show run structured' to get the config in a parsable 
format.  If the switch does not support that command it will not work.  It will 
also have trouble with configs that have no port configurations, in this case 
it will still capture the interfaces and any descriptions, but not much more.
It is still advised to use the script to create the output in a consistent 
format and then manually modify the spreadsheet as needed.  (A solution to this 
issue is currently being worked on.)

The vlanmap.txt file contains the mapping between VLAN and Port Type.  This file 
will need to be populated or all ports will be labeled as a data port.  If the 
script is unable to find a vlan for a port the port type will return '**CHECK**' 
if the vlan is not found in the list, the script will assume it is a data_port.
This way you only need to create mappings for non data ports.  The script will 
use the vlanmap.txt file that is in the same folder as the script, you may also 
specify a different map file on the command line by adding the --vlanmap argument.

Once the correct script is selected simply run the command, select the 
configuration file/files you want to parse and click Ok.  When the script is done 
parsing the file you will find the CSV file in the output folder.  If only one 
file was selected it will automatically open the file for review, if multiple files 
were selected you will need to browse to the output folder and manually open them. 
You can stop the automatic file open process by adding the --noview flag to the 
command line.