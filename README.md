# Timeline itinerary

## About

This repository contains a Python script to process your Google location history data, and a basic website using [d3](https://d3js.org/) to render this data.

## Usage

1. Download your location history using [Google Takeout](https://accounts.google.com/ServiceLogin?service=backup). [Here are the instructions.](https://support.google.com/accounts/answer/3024190?hl=en)

2. Clone or download this repository; e.g.:

```
git clone https://github.com/majube/timeline-itinerary
```

3. Use the python script `preprocess.py`, in the root folder of this directory, to unzip and process the location data. If you don't have [Python you'll have to install it.](https://www.python.org/downloads/) The script doesn't have any dependencies outside the standard library.

Usage:
```
cd timeline-itinerary
python preprocess.py takeout-20230325T162834Z-001.zip 02/09/2020
```

Other options for preprocessing the data can be seen by typing `python preprocess.py -h`.

4. Start a webserver to serve the webpage:

```
python -m http.server 8080
```

5. Open a browser and navigate to [http://localhost:8080/](http://localhost:8080/). The page with a globe with points from your location history on it should load!