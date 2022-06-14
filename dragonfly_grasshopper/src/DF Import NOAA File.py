# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Import climate data from a .csv file of annual data obtained from the National
Oceanic and Atmospheric Administration (NOAA) database.  The database can be
accessed here:
https://gis.ncdc.noaa.gov/maps/ncei/cdo/hourly
-

    Args:
        _noaa_file: The path to a .csv file of annual data obtained from the NOAA
            database on your system as a string.
        time_zone_: Optional time zone for the station.  If blank, a default time
            zone will be estimated from the longitude.
        _timestep_: Integer forthe timestep at which the data collections should be output.
            Data in the .csv that does not conform to this timestep will be
            ignored in the output data collections. This can be set as high
            as 60 to ensure that all data from the .csv file is imported.
            However, such large data collections can be time consuming to
            edit. (Default: 1).
        _run: Set to True to run the component and import the data.

    Returns:
        dry_bulb_temp: The houlry dry bulb temperature, in C.
            Note that this is a full numeric field (i.e. 23.6) and not an integer
            representation with tenths. Valid values range from 70 C to
            70 C. Missing value for this field is 99.9.
        dew_point_temp: The hourly dew point temperature, in C.
            Note that this is a full numeric field (i.e. 23.6) and not an integer
            representation with tenths. Valid values range from 70 C to
            70 C. Missing value for this field is 99.9.
        wind_speed: The hourly wind speed in m/sec.
            Values can range from 0 to 40. Missing value is 999.
        wind_direction: The hourly wind direction in degrees.
            The convention is that North=0.0, East=90.0, South=180.0, West=270.0.
            (If wind is calm for the given hour, the direction equals zero.)
            Values can range from 0 to 360. Missing value is 999.
        total_sky_cover: The fraction for total sky cover (tenths of coverage).
            (i.e. 1 is 1/10 covered. 10 is total coverage) (Amount of sky
            dome in tenths covered by clouds or obscuring phenomena at the
            hour indicated at the time indicated.) Minimum value is 0;
            maximum value is 10; missing value is 99."
        atmos_pressure: The hourly weather station pressure in Pa.
            Valid values range from 31,000 to 120,000...
            Missing value for this field is 999999."
        visibility: This is the value for visibility in km. (Horizontal
            visibilitY). It is not currently used in EnergyPlus calculations.
            Missing value is 9999.
        ceiling_Height: This is the value for ceiling height in m. (77777 is
            unlimited ceiling height. 88888 is cirroform ceiling.) It is not
            currently used in EnergyPlus calculations. Missing value is 99999
        model_year: The year from which the hourly data has been extracted.
            Note that, for this component to run correclty, all of the data in
            the text file must be from a single year.
