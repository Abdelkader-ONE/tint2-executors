#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
Development just started. Nothing useful inside yet.

Dependencies: wget
"""

import subprocess
import json
from collections import namedtuple
import locale
import os
import sys


def main():
    t2ec_dir = os.getenv("HOME") + "/.t2ecol"
    response = None
    name = None

    settings = Settings()

    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if sys.argv[i].upper() == '-N':
                name = "Weather:"

            if sys.argv[i].upper().startswith('-M'):
                name = sys.argv[i][2::]

            if sys.argv[i].startswith("-I"):
                settings.items = sys.argv[i][2::]

            if sys.argv[i].startswith("-A"):
                settings.api_key = sys.argv[i][2::]

            if sys.argv[i].startswith("-C"):
                settings.city_id = sys.argv[i][2::]

            if sys.argv[i].startswith("-U"):
                settings.units = sys.argv[i][2::]

            if sys.argv[i].startswith("-L"):
                settings.lang = sys.argv[i][2::]

    request_url = "http://api.openweathermap.org/data/2.5/weather?id=" + settings.city_id + "&appid=" + \
                  settings.api_key + "&units=" + settings.units + "&lang=" + settings.lang
    try:
        response = subprocess.check_output("wget -qO- '" + request_url + "'", shell=True)
        subprocess.call(["echo '" + str(response) + "' > " + t2ec_dir + "/.weather-" + settings.city_id], shell=True)

    except subprocess.CalledProcessError as exitcode:
        print("Error accessing openweathermap.org, exit code: ", exitcode.returncode)
        exit(0)

    if response is not None:
        # Convert JSON to object - after DS. at https://stackoverflow.com/a/15882054/4040598
        owm = json.loads(response, object_hook=lambda d: namedtuple('t', d.keys())(*d.values()))
        print_output(owm, name, settings.items, settings.units)


def print_output(owm, name, items, units):
    icons = {'01d': '01d.png',
             '01n': '01n.png',
             '02d': '02d.png',
             '02n': '02n.png',
             '03d': '03d.png',
             '03n': '03d.png',
             '04d': '04d.png',
             '04n': '04d.png',
             '09d': '09d.png',
             '09n': '09d.png',
             '10d': '10d.png',
             '10n': '10n.png',
             '11d': '11d.png',
             '11n': '11d.png',
             '13d': '13d.png',
             '13n': '13d.png',
             '50d': '50d.png',
             '50n': '50d.png'}

    if owm.cod == 200:
        #print(owm)
        if name is not None:
            print(name)
        else:
            icon = getattr(owm.weather[0], "icon")
            if icon:
                print("icons/" + icons[icon])
            else:
                print("icons/refresh.svg")

        for i in range(len(items)):
            if items[i] == "c":
                print(owm.name + ", " + getattr(owm.sys, "country"))
            if items[i] == "s":
                print(getattr(owm.weather[0], "main"))
            if items[i] == "d":
                print(getattr(owm.weather[0], "description"))
            if items[i] == "t":
                unit = "℉" if units == "imperial" else "℃"
                print(str(getattr(owm.main, "temp")) + unit)
            if items[i] == "p":
                print(str(getattr(owm.main, "pressure")) + " hpa")
            if items[i] == "p":
                print(str(getattr(owm.wind, "speed")) + " m/s " + str(getattr(owm.wind, "deg")) + " deg")

    else:
        print("Error accessing openweathermap.org, HTTP status: " + str(owm.cod))
        exit(0)


class Settings:
    def __init__(self):
        super().__init__()

        t2ec_dir = os.getenv("HOME") + "/.t2ecol"
        # Create settings file if not found
        if not os.path.isdir(t2ec_dir):
            os.makedirs(t2ec_dir)
        if not os.path.isfile(t2ec_dir + "/weatherrc"):
            config = [
                "# Items: [s]hort description, [d]escription, [t]emperature, [t]ressure, [h]umidity, [w]ind, [c]ity name\n",
                "# API key: go to http://openweathermap.org and get one\n",
                "# city_id you will find at http://openweathermap.org/find\n",
                "# units may be metric or imperial\n",
                "# uncomment lang to override system $LANG value\n",
                "# Delete this file if something goes wrong :)\n",
                "# ------------------------------------------------\n",
                "items = cstw\n",
                "api_key = your_key_here\n",
                "city_id = 2643743\n",
                "units = metric\n",
                "#lang = en"]

            subprocess.call(["echo '" + ''.join(config) + "' > " + t2ec_dir + "/weatherrc"], shell=True)

        self.items = "cstw"
        self.api_key = ""
        self.city_id = "2643743"  # London, UK
        self.units = "metric"
        self.lang = None

        # read from settings file
        lines = open(t2ec_dir + "/weatherrc", 'r').read().rstrip().splitlines()

        for line in lines:
            if not line.startswith("#"):
                if line.startswith("items"):
                    self.items = line.split("=")[1].strip()
                elif line.startswith("api_key"):
                    self.api_key = line.split("=")[1].strip()
                elif line.startswith("city_id"):
                    self.city_id = line.split("=")[1].strip()
                elif line.startswith("units"):
                    self.units = line.split("=")[1].strip()
                elif line.startswith("lang"):
                    self.lang = line.split("=")[1].strip()

        if self.lang is None:
            loc = locale.getdefaultlocale()[0][:2]
            self.lang = loc if loc else "en"


if __name__ == "__main__":
    main()