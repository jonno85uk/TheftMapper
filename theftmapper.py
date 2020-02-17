#!/usr/bin/env python
# Tool to visualise theft reports onto a map
# Copyright (C) 2020  Jon Noble jonnobleuk@gmail.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import folium
from typing import Final
import datetime
from enum import Enum
import argparse


DEFAULT_DATA_FILE: Final = "data.csv"
DEFAULT_ZOOM: Final = 12  # Bristol fits in browser at 1920x1080
DEFAULT_LOCATION: Final = "51.4545, -2.5879"  # Bristol, England
DATE_INDEX: Final = 1
LONG_INDEX: Final = 2
LAT_INDEX: Final = 3
ACCURATE_INDEX: Final = 4
LINK_INDEX: Final = 5
TYPE_INDEX: Final = 6
NOTES_INDEX: Final = 7
HTML_SAVE_FILE: Final = "thefts.html"
DEFAULT_DAYS: Final = 0
DEFAULT_CIRCLE_SIZE: Final = 1000


class EntryType(Enum):
    UNKNOWN = 0,
    STOLEN = 1,
    FOUND = 2,
    SIGHTING = 3,
    BURNT = 4


parser = argparse.ArgumentParser(description="Place theft reports onto a map")
parser.add_argument("-i", dest="datafile", default=DEFAULT_DATA_FILE,
                    help="csv file of the reports. default='{0}'".format(DEFAULT_DATA_FILE))
parser.add_argument("-o", dest="savefile", default=HTML_SAVE_FILE,
                    help="The name of the created html file. default='{0}'".format(HTML_SAVE_FILE))
parser.add_argument("-z", dest="zoom", default=DEFAULT_ZOOM,
                    help="Zoom level of the map on file open. default='{0}'".format(DEFAULT_ZOOM))
parser.add_argument("-l", dest="location", default=DEFAULT_LOCATION,
                    help="Location to center map on file open e.g. longitude,latitude. default='{0}'"
                    .format(DEFAULT_LOCATION))
parser.add_argument("-c", dest="circlesize", default=DEFAULT_CIRCLE_SIZE,
                    help="A variable to adjust the size of the displayed circles. default='{0}'"
                    .format(DEFAULT_CIRCLE_SIZE))
# TODO: day filter
# parser.add_argument("-d", dest="days", default=0,
#                     help="The amount of days (from now) of data to plot on the map (0==all days possible). "
#                          "default='{0}'".format(DEFAULT_DAYS))

args = parser.parse_args()


class Entry:
    def __init__(self, date, longitude, latitude, accurate, entry_type, url=None, notes=None):
        self.date = datetime.datetime.strptime(date, "%d/%m/%Y")
        self.longitude = longitude
        self.latitude = latitude
        self.accurate = accurate
        if str(entry_type).lower() == "stolen":
            self.entry_type = EntryType.STOLEN
        elif str(entry_type).lower() == "found":
            self.entry_type = EntryType.FOUND
        elif str(entry_type).lower() == "sighting":
            self.entry_type = EntryType.SIGHTING
        elif str(entry_type).lower() == "burnt":
            self.entry_type = EntryType.BURNT
        else:
            self.entry_type = EntryType.UNKNOWN
        self.link = url
        self.notes = notes

    def __str__(self):
        return "Date = {self.date}, Location = ({self.longitude}, {self.latitude}), Type = {self.entry_type}, " \
               "Link = {self.link}".format(self=self)


details = open(args.datafile, "r")
details.readline()  # Ignore first line
entries = []
for line in details.readlines():
    details = line.split(',')
    e = Entry(date=details[DATE_INDEX], longitude=details[LONG_INDEX], latitude=details[LAT_INDEX],
              accurate=details[ACCURATE_INDEX].lower() == "yes", entry_type=details[TYPE_INDEX],
              url=details[LINK_INDEX], notes=details[NOTES_INDEX])
    entries.append(e)

m = folium.Map(location=args.location.split(','), zoom_start=DEFAULT_ZOOM)


for e in entries:
    colour = None
    sign = None
    prefix = None
    if e.entry_type == EntryType.STOLEN:
        colour = "red"
        sign = "exclamation-circle"
        prefix = "fa"
    elif e.entry_type == EntryType.FOUND:
        colour = "green"
        sign = "bell"
        prefix = "fa"
    elif e.entry_type == EntryType.BURNT:
        colour = "orange"
        sign = "fire"
        prefix = "fa"
    elif e.entry_type == EntryType.SIGHTING:
        colour = "blue"
        sign = "binoculars"
        prefix = "fa"
    else:
        colour = "black"
    link = ""
    if e.link:
        link = "<a href='{0}'>Link</a>".format(e.link)
    if e.accurate:
        folium.Marker(
            location=[e.longitude, e.latitude],
            popup="{0}\n{1}".format(e.date.date(), link),
            icon=folium.Icon(color=colour, icon=sign, prefix=prefix)
        ).add_to(m)
    else:
        folium.Circle(
            location=(e.longitude, e.latitude),
            radius=arg.circlesize,
            color=colour,
            fill=True,
            popup="{0}\n{1}".format(e.date.date(), link),
            icon=folium.Icon(color=colour, icon=sign, prefix=prefix)
        ).add_to(m)

m.save(args.savefile)

print("Map created with {0} reports".format(len(entries)))
