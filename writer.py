# -*- coding: utf-8 -*-

import os
from datetime import datetime


class KmlWriter:
    """
    Write a gas prices KML file for organic maps.
    """

    def __init__(self, filepath, name, source, color):
        """
        Creates the writer with its metadata
        """
        self.filepath = filepath
        self._fd = open(filepath, "w")
        self.name = name
        self.color = color

        now = datetime.now().isoformat(' ', timespec='minutes')
        self._fd.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <Style id="placemark-{color}">
    <IconStyle>
      <Icon>
        <href>https://omaps.app/placemarks/placemark-{color}.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <name>{name}</name>
  <visibility>1</visibility>
  <ExtendedData xmlns:mwm="https://omaps.app">
    <mwm:name>
      <mwm:lang code="default">{name}</mwm:lang>
    </mwm:name>
    <mwm:annotation>
    </mwm:annotation>
    <mwm:description>
      <mwm:lang code="en">Generated from {source} data on {now}</mwm:lang>
      <mwm:lang code="fr">
        Généré à partir des données de {source} à {now}
      </mwm:lang>
    </mwm:description>
    <mwm:accessRules>Local</mwm:accessRules>
  </ExtendedData>
""")

    def close(self):
        """
        Close the writer and its resources.
        """
        self._fd.write("""</Document>
</kml>""")
        self._fd.close()

    def writeStation(self, price, update_time, lon, lat, vending):
        """
        Write a gas station data to the file.
        """
        self._fd.write(f"""  <Placemark>
    <name>{price}</name>
    <TimeStamp><when>{update_time}</when></TimeStamp>
    <styleUrl>#placemark-{self.color}</styleUrl>
    <Point><coordinates>{lon},{lat}</coordinates></Point>
    <ExtendedData xmlns:mwm="https://omaps.app">
      <mwm:name><mwm:lang code="default">{price}</mwm:lang></mwm:name>
      <mwm:description>
        <mwm:lang code="default">Automate: {vending}</mwm:lang>
      </mwm:description>
      <mwm:icon>Gas</mwm:icon>
    </ExtendedData>
  </Placemark>
""")
