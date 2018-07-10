import pytest
import create_osm
import xml.sax
import xml.etree.ElementTree as ET

def test_convert_opening_247():
    assert create_osm.convert_opening({
        'Mo': [{'open': '01:00', 'close': '01:00'}],
        'Tu': [{'open': '01:00', 'close': '01:00'}],
        'We': [{'open': '01:00', 'close': '01:00'}],
        'Th': [{'open': '01:00', 'close': '01:00'}],
        'Fr': [{'open': '01:00', 'close': '01:00'}],
        'Sa': [{'open': '01:00', 'close': '01:00'}],
        'Su': [{'open': '01:00', 'close': '01:00'}]}) == '24/7'

def test_convert_opening():
    expected = 'Mo-We 09:00-12:00,14:00-19:00; Th-Sa 09:00-19:00; Su 09:00-12:00'
    assert create_osm.convert_opening({
        'Mo': [{'open': '09:00', 'close': '12:00'}, {'open': '14:00', 'close': '19:00'}],
        'Tu': [{'open': '09:00', 'close': '12:00'}, {'open': '14:00', 'close': '19:00'}],
        'We': [{'open': '09:00', 'close': '12:00'}, {'open': '14:00', 'close': '19:00'}],
        'Th': [{'open': '09:00', 'close': '19:00'}],
        'Fr': [{'open': '09:00', 'close': '19:00'}],
        'Sa': [{'open': '09:00', 'close': '19:00'}],
        'Su': [{'open': '09:00', 'close': '12:00'}]}) == expected

def test_convert_close():
    expected = 'Mo-We 09:00-12:00,14:00-19:00; Th-Sa 09:00-19:00'
    assert create_osm.convert_opening({
        'Mo': [{'open': '09:00', 'close': '12:00'}, {'open': '14:00', 'close': '19:00'}],
        'Tu': [{'open': '09:00', 'close': '12:00'}, {'open': '14:00', 'close': '19:00'}],
        'We': [{'open': '09:00', 'close': '12:00'}, {'open': '14:00', 'close': '19:00'}],
        'Th': [{'open': '09:00', 'close': '19:00'}],
        'Fr': [{'open': '09:00', 'close': '19:00'}],
        'Sa': [{'open': '09:00', 'close': '19:00'}]}) == expected

def test_convert():
    data = '''
       <pdv id="2110002" latitude="4998600" longitude="346100" cp="02110" pop="R">
         <adresse>22 rue de Vaux</adresse>
         <ville>BOHAIN-EN-VERMANDOIS</ville>
         <horaires automate-24-24="">
           <jour id="1" nom="Lundi" ferme="">
             <horaire ouverture="09.00" fermeture="12.00"/>
             <horaire ouverture="14.00" fermeture="19.00"/>
           </jour>
           <jour id="2" nom="Mardi" ferme="">
             <horaire ouverture="09.00" fermeture="12.00"/>
             <horaire ouverture="14.00" fermeture="19.00"/>
           </jour>
           <jour id="3" nom="Mercredi" ferme="">
             <horaire ouverture="09.00" fermeture="12.00"/>
             <horaire ouverture="14.00" fermeture="19.00"/>
           </jour>
           <jour id="4" nom="Jeudi" ferme="">
             <horaire ouverture="09.00" fermeture="12.00"/>
             <horaire ouverture="14.00" fermeture="19.00"/>
           </jour>
           <jour id="5" nom="Vendredi" ferme="">
             <horaire ouverture="09.00" fermeture="19.00"/>
           </jour>
           <jour id="6" nom="Samedi" ferme="">
             <horaire ouverture="09.00" fermeture="19.00"/>
           </jour>
           <jour id="7" nom="Dimanche" ferme="">
             <horaire ouverture="09.00" fermeture="12.00"/>
           </jour>
         </horaires>
         <services>
           <service>Vente de pétrole lampant</service>
         </services>
         <prix nom="Gazole" id="1" maj="2018-07-06T08:23:34" valeur="1399"/>
         <prix nom="SP95" id="2" maj="2018-07-06T08:23:35" valeur="1494"/>
         <prix nom="E10" id="5" maj="2018-07-06T08:23:35" valeur="1447"/>
         <rupture id="3" nom="E85" debut="2010-03-02T11:12:00" fin=""/>
         <rupture id="6" nom="SP98" debut="2014-03-11T00:00:00" fin=""/>
         <rupture id="4" nom="GPLc" debut="2017-09-26T09:19:50" fin=""/>
       </pdv>
    '''

    expected = '''<?xml version='1.0' encoding='UTF-8'?>
    <osm version='0.5'>
      <node id='2110002' visible='true' lat='49.986' lon='3.461'>
        <tag k='name' v='Gazole 1.399€ | SP95 1.494€ | E10 1.447€'/>
        <tag k='description' v='Gazole: 1.399€ (2018-07-06)&#10;SP95: 1.494€ (2018-07-06)&#10;E10: 1.447€ (2018-07-06)'/>
        <tag k='opening_hours' v='Mo-Th 09:00-12:00,14:00-19:00; Fr-Sa 09:00-19:00; Su 09:00-12:00'/>
        <tag k='amenity' v='fuel'/>
        <tag k='fuel:diesel' v='yes'/>
        <tag k='fuel:octane_95' v='yes'/>
        <tag k='fuel:e10' v='yes'/>
        <tag k='source' v='prix-carburant.economie.gouv.fr'/>
      </node>
    </osm>'''

    handler = create_osm.PrixCarburantHandler('test_out.xml')
    xml.sax.parseString(data, handler)
    with open('test_out.xml', 'r') as test_file:
        assert_xml_equal(test_file.read(), expected)

