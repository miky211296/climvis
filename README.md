# A climate visualization package

**climvis** offers command line tools to display climate data in your browser.
**windvis** offers also command line tools but to display recent wind data
in your browser. The wind data is taken from stations in and around Innsbruck.

It was written for the University of Innsbruck's
[scientific programming](http://fabienmaussion.info/scientific_programming)
lecture as a package template for the assignments.

## HowTo

Make sure you have all dependencies installed. These are:
- numpy
- pandas
- xarray
- motionless
- matplotlib
- windrose
- holoviews
- bokeh
- tornado

**If you installed the scipy packages separately then you might need to install** ``scipy`` **since this package makes use of the** ``scipy.stats`` **module.**

Download the package and install it in development mode. From the root
directory, do:

    $ pip install -e .

If you are on a university computer, you should use:

    $ pip install --user -e .

## Further requirements
In order to display something you actually need the climate data.
You can download them here:
- [temperature](https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.03/cruts.1905011326.v4.03/tmp/cru_ts4.03.1901.2018.tmp.dat.nc.gz)
- [precipitation](https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.03/cruts.1905011326.v4.03/pre/cru_ts4.03.1901.2018.pre.dat.nc.gz)
- [elevation](https://cluster.klima.uni-bremen.de/~fmaussion/misc/cru_cl1_topography.nc)

**The decompressed output is about 6GB**

Save and decompress the data in a folder of your choice. Remember to specify
its path in a file named ``.cruvis`` located in your ``HOME``.
If you fail to do so then ``climvis`` won't work and you will be asked to
fulfill this requirement.

## Command line interface

``setup.py`` defines an "entry point" for a script to be used as a
command line program. There are two commands installed ``cruvis`` and 
``windvis``.

After installation, just type:

    $ cruvis --help

or

    $ windvis --help

To see what they can do for you.

## Testing

We recommend to use [pytest](https://docs.pytest.org) for testing. To test
the package, do:

    $ pytest .

From the package root directory.

## License

With the exception of the ``setup.py`` file which was adapted from the
[sampleproject](https://github.com/pypa/sampleproject) package, all the
code in this repository is dedicated to the public domain.