"""

ghenv.Component.Name = 'DF Import NOAA File'
ghenv.Component.NickName = 'ImportNOAA'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import os
import csv
import datetime

try:
    from ladybug.location import Location
    from ladybug.dt import DateTime
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.header import Header
    from ladybug.datacollection import HourlyDiscontinuousCollection, HourlyContinuousCollection
    from ladybug.datatype.temperature import DryBulbTemperature, DewPointTemperature
    from ladybug.datatype.speed import WindSpeed
    from ladybug.datatype.angle import WindDirection
    from ladybug.datatype.fraction import TotalSkyCover
    from ladybug.datatype.pressure import AtmosphericStationPressure
    from ladybug.datatype.distance import Visibility, CeilingHeight
    from ladybug.datatype.generic import GenericType
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def extract_location(climate_file, time_zone=None):
    """Extract a Ladybug Location object from the data in the CSV.
    
    Args:
        climate_file: file path to the NCDC .csv file.
        time_zone: Optional integer for the time zone. If None, it will be
            estimated from the longitude in the file.
    """
    with open(climate_file) as station_file:
        station_file.readline()  # Skip header row

        # get the pattern of data within the file
        dat_line = station_file.readline().strip().split(',')

        # parse all of the info from the file
        station_id = dat_line[0].replace('"', '')
        city = dat_line[6].replace('"', '')
        latitude = float(dat_line[3].replace('"', ''))
        longitude = float(dat_line[4].replace('"', ''))
        elevation = float(dat_line[5].replace('"', ''))

        # estimate or parse time zone.
        if time_zone:
            assert -12 <= time_zone <= 14, ' time_zone must be between -12 and '\
                ' 14. Got {}.'.format(time_zone)
            time_zone = time_zone
        else:
            time_zone = int((longitude / 180) * 12)

        # build the location object
        location = Location(
            city=city, latitude=latitude, longitude=longitude,
            time_zone=time_zone, elevation=elevation,
            station_id=station_id, source='NCDC')
    return location, time_zone


def build_collection(values, dates, data_type, unit, time_offset, year):
    """Build a data collection from raw noaa data and process it to the timestep.

    Args:
        values: A list of values to be included in the data collection.
        dates: A list of datetime strings that align with the values.
        data_type: Ladybug data type for the data collection.
        unit: Text for the unit of the collection.
        time_offset: Python timedelta object to correct for the time zone.
        year: Integer for the year of the data.
    """
    if values == []:
        return None

    # convert date codes into datetimes and ensure no duplicates
    leap_yr = True if year % 4 == 0 else False
    datetimes = []
    clean_values = []
    for i, (dat, val) in enumerate(zip(dates, values)):
        if dat != dates[i - 1]:
            yr, month, day, hr, minute = int(dat[:4]), int(dat[5:7]), \
                int(dat[8:10]), int(dat[11:13]), int(dat[14:16])
            py_dat = datetime.datetime(yr, month, day, hr, minute) + time_offset
            if py_dat.year == year:
                lb_dat = DateTime(py_dat.month, py_dat.day, py_dat.hour,
                                  py_dat.minute, leap_year=leap_yr)
                datetimes.append(lb_dat)
                clean_values.append(val)

    # make a discontinuous cata collection
    data_header = Header(data_type, unit, AnalysisPeriod(is_leap_year=leap_yr))
    data_init = HourlyDiscontinuousCollection(data_header, clean_values, datetimes)
    data_final = data_init.validate_analysis_period()

    # cull out unwanted timesteps.
    if _timestep_:
        data_final.convert_to_culled_timestep(_timestep_)
    else:
        data_final.convert_to_culled_timestep(1)

    return data_final


if all_required_inputs(ghenv.Component) and _run:
    # check that the file exists.
    assert os.path.isfile(_noaa_file), 'Cannot find file at {}.'.format(_noaa_file)

    # extract the location and the time zone
    location, t_zone = extract_location(_noaa_file, time_zone_)
    t_offset = datetime.timedelta(seconds=t_zone * 3600)

    # empty lists to be filled with data
    all_years = []
    all_dates = []
    header_txt = []
    db_t = []
    db_t_dates = []
    dp_t = []
    dp_t_dates = []
    ws = []
    ws_dates = []
    wd = []
    wd_dates = []
    sc = []
    sc_dates = []
    slp = []
    slp_dates = []
    vis = []
    vis_dates = []
    ceil = []
    ceil_dates = []

    # pull relevant data out of the file
    with open(_noaa_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', skipinitialspace=True)

        # find the column with total sky cover if it exists
        header = csv_reader.next()  # get header row
        sc_col = None
        for i, colname in enumerate(header):
            if colname == 'GF1':
                sc_col = i

        for row in csv_reader:
            # parse the dates and the years
            date_row = row[1]
            all_dates.append(date_row)
            all_years.append(int(date_row[:4]))

            # parse the wind information
            wind_info = row[10].split(',')
            if wind_info[0] != '999':
                wd.append(float(wind_info[0]))
                wd_dates.append(date_row)
            if wind_info[3] != '9999':
                ws.append(float(wind_info[3]) / 10)
                ws_dates.append(date_row)

            # parse the ceiling height information
            ceil_info = row[11].split(',')
            if ceil_info[0] != '99999':
                ceil.append(float(ceil_info[0]))
                ceil_dates.append(date_row)

            # parse the visibility information
            vis_info = row[12].split(',')
            if vis_info[0] != '999999':
                vis.append(float(vis_info[0]) / 1000)
                vis_dates.append(date_row)

            # parse the dry bulb and dew point information
            temp_info = row[13].split(',')
            if temp_info[0] != '+9999':
                db_t.append(float(temp_info[0]) / 10)
                db_t_dates.append(date_row)
            dwpt_info = row[14].split(',')
            if dwpt_info[0] != '+9999':
                dp_t.append(float(dwpt_info[0]) / 10)
                dp_t_dates.append(date_row)

            # parse the pressure information
            slp_info = row[15].split(',')
            if slp_info[0] != '99999':
                slp.append(float(slp_info[0]) * 10)
                slp_dates.append(date_row)

            # parse the sky cover info if it exists
            if sc_col is not None and row[sc_col] != '':
                sc_info = row[sc_col].split(',')
                sc_oktas = int(sc_info[0])
                sc_tenths = sc_oktas * (10 / 8) if sc_oktas != 9 else 10
                sc.append(sc_tenths)
                sc_dates.append(date_row)

    # get the most predominant year in the file to make sure all data is for one year
    dom_yr = int(max(set(all_years), key=all_years.count))
    model_year = build_collection(
        all_years, all_dates, GenericType('Years', 'yr'), 'yr', t_offset, dom_yr)

    # build data collections from the imported values
    dry_bulb_temp = build_collection(
        db_t, db_t_dates, DryBulbTemperature(), 'C', t_offset, dom_yr)
    dew_point_temp = build_collection(
        dp_t, dp_t_dates, DewPointTemperature(), 'C', t_offset, dom_yr)
    wind_speed = build_collection(
        ws, ws_dates, WindSpeed(), 'm/s', t_offset, dom_yr)
    wind_direction = build_collection(
        wd, wd_dates, WindDirection(), 'degrees', t_offset, dom_yr)
    ceiling_height = build_collection(
        ceil, ceil_dates, CeilingHeight(), 'm', t_offset, dom_yr)
    visibility = build_collection(
        vis, vis_dates, Visibility(), 'km', t_offset, dom_yr)
    atmos_pressure = build_collection(
        slp, slp_dates, AtmosphericStationPressure(), 'Pa', t_offset, dom_yr)
    total_sky_cover = build_collection(
        sc, sc_dates, TotalSkyCover(), 'tenths', t_offset, dom_yr)
