"""
Methods for extracting metadata from *.pcap files
"""

from __future__ import print_function

import pandas as pd

from pcapfile import savefile
from pcapfile.protocols.transport.tcp import TCP
from pcapfile.protocols.transport.udp import UDP

from preprocessing.util import ip2team


INDEX = 'timestamp'
COLUMNS = [INDEX, 'protocol',
           'src_team', 'src_port',
           'dst_team', 'dst_port',
           'len_payload']


def read(filename, verbose=False):
    """
    Read metadata from a *.pcap file and return a pandas dataframe
    """

    metadata = []
    num_tcp, num_udp, num_other = 0, 0, 0

    with open(filename, 'rb') as handle:
        cap = savefile.load_savefile(handle, layers=3, verbose=verbose)

        for frame in cap.packets:
            # link layer (ethernet)
            timestamp = frame.timestamp

            # network layer (ip)
            packet = frame.packet.payload
            src_team = ip2team(packet.src)
            dst_team = ip2team(packet.dst)
            protocol = packet.p

            # transport layer (udp, tcp)
            if isinstance(packet.payload, UDP):
                num_udp += 1

                segment = packet.payload
                len_payload = len(segment.payload)
                src_port = segment.src_port
                dst_port = segment.dst_port

            elif isinstance(packet.payload, TCP):
                num_tcp += 1

                datagram = packet.payload
                len_payload = len(datagram.payload)
                src_port = datagram.src_port
                dst_port = datagram.dst_port

            else:
                num_other += 1

                # use complete ip packet payload for other protocols
                len_payload = len(packet.payload)
                src_port, dst_port = None, None

            metadata.append((timestamp, protocol,
                             src_team, src_port, dst_team, dst_port, len_payload))

    # convert to pandas data frame
    metadata = pd.DataFrame(metadata, columns=COLUMNS).set_index(INDEX)
    print("Read metadata of {:,} packets ({:,} TCP, {:,} UDP, {:,} Other)"
          .format(metadata.shape[0], num_tcp, num_udp, num_other))

    return metadata
