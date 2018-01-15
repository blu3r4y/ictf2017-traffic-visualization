#!/usr/bin/env python3

"""
Combine multiple *.csv.gz files to a single *.csv.gz file
"""

from __future__ import print_function

import io
import gzip
import argparse
import itertools

import preprocessing as pre

ARGS = []


def merge_files():
    """
    Read and uncompress the input *.csv.gz files
    before writing and compressing a single *.csv.gz output file.
    """
    header = ','.join(pre.pcap.COLUMNS).encode("utf-8")

    with io.BufferedWriter(gzip.open(ARGS.out.name, 'wb')) as writer:
        writer.write(header)

        # read input files
        eta = pre.timing.ETACalculator(len(ARGS.files))
        for i, csv in enumerate(ARGS.files):
            print("Reading {} ... ({} / {})".format(csv.name, i + 1, len(ARGS.files)))

            def blockwise_copy():
                with io.BufferedReader(gzip.open(csv.name, 'rb')) as reader:
                    # seek to the beginning if there is no header
                    if reader.read(len(header)) != header:
                        reader.seek(0)
                    # block-wise copy
                    for block in itertools.count(1):
                        buf = reader.read(64 * 1024)
                        if not buf:
                            break
                        writer.write(buf)

                        # status output
                        if block % 100 == 0:
                            print('.', end='\n' if block % (100 * 80) == 0 else '',
                                  flush=True)

                    print()
                    writer.flush()

            eta.execute(i, blockwise_copy)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description='Combine multiple *.csv.gz files to a single *.csv.gz file')
    PARSER.add_argument('out', type=argparse.FileType('wb'),
                        help='The merged *.csv.gz output file')
    PARSER.add_argument('files', type=argparse.FileType('rb'), nargs='+',
                        help='One or more *.csv.gz files, which will be merged to a single *.csv.gz file.')
    ARGS = PARSER.parse_args()

    # make it faster ...
    print("WARNING! This method might be really slow for large files.\n" +
          "If possible, uncompressing the data manually and re-compressing it\n" +
          "should be about 10x faster.")

    merge_files()
