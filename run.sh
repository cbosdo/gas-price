#!/bin/sh
# Copyright (c) 2015 Cédric Bosdonnat <cedric@bosdonnat.fr>
# 
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

grab_data ()
{
    wget -O $WORKDIR/data.zip http://donnees.roulez-eco.fr/opendata/instantane
    unzip $WORKDIR/data.zip -d $WORKDIR
}

create_obf ()
{
    create_obf_in=$1
    create_obf_out=$2
    mapcreator=$PWD/OsmAndMapCreator-main
    batch=$mapcreator/osm2obf.xml

    # Download OsmandMapCreator if needed
    if ! test -e "$mapcreator"; then
        mkdir -p "$mapcreator"
        wget http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip
        unzip OsmAndMapCreator-main.zip -d $mapcreator
    fi


    cat >$batch <<EOF
<?xml version="1.0" encoding="utf-8"?>
<batch_process>
    <process_attributes
        mapZooms=""
        renderingTypesFile=""
        zoomWaySmoothness=""
        osmDbDialect="sqlite"
        mapDbDialect="sqlite"/>
    <process
        directory_for_osm_files="$create_obf_in"
        directory_for_index_files="$create_obf_out"
        directory_for_generation="$create_obf_out"
        skipExistingIndexesAt=""
        indexPOI="true"
        indexRouting="false"
        indexMap="false"
        indexTransport="false"
        indexAddress="false">
    </process>
</batch_process>
EOF

  cd "$mapcreator"
  java -Djava.util.logging.config.file=logging.properties -Xms256M -Xmx2560M \
       -cp "./OsmAndMapCreator.jar:./lib/OsmAnd-core.jar:./lib/*.jar" \
       net.osmand.util.IndexBatchCreator osm2obf.xml
  cd $OLDPWD
}

WORKDIR=$PWD/tmp
if ! test -e $WORKDIR; then
    mkdir $WORKDIR
fi

osmdir=$PWD/osm
obfdir=$PWD/obf

mkdir -p $osmdir
mkdir -p $obfdir

grab_data

data=$(ls -1 $WORKDIR/*.xml)

python3 create_osm.py "$data" "$osmdir/prix-carburant.osm"

create_obf "$osmdir" "$obfdir"
rm $obfdir/*.gen.log

for f in $(ls -1 $obfdir/*.obf); do
    newname=$(echo "$f" | sed "s/_2//")
    mv $f $newname
done

rm -rf $WORKDIR
rm -rf "$osmdir"
