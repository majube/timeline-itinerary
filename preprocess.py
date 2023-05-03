"""
Preprocesses Google Timeline takeout data by:
    - Unzipping the takeout data
    - Filtering out location outside of the given date interval
    - Filtering out all but the last location for each day
    - Filtering out days in which the last location was the same as that of the previous day
    - Adding a random error to each location
    - Saving the data to a JSON file
"""

import argparse, json
from datetime import datetime
from itertools import pairwise
from math import asin, cos, pi, sin, sqrt
from pathlib import Path
from random import random
from zipfile import ZipFile


RECORDS_PATH = Path(
    "Takeout/Location History/Records.json"
)  # Subpath of timeline records in takeout zip
RESOLUTION = 10  # radius within which end-of-day locations will be considered identical
R = 6371  # mean radius of earth (km)
DEFAULT_ERROR = 1  # km
DATA_FOLDER = Path("data")


def init_argparse():
    parser = argparse.ArgumentParser(
        description="Preprocess Google Timeline Takeout data from a starting date until an ending data, and add an error to it"
    )

    parser.add_argument(
        "ZIPFILE",
        nargs=1,
        action="store",
        type=Path,
        metavar="takeout-20230325T162834Z-001.zip",
        help="Google Timeline Takeout zip file",
    )
    parser.add_argument(
        "STARTDATE", nargs=1, action="store", metavar="DD/MM/YYYY", help="Start date"
    )
    parser.add_argument(
        "-u",
        "--until",
        action="store",
        default=[datetime.today().strftime("%d/%m/%Y")],
        dest="ENDDATE",
        metavar="DD/MM/YYYY",
        required=False,
        help="End date (default: today)",
    )
    parser.add_argument(
        "-e",
        "--error",
        action="store",
        default=DEFAULT_ERROR,
        dest="ERROR",
        required=False,
        type=float,
        help="Error distance (in km) to add to locations",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        default="itin.json",
        dest="OUTPUT",
        metavar="outputfile.json",
        required=False,
        help="Output file (preprocessed JSON)",
    )

    return parser


def d(lat1, lon1, lat2, lon2):
    """
    Calculates distance (in km) between two points on sphere using haversine formula

    Parameters:
        lat1 (float): latitude of point 1 (in degrees)
        lon1 (float): longitude of point 1 (in degrees)
        lat2 (float): latitude of point 2 (in degrees)
        lon2 (float): longitude of point 2 (in degrees)

    Returns:
        d (float): distance between points (in km)
    """
    lat1, lon1, lat2, lon2 = map(lambda c: c * pi / 180, (lat1, lon1, lat2, lon2))
    return (
        2
        * R
        * asin(
            sqrt(
                sin((lat2 - lat1) / 2) ** 2
                + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
            )
        )
    )


def add_error(lat, lon, error):
    # flat plane approximation
    coordinate_error = (error * 180) / (pi * R)
    angle = 2 * pi * random()
    return lat + coordinate_error * sin(angle), lon + coordinate_error * cos(angle)


def parse_ts(ts):
    return datetime.strptime(ts.split("T")[0], "%Y-%m-%d")


def main(takeoutzip, startdate, enddate, error, outputfile):
    # unzip takeout file
    with ZipFile(takeoutzip, "r") as zip:
        zip.extractall()

    # load location history json
    with open(takeoutzip.parent / RECORDS_PATH, "r") as f:
        lhist = json.loads(f.read())

    # retain last location of the day
    day_locs = []
    for cday, nday in pairwise(lhist["locations"]):

        cdate, ndate = map(parse_ts, (cday['timestamp'], nday['timestamp']))
        # before start of date range
        if ndate < startdate:
            next
        # after start of date range
        elif cdate > enddate:
            break
        # in date range and cday last loc of day
        elif ndate > cdate:
            day_locs.append(
                {
                    "date": cdate.strftime("%Y-%m-%d"),
                    "lat": cday["latitudeE7"] / 1e7,
                    "lon": cday["longitudeE7"] / 1e7,
                }
            )

    # filter out same location on subsequent days and add error
    errored_locs = []
    start = 0
    while True:
        startcoords = (day_locs[start]["lat"], day_locs[start]["lon"])
        for i in range(start, len(day_locs)):
            if (
                d(
                    *startcoords,
                    day_locs[i]["lat"],
                    day_locs[i]["lon"],
                )
                > RESOLUTION
            ):
                latE, lonE = add_error(
                    day_locs[start]["lat"], day_locs[start]["lon"], error
                )
                errored_locs.append(
                    {"date": day_locs[start]["date"], "lat": latE, "lon": lonE}
                )
                start = i
                break

        if i + 1 == len(day_locs):
            break

    # save processed json
    with open(DATA_FOLDER / Path(outputfile), "w") as f:
        f.write(json.dumps(errored_locs))


if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()

    startdate, enddate = [
        datetime.strptime(d[0], "%d/%m/%Y") for d in (args.STARTDATE, args.ENDDATE)
    ]
    if enddate < startdate:
        exit(
            f"Start date ({args.STARTDATE}) needs to be before end date ({args.ENDDATE})"
        )

    if not args.ZIPFILE[0].is_file():
        exit(f"{args.ZIPFILE[0]} doesn't exist")

    main(args.ZIPFILE[0], startdate, enddate, args.ERROR, args.OUTPUT)
