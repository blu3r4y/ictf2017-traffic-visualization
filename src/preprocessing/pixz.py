"""
Methods for decompressing *.tpxz archives
"""

from __future__ import print_function

import os
import tarfile
import subprocess

from preprocessing.util import sorted_alpanumeric


def read_index(archive):
    """
    Return a list of archive contents within a *.tpxz archive
    """
    print("Reading archive index of {} ...".format(archive))

    index = subprocess.check_output(
        ["pixz", "-l", archive]).decode("utf-8").splitlines()
    # remove the root directory (first entry)
    del index[0]

    print("Indexed {} files within the archive".format(len(index)))

    return sorted_alpanumeric(index)


def extract_pcap(archive, filename, out_directory):
    """
    Extract a single *.pcap file from an *.tpxz archive to a directory.
    Returns the path to the extracted *.pcap file in the output directory.
    """
    # unpack and untar (with a temporary *.tar file)
    tar_path = os.path.join(out_directory, "pixz.tar")
    subprocess.call(["pixz", "-x", filename, "-i", archive, "-o", tar_path])
    with tarfile.open(tar_path) as tar:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner) 
            
        
        safe_extract(tar, path=out_directory)
    os.remove(tar_path)

    # rename to *.pcap
    pcap_path = os.path.join(out_directory, filename)
    os.rename(pcap_path, pcap_path + ".pcap")
    pcap_path += ".pcap"

    print("Extracted {}".format(pcap_path))
    return pcap_path
