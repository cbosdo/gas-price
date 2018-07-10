#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import xml.sax
import six

def convert_opening(timetable):
    # Loop over all days
    ordered_days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    ret = None

    # A common pattern for 24/7 is all days with same open and close values
    if not timetable.get('auto', False) and \
       len([day for day in ordered_days
            if day in timetable and timetable[day][0]['open'] == timetable[day][0]['close']]) != 7:
        all_hours = {day : ','.join(['{0}-{1}'.format(hours['open'], hours['close'])
                                     for hours in timetable[day]])
                     for day in ordered_days if day in timetable}

        def _format_range(start, end, hours):
            ret = ''
            if start and end and hours:
                ret = '{0} {1}'.format('{0}-{1}'.format(start, end) if start != end else start,
                                       hours)
            return ret

        start = None
        end = None
        hours = None
        ranges = []
        for day in ordered_days:
            if day in all_hours:
                if not start:
                    start = day
                    hours = all_hours[day]
                elif hours != all_hours[day]:
                    ranges.append(_format_range(start, end, hours))
                    start = day
                    hours = all_hours[day]
                end = day
            elif start and end:
                ranges.append(_format_range(start, end, hours))
                start = None
                end = None
                hours = None

        ranges.append(_format_range(start, end, hours))
        # The ranges may contain empty strings, filter them out
        ret = '; '.join([opening_range for opening_range in ranges if opening_range])

    return ret or '24/7'

class PrixCarburantHandler(xml.sax.ContentHandler):

    def __init__(self, output):
        xml.sax.ContentHandler.__init__(self)
        self.shop = None
        self.day = None
        self.out = open(output, 'w')
        self.out.writelines(["<?xml version='1.0' encoding='UTF-8'?>\n",
                             "<osm version='0.5'>\n"])

    def endDocument(self):
        self.out.write('</osm>')
        self.out.close()

    def startElement(self, name, attrs):
        if name == 'pdv':
            self.shop = {'id': attrs.get('id'),
                         'lat': float(attrs.get('latitude') or 0) / 100000.0,
                         'lng': float(attrs.get('longitude') or 0) / 100000.0,
                         'price': {},
                         'timetable': {}}
        elif name == 'prix':
            update = attrs.get('maj')[:attrs.get('maj').find('T')]
            self.shop['price'][attrs.get('nom')] = {'value': float(attrs.get('valeur')) / 1000.0,
                                                    'update': update}
        elif name == 'jour':
            days_map = {'Lundi': 'Mo',
                        'Mardi': 'Tu',
                        'Mercredi': 'We',
                        'Jeudi': 'Th',
                        'Vendredi': 'Fr',
                        'Samedi': 'Sa',
                        'Dimanche': 'Su'}
            self.day = {'name': days_map[attrs.get('nom')],
                        'opened': attrs.get('ferme') != '1'}
        elif name == 'horaire' and self.day:
            timetable = self.shop['timetable'].get(self.day['name'], [])
            timetable.append({'open': attrs.get('ouverture').replace('.', ':'),
                              'close': attrs.get('fermeture').replace('.', ':')})
            self.shop['timetable'][self.day['name']] = timetable
        elif name == 'horaires' and attrs.get('automate-24-24') == '1':
            self.shop['timetable'] = {'auto': True}

    def endElement(self, name):
        if name == 'pdv':
            self._writeShop()
        elif name == 'jour':
            if not self.shop['timetable'].get(self.day['name']) and self.day['opened']:
                self.shop['timetable'][self.day['name']] = [{'open': '00:00', 'close': '00:00'}]
            self.day = None

    def _writeShop(self):
        if self.shop['lat'] and self.shop['lng'] and self.shop['price']:
            fuel_map = {'Gazole': 'diesel',
                        'SP95': 'octane_95',
                        'SP98': 'octane_98',
                        'GPLc': 'lgp',
                        'E85':  'e85',
                        'E10':  'e10'}

            name = ' | '.join(['{0} {1}€'.format(k, v['value'])
                               for k, v in six.iteritems(self.shop['price'])])
            description = '&#10;'.join(['{0}: {1}€ ({2})'.format(k, v['value'], v['update'])
                                      for k, v in six.iteritems(self.shop['price'])])
            fuel_tags = '\n'.join(["<tag k='fuel:{0}' v='yes'/>".format(fuel_map[fuel])
                                   for fuel in self.shop['price']])

            opening_hours = ''
            if self.shop['timetable']:
                opening_hours = "<tag k='opening_hours' v='{0}'/>".format(
                    convert_opening(self.shop['timetable']))
            self.out.write('''
                <node id='{0}' visible='true' lat='{1}' lon='{2}'>
                  <tag k='name' v='{3}'/>
                  <tag k='description' v='{4}'/>
                  {5}
                  <tag k='amenity' v='fuel'/>
                  {6}
                  <tag k='source' v='prix-carburant.economie.gouv.fr'/>
                </node>'''.format(self.shop['id'],
                                  self.shop['lat'],
                                  self.shop['lng'],
                                  name,
                                  description,
                                  opening_hours,
                                  fuel_tags))
        self.shop = None


def main(args):
    handler = PrixCarburantHandler(args[2])
    xml.sax.parse(args[1], handler)

if __name__ == '__main__':
    main(sys.argv)
