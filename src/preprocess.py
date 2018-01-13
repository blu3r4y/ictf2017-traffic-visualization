#!/usr/bin/env python3
import os
import re
import socket
import struct
import shutil
import argparse
import tempfile
import subprocess
import code
import pandas as pd

from pcapfile import savefile
from pcapfile.protocols.transport.tcp import TCP
from pcapfile.protocols.transport.udp import UDP

ARGS = []


#######################################################################
# MAIN LOGIC
#######################################################################


def main():
    index = read_index(ARGS.traffic)

    dataframe = pd.DataFrame(
        columns=['tick', 'src', 'dst', 'packets', 'bytes'])

    try:

        # cache contents
        tmpdir = tempfile.mkdtemp(prefix="pixz_cache_")
        print("Using temporary cache for extracted files in %s" % tmpdir)

        firstTimestamp = None

        for i in range(4):  # len(index):
            pcapfile = extract_pcap(ARGS.traffic, index[0], tmpdir)
            read_pcap(pcapfile, firstTimestamp)
            print("\n" + "#" * 80 + "\n")

        # clean up extracted pcap file
        os.remove(pcapfile)

    finally:
        # clean up everything
        shutil.rmtree(tmpdir)
        print("Cleaned up temporary cache %s" % tmpdir)


def read_index(archive):
    # List archive contents and remove the root directory (first entry)
    print("Reading archive contents of %s ..." % archive)
    index = subprocess.check_output(
        ["pixz", "-l", archive]).decode("utf-8").splitlines()
    del index[0]
    print("Observed %d traffic captures within the archive" % len(index))

    return sorted_alpanumeric(index)


def extract_pcap(archive, content, tmpdir):
    # unpack and untar (with a temporary file for pixz)
    pixz_tmp_out = os.path.join(tmpdir, "pixz.tar")
    subprocess.call(["pixz", "-x", content, "-i", archive, "-o", pixz_tmp_out])
    subprocess.call(["tar", "xf", pixz_tmp_out, "-C", tmpdir])
    os.remove(pixz_tmp_out)

    # rename to pcap
    content_extracted = os.path.join(tmpdir, content)
    os.rename(content_extracted, content_extracted + ".pcap")
    content_extracted += ".pcap"

    print("Extracted %s" % content_extracted)
    return content_extracted


def read_pcap(pcap, firstTimestamp=None):
    dataframe = pd.DataFrame(
        columns=['tick', 'src', 'dst', 'packets', 'bytes'])

    try:
        handle = open(pcap, 'rb')
        cap = savefile.load_savefile(handle, layers=2, verbose=False)
        for pack in cap.packets:

            # remember first timestamp if not explicitly given
            if firstTimestamp is None:
                firstTimestamp = pack.timestamp
            assert pack.timestamp >= firstTimestamp

            # calculate tick
            tick = ((pack.timestamp - firstTimestamp) / 60.0) // ARGS.tick
            src = ip2team(pack.packet.payload.src)
            dst = ip2team(pack.packet.payload.dst)
            src_port = TCP(pack.packet.payload.payload).src_port
            dst_port = TCP(pack.packet.payload.payload).dst_port
            eth_pack_len = pack.packet_len
            ip_pack_len = pack.packet.payload.len

            print("%03d: %d -> %d with %d bytes" %
                  (tick, src, dst, ip_pack_len))

            # TODO

    finally:
        handle.close()

    return firstTimestamp


#######################################################################
# UTILITIES
#######################################################################


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


def team2ip(team):
    team_subnet = team // 254
    return '172.31.%d.%d' % (129 + team_subnet, (team + team_subnet) % 255)


IP_BASE = ip2int('172.31.129.0')


def ip2team(addr):
    if not isinstance(addr, int):
        addr = ip2int(addr)

    id = addr - IP_BASE
    id -= 2 * (id // 256)

    return id


def sorted_alpanumeric(elements):
    def alphanum_key(key):
        return [(int(c) if c.isdigit() else c) for c in re.split('([0-9]+)', key)]

    return sorted(elements, key=alphanum_key)


#######################################################################
# ENTRY POINT
#######################################################################


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Decompress *.tpxz and extract metadata from the *.pcap files.')
    parser.add_argument('traffic', type=str,
                        help='The compressed *.tpxz archive containing raw traffic data')
    parser.add_argument('--from', type=int, default=None,
                        help='Extract only traffic data starting with this sequence number, inclusive')
    parser.add_argument('--to', type=int, default=None,
                        help='Extract only traffic data up to this sequence number, inclusive')
    parser.add_argument('--tick', type=float, default=4.8,
                        help='The duration of a tick in minutes')
    ARGS = parser.parse_args()

    main()
