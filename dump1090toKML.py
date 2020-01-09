import csv
import sys
import random
import string
import os.path

arguments = len(sys.argv) - 1
if arguments < 1:
    print("No file specified.")
    quit()
else:
    fileName = sys.argv[1]

if not os.path.isdir("./output"):
    os.mkdir("./output")

def set_HEX_color():
    """Generates a random HEX 00-FF color for KML;
    input: None
    Output: color aabbggrr where aa is opacity, bb is blue, gg is green, and rr is red"""
    color = 'ff'
    HEXcolor = "%06x" % random.randint(0, 0xFFFFFF)
    color += HEXcolor
    return color

def load_dump1090():
    """Imports dump1090 log from csv text file and returns dictionary of log
    input: None
    output: {ICAO:[HEXcolor, CallSign, Track[long,lat,alt]]"""
    KMLdict = {}

    with open(fileName, newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=("MSG", "A", "B", "C", "ICAO", "D", "DATE1", "TIME1", "DATE2", "TIME2", "CallSign", "alt", "E", "F", "long", "lat", "G", "H", "I", "J", "K", "L"))
        for row in reader:
            if row['ICAO'] not in KMLdict:
                KMLdict[row['ICAO']] = {'HEXcolor': set_HEX_color(), 'CallSign': row['CallSign'], 'Track': []}
            if row['CallSign'] not in KMLdict[row['ICAO']]['CallSign']:
                KMLdict[row['ICAO']]['CallSign'] = row['CallSign']
            if row['long'] != '':
                KMLdict[row['ICAO']]['Track'].append([row['lat'], row['long'], row['alt'], row['DATE1'], row['TIME1']])

    return KMLdict

def createKML(KMLdict, ICAO):
    """Generates a KML file for each track
    input: KMLdict
    output: ICAO.kml"""
    aircraft = ICAO
    color = KMLdict[ICAO]['HEXcolor']
    callsign = KMLdict[ICAO]['CallSign']
    track = KMLdict[ICAO]['Track']
    if KMLdict[ICAO]['Track'] == []:
        return
    track_output = ''

    if callsign != '':
        name = callsign.rstrip()
    else:
        name = ICAO

    for position in track:
        track_output += position[0] + ',' + position[1] + ',' + position[2] + "\n"

    with open("./output/" + name + ".kml", "w") as kmlfile: 
        kmlfile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        kmlfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        kmlfile.write("<Document>\n")
        kmlfile.write(f"<name>{name}</name>\n")
        kmlfile.write(f'<description>Track of aircraft operating on the 1090 MHz spectrum with either Mode S or ADS-B</description>\n')
        kmlfile.write(f'<Style id=\"None\">\n<LineStyle>\n<color>{color}</color>\n<width>4</width>\n</LineStyle>\n')
        kmlfile.write(f'<PolyStyle>\n<color>7f00ff00</color>\n</PolyStyle>\n</Style>\n')
        kmlfile.write(f'<Placemark>\n<name>{aircraft}</name>\n<description>{aircraft} with CallSign {callsign}</description>\n')
        kmlfile.write("<styleUrl>None</styleUrl>\n<LineString>\n<tessellate>1</tessellate>\n<altitudeMode>absolute</altitudeMode>\n")
        kmlfile.write(f'<coordinates> {track_output}</coordinates>\n</LineString>\n</Placemark>\n</Document>\n</kml>\n')

KMLdict = load_dump1090()
no_position = []

for aircraft in KMLdict.keys():
    createKML(KMLdict, aircraft)
    if KMLdict[aircraft]['Track'] == []:
        if KMLdict[aircraft]['CallSign'] != '':
            no_position.append(KMLdict[aircraft]['CallSign'])
        else:
            no_position.append(aircraft)

print("KML created with "+ str(len(KMLdict)) + " unique aircraft contacts.")
if no_position != []:
    print("The following " + str(len(no_position)) + " aircraft did not broadcast positions:" + str(no_position))
