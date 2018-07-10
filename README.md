Create OBF files for use with [OsmAnd][0] from [prix-carburant-economie.gouv.fr][1] data.
These data are licensed under opened, see the [FAQ here][2].

Install
-------

Download the monthly [generated OBF](http://bosdonnat.fr/osmand-fuel/Prix-carburant.obf) file
in your osmand data **Android/data/net.osmand.plus/files**, restart OsmAnd and search the fuel
you need!

How to use me
-------------

Dependencies:

* python
* python six module

Run the `run.sh` script (no argument needed)

    ./run.sh

Once the conversion is done, a file for each know fuel type will be available in the obf
folder. To use them in OsmAnd, copy the files you need in the OsmAnd data folder on your
mobile device:

  * `/sdcard/osmand` on older versions
  * `/sdcard/Android/data/net.osmand.plus/files` in more recent ones

Force OsmAnd to restart, and the new POIs will be available for searches or as a layer
on the map.

 [0]: http://osmand.net
 [1]: http://www.prix-carburants.economie.gouv.fr/
 [2]: https://www.data.gouv.fr/fr/faq/
