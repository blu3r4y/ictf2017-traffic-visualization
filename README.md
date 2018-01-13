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

The dataset is available at the [2016-2017 iCTF archive page](https://ictf.cs.ucsb.edu/pages/the-2016-2017-ictf.html).

This repository already contains the extracted flag captures dataset `captures.tar.xz` in the [dataset directory](dataset/captures).
Complete traffic dumps for preprocessing are not included within this repository, since the archives are 17.4 GB (round 1) + 24.3 GB (round 2) in size. However, the extracted metadata is already available within this repository in the [dataset directory](dataset/traffic).

At the moment, our visualization only considers traffic from round 2.

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

## Contributing

- Use _Kernel > Restart & Run All_ in Jupyter before committing notebooks
- If necessary, add or change python dependencies in the [requirements.txt](requirements.txt)