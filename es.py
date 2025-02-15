#!/usr/bin/python3

# SPDX-FileCopyrightText: 2025 Cédric Bosdonnat <cedric.bosdonnat@gmail.com>
#
# SPDX-License-Identifier: MIT

import click
from datetime import datetime
import sys
import requests
import os.path
import tempfile
import xml.etree.ElementTree as ET
import writer


def parse_xml(xml_file, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    writers = {
        "Precio_x0020_Gasoleo_x0020_A": writer.KmlWriter(
            os.path.join(out_dir, "diesel.kml"),
            "Diesel",
            "https://sedeaplicaciones.minetur.gob.es",
            "yellow"
        ),
        "Precio_x0020_Gasoleo_x0020_Premium": writer.KmlWriter(
            os.path.join(out_dir, "diesel-premium.kml"),
            "Diesel Premium",
            "https://sedeaplicaciones.minetur.gob.es",
            "yellow"
        ),
        "Precio_x0020_Biodiesel": writer.KmlWriter(
            os.path.join(out_dir, "biodiesel.kml"),
            "Biodiesel",
            "https://sedeaplicaciones.minetur.gob.es",
            "yellow"
        ),
        "Precio_x0020_Bioetanol": writer.KmlWriter(
            os.path.join(out_dir, "e85.kml"),
            "E85",
            "https://sedeaplicaciones.minetur.gob.es",
            "cyan"
        ),
        "Precio_x0020_Gasolina_x0020_98_x0020_E10": writer.KmlWriter(
            os.path.join(out_dir, "e10.kml"),
            "SP98E10",
            "https://sedeaplicaciones.minetur.gob.es",
            "lime"
        ),
        "Precio_x0020_Gasolina_x0020_98_x0020_E5": writer.KmlWriter(
            os.path.join(out_dir, "sp98.kml"),
            "SP98",
            "https://sedeaplicaciones.minetur.gob.es",
            "green"
        ),
        "Precio_x0020_Gasolina_x0020_95_x0020_E10": writer.KmlWriter(
            os.path.join(out_dir, "sp95e10.kml"),
            "SP95E10",
            "https://sedeaplicaciones.minetur.gob.es",
            "green"
        ),
        "Precio_x0020_Gasolina_x0020_95_x0020_E5": writer.KmlWriter(
            os.path.join(out_dir, "sp95.kml"),
            "SP95",
            "https://sedeaplicaciones.minetur.gob.es",
            "green"
        ),
        "Precio_x0020_Gasolina_x0020_95_x0020_E5_x0020_Premium": writer.KmlWriter(
            os.path.join(out_dir, "sp95-premium.kml"),
            "SP95 Premium",
            "https://sedeaplicaciones.minetur.gob.es",
            "green"
        ),
        "Precio_x0020_Gases_x0020_licuados_x0020_del_x0020_petróleo": writer.KmlWriter(
            os.path.join(out_dir, "gplc.kml"),
            "GPLc",
            "https://sedeaplicaciones.minetur.gob.es",
            "blue"
        ),
        "Precio_x0020_Gas_x0020_Natural_x0020_Licuado": writer.KmlWriter(
            os.path.join(out_dir, "lng.kml"),
            "LNG",
            "https://sedeaplicaciones.minetur.gob.es",
            "blue"
        ),
        "Precio_x0020_Gas_x0020_Natural_x0020_Comprimido": writer.KmlWriter(
            os.path.join(out_dir, "cng.kml"),
            "CNG",
            "https://sedeaplicaciones.minetur.gob.es",
            "blue"
        ),
        "Precio_x0020_Hidrogeno": writer.KmlWriter(
            os.path.join(out_dir, "h.kml"),
            "Hydrogen",
            "https://sedeaplicaciones.minetur.gob.es",
            "blue"
        ),
    }

    # Loop over all stations
    ns="{http://schemas.datacontract.org/2004/07/ServiciosCarburantes}"

    update_time = ""
    for _, element in ET.iterparse(xml_file):
        if element.tag == ns+"Fecha":
            dt = datetime.strptime(element.text, "%d/%m/%Y %H:%M:%S")
            update_time = dt.isoformat()+"Z"
        if element.tag == ns+"EESSPrecio":
            lat = float(element.find(ns+"Latitud").text.replace(",", "."))
            lon = float(element.find(ns+"Longitud_x0020__x0028_WGS84_x0029_").text.replace(",", "."))
            timetable = element.find(ns+"Horario").text
            vending = timetable == "L-D: 24H"

            if element.find(ns+"Tipo_x0020_Venta").text != "P":
                # Ignore shops not for individuals
                continue

            for tag_name, w in writers.items():
                price = element.find(ns+tag_name)
                if price.text != None:
                    w.writeStation(price.text, update_time, lon, lat, vending)

    for w in writers.values():
        w.close()


@click.command()
@click.option("-i", "file_in", help="Gas price XML file to use instead of downloading")
@click.option("-o", "out", help="Directory to write the KML files to", default=".")
def main(file_in, out):
    if file_in is None:
        with requests.get(
                    "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/",
                    headers={"Accept": "text/xml"},
                    stream=True,
                ) as req:
            if req.status_code != 200:
                print(f"failed to download data: {req.status_code}", file=sys.stderr)
                sys.exit(1)

            fd, tmp_xml = tempfile.mkstemp()
            try:
                with os.fdopen(fd, "wb") as tmp_file:
                    for chunk in req.iter_content(chunk_size=1024):
                        if chunk:
                            tmp_file.write(chunk)

                with open(tmp_xml, "r") as xml_file:
                    parse_xml(xml_file, out)
            finally:
                os.unlink(tmp_xml)
    else:
        with open(file_in, "r") as xml_file:
            parse_xml(xml_file, out)


if __name__ == '__main__':
    main()
