def calculate_cidr_len(mask):
    return sum(bin(int(x)).count('1') for x in mask.split('.'))


def cisco2aruba(interface):
    """
    Convert Cisco interface name to Aruba CX interface name.
    """
    # Split the interface name into parts
    parts = interface.split('/')

    return f"{parts[0][-1]}/1/{parts[2]}"
