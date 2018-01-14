"""
Utility functions for converting ip addresses and team numbers and more
"""

import re
import struct
import socket


def ip2int(addr):
    """
    Convert an ip address to its integer representation
    """
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    """
    Convert an integer to a string-based ip address notation
    """
    return socket.inet_ntoa(struct.pack("!I", addr))


def team2ip(team):
    """
    Return the string-based ip address for a team id.
    IP addresses start at 172.31.129.0 (for team 0) and use ip address .0 - .253
    """
    team_subnet = team // 254
    return '172.31.%d.%d' % (129 + team_subnet, (team + team_subnet) % 255)


IP_BASE = ip2int('172.31.129.0')


def ip2team(addr):
    """
    Return the team id for a given ip address (string or integer).
    IP addresses start at 172.31.129.0 (for team 0) and use ip address .0 - .253
    """
    if not isinstance(addr, int):
        addr = ip2int(addr)

    team = addr - IP_BASE
    team -= 2 * (team // 256)

    return team


def transport_type(protocol):
    """
    Returns the protocol keyword for standard internet protocol numbers
    (see https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers)
    """
    if protocol == 0x01:
        return 'ICMP'
    if protocol == 0x11:
        return 'UDP'
    elif protocol == 0x06:
        return 'TCP'
    else:
        return 'Unknown'


def sorted_alpanumeric(elements):
    """
    Sort a list alphanumerically (i.e. keep numerical order in alphanumeric strings)
    """
    def alphanum_key(key):
        return [(int(c) if c.isdigit() else c) for c in re.split('([0-9]+)', key)]

    return sorted(elements, key=alphanum_key)
