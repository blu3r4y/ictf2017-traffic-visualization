#!/usr/bin/env python3

"""
Aggregate single *.csv.gz file by merging packets together, given fixed time slices
"""

from __future__ import print_function

import os
import math
import argparse

import numpy as np
import pandas as pd

import preprocessing as pre

ARGS = []
FILTER_PORTS = list(range(20001, 20012 + 1))
MAX_TEAM_ID = 317
GROUPBY = [pre.pcap.INDEX] + ['src_team', 'src_port',
                              'dst_team', 'dst_port']
SUMBY = "len_payload"
COLUMNS = GROUPBY + [SUMBY]
DTYPES = {"timestamp": np.int64, "src_team": np.int32, "src_port": np.int32,
          "dst_team": np.int32, "dst_port": np.int32,
          "len_payload": np.int64}

# estimated number of bytes per line (for fast line estimation based on file size)
# 5756934362 compressed (49211733019 uncompressed) bytes hold 2716530460 lines
COMPRESSED_BYTES_PER_LINE = 2.11


def aggregate_packets():
    """
    Read the input file in chunks, merge timestamps
    and group by (src_team, src_port, dst_team, dst_port)
    """

    if os.path.isfile(ARGS.out):
        print("Output file {} exists already. Aborting.".format(ARGS.out))
        return

    # create output file
    pd.DataFrame(columns=COLUMNS).set_index(pre.pcap.INDEX).to_csv(ARGS.out)

    total_lines = os.path.getsize(ARGS.file.name) // COMPRESSED_BYTES_PER_LINE
    total_chunks = math.ceil(total_lines / ARGS.chunksize)
    reader = pd.read_csv(
        ARGS.file.name, chunksize=ARGS.chunksize, dtype=DTYPES)
    timestamp_offset = None
    num_reduced = 0
    num_lines = 0

    # read the csv chunk by chunk
    eta = pre.timing.ETACalculator(total_chunks)
    for i, chunk in enumerate(reader):
        num_lines += chunk.shape[0]

        if timestamp_offset is None:
            timestamp_offset = chunk[pre.pcap.INDEX][0] % ARGS.resolution

        def merge_group_append(ch):
            # drop non-service ports
            index = (ch['dst_port'].isin(FILTER_PORTS)) & \
                (ch['src_team'] >= 0) & (ch['src_team'] <= 317) & \
                (ch['dst_team'] >= 0) & (ch['dst_team'] <= 317)

            # merge time slices
            ch.loc[index, pre.pcap.INDEX] = merge(ch.loc[index, pre.pcap.INDEX].as_matrix(),
                                                  timestamp_offset)

            grouped = group(ch.loc[index, COLUMNS])
            append_output(grouped, ARGS.out)

            ratio = (grouped.shape[0] / ARGS.chunksize) * 100.0
            print("Chunk {:,} / ~ {:,} aggregated data to {:.2F} % of original size ({:,} / {:,.0F} lines)"
                  .format(i + 1, total_chunks, ratio, grouped.shape[0], ARGS.chunksize))

            num = grouped.shape[0]
            del grouped
            del ch

            return num

        num = eta.execute(i, merge_group_append, {"ch": chunk})
        num_reduced += num

        print()

    final_ratio = (num_reduced / num_lines) * 100.0
    print()
    print("Successfully reduced {:,.0F} lines to {:,.0F} lines ({:.2F} %)"
          .format(num_lines, num_reduced, final_ratio))

    # do a final group-by round once the dataset fits in memory
    print()
    print("Attempting to do a final group by step with the reduced dataset.\n" +
          "This ensures that there are no duplicate groups inside the dataset.\n\n" +
          "This may fail if the dataset is too big to fit in memory.\n" +
          "If so, try increasing the resolution argument or ignore this step.\n")

    try:
        # read
        final = pd.read_csv(ARGS.out)
        pre_length = final.shape[0]

        # group
        grouped = group(final)
        post_length = grouped.shape[0]

        # write
        grouped.set_index(pre.pcap.INDEX).to_csv(ARGS.out)
        print("Final grouping successful. Merged {:,.0F} duplicate lines."
              .format(pre_length - post_length))
    except MemoryError:
        print("Final grouping failed. Duplicates may exist within the dataset.")


def merge(series, timestamp_offset):
    floored = np.floor_divide(series - timestamp_offset, ARGS.resolution)
    return floored + floored * (ARGS.resolution - 1) + timestamp_offset


def group(dataframe):
    """
    Aggregates the supplied dataframe by the GROUPBY columns
    and sums of the SUMBY column. Additional columns are ignored.
    """
    return dataframe.groupby(GROUPBY, as_index=False, sort=False).sum()


def append_output(data, filename):
    """
    Append downscaled results to the *.csv file
    """
    size_pre = os.path.getsize(filename) / 1.0e+6
    data.set_index(pre.pcap.INDEX).to_csv(filename, header=False, mode='a')
    size_post = os.path.getsize(filename) / 1.0e+6
    size_appended = size_post - size_pre

    print("Appended {:.2F} MB of data to {} ({:.2F} MB)"
          .format(size_appended, filename, size_post))


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description='Aggregate single *.csv.gz file by merging packets together, given fixed time slices')
    PARSER.add_argument('file', type=argparse.FileType('rb'),
                        help='The input *.csv.gz file')
    PARSER.add_argument('out', type=str,
                        help='The uncompressed and merged *.csv output file')
    PARSER.add_argument('--resolution', type=float, default=10 * 60,
                        help='Merges packets into time slices of fixed resolution (in seconds)')
    PARSER.add_argument('--chunksize', type=int, default=1e+5,
                        help='Number of lines per chunk')
    ARGS = PARSER.parse_args()

    aggregate_packets()
