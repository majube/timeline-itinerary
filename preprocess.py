import argparse, json
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

RECORDS_PATH = "Takeout/Location History/Records.json"


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
        default=1,
        dest="ERROR",
        required=False,
        type=float,
        help="Error distance (in km) to add to locations",
    )

    return parser


def parse_ts(ts):
    return datetime.strptime(ts.split("T")[0], "%Y-%m-%d")


def main(takeoutzip, startdate, enddate, error):
    with ZipFile(takeoutzip, "r") as zip:
        zip.extractall()

    with open(takeoutzip.parent / RECORDS_PATH, "r") as f:
        lhist = json.loads(f.read())

    filtered_locs = []
    parse_date = True
    for i, loc in enumerate(lhist["locations"]):
        if parse_date:
            locdate = parse_ts(loc["timestamp"])

        if locdate < startdate:
            next
        elif locdate > enddate:
            break
        else:
            try:
                nlocdate = parse_ts(lhist["locations"][i + 1]["timestamp"])
            except IndexError:
                break
            else:
                if nlocdate > locdate:
                    filtered_locs.append(
                        {
                            "date": locdate.strftime("%Y-%m-%d"),
                            "lat": loc["latitudeE7"],
                            "lon": loc["longitudeE7"],
                        }
                    )
                locdate = nlocdate
                parse_date = False

    # TODO: add autocorrelated error to the co-ordinates of each day

    with open("filtered.json", "w") as f:
        f.write(json.dumps(filtered_locs))


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

    if not (args.ZIPFILE[0].is_file()):
        exit(f"{args.ZIPFILE[0]} doesn't exist")

    main(args.ZIPFILE[0], startdate, enddate, args.ERROR)