def test_convert_noopening():
    data = '''
      <pdv id="2100018" latitude="4984226" longitude="328387" cp="02100" pop="R">
        <adresse>25 Boulevard Victor Hugo</adresse>
        <ville>SAINT-QUENTIN</ville>
        <services>
          <service>Carburant additivé</service>
          <service>Vente de gaz domestique (Butane, Propane)</service>
          <service>Automate CB</service>
          <service>Vente de fioul domestique</service>
          <service>Vente de pétrole lampant</service>
        </services>
        <prix nom="Gazole" id="1" maj="2018-05-25T09:31:11" valeur="1453"/>
        <prix nom="SP95" id="2" maj="2018-05-25T09:31:55" valeur="1545"/>
        <prix nom="SP98" id="6" maj="2018-05-25T09:32:48" valeur="1585"/>
      </pdv>
    '''

    expected = '''<?xml version='1.0' encoding='UTF-8'?>
    <osm version='0.5'>
      <node id='2100018' visible='true' lat='49.84226' lon='3.28387'>
        <tag k='name' v='Gazole 1.453€ | SP95 1.545€ | SP98 1.585€'/>
        <tag k='description' v='Gazole: 1.453€ (2018-05-25)&#10;SP95: 1.545€ (2018-05-25)&#10;SP98: 1.585€ (2018-05-25)'/>
        <tag k='amenity' v='fuel'/>
        <tag k='fuel:diesel' v='yes'/>
        <tag k='fuel:octane_95' v='yes'/>
        <tag k='fuel:octane_98' v='yes'/>
        <tag k='source' v='prix-carburant.economie.gouv.fr'/>
      </node>
    </osm>'''

    handler = create_osm.PrixCarburantHandler('test_out.xml')
    xml.sax.parseString(data, handler)
    with open('test_out.xml', 'r') as test_file:
        assert_xml_equal(test_file.read(), expected)

def test_convert_closed():
    data = '''
      <pdv id="2100014" latitude="" longitude="" cp="02100" pop="R">
        <adresse>60 BIS RUE DE LA FERE</adresse>
        <ville>SAINT QUENTIN</ville>
        <services>
          <service>Toilettes publiques</service>
          <service>Boutique alimentaire</service>
          <service>Station de gonflage</service>
          <service>Boutique non alimentaire</service>
          <service>Piste poids lourds</service>
          <service>Lavage automatique</service>
        </services>
        <fermeture type="T" debut="2009-02-01T00:00:00" fin=""/>
      </pdv>
    '''

    expected = '''<?xml version='1.0' encoding='UTF-8'?>
    <osm version='0.5'>
    </osm>'''

    handler = create_osm.PrixCarburantHandler('test_out.xml')
    xml.sax.parseString(data, handler)
    with open('test_out.xml', 'r') as test_file:
        assert_xml_equal(test_file.read(), expected)

