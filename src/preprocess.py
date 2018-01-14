#!/usr/bin/env python3

"""
Decompress *.tpxz and extract metadata from the *.pcap files
"""

from __future__ import print_function

import os
import shutil
import argparse
import tempfile
import pandas as pd

import preprocessing as pre

ARGS = []


def extract_metadata():
    """
    Extract metadata from compressed *.tpxz archives and append the metadata
    to compressed *.csv.gz files
    """

    create_output(ARGS.out)
    index = pre.pixz.read_index(ARGS.traffic)

    try:
        tmp = tempfile.mkdtemp(prefix="ictf2017_cache_")
        print("Using temporary cache for extracted files at {}".format(tmp))

        file_indexes = [i for i in range(len(index))
                        if (i >= ARGS.start and i <= ARGS.stop)]

        # a wrapper which measures execution times and calculates eta
        eta = pre.timing.ETACalculator(len(file_indexes))

        for count, i in enumerate(file_indexes):
            print("\nProcessing index {} from [{}, {}]"
                  .format(i, min(file_indexes), max(file_indexes)))

            def extract_read_append_remove():
                pcapfile = pre.pixz.extract_pcap(ARGS.traffic, index[i], tmp)
                metadata = pre.pcap.read(pcapfile)
                append_output(metadata, ARGS.out)
                os.remove(pcapfile)

            eta.execute(count, extract_read_append_remove)

    finally:
        shutil.rmtree(tmp)
        print("Cleaned up temporary cache {}\n\n".format(tmp))


def create_output(filename):
    """
    Create the output file if necessary
    """
    if not os.path.isfile(filename):
        pd.DataFrame(columns=pre.pcap.COLUMNS).set_index(pre.pcap.INDEX) \
            .to_csv(ARGS.out, compression='gzip')
        print("Created empty output file {}".format(ARGS.out))
    else:
        size = os.path.getsize(filename) / 1.0e+6
        print("Found existing output file which will be appended {} ({:.2F} MB)"
              .format(ARGS.out, size))


def append_output(metadata, filename):
    """
    Append metadata to the compressed *.csv.gz file
    """
    size_pre = os.path.getsize(filename) / 1.0e+6
    metadata.to_csv(filename, header=False,
                    mode='a', compression='gzip')
    size_post = os.path.getsize(filename) / 1.0e+6
    size_appended = size_post - size_pre

    print("Appended {:.2F} MB of metadata to {} ({:.2F} MB)"
          .format(size_appended, filename, size_post))


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description='Decompress *.tpxz and extract metadata from the *.pcap files.')
    PARSER.add_argument('traffic', type=str,
                        help='The compressed *.tpxz archive containing raw traffic data')
    PARSER.add_argument('out', type=str,
                        help='The *.csv.gz which will be appended')
    PARSER.add_argument('--start', type=int, default=0,
                        help='Extract only traffic data starting with this index number, inclusive')
    PARSER.add_argument('--stop', type=int, default=1e+9,
                        help='Extract only traffic data up to this index number, inclusive')
    PARSER.add_argument('--tick', type=float, default=4.8,
                        help='The duration of a tick in minutes')
    ARGS = PARSER.parse_args()

    extract_metadata()
