# uncompyle6 version 3.3.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.7.3 (v3.7.3:ef4ec6ed12, Mar 25 2019, 21:26:53) [MSC v.1916 32 bit (Intel)]
# Embedded file name: C:\Users\jfayr\flight\aviationFormula\aviationFormula.py
# Compiled at: 2019-05-19 12:59:54
from math import sin, asin, cos, acos, tan, atan2, sqrt, radians, degrees, pi

def gcDistance(lat1, lon1, lat2, lon2):
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    return 2 * asin(sqrt(sin((lat1 - lat2) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon1 - lon2) / 2) ** 2))


def gcDistanceNm(lat1, lon1, lat2, lon2):
    return 10800 / pi * gcDistance(lat1, lon1, lat2, lon2)


def gcIntermediatePoint(lat1, lon1, lat2, lon2, *args):
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    if len(args):
        f = args[0]
    else:
        f = 0.5
    d = gcDistance(lat1, lon1, lat2, lon2)
    A = sin((1 - f) * d) / sin(d)
    B = sin(f * d) / sin(d)
    x = A * cos(lat1) * cos(lon1) + B * cos(lat2) * cos(lon2)
    y = A * cos(lat1) * sin(lon1) + B * cos(lat2) * sin(lon2)
    z = A * sin(lat1) + B * sin(lat2)
    lat = atan2(z, sqrt(x ** 2 + y ** 2))
    lon = atan2(y, x)
    return [
     degrees(lat), degrees(lon)]


def calcBearing(lat1, lon1, lat2, lon2):
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    dLon = lon2 - lon1
    y = sin(dLon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
    return atan2(y, x)