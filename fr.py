#!/usr/bin/python3

# SPDX-FileCopyrightText: 2024 Cédric Bosdonnat <cedric.bosdonnat@gmail.com>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import click
import sys
import requests
import os.path
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import writer


def parse_xml(xml_file, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    writers = {
        "Gazole": writer.KmlWriter(
            os.path.join(out_dir, "diesel.kml"),
            "France - Diesel",
            "https://www.prix-carburants.gouv.fr",
            "yellow"
        ),
        "E85": writer.KmlWriter(
            os.path.join(out_dir, "e85.kml"),
            "France - E85",
            "https://www.prix-carburants.gouv.fr",
            "cyan"
        ),
        "E10": writer.KmlWriter(
            os.path.join(out_dir, "e10.kml"),
            "France - E10",
            "https://www.prix-carburants.gouv.fr",
            "lime"
        ),
        "SP98": writer.KmlWriter(
            os.path.join(out_dir, "sp98.kml"),
            "France - SP98",
            "https://www.prix-carburants.gouv.fr",
            "green"
        ),
        "SP95": writer.KmlWriter(
            os.path.join(out_dir, "sp95.kml"),
            "France - SP95",
            "https://www.prix-carburants.gouv.fr",
            "green"
        ),
        "GPLc": writer.KmlWriter(
            os.path.join(out_dir, "gplc.kml"),
            "France - GPLc",
            "https://www.prix-carburants.gouv.fr",
            "blue"
        ),
    }

    # Loop over all stations
    for event, element in ET.iterparse(xml_file):
        if element.tag == "pdv":
            prices = element.findall("prix")
            for gas in prices:
                name = gas.get("nom")
                w = writers.get(name)
                if w is None:
                    print(f"Unhandled gas type: {name}", file=sys.stderr)

                lat = float(element.get("latitude", 0)) / 100000.0
                lon = float(element.get("longitude", 0)) / 100000.0
                update_time = gas.get("maj").replace(" ", "T") + "Z"
                timetable = element.find("horaires")
                vending = False
                price = gas.get('valeur')
                if timetable is not None and timetable.get("automate-24-24") == "1":
                    vending = True
                w.writeStation(price, update_time, lon, lat, vending)

    for w in writers.values():
        w.close()


@click.command()
@click.option("-i", "file_in", help="Gas price XML file to use instead of downloading the instant snapshot")
@click.option("-o", "out", help="Directory to write the KML files to", default=".")
def main(file_in, out):
    if file_in is None:
        req = requests.get("http://donnees.roulez-eco.fr/opendata/instantane", stream=True)
        if req.status_code != 200:
            print("failed to download data: " + req.status_code, file=sys.stderr)
            sys.exit(1)

        tmp_dir = tempfile.mkdtemp()
        tmp_zip = os.path.join(tmp_dir, "data.zip")

        with open(tmp_zip, 'wb') as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        # Uncompress the zip file
        with zipfile.ZipFile(tmp_zip) as zip_file:
            with zip_file.open("PrixCarburants_instantane.xml") as xml_file:
                parse_xml(xml_file, out)
    else:
        with open(file_in, "r", encoding="iso-8859-1") as xml_file:
            parse_xml(xml_file, out)


if __name__ == '__main__':
    main()
