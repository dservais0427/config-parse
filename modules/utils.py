def strip_quotes(text):
    return text.removeprefix('"').removesuffix('"')


def replace_dash(text):
    return text.replace(' ', '_').replace('-', '_')


def replace_space(text):
    return text.replace(' ', '_').replace('-', '_')


def get_cidr(netmask):
    '''
    :param netmask: netmask ip addr (eg: 255.255.255.0)
    :return: equivalent cidr number to given netmask ip (eg: 24)
    '''
    return sum([bin(int(x)).count('1') for x in netmask.split('.')])


def get_mask(netmask):
    return '.'.join([str((0xffffffff << (32 - netmask) >> i) & 0xff) for i in [24, 16, 8, 0]])


def convertmask(netmask):
    netmask = str(netmask).strip(' /')
    if len(netmask) > 2:
        return sum([bin(int(x)).count('1') for x in netmask.split('.')])
    else:
        return '.'.join([str((0xffffffff << (32 - int(netmask)) >> i) & 0xff) for i in [24, 16, 8, 0]])
