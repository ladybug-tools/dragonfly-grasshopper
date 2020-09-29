# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Import climate data from a .csv file of annual data obtained from the National
Oceanic and Atmospheric Administration (NOAA) database.  The database can be
accessed here:
https://gis.ncdc.noaa.gov/maps/ncei/cdo/hourly
-

    Args:
        _noaa_file: The path to a .csv file of annual data obtained from the NOAA
            database on your system as a string.
        _timestep_: The timestep at which the data collections should be output.
            Default is 1 but this can be set as high as 60 to ensure that all data
            from the .csv file is imported.
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

ghenv.Component.Name = "DF Import NOAA File"
ghenv.Component.NickName = 'ImportNOAA'
ghenv.Component.Message = '0.2.1'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import os
import csv

try:
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


def build_collection(values, dates, data_type, unit):
    """Build a data collection from raw noaa data and process it to the timestep."""
    if values == []:
        return None
    
    # convert date codes into datetimes.
    datetimes = [DateTime(int(dat[5:7]), int(dat[8:10]), int(dat[11:13]),
                 int(dat[14:16])) for dat in dates]
    
    # make a discontinuous cata collection
    data_header = Header(data_type, unit, AnalysisPeriod())
    data_init = HourlyDiscontinuousCollection(data_header, values, datetimes)
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

    # empty lists to be filled with data
    all_years = []
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

    # check that all years in the file are the same.
    yr1 = all_years[0]
    for yr in all_years:
        assert yr == yr1, 'Not all of the data in the file is from the same ' \
            'year. {} != {}'.format(yr1, yr)
    data_header = Header(GenericType('Years', 'yr'), 'yr', AnalysisPeriod())
    model_year = HourlyContinuousCollection(data_header, [yr1] * 8760)

    # build data collections from the imported values
    dry_bulb_temp = build_collection(db_t, db_t_dates, DryBulbTemperature(), 'C')
    dew_point_temp = build_collection(dp_t, dp_t_dates, DewPointTemperature(), 'C')
    wind_speed = build_collection(ws, ws_dates, WindSpeed(), 'm/s')
    wind_direction = build_collection(wd, wd_dates, WindDirection(), 'degrees')
    ceiling_height = build_collection(ceil, ceil_dates, CeilingHeight(), 'm')
    visibility = build_collection(vis, vis_dates, Visibility(), 'km')
    atmos_pressure = build_collection(slp, slp_dates, AtmosphericStationPressure(), 'Pa')
    total_sky_cover = build_collection(sc, sc_dates, TotalSkyCover(), 'tenths')