def test_convert_auto247():
    data = '''
      <pdv id="3000001" latitude="4654100" longitude="334400" cp="03000" pop="R">
        <adresse>169 ROUTE DE LYON</adresse>
        <ville>MOULINS</ville>
        <horaires automate-24-24="1">
          <jour id="1" nom="Lundi" ferme="">
            <horaire ouverture="09.00" fermeture="19.00"/>
          </jour>
          <jour id="2" nom="Mardi" ferme="">
            <horaire ouverture="09.00" fermeture="19.00"/>
          </jour>
          <jour id="3" nom="Mercredi" ferme="">
            <horaire ouverture="09.00" fermeture="19.00"/>
          </jour>
          <jour id="4" nom="Jeudi" ferme="">
            <horaire ouverture="09.00" fermeture="19.00"/>
          </jour>
          <jour id="5" nom="Vendredi" ferme="">
            <horaire ouverture="09.00" fermeture="19.00"/>
          </jour>
          <jour id="6" nom="Samedi" ferme="">
            <horaire ouverture="09.00" fermeture="19.00"/>
          </jour>
          <jour id="7" nom="Dimanche" ferme="1"/>
        </horaires>
        <services>
          <service>Vente de gaz domestique (Butane, Propane)</service>
          <service>Piste poids lourds</service>
          <service>Automate CB</service>
          <service>Automate CB 24/24</service>
        </services>
        <prix nom="Gazole" id="1" maj="2018-07-07T10:21:54" valeur="1439"/>
        <prix nom="SP95" id="2" maj="2018-07-07T10:21:54" valeur="1518"/>
        <prix nom="E10" id="5" maj="2018-07-07T10:21:54" valeur="1485"/>
        <rupture id="6" nom="SP98" debut="2013-07-09T11:45:00" fin=""/>
        <rupture id="3" nom="E85" debut="2016-06-29T00:00:00" fin=""/>
      </pdv>
    '''

    expected = '''<?xml version='1.0' encoding='UTF-8'?>
    <osm version='0.5'>
      <node id='3000001' visible='true' lat='46.541' lon='3.344'>
        <tag k='name' v='Gazole 1.439€ | SP95 1.518€ | E10 1.485€'/>
        <tag k='description' v='Gazole: 1.439€ (2018-07-07)&#10;SP95: 1.518€ (2018-07-07)&#10;E10: 1.485€ (2018-07-07)'/>
        <tag k='opening_hours' v='24/7'/>
        <tag k='amenity' v='fuel'/>
        <tag k='fuel:diesel' v='yes'/>
        <tag k='fuel:octane_95' v='yes'/>
        <tag k='fuel:e10' v='yes'/>
        <tag k='source' v='prix-carburant.economie.gouv.fr'/>
      </node>
    </osm>'''

    handler = create_osm.PrixCarburantHandler('test_out.xml')
    xml.sax.parseString(data, handler)
    with open('test_out.xml', 'r') as test_file:
        assert_xml_equal(test_file.read(), expected)

def test_convert_noclose():
    data = '''
  <pdv id="3410001" latitude="4633800" longitude="256800" cp="03410" pop="R">
    <adresse>65 Avenue des Martyrs</adresse>
    <ville>MONTLUCON-DOMERAT</ville>
    <horaires automate-24-24="">
      <jour id="1" nom="Lundi" ferme=""/>
      <jour id="2" nom="Mardi" ferme=""/>
      <jour id="3" nom="Mercredi" ferme=""/>
      <jour id="4" nom="Jeudi" ferme=""/>
      <jour id="5" nom="Vendredi" ferme=""/>
      <jour id="6" nom="Samedi" ferme=""/>
      <jour id="7" nom="Dimanche" ferme=""/>
    </horaires>
    <prix nom="Gazole" id="1" maj="2018-07-06T10:44:48" valeur="1395"/>
    <prix nom="SP95" id="2" maj="2018-07-06T10:44:48" valeur="1492"/>
    <prix nom="GPLc" id="4" maj="2018-06-07T10:15:31" valeur="720"/>
    <prix nom="E10" id="5" maj="2018-07-06T10:44:48" valeur="1444"/>
    <prix nom="SP98" id="6" maj="2018-07-06T10:44:49" valeur="1524"/>
  </pdv>
    '''

    expected = '''<?xml version='1.0' encoding='UTF-8'?>
    <osm version='0.5'>
      <node id='3410001' visible='true' lat='46.338' lon='2.568'>
        <tag k='name' v='Gazole 1.395€ | SP95 1.492€ | GPLc 0.72€ | E10 1.444€ | SP98 1.524€'/>
        <tag k='description' v='Gazole: 1.395€ (2018-07-06)&#10;SP95: 1.492€ (2018-07-06)&#10;GPLc: 0.72€ (2018-06-07)&#10;E10: 1.444€ (2018-07-06)&#10;SP98: 1.524€ (2018-07-06)'/>
        <tag k='opening_hours' v='24/7'/>
        <tag k='amenity' v='fuel'/>
        <tag k='fuel:diesel' v='yes'/>
        <tag k='fuel:octane_95' v='yes'/>
        <tag k='fuel:lgp' v='yes'/>
        <tag k='fuel:e10' v='yes'/>
        <tag k='fuel:octane_98' v='yes'/>
        <tag k='source' v='prix-carburant.economie.gouv.fr'/>
      </node>
    </osm>'''

    handler = create_osm.PrixCarburantHandler('test_out.xml')
    xml.sax.parseString(data, handler)
    with open('test_out.xml', 'r') as test_file:
        assert_xml_equal(test_file.read(), expected)

def assert_xml_equal(xml1, xml2):
    '''
    write the two XML strings on a single line without any additional
    whitespace to compare them safely
    '''
    tree1 = ET.fromstring(xml1)
    for node in tree1.iter():
        node.text = None
        node.tail = None

    tree2 = ET.fromstring(xml2)
    for node in tree2.iter():
        node.text = None
        node.tail = None

    assert ET.tostring(tree1) == ET.tostring(tree2)
