# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Import station location from a .csv file of station information obtained from the
National Oceanic and Atmospheric Administration (NOAA) database.  The database can
be accessed here:
https://gis.ncdc.noaa.gov/maps/ncei/cdo/hourly
-

    Args:
        _station_file: The path to a .csv file of NOAA station location data
            on your system as a string.
        times_zone_: Optional time zone for the station.  If blank, a default
            time zone will be estimated from the longitude.

    Returns:
        location: A Ladybug Location object describing the location data in the
            NOAA station information file.
"""

ghenv.Component.Name = 'DF Import NOAA Staion Location'
ghenv.Component.NickName = 'ImportStaion'
ghenv.Component.Message = '0.2.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import os

try:
    from ladybug.datatype.distance import Distance
    from ladybug.location import Location
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check that the file exists.
    assert os.path.isfile(_station_file), 'Cannot find file at {}.'.format(_station_file)
    
    with open(_station_file) as station_file:
        station_file.readline()  # Skip header row

        # get the pattern of data within the file
        dat_line = station_file.readline().strip().split(',')

        # parse all of the info from the file
        station_id = dat_line[0].replace('"', '')
        city = dat_line[6].replace('"', '')
        latitude = float(dat_line[3].replace('"', ''))
        longitude = float(dat_line[4].replace('"', ''))
        elevation = float(dat_line[5].replace('"', ''))
        elevation = Distance().to_unit([elevation], 'm', 'ft')[0]  # convert to meters

        # estimate or parse time zone.
        if time_zone_:
            assert -12 <= time_zone_ <= 14, ' time_zone_ must be between -12 and '\
                ' 14. Got {}.'.format(time_zone_)
            time_zone = time_zone_
        else:
            time_zone = int((longitude / 180) * 12)

        # build the location object
        location = Location(
            city=city, latitude=latitude, longitude=longitude,
            time_zone=time_zone, elevation=elevation,
            station_id=station_id, source='NCDC')
