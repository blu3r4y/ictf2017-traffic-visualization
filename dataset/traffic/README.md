# Traffic Dumps

Complete traffic dumps for preprocessing are not included within this repository, since the archives are 17.4 GB (round 1) + 24.3 GB (round 2) in size.

The dataset is available at the [2016-2017 iCTF archive page](https://ictf.cs.ucsb.edu/pages/the-2016-2017-ictf.html).

## Creating `.tpxz.index` files

These files are just for a better overview and not needed for any of the scripts.

```sh
pixz -l traffic_1.tpxz | sed -e '/\/$/d' | sort -V > traffic_1.tpxz.index
pixz -l traffic_2.tpxz | sed -e '/\/$/d' | sort -V > traffic_2.tpxz.index
```