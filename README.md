# iCTF 2017 Traffic Visualization

This repository holds a Python project, which tries to visualize the network traffic during the [2016-2017 UCSB iCTF contest](https://ictf.cs.ucsb.edu/archive/2016-2017/website/).
This work was developed as a class room project during the Visual Analytics course, held by [Prof. Marc Streit](https://github.com/mstreit) at the [Johannes Kepler University Linz](http://www.jku.at).

This project preprocesses the [public traffic dumps](https://ictf.cs.ucsb.edu/pages/the-2016-2017-ictf.html), extracts metadata and visualizes it with the help of `matplotlib` and friends in IPython notebooks.

The 2016-2017 UCSB International Capture The Flag (iCTF) took place from Friday, March 3rd, 2017 at 9 AM PST until Saturday, March 4th, 2017 at 9 AM PST.
During those 24 hours, 317 academic and public teams attended the contest and produced more than 300 GB of uncompressed traffic.
The 2016-2017 iCTF contest was organized by [Giovanni Vigna](http://www.cs.ucsb.edu/~vigna/), [Adam Doupé](http://adamdoupe.com/), [Shellphish](http://www.shellphish.net/), and [SEFCOM](http://sefcom.asu.edu/). 

## Results

On GitHub, one can observe our IPython notebook [here](src/ictf2017-traffic-visualization.ipynb).

## Dataset

The extracted metadata is available for download [here](https://www.dropbox.com/s/fv2xlmhg0vg8c0g/traffic_2_60sec.csv.gz?dl=1) (~ 175 MB).

The full dataset is available at the [2016-2017 iCTF archive page](https://ictf.cs.ucsb.edu/pages/the-2016-2017-ictf.html).

This repository already contains the extracted flag captures dataset `captures.tar.xz` in the [dataset directory](dataset/captures).
Complete traffic dumps for preprocessing are not included within this repository, since the archives are 17.4 GB (round 1) + 24.3 GB (round 2) in size.

At the moment, our visualization only considers traffic from round 2.
The traffic dumps for round 2 take up approximately 341.1 GB in uncompressed form.

## Installation

### Python requirements

Python 3.6 is required for the python scripts and notebooks.
Additionally, you need a framework to view IPython notebooks.

Package requirements are specified in the [requirements.txt](requirements.txt) file.

We need the latest version of [pypcapfile](https://github.com/kisom/pypcapfile), i.e. we are cloning it directly from source.

```sh
pip3 install -r requirements.txt
```

### Preprocessing traffic dumps

To also be able to extract metadata from the huge traffic dumps, a Linux system is necessary, since we depend on the [pixz compressor](https://github.com/vasi/pixz) to uncompress the `.pixz` archives.

```sh
sudo apt-get install pixz
```

## Details on data preprocessing

The preprocessing step is rather exhausting at the moment and consists of the following steps:

- `preprocess.py` writes a huge `*.csv.gz` file, extracting metadata from the packets. For each packet, the following metadata is extracted:
    - `timestamp` is a UNIX timestamp (in seconds) of the packet arrival time
    - `protocol` of the ip packet (e.g. `{0x06: 'TCP', 0x11: 'UDP', 0x01: 'ICMP', ... }`)
    - `src_team` is the team id of the sender
    - `src_port` is the port of the sender (only for UDP and TCP)
    - `dst_team` is the team id of the recipient
    - `dst_port` is the port of the recipient (only for UDP and TCP)
    - `len_payload` holds the tcp or udp payload length in bytes (excluding headers)
    
    If the protocol is neither UDP nor TCP, `src_port` and `dst_port` will be empty and `len_payload` will hold the payload length of the IP packet (possibly including headers of following protocols).

    The team id is an identifier, which maps ip addresses to simple numbers, starting at the base address `172.31.129.0`. Team `0` therefore has ip `172.31.129.0` and team `253` has ip `172.31.129.253`, but team `254` has ip `172.31.130.0`. Packets with ip addresses in other subnets might yield invalid team ids, i.e. those are game servers or infrastructure servers. The functions `team2ip(team)` and `ip2team(addr)` in [util.py](src/preprocessing/util.py) can be used to convert these addresses.

    Preprocessing round 2 of the dataset takes up to 2 days (without parallelization) and extracts metadata for approximately 1.3 billion packets. The `*.csv` file holds that many lines and takes up approximately 46 GB of disk space (5.6 GB when compressed with `gzip`).

- `merge.py` is able to merge multiple `*.csv.gz` files, created by `preprocess.py` into a single `*.csv.gz` file. This step is only necessary if the previous step was conducted in many (parallel) steps.

    However, the current Python implementation is really slow. I would rather recommend you to use the following set of bash commands: (if you got enough disk space)

    ```sh
    #!/usr/bin/bash

    # uncompress the individual archives
    gzip -d *.csv.gz
    # write the header of any of the files to a new file
    head -1 file0.csv > final.csv
    # append all files (excluding the header)
    for filename in $(ls file*.csv); do tail -n +2 $filename >> final.csv; done
    ```

- `aggregate.py` is able to minimize the previous output file by merging packets together, given fixed time slices. This makes it possible to properly use the data for visualizations and further extraction.

    Aggregating just sums the `len_payload` field for each group of `(src_team, src_port, dst_team, dst_port)` and within a given time slice (e.g. 10 seconds).

    Further analysis is based upon this dataset.

## Contributing

- Use _Kernel > Restart & Run All_ in Jupyter before committing notebooks
- If necessary, add or change python dependencies in the [requirements.txt](requirements.txt)
