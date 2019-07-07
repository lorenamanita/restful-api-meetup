# -*- coding: utf-8 -*-
# pylint: disable=locally-disabled, multiple-statements
# pylint: disable=fixme, line-too-long, invalid-name
# pylint: disable=W0703

""" Meetup Flask API """

import json
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from geopy import distance
from pymysql import cursors, connect, err


# app initialization
app = Flask(__name__)

# load  configuration settings
with open("settings.json") as settings:
    cfg = json.load(settings)

# setup database connection
try:
    db_conn = connect(host=cfg['db_host'],
                      user=cfg['db_user'],
                      password=cfg['db_password'],
                      db=cfg['db_name'],
                      charset='utf8mb4',
                      cursorclass=cursors.DictCursor)
except err.OperationalError:
    print("ERR: DB CONNECTION ERROR")
    sys.exit(1)


# helper functions
def get_near_groups(lat, lon, num):
    """ list a total of `num` cities closest to given `lat` and `lon` coordinates
    :param: lat, lon, num: latitude [-90..90], longitude [180..-180], in degrees.
    :return: dict object
    """
    with db_conn.cursor() as cur:
        sql = '''SELECT CITY, LAT, LON FROM (
                SELECT DISTINCT CITY, LAT, LON, (X+Y) AS Z FROM (
                SELECT CITY, LAT, LON, ABS(LAT - %s) AS X, ABS(LON - %s) AS Y FROM cities ORDER BY X ASC) AS PIZZA 
                GROUP BY CITY 
                ORDER BY Z 
                LIMIT %s 
                ) AS CICCIO'''
        cur.execute(sql, (lat, lon, num))
        query_result = cur.fetchall()   # a list of dicts

    # update the returned dict with distance information
    for i in query_result:
        i.update({'DIST': round(distance.distance((lat, lon), (i['LAT'], i['LON'])).km, 2)})    # geopy geodesic distance measure

    return sorted(query_result, key=lambda x: x['DIST'])


def get_top_cities(date, num):
    """ run SQL query to collect data for the /near endpoint
    :param: lat, lon, num
    :return: cursor object
    """
    with db_conn.cursor() as cur:
        sql = "SELECT DISTINCT `CITY`, `DATE`, COUNT(`MID`) AS `TOT` \
                FROM `cities` \
                WHERE `DATE` = %s \
                GROUP BY `CITY` \
                ORDER BY `TOT` DESC \
                LIMIT %s"
        cur.execute(sql, (date, num,))
        return cur.fetchall()


# API endpoints
# /near endpoint -- closest groups
@app.route('/near')
def near_groups():
    """ Given lat and lon and num, return the num closest groups in distance
    :param: lat, lon, num. latitude and longitude from the url: http://127.0.0.1:5000/near?lat=43&lon=-5.6&num=10
    :return: JSON string
    """
    # capture url parameters, set type and defaults for missing values
    lat = request.args.get('lat', 0, type=float)
    lon = request.args.get('lon', 0, type=float)
    num = request.args.get('num', 1, type=int)

    if lat not in range(-91, 91):
        lat = 0
    if lon not in range(-181, 181):
        lon = 0

    return jsonify(get_near_groups(lat, lon, num)[:num])


# /topCities endpoint -- cities top attendees
@app.route('/topCities')
def top_cities():
    """ Given a date (ISO) return the top num cities sorted by the num people attending the event on that day
    :param: date (ISO). http://127.0.0.1:5000/topCities?date=20190801&num=10
    :return: JSON string"""
    day = request.args.get('day', datetime.now().strftime("%Y%m%d"), type=str)
    num = request.args.get('num', 1, type=int)

    # input validation
    if num <= 1:
        num = 1

    try:
        datetime.strptime(day, '%Y%m%d')
    except ValueError:
        day = datetime.now().strftime("%Y%m%d") # when missing, set today as default date

    return jsonify(get_top_cities(day, num))


if __name__ == '__main__':
    app.run()
